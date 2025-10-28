import hashlib
from asyncio import sleep
from datetime import date

from bc_fastkit.common.typing import DATE_STR_FORMAT, D
from sqlalchemy import func
from sqlalchemy.orm import Session
from wqb import URL_ALPHAS_ALPHAID, Alpha, FilterRange, WQBSession, to_multi_alphas

from app.core.db import sync_session
from app.crud import (
    quants_alpha_template_handler,
    quants_wqb_alpha_handler,
    quants_wqb_data_field_handler,
    quants_wqb_operator_handler,
    quants_wqb_universe_handler,
)
from config import settings

from .strategy import ExpressionGenerator

db = sync_session()
URL = URL_ALPHAS_ALPHA_PNL = URL_ALPHAS_ALPHAID + "/recordsets/pnl"


class WorldQuantClient:
    def __init__(
        self,
        username: str = settings.Q_ACCOUNT,
        password: str = settings.Q_PASSWORD,
    ) -> None:
        self.wqb = WQBSession((username, password))
        self.mul_cnt = 10

    def sync_operators(self, db: Session):
        resp = self.wqb.search_operators()
        data = resp.json()
        names = [d["name"] for d in data]
        to_delete = quants_wqb_operator_handler.search(db, q={"name_not_in": names})
        for entity in to_delete:
            quants_wqb_operator_handler.remove(db, id=entity.id)
        for d in data:
            quants_wqb_operator_handler.create_on_duplicate_update(db, obj_in=d)
        db.commit()

    def sync_all_dataset_field(self, db: Session):
        universes = quants_wqb_universe_handler.search(db, q={})
        for idx, universe in enumerate(universes[::-1][23:]):
            resps = self.wqb.search_datasets(
                region=universe.region, delay=universe.delay, universe=universe.name
            )
            for resp in resps:
                data = resp.json()
                for d in data.get("results", []):
                    self.sync_dataset_field(
                        db,
                        region=universe.region,
                        delay=universe.delay,
                        universe=universe.name,
                        dataset_id=d["id"],
                        coverage=FilterRange.from_str("[0.65,inf)"),
                        alpha_count=FilterRange.from_str("[3,inf)"),
                        user_count=FilterRange.from_str("[3,inf)"),
                    )
                    print(f"Idx: {idx} Synced Dataset Fields for Dataset ID: {d['id']}")

    def sync_dataset_field(
        self, db: Session, region, delay, universe, dataset_id, **kwargs
    ):
        resps = self.wqb.search_fields(
            region=region,
            delay=delay,
            universe=universe,
            dataset_id=dataset_id,
            timeout=60,
            **kwargs,
        )
        for resp in resps:
            data = resp.json()
            for d in data.get("results", []):
                obj_in = {
                    "region": d["region"],
                    "delay": d["delay"],
                    "universe": d["universe"],
                    "dataset_id": d["dataset"]["id"],
                    "typ": quants_wqb_data_field_handler.model.typ_from_str(d["type"]),
                    "category": d["category"]["id"],
                    "sub_category": d.get("subcategory", {}).get("id") or "",
                    "name": d["id"],
                    "description": d["description"],
                    "payramid_multiplier": d["pyramidMultiplier"],
                    "coverage": d["coverage"],
                    "user_count": d["userCount"],
                    "alpha_count": d["alphaCount"],
                }
                prev = quants_wqb_data_field_handler.search_one(
                    db,
                    q={
                        "region": obj_in["region"],
                        "universe": obj_in["universe"],
                        "delay": obj_in["delay"],
                        "dataset_id": obj_in["dataset_id"],
                        "name": obj_in["name"],
                    },
                )
                if prev:
                    quants_wqb_data_field_handler.update(
                        db,
                        obj_in={**obj_in, "id": prev.id},
                    )
                else:
                    quants_wqb_data_field_handler.create(db, obj_in=obj_in)
            db.commit()

    async def simulate_alpha(self, expression: Alpha):
        """模拟运行alpha表达式"""
        resp = await self.wqb.simulate(target=expression)
        return resp

    def generate_batch(
        self,
        db: Session,
        template_id: int,
        fields: D,
        settings: D,
        typ: int = 0,
        parent_id: int = 0,
    ):
        """生成批次的alpha表达式记录"""
        template = quants_alpha_template_handler.get(db, id=template_id)
        if not template:
            raise ValueError(f"模板ID不存在: {template_id}")
        expression = template.expression
        batch_no = f"""{date.today().strftime(DATE_STR_FORMAT)}_{
            hashlib.sha256((expression + str(fields) + str(settings)).encode('utf-8')).hexdigest()[:8]}"""
        for expr in ExpressionGenerator(expression, fields).generate():
            obj_in = {
                "template_id": 0,
                "task_id": 0,
                "expression": expr,
                "operator_count": expr.count("("),  # 简单估计操作符数量
                "description": "",
                "typ": typ,
                "region": settings.get("region", ""),
                "universe": settings.get("universe", ""),
                "delay": settings.get("delay", 0),
                "setting_str": str(settings),
                "state": quants_wqb_alpha_handler.model.STATE_PENDING,
                "wqb_data": {},
                "data_field": "",
                "batch_no": batch_no,
                "parent_id": parent_id,
            }
            quants_wqb_alpha_handler.create(db, obj_in=obj_in)

    async def batch_simulate_alpha(
        self, db: Session, batch_no: str, conurrency: int = 1, cnt=0
    ):
        """批量异步运行alpha表达式, 测试alpha是否异常cnt=1即可"""

        def on_success(d: D):
            # resp = d["resp"]
            pass
            # TODO 更新，并且根据条件获取pnl数据

        skip = 0
        total = 1
        limit = 1000
        while skip < cnt or total:
            alphas, total = quants_wqb_alpha_handler.search_limit(
                db, q={"batch_no": batch_no, "state": 0}, skip=skip, limit=limit
            )
            mul_alphas = to_multi_alphas((a.to_wqb for a in alphas), self.mul_cnt)
            # TODO check 最后数量不足mul_cnt的情况
            await self.wqb.concurrent_simulate(
                targets=mul_alphas, concurrency=conurrency, on_success=on_success
            )
            skip += limit

    def sync_simulate_alpha(self, db: Session, **kwargs):
        """同步运行alpha表达式"""
        for resp in self.wqb.filter_alphas(**kwargs):
            for data in resp.json().get("results", []):
                obj_in = {
                    "wqb_alpha_id": data["id"],
                    "template_id": 0,
                    "task_id": 0,
                    "expression": data["regular"]["code"],
                    "operator_count": data["regular"]["operatorCount"],
                    "description": data["regular"].get("description", "") or "",
                    "typ": 0,
                    "region": data["settings"]["region"],
                    "universe": data["settings"]["universe"],
                    "delay": data["settings"]["delay"],
                    "setting_str": str(data["settings"]),
                    "state": quants_wqb_alpha_handler.model.state_from_str(
                        data["status"]
                    ),
                    "wqb_data": data,
                    "data_field": "",
                }
                prev = quants_wqb_alpha_handler.search_one(
                    db, q={"wqb_alpha_id": data["id"]}
                )
                if prev:
                    quants_wqb_alpha_handler.update(
                        db,
                        obj_in=obj_in | {"id": prev.id},
                    )
                else:
                    quants_wqb_alpha_handler.create(db, obj_in=obj_in)
                print(f"Synced WQB Alpha ID: {data['id']}")
            db.commit()

    async def update_alpha_pnl(self, db: Session):
        alphas = (
            db.query(quants_wqb_alpha_handler.model)
            .filter(quants_wqb_alpha_handler.model.wqb_pnl_data == func.json_object())
            .all()
        )
        for alpha in alphas:
            resp = self.wqb.request(
                "get", URL_ALPHAS_ALPHA_PNL.format(alpha.wqb_alpha_id)
            )
            if resp.status_code == 200:
                try:
                    alpha.wqb_pnl_data = resp.json()
                    quants_wqb_alpha_handler.update(
                        db, obj_in={"id": alpha.id, "wqb_pnl_data": alpha.wqb_pnl_data}
                    )
                    print(f"Updated PnL for Alpha ID: {alpha.wqb_alpha_id}")
                    db.commit()
                except Exception as e:
                    print(
                        f"Failed to update PnL for Alpha ID: {alpha.wqb_alpha_id}, Error: {e} content: {resp.content}"
                    )
                    self.wqb.auth_request()
                    await sleep(120)
            await sleep(10)  # 避免请求过快


wqb_client = WorldQuantClient()
