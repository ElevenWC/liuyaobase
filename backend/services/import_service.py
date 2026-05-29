"""JSON 导入服务 —— 解析 + 字段映射 + 串行级联去重 + 调用预计算。

★ 重点关注：dyaolist 符号转换、占问时间提取、四层去重判定。
"""
import json
import re
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from backend.crud.guali import create as create_guali
from backend.crud.system_config import get_config, set_config
from backend.crud.bagong_gua import get_by_code as get_gua_by_code
from backend.services.precalculate_service import precalculate
from backend.models.guali import Guali

_CONFIG_KEY = "last_import_time"
_CONFIG_FILES_KEY = "imported_files"

# dyaolist 符号 → (本卦位, 爻变位)
_YAO_MAP = {
    "′": ("1", "0"),   # 静阳
    "″": ("0", "0"),   # 静阴
    "○": ("1", "1"),   # 动阳
    "×": ("0", "1"),   # 动阴
}

# dTitle 中提取 MM.DD 的正则（\b 在中文下失效，靠后续月份范围校验过滤）
_DDATE_RE = re.compile(r"(\d{2})\.(\d{2})")


def _compute_zhi_code(ben_code: str, yao_bian_code: str) -> str:
    """ben_code XOR yao_bian_code → zhi_code"""
    return "".join(
        "1" if ben_code[i] != yao_bian_code[i] else "0" for i in range(6)
    )


def is_duplicate(session: Session, shiyou: str, time, ben_code: str, zhi_code: str) -> bool:
    """串行级联四层判定：事由→时间→本卦→之卦。一次 DB 查询 + 内存过滤。"""
    candidates = session.exec(
        select(Guali).where(Guali.zhanwen_shiyou == shiyou)
    ).all()
    for g in candidates:
        if g.zhanwen_time == time and g.ben_code == ben_code and g.zhi_code == zhi_code:
            return True
    return False


def is_file_imported(session: Session, filename: str) -> bool:
    """检查文件名是否已导入过"""
    val = get_config(session, _CONFIG_FILES_KEY)
    if not val:
        return False
    try:
        return filename in json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return False


def mark_file_imported(session: Session, filename: str):
    """记录文件名已导入"""
    val = get_config(session, _CONFIG_FILES_KEY)
    files = json.loads(val) if val else []
    if filename not in files:
        files.append(filename)
        set_config(session, _CONFIG_FILES_KEY, json.dumps(files, ensure_ascii=False))


def import_from_json(file_path: str, session: Session, original_filename: str = "") -> dict:
    """从 JSON 文件导入卦例。串行级联去重，支持重复导入同一文件。

    返回 {"imported": 数量, "duplicates": 数量, "errors": [...]}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    filename = original_filename or path.name

    # 文件已导入过 → 整批跳过
    if is_file_imported(session, filename):
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        total = len(data) if isinstance(data, list) else 0
        return {"imported": 0, "duplicates": total, "errors": [],
                "message": f"文件「{filename}」已导入过，共 {total} 条全部跳过"}

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError("JSON 应为数组格式")

    # 文件为新→旧顺序，倒过来让最老记录先导入 → 编号最小
    data.reverse()

    newest_time: datetime | None = None

    imported = 0
    duplicates = 0
    errors: list[str] = []

    for item in data:
        dinitime_str = item.get("dIniTime", "")
        if not dinitime_str:
            errors.append("缺少 dIniTime")
            continue

        try:
            dinitime = datetime.fromisoformat(dinitime_str)
        except (ValueError, TypeError):
            errors.append(f"dIniTime 格式错误: {dinitime_str}")
            continue

        try:
            zhanwen_time = _extract_zhanwen_time(item, dinitime)
            ben_code, yao_bian_code = _parse_dyaolist(item.get("dyaolist", ""))
            zhi_code = _compute_zhi_code(ben_code, yao_bian_code)
            shiyou = item.get("dTitle", "")

            if is_duplicate(session, shiyou, zhanwen_time, ben_code, zhi_code):
                duplicates += 1
                continue

            _import_one(item, dinitime, session)
        except Exception as e:
            errors.append(f"导入失败: {e}")
            continue

        imported += 1
        if newest_time is None or dinitime > newest_time:
            newest_time = dinitime

    # 更新 last_import_time
    if newest_time is not None:
        last_time_str = get_config(session, _CONFIG_KEY)
        last_time = datetime.fromisoformat(last_time_str) if last_time_str else None
        if last_time is None or newest_time > last_time:
            set_config(session, _CONFIG_KEY, newest_time.isoformat())

    # 标记文件已导入
    if imported > 0:
        mark_file_imported(session, filename)

    return {"imported": imported, "duplicates": duplicates, "errors": errors}


def import_single(data: dict, session: Session) -> Guali:
    """手动导入单个卦例。data 来自前端表单。"""
    zhanwen_time = data.get("zhanwen_time")
    if isinstance(zhanwen_time, str):
        zhanwen_time = datetime.fromisoformat(zhanwen_time)

    # 卦名 → 代码转换
    ben_code = data.get("ben_code")
    if not ben_code:
        ben_name = data.get("ben_name")
        if ben_name:
            gua = get_gua_by_code(session, "")  # 需要按名称查
            # 遍历 bagong_gua 表匹配卦名
            from backend.models.bagong_gua import BagongGua
            gua = session.exec(
                select(BagongGua).where(BagongGua.name == ben_name)
            ).first()
            if not gua:
                raise ValueError(f"卦名不存在: {ben_name}")
            ben_code = gua.code

    zhi_code = data.get("zhi_code")
    if not zhi_code:
        zhi_name = data.get("zhi_name")
        if zhi_name:
            from backend.models.bagong_gua import BagongGua
            gua = session.exec(
                select(BagongGua).where(BagongGua.name == zhi_name)
            ).first()
            if not gua:
                raise ValueError(f"卦名不存在: {zhi_name}")
            zhi_code = gua.code

    guali_data = {
        "zhanwen_time": zhanwen_time,
        "zhanwen_shiyou": data.get("zhanwen_shiyou", ""),
        "zhanduan": data.get("zhanduan", ""),
        "ben_code": ben_code,
        "yao_bian_code": data.get("yao_bian_code", "000000"),
        "zhi_code": zhi_code or "000000",
    }

    # 去重检查
    if is_duplicate(session, guali_data["zhanwen_shiyou"], guali_data["zhanwen_time"],
                    guali_data["ben_code"], guali_data["zhi_code"]):
        raise ValueError("此卦例已存在（事由+时间+本卦+之卦四层匹配）")

    guali = create_guali(session, guali_data)
    precalculate(session, guali.id)
    return guali


def get_last_import_time(session: Session) -> str | None:
    """从 system_config 读取上次导入时间"""
    return get_config(session, _CONFIG_KEY)


def update_last_import_time(session: Session, dinitime: str):
    """更新 system_config 中的 last_import_time"""
    set_config(session, _CONFIG_KEY, dinitime)


def _import_one(item: dict, dinitime: datetime, session: Session):
    """导入单条 JSON 卦例。"""
    zhanwen_time = _extract_zhanwen_time(item, dinitime)
    ben_code, yao_bian_code = _parse_dyaolist(item.get("dyaolist", ""))

    guali_data = {
        "zhanwen_time": zhanwen_time,
        "zhanwen_shiyou": item.get("dTitle", ""),
        "zhanduan": (item.get("dNote") or "").replace("\\n", "\n"),
        "ben_code": ben_code,
        "yao_bian_code": yao_bian_code,
    }
    guali = create_guali(session, guali_data)
    precalculate(session, guali.id)


def _extract_zhanwen_time(item: dict, dinitime: datetime) -> datetime:
    """从 dTitle 提取 MM.DD 日期 + dIniTime 年份 → 占问时间（只保留年月日）。

    若 dTitle 含 MM.DD-MM.DD 日期范围 → 回退用 dIniTime。
    若 dTitle 无 MM.DD → 用 dIniTime。
    """
    title = item.get("dTitle", "")

    # 日期范围（如 02.25-03.01）→ 不用 dTitle
    if re.search(r"\d{2}\.\d{2}-\d{2}\.\d{2}", title):
        return dinitime.replace(hour=0, minute=0, second=0, microsecond=0)

    m = _DDATE_RE.search(title)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return datetime(dinitime.year, month, day)

    return dinitime.replace(hour=0, minute=0, second=0, microsecond=0)


def _parse_dyaolist(dyaolist: str) -> tuple[str, str]:
    """dyaolist 符号串 → (ben_code, yao_bian_code)。

    "○,′,″,○,′,′," → ben_code="110111", yao_bian_code="100100"
    """
    cleaned = dyaolist.strip().rstrip(",")
    if not cleaned:
        raise ValueError("dyaolist 为空")
    symbols = [s.strip() for s in cleaned.split(",")]
    if len(symbols) != 6:
        raise ValueError(f"dyaolist 应有 6 个符号，实际 {len(symbols)}: {dyaolist}")

    ben_bits: list[str] = []
    bian_bits: list[str] = []
    for sym in symbols:
        if sym not in _YAO_MAP:
            raise ValueError(f"未知爻符号: {sym}")
        b, bi = _YAO_MAP[sym]
        ben_bits.append(b)
        bian_bits.append(bi)

    return "".join(ben_bits), "".join(bian_bits)
