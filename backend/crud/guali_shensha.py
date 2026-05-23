"""神煞扩展表 CRUD — 每卦例 1 行 37 字段"""
from sqlmodel import Session, select
from backend.models.guali_shensha import GualiShensha


def create(session: Session, guali_id: int, data: dict) -> GualiShensha:
    """新增神煞记录。data 来自 shensha.calc_shensha_status() 的返回。"""
    record = GualiShensha(guali_id=guali_id, **data)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_by_guali_id(session: Session, guali_id: int) -> GualiShensha | None:
    """按卦例 ID 查询"""
    return session.exec(
        select(GualiShensha).where(GualiShensha.guali_id == guali_id)
    ).first()
