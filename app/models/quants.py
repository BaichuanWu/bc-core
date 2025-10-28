from typing import Set

from bc_fastkit.model import (
    BINARY,
    VARCHAR,
    BaseModel,
    Column,
    Computed,
    DefaultDecimalColumn,
    DefaultIdColumn,
    DefaultJsonColumn,
    DefaultTextColumn,
    DefaultTimeColumn,
    DefaultTypeColumn,
    NotNullColumn,
    UniqueConstraint,
    classproperty,
)


class QuantsInspirationModel(BaseModel):
    title = NotNullColumn(VARCHAR(63), comment="标题")
    link = NotNullColumn(VARCHAR(255), server_default="", comment="链接")
    content = DefaultTextColumn(comment="内容")


class QuantsAlphaTemplateModel(BaseModel):
    title = NotNullColumn(VARCHAR(63), comment="标题")
    inspiration_id = DefaultIdColumn(comment="灵感ID")
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: 一阶, 2: 二阶, 3: 三阶")
    description = NotNullColumn(VARCHAR(512), comment="描述")
    expression = DefaultTextColumn(comment="内容")


class QuantsWqbAlphaTaskModel(BaseModel):
    template_id = DefaultIdColumn(comment="模板ID")
    parent_alpha_id = DefaultIdColumn(comment="父因子ID")
    expression = DefaultTextColumn(comment="alpha 表达式")
    data_field = NotNullColumn(VARCHAR(511), comment="数据字段")
    setting_str = NotNullColumn(VARCHAR(511), comment="参数设置字符串")
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: 一阶, 2: 二阶, 3: 三阶")
    state = DefaultTypeColumn(
        comment="状态: 0: 未知, 1: 待提交, 2: 提交中, 3: 已完成, 4: 失败"
    )
    fail_count = DefaultTypeColumn(comment="失败次数")
    fail_reason = NotNullColumn(VARCHAR(255), server_default="", comment="失败原因")
    wqb_simulate_id = NotNullColumn(VARCHAR(63), index=True, comment="世坤模拟ID")
    wqb_alpha_id = NotNullColumn(VARCHAR(63), unique=True, comment="世坤因子ID")
    alpha_hash = Column(
        BINARY(32),
        Computed("UNHEX(SHA2(CONCAT(expression, setting_str), 256))", persisted=True),
        unique=True,
        comment="表达式和设置的哈希",
    )


class QuantsWqbAlphaModel(BaseModel):
    STATE_INIT = 0
    STATE_PENDING = 1
    STATE_SIMULATING = 5
    STATE_SIMULATED = 10
    STATE_SELF_CHECKED = 12
    STATE_CHECKED = 15
    STATE_ACTIVE = 20

    template_id = DefaultIdColumn(comment="模板ID")
    batch_no = NotNullColumn(VARCHAR(63), server_default="", comment="批次ID")
    parent_id = DefaultIdColumn(comment="父alphaID")
    typ = DefaultTypeColumn(
        comment="类型: 0: 未知, 1: 一阶, 2: 二阶, 3: 三阶, 10: 负值模板"
    )
    expression = DefaultTextColumn(comment="alpha 表达式")
    setting_str = NotNullColumn(VARCHAR(511), comment="参数设置字符串")
    expression_hash = NotNullColumn(VARCHAR(127), comment="setting和expression哈希值")
    data_field = NotNullColumn(VARCHAR(511), comment="数据字段")
    region = NotNullColumn(VARCHAR(63), comment="适用市场")
    universe = NotNullColumn(VARCHAR(63), comment="适用股票池")
    delay = DefaultTypeColumn(comment="延迟天数")
    description = DefaultTextColumn(comment="描述")
    operator_count = DefaultTypeColumn(comment="操作符数")
    sharpe = DefaultDecimalColumn(comment="夏普比率")
    fitness = DefaultDecimalColumn(comment="适应度")
    level = DefaultTypeColumn(comment="级别")
    state = DefaultTypeColumn(
        comment="状态: 0: 初始, 1: 待回测, 5: 测试中, 10: 回测完, 12: 自检完, 15: 审核完, 20: 已激活"
    )
    wqb_simulate_time = DefaultTimeColumn(comment="wqb最后一次模拟时间")
    wqb_simulate_id = NotNullColumn(VARCHAR(63), index=True, comment="世坤模拟ID")
    wqb_alpha_id = NotNullColumn(VARCHAR(63), unique=True, comment="世坤因子ID")
    wqb_data = DefaultJsonColumn(server_default={}, comment="世坤返回的因子数据")
    wqb_create_time = DefaultTimeColumn(comment="wqb创建时间")
    wqb_commit_time = DefaultTimeColumn(comment="wqb提交时间")
    wqb_pnl_shape = DefaultTypeColumn(comment="收益形态:-1: 异常, 0: 未捕捉, 1: 正常")
    wqb_pnl_data = DefaultJsonColumn(server_default={}, comment="收益数据")

    @classproperty
    def immutable_column_names(cls) -> Set[str]:
        return super().immutable_column_names | {
            "alpha_hash",
            "expression",
            "date_field" "setting_str",
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

    @property
    def to_wqb(self) -> dict:
        return {
            "id": self.wqb_alpha_id,
            "regular": {
                "code": self.expression,
                "operatorCount": self.operator_count,
                "description": self.description,
            },
            "settings": {
                "region": self.region,
                "universe": self.universe,
                "delay": self.delay,
            },
            "status": self.state,
        }


class QuantsWqbOperatorModel(BaseModel):
    name = NotNullColumn(VARCHAR(127), unique=True, comment="操作名")
    category = NotNullColumn(VARCHAR(127), comment="类型名")
    scope = DefaultJsonColumn(server_default=[], comment="作用域")
    description = NotNullColumn(VARCHAR(511), server_default="", comment="描述")
    definition = NotNullColumn(VARCHAR(511), server_default="", comment="定义")
    documentation = NotNullColumn(VARCHAR(511), server_default="", comment="文档链接")
    level = NotNullColumn(VARCHAR(63), server_default="", comment="级别")


class QuantsWqbUniverseModel(BaseModel):
    name = NotNullColumn(VARCHAR(127), comment="操作名")
    region = NotNullColumn(VARCHAR(127), comment="地区")
    delay = DefaultTypeColumn(comment="延迟天数")


class QuantsWqbDataFieldModel(BaseModel):
    region = NotNullColumn(VARCHAR(127), comment="地区")
    universe = NotNullColumn(VARCHAR(127), comment="操作名")
    delay = DefaultTypeColumn(comment="延迟天数")
    category = NotNullColumn(VARCHAR(127), index=True, comment="类别")
    sub_category = NotNullColumn(VARCHAR(127), index=True, comment="子类别")
    dataset_id = NotNullColumn(VARCHAR(127), index=True, comment="数据集ID")
    name = NotNullColumn(VARCHAR(127), comment="字段名称")
    description = DefaultTextColumn(comment="描述")
    typ = DefaultTypeColumn(comment="类型: 0: 未知, 1: matrix, 2: vertor")
    payramid_multiplier = DefaultDecimalColumn(comment="金字塔主题乘数")
    coverage = DefaultDecimalColumn(comment="覆盖率")
    user_count = DefaultDecimalColumn(comment="使用该字段的用户数")
    alpha_count = DefaultDecimalColumn(comment="使用该字段的因子数")

    @classmethod
    def typ_from_str(cls, typ_str: str) -> int:
        mapping = {
            "matrix": 1,
            "vector": 2,
        }
        return mapping.get(typ_str.lower(), 0)

    UniqueConstraint(
        region,
        universe,
        delay,
        dataset_id,
        name,
        name="uix_wqb_data_field_unique",
    )
