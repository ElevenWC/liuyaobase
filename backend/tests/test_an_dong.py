from backend.core.an_dong import check_an_dong


def test_all_6_chong():
    pairs = [("子","午"),("丑","未"),("寅","申"),("卯","酉"),("辰","戌"),("巳","亥")]
    for a, b in pairs:
        assert check_an_dong(a, False, b)
        assert check_an_dong(b, False, a)


def test_dong_yao_excluded():
    assert not check_an_dong("子", True, "午")


def test_same_not_chong():
    assert not check_an_dong("子", False, "子")


def test_not_chong():
    assert not check_an_dong("子", False, "丑")
    assert not check_an_dong("寅", False, "卯")
