from wqb import Alpha, WQBSession

from app.core.db import sync_session
from app.crud import quants_wqb_alpha_handler
from config import settings

db = sync_session()


class WorldQuantClient:
    def __init__(
        self, username: str = settings.Q_ACCOUNT, password: str = settings.Q_PASSWORD
    ) -> None:
        self.wqb = WQBSession((username, password))

    def get_operator_list(self):
        """获取操作人列表"""
        resp = self.wqb.search_operators()
        return resp

    def get_dataset_list(
        self, region, delay, universe, *, dataset_id, offset=0, limit=2000
    ):
        """获取数据集列表"""
        resp = self.wqb.search_fields_limited(
            region=region,
            delay=delay,
            universe=universe,
            dataset_id=dataset_id,
            offset=offset,
            limit=limit,
            timeout=60,
        )
        return resp

    async def simulate_alpha(self, expression: Alpha):
        """模拟运行alpha表达式"""
        resp = await self.wqb.simulate(target=expression)
        return resp

    def sync_simulate_alpha(self, **kwargs):
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
                    "wbq_data": data,
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


wqb_client = WorldQuantClient()
