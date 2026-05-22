from backend.core.liuqin import calc_liuqin, get_liuqin_list


def test_all_five():
    assert calc_liuqin("火", "亥") == "官鬼"  # 水克火 爻克宫
    assert calc_liuqin("火", "午") == "兄弟"  # 同五行
    assert calc_liuqin("火", "卯") == "父母"  # 木生火 爻生宫
    assert calc_liuqin("火", "丑") == "子孙"  # 火生土 宫生爻
    assert calc_liuqin("火", "酉") == "妻财"  # 火克金 宫克爻


def test_direction_sensitive():
    assert calc_liuqin("火", "亥") == "官鬼"  # 水克火
    assert calc_liuqin("水", "巳") == "妻财"  # 水克火, 方向不同结果不同
    assert calc_liuqin("火", "亥") != calc_liuqin("水", "巳")


def test_batch():
    result = get_liuqin_list("火", ["卯", "丑", "亥", "午", "申", "戌"])
    assert len(result) == 6
    assert result[0] == "父母"  # 卯木生火


def test_gold_palace():
    assert calc_liuqin("金", "丑") == "父母"  # 土生金
    assert calc_liuqin("金", "午") == "官鬼"  # 火克金
    assert calc_liuqin("金", "亥") == "子孙"  # 金生水
    assert calc_liuqin("金", "卯") == "妻财"  # 金克木
    assert calc_liuqin("金", "酉") == "兄弟"  # 金=金
