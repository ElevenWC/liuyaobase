"""临时路由——卦爻辞查询。v0.5 迁移到 jiegua 路由下。"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.db.connection import get_session
from backend.crud.guaci import get_by_code

router = APIRouter(prefix="/guaci", tags=["卦爻辞"])


@router.get("/{code}")
async def fetch_guaci(code: str, session: Session = Depends(get_session)):
    """获取卦爻辞数据"""
    guaci = get_by_code(session, code)
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
