from backend.core.dizhi_relation import (
    check_sheng, check_ke, check_he, check_chong,
    check_banhe, check_sanhe, check_shengwang,
)


def test_sheng():
    assert check_sheng("子", "寅")
    assert not check_sheng("寅", "子")
    assert check_sheng("寅", "午")
    assert not check_sheng("午", "寅")


def test_ke():
    assert check_ke("子", "午")
    assert check_ke("巳", "申")
    assert not check_ke("申", "子")


def test_he():
    assert check_he("子", "丑")
    assert check_he("丑", "子")
    assert not check_he("子", "寅")
    assert not check_he("子", "子")


def test_chong():
    assert check_chong("子", "午")
    assert check_chong("午", "子")
    assert not check_chong("子", "丑")


def test_banhe():
    assert check_banhe("申", "子")
    assert check_banhe("子", "申")
    assert not check_banhe("子", "丑")


def test_sanhe():
    assert check_sanhe("申", "子", "辰") == "水"
    assert check_sanhe("辰", "申", "子") == "水"
    assert check_sanhe("亥", "卯", "未") == "木"
    assert check_sanhe("寅", "午", "戌") == "火"
    assert check_sanhe("巳", "酉", "丑") == "金"
    assert check_sanhe("子", "丑", "寅") == ""
    assert check_sanhe("申", "申", "申") == ""


def test_shengwang():
    assert check_shengwang("寅", "亥", "长生")
    assert check_shengwang("寅", "卯", "帝旺")
    assert check_shengwang("辰", "申", "长生")  # 土同水
    assert not check_shengwang("寅", "子", "长生")


def test_invalid_input():
    assert not check_sheng("猫", "狗")
    assert check_sanhe("猫", "狗", "猪") == ""
    assert not check_shengwang("猫", "狗", "长生")
    assert not check_shengwang("子", "丑", "奇怪")
