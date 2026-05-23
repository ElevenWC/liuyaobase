"""八宫卦序表 CRUD — 只读查询"""
from sqlmodel import Session, select
from backend.models.bagong_gua import BagongGua


def get_by_code(session: Session, code: str) -> BagongGua | None:
    """按卦代码查询"""
    return session.exec(
        select(BagongGua).where(BagongGua.code == code)
    ).first()


def get_by_name(session: Session, name: str) -> BagongGua | None:
    """按卦名查询"""
    return session.exec(
        select(BagongGua).where(BagongGua.name == name)
    ).first()


def get_all(session: Session) -> list[BagongGua]:
    """返回全部 64 卦"""
    return list(session.exec(select(BagongGua)).all())


def get_by_palace(session: Session, palace: str) -> list[BagongGua]:
    """按卦宫查询（如 乾宫/坤宫 等）"""
    return list(
        session.exec(
            select(BagongGua).where(BagongGua.palace == palace)
        ).all()
    )
