"""解卦 API —— 互卦计算、网络图谱数据、卦爻辞查询"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.db.connection import get_session
from backend.core.hugua import calc_hugua
from backend.core.bagong_bian import calc_bagong_bian
from backend.crud.bagong_gua import get_by_code, get_all
from backend.crud.guaci import get_by_code as get_guaci_by_code

router = APIRouter(prefix="/jiegua", tags=["解卦"])


def _ok(data=None) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _err(msg: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": msg}


# ── 图谱缓存（数据固定，首次计算后缓存） ──
_graph_cache: dict[str, dict] = {}


def _get_chain_position(code: str, session) -> tuple[list[str], int]:
    """找到卦在其本宫卦链中的位置，返回 (chain_codes, position_index)"""
    gua = get_by_code(session, code)
    if not gua:
        return [], -1

    # 找本宫卦
    all_gua = get_all(session)
    ben_gong = next(
        (g for g in all_gua if g.palace == gua.palace and g.palace_type == "本宫卦"), None
    )
    if not ben_gong:
        return [], -1

    # 从本宫卦计算累积链
    steps = calc_bagong_bian(ben_gong.code)
    chain = [ben_gong.code]
    for s in steps:
        chain.append(s["code"])

    if code not in chain:
        return [], -1

    return chain, chain.index(code)


def _build_graph(graph_type: str, session: Session) -> dict:
    """构建网络图谱节点+边数据

    参考 getDirectNeighbors 逻辑：每个卦找到其在本宫链中的位置，
    边仅连接链中紧邻的前后节点（非全部7个）。
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

    # 变化类型名（对应链中位置间的关系）
    CHANGE_TYPES = ["一世", "二世", "三世", "四世", "五世", "游魂", "归魂"]

    # 对每个节点，找其在链中的紧邻 → 独立应用7种变化 → 直接邻居边
    edge_set: set[tuple[str, str, str]] = set()
    for g in matched:
        chain, pos = _get_chain_position(g.code, session)
        if pos < 0:
            continue
        # 前驱
        if pos > 0:
            prev_code = chain[pos - 1]
            if prev_code in code_set:
                edge_set.add((g.code, prev_code, CHANGE_TYPES[pos - 1]))
        # 后继
        if pos < len(chain) - 1:
            next_code = chain[pos + 1]
            if next_code in code_set:
                edge_set.add((g.code, next_code, CHANGE_TYPES[pos]))

    edges = [
        {"source": s, "target": t, "type": tp} for s, t, tp in edge_set
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
            "yao_ci": guaci.yao_ci,
            "wenyan": guaci.wenyan,
            "yong": guaci.yong,
        },
        "message": "success",
    }
