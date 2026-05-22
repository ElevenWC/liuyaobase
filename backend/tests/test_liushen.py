import pytest
from backend.core.liushen import get_liushen
from backend.core.enums import TIAN_GAN


def test_all_10_gan():
    for gan in TIAN_GAN:
        result = get_liushen(gan)
        assert len(result) == 6
        assert len(set(result)) == 6  # all unique


def test_jia_start():
    assert get_liushen("甲") == ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]


def test_bing_start():
    assert get_liushen("丙")[0] == "朱雀"


def test_wu_start():
    assert get_liushen("戊")[0] == "勾陈"


def test_ji_start():
    assert get_liushen("己")[0] == "螣蛇"


def test_geng_start():
    assert get_liushen("庚")[0] == "白虎"


def test_ren_start():
    assert get_liushen("壬")[0] == "玄武"


def test_invalid():
    with pytest.raises(ValueError):
        get_liushen("猫")
