"""卦例 API —— 查询/修改/删除 + 标签关联"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.db.connection import get_session
from backend.services.guali_service import get_guali_list, get_guali_detail
from backend.crud.guali import update as update_guali_crud, delete as delete_guali_crud, delete_batch
from backend.crud.tag import add_guali_tag, remove_guali_tag

router = APIRouter(prefix="/guali", tags=["卦例"])


def _ok(data=None) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _err(msg: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": msg}


@router.get("")
async def list_guali(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
    tag_id: int | None = Query(None),
    session: Session = Depends(get_session),
):
    """卦例列表（分页 + 搜索 + 标签筛选）"""
    result = get_guali_list(session, page, page_size, keyword, tag_id)
    return _ok(result)


@router.get("/{guali_id}")
async def detail_guali(guali_id: int, session: Session = Depends(get_session)):
    """卦例详情（5 表拼装）"""
    detail = get_guali_detail(session, guali_id)
    if detail is None:
        return _err("卦例不存在", 404)
    return _ok(detail)


@router.put("/{guali_id}")
async def update_guali(guali_id: int, data: dict, session: Session = Depends(get_session)):
    """更新卦例（仅允许修改占问事由和占断内容）"""
    guali = update_guali_crud(session, guali_id, data)
    if guali is None:
        return _err("卦例不存在", 404)
    return _ok({"id": guali.id})


@router.delete("/{guali_id}")
async def delete_guali(guali_id: int, session: Session = Depends(get_session)):
    """删除单个卦例"""
    ok = delete_guali_crud(session, guali_id)
    if not ok:
        return _err("卦例不存在", 404)
    return _ok(None)


@router.delete("/batch")
async def batch_delete_guali(data: dict, session: Session = Depends(get_session)):
    """批量删除卦例"""
    ids = data.get("ids", [])
    if not ids:
        return _err("ids 不能为空")
    count = delete_batch(session, ids)
    return _ok({"deleted": count})


@router.post("/{guali_id}/tags")
async def add_tag(guali_id: int, data: dict, session: Session = Depends(get_session)):
    """给卦例关联标签"""
    tag_id = data.get("tag_id")
    if not tag_id:
        return _err("tag_id 不能为空")
    add_guali_tag(session, guali_id, tag_id)
    return _ok(None)


@router.delete("/{guali_id}/tags/{tag_id}")
async def remove_tag(guali_id: int, tag_id: int, session: Session = Depends(get_session)):
    """移除卦例的标签关联"""
    remove_guali_tag(session, guali_id, tag_id)
    return _ok(None)
