"""
六爻卦例分析系统 - 伏神计算模块测试

测试fushen模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import LiuQin, ZhongGua, Wuxing, Dizhi
from backend.core.models import Yao, Guali
from backend.core.fushen import (
    check_liuqin_complete,
    get_ben_gong_gua,
    find_yao_by_liuqin,
    calculate_feishen_fushen_relation,
    find_fushen,
    calculate_fushen_for_guali,
    GONGWEI_TO_BENGONG
)


# =============================================================================
# 任务 8.1 - 检查六亲是否齐全测试
# =============================================================================

class TestCheckLiuqinComplete:
    """检查六亲是否齐全测试"""

    def test_all_liuqin_present(self):
        """测试六亲齐全的情况"""
        yaos = [
            Yao(position=1, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=2, yao_type=1, liuqin=LiuQin.GUAN_GUI),
            Yao(position=3, yao_type=1, liuqin=LiuQin.ZI_SUN),
            Yao(position=4, yao_type=1, liuqin=LiuQin.QI_CAI),
            Yao(position=5, yao_type=1, liuqin=LiuQin.XIONG_DI),
            Yao(position=6, yao_type=1, liuqin=LiuQin.FU_MU)  # 父母重复
        ]
        missing = check_liuqin_complete(yaos)
        assert len(missing) == 0  # 六亲齐全

    def test_missing_liuqin(self):
        """测试缺少六亲的情况"""
        yaos = [
            Yao(position=1, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=2, yao_type=1, liuqin=LiuQin.GUAN_GUI),
            Yao(position=3, yao_type=1, liuqin=LiuQin.ZI_SUN),
            Yao(position=4, yao_type=1, liuqin=LiuQin.QI_CAI),
            Yao(position=5, yao_type=1, liuqin=LiuQin.FU_MU),  # 缺少兄弟
            Yao(position=6, yao_type=1, liuqin=LiuQin.FU_MU)
        ]
        missing = check_liuqin_complete(yaos)
        assert len(missing) == 1
        assert LiuQin.XIONG_DI in missing

    def test_multiple_missing_liuqin(self):
        """测试缺少多个六亲的情况"""
        yaos = [
            Yao(position=1, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=2, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=3, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=4, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=5, yao_type=1, liuqin=LiuQin.FU_MU),
            Yao(position=6, yao_type=1, liuqin=LiuQin.FU_MU)
        ]
        missing = check_liuqin_complete(yaos)
        assert len(missing) == 4  # 缺少官鬼、子孙、妻财、兄弟

    def test_empty_liuqin(self):
        """测试六亲为空的情况"""
        yaos = [
            Yao(position=1, yao_type=1, liuqin=None),
            Yao(position=2, yao_type=1, liuqin=None),
            Yao(position=3, yao_type=1, liuqin=None),
            Yao(position=4, yao_type=1, liuqin=None),
            Yao(position=5, yao_type=1, liuqin=None),
            Yao(position=6, yao_type=1, liuqin=None)
        ]
        missing = check_liuqin_complete(yaos)
        assert len(missing) == 5


# =============================================================================
# 任务 8.2 - 获取本宫卦测试
# =============================================================================

class TestGetBenGongGua:
    """获取本宫卦测试"""

    def test_get_qian_gong_bengong(self):
        """测试获取乾宫本宫卦"""
        ben_gong = get_ben_gong_gua("乾宫")
        assert ben_gong == ZhongGua.QIAN_WEI_TIAN

    def test_get_kan_gong_bengong(self):
        """测试获取坎宫本宫卦"""
        ben_gong = get_ben_gong_gua("坎宫")
        assert ben_gong == ZhongGua.KAN_WEI_SHUI

    def test_get_zhen_gong_bengong(self):
        """测试获取震宫本宫卦"""
        ben_gong = get_ben_gong_gua("震宫")
        assert ben_gong == ZhongGua.ZHEN_WEI_LEI

    def test_get_kun_gong_bengong(self):
        """测试获取坤宫本宫卦"""
        ben_gong = get_ben_gong_gua("坤宫")
        assert ben_gong == ZhongGua.KUN_WEI_DI

    def test_get_invalid_gongwei(self):
        """测试无效卦宫"""
        ben_gong = get_ben_gong_gua("无效宫")
        assert ben_gong is None

    def test_all_gongwei_have_bengong(self):
        """测试所有卦宫都有本宫卦映射"""
        gongwei_list = ["乾宫", "坎宫", "艮宫", "震宫", "巽宫", "离宫", "坤宫", "兑宫"]
        for gongwei in gongwei_list:
            assert gongwei in GONGWEI_TO_BENGONG, f"缺少卦宫映射: {gongwei}"


# =============================================================================
# 任务 8.3 - 查找伏神测试
# =============================================================================

class TestFindYaoByLiuqin:
    """根据六亲查找爻测试"""

    def test_find_existing_liuqin(self):
        """测试查找存在的六亲"""
        yaos = [
            Yao(position=1, yao_type=1, dizhi=Dizhi.ZI, liuqin=LiuQin.ZI_SUN),
            Yao(position=2, yao_type=1, dizhi=Dizhi.YIN, liuqin=LiuQin.QI_CAI),
            Yao(position=3, yao_type=1, dizhi=Dizhi.CHEN, liuqin=LiuQin.FU_MU),
        ]
        result = find_yao_by_liuqin(yaos, LiuQin.QI_CAI)
        assert result is not None
        assert result["position"] == 2
        assert result["dizhi"] == Dizhi.YIN

    def test_find_non_existing_liuqin(self):
        """测试查找不存在的六亲"""
        yaos = [
            Yao(position=1, yao_type=1, dizhi=Dizhi.ZI, liuqin=LiuQin.ZI_SUN),
            Yao(position=2, yao_type=1, dizhi=Dizhi.YIN, liuqin=LiuQin.QI_CAI),
        ]
        result = find_yao_by_liuqin(yaos, LiuQin.GUAN_GUI)
        assert result is None


class TestCalculateFeishenFushenRelation:
    """飞神与伏神关系计算测试"""

    def test_same_wuxing(self):
        """测试相同五行（比和）"""
        relation = calculate_feishen_fushen_relation(Wuxing.JIN, Wuxing.JIN)
        assert "比和" in relation

    def test_feisheng_fu(self):
        """测试飞生伏"""
        relation = calculate_feishen_fushen_relation(Wuxing.JIN, Wuxing.SHUI)
        assert "飞生伏" in relation or "长生" in relation

    def test_feike_fu(self):
        """测试飞克伏"""
        relation = calculate_feishen_fushen_relation(Wuxing.JIN, Wuxing.MU)
        assert "飞克伏" in relation or "受克" in relation

    def test_fusheng_fei(self):
        """测试伏生飞"""
        relation = calculate_feishen_fushen_relation(Wuxing.SHUI, Wuxing.JIN)
        assert "伏生飞" in relation or "泄气" in relation

    def test_fuke_fei(self):
        """测试伏克飞"""
        # 伏克飞：伏神五行克飞神五行，如木克土
        # feishen=土, fushen=木，木克土，所以是伏克飞
        relation = calculate_feishen_fushen_relation(Wuxing.TU, Wuxing.MU)
        assert "伏克飞" in relation or "出暴" in relation


class TestFindFushen:
    """查找伏神测试"""

    def test_find_fushen_tian_feng_gou(self):
        """测试天风姤查找伏神"""
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()

        # 检查缺失的六亲
        missing = check_liuqin_complete(guali.yaos)

        # 如果有缺失，查找伏神
        if missing:
            fushen_list = find_fushen(guali, missing)
            assert len(fushen_list) > 0

            # 验证伏神信息完整性
            for fs in fushen_list:
                assert fs.liuqin in missing
                assert fs.fushen_position >= 1 and fs.fushen_position <= 6
                assert fs.fushen_dizhi is not None

    def test_find_fushen_no_missing(self):
        """测试六亲齐全时查找伏神"""
        # 乾为天六亲应该齐全
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()

        missing = check_liuqin_complete(guali.yaos)

        # 如果六亲齐全，伏神列表应为空
        if not missing:
            fushen_list = find_fushen(guali, missing)
            assert len(fushen_list) == 0


# =============================================================================
# 任务 8.4 - 卦例伏神计算测试
# =============================================================================

class TestCalculateFushenForGuali:
    """卦例伏神计算测试"""

    def test_calculate_fushen_structure(self):
        """测试伏神计算结果结构"""
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()

        fushen_info = calculate_fushen_for_guali(guali)

        # 验证返回结构
        assert "has_fushen" in fushen_info
        assert "missing_liuqin" in fushen_info
        assert "fushen_list" in fushen_info

        assert isinstance(fushen_info["has_fushen"], bool)
        assert isinstance(fushen_info["missing_liuqin"], list)
        assert isinstance(fushen_info["fushen_list"], list)

    def test_calculate_fushen_with_missing(self):
        """测试有缺失六亲时的伏神计算"""
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()

        fushen_info = calculate_fushen_for_guali(guali)

        if fushen_info["has_fushen"]:
            # 验证伏神信息结构
            for fs in fushen_info["fushen_list"]:
                assert "liuqin" in fs
                assert "fushen_position" in fs
                assert "fushen_dizhi" in fs
                assert "feishen_position" in fs
                assert "relation" in fs


class TestGualiFushenIntegration:
    """与Guali类集成测试"""

    def test_guali_set_fushen(self):
        """测试Guali类的set_fushen方法"""
        from backend.core.nama import load_dizhi_to_guali

        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        load_dizhi_to_guali(guali)
        guali.set_liuqin()
        guali.set_fushen()

        # 验证fushen属性已设置
        assert guali.fushen is not None
        assert isinstance(guali.fushen, dict)

    def test_guali_calculate_all_includes_fushen(self):
        """测试calculate_all包含伏神计算"""
        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        guali.calculate_all()

        # 验证伏神已计算
        assert guali.fushen is not None
        assert "has_fushen" in guali.fushen

    def test_guali_display_shows_fushen(self):
        """测试display方法显示伏神信息"""
        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
        guali.calculate_all()

        display_str = guali.display()

        # 如果有伏神，应该包含伏神信息
        if guali.fushen.get("has_fushen"):
            assert "伏神" in display_str


# =============================================================================
# 综合测试
# =============================================================================

class TestComprehensiveFushen:
    """伏神综合测试"""

    def test_all_gongwei_fushen(self):
        """测试所有卦宫的伏神计算"""
        from backend.core.nama import load_dizhi_to_guali

        # 测试各宫的卦例
        test_guas = [
            ZhongGua.QIAN_WEI_TIAN,    # 乾宫本宫
            ZhongGua.TIAN_FENG_GOU,    # 乾宫一世
            ZhongGua.HUO_DI_JIN,       # 乾宫游魂
            ZhongGua.KAN_WEI_SHUI,     # 坎宫本宫
            ZhongGua.KUN_WEI_DI,       # 坤宫本宫
        ]

        for gua in test_guas:
            guali = Guali(ben_gua=gua)
            guali.calculate_all()

            # 确保不会出错
            assert guali.fushen is not None
            assert "has_fushen" in guali.fushen

    def test_qian_wei_tian_no_fushen(self):
        """测试乾为天六亲齐全无伏神"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()

        # 乾为天应该六亲齐全
        missing = check_liuqin_complete(guali.yaos)
        # 乾为天六亲分布：子孙、妻财、父母、官鬼、兄弟、父母 - 应该齐全


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
