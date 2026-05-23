"""卦类扩展表 CRUD — 每卦例 1 行 14 字段"""
from sqlmodel import Session, select
from backend.models.guali_gua import GualiGua


def create(session: Session, guali_id: int, data: dict) -> GualiGua:
    """新增卦类记录。data 来自 gua_type 判断 + bagong_gua 查询。"""
    record = GualiGua(guali_id=guali_id, **data)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_by_guali_id(session: Session, guali_id: int) -> GualiGua | None:
    """按卦例 ID 查询"""
    return session.exec(
        select(GualiGua).where(GualiGua.guali_id == guali_id)
    ).first()
