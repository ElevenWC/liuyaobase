"""标签 API —— 树查询/增删改 + 卦例列表"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.db.connection import get_session
from backend.services.tag_service import (
    get_tag_tree, create_tag, update_tag, delete_tag, get_guali_by_tag, reorder_tags,
)

router = APIRouter(prefix="/tags", tags=["标签"])


def _ok(data=None) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _err(msg: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": msg}


@router.get("")
async def list_tags(session: Session = Depends(get_session)):
    """标签树（嵌套结构）"""
    tree = get_tag_tree(session)
    return _ok(tree)


@router.post("")
async def add_tag(data: dict, session: Session = Depends(get_session)):
    """创建标签"""
    name = data.get("name", "")
    if not name:
        return _err("标签名不能为空")
    parent_id = data.get("parent_id")
    tag = create_tag(session, name, parent_id)
    return _ok({"id": tag.id, "name": tag.name})


@router.put("/{tag_id}")
async def rename_tag(tag_id: int, data: dict, session: Session = Depends(get_session)):
    """重命名标签"""
    name = data.get("name", "")
    if not name:
        return _err("标签名不能为空")
    try:
        tag = update_tag(session, tag_id, name)
        return _ok({"id": tag.id, "name": tag.name})
    except ValueError as e:
        return _err(str(e), 404)


@router.delete("/{tag_id}")
async def remove_tag(tag_id: int, session: Session = Depends(get_session)):
    """删除标签（有子标签时拒绝）"""
    try:
        delete_tag(session, tag_id)
        return _ok(None)
    except ValueError as e:
        return _err(str(e))


@router.post("/reorder")
async def reorder(data: dict, session: Session = Depends(get_session)):
    """更新一级标签排序"""
    ids = data.get("ids", [])
    if not ids:
        return _err("ids 不能为空")
    reorder_tags(session, ids)
    return _ok(None)


@router.get("/{tag_id}/guali")
async def list_guali_by_tag(
    tag_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """某标签下的卦例列表"""
    result = get_guali_by_tag(session, tag_id, page, page_size)
    return _ok(result)
