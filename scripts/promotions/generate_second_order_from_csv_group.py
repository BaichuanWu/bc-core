#!/usr/bin/env python3
"""Generate group-only second-order expressions from a CSV of first-order expressions.

This is a safer replacement that reads `mcp_groupings.json` or `groupings.json`
from the same directory (fallback to ["SUBINDUSTRY"]) and generates only
group-related operators for each first-order expression.
"""
import csv
import json
from pathlib import Path
from typing import List

THIS_DIR = Path(__file__).resolve().parent
INPUT_CSV = THIS_DIR / "二阶.csv"
OUT_JSON = THIS_DIR / "二阶_expanded.json"


DEFAULT_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "ILLIQUID_MINVOL1M",
    "delay": 1,
    "decay": 5,
    "neutralization": "SUBINDUSTRY",
    "truncation": 0.05,
    "pasteurization": "ON",
    "testPeriod": "P0Y0M",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "maxTrade": "ON",
    "language": "FASTEXPR",
    "visualization": False,
}


# group-only templates; {g} will be replaced by the group field name
GROUP_TEMPLATES = [
    "group_rank({e}, {g})",
    "group_mean({e}, {g}, 63)",
    "group_mean({e}, {g}, 252)",
    "group_std({e}, {g}, 66)",
    "group_zscore({e}, {g})",
]


def read_groupings(dir_path: Path) -> List[str]:
    for name in ("mcp_groupings.json", "groupings.json"):
        p = dir_path / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return [str(x) for x in data if x]
                if isinstance(data, dict):
                    for key in ("groups", "groupings", "fields"):
                        v = data.get(key)
                        if isinstance(v, list):
                            return [str(x) for x in v if x]
                vals = [str(v) for v in data.values() if isinstance(v, (str, int))]
                if vals:
                    return vals
            except Exception:
                continue
    return ["SUBINDUSTRY"]


def read_expressions(csv_path: Path) -> List[str]:
    if not csv_path.exists():
        raise FileNotFoundError(f"input not found: {csv_path}")

    exprs = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            e = row.get("expression")
            if not e:
                first = list(row.values())[0] if row else None
                e = first
            if e:
                e = e.strip().strip('"')
                exprs.append(e)
    return exprs


def generate_second_order(exprs: List[str], groups: List[str]) -> List[dict]:
    out = []
    for e in exprs:
        e_clean = e
        for g in groups:
            for t in GROUP_TEMPLATES:
                code = t.format(e=e_clean, g=g)
                obj = {
                    "type": "REGULAR",
                    "settings": DEFAULT_SETTINGS,
                    "regular": code,
                }
                out.append(obj)
    return out


def main():
    groups = read_groupings(THIS_DIR)
    print(f"使用分组字段: {groups}")
    exprs = read_expressions(INPUT_CSV)
    print(f"读取到 {len(exprs)} 一阶表达式，从 {INPUT_CSV}")
    expanded = generate_second_order(exprs, groups)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(expanded, f, ensure_ascii=False, indent=2)
    print(f"已写入 {OUT_JSON}，二阶表达式数量: {len(expanded)}")


if __name__ == "__main__":
    main()
