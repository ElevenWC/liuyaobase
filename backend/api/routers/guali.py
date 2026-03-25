# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 卦例API路由

实现卦例的CRUD接口和详情计算接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from backend.db.connection import SyncSessionLocal
from backend.db.repositories import guali_repository, yao_detail_repository
from backend.db.models import GualiModel
from backend.core.models import Guali, create_guali_from_input
from backend.core.enums import ZhongGua
from backend.api.schemas import (
    GualiCreate,
    GualiUpdate,
    GualiResponse,
    GualiDetailResponse,
    GualiListResponse,
    YaoResponse,
    MessageResponse,
    CsvImportResponse,
    CsvImportResult
)
from backend.utils.validators import validate_csv_file, validate_csv_format


router = APIRouter(prefix="/api/guali", tags=["卦例管理"])


# =============================================================================
# 数据库会话依赖
# =============================================================================

def get_db():
    """
    获取数据库会话的依赖

    用于FastAPI的依赖注入
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# 辅助函数
# =============================================================================

def model_to_response(model: GualiModel) -> GualiResponse:
    """
    将数据库模型转换为响应模型
    """
    ben_gua = ZhongGua.from_code(model.ben_gua_code)
    zhi_gua = ZhongGua.from_code(model.zhi_gua_code) if model.zhi_gua_code else None

    return GualiResponse(
        id=model.id,
        solar_year=model.solar_year,
        solar_month=model.solar_month,
        solar_day=model.solar_day,
        ganzhi_year=model.ganzhi_year,
        ganzhi_month=model.ganzhi_month,
        ganzhi_day=model.ganzhi_day,
        xunkong=model.xunkong,
        ben_gua_name=ben_gua.gua_name if ben_gua else None,
        zhi_gua_name=zhi_gua.gua_name if zhi_gua else None,
        ben_gua_code=model.ben_gua_code,
        zhi_gua_code=model.zhi_gua_code or 0,
        yao_bian_code=model.yao_bian_code,
        gongwei=model.gongwei,
        gongwei_index=model.gongwei_index,
        zhan_wen=model.zhan_wen,
        zhan_duan=model.zhan_duan,
        image_path=model.image_path
    )


def guali_to_detail_response(guali: Guali) -> GualiDetailResponse:
    """
    将业务对象转换为详情响应模型
    """
    # 转换爻列表
    yao_responses = []
    for yao in guali.yaos:
        yao_resp = YaoResponse(
            position=yao.position,
            yao_type=yao.yao_type,
            state=yao.state,
            dizhi=yao.dizhi.value if yao.dizhi else None,
            liuqin=yao.liuqin.value if yao.liuqin else None,
            liushen=yao.liushen.value if yao.liushen else None,
            wuxing=yao.wuxing.value if yao.wuxing else None,
            is_world=yao.is_world,
            is_response=yao.is_response,
            position_name=yao.position_name,
            yao_type_name=yao.yao_type_name,
            state_name=yao.state_name
        )
        yao_responses.append(yao_resp)

    return GualiDetailResponse(
        id=guali.id,
        solar_year=guali.solar_year,
        solar_month=guali.solar_month,
        solar_day=guali.solar_day,
        ganzhi_year=guali.ganzhi_year,
        ganzhi_month=guali.ganzhi_month,
        ganzhi_day=guali.ganzhi_day,
        xunkong=guali.xunkong,
        ben_gua_name=guali.ben_gua_name,
        zhi_gua_name=guali.zhi_gua_name,
        ben_gua_code=guali.ben_gua_code,
        zhi_gua_code=guali.zhi_gua_code,
        yao_bian_code=guali.yao_bian_code,
        gongwei=guali.gongwei,
        gongwei_index=guali.gongwei_index,
        zhan_wen=guali.zhan_wen,
        zhan_duan=guali.zhan_duan,
        image_path=guali.image_path,
        yaos=yao_responses,
        fushen=guali.fushen if guali.fushen else None,
        fanyin_fuyin=guali.fanyin_fuyin if guali.fanyin_fuyin else None,
        shensha=guali.shensha if guali.shensha else None,
        shengwang_mujue=guali.shengwang_mujue if guali.shengwang_mujue else None
    )


# =============================================================================
# 任务 17.1 - 创建卦例接口
# =============================================================================

@router.post("", response_model=GualiResponse, status_code=201)
async def create_guali(
    data: GualiCreate,
    session: Session = Depends(get_db)
):
    """
    创建卦例

    - 接收卦例创建请求
    - 调用格式转换和计算引擎
    - 保存到数据库
    """
    try:
        # 1. 从输入创建业务对象
        guali = create_guali_from_input(
            solar_year=data.solar_year,
            solar_month=data.solar_month,
            solar_day=data.solar_day,
            ben_gua_name=data.ben_gua_name,
            zhi_gua_name=data.zhi_gua_name,
            zhan_wen=data.zhan_wen,
            zhan_duan=data.zhan_duan
        )

        # 2. 填充干支时间和计算所有属性
        guali.fill_ganzhi_time()
        guali.calculate_all()

        # 3. 保存到数据库
        model = guali_repository.create_from_guali(guali, session=session)

        # 4. 保存爻详情
        yao_detail_repository.save_yao_details(model.id, guali.yaos, session=session)

        # 5. 返回响应
        return model_to_response(model)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建卦例失败: {str(e)}")


# =============================================================================
# 任务 17.2 - 获取卦例接口
# =============================================================================

@router.get("/{guali_id}", response_model=GualiResponse)
async def get_guali(
    guali_id: int,
    session: Session = Depends(get_db)
):
    """
    获取单个卦例

    - 根据ID获取卦例基本信息
    """
    model = guali_repository.get_guali_by_id(guali_id, session=session)

    if not model:
        raise HTTPException(status_code=404, detail=f"卦例不存在: ID={guali_id}")

    return model_to_response(model)


# =============================================================================
# 任务 17.3 - 获取卦例列表接口
# =============================================================================

@router.get("", response_model=GualiListResponse)
async def list_gualis(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    year: Optional[int] = Query(default=None, ge=1900, le=2100, description="公历年筛选"),
    session: Session = Depends(get_db)
):
    """
    获取卦例列表

    - 支持分页
    - 支持按年份筛选
    """
    if year:
        models, total = guali_repository.get_gualis_by_year(
            year=year,
            page=page,
            page_size=page_size,
            session=session
        )
    else:
        models, total = guali_repository.get_all_gualis(
            page=page,
            page_size=page_size,
            session=session
        )

    # 计算总页数
    pages = (total + page_size - 1) // page_size

    # 转换为响应模型
    items = [model_to_response(m) for m in models]

    return GualiListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


# =============================================================================
# 任务 17.4 - 更新卦例接口
# =============================================================================

@router.put("/{guali_id}", response_model=GualiResponse)
async def update_guali(
    guali_id: int,
    data: GualiUpdate,
    session: Session = Depends(get_db)
):
    """
    更新卦例

    - 只允许更新语句字段（占问事由、占断）
    - 时间字段和重卦字段禁止修改
    """
    # 检查是否提供了更新数据
    if data.zhan_wen is None and data.zhan_duan is None and data.image_path is None:
        raise HTTPException(status_code=400, detail="请提供要更新的字段")

    # 更新卦例
    model = guali_repository.update_guali(
        guali_id=guali_id,
        zhan_wen=data.zhan_wen,
        zhan_duan=data.zhan_duan,
        image_path=data.image_path,
        session=session
    )

    if not model:
        raise HTTPException(status_code=404, detail=f"卦例不存在: ID={guali_id}")

    return model_to_response(model)


# =============================================================================
# 任务 17.5 - 删除卦例接口
# =============================================================================

@router.delete("/{guali_id}", response_model=MessageResponse)
async def delete_guali(
    guali_id: int,
    session: Session = Depends(get_db)
):
    """
    删除卦例

    - 同时级联删除关联的爻详情
    """
    success = guali_repository.delete_guali(guali_id, session=session)

    if not success:
        raise HTTPException(status_code=404, detail=f"卦例不存在: ID={guali_id}")

    return MessageResponse(message=f"卦例已删除: ID={guali_id}", success=True)


# =============================================================================
# 任务 18.1 - 卦例完整详情接口
# =============================================================================

@router.get("/{guali_id}/detail", response_model=GualiDetailResponse)
async def get_guali_detail(
    guali_id: int,
    session: Session = Depends(get_db)
):
    """
    获取卦例完整详情

    - 返回包含所有卦理计算结果
    - 包括：六爻详情、伏神、反吟伏吟、神煞、生旺墓绝
    """
    # 获取数据库模型
    model = guali_repository.get_guali_by_id(guali_id, session=session)

    if not model:
        raise HTTPException(status_code=404, detail=f"卦例不存在: ID={guali_id}")

    # 转换为业务对象（包含爻详情）
    guali = guali_repository.model_to_guali(model, with_yao_details=True)

    # 重新计算所有属性（确保数据完整）
    guali.calculate_all()

    # 返回详情响应
    return guali_to_detail_response(guali)


# =============================================================================
# 任务 19.2 - CSV导入接口
# =============================================================================

@router.post("/import-csv", response_model=CsvImportResponse)
async def import_csv(
    file: UploadFile = File(..., description="CSV文件"),
    session: Session = Depends(get_db)
):
    """
    CSV文件导入卦例

    CSV格式要求:
    - 第一列: 年;月.日 (如 2024;02.12)
    - 第二列: 本卦名 (如 乾为天)
    - 第三列: 之卦名 (可为空)
    - 第四列: 占问事由 (可为空)
    - 第五列: 占断 (可为空)
    - 第六列: 图片路径 (可为空)

    示例:
    2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨,
    2024;03.15,乾为天,,,测试占问,
    """
    # 检查文件类型
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="请上传CSV文件")

    # 读取文件内容
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取文件失败: {str(e)}")

    # 验证CSV内容
    validation_result = validate_csv_file(content)

    if validation_result["total_rows"] == 0:
        raise HTTPException(status_code=400, detail="CSV文件为空或格式不正确")

    # 准备导入结果
    results: List[CsvImportResult] = []
    success_count = 0
    failed_count = 0
    errors: List[str] = []

    # 逐条导入
    for i, data in enumerate(validation_result["data"], start=1):
        try:
            # 创建卦例业务对象
            guali = create_guali_from_input(
                solar_year=data["solar_year"],
                solar_month=data["solar_month"],
                solar_day=data["solar_day"],
                ben_gua_name=data["ben_gua_name"],
                zhi_gua_name=data["zhi_gua_name"],
                zhan_wen=data["zhan_wen"],
                zhan_duan=data["zhan_duan"]
            )

            # 填充干支时间和计算所有属性
            guali.fill_ganzhi_time()
            guali.calculate_all()

            # 设置图片路径
            if data.get("image_path"):
                guali.image_path = data["image_path"]

            # 保存到数据库
            model = guali_repository.create_from_guali(guali, session=session)

            # 保存爻详情
            yao_detail_repository.save_yao_details(model.id, guali.yaos, session=session)

            results.append(CsvImportResult(
                row_number=i,
                success=True,
                guali_id=model.id,
                error=None
            ))
            success_count += 1

        except Exception as e:
            error_msg = f"行 {i}: {str(e)}"
            errors.append(error_msg)
            results.append(CsvImportResult(
                row_number=i,
                success=False,
                guali_id=None,
                error=str(e)
            ))
            failed_count += 1

    # 添加验证阶段发现的错误
    if validation_result.get("errors"):
        errors.extend(validation_result["errors"])

    return CsvImportResponse(
        total_rows=validation_result["total_rows"],
        success_count=success_count,
        failed_count=failed_count + validation_result["invalid_rows"],
        results=results,
        errors=errors
    )
