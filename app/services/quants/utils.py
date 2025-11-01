import random
import re
from datetime import date, datetime
from itertools import product
from typing import Iterator, Optional, Tuple

from bc_fastkit.common.typing import D
from sqlalchemy.orm import Session

from app import models
from app.common.wqb import COUNTRY_GROUPING_OPERATOR, COUNTRY_GROUPING_REGIONS

TAG_RE = re.compile(r"<([A-Za-z0-9_]+)\s*/>")
CLOSE_TAG_RE = re.compile(r"</>\s*")


def first_day_of_quarter(dt: date | datetime | None = None) -> date:
    """返回给定日期所在季度的第一天（返回 datetime.date）"""
    if dt is None:
        dt = date.today()
    # 如果传入 datetime，取其 date 部分
    if isinstance(dt, datetime):
        dt = dt.date()
    q = (dt.month - 1) // 3  # 0,1,2,3 -> 季度索引
    first_month = q * 3 + 1
    return date(dt.year, first_month, 1)


def convert_template_to_format(template: str) -> str:
    out = TAG_RE.sub(r"{\1}", template)
    out = CLOSE_TAG_RE.sub("", out)
    return out


def rand_index(total: int, limit: int, step_mul: int = 2) -> Iterator[int]:
    """在 total 个元素中随机均匀选择 limit 个索引"""
    if limit >= total:
        yield from range(total)
        return
    rng = random.Random()
    prev = -1
    mul = total // limit
    for i in range(limit):
        idx = rng.randint(prev + 1, min(total - (limit - i), prev + mul * step_mul))
        yield idx
        prev = idx


def descartes_strategy(
    fields: D,
    *,
    limit: Optional[int] = None,
    randomize: bool = True,
    seed: Optional[int] = None,
) -> Iterator[D]:
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    total = 1
    for v in values:
        total *= len(v)
    limit = min(limit or total, total)
    if randomize:
        rng = random.Random(seed)
        for v in values:
            rng.shuffle(v)
    choice = rand_index(total, limit)
    next_idx = next(choice, None)
    for idx, combo in enumerate(product(*values)):
        if next_idx is None:
            break
        if idx != next_idx:
            continue
        yield dict(zip(keys, combo))
        next_idx = next(choice, None)


class ExpressionGenerator:
    def __init__(self, template: str, fields: D, data_field_name="data_field"):
        self.template = convert_template_to_format(template)
        self.fields = fields
        self.data_field_name = data_field_name

    def parse_field(self, k, v, settings: dict) -> str:
        if isinstance(v, models.QuantsWqbDataFieldModel):
            if v.typ == v.TYP_VECTOR:
                return f"vec_avg({v.name})"
            else:
                return v.name
        elif isinstance(v, models.QuantsWqbAlphaModel):
            return v.expression
        elif (
            "country_universe" in k
            and settings.get("region") in COUNTRY_GROUPING_REGIONS
        ):
            return COUNTRY_GROUPING_OPERATOR.format(v)
        else:
            return v

    def generate(
        self, db: Session, *, limit: Optional[int] = None
    ) -> Iterator[Tuple[str, D]]:
        for field_combo in descartes_strategy(self.fields, limit=limit):
            if self.data_field_name and self.data_field_name in field_combo:
                settings = field_combo[self.data_field_name].settings
                kwargs = {
                    k: self.parse_field(k, v, settings) for k, v in field_combo.items()
                }
            expression = self.template.format(**kwargs)
            if self.validation(expression, db):
                yield expression, field_combo

    def validation(self, expression: str, db: Session):
        """ex:
        name	definition
        add	    add(x, y, filter = false), x + y
        """
        return True
