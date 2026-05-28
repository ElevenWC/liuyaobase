"""卦例主表 CRUD — 增删改查 + 列表分页 + 标签筛选"""
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import or_, and_, func
from backend.models.guali import Guali
from backend.models.tag import GualiTag, Tag
from backend.crud.tag import get_child_tag_ids


def _build_keyword_conditions(keyword: str) -> list:
    """根据关键词构建搜索条件列表，多条之间 OR 关系。

    纯数字且无前导零：ID 精确匹配（避免 "0126" 匹配到 ID=126）
    4位纯数字：MMDD 日期匹配
    6位纯数字：YYMMDD 日期匹配（校验年份后两位）
    始终包含：占问事由文本模糊搜索
    """
    if not keyword:
        return []

    conds = [Guali.zhanwen_shiyou.contains(keyword)]

    if keyword.isdigit():
        n = len(keyword)

        # ID 匹配：仅当无前导零时（"126"→ID=126，"0126"→不做ID匹配）
        if str(int(keyword)) == keyword:
            conds.append(Guali.id == int(keyword))

        if n == 6:  # YYMMDD
            yy = int(keyword[0:2])
            mm = int(keyword[2:4])
            dd = int(keyword[4:6])
            conds.append(
                and_(
                    func.MOD(func.YEAR(Guali.zhanwen_time), 100) == yy,
                    func.MONTH(Guali.zhanwen_time) == mm,
                    func.DAY(Guali.zhanwen_time) == dd,
                )
            )
        elif n == 4:  # MMDD
            mm = int(keyword[0:2])
            dd = int(keyword[2:4])
            conds.append(
                and_(
                    func.MONTH(Guali.zhanwen_time) == mm,
                    func.DAY(Guali.zhanwen_time) == dd,
                )
            )

    return conds


def create(session: Session, data: dict) -> Guali:
    """新增一条卦例。zhi_code 若未提供则自动计算（ben_code XOR yao_bian_code）。"""
    if "zhi_code" not in data:
        ben = data["ben_code"]
        yao_bian = data.get("yao_bian_code", "000000")
        data["zhi_code"] = "".join(
            "1" if ben[i] != yao_bian[i] else "0" for i in range(6)
        )
    guali = Guali(**data)
    session.add(guali)
    session.commit()
    session.refresh(guali)
    return guali


def get_by_id(session: Session, guali_id: int) -> Guali | None:
    """按 ID 查询卦例"""
    return session.exec(
        select(Guali).where(Guali.id == guali_id)
    ).first()


def list_guali(
    session: Session,
    page: int,
    page_size: int,
    keyword: str = "",
    tag_id: int | None = None,
) -> tuple[list[Guali], int]:
    """分页列表，按 zhanwen_time 倒序；keyword 搜索占问事由；tag_id 按标签筛选。"""
    base: SelectOfScalar = select(Guali)

    if tag_id is not None:
        # 包含子标签：一级标签筛选时自动纳入其下二级标签的卦例
        child_ids = get_child_tag_ids(session, tag_id)
        tag_ids = [tag_id] + child_ids
        base = (
            base.join(GualiTag, Guali.id == GualiTag.guali_id)
            .where(GualiTag.tag_id.in_(tag_ids))  # type: ignore[union-attr]
        )

    kw_conds = _build_keyword_conditions(keyword)
    if kw_conds:
        base = base.where(or_(*kw_conds))  # type: ignore[union-attr]

    # 总数
    count_stmt = select(Guali.id)
    if tag_id is not None:
        tag_ids = [tag_id] + get_child_tag_ids(session, tag_id)
        count_stmt = count_stmt.join(GualiTag, Guali.id == GualiTag.guali_id).where(GualiTag.tag_id.in_(tag_ids))  # type: ignore[union-attr]
    if kw_conds:
        count_stmt = count_stmt.where(or_(*kw_conds))  # type: ignore[union-attr]
    total = len(session.exec(count_stmt).all())

    # 分页
    offset = (page - 1) * page_size
    results = list(
        session.exec(
            base.order_by(Guali.zhanwen_time.desc()).offset(offset).limit(page_size)  # type: ignore[union-attr]
        ).all()
    )

    return results, total


def update(session: Session, guali_id: int, data: dict) -> Guali | None:
    """更新卦例——只允许修改 zhanwen_shiyou 和 zhanduan。"""
    guali = get_by_id(session, guali_id)
    if guali is None:
        return None
    for field in ("zhanwen_shiyou", "zhanduan"):
        if field in data:
            setattr(guali, field, data[field])
    session.commit()
    session.refresh(guali)
    return guali


def delete(session: Session, guali_id: int) -> bool:
    """删除单个卦例。级联删除 guali_* 扩展表由外键 CASCADE 处理。"""
    guali = get_by_id(session, guali_id)
    if guali is None:
        return False
    session.delete(guali)
    session.commit()
    return True


def delete_batch(session: Session, ids: list[int]) -> int:
    """批量删除，返回实际删除数量。"""
    if not ids:
        return 0
    gualis = list(
        session.exec(select(Guali).where(Guali.id.in_(ids))).all()  # type: ignore[union-attr]
    )
    for g in gualis:
        session.delete(g)
    session.commit()
    return len(gualis)


def get_by_code(session: Session, ben_code: str) -> list[Guali]:
    """按本卦代码查询全部卦例"""
    return list(
        session.exec(
            select(Guali).where(Guali.ben_code == ben_code)
        ).all()
    )
