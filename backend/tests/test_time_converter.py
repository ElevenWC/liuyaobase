from datetime import datetime
from backend.core.time_converter import convert_time, get_jieqi_dates
from backend.core.enums import TIAN_GAN, DI_ZHI


def test_convert_basic():
    r = convert_time(datetime(2026, 3, 25))
    for k in ["year_pillar","year_gan","year_zhi","month_pillar","month_gan",
              "month_zhi","day_pillar","day_gan","day_zhi","xun_kong","jieqi"]:
        assert k in r and isinstance(r[k], str) and len(r[k]) >= 1


def test_pillar_consistency():
    r = convert_time(datetime(2026, 6, 15))
    assert r["year_gan"] + r["year_zhi"] == r["year_pillar"]
    assert r["month_gan"] + r["month_zhi"] == r["month_pillar"]
    assert r["day_gan"] + r["day_zhi"] == r["day_pillar"]


def test_gan_zhi_valid():
    r = convert_time(datetime(2026, 1, 1))
    assert r["day_gan"] in TIAN_GAN
    assert r["day_zhi"] in DI_ZHI


def test_xun_kong_format():
    r = convert_time(datetime(2026, 3, 25))
    assert len(r["xun_kong"]) == 2


def test_lichun_boundary():
    r1 = convert_time(datetime(2026, 2, 4))
    r2 = convert_time(datetime(2026, 2, 3))
    assert r1["month_zhi"] == "寅"
    assert r2["month_zhi"] == "丑"


def test_jieqi_count():
    dates = get_jieqi_dates(2026)
    assert len(dates) == 24
    names = [n for n, _ in dates]
    for jq in ["立春", "惊蛰", "清明", "立夏", "芒种", "小暑", "立秋", "白露", "寒露", "立冬", "大雪", "冬至"]:
        assert jq in names
