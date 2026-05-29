"""B1 时间转换：公历 datetime → 干支时间信息

使用 lunar-python 库。所有时间按本地时间处理，只精确到日（无时柱）。
"""
from datetime import date, datetime
from lunar_python import Solar

# lunar-python 节气表中英文名 → 中文名
_JIEQI_EN_TO_CN: dict[str, str] = {
    "LI_CHUN": "立春", "YU_SHUI": "雨水", "JING_ZHE": "惊蛰",
    "CHUN_FEN": "春分", "QING_MING": "清明", "GU_YU": "谷雨",
    "LI_XIA": "立夏", "XIAO_MAN": "小满", "MANG_ZHONG": "芒种",
    "XIA_ZHI": "夏至", "XIAO_SHU": "小暑", "DA_SHU": "大暑",
    "LI_QIU": "立秋", "CHU_SHU": "处暑", "BAI_LU": "白露",
    "QIU_FEN": "秋分", "HAN_LU": "寒露", "SHUANG_JIANG": "霜降",
    "LI_DONG": "立冬", "XIAO_XUE": "小雪", "DA_XUE": "大雪",
    "DONG_ZHI": "冬至", "XIAO_HAN": "小寒", "DA_HAN": "大寒",
}


def convert_time(dt: datetime) -> dict:
    """公历 datetime → 干支时间信息

    返回: {
        "year_pillar": "丙午", "year_gan": "丙", "year_zhi": "午",
        "month_pillar": "辛卯", "month_gan": "辛", "month_zhi": "卯",
        "day_pillar": "甲子", "day_gan": "甲", "day_zhi": "子",
        "xun_kong": "戌亥",
        "jieqi": "惊蛰"      # 当前节气，非节气日为 None 或上一节气
    }
    """
    solar = Solar.fromDate(dt)
    lunar = solar.getLunar()

    return {
        "year_pillar": lunar.getYearInGanZhi(),
        "year_gan": lunar.getYearGan(),
        "year_zhi": lunar.getYearZhi(),
        "month_pillar": lunar.getMonthInGanZhi(),
        "month_gan": lunar.getMonthGan(),
        "month_zhi": lunar.getMonthZhi(),
        "day_pillar": lunar.getDayInGanZhi(),
        "day_gan": lunar.getDayGan(),
        "day_zhi": lunar.getDayZhi(),
        "xun_kong": lunar.getDayXunKong(),
        "jieqi": lunar.getCurrentJieQi() or _prev_jieqi(lunar),
    }


def get_jieqi_dates(year: int) -> list[tuple[str, date]]:
    """返回指定年份的 24 节气名称 + 公历日期列表。

    用于 C4 月K 聚合（如卯月 = 惊蛰当天 → 清明前一天）。
    """
    # 获取该年春节附近的农历对象来查节气表
    solar = Solar.fromDate(datetime(year, 6, 15))
    lunar = solar.getLunar()
    table = lunar.getJieQiTable()

    result: list[tuple[str, date]] = []
    for name, s in table.items():
        # 统一节日名称为中文
        cn_name = _JIEQI_EN_TO_CN.get(name, name)
        jieqi_date = date(int(str(s)[:4]), int(str(s)[5:7]), int(str(s)[8:10]))
        if jieqi_date.year == year:
            result.append((cn_name, jieqi_date))

    result.sort(key=lambda x: x[1])
    return result


def _prev_jieqi(lunar) -> str | None:
    """获取上一个节气名（非节气日时用）"""
    prev = lunar.getPrevJieQi()
    if prev:
        return _JIEQI_EN_TO_CN.get(prev.getName(), prev.getName())
    return None


def get_calendar_month(year: int, month: int) -> dict:
    """返回指定年月的日历数据——每天的公历日期、星期、干支、节气标记。

    返回: {
        "year": 2026, "month": 5,
        "days": [{"day": 1, "weekday": 0, "day_ganzhi": "甲子",
                  "year_ganzhi": "丙午", "month_ganzhi": "癸巳", "jieqi": null}, ...]
    }
    weekday: 0=周一, 6=周日
    """
    import calendar as cal_mod

    days = []
    _, total_days = cal_mod.monthrange(year, month)

    # 节气表：当前月 + 相邻月
    jieqi_map: dict[int, str] = {}
    for y in (year - 1, year, year + 1):
        for name, d in get_jieqi_dates(y):
            if d.year == year and d.month == month:
                jieqi_map[d.day] = name

    for day_num in range(1, total_days + 1):
        dt = datetime(year, month, day_num)
        solar = Solar.fromDate(dt)
        lunar = solar.getLunar()

        # weekday: Python 的 weekday() 0=周一 6=周日，正好与需求一致
        wd = dt.weekday()

        days.append({
            "day": day_num,
            "weekday": wd,
            "day_ganzhi": lunar.getDayInGanZhi(),
            "year_ganzhi": lunar.getYearInGanZhi(),
            "month_ganzhi": lunar.getMonthInGanZhi(),
            "jieqi": jieqi_map.get(day_num),
        })

    return {"year": year, "month": month, "days": days}
