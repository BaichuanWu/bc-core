import asyncio

from app.services.quants.worldbrain import db, wqb_client


async def main():
    # wqb_client.sync_simulate_alpha(db,sharpe=FilterRange.from_str("(1.0,inf)"), universe="ILLIQUID_MINVOL1M")
    wqb_client.sync_operators(db)
    # await wqb_client.update_alpha_pnl(db)
    # wqb_client.sync_all_dataset_field(db)


if __name__ == "__main__":
    # wqb_client.sync_simulate_alpha(sharpe=FilterRange.from_str("(-inf,-1)"))
    # db.commit()
    # resp = client.get_dataset_list(
    #     region="USA",
    #     delay=1,
    #     universe="TOP3000",
    #     dataset_id="analyst11",
    #     offset=0,
    #     limit=20
    # )
    # print(resp.content)
    # resp

    asyncio.run(main())
