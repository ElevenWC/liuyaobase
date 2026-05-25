"""C3 检索 API —— 复杂检索 / 推荐方案 / 导出"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session
from backend.db.connection import get_session
from backend.schemas.search import SearchRequest, SearchResponse
from backend.services.search_service import execute_search
from backend.services.export_service import export_results

router = APIRouter(prefix="/search", tags=["检索"])


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest, session: Session = Depends(get_session)):
    """执行复杂检索"""
    return execute_search(session, request)


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
