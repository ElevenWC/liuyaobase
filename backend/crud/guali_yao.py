"""爻类扩展表 CRUD — 每卦例 6 行 20 字段"""
from sqlmodel import Session, select
from backend.models.guali_yao import GualiYao


def create_batch(session: Session, guali_id: int, yao_list: list[dict]) -> list[GualiYao]:
    """批量插入 6 条爻记录，使用 session.add_all() 一次 commit。"""
    records = [GualiYao(guali_id=guali_id, **yao) for yao in yao_list]
    session.add_all(records)
    session.commit()
    for r in records:
        session.refresh(r)
    return records


def get_by_guali_id(session: Session, guali_id: int) -> list[GualiYao]:
    """查询某卦例的全部 6 爻，按 yao_position 升序。"""
    return list(
        session.exec(
            select(GualiYao)
            .where(GualiYao.guali_id == guali_id)
            .order_by(GualiYao.yao_position)
        ).all()
    )


def get_dong_yao(session: Session, guali_id: int) -> list[GualiYao]:
    """只查动爻（is_dong=True）"""
    return list(
        session.exec(
            select(GualiYao).where(
                GualiYao.guali_id == guali_id,
                GualiYao.is_dong == True,  # noqa: E712
            )
        ).all()
    )


def delete_by_guali_id(session: Session, guali_id: int):
    """删除某卦例的全部爻记录（通常由外键 CASCADE 处理）"""
    records = get_by_guali_id(session, guali_id)
    for r in records:
        session.delete(r)
    session.commit()
