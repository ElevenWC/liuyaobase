# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 阶段十二：Guali类整合计算测试

本测试文件验证Guali类的calculate_all方法和完整卦例计算的正确性。
"""
import pytest
from datetime import date

from backend.core.enums import (
    Wuxing, Tiangan, Dizhi, DanGua, ZhongGua, LiuQin, LiuShen, ShenSha
)
from backend.core.models import Guali, Yao, create_guali_from_input


# =============================================================================
# 任务 12.1 - Guali类calculate_all方法框架测试
# =============================================================================

class TestGualiCalculateAllFramework:
    """测试Guali类的calculate_all方法框架"""

    def test_calculate_all_exists(self):
        """测试calculate_all方法存在"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        assert hasattr(guali, 'calculate_all')
        assert callable(guali.calculate_all)

    def test_calculate_all_sets_nama(self):
        """测试calculate_all设置纳甲"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()
        # 验证所有爻都有地支
        assert all(yao.dizhi is not None for yao in guali.yaos)

    def test_calculate_all_sets_shiying(self):
        """测试calculate_all设置世应"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()
        # 验证有世爻和应爻
        assert guali.world_yao is not None
        assert guali.response_yao is not None

    def test_calculate_all_sets_liuqin(self):
        """测试calculate_all设置六亲"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()
        # 验证所有爻都有六亲
        assert all(yao.liuqin is not None for yao in guali.yaos)

    def test_calculate_all_sets_liushen(self):
        """测试calculate_all设置六神（需要日干）"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN, ganzhi_day="甲午")
        guali.calculate_all()
        # 验证所有爻都有六神
        assert all(yao.liushen is not None for yao in guali.yaos)

    def test_calculate_all_without_ganzhi(self):
        """测试无干支时的calculate_all"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()
        # 纳甲、世应、六亲应该正常
        assert all(yao.dizhi is not None for yao in guali.yaos)
        assert guali.world_yao is not None
        assert all(yao.liuqin is not None for yao in guali.yaos)
        # 六神应为None（无日干）
        assert all(yao.liushen is None for yao in guali.yaos)


# =============================================================================
# 任务 12.2 - 完整卦例计算测试
# =============================================================================

class TestCompleteGualiCalculation:
    """测试完整卦例的所有计算"""

    def test_complete_qian_wei_tian(self):
        """测试乾为天的完整计算"""
        # 创建卦例
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhi_gua_name=None,
            zhan_wen="测试占问",
            zhan_duan="测试占断"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        # 验证时间转换
        assert guali.ganzhi_year is not None
        assert guali.ganzhi_month is not None
        assert guali.ganzhi_day is not None
        assert guali.xunkong is not None

        # 验证纳甲装卦（乾卦：子寅辰午申戌）
        assert guali.yaos[0].dizhi == Dizhi.ZI
        assert guali.yaos[1].dizhi == Dizhi.YIN
        assert guali.yaos[2].dizhi == Dizhi.CHEN
        assert guali.yaos[3].dizhi == Dizhi.WU
        assert guali.yaos[4].dizhi == Dizhi.SHEN
        assert guali.yaos[5].dizhi == Dizhi.XU

        # 验证六亲（乾宫属金）
        assert guali.yaos[0].liuqin == LiuQin.ZI_SUN   # 子水，金生水
        assert guali.yaos[1].liuqin == LiuQin.QI_CAI   # 寅木，金克木
        assert guali.yaos[2].liuqin == LiuQin.FU_MU    # 辰土，土生金
        assert guali.yaos[3].liuqin == LiuQin.GUAN_GUI # 午火，火克金
        assert guali.yaos[4].liuqin == LiuQin.XIONG_DI # 申金，金=金
        assert guali.yaos[5].liuqin == LiuQin.FU_MU    # 戌土，土生金

        # 验证六神
        tiangan = guali.day_tiangan
        assert tiangan is not None
        for i, yao in enumerate(guali.yaos):
            expected = LiuShen.get_by_tiangan_and_position(tiangan, i + 1)
            assert yao.liushen == expected

        # 验证世应（本宫卦：世在上爻，应在三爻）
        assert guali.yaos[5].is_world == True
        assert guali.yaos[2].is_response == True

        # 验证神煞
        assert 'ganlu' in guali.shensha
        assert 'yima' in guali.shensha
        assert 'yangren' in guali.shensha
        assert 'taohua' in guali.shensha

        # 验证伏神（乾为天是本宫卦，六亲齐全，无伏神）
        assert guali.fushen.get('has_fushen') == False

    def test_complete_shan_feng_gu(self):
        """测试山风蛊的完整计算"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋",
            zhan_wen="占问股票走势",
            zhan_duan="占断上涨"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        # 验证本卦信息
        assert guali.ben_gua == ZhongGua.SHAN_FENG_GU
        assert guali.zhi_gua == ZhongGua.HUO_DI_JIN
        assert guali.ben_gua.gongwei == "巽宫"
        assert guali.ben_gua.gongwei_index == "归魂"

        # 验证爻变代码
        # 山风蛊(011001) XOR 火地晋(000101) = 011100
        assert guali.yao_bian_code == 0b011100

        # 验证动爻
        moving_yaos = guali.moving_yaos
        assert len(moving_yaos) == 3  # 三爻、四爻、五爻动

        # 验证世应（归魂卦：世在三爻，应在上爻）
        assert guali.yaos[2].is_world == True
        assert guali.yaos[5].is_response == True

        # 验证六亲（巽宫属木）
        # 山风蛊：内卦巽，外卦艮
        # 巽卦（内卦）：丑亥酉 - 丑(土)、亥(水)、酉(金)
        # 艮卦（外卦）：戌子寅 - 戌(土)、子(水)、寅(木)
        # 巽宫木：
        # - 土受木克 -> 妻财
        # - 水生木 -> 父母
        # - 金克木 -> 官鬼
        # - 木 = 木 -> 兄弟
        assert guali.yaos[0].liuqin == LiuQin.QI_CAI    # 丑土，木克土
        assert guali.yaos[1].liuqin == LiuQin.FU_MU     # 亥水，水生木
        assert guali.yaos[2].liuqin == LiuQin.GUAN_GUI  # 酉金，金克木
        assert guali.yaos[3].liuqin == LiuQin.QI_CAI    # 戌土，木克土
        assert guali.yaos[4].liuqin == LiuQin.FU_MU     # 子水，水生木
        assert guali.yaos[5].liuqin == LiuQin.XIONG_DI  # 寅木，木=木

    def test_complete_kun_wei_di(self):
        """测试坤为地的完整计算"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=6,
            solar_day=15,
            ben_gua_name="坤为地"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        # 验证纳甲装卦（坤卦：未巳卯丑亥酉）
        assert guali.yaos[0].dizhi == Dizhi.WEI
        assert guali.yaos[1].dizhi == Dizhi.SI
        assert guali.yaos[2].dizhi == Dizhi.MAO
        assert guali.yaos[3].dizhi == Dizhi.CHOU
        assert guali.yaos[4].dizhi == Dizhi.HAI
        assert guali.yaos[5].dizhi == Dizhi.YOU

        # 验证六亲（坤宫属土）
        # - 土 = 土 -> 兄弟
        # - 火生土 -> 父母
        # - 木克土 -> 官鬼
        # - 土克水 -> 妻财
        # - 土生金 -> 子孙
        assert guali.yaos[0].liuqin == LiuQin.XIONG_DI   # 未土，土=土
        assert guali.yaos[1].liuqin == LiuQin.FU_MU      # 巳火，火生土
        assert guali.yaos[2].liuqin == LiuQin.GUAN_GUI   # 卯木，木克土
        assert guali.yaos[3].liuqin == LiuQin.XIONG_DI   # 丑土，土=土
        assert guali.yaos[4].liuqin == LiuQin.QI_CAI     # 亥水，土克水
        assert guali.yaos[5].liuqin == LiuQin.ZI_SUN     # 酉金，土生金

        # 验证世应（本宫卦）
        assert guali.yaos[5].is_world == True
        assert guali.yaos[2].is_response == True

    def test_complete_with_fushen(self):
        """测试有伏神的卦例计算"""
        # 天风姤（乾宫一世卦）- 缺妻财爻
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="天风姤"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        # 验证伏神存在
        assert guali.fushen.get('has_fushen') == True

        # 验证缺失的六亲（返回的是字符串列表）
        missing_liuqin = guali.fushen.get('missing_liuqin', [])
        assert LiuQin.QI_CAI.value in missing_liuqin  # 天风姤缺妻财


# =============================================================================
# 综合测试：全64卦验证
# =============================================================================

class TestAllZhongGua:
    """测试所有64卦的计算"""

    @pytest.mark.parametrize("gua", list(ZhongGua))
    def test_all_gua_nama(self, gua):
        """测试所有64卦的纳甲装卦"""
        guali = Guali(ben_gua=gua)
        guali.calculate_all()

        # 验证所有爻都有地支
        assert len(guali.yaos) == 6
        assert all(yao.dizhi is not None for yao in guali.yaos)

    @pytest.mark.parametrize("gua", list(ZhongGua))
    def test_all_gua_shiying(self, gua):
        """测试所有64卦的世应设置"""
        guali = Guali(ben_gua=gua)
        guali.calculate_all()

        # 验证世应存在
        assert guali.world_yao is not None
        assert guali.response_yao is not None
        assert guali.world_yao.position != guali.response_yao.position

    @pytest.mark.parametrize("gua", list(ZhongGua))
    def test_all_gua_liuqin(self, gua):
        """测试所有64卦的六亲计算"""
        guali = Guali(ben_gua=gua)
        guali.calculate_all()

        # 验证所有爻都有六亲
        assert all(yao.liuqin is not None for yao in guali.yaos)

        # 验证六亲类型正确
        liuqin_set = set(yao.liuqin for yao in guali.yaos)
        assert liuqin_set.issubset(set(LiuQin))


# =============================================================================
# 特殊卦例测试
# =============================================================================

class TestSpecialGua:
    """测试特殊卦例"""

    def test_liuchong_gua(self):
        """测试六冲卦"""
        # 乾为天是六冲卦
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()
        assert guali.ben_gua.is_liuchong == True

    def test_liuhe_gua(self):
        """测试六合卦"""
        # 天地否是六合卦
        guali = Guali(ben_gua=ZhongGua.TIAN_DI_FOU)
        guali.calculate_all()
        assert guali.ben_gua.is_liuhe == True

    def test_fanyin_gua(self):
        """测试反吟卦"""
        # 火天大有之火风鼎，内卦易冒反吟
        guali = Guali(
            ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
            zhi_gua=ZhongGua.HUO_FENG_DING
        )
        guali.calculate_all()

        # 验证有反吟
        assert guali.fanyin_fuyin.get('has_fanyin') == True

    def test_fuyin_gua(self):
        """测试伏吟卦"""
        # 乾为天之震为雷，内卦伏吟
        guali = Guali(
            ben_gua=ZhongGua.QIAN_WEI_TIAN,
            zhi_gua=ZhongGua.ZHEN_WEI_LEI
        )
        guali.calculate_all()

        # 验证有伏吟
        assert guali.fanyin_fuyin.get('has_fuyin') == True


# =============================================================================
# 工厂函数测试
# =============================================================================

class TestCreateGualiFromInput:
    """测试create_guali_from_input工厂函数"""

    def test_create_with_full_info(self):
        """测试完整信息创建"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhi_gua_name="坤为地",
            zhan_wen="测试占问",
            zhan_duan="测试占断"
        )

        assert guali.solar_year == 2024
        assert guali.solar_month == 2
        assert guali.solar_day == 12
        assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
        assert guali.zhi_gua == ZhongGua.KUN_WEI_DI
        assert guali.zhan_wen == "测试占问"
        assert guali.zhan_duan == "测试占断"

        # 验证爻变代码
        assert guali.yao_bian_code == 0b111111  # 6爻全动

    def test_create_without_zhi_gua(self):
        """测试无之卦创建"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天"
        )

        assert guali.zhi_gua is None
        assert guali.yao_bian_code == 0

    def test_create_invalid_bengua(self):
        """测试无效本卦名"""
        with pytest.raises(ValueError):
            create_guali_from_input(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ben_gua_name="不存在的卦"
            )

    def test_create_invalid_zhigua(self):
        """测试无效之卦名"""
        with pytest.raises(ValueError):
            create_guali_from_input(
                solar_year=2024,
                solar_month=2,
                solar_day=12,
                ben_gua_name="乾为天",
                zhi_gua_name="不存在的卦"
            )


# =============================================================================
# 显示方法测试
# =============================================================================

class TestGualiDisplay:
    """测试Guali的显示方法"""

    def test_display_basic(self):
        """测试基本显示"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="乾为天",
            zhan_wen="测试占问"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        display_str = guali.display()
        assert display_str is not None
        assert "乾为天" in display_str

    def test_display_with_zhi_gua(self):
        """测试有之卦的显示"""
        guali = create_guali_from_input(
            solar_year=2024,
            solar_month=2,
            solar_day=12,
            ben_gua_name="山风蛊",
            zhi_gua_name="火地晋"
        )
        guali.fill_ganzhi_time()
        guali.calculate_all()

        display_str = guali.display()
        assert "山风蛊" in display_str
        assert "火地晋" in display_str

    def test_repr(self):
        """测试__repr__方法"""
        guali = Guali(id=1, ben_gua=ZhongGua.QIAN_WEI_TIAN)
        repr_str = repr(guali)
        assert "Guali" in repr_str


# =============================================================================
# 边界条件测试
# =============================================================================

class TestBoundaryConditions:
    """测试边界条件"""

    def test_empty_bengua(self):
        """测试空本卦"""
        guali = Guali()
        guali.calculate_all()  # 不应该报错
        assert len(guali.yaos) == 0

    def test_no_dizhi_for_liushen(self):
        """测试无地支时六亲为None"""
        yao = Yao(position=1, yao_type=1)
        assert yao.liuqin is None

    def test_guali_without_tiangan(self):
        """测试无日干时的计算"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()

        # 纳甲、世应、六亲正常
        assert all(yao.dizhi is not None for yao in guali.yaos)
        # 六神为None
        assert all(yao.liushen is None for yao in guali.yaos)
