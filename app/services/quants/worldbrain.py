from asyncio import sleep

from sqlalchemy import func
from sqlalchemy.orm import Session
from wqb import (
    URL_ALPHAS_ALPHAID,
    Alpha,
    FilterRange,
    WQBSession,
    to_multi_alphas,
    wqb_logger,
)

from app.core.db import sync_session
from app.crud import (
    quants_wqb_alpha_handler,
    quants_wqb_data_field_handler,
    quants_wqb_operator_handler,
    quants_wqb_universe_handler,
)
from config import settings

db = sync_session()
URL_ALPHAS_ALPHA_PNL = URL_ALPHAS_ALPHAID + "/recordsets/pnl"
URL_PYRAMIDS_ALPHA = (
    "https://api.worldquantbrain.com/users/self/activities/pyramid-alphas"
)


class WorldQuantClient:
    def __init__(
        self,
        username: str = settings.Q_ACCOUNT,
        password: str = settings.Q_PASSWORD,
    ) -> None:
        self.logger = wqb_logger()
        self.wqb = WQBSession((username, password), logger=self.logger)
        self.mul_cnt = 10

    def fetch_operators(self, db: Session):
        resp = self.wqb.search_operators()
        data = resp.json()
        names = [d["name"] for d in data]
        to_delete = quants_wqb_operator_handler.search(db, q={"name_not_in": names})
        for entity in to_delete:
            quants_wqb_operator_handler.remove(db, id=entity.id)
        for d in data:
            quants_wqb_operator_handler.create_on_duplicate_update(db, obj_in=d)
        db.commit()

    def fetch_all_dataset_field(self, db: Session):
        universes = quants_wqb_universe_handler.search(db, q={})
        for idx, universe in enumerate(universes[::-1][23:]):
            resps = self.wqb.search_datasets(
                region=universe.region, delay=universe.delay, universe=universe.name
            )
            for resp in resps:
                data = resp.json()
                for d in data.get("results", []):
                    self.fetch_dataset_field(
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

    def fetch_dataset_field(
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
                quants_wqb_data_field_handler.create_or_update_by_wqb_data(db, data=d)
                print(f"Synced WQB Data Field ID: {d['id']}")
            db.commit()

    async def simulate_alpha(self, expression: Alpha):
        """模拟运行alpha表达式"""
        resp = await self.wqb.simulate(target=expression)
        return resp

    async def simulate_by_db(self, db: Session, conurrency: int = 1):
        alphas = quants_wqb_alpha_handler.search(
            db, q={"state": quants_wqb_alpha_handler.model.STATE_PENDING}
        )
        db.query(quants_wqb_alpha_handler.model).filter(
            quants_wqb_alpha_handler.model.state
            == quants_wqb_alpha_handler.model.STATE_PENDING
        ).update({"state": quants_wqb_alpha_handler.model.STATE_SIMULATING})
        db.commit()
        print(f"Total to simulate alphas: {len(alphas)}")
        target = {}
        for alpha in alphas:
            target.setdefault((alpha.region, alpha.delay, alpha.universe), []).append(
                alpha
            )
        for alphas in target.values():
            mul_alphas = to_multi_alphas((a.to_wqb for a in alphas), self.mul_cnt)
            # TODO check 最后数量不足mul_cnt的情况
            await self.wqb.concurrent_simulate(
                targets=mul_alphas, concurrency=conurrency, log="simulate_alpha"
            )

    def fetch_simulate_alpha(self, db: Session, **kwargs):
        """同步运行alpha表达式"""
        for resp in self.wqb.filter_alphas(**kwargs):
            for data in resp.json().get("results", []):
                print(f"Synced WQB Alpha ID: {data['id']}")
                quants_wqb_alpha_handler.create_or_update_by_wqb_data(db, data=data)
            db.commit()

    async def fetch_alpha_pnl(self, db: Session):
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

    def get_pyramids_alpha_info(self) -> dict:
        resp = self.wqb.request("get", URL_PYRAMIDS_ALPHA)
        rs = {}
        for data in resp.json().get("pyramids", []):
            rs[(data["region"], data["delay"], data["category"]["id"])] = data[
                "alphaCount"
            ]
        return rs


wqb_client = WorldQuantClient()
