from typing import Set

from bc_fastkit.model import (
    BINARY,
    DECIMAL,
    VARCHAR,
    BaseModel,
    Column,
    Computed,
    DefaultIdColumn,
    DefaultJsonColumn,
    DefaultTextColumn,
    DefaultTypeColumn,
    NotNullColumn,
    classproperty,
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
    expression = DefaultTextColumn(comment="alpha 表达式")
    setting_str = NotNullColumn(VARCHAR(511), comment="参数设置字符串")
    wqb_simulate_id = NotNullColumn(VARCHAR(63), index=True, comment="世坤模拟ID")
    wqb_alpha_id = NotNullColumn(VARCHAR(63), unique=True, comment="世坤因子ID")
    alpha_hash = Column(
        BINARY(32),
        Computed("UNHEX(SHA2(CONCAT(expression, setting_str), 256))", persisted=True),
        unique=True,
        comment="表达式和设置的哈希",
    )


class QuantsWqbAlphaModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    parent_id = DefaultIdColumn(comment="模板ID")
    task_id = DefaultIdColumn(comment="任务ID")
    expression = DefaultTextColumn(comment="alpha 表达式")
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: 因子, 2: 策略")
    region = NotNullColumn(VARCHAR(63), comment="适用市场")
    universe = NotNullColumn(VARCHAR(63), comment="适用股票池")
    delay = DefaultTypeColumn(comment="延迟天数")
    setting_str = NotNullColumn(VARCHAR(511), comment="参数设置字符串")
    description = DefaultTextColumn(comment="描述")
    operator_count = DefaultTypeColumn(comment="操作符数")
    sharpe = Column(
        DECIMAL(20, 8),
        Computed(
            "COALESCE(CAST(JSON_EXTRACT(wbq_data, '$.is.sharpe') AS DECIMAL(20,8)), 0)",
            persisted=True,
        ),
        comment="夏普比率",
    )
    fitness = Column(
        DECIMAL(20, 8),
        Computed(
            "COALESCE(CAST(JSON_EXTRACT(wbq_data, '$.is.fitness') AS DECIMAL(20,8)), 0)",
            persisted=True,
        ),
        comment="适应度",
    )
    level = DefaultTypeColumn(comment="级别")
    pnl_shape = DefaultTypeColumn(comment="收益形态:-1: 异常, 0: 未捕捉, 1: 正常")
    pnl_data = DefaultJsonColumn(server_default={}, comment="收益数据")
    wqb_alpha_id = NotNullColumn(VARCHAR(63), unique=True, comment="世坤因子ID")
    state = DefaultTypeColumn(comment="状态: 0: 未知, 1: 开发中, 2: 测试中, 3: 已上线")
    wbq_data = DefaultJsonColumn(server_default={}, comment="世坤返回的因子数据")
    wbq_create_time = Column(
        VARCHAR(63),
        Computed(
            "COALESCE(CAST(JSON_UNQUOTE(JSON_EXTRACT(wbq_data, '$.dateCreated')) AS VARCHAR(63)), '')",
            persisted=True,
        ),
        comment="创建时间",
        index=True,
    )

    @classproperty
    def immutable_column_names(cls) -> Set[str]:
        return super().immutable_column_names | {
            "alpha_hash",
            "expression",
            "setting_str",
            "typ",
            "region",
            "universe",
            "delay",
        }

    @classmethod
    def state_from_str(cls, state_str: str) -> int:
        mapping = {
            "active": 20,
            "unsubmitted": 10,
        }
        return mapping.get(state_str.lower(), 0)


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
