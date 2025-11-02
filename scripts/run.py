import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from wqb import FilterRange

try:
    base = Path(__file__).resolve().parent
except NameError:
    base = Path.cwd()

sys.path.insert(0, os.path.abspath(os.path.dirname(base)))


from app.services.quants.strategy.three_level import ThreeLevelStrategy  # noqa: E402
from app.services.quants.worldbrain import db, wqb_client  # noqa: E402


def iso_with_tz(days_offset=0, tz_offset_hours=-4):
    """
    生成指定天数偏移的 ISO 8601 时间字符串（带时区）

    :param days_offset: 0表示今天，1表示昨天，-1表示明天
    :param tz_offset_hours: 时区偏移，例如 -4 表示 UTC-4
    :return: ISO 8601 字符串，如 2025-10-24T00:00:00-04:00
    """
    tz = timezone(timedelta(hours=tz_offset_hours))
    dt = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    dt_offset = dt - timedelta(days=days_offset)
    return dt_offset.isoformat(timespec="seconds")


# 1. 创建解析器
parser = argparse.ArgumentParser(description="wqb量化因子同步脚本")

# 2. 定义参数
parser.add_argument(
    "-s", type=str, help="指令代码: g-生成一阶因子, s-回测同步数据, f-抓取同步信息"
)


async def main():
    args = parser.parse_args()
    template_ids = getattr(args, "t", "3,5,6")
    batch_size = getattr(args, "b", 500)
    strategy = ThreeLevelStrategy(
        template_ids=tuple(int(i) for i in template_ids.split(",")),
        regions=["GLB", "ASI", "EUR", "USA"],
        batch_size=batch_size,
    )
    if args.s == "g1":
        strategy.generate_first_level_alpha(db)
    elif args.s == "g2":
        strategy.generate_second_level_alpha(db)
    elif args.s == "g3":
        strategy.generate_third_level_alpha(db)
    elif args.s == "s":
        await wqb_client.simulate_by_db(db, conurrency=5)
    elif args.s == "f":
        wqb_client.fetch_simulate_alpha(
            db,
            date_created=FilterRange.from_str(f"[{iso_with_tz(1)},{iso_with_tz(-1)})"),
        )
    db.commit()


if __name__ == "__main__":
    asyncio.run(main())
    # wqb_client.fetch_simulate_alpha(db, date_created=FilterRange.from_str(f"[{iso_with_tz(0)},{iso_with_tz(-1)})"))
    # strategy.generate_first_level_alpha(db)
