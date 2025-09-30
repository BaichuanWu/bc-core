from sqlalchemy import Column
from typing import Optional
from pydantic import computed_field
from bc_fastkit.model import (
    BaseModel,
    DefaultJsonColumn,
    NotNullColumn,
    VARCHAR,
    TEXT,
    DefaultTypeColumn,
    DefaultIdColumn,
)

class QuantInspirationModel(BaseModel):
    title=NotNullColumn(VARCHAR(63), comment="标题")
    content = NotNullColumn(TEXT, comment="内容")

class QuantAlphaTemplateModel(BaseModel):
    title= NotNullColumn(VARCHAR(63), comment="标题")
    content= NotNullColumn(TEXT, comment="内容")
    inspiration_id = DefaultIdColumn(comment="灵感id")
    var_data =DefaultJsonColumn(server_default={}, comment="反馈内容")


class QuantsUncommitAlphaModel(BaseModel):
    expression =NotNullColumn(VARCHAR(511), unique=True, comment="alpha 表达式")
    state = DefaultTypeColumn(comment="当前状态: 0: 未上报, 3: 无法上报, 5: 已上报")


class QuantsAlphaRecordModel(BaseModel):
    cno = NotNullColumn(VARCHAR(63), unique=True, comment="世坤编号")
    expression=NotNullColumn(VARCHAR(511), unique=True, comment="alpha 表达式")
    state=DefaultTypeColumn(
            comment="当前状态: 0: 未上报, 3: 无法上报, 5: 已上报, 8:无法提交, 10: 已提交"
        )
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: 因子, 2: 策略")
    rate = DefaultTypeColumn(comment="评级")
    feedback =DefaultJsonColumn(server_default={}, comment="反馈内容")