"""
六爻卦例分析系统 - 世应定位模块测试

测试shiying模块的所有功能
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.enums import ZhongGua
from backend.core.shiying import (
    SHI_YING_MAP,
    get_shiying_by_gongwei,
    get_shi_position,
    get_ying_position,
    validate_gongwei_index,
    set_shiying_for_guali,
    get_shiying_info
)


# =============================================================================
# 任务 7.1 - 世应映射表测试
# =============================================================================

class TestShiYingMappingTable:
    """世应映射表测试"""

    def test_mapping_completeness(self):
        """测试映射表完整性"""
        expected_keys = ["本宫", "一世", "二世", "三世", "四世", "五世", "游魂", "归魂"]
        for key in expected_keys:
            assert key in SHI_YING_MAP, f"缺少宫位映射: {key}"

    def test_bengong_mapping(self):
        """测试本宫世应"""
        assert SHI_YING_MAP["本宫"] == (6, 3)

    def test_yishi_mapping(self):
        """测试一世世应"""
        assert SHI_YING_MAP["一世"] == (1, 4)

    def test_ershi_mapping(self):
        """测试二世世应"""
        assert SHI_YING_MAP["二世"] == (2, 5)

    def test_sanshi_mapping(self):
        """测试三世世应"""
        assert SHI_YING_MAP["三世"] == (3, 6)

    def test_sishi_mapping(self):
        """测试四世世应"""
        assert SHI_YING_MAP["四世"] == (4, 1)

    def test_wushi_mapping(self):
        """测试五世世应"""
        assert SHI_YING_MAP["五世"] == (5, 2)

    def test_youhun_mapping(self):
        """测试游魂世应"""
        assert SHI_YING_MAP["游魂"] == (4, 1)

    def test_guihun_mapping(self):
        """测试归魂世应"""
        assert SHI_YING_MAP["归魂"] == (3, 6)


# =============================================================================
# 任务 7.2 - 根据宫位获取世应爻位测试
# =============================================================================

class TestGetShiYingByGongwei:
    """根据宫位获取世应爻位测试"""

    def test_get_shiying_bengong(self):
        """测试本宫世应"""
        world_pos, response_pos = get_shiying_by_gongwei("本宫")
        assert world_pos == 6
        assert response_pos == 3

    def test_get_shiying_yishi(self):
        """测试一世世应"""
        world_pos, response_pos = get_shiying_by_gongwei("一世")
        assert world_pos == 1
        assert response_pos == 4

    def test_get_shiying_youhun(self):
        """测试游魂世应"""
        world_pos, response_pos = get_shiying_by_gongwei("游魂")
        assert world_pos == 4
        assert response_pos == 1

    def test_get_shiying_guihun(self):
        """测试归魂世应"""
        world_pos, response_pos = get_shiying_by_gongwei("归魂")
        assert world_pos == 3
        assert response_pos == 6

    def test_get_shiying_invalid(self):
        """测试无效宫位"""
        world_pos, response_pos = get_shiying_by_gongwei("无效")
        assert world_pos == 0
        assert response_pos == 0


class TestGetShiPosition:
    """获取世爻位置测试"""

    def test_get_shi_position_bengong(self):
        """测试本宫世爻位置"""
        assert get_shi_position("本宫") == 6

    def test_get_shi_position_yishi(self):
        """测试一世世爻位置"""
        assert get_shi_position("一世") == 1


class TestGetYingPosition:
    """获取应爻位置测试"""

    def test_get_ying_position_bengong(self):
        """测试本宫应爻位置"""
        assert get_ying_position("本宫") == 3

    def test_get_ying_position_yishi(self):
        """测试一世应爻位置"""
        assert get_ying_position("一世") == 4


class TestValidateGongweiIndex:
    """验证宫位有效性测试"""

    def test_valid_gongwei(self):
        """测试有效宫位"""
        assert validate_gongwei_index("本宫") == True
        assert validate_gongwei_index("一世") == True
        assert validate_gongwei_index("游魂") == True

    def test_invalid_gongwei(self):
        """测试无效宫位"""
        assert validate_gongwei_index("无效") == False
        assert validate_gongwei_index("") == False


# =============================================================================
# 任务 7.3 - 卦例世应设置测试
# =============================================================================

class TestSetShiyingForGuali:
    """卦例世应设置测试"""

    def test_set_shiying_bengong(self):
        """测试本宫世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)  # 本宫卦
        set_shiying_for_guali(guali)

        # 本宫: 世上(6)，应三(3)
        assert guali.yaos[5].is_world == True
        assert guali.yaos[2].is_response == True

        # 其他爻不应该是世应
        for i in [0, 1, 3, 4]:
            assert guali.yaos[i].is_world == False
            assert guali.yaos[i].is_response == False

    def test_set_shiying_yishi(self):
        """测试一世世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)  # 一世卦
        set_shiying_for_guali(guali)

        # 一世: 世初(1)，应四(4)
        assert guali.yaos[0].is_world == True
        assert guali.yaos[3].is_response == True

    def test_set_shiying_ershi(self):
        """测试二世世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.TIAN_SHAN_DUN)  # 二世卦
        set_shiying_for_guali(guali)

        # 二世: 世二(2)，应五(5)
        assert guali.yaos[1].is_world == True
        assert guali.yaos[4].is_response == True

    def test_set_shiying_sanshi(self):
        """测试三世世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.TIAN_DI_FOU)  # 三世卦
        set_shiying_for_guali(guali)

        # 三世: 世三(3)，应上(6)
        assert guali.yaos[2].is_world == True
        assert guali.yaos[5].is_response == True

    def test_set_shiying_sishi(self):
        """测试四世世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.FENG_DI_GUAN)  # 四世卦
        set_shiying_for_guali(guali)

        # 四世: 世四(4)，应初(1)
        assert guali.yaos[3].is_world == True
        assert guali.yaos[0].is_response == True

    def test_set_shiying_wushi(self):
        """测试五世世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.SHAN_DI_BO)  # 五世卦
        set_shiying_for_guali(guali)

        # 五世: 世五(5)，应二(2)
        assert guali.yaos[4].is_world == True
        assert guali.yaos[1].is_response == True

    def test_set_shiying_youhun(self):
        """测试游魂世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.HUO_DI_JIN)  # 游魂卦
        set_shiying_for_guali(guali)

        # 游魂: 世四(4)，应初(1)
        assert guali.yaos[3].is_world == True
        assert guali.yaos[0].is_response == True

    def test_set_shiying_guihun(self):
        """测试归魂世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.HUO_TIAN_DA_YOU)  # 归魂卦
        set_shiying_for_guali(guali)

        # 归魂: 世三(3)，应上(6)
        assert guali.yaos[2].is_world == True
        assert guali.yaos[5].is_response == True


# =============================================================================
# 辅助函数测试
# =============================================================================

class TestHelperFunctions:
    """辅助函数测试"""

    def test_get_shiying_info(self):
        """测试获取世应信息描述"""
        info = get_shiying_info("本宫")
        assert "世" in info
        assert "应" in info
        assert "上爻" in info
        assert "三爻" in info

    def test_get_shiying_info_invalid(self):
        """测试无效宫位的世应信息"""
        info = get_shiying_info("无效")
        assert info == "未知宫位"


# =============================================================================
# 与models.py集成测试
# =============================================================================

class TestGualiShiyingIntegration:
    """与models.py集成测试"""

    def test_guali_set_shiying(self):
        """测试Guali类的set_shiying方法"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.set_shiying()

        # 验证世应正确设置
        assert guali.world_yao is not None
        assert guali.response_yao is not None
        assert guali.world_yao.position == 6
        assert guali.response_yao.position == 3

    def test_guali_calculate_all_includes_shiying(self):
        """测试calculate_all包含世应设置"""
        from backend.core.models import Guali

        guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
        guali.calculate_all()

        # 验证世应已设置
        assert guali.world_yao is not None
        assert guali.response_yao is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
