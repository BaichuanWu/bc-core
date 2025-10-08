from bc_fastkit.model import (
    DefaultJsonColumn,
    NotNullColumn,
    VARCHAR,
    TEXT,
    DefaultTypeColumn,
    DefaultIdColumn,
    DefaultTextColumn,
    DefaultDecimalColumn,
    UniqueConstraint,
)
from bc_fastkit.model import BaseModel 


class QuantsInspirationModel(BaseModel):
    title= NotNullColumn(VARCHAR(63), comment="标题")
    link= NotNullColumn(VARCHAR(511), comment="链接")
    content= DefaultTextColumn(comment="内容")


class QuantsAlphaTemplateModel(BaseModel):
    title = NotNullColumn(VARCHAR(63), comment="标题")
    inspiration_id = DefaultIdColumn(comment="灵感ID")
    expression = DefaultTextColumn(comment="内容")

class QuantsWqbAlphaTemplateTaskModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    field_data = DefaultJsonColumn(server_default={}, comment="字段数据")
    setting_data = DefaultJsonColumn(server_default={}, comment="设置数据")

class QuantsWqbAlphaModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    expression = NotNullColumn(VARCHAR(511), unique=True, comment="alpha 表达式")
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: 因子, 2: 策略")
    region = NotNullColumn(VARCHAR(63), comment="适用市场")
    universe = NotNullColumn(VARCHAR(63), comment="适用股票池")
    delay = DefaultTypeColumn(comment="延迟天数")
    setting_str = NotNullColumn(VARCHAR(511), comment="参数设置字符串")
    wqb_alpha_id = NotNullColumn(VARCHAR(63), unique=True, comment="世坤因子ID")
    state = DefaultTypeColumn(comment="状态: 0: 未知, 1: 开发中, 2: 测试中, 3: 已上线")
    wbq_data = DefaultJsonColumn(server_default={}, comment="世坤返回的因子数据")

    UniqueConstraint(expression, setting_str, name="uq_expression_setting")    
