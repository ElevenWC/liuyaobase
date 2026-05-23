"""八宫卦序表 CRUD（v0.2 最小版，v0.3 扩充）"""
from sqlmodel import Session, select
from backend.models.bagong_gua import BagongGua


def get_by_code(session: Session, code: str) -> BagongGua | None:
    """按卦代码查询"""
    return session.exec(
        select(BagongGua).where(BagongGua.code == code)
    ).first()
