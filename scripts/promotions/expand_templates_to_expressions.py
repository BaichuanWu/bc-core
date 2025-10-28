#!/usr/bin/env python3
"""
将 `一阶_templates.json` 中的模板展开为按 datafield 的表达式列表，输出可直接用于回测的 JSON 文件。

输出文件: expressions_with_setting_from_一阶_expanded.json

每个条目格式和示例文件 `expressions_with_setting.json` 保持一致：
  {"type":"REGULAR","settings":{...},"regular":"<expr>"}

其中 <expr> 是把模板中的 x 替换为具体 datafield 名称后的字符串。
"""
import json
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SRC = THIS_DIR / "一阶_templates.json"
OUT = THIS_DIR / "expressions_with_setting_from_一阶_expanded.json"

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


def replace_x(template: str, field: str) -> str:
    # Replace occurrences of 'x' as a parameter name with the field
    # Simple approach: replace 'x' when appearing as argument 'x,' or '(x' or ',x' or '(x)'
    # But safer: replace the substring 'x' that is between parentheses in the template
    return template.replace("x", field)


def main():
    if not SRC.exists():
        print(f"源文件不存在: {SRC}")
        return 2

    templates = json.loads(SRC.read_text(encoding="utf-8"))
    out = []
    count = 0

    for tmpl, fields in templates.items():
        for f in fields:
            expr = replace_x(tmpl, f)
            obj = {
                "type": "REGULAR",
                "settings": DEFAULT_SETTINGS,
                "regular": expr,
            }
            out.append(obj)
            count += 1

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"写入 {OUT}，共 {count} 条表达式")


if __name__ == "__main__":
    raise SystemExit(main())
