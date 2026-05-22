"""卦例主表 CRUD — 增删改查 + 列表分页 + 标签筛选"""
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar
from backend.models.guali import Guali
from backend.models.tag import GualiTag


def create(session: Session, data: dict) -> Guali:
    """新增一条卦例。zhi_code 若未提供则自动计算（ben_code XOR yao_bian_code）。"""
    if "zhi_code" not in data:
        ben = data["ben_code"]
        yao_bian = data.get("yao_bian_code", "000000")
        data["zhi_code"] = "".join(
            "1" if ben[i] != yao_bian[i] else "0" for i in range(6)
        )
    guali = Guali(**data)
    session.add(guali)
    session.commit()
    session.refresh(guali)
    return guali


def get_by_id(session: Session, guali_id: int) -> Guali | None:
    """按 ID 查询卦例"""
    return session.exec(
        select(Guali).where(Guali.id == guali_id)
    ).first()


def list_guali(
    session: Session,
    page: int,
    page_size: int,
    keyword: str = "",
    tag_id: int | None = None,
) -> tuple[list[Guali], int]:
    """分页列表，按 zhanwen_time 倒序；keyword 搜索占问事由；tag_id 按标签筛选。"""
    base: SelectOfScalar = select(Guali)

    if tag_id is not None:
        base = (
            base.join(GualiTag, Guali.id == GualiTag.guali_id)
            .where(GualiTag.tag_id == tag_id)
        )

    if keyword:
        base = base.where(Guali.zhanwen_shiyou.contains(keyword))  # type: ignore[union-attr]

    # 总数
    count_stmt = select(Guali.id)
    if tag_id is not None:
        count_stmt = count_stmt.join(GualiTag, Guali.id == GualiTag.guali_id).where(GualiTag.tag_id == tag_id)
    if keyword:
        count_stmt = count_stmt.where(Guali.zhanwen_shiyou.contains(keyword))  # type: ignore[union-attr]
    total = len(session.exec(count_stmt).all())

    # 分页
    offset = (page - 1) * page_size
    results = list(
        session.exec(
            base.order_by(Guali.zhanwen_time.desc()).offset(offset).limit(page_size)  # type: ignore[union-attr]
        ).all()
    )

    return results, total


def update(session: Session, guali_id: int, data: dict) -> Guali | None:
    """更新卦例——只允许修改 zhanwen_shiyou 和 zhanduan。"""
    guali = get_by_id(session, guali_id)
    if guali is None:
        return None
    for field in ("zhanwen_shiyou", "zhanduan"):
        if field in data:
            setattr(guali, field, data[field])
    session.commit()
    session.refresh(guali)
    return guali


def delete(session: Session, guali_id: int) -> bool:
    """删除单个卦例。级联删除 guali_* 扩展表由外键 CASCADE 处理。"""
    guali = get_by_id(session, guali_id)
    if guali is None:
        return False
    session.delete(guali)
    session.commit()
    return True


def delete_batch(session: Session, ids: list[int]) -> int:
    """批量删除，返回实际删除数量。"""
    if not ids:
        return 0
    gualis = list(
        session.exec(select(Guali).where(Guali.id.in_(ids))).all()  # type: ignore[union-attr]
    )
    for g in gualis:
        session.delete(g)
    session.commit()
    return len(gualis)


def get_by_code(session: Session, ben_code: str) -> list[Guali]:
    """按本卦代码查询全部卦例"""
    return list(
        session.exec(
            select(Guali).where(Guali.ben_code == ben_code)
        ).all()
    )
