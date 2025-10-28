import random
import re
from itertools import product
from typing import Iterator, Optional

from bc_fastkit.common.typing import D

TAG_RE = re.compile(r"<([A-Za-z0-9_]+)\s*/>")
CLOSE_TAG_RE = re.compile(r"</>\s*")


def convert_template_to_format(template: str) -> str:
    """Convert <tag/> occurrences to {tag} and strip literal closing tags "</>".

    Args:
        template: input template string containing tags like `<foo/>`.

    Returns:
        A Python format-style string where tags are replaced by `{foo}`.
    """
    # Replace tags <name/> -> {name}
    out = TAG_RE.sub(r"{\1}", template)

    # Remove explicit closing markers like </>
    out = CLOSE_TAG_RE.sub("", out)

    return out


def descartes_strategy(
    fields: D,
    *,
    limit: Optional[int] = None,
    randomize: bool = True,
    seed: Optional[int] = None,
) -> Iterator[D]:
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    if randomize:
        rng = random.Random(seed)
        for v in values:
            rng.shuffle(v)
    count = 0
    for combo in product(*values):
        yield dict(zip(keys, combo))
        count += 1
        if limit is not None and count >= limit:
            break


class ExpressionGenerator:
    def __init__(self, template: str, fields: D):
        self.template = convert_template_to_format(template)
        self.fields = fields

    def generate(self, *, limit: Optional[int] = None) -> Iterator[str]:
        for field_combo in descartes_strategy(self.fields, limit=limit):
            yield self.template.format(**field_combo)
