# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 数据仓库测试

测试GualiRepository、YaoDetailRepository和YanqingRepository的CRUD操作
"""
import pytest
from datetime import datetime

from backend.db.connection import get_session, Base, sync_engine
from backend.db.models import GualiModel, YaoDetailModel, YanqingModel
from backend.db.repositories import (
    GualiRepository,
    YaoDetailRepository,
    YanqingRepository,
    guali_repository,
    yao_detail_repository,
    yanqing_repository
)
from backend.core.models import Guali, Yao, create_guali_from_input
from backend.core.enums import ZhongGua, Dizhi, LiuQin, LiuShen


# =============================================================================
# 测试固件
# =============================================================================

@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话

    每个测试函数使用独立的会话，测试结束后回滚
    """
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
                session.query(YanqingModel).delete()
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
def yanqing_repo():
    """获取占验情况仓库实例"""
    return YanqingRepository()


@pytest.fixture
def sample_guali_data():
    """获取示例卦例数据"""
    return {
        "solar_year": 2024,
        "solar_month": 2,
        "solar_day": 12,
        "ganzhi_year": "甲辰",
        "ganzhi_month": "丙寅",
        "ganzhi_day": "甲午",
        "xunkong": "辰巳",
        "ben_gua_code": 0b111111,  # 乾为天 (二进制111111 = 十进制63)
        "zhi_gua_code": None,
        "yao_bian_code": 0,
        "gongwei": "乾宫",
        "gongwei_index": "本宫",
        "zhan_wen": "测试占问事由",
        "zhan_duan": "测试占断"
    }


@pytest.fixture
def sample_guali_biz():
    """创建示例业务对象Guali"""
    guali = create_guali_from_input(
        solar_year=2024,
        solar_month=2,
        solar_day=12,
        ben_gua_name="乾为天",
        zhi_gua_name=None,
        zhan_wen="业务对象测试",
        zhan_duan="占断内容"
    )
    guali.fill_ganzhi_time()
    guali.calculate_all()
    return guali


# =============================================================================
# 测试 GualiRepository - 创建操作
# =============================================================================

class TestGualiRepositoryCreate:
    """测试卦例仓库的创建操作"""

    def test_create_guali_basic(self, guali_repo, sample_guali_data, db_session):
        """测试基本的卦例创建"""
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)

        assert guali is not None
        assert guali.id is not None
        assert guali.id > 0
        assert guali.solar_year == 2024
        assert guali.solar_month == 2
        assert guali.solar_day == 12
        assert guali.ganzhi_year == "甲辰"
        assert guali.ganzhi_month == "丙寅"
        assert guali.ganzhi_day == "甲午"
        assert guali.xunkong == "辰巳"
        assert guali.ben_gua_code == 0b111111  # 63
        assert guali.gongwei == "乾宫"
        assert guali.gongwei_index == "本宫"
        assert guali.zhan_wen == "测试占问事由"
        assert guali.zhan_duan == "测试占断"

    def test_create_guali_without_session(self, guali_repo, sample_guali_data):
        """测试不提供session的卦例创建（自动创建会话）"""
        guali = guali_repo.create_guali(**sample_guali_data)

        assert guali is not None
        assert guali.id is not None
        assert guali.id > 0

        # 验证可以查询到
        found = guali_repo.get_guali_by_id(guali.id)
        assert found is not None
        assert found.id == guali.id

        # 清理
        guali_repo.delete_guali(guali.id)

    def test_create_from_guali_biz_object(self, guali_repo, sample_guali_biz, db_session):
        """测试从业务对象创建卦例"""
        guali_model = guali_repo.create_from_guali(sample_guali_biz, session=db_session)

        assert guali_model is not None
        assert guali_model.id is not None
        assert guali_model.solar_year == 2024
        assert guali_model.ben_gua_code == 0b111111  # 63
        assert guali_model.gongwei == "乾宫"
        assert guali_model.gongwei_index == "本宫"


# =============================================================================
# 测试 GualiRepository - 查询操作
# =============================================================================

class TestGualiRepositoryQuery:
    """测试卦例仓库的查询操作"""

    def test_get_guali_by_id_exists(self, guali_repo, sample_guali_data, db_session):
        """测试根据ID查询存在的卦例"""
        # 先创建
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 再查询
        found = guali_repo.get_guali_by_id(created.id, session=db_session)

        assert found is not None
        assert found.id == created.id
        assert found.solar_year == sample_guali_data["solar_year"]

    def test_get_guali_by_id_not_exists(self, guali_repo, db_session):
        """测试根据ID查询不存在的卦例"""
        found = guali_repo.get_guali_by_id(99999, session=db_session)
        assert found is None

    def test_get_all_gualis(self, guali_repo, sample_guali_data, db_session):
        """测试获取所有卦例（分页）"""
        # 创建多个卦例
        for i in range(5):
            data = sample_guali_data.copy()
            data["solar_year"] = 2020 + i
            guali_repo.create_guali(**data, session=db_session)

        # 查询第一页
        gualis, total = guali_repo.get_all_gualis(page=1, page_size=3, session=db_session)

        assert total == 5
        assert len(gualis) == 3

        # 查询第二页
        gualis2, _ = guali_repo.get_all_gualis(page=2, page_size=3, session=db_session)
        assert len(gualis2) == 2

    def test_get_gualis_by_year(self, guali_repo, sample_guali_data, db_session):
        """测试根据年份获取卦例"""
        # 创建不同年份的卦例
        for year in [2022, 2023, 2024]:
            data = sample_guali_data.copy()
            data["solar_year"] = year
            guali_repo.create_guali(**data, session=db_session)

        # 查询2024年的卦例
        gualis, total = guali_repo.get_gualis_by_year(2024, session=db_session)

        assert total == 1
        assert gualis[0].solar_year == 2024

    def test_get_gualis_by_gongwei(self, guali_repo, sample_guali_data, db_session):
        """测试根据卦宫获取卦例"""
        # 创建不同卦宫的卦例
        data1 = sample_guali_data.copy()
        data1["gongwei"] = "乾宫"
        data1["ben_gua_code"] = 0b111111  # 63
        guali_repo.create_guali(**data1, session=db_session)

        data2 = sample_guali_data.copy()
        data2["gongwei"] = "坎宫"
        data2["ben_gua_code"] = 101010
        guali_repo.create_guali(**data2, session=db_session)

        # 查询乾宫的卦例
        gualis, total = guali_repo.get_gualis_by_gongwei("乾宫", session=db_session)

        assert total == 1
        assert gualis[0].gongwei == "乾宫"

    def test_search_gualis_by_ben_gua_name(self, guali_repo, sample_guali_data, db_session):
        """测试根据本卦名搜索卦例"""
        # 创建卦例
        guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 搜索乾为天
        gualis, total = guali_repo.search_gualis(
            ben_gua_name="乾为天",
            session=db_session
        )

        assert total >= 1
        assert any(g.ben_gua_code == 0b111111 for g in gualis)  # 63

    def test_search_gualis_by_keyword(self, guali_repo, sample_guali_data, db_session):
        """测试根据关键词搜索卦例"""
        data = sample_guali_data.copy()
        data["zhan_wen"] = "股票走势如何"
        guali_repo.create_guali(**data, session=db_session)

        # 搜索"股票"关键词
        gualis, total = guali_repo.search_gualis(
            zhan_wen_keyword="股票",
            session=db_session
        )

        assert total >= 1
        assert any("股票" in g.zhan_wen for g in gualis)


# =============================================================================
# 测试 GualiRepository - 更新操作
# =============================================================================

class TestGualiRepositoryUpdate:
    """测试卦例仓库的更新操作"""

    def test_update_zhan_wen(self, guali_repo, sample_guali_data, db_session):
        """测试更新占问事由"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 更新占问事由
        updated = guali_repo.update_guali(
            created.id,
            zhan_wen="更新后的占问事由",
            session=db_session
        )

        assert updated is not None
        assert updated.zhan_wen == "更新后的占问事由"
        assert updated.zhan_duan == sample_guali_data["zhan_duan"]  # 其他字段不变

    def test_update_zhan_duan(self, guali_repo, sample_guali_data, db_session):
        """测试更新占断"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 更新占断
        updated = guali_repo.update_guali(
            created.id,
            zhan_duan="更新后的占断",
            session=db_session
        )

        assert updated is not None
        assert updated.zhan_duan == "更新后的占断"

    def test_update_both(self, guali_repo, sample_guali_data, db_session):
        """测试同时更新占问和占断"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 同时更新
        updated = guali_repo.update_guali(
            created.id,
            zhan_wen="新占问",
            zhan_duan="新占断",
            session=db_session
        )

        assert updated is not None
        assert updated.zhan_wen == "新占问"
        assert updated.zhan_duan == "新占断"

    def test_update_not_exists(self, guali_repo, db_session):
        """测试更新不存在的卦例"""
        updated = guali_repo.update_guali(99999, zhan_wen="测试", session=db_session)
        assert updated is None


# =============================================================================
# 测试 GualiRepository - 删除操作
# =============================================================================

class TestGualiRepositoryDelete:
    """测试卦例仓库的删除操作"""

    def test_delete_exists(self, guali_repo, sample_guali_data, db_session):
        """测试删除存在的卦例"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)
        guali_id = created.id
        db_session.flush()  # 确保创建已提交

        # 删除
        result = guali_repo.delete_guali(guali_id, session=db_session)
        assert result is True
        db_session.flush()  # 确保删除已提交

        # 验证已删除 - 需要清除session缓存
        db_session.expire_all()
        found = guali_repo.get_guali_by_id(guali_id, session=db_session)
        assert found is None

    def test_delete_not_exists(self, guali_repo, db_session):
        """测试删除不存在的卦例"""
        result = guali_repo.delete_guali(99999, session=db_session)
        assert result is False


# =============================================================================
# 测试 GualiRepository - 转换方法
# =============================================================================

class TestGualiRepositoryConvert:
    """测试卦例仓库的转换方法"""

    def test_model_to_guali(self, guali_repo, sample_guali_data, db_session):
        """测试将模型转换为业务对象"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 转换
        guali_biz = guali_repo.model_to_guali(created, with_yao_details=False)

        assert guali_biz is not None
        assert guali_biz.id == created.id
        assert guali_biz.solar_year == 2024
        assert guali_biz.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali_biz.gongwei == "乾宫"
        assert guali_biz.gongwei_index == "本宫"

    def test_model_to_guali_with_yao_details(self, guali_repo, sample_guali_data, db_session):
        """测试将模型转换为业务对象（包含爻详情）"""
        # 创建卦例
        created = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 添加爻详情
        yao_repo = YaoDetailRepository()
        yaos = [
            Yao(position=1, yao_type=1, state=0, dizhi=Dizhi.ZI, is_world=False, is_response=False),
            Yao(position=2, yao_type=1, state=0, dizhi=Dizhi.YIN, is_world=False, is_response=False),
            Yao(position=3, yao_type=1, state=0, dizhi=Dizhi.CHEN, is_world=False, is_response=True),
            Yao(position=4, yao_type=1, state=0, dizhi=Dizhi.WU, is_world=False, is_response=False),
            Yao(position=5, yao_type=1, state=0, dizhi=Dizhi.SHEN, is_world=False, is_response=False),
            Yao(position=6, yao_type=1, state=0, dizhi=Dizhi.XU, is_world=True, is_response=False),
        ]
        yao_repo.save_yao_details(created.id, yaos, session=db_session)

        # 重新查询
        found = guali_repo.get_guali_by_id(created.id, session=db_session)
        guali_biz = guali_repo.model_to_guali(found, with_yao_details=True)

        assert guali_biz is not None
        assert len(guali_biz.yaos) == 6
        assert guali_biz.yaos[0].dizhi == Dizhi.ZI
        assert guali_biz.yaos[5].is_world is True
        assert guali_biz.yaos[2].is_response is True


# =============================================================================
# 测试 YaoDetailRepository
# =============================================================================

class TestYaoDetailRepository:
    """测试爻详情仓库"""

    def test_save_yao_details(self, yao_repo, guali_repo, sample_guali_data, db_session):
        """测试批量保存爻详情"""
        # 先创建卦例
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 创建爻
        yaos = [
            Yao(position=1, yao_type=1, state=0, dizhi=Dizhi.ZI),
            Yao(position=2, yao_type=1, state=0, dizhi=Dizhi.YIN),
            Yao(position=3, yao_type=1, state=0, dizhi=Dizhi.CHEN),
            Yao(position=4, yao_type=1, state=0, dizhi=Dizhi.WU),
            Yao(position=5, yao_type=1, state=0, dizhi=Dizhi.SHEN),
            Yao(position=6, yao_type=1, state=0, dizhi=Dizhi.XU),
        ]

        # 保存
        yao_models = yao_repo.save_yao_details(guali.id, yaos, session=db_session)

        assert len(yao_models) == 6
        assert all(ym.guali_id == guali.id for ym in yao_models)

    def test_get_yao_details(self, yao_repo, guali_repo, sample_guali_data, db_session):
        """测试获取爻详情列表"""
        # 创建卦例和爻详情
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yaos = [Yao(position=i, yao_type=1, state=0, dizhi=Dizhi.ZI) for i in range(1, 7)]
        yao_repo.save_yao_details(guali.id, yaos, session=db_session)

        # 获取
        yao_models = yao_repo.get_yao_details(guali.id, session=db_session)

        assert len(yao_models) == 6
        # 验证按位置排序
        positions = [ym.position for ym in yao_models]
        assert positions == [1, 2, 3, 4, 5, 6]

    def test_get_yao_detail_by_position(self, yao_repo, guali_repo, sample_guali_data, db_session):
        """测试获取指定位置的爻详情"""
        # 创建卦例和爻详情
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yaos = [
            Yao(position=i, yao_type=1, state=0, dizhi=Dizhi.ZI, is_world=(i == 6))
            for i in range(1, 7)
        ]
        yao_repo.save_yao_details(guali.id, yaos, session=db_session)

        # 获取第6爻（世爻）
        yao_model = yao_repo.get_yao_detail_by_position(guali.id, 6, session=db_session)

        assert yao_model is not None
        assert yao_model.position == 6
        assert yao_model.is_world is True


# =============================================================================
# 测试 YanqingRepository
# =============================================================================

class TestYanqingRepository:
    """测试占验情况仓库"""

    def test_annotate_create(self, yanqing_repo, guali_repo, sample_guali_data, db_session):
        """测试创建占验情况标注"""
        # 创建卦例
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)

        # 标注
        yanqing = yanqing_repo.annotate(
            guali_id=guali.id,
            status="应验",
            note="实际走势一致",
            session=db_session
        )

        assert yanqing is not None
        assert yanqing.guali_id == guali.id
        assert yanqing.status == "应验"
        assert yanqing.note == "实际走势一致"

    def test_annotate_update(self, yanqing_repo, guali_repo, sample_guali_data, db_session):
        """测试更新占验情况标注"""
        # 创建卦例和标注
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yanqing_repo.annotate(guali.id, "模糊", "待验证", session=db_session)

        # 更新
        yanqing = yanqing_repo.annotate(
            guali_id=guali.id,
            status="应验",
            note="已验证",
            session=db_session
        )

        assert yanqing.status == "应验"
        assert yanqing.note == "已验证"

    def test_get_by_guali_id(self, yanqing_repo, guali_repo, sample_guali_data, db_session):
        """测试根据卦例ID获取占验情况"""
        # 创建卦例和标注
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yanqing_repo.annotate(guali.id, "应验", "测试", session=db_session)

        # 获取
        yanqing = yanqing_repo.get_by_guali_id(guali.id, session=db_session)

        assert yanqing is not None
        assert yanqing.guali_id == guali.id

    def test_get_by_guali_id_not_exists(self, yanqing_repo, db_session):
        """测试获取不存在的占验情况"""
        yanqing = yanqing_repo.get_by_guali_id(99999, session=db_session)
        assert yanqing is None

    def test_delete_by_guali_id(self, yanqing_repo, guali_repo, sample_guali_data, db_session):
        """测试删除占验情况"""
        # 创建卦例和标注
        guali = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yanqing_repo.annotate(guali.id, "应验", "测试", session=db_session)
        db_session.flush()  # 确保已提交

        # 删除
        result = yanqing_repo.delete_by_guali_id(guali.id, session=db_session)
        assert result is True
        db_session.flush()  # 确保删除已提交

        # 验证已删除
        db_session.expire_all()
        yanqing = yanqing_repo.get_by_guali_id(guali.id, session=db_session)
        assert yanqing is None

    def test_get_all_by_status(self, yanqing_repo, guali_repo, sample_guali_data, db_session):
        """测试根据状态获取占验情况列表"""
        # 创建多个卦例和标注
        for i in range(3):
            data = sample_guali_data.copy()
            data["solar_day"] = i + 1
            guali = guali_repo.create_guali(**data, session=db_session)
            status = "应验" if i < 2 else "不验"
            yanqing_repo.annotate(guali.id, status, f"测试{i}", session=db_session)

        # 查询应验的
        yanqings, total = yanqing_repo.get_all_by_status("应验", session=db_session)

        assert total == 2
        assert all(y.status == "应验" for y in yanqings)


# =============================================================================
# 集成测试
# =============================================================================

class TestIntegration:
    """集成测试"""

    def test_create_guali_with_yao_details_and_yanqing(
        self,
        guali_repo,
        yao_repo,
        yanqing_repo,
        sample_guali_biz,
        db_session
    ):
        """测试完整流程：创建卦例 -> 保存爻详情 -> 标注占验情况"""
        # 1. 从业务对象创建卦例
        guali_model = guali_repo.create_from_guali(sample_guali_biz, session=db_session)
        assert guali_model.id is not None

        # 2. 保存爻详情
        yao_repo.save_yao_details(guali_model.id, sample_guali_biz.yaos, session=db_session)

        # 3. 标注占验情况
        yanqing = yanqing_repo.annotate(
            guali_id=guali_model.id,
            status="应验",
            note="集成测试验证",
            session=db_session
        )

        # 4. 验证完整数据
        found_guali = guali_repo.get_guali_by_id(guali_model.id, session=db_session)
        assert found_guali is not None

        yao_details = yao_repo.get_yao_details(guali_model.id, session=db_session)
        assert len(yao_details) == 6

        found_yanqing = yanqing_repo.get_by_guali_id(guali_model.id, session=db_session)
        assert found_yanqing is not None
        assert found_yanqing.status == "应验"

    def test_delete_guali_cascades_yao_details(
        self,
        guali_repo,
        yao_repo,
        sample_guali_data,
        db_session
    ):
        """测试删除卦例时级联删除爻详情"""
        # 创建卦例和爻详情
        guali_model = guali_repo.create_guali(**sample_guali_data, session=db_session)
        yaos = [Yao(position=i, yao_type=1, state=0, dizhi=Dizhi.ZI) for i in range(1, 7)]
        yao_repo.save_yao_details(guali_model.id, yaos, session=db_session)
        db_session.flush()  # 确保已提交

        # 验证爻详情存在
        yao_details = yao_repo.get_yao_details(guali_model.id, session=db_session)
        assert len(yao_details) == 6

        # 删除卦例
        guali_repo.delete_guali(guali_model.id, session=db_session)
        db_session.flush()  # 确保删除已提交

        # 验证爻详情也被删除
        db_session.expire_all()
        yao_details = yao_repo.get_yao_details(guali_model.id, session=db_session)
        assert len(yao_details) == 0
