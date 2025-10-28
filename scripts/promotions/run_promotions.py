#!/usr/bin/env python3
"""Helper runner for promotion scripts.

Usage:
    python3 run_promotions.py

This script will:
 - Optionally run the first-order templates converter if present
 - Run the group-only second-order generator to produce 二阶_expanded.json
"""
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
FIRST_ORDER_SCRIPT = THIS_DIR / "generate_expressions_from_templates.py"
SECOND_ORDER_SCRIPT = THIS_DIR / "generate_second_order_from_csv_group.py"


def run(cmd):
    print(f"-> running: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(res.returncode)


def main():
    # 1) run first-order converter if exists
    if FIRST_ORDER_SCRIPT.exists():
        print("Found first-order converter, running it...")
        run(f"python3 {FIRST_ORDER_SCRIPT}")
    else:
        print("First-order converter not found, skipping.")

    # 2) run second-order group-only generator
    if SECOND_ORDER_SCRIPT.exists():
        print("Running second-order (group-only) generator...")
        run(f"python3 {SECOND_ORDER_SCRIPT}")
    else:
        print("Second-order generator not found; expected:", SECOND_ORDER_SCRIPT)


if __name__ == "__main__":
    main()
