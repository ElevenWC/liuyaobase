"""笔记导出/导入 API"""
import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/notes", tags=["notes"])

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "notes_export")
os.makedirs(EXPORT_DIR, exist_ok=True)


class NotesExportRequest(BaseModel):
    notes: list


@router.post("/export")
def export_notes(body: NotesExportRequest):
    """导出笔记到 backend/notes_export/ 文件夹"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"六爻笔记_{ts}.json"
    filepath = os.path.join(EXPORT_DIR, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(body.notes, f, ensure_ascii=False, indent=2)
        return {"code": 200, "data": {"filename": filename}, "message": "导出成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {e}")


@router.get("/exports")
def list_exports():
    """列出已导出的笔记文件"""
    try:
        files = sorted(
            [f for f in os.listdir(EXPORT_DIR) if f.endswith(".json")],
            reverse=True,
        )
        return {"code": 200, "data": {"files": files}, "message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
