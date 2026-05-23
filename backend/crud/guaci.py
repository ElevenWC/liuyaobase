"""卦爻辞表查询 — 只读"""
from sqlmodel import Session, select
from backend.models.guaci import Guaci


def get_by_code(session: Session, code: str) -> Guaci | None:
    """按卦代码查询卦爻辞"""
    return session.exec(
        select(Guaci).where(Guaci.code == code)
    ).first()
