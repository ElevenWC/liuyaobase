"""卦例业务逻辑 —— 列表查询 + 5 表详情拼装。

★ 重点关注：5 表 JOIN 数据组装、标签批量查询防 N+1。
"""
from sqlmodel import Session
from backend.crud.guali import list_guali, get_by_id as get_guali
from backend.crud.guali_time import get_by_guali_id as get_time
from backend.crud.guali_yao import get_by_guali_id as get_yaos
from backend.crud.guali_shensha import get_by_guali_id as get_shensha
from backend.crud.guali_gua import get_by_guali_id as get_gua
from backend.crud.tag import get_tags_by_guali, get_all as get_all_tags
from backend.core.enums import CODE_TO_NAME
from backend.schemas.guali import GualiDetailResponse


def get_guali_list(
    session: Session,
    page: int,
    page_size: int,
    keyword: str = "",
    tag_id: int | None = None,
) -> dict:
    """分页列表——返回卡片字段，标签批量预查。"""
    results, total = list_guali(session, page, page_size, keyword, tag_id)

    if not results:
        return {"items": [], "total": total, "page": page}

    # 批量查标签（一次 SQL，避免 N+1）
    guali_ids = [g.id for g in results]
    all_tags = get_all_tags(session)
    # 预加载关联关系
    from backend.models.tag import GualiTag
    links = session.query(GualiTag).where(
        GualiTag.guali_id.in_(guali_ids)  # type: ignore[attr-defined]
    ).all()
    tag_by_guali: dict[int, list[str]] = {}
    for link in links:
        tag = next((t for t in all_tags if t.id == link.tag_id), None)
        if tag:
            tag_by_guali.setdefault(link.guali_id, []).append(tag.name)

    items = []
    for g in results:
        items.append({
            "id": g.id,
            "zhanwen_time": g.zhanwen_time.isoformat() if g.zhanwen_time else None,
            "zhanwen_shiyou": g.zhanwen_shiyou[:50] if g.zhanwen_shiyou else "",
            "ben_code": g.ben_code,
            "tags": tag_by_guali.get(g.id, [])[:3],  # 列表最多显示 3 个
        })

    return {"items": items, "total": total, "page": page}


def get_guali_detail(session: Session, guali_id: int) -> dict | None:
    """5 表拼装——返回完整卦例详情。缺失扩展表字段返回空值。"""
    guali = get_guali(session, guali_id)
    if guali is None:
        return None

    time = get_time(session, guali_id)
    yaos = get_yaos(session, guali_id)
    shensha = get_shensha(session, guali_id)
    gua = get_gua(session, guali_id)
    tags = get_tags_by_guali(session, guali_id)

    def _str(v):
        return str(v) if v else ""

    detail = {
        "id": guali.id,
        "zhanwen_time": guali.zhanwen_time,
        "zhanwen_shiyou": guali.zhanwen_shiyou or "",
        "zhanduan": guali.zhanduan or "",
        "ben_code": guali.ben_code,
        "yao_bian_code": guali.yao_bian_code,
        "zhi_code": guali.zhi_code,
        "ben_name": CODE_TO_NAME.get(guali.ben_code, ""),
        "zhi_name": CODE_TO_NAME.get(guali.zhi_code, "") if guali.yao_bian_code != "000000" else "",
    }

    # 时间
    if time:
        detail.update({
            "year_pillar": _str(time.year_pillar), "year_gan": _str(time.year_gan),
            "year_zhi": _str(time.year_zhi), "month_pillar": _str(time.month_pillar),
            "month_gan": _str(time.month_gan), "month_zhi": _str(time.month_zhi),
            "day_pillar": _str(time.day_pillar), "day_gan": _str(time.day_gan),
            "day_zhi": _str(time.day_zhi), "xun_kong": _str(time.xun_kong),
        })

    # 神煞
    if shensha:
        detail.update({
            "gan_lu": _str(shensha.gan_lu), "yi_ma": _str(shensha.yi_ma),
            "yang_ren": _str(shensha.yang_ren), "tao_hua": _str(shensha.tao_hua),
        })

    # 卦类
    if gua:
        detail.update({
            "ben_palace": _str(gua.ben_palace),
            "ben_palace_type": _str(gua.ben_palace_type),
            "ben_special_type": _str(gua.ben_special_type),
            "zhi_palace": _str(gua.zhi_palace),
            "zhi_palace_type": _str(gua.zhi_palace_type),
            "zhi_special_type": _str(gua.zhi_special_type),
            "fan_yin_yimao": _str(gua.fan_yin_yimao),
            "fan_yin_yaobian": _str(gua.fan_yin_yaobian),
            "fu_yin": _str(gua.fu_yin),
        })

    # 爻
    detail["yaos"] = []
    for y in yaos:
        detail["yaos"].append({
            "yao_position": y.yao_position,
            "liushen": _str(y.liushen),
            "yimao_liuqin": _str(y.yimao_liuqin), "yimao_dizhi": _str(y.yimao_dizhi),
            "zengshan_exists": y.zengshan_exists,
            "zengshan_liuqin": _str(y.zengshan_liuqin), "zengshan_dizhi": _str(y.zengshan_dizhi),
            "ben_yao_type": _str(y.ben_yao_type),
            "ben_liuqin": _str(y.ben_liuqin), "ben_tiangan": _str(y.ben_tiangan),
            "ben_dizhi": _str(y.ben_dizhi), "ben_shi_ying": _str(y.ben_shi_ying),
            "is_dong": y.is_dong, "is_an_dong": y.is_an_dong,
            "zhi_yao_type": _str(y.zhi_yao_type),
            "zhi_liuqin": _str(y.zhi_liuqin), "zhi_tiangan": _str(y.zhi_tiangan),
            "zhi_dizhi": _str(y.zhi_dizhi), "zhi_shi_ying": _str(y.zhi_shi_ying),
        })

    # 标签
    detail["tags"] = [t.name for t in tags]

    return detail
