import asyncio

from app.services.quants.worldbrain import WorldQuantClient

d = (
    {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 10,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.05,
            "pasteurization": "ON",
            "testPeriod": "P0Y0M",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "maxTrade": "ON",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": """ranked_signal = ts_zscore(vec_sum(ern4_impliedee), 120);
        signal = group_zscore(ranked_signal,SUBINDUSTRY);
        ts_product(signal, 120)""",
    },
)


async def main():
    client = WorldQuantClient()
    resp = await client.simulate_alpha(d)
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())
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
