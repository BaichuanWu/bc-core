import hashlib
import math
import re
from typing import Any, Sequence

from bc_fastkit.crud import CRUDBase
from sqlalchemy.orm import Session

from app.models.quants import (
    QuantsAlphaTemplateModel,
    QuantsInspirationModel,
    QuantsWqbAlphaModel,
    QuantsWqbAlphaTaskModel,
    QuantsWqbDataFieldModel,
    QuantsWqbOperatorModel,
    QuantsWqbUniverseModel,
)


def normalize_expr(
    s: str, remove_whitespace: bool = True, newline_after_semicolon: bool = True
) -> str:
    """
    标准化表达式字符串：
      - remove_whitespace=True 时，删除引号外的所有空白字符（保留引号内的空白）
      - newline_after_semicolon=True 时，把每个分号及其后面的空白替换为 ';\n'
    返回去除首尾空白的结果（末尾不会多余换行）。
    """
    if not isinstance(s, str):
        raise TypeError("输入必须是字符串")

    def _remove_ws_outside_quotes(text: str) -> str:
        # 把双引号或单引号内的片段保留为独立段落，其余段落删除空白
        parts = re.split(r'(".*?"|\'.*?\')', text)
        for i in range(0, len(parts), 2):  # 偶数索引是引号外的片段
            parts[i] = re.sub(r"\s+", "", parts[i])
        return "".join(parts)

    out = s
    if remove_whitespace:
        out = _remove_ws_outside_quotes(out)

    if newline_after_semicolon:
        # 把分号及其后跟随的任意空白，替换为 ';\n'
        out = re.sub(r";\s*", ";\n", out)

    # 去除首尾空白与多余换行
    out = out.strip()
    # 如果最后字符是换行，则去掉
    out = out.rstrip("\n")
    return out


def score_by_adjacent_changes(
    rows: Sequence[Sequence[Any]],
    value_index: int = 2,
) -> int:
    """
    rows: 序列，每项为 list/tuple，value_index 指定用于检测变化的数值索引（默认第3项）
    返回 int 分数，范围 [-50, 50]
    """

    def sign(x: float) -> int:
        if x > 0:
            return 1
        if x < 0:
            return -1
        return 0

    n = len(rows)
    if n < 2:
        return 0  # 无法定义变化，返回中性 0（你也可以改成 -50 或其它）
    # 提取序列并转换为数字（尽量容错）
    vals = []
    for r in rows:
        try:
            v = r[value_index]
            # 如果 v 是字符串包含数字，尝试转为 float
            if isinstance(v, str):
                v = float(v) if v.strip() != "" else 0.0
            else:
                v = float(v)
        except Exception:
            # 转换失败则当作 0 处理
            v = 0.0
        vals.append(v)

    # 计算相邻符号变化次数
    changes = 0
    prev_s = sign(vals[0])
    for x in vals[1:]:
        s = sign(x)
        if s != prev_s:
            changes += 1
        prev_s = s

    max_changes = n - 1
    r = changes / max_changes if max_changes > 0 else 0.0
    score = r * 100.0 - 50.0
    # 四舍五入并转 int
    return int(math.floor(score + 0.5)) if score >= 0 else int(math.ceil(score - 0.5))


class CRUDWqbAlphaTemplateTask(CRUDBase):
    def generate_wqb_alpha(self, db, *, id):
        pass


class CRUDWqbAlpha(CRUDBase[QuantsWqbAlphaModel]):
    def complement_obj_in(self, db: Session, *, obj_in):
        if "expression" in obj_in:
            obj_in["expression"] = normalize_expr(obj_in["expression"])
        if "wqb_data" in obj_in:
            obj_in["sharpe"] = (obj_in["wqb_data"]["is"]["sharpe"],)
            obj_in["fitness"] = obj_in["wqb_data"]["is"]["fitness"]
        if "setting_str" in obj_in and "expression" in obj_in:
            obj_in["expression_hash"] = hashlib.sha256(
                (obj_in["setting_str"] + obj_in["expression"]).encode("utf-8")
            ).hexdigest()
        return super().complement_obj_in(db, obj_in=obj_in)


quants_inspiration_handler = CRUDBase(QuantsInspirationModel)
quants_alpha_template_handler = CRUDBase(QuantsAlphaTemplateModel)
quants_wqb_alpha_handler = CRUDWqbAlpha(QuantsWqbAlphaModel)
quants_wqb_alpha_task_handler = CRUDWqbAlphaTemplateTask(QuantsWqbAlphaTaskModel)
quants_wqb_operator_handler = CRUDBase(QuantsWqbOperatorModel)
quants_wqb_data_field_handler = CRUDBase(QuantsWqbDataFieldModel)
quants_wqb_universe_handler = CRUDBase(QuantsWqbUniverseModel)
