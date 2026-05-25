"""C3 复杂检索核心——动态 SQL 生成 + 执行"""
from sqlmodel import Session, text
from backend.schemas.search import SearchRequest, Condition, RelationCondition, LogicItem, SearchResponse

# ── 字段映射白名单 ──
# field_name → (table_alias, column_expression, needs_yao_join, needs_shensha_join, needs_gua_join, needs_time_join)
FIELD_MAP: dict[str, dict] = {
    # 爻属性（需 guali_yao）
    "yao_position":    {"sql": "y.yao_position",      "joins": {"y"}},
    "ben_yao_type":    {"sql": "y.ben_yao_type",      "joins": {"y"}},
    "ben_liuqin":      {"sql": "y.ben_liuqin",        "joins": {"y"}},
    "ben_dizhi":       {"sql": "y.ben_dizhi",         "joins": {"y"}},
    "ben_shi_ying":    {"sql": "y.ben_shi_ying",      "joins": {"y"}},
    "ben_tiangan":     {"sql": "y.ben_tiangan",       "joins": {"y"}},
    "zhi_liuqin":      {"sql": "y.zhi_liuqin",        "joins": {"y"}},
    "zhi_dizhi":       {"sql": "y.zhi_dizhi",         "joins": {"y"}},
    "zhi_shi_ying":    {"sql": "y.zhi_shi_ying",      "joins": {"y"}},
    "zhi_yao_type":    {"sql": "y.zhi_yao_type",      "joins": {"y"}},
    "yimao_liuqin":    {"sql": "y.yimao_liuqin",      "joins": {"y"}},
    "yimao_dizhi":     {"sql": "y.yimao_dizhi",       "joins": {"y"}},
    "zengshan_liuqin": {"sql": "y.zengshan_liuqin",   "joins": {"y"}},
    "zengshan_dizhi":  {"sql": "y.zengshan_dizhi",    "joins": {"y"}},
    "is_dong":         {"sql": "y.is_dong",            "joins": {"y"}},
    "is_an_dong":      {"sql": "y.is_an_dong",         "joins": {"y"}},
    "liushen":         {"sql": "y.liushen",            "joins": {"y"}},
    "zengshan_exists": {"sql": "y.zengshan_exists",    "joins": {"y"}},

    # 卦类（需 guali_gua）
    "ben_palace":       {"sql": "g.ben_palace",        "joins": {"g"}},
    "ben_palace_type":  {"sql": "g.ben_palace_type",   "joins": {"g"}},
    "ben_special_type": {"sql": "g.ben_special_type",  "joins": {"g"}},
    "zhi_palace":       {"sql": "g.zhi_palace",        "joins": {"g"}},
    "zhi_palace_type":  {"sql": "g.zhi_palace_type",   "joins": {"g"}},
    "zhi_special_type": {"sql": "g.zhi_special_type",  "joins": {"g"}},
    "fan_yin_yimao":    {"sql": "g.fan_yin_yimao",     "joins": {"g"}},
    "fan_yin_yaobian":  {"sql": "g.fan_yin_yaobian",   "joins": {"g"}},
    "fu_yin":           {"sql": "g.fu_yin",            "joins": {"g"}},

    # 时间（需 guali_time）
    "year_pillar":  {"sql": "t.year_pillar",  "joins": {"t"}},
    "year_gan":     {"sql": "t.year_gan",     "joins": {"t"}},
    "year_zhi":     {"sql": "t.year_zhi",     "joins": {"t"}},
    "month_pillar": {"sql": "t.month_pillar", "joins": {"t"}},
    "month_gan":    {"sql": "t.month_gan",    "joins": {"t"}},
    "month_zhi":    {"sql": "t.month_zhi",    "joins": {"t"}},
    "day_pillar":   {"sql": "t.day_pillar",   "joins": {"t"}},
    "day_gan":      {"sql": "t.day_gan",      "joins": {"t"}},
    "day_zhi":      {"sql": "t.day_zhi",      "joins": {"t"}},
    "xun_kong":     {"sql": "t.xun_kong",     "joins": {"t"}},
}

# 神煞字段映射 → guali_shensha 表的 (is_field, dai_field)
SHENSHA_MAP = {
    "is_ganlu":  ("is_ganlu",  "dai_ganlu"),
    "is_yima":   ("is_yima",   "dai_yima"),
    "is_yangren":("is_yangren","dai_yangren"),
    "is_taohua": ("is_taohua", "dai_taohua"),
    "ganlu":     ("is_ganlu",  "dai_ganlu"),
    "yima":      ("is_yima",   "dai_yima"),
    "yangren":   ("is_yangren","dai_yangren"),
    "taohua":    ("is_taohua", "dai_taohua"),
}

# yao_object 六爻对象 → 查找方式
YAO_OBJECTS = {"世爻", "应爻", "妻财爻", "官鬼爻", "父母爻", "兄弟爻", "子孙爻"}


def _parse_yao_object(value: str) -> tuple[str, str]:
    """世爻 → ('ben_shi_ying', '世')，妻财爻 → ('ben_liuqin', '妻财')"""
    if value == "世爻":
        return "ben_shi_ying", "世"
    if value == "应爻":
        return "ben_shi_ying", "应"
    for qin in ["妻财", "官鬼", "父母", "兄弟", "子孙"]:
        if value == f"{qin}爻":
            return "ben_liuqin", qin
    return "ben_liuqin", value


def _build_condition_clause(cond: Condition, params: dict, idx: int) -> str:
    """单个条件 → WHERE 子句片段，返回 SQL 文本"""
    field_info = FIELD_MAP.get(cond.field)
    if not field_info:
        raise ValueError(f"未知字段: {cond.field}")

    sql_col = field_info["sql"]
    op = cond.operator
    key = f"v{idx}"
    val = cond.value

    clauses = []
    # scope 过滤：按来源范围限定
    if cond.scope:
        scope_clause = _scope_filter(cond.scope, field_info)
        if scope_clause:
            clauses.append(scope_clause)

    # 运算符映射
    if op == "equals":
        clauses.append(f"{sql_col} = :{key}")
        params[key] = val
    elif op == "not_equals":
        clauses.append(f"({sql_col} != :{key} OR {sql_col} IS NULL)")
        params[key] = val
    elif op == "in":
        if not isinstance(val, list):
            val = [val]
        placeholders = []
        for vi, vv in enumerate(val):
            pk = f"{key}_{vi}"
            placeholders.append(f":{pk}")
            params[pk] = vv
        clauses.append(f"{sql_col} IN ({','.join(placeholders)})")
    elif op == "not_in":
        if not isinstance(val, list):
            val = [val]
        placeholders = []
        for vi, vv in enumerate(val):
            pk = f"{key}_{vi}"
            placeholders.append(f":{pk}")
            params[pk] = vv
        clauses.append(f"({sql_col} NOT IN ({','.join(placeholders)}) OR {sql_col} IS NULL)")
    elif op == "gt":
        clauses.append(f"{sql_col} > :{key}")
        params[key] = val
    elif op == "lt":
        clauses.append(f"{sql_col} < :{key}")
        params[key] = val
    elif op == "gte":
        clauses.append(f"{sql_col} >= :{key}")
        params[key] = val
    elif op == "lte":
        clauses.append(f"{sql_col} <= :{key}")
        params[key] = val
    elif op == "range":
        if isinstance(val, list) and len(val) == 2:
            clauses.append(f"{sql_col} >= :{key}_lo")
            clauses.append(f"{sql_col} <= :{key}_hi")
            params[f"{key}_lo"] = val[0]
            params[f"{key}_hi"] = val[1]
        else:
            raise ValueError(f"range 运算符需要 2 个值: {val}")
    else:
        raise ValueError(f"不支持的运算符: {op}")

    return " AND ".join(clauses)


def _scope_filter(scope: str, field_info: dict) -> str:
    """根据 scope 限定爻的来源范围"""
    if scope == "ben_gua":
        return "1=1"  # 本卦爻默认无额外过滤
    elif scope == "bian_yao":
        return "y.is_dong = TRUE"
    elif scope == "zhi_gua":
        return "y.is_dong = FALSE"
    elif scope == "yimao":
        return "TRUE"  # yimao 字段自带来源
    elif scope == "zengshan":
        return "y.zengshan_exists = TRUE"
    return ""


def _build_shensha_clause(field: str, mode: str, obj_field: str, obj_value: str, params: dict, idx: int) -> str:
    """神煞条件：FIND_IN_SET 方式"""
    prefix_map = {"ben_gua": "ben", "zhi_gua": "zhi", "yimao": "yimao", "zengshan": "zengshan", "bian_yao": "ben"}
    shensha_info = SHENSHA_MAP.get(field.replace("is_", "").replace("dai_", ""))
    if not shensha_info:
        raise ValueError(f"未知神煞字段: {field}")

    is_col, dai_col = shensha_info
    # mode: "是"→is, "带"→dai, "是或带"→(is != '' OR dai != '')
    clauses = []
    for scope_prefix in ["ben", "zhi", "yimao", "zengshan"]:
        if mode in ("是", "是或带"):
            col = f"s.{scope_prefix}_{is_col}"
            clauses.append(f"(FIND_IN_SET(y.yao_position, {col}) > 0)")
        if mode in ("带", "是或带"):
            col = f"s.{scope_prefix}_{dai_col}"
            clauses.append(f"(FIND_IN_SET(y.yao_position, {col}) > 0)")

    sub = " OR ".join(clauses) if clauses else "FALSE"

    # 同时需要匹配对象（如"妻财爻"）
    if obj_value in YAO_OBJECTS:
        obj_col, obj_val = _parse_yao_object(obj_value)
        return f"({sub}) AND y.{obj_col} = :sobj{idx}"

    if obj_value:
        params[f"sobj{idx}"] = obj_value
        return f"({sub})"

    return f"({sub})"


def _build_relation_clause(rel: RelationCondition, params: dict, idx: int) -> str:
    """关系条件 → MySQL 存储函数调用"""
    relation = rel.relation
    left_val = rel.left_value
    right_val = rel.right_value
    bureau = rel.bureau

    # 获取地支值的方式：yao_object 查字段，time_object 查 guali_time
    def resolve_dz(obj_type, obj_value, suffix):
        if obj_type == "yao_object":
            col, val = _parse_yao_object(obj_value)
            # 找到对应爻的地支字段
            dz_map = {"ben_shi_ying": "y.ben_dizhi", "ben_liuqin": "y.ben_dizhi"}
            return f"(SELECT y_inner.ben_dizhi FROM guali_yao y_inner WHERE y_inner.guali_id = guali.id AND y_inner.{col} = :{suffix}_obj)"
        elif obj_type == "time_object":
            tm_map = {"年支": "t.year_zhi", "月支": "t.month_zhi", "日支": "t.day_zhi"}
            return tm_map.get(obj_value, f":{suffix}_dz")
        elif obj_type == "condition_group_ref":
            # 返回引用条件组的爻位集合的子查询
            return f"(SELECT y_ref.ben_dizhi FROM guali_yao y_ref WHERE y_ref.guali_id = guali.id AND y_ref.id IN (/* ref to {obj_value} */))"
        return f":{suffix}_dz"

    dz1 = resolve_dz(rel.left_type, rel.left_value, f"l{idx}")
    dz2 = resolve_dz(rel.right_type, rel.right_value, f"r{idx}")

    if relation in ("生", "克"):
        func = "check_sheng" if relation == "生" else "check_ke"
        return f"{func}({dz1}, {dz2}) = TRUE"
    elif relation == "合":
        return f"check_he({dz1}, {dz2}) = TRUE"
    elif relation == "冲":
        return f"check_chong({dz1}, {dz2}) = TRUE"
    elif relation == "半合":
        return f"check_banhe({dz1}, {dz2}) = TRUE"
    elif relation == "三合":
        b = f"'{bureau}'" if bureau else "'不限'"
        # 三合需要 3 个地支，第三个从 bureau 推算或额外参数
        return f"check_sanhe({dz1}, {dz2}, {b}) = TRUE"
    elif relation == "=":
        return f"{dz1} = {dz2}"
    elif relation in ("长生", "帝旺", "墓", "绝"):
        return f"check_shengwang({dz1}, {dz2}, '{relation}') = TRUE"

    return "FALSE"


def _collect_joins(conditions: list) -> set[str]:
    """收集所需 JOIN"""
    joins: set[str] = set()
    for cond in conditions:
        if isinstance(cond, RelationCondition):
            joins.add("y")
            continue
        info = FIELD_MAP.get(cond.field)
        if info:
            joins.update(info.get("joins", set()))
        # 神煞字段
        if cond.field in SHENSHA_MAP or cond.field.replace("is_", "").replace("dai_", "") in SHENSHA_MAP:
            joins.add("s")
            joins.add("y")
    return joins


def _build_join_clauses(joins: set[str]) -> str:
    clauses = []
    if "y" in joins:
        clauses.append("LEFT JOIN guali_yao y ON y.guali_id = guali.id")
    if "s" in joins:
        clauses.append("LEFT JOIN guali_shensha s ON s.guali_id = guali.id")
    if "g" in joins:
        clauses.append("LEFT JOIN guali_gua g ON g.guali_id = guali.id")
    if "t" in joins:
        clauses.append("LEFT JOIN guali_time t ON t.guali_id = guali.id")
    return "\n".join(clauses)


def execute_search(session: Session, request: SearchRequest) -> SearchResponse:
    conditions = request.conditions
    logic = request.logic
    pagination = request.pagination

    if not conditions:
        # 无条件→返回全部卦例
        count_sql = "SELECT COUNT(*) FROM guali"
        total = session.exec(text(count_sql)).scalar() or 0
        pg = pagination.page
        ps = pagination.page_size
        rows = session.exec(
            text("SELECT * FROM guali ORDER BY zhanwen_time DESC LIMIT :limit OFFSET :offset").bindparams(limit=ps, offset=(pg - 1) * ps)
        ).mappings().all()
        return SearchResponse(
            data={"results": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}
        )

    # 收集 JOIN
    joins = _collect_joins(conditions)
    # 确保主表
    if "guali" not in joins:
        pass  # FROM 始终是 guali

    join_sql = _build_join_clauses(joins)

    # 构建 WHERE 子句
    params: dict = {}
    where_parts: list[str] = []
    cond_clauses: dict[str, str] = {}  # id → SQL clause

    for i, cond in enumerate(conditions):
        if isinstance(cond, RelationCondition):
            clause = _build_relation_clause(cond, params, i)
        else:
            clause = _build_condition_clause(cond, params, i)
        cond_clauses[cond.id] = clause

    # 解析逻辑链
    where_sql = _assemble_logic(logic, cond_clauses) if logic else " AND ".join(cond_clauses.values())

    # 完整 SQL
    base_sql = f"FROM guali {join_sql}"
    if where_sql:
        base_sql += f" WHERE {where_sql}"

    count_sql = f"SELECT COUNT(DISTINCT guali.id) {base_sql}"
    total = session.exec(text(count_sql).bindparams(**params)).scalar() or 0

    page = pagination.page
    page_size = pagination.page_size
    query_sql = f"SELECT DISTINCT guali.* {base_sql} ORDER BY guali.zhanwen_time DESC LIMIT :_limit OFFSET :_offset"
    params["_limit"] = page_size
    params["_offset"] = (page - 1) * page_size

    rows = session.exec(text(query_sql).bindparams(**params)).mappings().all()

    return SearchResponse(
        data={"results": [dict(r) for r in rows], "total": total, "page": page, "page_size": page_size}
    )


def _assemble_logic(logic: list[LogicItem], cond_clauses: dict[str, str]) -> str:
    """将逻辑链转为 SQL WHERE 表达式"""
    if not logic:
        return " AND ".join(cond_clauses.values())

    parts: list[str] = []
    for item in logic:
        if item.type == "condition":
            clause = cond_clauses.get(item.id or "", "TRUE")
            parts.append(f"({clause})")
        elif item.type in ("and", "or"):
            if parts:
                parts.append(f" {item.type.upper()} ")
        elif item.type == "not":
            parts.append("NOT ")
        elif item.type == "(":
            parts.append("(")
        elif item.type == ")":
            parts.append(")")

    return "".join(parts)
