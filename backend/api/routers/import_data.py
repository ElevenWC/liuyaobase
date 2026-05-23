"""导入模块 API —— JSON 上传 + 手动导入 + 导入状态"""
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from backend.db.connection import get_session
from backend.services.import_service import (
    import_from_json,
    import_single,
    get_last_import_time,
)
from backend.schemas.guali import ManualImportSchema

router = APIRouter(prefix="/api/import", tags=["导入"])


def _success(data: dict) -> dict:
    return {"code": 200, "data": data, "message": "success"}


def _error(message: str, code: int = 400) -> dict:
    return {"code": code, "data": None, "message": message}


@router.post("/json")
async def import_json(file: UploadFile, session: Session = Depends(get_session)):
    """上传 JSON 文件批量导入"""
    if not file.filename or not file.filename.endswith(".json"):
        return _error("仅支持 JSON 文件")

    # 写入临时文件
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w", encoding="utf-8"
    )
    try:
        content = await file.read()
        tmp.write(content.decode("utf-8"))
        tmp.close()

        result = import_from_json(tmp.name, session)
        return _success({"imported": result["imported"],
                         "skipped": result["skipped"]})
    except Exception as e:
        return _error(str(e))
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


@router.post("/manual")
async def import_manual(
    data: ManualImportSchema, session: Session = Depends(get_session)
):
    """手动导入单个卦例"""
    try:
        guali = import_single(data.model_dump(), session)
        return _success({"guali_id": guali.id})
    except Exception as e:
        return _error(str(e))


@router.get("/status")
async def import_status(session: Session = Depends(get_session)):
    """获取上次导入时间"""
    t = get_last_import_time(session)
    return _success({"last_import_time": t})
