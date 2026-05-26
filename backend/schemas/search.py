"""C3 复杂检索 —— 请求/响应 Schema"""
from pydantic import BaseModel, field_validator
from typing import Union, Optional


# ── 运算符白名单 ──
VALID_OPERATORS = {"equals", "not_equals", "in", "not_in", "gt", "lt", "gte", "lte", "range"}
VALID_RELATIONS = {"生", "克", "合", "冲", "半合", "三合", "=", "长生", "帝旺", "墓", "绝"}
VALID_OBJECT_TYPES = {"yao_object", "time_object", "condition_group_ref"}
VALID_LOGIC_TYPES = {"condition", "and", "or", "not", "(", ")"}


class Condition(BaseModel):
    """单个检索条件"""
    id: str
    field: str
    operator: str
    value: Union[str, list[str]]
    scope: Optional[str] = None  # ben_gua / zhi_gua / bian_yao / yimao / zengshan

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
    middle_type: Optional[str] = None  # 三合专用：中间对象类型
    middle_value: Optional[str] = None  # 三合专用：中间对象值
    relation: str         # 生/克/合/冲/半合/三合/=/长生/帝旺/墓/绝
    right_type: str       # yao_object / time_object / condition_group_ref
    right_value: str      # 右对象值
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


class SearchRequest(BaseModel):
    """检索请求"""
    conditions: list[Union[Condition, RelationCondition]] = []
    logic: list[LogicItem] = []
    pagination: Pagination = Pagination()


class SearchResponse(BaseModel):
    """检索响应"""
    code: int = 200
    data: Optional[dict] = None
    message: str = "success"
