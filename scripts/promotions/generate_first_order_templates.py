#!/usr/bin/env python3
"""
读取无标题 CSV, 根据字段名和 description 启发式映射到一阶 ts 模板，并输出 JSON 文件。

输出文件: 一阶_templates.json

使用方法:
    python3 generate_first_order_templates.py
"""
import csv
import json
import re
from collections import defaultdict

CSV_PATH = __file__.replace("generate_first_order_templates.py", "无标题.csv")
OUT_PATH = __file__.replace("generate_first_order_templates.py", "一阶_templates.json")


def month_token_to_days(tok: str):
    tok = tok.lower()
    if "1m" in tok or tok.startswith("1_") or "1 month" in tok:
        return 21
    if "3m" in tok or "3_month" in tok or "3 month" in tok:
        return 63
    if "6m" in tok or "6_month" in tok or "6 month" in tok:
        return 126
    if "12" in tok or "12m" in tok or "12_month" in tok or "12 month" in tok:
        return 252
    return None


def infer_templates(name: str, desc: str, category: str):
    name_l = name.lower()
    desc_l = (desc or "").lower()
    templates = []

    # tokens that indicate the field is already a time-difference or dispersion measure
    is_delta_token = bool(
        re.search(r"\b(chg|change|delta|pct|percent)\b", name_l + " " + desc_l)
    )
    is_std_token = bool(
        re.search(r"\b(std|stddev|std_dev|volatility|vol)\b", name_l + " " + desc_l)
    )

    # look for explicit month tokens in name/desc
    for tok in [name_l, desc_l]:
        d = month_token_to_days(tok)
        if d:
            # if it's a percent-change-like field
            if is_delta_token:
                # field already encodes a change over time — avoid applying ts_delta again
                # prefer a cross-sectional transform (rank) to keep variation without double-differencing
                templates.append("ts_rank(x,21)")
                return templates
            # otherwise use mean by default for group-aggregates
            templates.append(f"ts_mean(x,{d})")
            return templates

    # percent-change fields
    if "chg" in name_l or "percent change" in desc_l or "percent change" in name_l:
        # prefer 63 (3m) default
        if is_delta_token:
            # already a delta-like field — avoid redundant ts_delta; use rank instead
            templates.append("ts_rank(x,21)")
        else:
            templates.append("ts_delta(x,63)")
        return templates

    # ranks / percentiles
    if (
        "percentile" in desc_l
        or "percentile" in name_l
        or "rank" in desc_l
        or "rank" in name_l
    ):
        templates.append("ts_rank(x,21)")
        return templates

    # standard deviation
    if "stddev" in name_l or "standard deviation" in desc_l or "std" in name_l:
        # if field already indicates a dispersion, avoid applying another ts_std
        if is_std_token:
            templates.append("ts_rank(x,21)")
        else:
            templates.append("ts_std(x,66)")
        return templates

    # counts / numbers / total
    if any(k in name_l for k in ("num", "count", "number", "total", "numof")) or any(
        k in desc_l for k in ("number of", "num of", "count of")
    ):
        # totals => sum longer window; counts changes => delta shorter
        if "total" in name_l or "total" in desc_l:
            templates.append("ts_sum(x,126)")
        else:
            templates.append("ts_delta(x,21)")
        return templates

    # fundamental estimates (analyst category) -> medium/long smoothing
    if category and "analyst" in category.lower():
        templates.append("ts_mean(x,66)")
        templates.append("ts_delta(x,120)")
        return templates

    # financial terms
    if any(
        k in name_l
        for k in (
            "revenue",
            "net profit",
            "netprofit",
            "ntp",
            "eps",
            "ebit",
            "ebitda",
            "profit",
        )
    ) or any(k in desc_l for k in ("earnings", "revenue", "net profit", "eps")):
        templates.append("ts_delta(x,66)")
        templates.append("ts_mean(x,120)")
        return templates

    # means / averages
    if (
        "mean" in name_l
        or "mean" in desc_l
        or "average" in desc_l
        or "average" in name_l
    ):
        templates.append("ts_mean(x,66)")
        return templates

    # fallback: short-term delta
    templates.append("ts_delta(x,63)")
    return templates


def main():
    mapping = defaultdict(list)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name") or row.get("Name")
            desc = row.get("description") or row.get("Description") or ""
            category = row.get("category") or ""
            if not name:
                continue
            templates = infer_templates(name, desc, category)
            for t in templates:
                mapping[t].append(name)

    # Convert defaultdict to normal dict for JSON
    out = {k: v for k, v in mapping.items()}

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(
        f"Wrote {OUT_PATH} with {sum(len(v) for v in out.values())} mappings across {len(out)} templates"
    )


if __name__ == "__main__":
    main()
