from backend.core.hugua import calc_hugua


def test_shuizejie():
    assert calc_hugua("110010") == "100001"


def test_qian():
    assert calc_hugua("111111") == "111111"


def test_length():
    result = calc_hugua("101111")
    assert len(result) == 6
    assert all(c in "01" for c in result)
