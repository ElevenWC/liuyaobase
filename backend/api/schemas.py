# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - Pydantic模型定义

定义API请求和响应的数据模型
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date


# =============================================================================
# 爻相关模型
# =============================================================================

class YaoBase(BaseModel):
    """爻基础模型"""
    position: int = Field(..., ge=1, le=6, description="爻位 (1-6)")
    yao_type: int = Field(..., ge=0, le=1, description="爻类型 (1=阳爻, 0=阴爻)")
    state: int = Field(default=0, ge=0, le=1, description="爻状态 (1=动爻, 0=静爻)")


class YaoResponse(YaoBase):
    """爻响应模型"""
    model_config = ConfigDict(from_attributes=True)

    dizhi: Optional[str] = Field(default=None, description="爻地支")
    liuqin: Optional[str] = Field(default=None, description="六亲")
    liushen: Optional[str] = Field(default=None, description="六神")
    wuxing: Optional[str] = Field(default=None, description="五行")
    is_world: bool = Field(default=False, description="是否世爻")
    is_response: bool = Field(default=False, description="是否应爻")
    position_name: Optional[str] = Field(default=None, description="爻位名称")
    yao_type_name: Optional[str] = Field(default=None, description="爻类型名称")
    state_name: Optional[str] = Field(default=None, description="爻状态名称")


# =============================================================================
# 卦例创建请求模型
# =============================================================================

class GualiCreate(BaseModel):
    """
    卦例创建请求模型

    用于接收用户输入创建新卦例的数据
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "solar_year": 2024,
                "solar_month": 2,
                "solar_day": 12,
                "ben_gua_name": "乾为天",
                "zhi_gua_name": None,
                "zhan_wen": "测试占问",
                "zhan_duan": None,
                "image_path": None
            }
        }
    )

    # 公历时间（必填）
    solar_year: int = Field(..., ge=1900, le=2100, description="公历年")
    solar_month: int = Field(..., ge=1, le=12, description="公历月")
    solar_day: int = Field(..., ge=1, le=31, description="公历日")

    # 卦信息
    ben_gua_name: str = Field(..., min_length=2, max_length=10, description="本卦名")
    zhi_gua_name: Optional[str] = Field(default=None, min_length=2, max_length=10, description="之卦名（可选）")

    # 文本信息（可选）
    zhan_wen: Optional[str] = Field(default=None, max_length=500, description="占问事由")
    zhan_duan: Optional[str] = Field(default=None, max_length=500, description="占断")
    image_path: Optional[str] = Field(default=None, max_length=255, description="图片路径")


class GualiUpdate(BaseModel):
    """
    卦例更新请求模型

    只允许更新语句字段，时间字段和重卦字段禁止修改
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "zhan_wen": "更新后的占问事由",
                "zhan_duan": "更新后的占断"
            }
        }
    )

    zhan_wen: Optional[str] = Field(default=None, max_length=500, description="占问事由")
    zhan_duan: Optional[str] = Field(default=None, max_length=500, description="占断")
    image_path: Optional[str] = Field(default=None, max_length=255, description="图片路径")


# =============================================================================
# 卦例响应模型
# =============================================================================

class GualiResponse(BaseModel):
    """
    卦例响应模型

    用于返回卦例的基本信息
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "solar_year": 2024,
                "solar_month": 2,
                "solar_day": 12,
                "ganzhi_year": "甲辰",
                "ganzhi_month": "丙寅",
                "ganzhi_day": "甲午",
                "xunkong": "辰巳",
                "ben_gua_name": "乾为天",
                "zhi_gua_name": None,
                "ben_gua_code": 63,
                "zhi_gua_code": 0,
                "yao_bian_code": 0,
                "gongwei": "乾宫",
                "gongwei_index": "本宫",
                "zhan_wen": "测试占问",
                "zhan_duan": None,
                "image_path": None
            }
        }
    )

    id: int = Field(..., description="卦例ID")

    # 公历时间
    solar_year: int = Field(..., description="公历年")
    solar_month: int = Field(..., description="公历月")
    solar_day: int = Field(..., description="公历日")

    # 干支时间
    ganzhi_year: Optional[str] = Field(default=None, description="年柱干支")
    ganzhi_month: Optional[str] = Field(default=None, description="月柱干支")
    ganzhi_day: Optional[str] = Field(default=None, description="日柱干支")
    xunkong: Optional[str] = Field(default=None, description="旬空")

    # 卦信息
    ben_gua_name: Optional[str] = Field(default=None, description="本卦名")
    zhi_gua_name: Optional[str] = Field(default=None, description="之卦名")
    ben_gua_code: int = Field(default=0, description="本卦代码")
    zhi_gua_code: int = Field(default=0, description="之卦代码")
    yao_bian_code: int = Field(default=0, description="爻变代码")
    gongwei: Optional[str] = Field(default=None, description="卦宫")
    gongwei_index: Optional[str] = Field(default=None, description="宫位")

    # 文本信息
    zhan_wen: Optional[str] = Field(default=None, description="占问事由")
    zhan_duan: Optional[str] = Field(default=None, description="占断")
    image_path: Optional[str] = Field(default=None, description="图片路径")


class GualiDetailResponse(GualiResponse):
    """
    卦例详情响应模型

    包含完整的卦理计算结果
    """
    # 六爻详情
    yaos: List[YaoResponse] = Field(default_factory=list, description="六爻详情列表")

    # 伏神信息
    fushen: Optional[Dict[str, Any]] = Field(default=None, description="伏神信息")

    # 反吟伏吟信息
    fanyin_fuyin: Optional[Dict[str, Any]] = Field(default=None, description="反吟伏吟信息")

    # 神煞信息
    shensha: Optional[Dict[str, Any]] = Field(default=None, description="神煞信息")

    # 生旺墓绝信息
    shengwang_mujue: Optional[Dict[str, Any]] = Field(default=None, description="生旺墓绝信息")


# =============================================================================
# 列表响应模型
# =============================================================================

class GualiListResponse(BaseModel):
    """卦例列表响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "pages": 10
            }
        }
    )

    items: List[GualiResponse] = Field(..., description="卦例列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


# =============================================================================
# 通用响应模型
# =============================================================================

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "操作成功",
                "success": True
            }
        }
    )

    message: str = Field(..., description="消息内容")
    success: bool = Field(default=True, description="是否成功")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "卦例不存在",
                "code": "NOT_FOUND"
            }
        }
    )

    detail: str = Field(..., description="错误详情")
    code: Optional[str] = Field(default=None, description="错误代码")


# =============================================================================
# CSV导入相关模型
# =============================================================================

class CsvImportResult(BaseModel):
    """单条CSV导入结果"""
    row_number: int = Field(..., description="行号")
    success: bool = Field(..., description="是否成功")
    guali_id: Optional[int] = Field(default=None, description="创建的卦例ID")
    error: Optional[str] = Field(default=None, description="错误信息")


class CsvImportResponse(BaseModel):
    """CSV导入响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_rows": 10,
                "success_count": 8,
                "failed_count": 2,
                "results": [
                    {"row_number": 1, "success": True, "guali_id": 1, "error": None},
                    {"row_number": 2, "success": False, "guali_id": None, "error": "无效的卦名"}
                ],
                "errors": ["行 2: 无效的卦名", "行 5: 时间格式错误"]
            }
        }
    )

    total_rows: int = Field(..., description="总行数")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    results: List[CsvImportResult] = Field(default_factory=list, description="每行导入结果")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")


# =============================================================================
# 图片相关模型
# =============================================================================

class ImageUploadResponse(BaseModel):
    """图片上传响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "20240212_abc123.jpg",
                "original_filename": "test.jpg",
                "file_size": 102400,
                "file_path": "./images/20240212_abc123.jpg",
                "url": "/api/images/20240212_abc123.jpg",
                "success": True,
                "message": "图片上传成功"
            }
        }
    )

    filename: str = Field(..., description="存储的文件名")
    original_filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_path: str = Field(..., description="存储路径")
    url: str = Field(..., description="访问URL")
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="图片上传成功", description="消息")


class ImageStorageConfigResponse(BaseModel):
    """图片存储配置响应模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "storage_path": "./images",
                "absolute_path": "D:/Code/liuyao/liuyaobase/images",
                "allowed_extensions": ["jpg", "jpeg", "png", "gif", "bmp"],
                "max_file_size": 10485760
            }
        }
    )

    storage_path: str = Field(..., description="配置的存储路径")
    absolute_path: str = Field(..., description="绝对路径")
    allowed_extensions: List[str] = Field(..., description="允许的文件扩展名")
    max_file_size: int = Field(..., description="最大文件大小（字节）")


# =============================================================================
# 检索相关模型
# =============================================================================

class SearchCondition(BaseModel):
    """
    检索条件模型
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "ben_gua_name",
                "operator": "=",
                "value": "乾为天",
                "logic": "and",
                "relation_type": None,
                "target_field": None
            }
        }
    )

    field: str = Field(..., description="字段名")
    operator: str = Field(default="=", description="运算符")
    value: Optional[Any] = Field(default=None, description="值")
    logic: str = Field(default="and", description="逻辑运算符 (and/or)")
    relation_type: Optional[str] = Field(default=None, description="关系类型 (he/chong/sheng/ke)")
    target_field: Optional[str] = Field(default=None, description="目标字段（用于关系运算）")


class SearchRequest(BaseModel):
    """
    检索请求模型
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conditions": [
                    {"field": "ben_gua_name", "operator": "=", "value": "乾为天", "logic": "and"}
                ],
                "logic": "and",
                "page": 1,
                "page_size": 20
            }
        }
    )

    conditions: List[SearchCondition] = Field(..., description="检索条件列表")
    logic: str = Field(default="and", description="条件间逻辑 (and/or)")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class SearchResponse(BaseModel):
    """
    检索响应模型
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "items": []
            }
        }
    )

    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[GualiResponse] = Field(default_factory=list, description="检索结果列表")
