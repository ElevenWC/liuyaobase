"""预计算调度中心 —— 串联 B1-B6 全部核心算法，结果分存 4 张 guali_* 扩展表。

★★ 核心文件：任何一步搞错 → 该卦例全部扩展数据错乱。
使用显式事务控制——所有步骤成功才一次 commit，任一失败则回滚。
"""
from sqlmodel import Session

from backend.core.time_converter import convert_time
from backend.core.liushen import get_liushen
from backend.core.shi_ying import get_shi_ying_labels
from backend.core.fushen_yimao import get_all_fushen as get_all_fushen_ym
from backend.core.fushen_zengshan import get_fushen as get_fushen_zs
from backend.core.an_dong import check_an_dong
from backend.core.shensha import calc_shensha_status, get_shensha_dizhi
from backend.core.liuqin import calc_liuqin
from backend.core.gua_type import (
    check_fan_yin_yimao, check_fan_yin_yaobian, check_fu_yin, get_special_type,
)
from backend.core.enums import PALACE_WUXING, CODE_TO_PALACE

from backend.models.guali import Guali
from backend.models.guali_time import GualiTime
from backend.models.guali_yao import GualiYao
from backend.models.guali_shensha import GualiShensha
from backend.models.guali_gua import GualiGua
from backend.models.static_gua_yao_info import StaticGuaYaoInfo
from backend.models.bagong_gua import BagongGua

# 夏至→冬至期间，天干用 summer；冬至→夏至用 winter
_SUMMER_JIEQI = frozenset({
    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
})


def precalculate(session: Session, guali_id: int):
    """对指定卦例执行全部预计算，结果存入 4 张 guali_* 扩展表。

    全程在一个事务内：任一阶段抛异常 → 回滚全部已写入数据。
    """
    # ── 1. 读取 guali 主表 ──────────────────────────
    guali = session.get(Guali, guali_id)
    if guali is None:
        raise ValueError(f"卦例不存在: id={guali_id}")

    zhanwen_time = guali.zhanwen_time
    ben_code = guali.ben_code
    yao_bian_code = guali.yao_bian_code
    zhi_code = guali.zhi_code

    # 缓存 bagong_gua 全表（64 行，批量导入时避免重复查询）
    bagong_map: dict[str, BagongGua] = {
        r.code: r
        for r in session.query(BagongGua).all()
    }
    ben_gua = bagong_map.get(ben_code)
    zhi_gua = bagong_map.get(zhi_code)
    if ben_gua is None or zhi_gua is None:
        raise ValueError(f"卦代码不在 bagong_gua 表中: ben={ben_code}, zhi={zhi_code}")

    ben_element = PALACE_WUXING[ben_gua.palace]

    # ── 2. B1 时间转换 → guali_time ─────────────────
    time_result = convert_time(zhanwen_time)
    day_gan = time_result["day_gan"]
    day_zhi = time_result["day_zhi"]
    jieqi = time_result["jieqi"]
    is_summer = jieqi in _SUMMER_JIEQI

    session.add(GualiTime(guali_id=guali_id, **time_result))

    # ── 3. B3 六神 ──────────────────────────────────
    liushen_list = get_liushen(day_gan)  # [初爻六神 ... 上爻六神]

    # ── 4. 查 static_gua_yao_info（本卦6爻） ─────────
    ben_static = _query_static_yao(session, ben_code)  # 6 rows

    # ── 5. 查 static_gua_yao_info（之卦6爻） ─────────
    zhi_static = _query_static_yao(session, zhi_code)

    # ── 6. B4 世应 ──────────────────────────────────
    # DB 存 "一世卦" 带"卦"后缀，get_shi_ying_labels 接受 "一世"
    ben_shi_ying = get_shi_ying_labels(ben_gua.palace_type.removesuffix("卦"))
    zhi_shi_ying = get_shi_ying_labels(zhi_gua.palace_type.removesuffix("卦"))

    # ── 7. B4 易冒伏神（6爻） ────────────────────────
    yimao_list = get_all_fushen_ym(ben_code)

    # ── 8. B4 增删伏神（0~2爻） ──────────────────────
    zengshan_list = get_fushen_zs(ben_code)

    # 增删伏神按爻位索引
    zengshan_by_yao: dict[int, dict] = {}
    for f in zengshan_list:
        zengshan_by_yao[f["yao_index"]] = f

    # 天干选择辅助
    def _pick_tiangan(static_row, is_sum):
        if static_row.tiangan is not None:
            return static_row.tiangan
        return static_row.tiangan_summer if is_sum else static_row.tiangan_winter

    # ── 9/10. 暗动 + 组装 guali_yao（6行×20字段） ────
    yimao_dizhi_list: list[str] = []
    zengshan_dizhi_list: list[str] = []

    for i in range(6):
        yao_pos = i + 1
        is_dong = yao_bian_code[i] == "1"

        ben = ben_static[i]
        zhi = zhi_static[i]
        yimao = yimao_list[i]

        # 天干
        ben_tg = _pick_tiangan(ben, is_summer)
        zhi_tg = _pick_tiangan(zhi, is_summer)

        # 之卦六亲：用本卦卦宫五行 + 之卦爻地支
        zhi_lq = calc_liuqin(ben_element, zhi.dizhi)
        # 爻类型（阳/阴）：取之卦卦代码对应位
        zhi_type = "阳" if zhi_code[i] == "1" else "阴"

        # 暗动：仅本卦静爻
        is_an = check_an_dong(ben.dizhi, is_dong, day_zhi)

        # 易冒伏神
        ym_fs = yimao["fushen_dizhi"]
        ym_lq = yimao["fushen_liuqin"]
        yimao_dizhi_list.append(ym_fs)

        # 增删伏神
        zs = zengshan_by_yao.get(yao_pos)
        has_zs = zs is not None
        zs_lq = zs["fushen_liuqin"] if zs else ""
        zs_dz = zs["fushen_dizhi"] if zs else ""
        if zs:
            zengshan_dizhi_list.append(zs_dz)

        session.add(GualiYao(
            guali_id=guali_id,
            yao_position=yao_pos,
            liushen=liushen_list[i],
            yimao_liuqin=ym_lq,
            yimao_dizhi=ym_fs,
            zengshan_exists=has_zs,
            zengshan_liuqin=zs_lq,
            zengshan_dizhi=zs_dz,
            ben_yao_type="阳" if ben_code[i] == "1" else "阴",
            ben_liuqin=ben.liuqin,
            ben_tiangan=ben_tg,
            ben_dizhi=ben.dizhi,
            ben_shi_ying=ben_shi_ying[i],
            is_dong=is_dong,
            is_an_dong=is_an,
            zhi_yao_type=zhi_type,
            zhi_liuqin=zhi_lq,
            zhi_tiangan=zhi_tg,
            zhi_dizhi=zhi.dizhi,
            zhi_shi_ying=zhi_shi_ying[i],
        ))

    # ── 11. B5 神煞 → guali_shensha ──────────────
    ben_dizhi_list = [r.dizhi for r in ben_static]
    zhi_dizhi_list = [r.dizhi for r in zhi_static]
    shensha_result = calc_shensha_status(
        day_gan, day_zhi,
        ben_dizhi_list, zhi_dizhi_list,
        yimao_dizhi_list, zengshan_dizhi_list,
    )
    # calc_shensha_status 只返回 32 组是/带状态，神煞地支需额外取
    ss_dizhi = get_shensha_dizhi(day_gan, day_zhi)
    shensha_result.update(ss_dizhi)
    # 键名翻译：算法用 gan_lu/yi_ma（带下划线），模型用 ganlu/yima（无下划线）
    _SS_KEY_MAP = {
        "gan_lu": "ganlu", "yi_ma": "yima",
        "yang_ren": "yangren", "tao_hua": "taohua",
        "zai_sha": "zaisha", "jie_sha": "jiesha",
    }
    for old, new in list(_SS_KEY_MAP.items()):
        for prefix in ("ben_is_", "ben_dai_", "zhi_is_", "zhi_dai_",
                       "yimao_is_", "yimao_dai_", "zengshan_is_", "zengshan_dai_"):
            old_key = prefix + old
            if old_key in shensha_result:
                shensha_result[prefix + new] = shensha_result.pop(old_key)
    session.add(GualiShensha(guali_id=guali_id, **shensha_result))

    # ── 12. B6 卦类型 + bagong_gua → guali_gua ────
    session.add(GualiGua(
        guali_id=guali_id,
        ben_inner_code=ben_code[:3],
        ben_outer_code=ben_code[3:],
        ben_palace=ben_gua.palace,
        ben_palace_type=ben_gua.palace_type,
        ben_special_type=get_special_type(ben_code),
        zhi_inner_code=zhi_code[:3],
        zhi_outer_code=zhi_code[3:],
        zhi_palace=zhi_gua.palace,
        zhi_palace_type=zhi_gua.palace_type,
        zhi_special_type=get_special_type(zhi_code),
        fan_yin_yimao=check_fan_yin_yimao(ben_code, zhi_code),
        fan_yin_yaobian=check_fan_yin_yaobian(ben_code, zhi_code),
        fu_yin=check_fu_yin(ben_code, zhi_code),
    ))

    # 全部成功 → 一次提交
    session.commit()


def _query_static_yao(session: Session, code: str) -> list[StaticGuaYaoInfo]:
    """查询某卦在 static_gua_yao_info 中的 6 爻，按 yao_index 升序。"""
    return list(
        session.query(StaticGuaYaoInfo)
        .where(StaticGuaYaoInfo.code == code)
        .order_by(StaticGuaYaoInfo.yao_index)
        .all()
    )
