from bc_fastkit.model import (
    VARCHAR,
    BaseModel,
    DefaultIdColumn,
    DefaultJsonColumn,
    DefaultTextColumn,
    DefaultTypeColumn,
    NotNullColumn,
    UniqueConstraint,
)


class QuantsInspirationModel(BaseModel):
    title = NotNullColumn(VARCHAR(63), comment="标题")
    link = NotNullColumn(VARCHAR(255), server_default="", comment="链接")
    content = DefaultTextColumn(comment="内容")


class QuantsAlphaTemplateModel(BaseModel):
    title = NotNullColumn(VARCHAR(63), comment="标题")
    inspiration_id = DefaultIdColumn(comment="灵感ID")
    description = NotNullColumn(VARCHAR(255), comment="描述")
    expression = DefaultTextColumn(comment="内容")


class QuantsWqbAlphaTaskModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    field_data = DefaultJsonColumn(server_default={}, comment="字段数据")
    setting_data = DefaultJsonColumn(server_default={}, comment="设置数据")


class QuantsWqbAlphaModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    task_id = DefaultIdColumn(comment="任务ID")
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


class QuantsWqbOperatorModel(BaseModel):
    name = NotNullColumn(VARCHAR(127), unique=True, comment="操作名")
    category = NotNullColumn(VARCHAR(127), comment="类型名")
    scope = DefaultJsonColumn(server_default=[], comment="作用域")
    description = NotNullColumn(VARCHAR(511), server_default="", comment="描述")
    definition = NotNullColumn(VARCHAR(511), server_default="", comment="定义")
    documentation = NotNullColumn(VARCHAR(511), server_default="", comment="文档链接")
    level = NotNullColumn(VARCHAR(63), server_default="", comment="级别")


class QuantsWqbUniverseModel(BaseModel):
    name = NotNullColumn(VARCHAR(127), unique=True, comment="操作名")
    region = NotNullColumn(VARCHAR(127), comment="地区")
    delay = DefaultTypeColumn(comment="延迟天数")
