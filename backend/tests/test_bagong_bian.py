from backend.core.bagong_bian import check_bagong_relation, calc_bagong_bian


def test_qian_7_steps():
    steps = calc_bagong_bian("111111")
    assert len(steps) == 7
    assert steps[0] == {"type": "一世", "code": "011111", "name": "天风姤"}
    assert steps[6] == {"type": "归魂", "code": "111101", "name": "火天大有"}


def test_shang_yao_never_changes():
    for step in calc_bagong_bian("111111"):
        assert step["code"][5] == "1"


def test_relation_yishi():
    assert check_bagong_relation("111111", "011111") == "一世"


def test_relation_ershi():
    assert check_bagong_relation("111111", "001111") == "二世"


def test_relation_same():
    assert check_bagong_relation("111111", "111111") == ""


def test_relation_guihun():
    assert check_bagong_relation("111111", "111101") == "归魂"
