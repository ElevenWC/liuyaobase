from backend.core.shensha import get_shensha_dizhi, calc_shensha_status


def test_values_jia_zi():
    r = get_shensha_dizhi("甲", "子")
    assert r["gan_lu"] == "寅"
    assert r["yi_ma"] == "寅"
    assert r["yang_ren"] == "卯"
    assert r["tao_hua"] == "酉"


def test_bing_wu_equal():
    assert get_shensha_dizhi("丙", "午")["gan_lu"] == get_shensha_dizhi("戊", "午")["gan_lu"]


def test_ding_ji_equal():
    assert get_shensha_dizhi("丁", "巳")["yang_ren"] == get_shensha_dizhi("己", "巳")["yang_ren"]


def test_propagate_ben():
    status = calc_shensha_status(
        "甲", "子",
        ben_dizhi=["卯","丑","亥","午","申","戌"],
        zhi_dizhi=["子","寅","辰","午","申","戌"],
        yimao_dizhi=["寅","辰","午","申","戌","子"],
        zengshan_dizhi=["酉"],
    )
    assert status["ben_is_gan_lu"] == ""
    assert status["ben_dai_gan_lu"] == "3,5"


def test_propagate_zengshan():
    status = calc_shensha_status(
        "甲", "子",
        ben_dizhi=["卯","丑","亥","午","申","戌"],
        zhi_dizhi=["子","寅","辰","午","申","戌"],
        yimao_dizhi=["寅","辰","午","申","戌","子"],
        zengshan_dizhi=["酉"],
    )
    assert status["zengshan_is_tao_hua"] == "1"


def test_32_keys():
    status = calc_shensha_status(
        "甲", "子",
        ben_dizhi=["卯"]*6,
        zhi_dizhi=["子"]*6,
        yimao_dizhi=["寅"]*6,
        zengshan_dizhi=[],
    )
    assert len(status) == 32
