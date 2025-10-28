Promotion scripts (one-step and two-step) — usage
===============================================

This folder contains scripts to generate first-order (one-step) expression templates and second-order (group-only) derived expressions for backtesting.

Files
-----
- `一阶_templates.json` — mapping from template string (e.g. `ts_mean(x,66)`) to a list of datafields.
- `expressions_with_setting_from_一阶.json` — simplified backtest-ready JSON (one entry per template).
- `二阶.csv` — CSV with a list of promising first-order expressions (columns: `expression`, `sharpe`, `fitness`, `wqb_data`).
- `generate_expressions_from_templates.py` — (existing) script to convert `一阶_templates.json` into backtest-ready JSON; can expand per-field.
- `generate_second_order_from_csv_group.py` — (new) generate group-only second-order expressions from `二阶.csv`.
- `mcp_groupings.json` — optional JSON listing grouping fields (e.g. `["SUBINDUSTRY","GICS_SECTOR"]`). If missing, scripts fall back to `["SUBINDUSTRY"]`.
- `run_promotions.py` — helper runner that executes the two main steps and writes outputs (created here).

How it works
------------
1. First-order templates are created/collected and saved in `一阶_templates.json`.
2. The script `generate_expressions_from_templates.py` converts these templates into `expressions_with_setting_from_一阶.json`. Optionally it can expand each template to per-field expressions.
3. After backtesting, pick promising first-order expressions and collect them into `二阶.csv` (as produced by your workflow).
4. Run `generate_second_order_from_csv_group.py` (or `run_promotions.py`) to create `二阶_expanded.json` containing group-only second-order expressions.

Running locally
---------------
All scripts use Python 3 and only stdlib modules. From the repository root run:

```bash
python3 ./bc-core/scripts/promotions/run_promotions.py
```

The runner will:
- Convert first-order templates if `一阶_templates.json` and the converter script are present.
- Read `二阶.csv` and write `二阶_expanded.json` using group templates.

Customization
-------------
- Edit `mcp_groupings.json` in the same folder to control which grouping fields are used.
- Edit `generate_second_order_from_csv_group.py` to adjust which group templates are generated (e.g. remove `group_zscore` or change mean windows).

Notes
-----
- Region is assumed USA; scripts avoid country-level Cartesian groupings per your instruction.
- If you want the runner to limit the number of first-order expressions used (top-N), modify the runner accordingly.

Contact
-------
If you want additional transforms (product/difference between first-order expressions, lagging, or TS-based second-order templates), tell me which operators to include and I will add them.
