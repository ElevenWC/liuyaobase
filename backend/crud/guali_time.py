"""时间扩展表 CRUD — 每卦例 1 行 11 字段"""
from sqlmodel import Session, select
from backend.models.guali_time import GualiTime


def create(session: Session, guali_id: int, data: dict) -> GualiTime:
    """新增一条时间记录。data 来自 time_converter.convert_time() 的返回。"""
    record = GualiTime(guali_id=guali_id, **data)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_by_guali_id(session: Session, guali_id: int) -> GualiTime | None:
    """按卦例 ID 查询"""
    return session.exec(
        select(GualiTime).where(GualiTime.guali_id == guali_id)
    ).first()


def delete_by_guali_id(session: Session, guali_id: int):
    """删除某卦例的时间记录（通常由外键 CASCADE 处理）"""
    record = get_by_guali_id(session, guali_id)
    if record:
        session.delete(record)
        session.commit()
