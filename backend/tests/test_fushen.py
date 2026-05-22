from backend.core.fushen_zengshan import get_fushen as get_fushen_zs
from backend.core.fushen_yimao import get_all_fushen as get_all_fushen_ym
from backend.core.enums import CODE_TO_NAME


def test_zengshan_guai():
    fs = get_fushen_zs("011111")
    assert len(fs) >= 1
    f = fs[0]
    assert f["missing_liuqin"] == "妻财"
    assert f["fushen_dizhi"] == "寅"
    assert f["fushen_liuqin"] == "妻财"
    assert f["yao_index"] == 2


def test_zengshan_qian_empty():
    fs = get_fushen_zs("111111")
    assert fs == []


def test_zengshan_keys():
    for code in CODE_TO_NAME:
        for f in get_fushen_zs(code):
            assert set(f.keys()) == {
                "yao_index","missing_liuqin","fushen_dizhi",
                "fushen_liuqin","feishen_dizhi","feishen_liuqin",
            }


def test_yimao_384():
    count = sum(len(get_all_fushen_ym(code)) for code in CODE_TO_NAME)
    assert count == 384


def test_yimao_per_gua():
    for code in CODE_TO_NAME:
        fs = get_all_fushen_ym(code)
        assert len(fs) == 6
        for f in fs:
            assert set(f.keys()) == {"fushen_dizhi", "fushen_liuqin", "yao_index"}
