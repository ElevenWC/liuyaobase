from backend.core.shi_ying import get_shi_ying, get_shi_ying_labels
from backend.core.enums import GONG_WEI


def test_all_8_types():
    for t in GONG_WEI:
        s, y = get_shi_ying(t)
        assert 1 <= s <= 6
        assert 1 <= y <= 6
        assert abs(s - y) == 3


def test_yishi():
    assert get_shi_ying("一世") == (1, 4)


def test_guihun():
    assert get_shi_ying("归魂") == (3, 6)


def test_bengong():
    assert get_shi_ying("本宫") == (6, 3)


def test_labels():
    labels = get_shi_ying_labels("一世")
    assert labels == ["世", "", "", "应", "", ""]


def test_labels_guihun():
    labels = get_shi_ying_labels("归魂")
    assert labels == ["", "", "世", "", "", "应"]
