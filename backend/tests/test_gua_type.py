from backend.core.gua_type import (
    check_liu_chong, check_liu_he, get_special_type,
    check_fan_yin_yimao, check_fan_yin_yaobian, check_fu_yin,
)


def test_liu_chong():
    assert check_liu_chong("111111")
    assert check_liu_chong("100111")
    assert not check_liu_chong("101111")


def test_liu_he():
    assert check_liu_he("000111")
    assert check_liu_he("011110")
    assert not check_liu_he("111111")


def test_special_type():
    assert get_special_type("111111") == "六冲"
    assert get_special_type("000111") == "六合"
    assert get_special_type("101111") == "普通"


def test_fan_yin_yimao():
    assert check_fan_yin_yimao("111101", "111010") == "外卦"
    assert check_fan_yin_yimao("111111", "111111") == "无"


def test_fan_yin_yaobian():
    assert check_fan_yin_yaobian("111000", "111011") == "外卦"
    assert check_fan_yin_yaobian("000111", "011111") == "内卦"


def test_fu_yin():
    assert check_fu_yin("111000", "100000") == "内卦"
