from wqb import FilterRange

from app.services.quants.worldbrain import db, wqb_client

if __name__ == "__main__":
    wqb_client.sync_simulate_alpha(sharpe=FilterRange.from_str("(-inf,-1)"))
    db.commit()
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
