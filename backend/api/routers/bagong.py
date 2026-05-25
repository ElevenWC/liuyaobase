"""八宫变化 API —— 输入卦代码，返回七种变化结果"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.db.connection import get_session
from backend.core.bagong_bian import calc_bagong_bian
from backend.crud.bagong_gua import get_by_code
from backend.crud.guali import get_by_id as get_guali_by_id

router = APIRouter(prefix="/jiegua", tags=["解卦"])


def _ok(data=None) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _err(msg: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": msg}


@router.get("/bagong/{gua_code}")
async def get_bagong(
    gua_code: str,
    guali_id: int | None = Query(None),
    session: Session = Depends(get_session),
):
    """获取指定卦的八宫变化（一世→归魂 七步）

    - gua_code: 6 位二进制卦代码
    - guali_id: 可选，卦例编号。提供时从 guali 表读取 ben_code 并检查上爻动爻
    """
    # 校验 gua_code 格式
    if len(gua_code) != 6 or not all(c in "01" for c in gua_code):
        return _err("无效卦代码，需要 6 位 0/1 字符串")

    # 若提供了 guali_id，读取卦例信息
    if guali_id is not None:
        guali = get_guali_by_id(session, guali_id)
        if guali is None:
            return _err(f"卦例 {guali_id} 不存在", 404)
        gua_code = guali.ben_code
        if guali.yao_bian_code[5] == "1":
            return _err("此卦上爻为动爻，不可用八宫变化")

    # 查 bagong_gua 获取本卦名称/卦宫/五行
    ben_row = get_by_code(session, gua_code)
    if ben_row is None:
        return _err("无效卦代码，bagong_gua 表中不存在此代码")

    ben_gua = {
        "code": ben_row.code,
        "name": ben_row.name,
        "palace": ben_row.palace,
        "element": ben_row.element,
    }

    # 计算七变并补充名称/卦宫/五行
    raw_steps = calc_bagong_bian(gua_code)
    steps = []
    for step in raw_steps:
        row = get_by_code(session, step["code"])
        steps.append({
            "type": step["type"],
            "code": step["code"],
            "name": row.name if row else step["name"],
            "palace": row.palace if row else "",
            "element": row.element if row else "",
        })

    return _ok({"ben_gua": ben_gua, "steps": steps})
