"""标签表 + 卦例-标签关联表 CRUD"""
from sqlmodel import Session, select
from backend.models.tag import Tag, GualiTag


def get_all(session: Session) -> list[Tag]:
    """返回全部标签"""
    return list(session.exec(select(Tag)).all())


def get_by_id(session: Session, tag_id: int) -> Tag | None:
    """按 ID 查询"""
    return session.exec(select(Tag).where(Tag.id == tag_id)).first()


def create(session: Session, name: str, parent_id: int | None = None) -> Tag:
    """创建标签"""
    tag = Tag(name=name, parent_id=parent_id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def update(session: Session, tag_id: int, name: str) -> Tag | None:
    """重命名标签"""
    tag = get_by_id(session, tag_id)
    if tag is None:
        return None
    tag.name = name
    session.commit()
    session.refresh(tag)
    return tag


def delete(session: Session, tag_id: int) -> bool:
    """删除标签，同时级联删除 guali_tag 关联"""
    tag = get_by_id(session, tag_id)
    if tag is None:
        return False
    # 删除关联记录
    links = session.exec(
        select(GualiTag).where(GualiTag.tag_id == tag_id)
    ).all()
    for link in links:
        session.delete(link)
    session.delete(tag)
    session.commit()
    return True


def add_guali_tag(session: Session, guali_id: int, tag_id: int):
    """关联卦例与标签。重复关联静默忽略。"""
    existing = session.exec(
        select(GualiTag).where(
            GualiTag.guali_id == guali_id,
            GualiTag.tag_id == tag_id,
        )
    ).first()
    if existing is not None:
        return
    session.add(GualiTag(guali_id=guali_id, tag_id=tag_id))
    session.commit()


def remove_guali_tag(session: Session, guali_id: int, tag_id: int):
    """解除卦例与标签的关联"""
    link = session.exec(
        select(GualiTag).where(
            GualiTag.guali_id == guali_id,
            GualiTag.tag_id == tag_id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()


def get_tags_by_guali(session: Session, guali_id: int) -> list[Tag]:
    """查询某卦例的全部标签"""
    return list(
        session.exec(
            select(Tag)
            .join(GualiTag, GualiTag.tag_id == Tag.id)
            .where(GualiTag.guali_id == guali_id)
        ).all()
    )


def get_guali_ids_by_tag(session: Session, tag_id: int) -> list[int]:
    """查询某标签下的全部卦例 ID"""
    links = session.exec(
        select(GualiTag.guali_id).where(GualiTag.tag_id == tag_id)
    ).all()
    return list(links)


def get_child_tag_ids(session: Session, parent_id: int) -> list[int]:
    """获取某父标签下的所有子标签 ID（不含父标签自身）"""
    children = session.exec(
        select(Tag.id).where(Tag.parent_id == parent_id)
    ).all()
    return list(children)
