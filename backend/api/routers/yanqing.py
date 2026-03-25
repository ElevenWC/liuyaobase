# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 占验情况API路由

提供占验情况的标注、查询、导入导出功能。

占验情况与主数据库弱耦合，使用独立的JSON文件存储。
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.yanqing_service import get_yanqing_service, YanqingService


router = APIRouter(prefix="/api/yanqing", tags=["占验情况"])


# =============================================================================
# Pydantic模型
# =============================================================================

class YanqingAnnotateRequest(BaseModel):
    """占验标注请求模型"""
    guali_id: int = Field(..., description="卦例ID")
    status: str = Field(..., description="占验状态：应验、模糊、不验")
    note: Optional[str] = Field(default=None, max_length=500, description="备注说明")


class YanqingResponse(BaseModel):
    """占验情况响应模型"""
    guali_id: int = Field(..., description="卦例ID")
    status: str = Field(..., description="占验状态")
    note: str = Field(default="", description="备注说明")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class YanqingBatchRequest(BaseModel):
    """批量获取占验情况请求"""
    guali_ids: List[int] = Field(..., description="卦例ID列表")


class YanqingImportRequest(BaseModel):
    """导入占验情况请求"""
    json_data: str = Field(..., description="JSON格式的占验数据")
    merge: bool = Field(default=True, description="是否合并现有数据")


class YanqingStatisticsResponse(BaseModel):
    """占验情况统计响应"""
    total: int = Field(..., description="总标注数")
    应验: int = Field(default=0, description="应验数量")
    模糊: int = Field(default=0, description="模糊数量")
    不验: int = Field(default=0, description="不验数量")


# =============================================================================
# API接口
# =============================================================================

@router.post("/annotate", response_model=YanqingResponse)
async def annotate_yanqing(request: YanqingAnnotateRequest):
    """
    标注占验情况

    为指定卦例标注占验状态（应验、模糊、不验）和备注。

    - **guali_id**: 卦例ID
    - **status**: 占验状态（应验、模糊、不验）
    - **note**: 备注说明（可选）
    """
    service = get_yanqing_service()

    try:
        result = service.annotate(
            guali_id=request.guali_id,
            status=request.status,
            note=request.note
        )
        return YanqingResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{guali_id}", response_model=YanqingResponse)
async def get_yanqing(guali_id: int):
    """
    获取指定卦例的占验情况

    - **guali_id**: 卦例ID
    """
    service = get_yanqing_service()
    result = service.get_by_guali_id(guali_id)

    if result is None:
        raise HTTPException(status_code=404, detail="该卦例暂无占验标注")

    return YanqingResponse(**result)


@router.put("/{guali_id}", response_model=YanqingResponse)
async def update_yanqing(guali_id: int, request: YanqingAnnotateRequest):
    """
    更新占验情况标注

    - **guali_id**: 卦例ID
    - **status**: 新的占验状态
    - **note**: 新的备注说明
    """
    # 更新操作与创建操作相同，使用相同的service方法
    service = get_yanqing_service()

    try:
        result = service.annotate(
            guali_id=guali_id,
            status=request.status,
            note=request.note
        )
        return YanqingResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{guali_id}")
async def delete_yanqing(guali_id: int):
    """
    删除占验情况标注

    - **guali_id**: 卦例ID
    """
    service = get_yanqing_service()
    success = service.delete(guali_id)

    if not success:
        raise HTTPException(status_code=404, detail="该卦例暂无占验标注")

    return {"message": "删除成功", "guali_id": guali_id}


@router.post("/batch", response_model=List[YanqingResponse])
async def get_yanqing_batch(request: YanqingBatchRequest):
    """
    批量获取多个卦例的占验情况

    - **guali_ids**: 卦例ID列表
    """
    service = get_yanqing_service()
    results = service.get_by_ids(request.guali_ids)

    return [YanqingResponse(**data) for data in results.values()]


@router.get("/status/{status}", response_model=List[YanqingResponse])
async def get_yanqing_by_status(status: str):
    """
    按状态获取占验情况列表

    - **status**: 占验状态（应验、模糊、不验）
    """
    valid_statuses = ['应验', '模糊', '不验']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"无效的状态值，有效值: {valid_statuses}"
        )

    service = get_yanqing_service()
    results = service.get_by_status(status)

    return [YanqingResponse(**data) for data in results]


@router.get("/statistics", response_model=YanqingStatisticsResponse)
async def get_yanqing_statistics():
    """
    获取占验情况统计信息

    返回各状态的标注数量统计。
    """
    service = get_yanqing_service()
    stats = service.get_statistics()
    return YanqingStatisticsResponse(**stats)


@router.get("/export")
async def export_yanqing():
    """
    导出所有占验情况数据

    返回JSON格式的占验情况数据，可用于备份或迁移。
    """
    service = get_yanqing_service()
    json_data = service.export_data()

    return {
        "message": "导出成功",
        "data": json_data,
        "count": len(service.get_all())
    }


@router.post("/import")
async def import_yanqing(request: YanqingImportRequest):
    """
    导入占验情况数据

    - **json_data**: JSON格式的占验数据
    - **merge**: 是否合并现有数据（True=合并，False=覆盖）
    """
    service = get_yanqing_service()

    try:
        count = service.import_data(request.json_data, request.merge)
        return {
            "message": "导入成功",
            "imported_count": count,
            "merge_mode": request.merge
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
