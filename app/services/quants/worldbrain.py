from wqb import Alpha, WQBSession

from config import settings


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


wqb_client = WorldQuantClient()
