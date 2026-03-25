# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 图片API路由

实现图片上传和访问接口
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from backend.config import settings
from backend.api.schemas import (
    ImageUploadResponse,
    ImageStorageConfigResponse,
    MessageResponse
)


router = APIRouter(prefix="/api/images", tags=["图片管理"])


# =============================================================================
# 辅助函数
# =============================================================================

def generate_filename(original_filename: str) -> str:
    """
    生成唯一文件名

    格式: YYYYMMDD_uuid.扩展名
    """
    # 获取文件扩展名
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1].lower()

    # 生成唯一文件名
    date_prefix = datetime.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8]

    return f"{date_prefix}_{unique_id}{ext}"


def validate_image_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
    """
    验证图片文件

    Returns:
        (是否有效, 错误信息)
    """
    # 检查文件名
    if not filename:
        return False, "文件名为空"

    # 检查扩展名
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if ext not in settings.image_extensions_list:
        return False, f"不支持的文件类型: .{ext}，支持的类型: {', '.join(settings.image_extensions_list)}"

    # 检查文件大小
    if file_size > settings.image_max_size:
        max_size_mb = settings.image_max_size / (1024 * 1024)
        return False, f"文件大小超过限制 ({max_size_mb}MB)"

    return True, None


# =============================================================================
# 任务 20.1 - 图片存储配置接口
# =============================================================================

@router.get("/config", response_model=ImageStorageConfigResponse)
async def get_image_storage_config():
    """
    获取图片存储配置

    返回图片存储路径等信息，供前端显示给用户
    """
    # 确保目录存在
    abs_path = settings.ensure_image_directory()

    return ImageStorageConfigResponse(
        storage_path=settings.image_storage_path,
        absolute_path=abs_path,
        allowed_extensions=settings.image_extensions_list,
        max_file_size=settings.image_max_size
    )


# =============================================================================
# 任务 20.2 - 图片上传接口
# =============================================================================

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(..., description="图片文件")
):
    """
    上传图片

    支持的图片格式: jpg, jpeg, png, gif, bmp
    最大文件大小: 10MB

    返回图片存储路径和访问URL
    """
    # 读取文件内容
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取文件失败: {str(e)}")

    file_size = len(content)

    # 验证文件
    valid, error = validate_image_file(file.filename or "", file_size)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    # 确保目录存在
    storage_path = settings.ensure_image_directory()

    # 生成唯一文件名
    new_filename = generate_filename(file.filename or "image.jpg")
    file_path = os.path.join(storage_path, new_filename)

    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

    # 构建响应
    relative_path = os.path.join(settings.image_storage_path, new_filename)

    return ImageUploadResponse(
        filename=new_filename,
        original_filename=file.filename or "unknown",
        file_size=file_size,
        file_path=relative_path,
        url=f"/api/images/{new_filename}",
        success=True,
        message="图片上传成功"
    )


# =============================================================================
# 任务 20.3 - 图片访问接口
# =============================================================================

@router.get("/{filename}")
async def get_image(filename: str):
    """
    获取图片

    通过文件名访问已上传的图片
    """
    # 安全检查：防止路径遍历攻击
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 额外检查：确保文件名不包含危险字符
    if not filename or filename.startswith(".") or filename.startswith("-"):
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 构建文件路径
    storage_path = settings.image_storage_absolute_path
    file_path = os.path.join(storage_path, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"图片不存在: {filename}")

    # 检查是否是文件
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    # 获取文件扩展名确定媒体类型
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    media_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "bmp": "image/bmp"
    }

    media_type = media_type_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


# =============================================================================
# 图片删除接口（可选）
# =============================================================================

@router.delete("/{filename}", response_model=MessageResponse)
async def delete_image(filename: str):
    """
    删除图片

    通过文件名删除已上传的图片
    """
    # 安全检查：防止路径遍历攻击
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 额外检查：确保文件名不包含危险字符
    if not filename or filename.startswith(".") or filename.startswith("-"):
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 构建文件路径
    storage_path = settings.image_storage_absolute_path
    file_path = os.path.join(storage_path, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"图片不存在: {filename}")

    # 检查是否是文件
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    # 删除文件
    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

    return MessageResponse(message=f"图片已删除: {filename}", success=True)


# =============================================================================
# 图片列表接口（可选）
# =============================================================================

@router.get("")
async def list_images():
    """
    获取图片列表

    返回所有已上传的图片文件名列表
    """
    storage_path = settings.image_storage_absolute_path

    # 确保目录存在
    if not os.path.exists(storage_path):
        return {"images": [], "total": 0}

    # 获取所有图片文件
    images = []
    for filename in os.listdir(storage_path):
        file_path = os.path.join(storage_path, filename)
        if os.path.isfile(file_path):
            ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
            if ext in settings.image_extensions_list:
                stat = os.stat(file_path)
                images.append({
                    "filename": filename,
                    "url": f"/api/images/{filename}",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

    # 按修改时间降序排序
    images.sort(key=lambda x: x["modified"], reverse=True)

    return {"images": images, "total": len(images)}
