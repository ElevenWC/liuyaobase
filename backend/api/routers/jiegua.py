"""解卦 API —— 互卦计算、网络图谱数据、卦爻辞查询"""
import json as _json
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.db.connection import get_session
from backend.core.hugua import calc_hugua
from backend.core.bagong_bian import calc_bagong_bian
from backend.core.time_converter import get_calendar_month
from backend.crud.bagong_gua import get_by_code, get_all
from backend.crud.guaci import get_by_code as get_guaci_by_code


def _parse_json_field(value):
    """若数据库返回的是 JSON 字符串（双编码），解析为 dict"""
    if isinstance(value, str):
        try:
            return _json.loads(value)
        except (_json.JSONDecodeError, TypeError):
            return value
    return value

router = APIRouter(prefix="/jiegua", tags=["解卦"])


def _ok(data=None) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _err(msg: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": msg}


# ── 图谱缓存（数据固定，首次计算后缓存） ──
_graph_cache: dict[str, dict] = {}


def _build_graph(graph_type: str, session: Session) -> dict:
    """构建网络图谱节点+边数据

    每个节点对自身累积应用 calc_bagong_bian → 7 条出边（一世→归魂），
    指向该节点在八宫变化中可到达的 7 个邻居。
    """
    if graph_type in _graph_cache:
        return _graph_cache[graph_type]

    target_upper = "1" if graph_type == "yang" else "0"

    all_gua = get_all(session)
    matched = [g for g in all_gua if g.code[5] == target_upper]
    code_set = {g.code for g in matched}

    nodes = [
        {"id": g.code, "name": g.name, "palace": g.palace, "element": g.element}
        for g in matched
    ]

    # 每个节点以自身为起点累积计算七变，每个步骤一条出边
    edge_map: dict[tuple[str, str], str] = {}
    for g in matched:
        steps = calc_bagong_bian(g.code)
        for step in steps:
            if step["code"] in code_set:
                key = (g.code, step["code"])
                if key not in edge_map:
                    edge_map[key] = step["type"]

    edges = [
        {"source": s, "target": t, "type": tp} for (s, t), tp in edge_map.items()
    ]

    result = {"nodes": nodes, "edges": edges}
    _graph_cache[graph_type] = result
    return result


# ── 互卦 ──

@router.get("/hugua/{gua_code}")
async def get_hugua(
    gua_code: str,
    zhi_code: str | None = Query(None),
    session: Session = Depends(get_session),
):
    """获取指定卦的互卦

    - gua_code: 6 位本卦代码
    - zhi_code: 可选，之卦代码。提供时同时返回之卦互卦
    """
    if len(gua_code) != 6 or not all(c in "01" for c in gua_code):
        return _err("无效卦代码，需要 6 位 0/1 字符串")

    hu_code = calc_hugua(gua_code)
    hu_row = get_by_code(session, hu_code)
    ben_hugua = {
        "code": hu_code,
        "name": hu_row.name if hu_row else "",
        "palace": hu_row.palace if hu_row else "",
        "element": hu_row.element if hu_row else "",
    }

    zhi_hugua = None
    if zhi_code:
        if len(zhi_code) != 6 or not all(c in "01" for c in zhi_code):
            return _err("无效之卦代码，需要 6 位 0/1 字符串")
        zhi_hu_code = calc_hugua(zhi_code)
        zhi_hu_row = get_by_code(session, zhi_hu_code)
        zhi_hugua = {
            "code": zhi_hu_code,
            "name": zhi_hu_row.name if zhi_hu_row else "",
            "palace": zhi_hu_row.palace if zhi_hu_row else "",
            "element": zhi_hu_row.element if zhi_hu_row else "",
        }

    return _ok({"ben_hugua": ben_hugua, "zhi_hugua": zhi_hugua})


# ── 网络图谱 ──

@router.get("/graph/{graph_type}")
async def get_graph(
    graph_type: str,
    session: Session = Depends(get_session),
):
    """获取网络图谱数据（力导向布局的节点和边）

    - graph_type: yang（上爻=1，32卦）或 yin（上爻=0，32卦）
    """
    if graph_type not in ("yang", "yin"):
        return _err("图谱类型无效，仅支持 yang 或 yin")
    return _ok(_build_graph(graph_type, session))


# ── 干支日历 ──

@router.get("/calendar")
async def get_calendar(year: int = 2024, month: int = 1):
    """获取指定年月的干支日历数据"""
    if month < 1 or month > 12:
        return _err("月份需在 1-12 之间")
    return _ok(get_calendar_month(year, month))


# ── 卦爻辞 ──

@router.get("/guaci/{gua_code}")
async def get_guaci(
    gua_code: str,
    session: Session = Depends(get_session),
):
    """获取卦爻辞（供 GuaCiFloat 使用，从原 /api/guaci/{code} 迁移）"""
    guaci = get_guaci_by_code(session, gua_code)
    if guaci is None:
        return {"code": 404, "data": None, "message": "卦代码不存在"}
    return {
        "code": 200,
        "data": {
            "code": guaci.code,
            "gua_ci": guaci.gua_ci,
            "tuan_zhuan": guaci.tuan_zhuan,
            "xiang_zhuan": guaci.xiang_zhuan,
            "yao_ci": _parse_json_field(guaci.yao_ci),
            "wenyan": guaci.wenyan,
            "yong": _parse_json_field(guaci.yong),
        },
        "message": "success",
    }
