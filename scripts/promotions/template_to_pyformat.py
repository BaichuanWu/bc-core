#!/usr/bin/env python3
"""Small utility: convert template tags like <ts_op/> and <s/> into Python format placeholders.

Example:
    input:  "<ts_op/>(<s/>) </>"
    output: "{ts_op}({s}) "

This tool replaces occurrences of <name/> with {name} and removes any literal closing tags "</>".
It is intentionally simple and conservative: it only treats tags matching [A-Za-z0-9_]+.
"""
from __future__ import annotations

import re
import sys
from typing import Iterable

TAG_RE = re.compile(r"<([A-Za-z0-9_]+)\s*/>")
CLOSE_TAG_RE = re.compile(r"</>\s*")


def convert_template_to_format(template: str) -> str:
    """Convert <tag/> occurrences to {tag} and strip literal closing tags "</>".

    Args:
        template: input template string containing tags like `<foo/>`.

    Returns:
        A Python format-style string where tags are replaced by `{foo}`.
    """
    if template is None:
        return template

    # Replace tags <name/> -> {name}
    out = TAG_RE.sub(r"{\1}", template)

    # Remove explicit closing markers like </>
    out = CLOSE_TAG_RE.sub("", out)

    return out


def convert_lines(lines: Iterable[str]) -> Iterable[str]:
    for line in lines:
        yield convert_template_to_format(line.rstrip("\n"))


def _cli(argv: Iterable[str]) -> int:
    """Simple CLI: if one argument is provided, treat it as the template to convert.
    Otherwise read stdin lines and write converted lines to stdout.
    """
    args = list(argv)
    if len(args) == 0:
        # read stdin
        for out in convert_lines(sys.stdin):
            print(out)
        return 0

    # join args with spaces to allow passing strings without shell quoting pain
    s = " ".join(args)
    print(convert_template_to_format(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
