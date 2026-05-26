"""C3 检索 API —— 复杂检索 / 推荐方案 / 导出"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session
from backend.db.connection import get_session
from backend.schemas.search import SearchRequest, SearchResponse
from backend.services.search_service import execute_search
from backend.services.export_service import export_results

router = APIRouter(prefix="/search", tags=["检索"])
logger = logging.getLogger(__name__)
SEARCH_TIMEOUT = 10  # 秒


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest, session: Session = Depends(get_session)):
    """执行复杂检索"""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(execute_search, session, request),
            timeout=SEARCH_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.warning(f"检索超时（>{SEARCH_TIMEOUT}s）")
        raise HTTPException(status_code=504, detail=f"检索超时（>{SEARCH_TIMEOUT}秒），请简化检索条件后重试")


@router.get("/schemes")
async def get_schemes():
    """预设检索模板（用户自定义方案由前端 localStorage 管理）"""
    return {
        "code": 200,
        "data": [],
        "message": "推荐方案已改为用户自定义，请在前端保存方案到 localStorage",
    }


@router.post("/export")
async def export_data(request: SearchRequest, fmt: str = "csv", session: Session = Depends(get_session)):
    """导出检索结果为 CSV/JSON 文件"""
    filepath = export_results(session, request, fmt)
    filename = filepath.split("/")[-1]
    return FileResponse(
        filepath,
        media_type="text/csv" if fmt == "csv" else "application/json",
        filename=filename,
    )
