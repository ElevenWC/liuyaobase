"""C3 复杂检索 —— 请求/响应 Schema"""
from pydantic import BaseModel, field_validator
from typing import Union, Optional, Literal


# ── 运算符白名单 ──
VALID_OPERATORS = {"equals", "not_equals", "in", "not_in", "gt", "lt", "gte", "lte", "range"}
VALID_RELATIONS = {"生", "克", "合", "冲", "半合", "三合", "=", "长生", "帝旺", "墓", "绝"}
VALID_OBJECT_TYPES = {"yao_object", "time_object", "condition_group_ref"}
VALID_LOGIC_TYPES = {"condition", "condition_group", "and", "or", "not", "(", ")"}
VALID_SOURCES = {"本卦", "变爻", "之卦(静爻)", "易冒伏神", "增删伏神"}
VALID_YONGSHEN = {"妻财", "官鬼", "父母", "兄弟", "子孙"}
VALID_FEISHEN_TYPES = {"增删飞神", "易冒飞神"}


class Condition(BaseModel):
    """单个检索条件"""
    id: str
    field: str
    operator: str
    value: Union[str, list[str]]
    scope: Optional[str] = None  # ben_gua / zhi_gua / bian_yao / yimao / zengshan
    countAttr: Optional[str] = None   # 数目判断专用：统计属性
    countValue: Optional[str] = None  # 数目判断专用：属性值
    tagId: Optional[int] = None       # 标签筛选专用：一级标签ID
    tagId2: Optional[int] = None      # 标签筛选专用：二级标签ID

    @field_validator("operator")
    @classmethod
    def check_operator(cls, v: str) -> str:
        if v not in VALID_OPERATORS:
            raise ValueError(f"无效运算符: {v}，支持: {VALID_OPERATORS}")
        return v


class RelationCondition(Condition):
    """关系条件——两个/三个对象之间的关系判断"""
    left_type: str        # yao_object / time_object / condition_group_ref
    left_value: str       # 左对象值
    left_scope: Optional[str] = None  # yao_object 来源：ben_gua/zhi_gua/bian_yao/yimao/zengshan
    middle_type: Optional[str] = None  # 三合专用：中间对象类型
    middle_value: Optional[str] = None  # 三合专用：中间对象值
    middle_scope: Optional[str] = None
    relation: str         # 生/克/合/冲/半合/三合/=/长生/帝旺/墓/绝
    right_type: str       # yao_object / time_object / condition_group_ref
    right_value: str      # 右对象值
    right_scope: Optional[str] = None
    bureau: Optional[str] = None  # 三合局类型（水/木/火/金），仅三合时有效

    @field_validator("relation")
    @classmethod
    def check_relation(cls, v: str) -> str:
        if v not in VALID_RELATIONS:
            raise ValueError(f"无效关系: {v}，支持: {VALID_RELATIONS}")
        return v

    @field_validator("left_type", "right_type")
    @classmethod
    def check_object_type(cls, v: str) -> str:
        if v not in VALID_OBJECT_TYPES:
            raise ValueError(f"无效对象类型: {v}，支持: {VALID_OBJECT_TYPES}")
        return v


class LogicItem(BaseModel):
    """逻辑链节点"""
    type: str   # "condition" / "and" / "or" / "not" / "(" / ")"
    id: Optional[str] = None  # 当 type=="condition" 时指向 Condition.id

    @field_validator("type")
    @classmethod
    def check_type(cls, v: str) -> str:
        if v not in VALID_LOGIC_TYPES:
            raise ValueError(f"无效逻辑类型: {v}，支持: {VALID_LOGIC_TYPES}")
        return v


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 50


# ── 条件组 ──

class SubCondition(BaseModel):
    """条件组内的子条件，使用通用字段名（不区分来源前缀）"""
    field: str          # liuqin / dizhi / shi_ying / yao_type / tiangan / yao_position / is_dong / is_an_dong / liushen / zengshan_exists
    operator: str
    value: Union[str, list[str]]

    @field_validator("operator")
    @classmethod
    def check_operator(cls, v: str) -> str:
        if v not in VALID_OPERATORS:
            raise ValueError(f"无效运算符: {v}")
        return v


class SourceConditions(BaseModel):
    """同爻位条件组中单个来源的配置"""
    source: str          # 本卦 / 变爻 / 之卦(静爻) / 易冒伏神 / 增删伏神
    conditions: list[SubCondition] = []

    @field_validator("source")
    @classmethod
    def check_source(cls, v: str) -> str:
        if v not in VALID_SOURCES:
            raise ValueError(f"无效来源: {v}")
        return v


class SameYaoGroup(BaseModel):
    """同一爻条件组——多来源 OR 逻辑"""
    id: str
    groupType: Literal["same_yao"] = "same_yao"
    sources: list[str] = ["本卦"]
    conditions: list[SubCondition] = []


class SamePositionGroup(BaseModel):
    """同爻位条件组——同爻位 AND 逻辑"""
    id: str
    groupType: Literal["same_position"] = "same_position"
    position: int = 1   # 爻位 1-6
    sources: list[SourceConditions] = []


class FeishenGroup(BaseModel):
    """飞神条件组"""
    id: str
    groupType: Literal["feishen"] = "feishen"
    feishenType: str = "增删飞神"     # 增删飞神 / 易冒飞神
    yongshen: str = "妻财"           # 妻财 / 官鬼 / 父母 / 兄弟 / 子孙

    @field_validator("feishenType")
    @classmethod
    def check_feishen_type(cls, v: str) -> str:
        if v not in VALID_FEISHEN_TYPES:
            raise ValueError(f"无效飞神类型: {v}")
        return v

    @field_validator("yongshen")
    @classmethod
    def check_yongshen(cls, v: str) -> str:
        if v not in VALID_YONGSHEN:
            raise ValueError(f"无效用神: {v}")
        return v


class SearchRequest(BaseModel):
    """检索请求"""
    conditions: list[Union[SameYaoGroup, SamePositionGroup, FeishenGroup, Condition, RelationCondition]] = []
    logic: list[LogicItem] = []
    pagination: Pagination = Pagination()
    sort_order: str = "desc"  # "desc" 或 "asc"


class SearchResponse(BaseModel):
    """检索响应"""
    code: int = 200
    data: Optional[dict] = None
    message: str = "success"
