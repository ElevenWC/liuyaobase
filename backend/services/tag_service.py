"""标签业务逻辑 —— 树构建 + 占验互斥 + CRUD 封装"""
from sqlmodel import Session
from backend.crud.tag import (
    get_all, get_by_id, create as create_tag_crud,
    update as update_tag_crud, delete as delete_tag_crud,
    add_guali_tag, remove_guali_tag,
    get_tags_by_guali, get_guali_ids_by_tag,
)
from backend.crud.guali import list_guali
from backend.models.tag import Tag


def get_tag_tree(session: Session) -> list[dict]:
    """构建嵌套标签树。parent_id=None 为一级。"""
    all_tags = get_all(session)
    return _build_tree(all_tags, None)


def create_tag(session: Session, name: str, parent_id: int | None = None) -> Tag:
    """创建标签"""
    return create_tag_crud(session, name, parent_id)


def update_tag(session: Session, tag_id: int, name: str) -> Tag:
    """重命名标签"""
    tag = update_tag_crud(session, tag_id, name)
    if tag is None:
        raise ValueError(f"标签不存在: {tag_id}")
    return tag


def delete_tag(session: Session, tag_id: int):
    """删除标签。系统标签和有一级子标签时拒绝删除。"""
    tag = session.get(Tag, tag_id)
    if tag is None:
        raise ValueError(f"标签不存在: {tag_id}")
    if tag.is_system:
        raise ValueError("系统标签不可删除")
    children = [t for t in get_all(session) if t.parent_id == tag_id]
    if children:
        names = ", ".join(c.name for c in children)
        raise ValueError(f"该标签下有子标签，请先删除子标签: {names}")
    ok = delete_tag_crud(session, tag_id)
    if not ok:
        raise ValueError(f"标签不存在: {tag_id}")


def get_guali_by_tag(
    session: Session, tag_id: int, page: int, page_size: int
) -> dict:
    """查询某标签下的卦例列表"""
    ids = get_guali_ids_by_tag(session, tag_id)
    if not ids:
        return {"items": [], "total": 0, "page": page}

    results, total = list_guali(session, page, page_size)
    return {"items": results, "total": total, "page": page}


def set_zhan_yan_tag(session: Session, guali_id: int, tag_id: int):
    """占验标签互斥——同一事务内删除旧占验关联 + 创建新关联。

    占验标签以 parent_id 区分（一级标签下挂占验子标签）。
    旧的同父占验标签先删除，再插新的。
    """
    # 获取 tag 信息
    tag = get_by_id(session, tag_id)
    if tag is None:
        raise ValueError(f"标签不存在: {tag_id}")
    if tag.parent_id is None:
        # 没有父标签，不是占验标签
        add_guali_tag(session, guali_id, tag_id)
        return

    # 删除同一父标签下的其他占验关联
    current_tags = get_tags_by_guali(session, guali_id)
    for ct in current_tags:
        if ct.parent_id == tag.parent_id:
            remove_guali_tag(session, guali_id, ct.id)

    add_guali_tag(session, guali_id, tag_id)


def _build_tree(tags: list[Tag], parent_id: int | None) -> list[dict]:
    """递归构建标签树"""
    result: list[dict] = []
    for tag in tags:
        if tag.parent_id != parent_id:
            continue
        children = _build_tree(tags, tag.id)
        result.append({
            "id": tag.id,
            "name": tag.name,
            "parent_id": tag.parent_id,
            "is_system": tag.is_system,
            "children": children,
        })
    return result
