from backend.core.najia import get_yao_info, get_dizhi, get_neigua_code, get_waigua_code
from backend.core.enums import CODE_TO_NAME


def test_neigua_waigua():
    assert get_neigua_code("101111") == "101"
    assert get_waigua_code("101111") == "111"


def test_qian_dizhi():
    dz = get_dizhi("111111")
    assert dz == ["子", "寅", "辰", "午", "申", "戌"]


def test_kun_dizhi():
    dz = get_dizhi("000000")
    assert dz == ["未", "巳", "卯", "丑", "亥", "酉"]


def test_tongren_dizhi():
    info = get_yao_info("101111")
    assert info[0]["dizhi"] == "卯"
    assert info[3]["dizhi"] == "午"


def test_nan_kun_dual_tiangan():
    info = get_yao_info("101111")
    assert info[3]["tiangan"] is None
    assert info[3]["tiangan_summer"] is not None
    assert info[3]["tiangan_winter"] is not None


def test_normal_tiangan():
    info = get_yao_info("010010")
    for y in info:
        assert y["tiangan"] is not None


def test_total_384():
    count = sum(len(get_yao_info(code)) for code in CODE_TO_NAME)
    assert count == 384
