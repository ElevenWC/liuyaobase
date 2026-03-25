# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 集成测试

阶段三十一：端到端集成测试
- 31.1: 卦例录入流程测试
- 31.2: 占验情况流程测试
- 31.3: 完整综合流程测试
- 31.4: 性能测试
"""
import pytest
import tempfile
import os
import time
from datetime import datetime
from unittest.mock import patch

from backend.core.enums import ZhongGua, Dizhi, LiuQin, LiuShen
from backend.core.models import Guali, Yao, create_guali_from_input
from backend.core.converter import (
    parse_standard_format,
    standard_format_to_guali
)
from backend.core.time_converter import solar_to_ganzhi_full
from backend.db.connection import get_session, Base, sync_engine
from backend.db.models import GualiModel, YaoDetailModel
from backend.db.repositories import GualiRepository, YaoDetailRepository
from backend.services.yanqing_service import YanqingService
from backend.utils.validators import validate_csv_format, parse_csv_to_guali_inputs


# ==================== 测试固件 ====================

@pytest.fixture(scope="function")
def db_session():
    """创建数据库会话"""
    # 创建所有表（如果不存在）
    Base.metadata.create_all(bind=sync_engine)

    session = None
    try:
        with get_session() as session:
            yield session
    finally:
        # 清理测试数据
        if session:
            try:
                session.query(YaoDetailModel).delete()
                session.query(GualiModel).delete()
                session.commit()
            except:
                pass


@pytest.fixture
def guali_repo():
    """获取卦例仓库实例"""
    return GualiRepository()


@pytest.fixture
def yao_repo():
    """获取爻详情仓库实例"""
    return YaoDetailRepository()


@pytest.fixture
def temp_yanqing_file():
    """创建临时占验情况文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('{}')
        temp_path = f.name
    yield temp_path
    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def yanqing_service(temp_yanqing_file):
    """创建占验情况服务"""
    return YanqingService(storage_path=temp_yanqing_file)


# ==================== 辅助函数 ====================

def create_and_save_guali(repo, yao_repo, session, **kwargs):
    """
    创建并保存卦例的辅助函数

    Args:
        repo: GualiRepository实例
        yao_repo: YaoDetailRepository实例
        session: 数据库会话
        **kwargs: 传递给create_guali_from_input的参数

    Returns:
        GualiModel: 保存后的卦例模型
    """
    # 提取create_guali_from_input支持的参数
    supported_params = {
        'solar_year', 'solar_month', 'solar_day',
        'ben_gua_name', 'zhi_gua_name',
        'zhan_wen', 'zhan_duan'
    }

    # 过滤参数
    guali_params = {k: v for k, v in kwargs.items() if k in supported_params}
    image_path = kwargs.get('image_path')

    # 创建业务对象
    guali_biz = create_guali_from_input(**guali_params)

    # 设置图片路径
    if image_path:
        guali_biz.image_path = image_path

    # 先填充干支时间（六神计算需要日干）
    guali_biz.fill_ganzhi_time()

    # 再计算所有派生属性（纳甲装卦、六亲、六神等）
    guali_biz.calculate_all()

    # 保存到数据库
    guali_model = repo.create_from_guali(guali_biz, session=session)

    # 保存爻详情
    yao_repo.save_yao_details(guali_model.id, guali_biz.yaos, session=session)

    return guali_model


# ==================== 31.1 端到端测试 - 录入流程 ====================

class TestE2EEntryFlow:
    """端到端测试 - 卦例录入流程"""

    def test_manual_entry_basic_guali(self, guali_repo, yao_repo, db_session):
        """测试手动输入基本卦例（无之卦）"""
        # 创建并保存基本卦例
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="山风蛊",
            zhi_gua_name=None,
            zhan_wen="占问股票走势",
            zhan_duan="占断上涨"
        )

        # 验证基本属性
        assert guali.id is not None
        assert guali.solar_year == 2024
        assert guali.solar_month == 2
        assert guali.solar_day == 12
        assert guali.ben_gua_code == ZhongGua.SHAN_FENG_GU.code

        # 验证干支时间已计算
        assert guali.ganzhi_year is not None
        assert guali.ganzhi_month is not None
        assert guali.ganzhi_day is not None
        assert guali.xunkong is not None

        # 验证卦宫信息
        assert guali.gongwei == "巽宫"
        assert guali.gongwei_index == "归魂"

        # 验证爻详情已保存
        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)
        assert len(yao_details) == 6

    def test_manual_entry_with_zhi_gua(self, guali_repo, yao_repo, db_session):
        """测试手动输入带之卦的卦例"""
        # 创建带之卦的卦例
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋",
            zhan_wen="占问工作变动",
            zhan_duan="占断顺利"
        )

        # 验证之卦信息
        assert guali.zhi_gua_code == ZhongGua.HUO_DI_JIN.code
        assert guali.yao_bian_code is not None
        assert guali.yao_bian_code > 0  # 有动爻

        # 验证动爻识别
        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)
        moving_yaos = [y for y in yao_details if y.state == 1]
        assert len(moving_yaos) > 0

    def test_standard_format_parsing(self):
        """测试标准格式解析"""
        # 测试完整格式
        result = parse_standard_format("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")

        assert result['solar_year'] == 2024
        assert result['solar_month'] == 2
        assert result['solar_day'] == 12
        assert result['ben_gua_name'] == "山风蛊"
        assert result['zhi_gua_name'] == "火地晋"
        assert result['zhan_wen'] == "占问股票走势"
        assert result['zhan_duan'] == "占断上涨"

    def test_standard_format_to_guali(self):
        """测试从标准格式创建完整卦例"""
        guali = standard_format_to_guali("2024;02.12,乾为天,,占问健康,吉")

        assert guali.solar_year == 2024
        assert guali.solar_month == 2
        assert guali.solar_day == 12
        assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali.zhi_gua is None
        assert guali.zhan_wen == "占问健康"
        assert guali.zhan_duan == "吉"

    def test_csv_import(self, guali_repo, yao_repo, db_session):
        """测试CSV批量导入"""
        csv_content = """2024;02.12,山风蛊,火地晋,占问股票,上涨
2024;02.15,乾为天,,占问工作,顺利
2024;02.20,坤为地,,测试占问,测试占断"""

        # 验证CSV格式
        validation_result = validate_csv_format(csv_content)
        assert validation_result['valid'] is True

        # 解析CSV - 返回元组 (data, errors)
        inputs, errors = parse_csv_to_guali_inputs(csv_content)
        assert len(inputs) == 3
        assert len(errors) == 0

        # 批量创建卦例
        created_ids = []

        for input_data in inputs:
            guali = create_and_save_guali(
                guali_repo, yao_repo, db_session, **input_data
            )
            created_ids.append(guali.id)

        # 验证所有卦例已创建
        assert len(created_ids) == 3
        for guali_id in created_ids:
            guali = guali_repo.get_guali_by_id(guali_id, session=db_session)
            assert guali is not None

    def test_csv_import_with_image_paths(self):
        """测试CSV导入带图片路径"""
        csv_content = "2024;02.12,山风蛊,,占问股票,上涨,test.jpg"

        inputs, errors = parse_csv_to_guali_inputs(csv_content)
        assert len(inputs) == 1
        assert inputs[0]['image_path'] == "test.jpg"

    def test_guali_six_relations_calculation(self, guali_repo, yao_repo, db_session):
        """测试六亲计算正确性"""
        # 创建乾为天卦例（乾宫，金）
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhan_wen="测试六亲"
        )

        # 获取爻详情
        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)

        # 乾为天六亲验证（卦宫五行=金）
        # 初爻子（水），金生水 → 子孙
        assert yao_details[0].liuqin == "子孙"
        # 二爻寅（木），金克木 → 妻财
        assert yao_details[1].liuqin == "妻财"

    def test_guali_six_gods_calculation(self, guali_repo, yao_repo, db_session):
        """测试六神计算正确性"""
        # 2024年2月12日是丙午日
        # 丙日六神：初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhan_wen="测试六神"
        )

        # 获取爻详情
        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)

        # 丙日六神：初朱雀、二勾陈、三螣蛇、四白虎、五玄武、上青龙
        assert yao_details[0].liushen == "朱雀"  # 初爻
        assert yao_details[1].liushen == "勾陈"  # 二爻
        assert yao_details[2].liushen == "螣蛇"  # 三爻
        assert yao_details[3].liushen == "白虎"  # 四爻
        assert yao_details[4].liushen == "玄武"  # 五爻
        assert yao_details[5].liushen == "青龙"  # 上爻


# ==================== 31.2 端到端测试 - 占验情况流程 ====================

class TestE2EYanqingFlow:
    """端到端测试 - 占验情况流程"""

    def test_yanqing_annotation(self, yanqing_service):
        """测试占验情况标注"""
        # 标注占验情况
        result = yanqing_service.annotate(
            guali_id=1,
            status="应验",
            note="实际走势与占断一致"
        )

        assert result['guali_id'] == 1
        assert result['status'] == "应验"
        assert result['note'] == "实际走势与占断一致"
        assert 'created_at' in result
        assert 'updated_at' in result

    def test_yanqing_query(self, yanqing_service):
        """测试占验情况查询"""
        # 先标注
        yanqing_service.annotate(1, "应验", "测试备注")

        # 查询
        result = yanqing_service.get_by_guali_id(1)
        assert result is not None
        assert result['status'] == "应验"

    def test_yanqing_batch_query(self, yanqing_service):
        """测试批量获取占验情况"""
        # 标注多个
        yanqing_service.annotate(1, "应验", "")
        yanqing_service.annotate(2, "不验", "")
        yanqing_service.annotate(3, "模糊", "")

        # 批量获取
        results = yanqing_service.get_by_ids([1, 2, 3])
        assert len(results) == 3

    def test_yanqing_update(self, yanqing_service):
        """测试更新占验情况"""
        # 先标注
        yanqing_service.annotate(1, "模糊", "待观察")

        # 更新
        result = yanqing_service.annotate(1, "应验", "已确认应验")

        assert result['status'] == "应验"
        assert result['note'] == "已确认应验"
        # created_at应保持不变
        original_created = yanqing_service._cache[1]['created_at']
        assert result['created_at'] == original_created

    def test_yanqing_delete(self, yanqing_service):
        """测试删除占验情况"""
        # 先标注
        yanqing_service.annotate(1, "应验", "")

        # 删除
        success = yanqing_service.delete(1)
        assert success is True

        # 验证已删除
        result = yanqing_service.get_by_guali_id(1)
        assert result is None

    def test_yanqing_statistics(self, yanqing_service):
        """测试占验情况统计"""
        # 标注多个
        yanqing_service.annotate(1, "应验", "")
        yanqing_service.annotate(2, "应验", "")
        yanqing_service.annotate(3, "不验", "")
        yanqing_service.annotate(4, "模糊", "")

        stats = yanqing_service.get_statistics()
        assert stats['total'] == 4
        assert stats['应验'] == 2
        assert stats['不验'] == 1
        assert stats['模糊'] == 1

    def test_yanqing_import_export(self, yanqing_service):
        """测试占验情况导入导出"""
        # 标注数据
        yanqing_service.annotate(1, "应验", "测试1")
        yanqing_service.annotate(2, "不验", "测试2")

        # 导出
        exported = yanqing_service.export_data()
        assert "应验" in exported
        assert "不验" in exported

        # 清空后导入
        yanqing_service._cache = {}
        yanqing_service._loaded = False

        import_count = yanqing_service.import_data(exported)
        assert import_count == 2

        # 验证导入成功
        result = yanqing_service.get_by_guali_id(1)
        assert result is not None


# ==================== 31.3 端到端测试 - 完整综合流程 ====================

class TestE2EFullFlow:
    """端到端测试 - 完整综合流程"""

    def test_full_workflow(self, guali_repo, yao_repo, db_session, temp_yanqing_file):
        """测试完整的业务流程"""
        yanqing_svc = YanqingService(storage_path=temp_yanqing_file)

        # 1. 导入卦例数据
        csv_content = """2024;01.15,山风蛊,火地晋,占问股票A走势,看涨
2024;01.20,乾为天,,占问工作调动,顺利
2024;02.01,坤为地,,占问健康状况,平稳
2024;02.10,水雷屯,,占问投资收益,有财
2024;02.15,雷风恒,,占问感情发展,持久"""

        inputs, errors = parse_csv_to_guali_inputs(csv_content)
        created_ids = []

        for input_data in inputs:
            guali = create_and_save_guali(
                guali_repo, yao_repo, db_session, **input_data
            )
            created_ids.append(guali.id)

        assert len(created_ids) == 5

        # 2. 标注多个卦例的占验情况
        yanqing_svc.annotate(created_ids[0], "应验", "股票确实上涨")
        yanqing_svc.annotate(created_ids[1], "应验", "工作调动成功")
        yanqing_svc.annotate(created_ids[2], "模糊", "健康情况有所好转但不明显")
        yanqing_svc.annotate(created_ids[3], "不验", "投资亏损")

        # 3. 验证统计数据
        stats = yanqing_svc.get_statistics()
        assert stats['total'] == 4
        assert stats['应验'] == 2
        assert stats['模糊'] == 1
        assert stats['不验'] == 1

        # 4. 使用多种检索条件查询
        # 按年份筛选
        year_results, total = guali_repo.get_all_gualis(session=db_session)
        assert total >= 5

        # 按ID获取详情
        detail = guali_repo.get_guali_by_id(created_ids[0], session=db_session)
        assert detail is not None
        assert detail.ben_gua_code == ZhongGua.SHAN_FENG_GU.code

        # 5. 验证占验情况与卦例关联
        yq_data = yanqing_svc.get_by_ids(created_ids)
        assert len(yq_data) == 4

        # 6. 更新卦例的占问事由
        guali_repo.update_guali(created_ids[0], zhan_wen="更新后:占问股票A走势", session=db_session)
        updated = guali_repo.get_guali_by_id(created_ids[0], session=db_session)
        assert "更新后" in updated.zhan_wen

        # 7. 验证导入导出
        exported = yanqing_svc.export_data()
        assert str(created_ids[0]) in exported

    def test_guali_with_all_features(self, guali_repo, yao_repo, db_session):
        """测试带有所有特性的卦例"""
        # 创建带之卦的卦例
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=3,
            solar_day=15,
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋",
            zhan_wen="综合测试",
            zhan_duan="测试占断"
        )

        # 获取完整详情
        guali_data = guali_repo.get_guali_by_id(guali.id, session=db_session)
        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)

        # 验证卦例基本信息
        assert guali_data.ben_gua_code is not None
        assert guali_data.zhi_gua_code is not None
        assert guali_data.yao_bian_code > 0

        # 验证干支时间
        assert guali_data.ganzhi_year is not None
        assert guali_data.ganzhi_month is not None
        assert guali_data.ganzhi_day is not None
        assert guali_data.xunkong is not None

        # 验证六爻信息
        assert len(yao_details) == 6
        for yao in yao_details:
            assert yao.dizhi is not None
            assert yao.liuqin is not None
            assert yao.liushen is not None

        # 验证世应设置
        world_yaos = [y for y in yao_details if y.is_world]
        response_yaos = [y for y in yao_details if y.is_response]
        assert len(world_yaos) == 1
        assert len(response_yaos) == 1

    def test_delete_cascade(self, guali_repo, yao_repo, db_session):
        """测试删除卦例时级联删除爻详情"""
        # 创建卦例
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024,
            solar_month=1,
            solar_day=1,
            ben_gua_name="乾为天",
            zhan_wen="测试删除"
        )

        guali_id = guali.id

        # 验证爻详情存在
        yao_details = yao_repo.get_yao_details(guali_id, session=db_session)
        assert len(yao_details) == 6

        # 删除卦例
        guali_repo.delete_guali(guali_id, session=db_session)
        db_session.flush()

        # 验证卦例已删除
        deleted = guali_repo.get_guali_by_id(guali_id, session=db_session)
        assert deleted is None

        # 验证爻详情已级联删除
        deleted_yaos = yao_repo.get_yao_details(guali_id, session=db_session)
        assert len(deleted_yaos) == 0


# ==================== 31.4 性能测试 ====================

class TestPerformance:
    """性能测试"""

    def test_batch_import_performance(self, guali_repo, yao_repo, db_session):
        """测试批量导入性能"""
        # 生成100个测试卦例
        gua_names = [
            "乾为天", "坤为地", "水雷屯", "山水蒙", "水天需",
            "天水讼", "地水师", "水地比", "风天小畜", "天泽履"
        ]

        start_time = time.time()

        for i in range(100):
            gua_name = gua_names[i % len(gua_names)]
            create_and_save_guali(
                guali_repo, yao_repo, db_session,
                solar_year=2024,
                solar_month=(i % 12) + 1,
                solar_day=(i % 28) + 1,
                ben_gua_name=gua_name,
                zhan_wen=f"性能测试{i+1}"
            )

        elapsed = time.time() - start_time

        # 100个卦例创建应该在30秒内完成
        assert elapsed < 30, f"批量导入耗时 {elapsed:.2f}s 超过30秒"

        # 验证所有卦例已创建
        all_gualis, total = guali_repo.get_all_gualis(session=db_session)
        assert total >= 100

    def test_query_performance(self, guali_repo, yao_repo, db_session):
        """测试查询性能"""
        # 先创建测试数据
        for i in range(50):
            create_and_save_guali(
                guali_repo, yao_repo, db_session,
                solar_year=2024,
                solar_month=2,
                solar_day=(i % 28) + 1,
                ben_gua_name="乾为天",
                zhan_wen=f"查询性能测试{i+1}"
            )

        # 测试列表查询性能
        start_time = time.time()
        results, total = guali_repo.get_all_gualis(session=db_session)
        elapsed = time.time() - start_time

        # 查询应该在1秒内完成
        assert elapsed < 1, f"查询耗时 {elapsed:.2f}s 超过1秒"
        assert total >= 50

    def test_yanqing_service_performance(self, yanqing_service):
        """测试占验情况服务性能"""
        # 批量标注
        start_time = time.time()

        for i in range(100):
            yanqing_service.annotate(i + 1, "应验" if i % 2 == 0 else "不验", f"性能测试{i+1}")

        elapsed = time.time() - start_time

        # 100次标注应该在5秒内完成
        assert elapsed < 5, f"占验情况标注耗时 {elapsed:.2f}s 超过5秒"

        # 测试统计性能
        start_time = time.time()
        stats = yanqing_service.get_statistics()
        elapsed = time.time() - start_time

        assert elapsed < 1, f"统计耗时 {elapsed:.2f}s 超过1秒"
        assert stats['total'] == 100

    def test_time_converter_performance(self):
        """测试时间转换性能"""
        start_time = time.time()

        for month in range(1, 13):
            for day in range(1, 29):
                solar_to_ganzhi_full(2024, month, day)

        elapsed = time.time() - start_time

        # 12*28=336次转换应该在5秒内完成
        assert elapsed < 5, f"时间转换耗时 {elapsed:.2f}s 超过5秒"


# ==================== 数据完整性测试 ====================

class TestDataIntegrity:
    """数据完整性测试"""

    def test_guali_code_uniqueness(self, guali_repo, yao_repo, db_session):
        """测试卦例代码唯一性"""
        # 创建相同数据的两个卦例应该都能成功（允许重复）
        guali1 = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024, solar_month=1, solar_day=1,
            ben_gua_name="乾为天", zhan_wen="测试1"
        )
        guali2 = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024, solar_month=1, solar_day=1,
            ben_gua_name="乾为天", zhan_wen="测试2"
        )

        assert guali1.id != guali2.id
        assert guali1.ben_gua_code == guali2.ben_gua_code

    def test_yao_position_integrity(self, guali_repo, yao_repo, db_session):
        """测试爻位完整性"""
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024, solar_month=1, solar_day=1,
            ben_gua_name="乾为天"
        )

        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)
        positions = [y.position for y in yao_details]

        # 验证爻位从1到6完整
        assert sorted(positions) == [1, 2, 3, 4, 5, 6]

    def test_shiying_integrity(self, guali_repo, yao_repo, db_session):
        """测试世应完整性"""
        # 测试不同宫位的卦
        test_guas = [
            ("乾为天", "本宫"),
            ("天风姤", "一世"),
            ("天山遁", "二世"),
            ("天地否", "三世"),
            ("风地观", "四世"),
            ("山地剥", "五世"),
            ("火地晋", "游魂"),
            ("火天大有", "归魂"),
        ]

        for gua_name, expected_gongwei in test_guas:
            guali = create_and_save_guali(
                guali_repo, yao_repo, db_session,
                solar_year=2024, solar_month=1, solar_day=1,
                ben_gua_name=gua_name
            )
            yao_details = yao_repo.get_yao_details(guali.id, session=db_session)

            # 验证有且只有一个世爻和一个应爻
            world_count = sum(1 for y in yao_details if y.is_world)
            response_count = sum(1 for y in yao_details if y.is_response)

            assert world_count == 1, f"{gua_name} 世爻数量不正确: {world_count}"
            assert response_count == 1, f"{gua_name} 应爻数量不正确: {response_count}"

    def test_yanqing_status_validation(self, yanqing_service):
        """测试占验状态验证"""
        # 有效状态
        for status in ["应验", "模糊", "不验"]:
            result = yanqing_service.annotate(1, status, "")
            assert result['status'] == status

        # 无效状态应该抛出异常
        with pytest.raises(ValueError):
            yanqing_service.annotate(1, "无效状态", "")


# ==================== 回归测试 ====================

class TestRegression:
    """回归测试 - 确保之前修复的bug不再出现"""

    def test_gua_code_calculation(self):
        """回归测试：确保卦代码计算正确（Bug 14）"""
        # 测试之前有问题的卦
        test_cases = [
            ("火泽睽", 0b110101),  # 内卦兑，外卦离
            ("风山渐", 0b001011),  # 内卦艮，外卦巽
            ("地风升", 0b011000),  # 内卦巽，外卦坤
            ("水风井", 0b011010),  # 内卦巽，外卦坎
        ]

        for gua_name, expected_code in test_cases:
            gua = ZhongGua.from_name(gua_name)
            assert gua.code == expected_code, f"{gua_name} 代码应为 {bin(expected_code)}，实际为 {bin(gua.code)}"

    def test_liuqin_calculation_rules(self, guali_repo, yao_repo, db_session):
        """回归测试：确保六亲计算规则正确"""
        # 坤为地（坤宫，土）
        guali = create_and_save_guali(
            guali_repo, yao_repo, db_session,
            solar_year=2024, solar_month=1, solar_day=1,
            ben_gua_name="坤为地"
        )

        yao_details = yao_repo.get_yao_details(guali.id, session=db_session)

        # 坤为地：内卦未巳卯，外卦丑亥酉
        # 卦宫五行=土
        # 未（土）→ 兄弟
        # 巳（火）→ 父母（火生土）
        # 卯（木）→ 官鬼（木克土）
        assert yao_details[0].liuqin == "兄弟"  # 未
        assert yao_details[1].liuqin == "父母"  # 巳
        assert yao_details[2].liuqin == "官鬼"  # 卯
