import os


def init_code():
    import sys
    from pathlib import Path

    try:
        base = Path(__file__).resolve().parent
    except NameError:
        base = Path.cwd()
    # ensure the local app package is importable
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(base))))
