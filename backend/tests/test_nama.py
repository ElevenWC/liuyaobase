"""
六爻卦例分析系统 - 纳甲装卦模块测试

测试nama模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import DanGua, Dizhi, ZhongGua
from backend.core.nama import (
    NAMA_DIZHI_NEIGUA,
    NAMA_DIZHI_WAIGUA,
    get_dizhi_from_dan_gua,
    get_dizhi_list_from_dan_gua,
    get_all_dizhi_from_zhong_gua,
    load_dizhi_to_guali,
    validate_nama_mapping,
    print_nama_table
)
from backend.core.models import Guali


# =============================================================================
# 任务 4.1 - 纳甲装卦映射表测试
# =============================================================================

class TestNamaMappingTable:
    """纳甲装卦映射表测试"""

    def test_neigua_mapping_completeness(self):
        """测试内卦映射表完整性"""
        # 验证所有八个单卦都有内卦映射
        assert len(NAMA_DIZHI_NEIGUA) == 8
        for gua in DanGua:
            assert gua in NAMA_DIZHI_NEIGUA, f"缺少单卦内卦映射: {gua.gua_name}"
            dizhi_tuple = NAMA_DIZHI_NEIGUA[gua]
            assert len(dizhi_tuple) == 3, f"内卦映射应该是3个地支"

    def test_waigua_mapping_completeness(self):
        """测试外卦映射表完整性"""
        # 验证所有八个单卦都有外卦映射
        assert len(NAMA_DIZHI_WAIGUA) == 8
        for gua in DanGua:
            assert gua in NAMA_DIZHI_WAIGUA, f"缺少单卦外卦映射: {gua.gua_name}"
            dizhi_tuple = NAMA_DIZHI_WAIGUA[gua]
            assert len(dizhi_tuple) == 3, f"外卦映射应该是3个地支"

    def test_qian_gua_mapping(self):
        """测试乾卦纳甲映射"""
        # 乾卦（内卦）：子、寅、辰
        assert NAMA_DIZHI_NEIGUA[DanGua.QIAN] == (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN)
        # 乾卦（外卦）：午、申、戌
        assert NAMA_DIZHI_WAIGUA[DanGua.QIAN] == (Dizhi.WU, Dizhi.SHEN, Dizhi.XU)

    def test_kun_gua_mapping(self):
        """测试坤卦纳甲映射"""
        # 坤卦（内卦）：未、巳、卯
        assert NAMA_DIZHI_NEIGUA[DanGua.KUN] == (Dizhi.WEI, Dizhi.SI, Dizhi.MAO)
        # 坤卦（外卦）：丑、亥、酉
        assert NAMA_DIZHI_WAIGUA[DanGua.KUN] == (Dizhi.CHOU, Dizhi.HAI, Dizhi.YOU)

    def test_zhen_gua_mapping(self):
        """测试震卦纳甲映射"""
        # 震卦（内卦）：子、寅、辰（与乾卦相同）
        assert NAMA_DIZHI_NEIGUA[DanGua.ZHEN] == (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN)
        # 震卦（外卦）：午、申、戌（与乾卦相同）
        assert NAMA_DIZHI_WAIGUA[DanGua.ZHEN] == (Dizhi.WU, Dizhi.SHEN, Dizhi.XU)


# =============================================================================
# 任务 4.2 - 根据单卦获取地支测试
# =============================================================================

class TestGetDizhiFromDanGua:
    """根据单卦获取地支测试"""

    def test_qian_neigua(self):
        """测试乾卦内卦地支"""
        # 乾卦内卦：初爻子、二爻寅、三爻辰
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 1) == Dizhi.ZI
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 2) == Dizhi.YIN
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 3) == Dizhi.CHEN

    def test_qian_waigua(self):
        """测试乾卦外卦地支"""
        # 乾卦外卦：四爻午、五爻申、上爻戌
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 4) == Dizhi.WU
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 5) == Dizhi.SHEN
        assert get_dizhi_from_dan_gua(DanGua.QIAN, 6) == Dizhi.XU

    def test_kan_gua(self):
        """测试坎卦地支"""
        # 坎卦（内卦）：寅、辰、午
        assert get_dizhi_from_dan_gua(DanGua.KAN, 1) == Dizhi.YIN
        assert get_dizhi_from_dan_gua(DanGua.KAN, 2) == Dizhi.CHEN
        assert get_dizhi_from_dan_gua(DanGua.KAN, 3) == Dizhi.WU
        # 坎卦（外卦）：申、戌、子
        assert get_dizhi_from_dan_gua(DanGua.KAN, 4) == Dizhi.SHEN
        assert get_dizhi_from_dan_gua(DanGua.KAN, 5) == Dizhi.XU
        assert get_dizhi_from_dan_gua(DanGua.KAN, 6) == Dizhi.ZI

    def test_li_gua(self):
        """测试离卦地支"""
        # 离卦（内卦）：卯、丑、亥
        assert get_dizhi_from_dan_gua(DanGua.LI, 1) == Dizhi.MAO
        assert get_dizhi_from_dan_gua(DanGua.LI, 2) == Dizhi.CHOU
        assert get_dizhi_from_dan_gua(DanGua.LI, 3) == Dizhi.HAI
        # 离卦（外卦）：酉、未、巳
        assert get_dizhi_from_dan_gua(DanGua.LI, 4) == Dizhi.YOU
        assert get_dizhi_from_dan_gua(DanGua.LI, 5) == Dizhi.WEI
        assert get_dizhi_from_dan_gua(DanGua.LI, 6) == Dizhi.SI

    def test_invalid_position(self):
        """测试无效爻位"""
        with pytest.raises(ValueError):
            get_dizhi_from_dan_gua(DanGua.QIAN, 0)
        with pytest.raises(ValueError):
            get_dizhi_from_dan_gua(DanGua.QIAN, 7)
        with pytest.raises(ValueError):
            get_dizhi_from_dan_gua(DanGua.QIAN, -1)


# =============================================================================
# 任务 4.3 - 重卦装地支测试
# =============================================================================

class TestLoadDizhiToGuali:
    """重卦装地支测试"""

    def test_qian_wei_tian(self):
        """测试乾为天装地支"""
        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        load_dizhi_to_guali(guali)

        # 验证六个爻的地支
        assert guali.yaos[0].dizhi == Dizhi.ZI   # 初爻子
        assert guali.yaos[1].dizhi == Dizhi.YIN  # 二爻寅
        assert guali.yaos[2].dizhi == Dizhi.CHEN # 三爻辰
        assert guali.yaos[3].dizhi == Dizhi.WU   # 四爻午
        assert guali.yaos[4].dizhi == Dizhi.SHEN # 五爻申
        assert guali.yaos[5].dizhi == Dizhi.XU   # 上爻戌

    def test_kun_wei_di(self):
        """测试坤为地装地支"""
        guali = Guali(ben_gua=ZhongGua.KUN_WEI_DI)
        load_dizhi_to_guali(guali)

        # 验证六个爻的地支
        assert guali.yaos[0].dizhi == Dizhi.WEI   # 初爻未
        assert guali.yaos[1].dizhi == Dizhi.SI    # 二爻巳
        assert guali.yaos[2].dizhi == Dizhi.MAO   # 三爻卯
        assert guali.yaos[3].dizhi == Dizhi.CHOU  # 四爻丑
        assert guali.yaos[4].dizhi == Dizhi.HAI   # 五爻亥
        assert guali.yaos[5].dizhi == Dizhi.YOU   # 上爻酉

    def test_shan_feng_gu(self):
        """测试山风蛊装地支"""
        # 山风蛊：内卦巽、外卦艮
        guali = Guali(ben_gua=ZhongGua.SHAN_FENG_GU)
        load_dizhi_to_guali(guali)

        # 内卦巽（初二三爻）：丑、亥、酉
        assert guali.yaos[0].dizhi == Dizhi.CHOU  # 初爻丑
        assert guali.yaos[1].dizhi == Dizhi.HAI   # 二爻亥
        assert guali.yaos[2].dizhi == Dizhi.YOU   # 三爻酉
        # 外卦艮（四五上爻）：戌、子、寅
        assert guali.yaos[3].dizhi == Dizhi.XU    # 四爻戌
        assert guali.yaos[4].dizhi == Dizhi.ZI    # 五爻子
        assert guali.yaos[5].dizhi == Dizhi.YIN   # 上爻寅

    def test_shui_lei_tun(self):
        """测试水雷屯装地支"""
        # 水雷屯：内卦震、外卦坎
        guali = Guali(ben_gua=ZhongGua.SHUI_LEI_TUN)
        load_dizhi_to_guali(guali)

        # 内卦震（初二三爻）：子、寅、辰
        assert guali.yaos[0].dizhi == Dizhi.ZI
        assert guali.yaos[1].dizhi == Dizhi.YIN
        assert guali.yaos[2].dizhi == Dizhi.CHEN
        # 外卦坎（四五上爻）：申、戌、子
        assert guali.yaos[3].dizhi == Dizhi.SHEN
        assert guali.yaos[4].dizhi == Dizhi.XU
        assert guali.yaos[5].dizhi == Dizhi.ZI

    def test_empty_bengua(self):
        """测试本卦为空的情况"""
        guali = Guali()
        load_dizhi_to_guali(guali)
        # 应该不会出错，地支保持None
        assert len(guali.yaos) == 0


# =============================================================================
# 辅助函数测试
# =============================================================================

class TestHelperFunctions:
    """辅助函数测试"""

    def test_get_dizhi_list_from_dan_gua_neigua(self):
        """测试获取单卦内卦地支列表"""
        dizhi_list = get_dizhi_list_from_dan_gua(DanGua.QIAN, True)
        assert dizhi_list == (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN)

    def test_get_dizhi_list_from_dan_gua_waigua(self):
        """测试获取单卦外卦地支列表"""
        dizhi_list = get_dizhi_list_from_dan_gua(DanGua.QIAN, False)
        assert dizhi_list == (Dizhi.WU, Dizhi.SHEN, Dizhi.XU)

    def test_get_all_dizhi_from_zhong_gua(self):
        """测试获取重卦所有地支"""
        dizhi_list = get_all_dizhi_from_zhong_gua(ZhongGua.QIAN_WEI_TIAN)
        assert len(dizhi_list) == 6
        assert dizhi_list[0] == Dizhi.ZI
        assert dizhi_list[5] == Dizhi.XU

    def test_validate_nama_mapping(self):
        """测试验证纳甲映射表"""
        assert validate_nama_mapping() == True


# =============================================================================
# 所有单卦地支映射验证测试
# =============================================================================

class TestAllDanGuaDizhi:
    """所有单卦地支映射验证测试"""

    def test_dui_gua(self):
        """测试兑卦地支"""
        # 兑卦（内卦）：巳、卯、丑
        assert NAMA_DIZHI_NEIGUA[DanGua.DUI] == (Dizhi.SI, Dizhi.MAO, Dizhi.CHOU)
        # 兑卦（外卦）：亥、酉、未
        assert NAMA_DIZHI_WAIGUA[DanGua.DUI] == (Dizhi.HAI, Dizhi.YOU, Dizhi.WEI)

    def test_gen_gua(self):
        """测试艮卦地支"""
        # 艮卦（内卦）：辰、午、申
        assert NAMA_DIZHI_NEIGUA[DanGua.GEN] == (Dizhi.CHEN, Dizhi.WU, Dizhi.SHEN)
        # 艮卦（外卦）：戌、子、寅
        assert NAMA_DIZHI_WAIGUA[DanGua.GEN] == (Dizhi.XU, Dizhi.ZI, Dizhi.YIN)

    def test_xun_gua(self):
        """测试巽卦地支"""
        # 巽卦（内卦）：丑、亥、酉
        assert NAMA_DIZHI_NEIGUA[DanGua.XUN] == (Dizhi.CHOU, Dizhi.HAI, Dizhi.YOU)
        # 巽卦（外卦）：未、巳、卯
        assert NAMA_DIZHI_WAIGUA[DanGua.XUN] == (Dizhi.WEI, Dizhi.SI, Dizhi.MAO)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
