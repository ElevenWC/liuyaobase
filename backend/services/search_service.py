"""C3 复杂检索核心——动态 SQL 生成 + 执行"""
from sqlmodel import Session, text
from backend.schemas.search import SearchRequest, Condition, RelationCondition, LogicItem, SearchResponse, SameYaoGroup, SamePositionGroup, FeishenGroup, SubCondition

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

# ── 条件组：通用字段名 × 来源 → SQL 列名 ──
GENERIC_YAO_FIELDS: dict[str, dict[str, str | None]] = {
    "liuqin": {
        "本卦": "y.ben_liuqin", "变爻": "y.zhi_liuqin",
        "之卦(静爻)": "y.zhi_liuqin", "易冒伏神": "y.yimao_liuqin",
        "增删伏神": "y.zengshan_liuqin",
    },
    "dizhi": {
        "本卦": "y.ben_dizhi", "变爻": "y.zhi_dizhi",
        "之卦(静爻)": "y.zhi_dizhi", "易冒伏神": "y.yimao_dizhi",
        "增删伏神": "y.zengshan_dizhi",
    },
    "shi_ying": {
        "本卦": "y.ben_shi_ying", "变爻": "y.zhi_shi_ying",
        "之卦(静爻)": "y.zhi_shi_ying", "易冒伏神": None,
        "增删伏神": None,
    },
    "yao_type": {
        "本卦": "y.ben_yao_type", "变爻": "y.zhi_yao_type",
        "之卦(静爻)": "y.zhi_yao_type", "易冒伏神": None,
        "增删伏神": None,
    },
    "tiangan": {
        "本卦": "y.ben_tiangan", "变爻": "y.zhi_tiangan",
        "之卦(静爻)": "y.zhi_tiangan", "易冒伏神": None,
        "增删伏神": None,
    },
    "yao_position": {
        "本卦": "y.yao_position", "变爻": "y.yao_position",
        "之卦(静爻)": "y.yao_position", "易冒伏神": "y.yao_position",
        "增删伏神": "y.yao_position",
    },
    "is_dong": {
        "本卦": "y.is_dong", "变爻": None, "之卦(静爻)": None,
        "易冒伏神": None, "增删伏神": None,
    },
    "is_an_dong": {
        "本卦": "y.is_an_dong", "变爻": None, "之卦(静爻)": None,
        "易冒伏神": None, "增删伏神": None,
    },
    "liushen": {
        "本卦": "y.liushen", "变爻": "y.liushen",
        "之卦(静爻)": "y.liushen", "易冒伏神": "y.liushen",
        "增删伏神": "y.liushen",
    },
    "zengshan_exists": {
        "本卦": None, "变爻": None, "之卦(静爻)": None,
        "易冒伏神": None, "增删伏神": "y.zengshan_exists",
    },
}

# 来源中文名 → scope 常量
SOURCE_TO_SCOPE = {
    "本卦": "ben_gua", "变爻": "bian_yao", "之卦(静爻)": "zhi_gua",
    "易冒伏神": "yimao", "增删伏神": "zengshan",
}


def _norm_bool(val):
    """MySQL TINYINT 列无法匹配字符串 'true'/'false'，统一转为 1/0"""
    if isinstance(val, str) and val.lower() in ('true', 'false'):
        return 1 if val.lower() == 'true' else 0
    return val


def _build_sub_condition_clause(sub_cond, sql_col: str, params: dict, key: str) -> str:
    """单个子条件 → SQL 片段（通用字段已解析为 sql_col）"""
    op = sub_cond.operator if hasattr(sub_cond, 'operator') else sub_cond.get("operator", "equals")
    val = _norm_bool(sub_cond.value if hasattr(sub_cond, 'value') else sub_cond.get("value", ""))

    if op == "equals":
        params[key] = val
        return f"{sql_col} = :{key}"
    elif op == "not_equals":
        params[key] = val
        return f"({sql_col} != :{key} OR {sql_col} IS NULL)"
    elif op == "in":
        if not isinstance(val, list):
            val = [val]
        placeholders = []
        for vi, vv in enumerate(val):
            pk = f"{key}_{vi}"
            placeholders.append(f":{pk}")
            params[pk] = _norm_bool(vv)
        return f"{sql_col} IN ({','.join(placeholders)})"
    elif op == "not_in":
        if not isinstance(val, list):
            val = [val]
        placeholders = []
        for vi, vv in enumerate(val):
            pk = f"{key}_{vi}"
            placeholders.append(f":{pk}")
            params[pk] = _norm_bool(vv)
        return f"({sql_col} NOT IN ({','.join(placeholders)}) OR {sql_col} IS NULL)"
    elif op == "gt":
        params[key] = val
        return f"{sql_col} > :{key}"
    elif op == "lt":
        params[key] = val
        return f"{sql_col} < :{key}"
    elif op == "gte":
        params[key] = val
        return f"{sql_col} >= :{key}"
    elif op == "lte":
        params[key] = val
        return f"{sql_col} <= :{key}"
    elif op == "range":
        if isinstance(val, list) and len(val) == 2:
            params[f"{key}_lo"] = val[0]
            params[f"{key}_hi"] = val[1]
            return f"({sql_col} >= :{key}_lo AND {sql_col} <= :{key}_hi)"
        raise ValueError(f"range 需要 2 个值: {val}")
    raise ValueError(f"不支持的运算符: {op}")


def _build_same_yao_group_sql(group, params: dict, idx: int) -> str:
    """同一爻条件组：来源间 OR，来源内 AND"""
    sources = group.sources if hasattr(group, 'sources') else group.get("sources", [])
    sub_conds = group.conditions if hasattr(group, 'conditions') else group.get("conditions", [])

    source_clauses = []
    for si, source in enumerate(sources):
        scope = SOURCE_TO_SCOPE.get(source, "")
        source_filter = _scope_filter(scope, {}) if scope else ""

        cond_parts = []
        for ci, sub in enumerate(sub_conds):
            field = sub.field if hasattr(sub, 'field') else sub.get("field", "")
            sql_col = GENERIC_YAO_FIELDS.get(field, {}).get(source)
            if sql_col is None:
                continue
            key_prefix = f"g{idx}_s{si}_c{ci}"
            clause = _build_sub_condition_clause(sub, sql_col, params, key_prefix)
            cond_parts.append(clause)

        if not cond_parts:
            continue

        source_sql = " AND ".join(cond_parts)
        if source_filter:
            source_sql = f"({source_filter} AND {source_sql})"
        source_clauses.append(f"({source_sql})")

    if not source_clauses:
        return "FALSE"
    return f"({' OR '.join(source_clauses)})"


def _build_same_position_group_sql(group, params: dict, idx: int) -> str:
    """同爻位条件组：同爻位 AND 逻辑"""
    position = group.position if hasattr(group, 'position') else group.get("position", 1)
    sources_cfg = group.sources if hasattr(group, 'sources') else group.get("sources", [])

    clauses = [f"y.yao_position = {int(position)}"]

    for si, src_cfg in enumerate(sources_cfg):
        source = src_cfg.source if hasattr(src_cfg, 'source') else src_cfg.get("source", "")
        sub_conds = src_cfg.conditions if hasattr(src_cfg, 'conditions') else src_cfg.get("conditions", [])

        scope = SOURCE_TO_SCOPE.get(source, "")
        source_filter = _scope_filter(scope, {}) if scope else ""
        if source_filter:
            clauses.append(source_filter)

        for ci, sub in enumerate(sub_conds):
            field = sub.field if hasattr(sub, 'field') else sub.get("field", "")
            sql_col = GENERIC_YAO_FIELDS.get(field, {}).get(source)
            if sql_col is None:
                continue
            key_prefix = f"gp{idx}_s{si}_c{ci}"
            clause = _build_sub_condition_clause(sub, sql_col, params, key_prefix)
            clauses.append(clause)

    return " AND ".join(clauses)


def _build_feishen_group_sql(group, params: dict, idx: int) -> str:
    """飞神条件组"""
    feishen_type = group.feishenType if hasattr(group, 'feishenType') else group.get("feishenType", "增删飞神")
    yongshen = group.yongshen if hasattr(group, 'yongshen') else group.get("yongshen", "妻财")
    key = f"fs{idx}"
    params[key] = yongshen

    if feishen_type == "增删飞神":
        return f"(y.zengshan_exists = TRUE AND y.zengshan_liuqin = :{key})"
    else:
        return f"(y.yimao_liuqin = :{key})"


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


def _build_condition_clause(cond: Condition, params: dict, idx: int, cond_clauses: dict = {}) -> str:
    """单个条件 → WHERE 子句片段，返回 SQL 文本"""
    # 神煞字段：委托给 _build_shensha_clause
    shensha_key = cond.field.replace("is_", "").replace("dai_", "")
    if shensha_key in SHENSHA_MAP:
        # mode 从 field 前缀推断：is_xxx→是，dai_xxx→带，裸名→是或带
        if cond.field.startswith("is_"):
            mode = "是"
        elif cond.field.startswith("dai_"):
            mode = "带"
        else:
            mode = "是或带"
        # obj_value 始终是用户在 value 字段中指定的对象（如"妻财爻"）
        obj_value = cond.value if isinstance(cond.value, str) else ""
        return _build_shensha_clause(cond.field, mode, cond.scope or "", obj_value, params, idx, cond_clauses)

    field_info = FIELD_MAP.get(cond.field)
    if not field_info:
        raise ValueError(f"未知字段: {cond.field}")

    sql_col = field_info["sql"]
    op = cond.operator
    key = f"v{idx}"
    val = _norm_bool(cond.value)

    clauses = []
    # scope 过滤：按来源范围限定
    if cond.scope:
        scope_clause = _scope_filter(cond.scope, field_info)
        if scope_clause.strip():
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
            params[pk] = _norm_bool(vv)
        clauses.append(f"{sql_col} IN ({','.join(placeholders)})")
    elif op == "not_in":
        if not isinstance(val, list):
            val = [val]
        placeholders = []
        for vi, vv in enumerate(val):
            pk = f"{key}_{vi}"
            placeholders.append(f":{pk}")
            params[pk] = _norm_bool(vv)
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
        return ""  # 本卦爻默认无额外过滤
    elif scope == "bian_yao":
        return "y.is_dong = TRUE"
    elif scope == "zhi_gua":
        return "y.is_dong = FALSE"
    elif scope == "yimao":
        return ""  # yimao 字段自带来源，无需额外条件
    elif scope == "zengshan":
        return "y.zengshan_exists = TRUE"
    return ""


def _build_shensha_clause(field: str, mode: str, scope: str, obj_value: str, params: dict, idx: int,
                           cond_clauses: dict = {}) -> str:
    """神煞条件：FIND_IN_SET 方式
    field: 如 is_ganlu / dai_yima / ganlu
    mode: "是"→查 is 字段 / "带"→查 dai 字段 / "是或带"→两者 OR
    scope: 限定来源（如果指定则只查该来源的字段）
    """
    shensha_info = SHENSHA_MAP.get(field.replace("is_", "").replace("dai_", ""))
    if not shensha_info:
        raise ValueError(f"未知神煞字段: {field}")

    is_col, dai_col = shensha_info
    # 确定要查哪些 scope
    scope_prefixes = ["ben", "zhi", "yimao", "zengshan"]
    if scope:
        scope_map = {"ben_gua": ["ben"], "zhi_gua": ["zhi"], "bian_yao": ["ben"], "yimao": ["yimao"], "zengshan": ["zengshan"]}
        scope_prefixes = scope_map.get(scope, scope_prefixes)

    clauses = []
    for sp in scope_prefixes:
        if mode in ("是", "是或带"):
            clauses.append(f"(FIND_IN_SET(y.yao_position, s.{sp}_{is_col}) > 0)")
        if mode in ("带", "是或带"):
            clauses.append(f"(FIND_IN_SET(y.yao_position, s.{sp}_{dai_col}) > 0)")

    sub = " OR ".join(clauses) if clauses else "FALSE"

    # 条件组引用：用条件组的 SQL 替换 yao object 过滤
    if obj_value and obj_value not in YAO_OBJECTS and cond_clauses.get(obj_value):
        ref_clause = cond_clauses[obj_value]
        return f"({sub}) AND ({ref_clause})"

    # 爻对象过滤（如"妻财爻" → 限制六亲 + 神煞）
    if obj_value and obj_value in YAO_OBJECTS:
        obj_col, obj_val = _parse_yao_object(obj_value)
        params[f"s{idx}"] = obj_val
        return f"({sub}) AND y.{obj_col} = :s{idx}"

    return f"({sub})"


def _build_relation_clause(rel: RelationCondition, params: dict, idx: int,
                           all_conditions: list = (), cond_clauses: dict = {}) -> str:
    """关系条件 → MySQL 存储函数调用"""
    relation = rel.relation
    bureau = rel.bureau

    # 条件组引用的子表别名计数器
    cg_counter = [0]

    # 获取地支值：yao_object → 子查询查爻表，time_object → 时间表字段
    def resolve_dz(obj_type, obj_value, suffix):
        if obj_type == "yao_object":
            col, val = _parse_yao_object(obj_value)
            params[suffix] = val
            return f"(SELECT y_inner.ben_dizhi FROM guali_yao y_inner WHERE y_inner.guali_id = guali.id AND y_inner.{col} = :{suffix} LIMIT 1)"
        elif obj_type == "time_object":
            tm_map = {"年支": "t.year_zhi", "月支": "t.month_zhi", "日支": "t.day_zhi"}
            dz_col = tm_map.get(obj_value)
            if dz_col:
                return dz_col
            params[suffix] = obj_value
            return f":{suffix}"
        elif obj_type == "condition_group_ref":
            # 找到被引用的条件，以独立表别名重建其 SQL 子句
            ref_cond = None
            for c in all_conditions:
                if c.id == obj_value:
                    ref_cond = c
                    break
            if ref_cond is None:
                raise ValueError(f"条件组引用目标不存在: {obj_value}")

            alias = f"ycg{cg_counter[0]}"
            cg_counter[0] += 1

            # 为被引用条件生成带新表别名的 SQL（替换 y. 为 alias.）
            ref_clause = cond_clauses.get(obj_value, "")
            ref_sql = ref_clause.replace("y.", f"{alias}.")

            # 如果被引用条件含神煞字段(s.)，子查询需 JOIN guali_shensha
            extra_join = ""
            if "s." in ref_sql:
                extra_join = f" LEFT JOIN guali_shensha s ON s.guali_id = {alias}.guali_id"

            return (
                f"(SELECT {alias}.ben_dizhi FROM guali_yao {alias}{extra_join}"
                f" WHERE {alias}.guali_id = guali.id AND ({ref_sql}) LIMIT 1)"
            )
        params[suffix] = obj_value
        return f":{suffix}"

    dz1 = resolve_dz(rel.left_type, rel.left_value, f"l{idx}")
    dz2 = resolve_dz(rel.right_type, rel.right_value, f"r{idx}")

    if relation == "三合":
        # 三合需要 3 个地支对象
        dz_mid = resolve_dz(rel.middle_type, rel.middle_value, f"m{idx}")
        if bureau:
            return f"check_sanhe({dz1}, {dz_mid}, {dz2}) = '{bureau}'"
        return f"check_sanhe({dz1}, {dz_mid}, {dz2}) != '无'"
    elif relation in ("生", "克"):
        func = "check_sheng" if relation == "生" else "check_ke"
        return f"{func}({dz1}, {dz2}) = TRUE"
    elif relation == "合":
        return f"check_he({dz1}, {dz2}) = TRUE"
    elif relation == "冲":
        return f"check_chong({dz1}, {dz2}) = TRUE"
    elif relation == "半合":
        return f"check_banhe({dz1}, {dz2}) = TRUE"
    elif relation == "=":
        return f"{dz1} = {dz2}"
    elif relation in ("长生", "帝旺", "墓", "绝"):
        return f"check_shengwang({dz1}, {dz2}, '{relation}') = TRUE"

    return "FALSE"


def _collect_joins(conditions: list) -> set[str]:
    """收集所需 JOIN"""
    joins: set[str] = set()
    for cond in conditions:
        if isinstance(cond, (SameYaoGroup, SamePositionGroup, FeishenGroup)):
            joins.add("y")
            continue
        if isinstance(cond, RelationCondition):
            joins.add("y")
            # 关系条件引用了时间对象 → 需要 guali_time
            if cond.left_type == "time_object" or cond.right_type == "time_object" or (getattr(cond, 'middle_type', None) == "time_object"):
                joins.add("t")
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
            data={"results": [dict(r) for r in rows], "total": total, "page": pg, "page_size": ps}
        )

    # 收集 JOIN
    joins = _collect_joins(conditions)
    # 确保主表
    if "guali" not in joins:
        pass  # FROM 始终是 guali

    join_sql = _build_join_clauses(joins)

    # 构建 WHERE 子句
    params: dict = {}
    cond_clauses: dict[str, str] = {}  # id → SQL clause

    # 第一遍：先生成所有条件的 SQL 子句（关系条件稍后处理）
    for i, cond in enumerate(conditions):
        if isinstance(cond, (SameYaoGroup, SamePositionGroup, FeishenGroup)):
            if isinstance(cond, SameYaoGroup):
                cond_clauses[cond.id] = _build_same_yao_group_sql(cond, params, i)
            elif isinstance(cond, SamePositionGroup):
                cond_clauses[cond.id] = _build_same_position_group_sql(cond, params, i)
            elif isinstance(cond, FeishenGroup):
                cond_clauses[cond.id] = _build_feishen_group_sql(cond, params, i)
        elif not isinstance(cond, RelationCondition):
            cond_clauses[cond.id] = _build_condition_clause(cond, params, i, cond_clauses)

    # 第二遍：处理关系条件（此时 cond_clauses 已完整，可供 condition_group_ref 引用）
    for i, cond in enumerate(conditions):
        if isinstance(cond, RelationCondition):
            cond_clauses[cond.id] = _build_relation_clause(cond, params, i, conditions, cond_clauses)

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

    MAX_BRACKET_DEPTH = 5
    depth = 0
    parts: list[str] = []
    for i, item in enumerate(logic):
        if item.type in ("condition", "condition_group"):
            clause = cond_clauses.get(item.id or "", "TRUE")
            parts.append(f"({clause})")
        elif item.type in ("and", "or"):
            if parts:
                parts.append(f" {item.type.upper()} ")
        elif item.type == "not":
            # NOT 后面必须跟 condition 或 "("
            next_valid = (i + 1 < len(logic) and
                          logic[i + 1].type in ("condition", "(", "not"))
            if not next_valid:
                raise ValueError(f"NOT 运算符后缺少操作数（位置 {i}）")
            parts.append("NOT ")
        elif item.type == "(":
            depth += 1
            if depth > MAX_BRACKET_DEPTH:
                raise ValueError(f"括号嵌套深度超过上限（最多 {MAX_BRACKET_DEPTH} 层）")
            parts.append("(")
        elif item.type == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("括号不匹配：多余的右括号")
            parts.append(")")

    if depth != 0:
        raise ValueError(f"括号不匹配：缺少 {depth} 个右括号")

    return "".join(parts)
