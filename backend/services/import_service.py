"""JSON 导入服务 —— 解析 + 字段映射 + 增量导入 + 调用预计算。

★ 重点关注：dyaolist 符号转换、占问时间提取、增量导入方向。
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

# dyaolist 符号 → (本卦位, 爻变位)
_YAO_MAP = {
    "′": ("1", "0"),   # 静阳
    "″": ("0", "0"),   # 静阴
    "○": ("1", "1"),   # 动阳
    "×": ("0", "1"),   # 动阴
}

# dTitle 中提取 MM.DD 的正则（\b 在中文下失效，靠后续月份范围校验过滤）
_DDATE_RE = re.compile(r"(\d{2})\.(\d{2})")


def import_from_json(file_path: str, session: Session) -> dict:
    """从 JSON 文件导入卦例。增量导入：只导入上次导入时间之后的新记录。

    返回 {"imported": 数量, "skipped": 数量, "errors": [...]}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError("JSON 应为数组格式")

    # 增量：只导入 last_import_time 之后的新记录
    last_time_str = get_config(session, _CONFIG_KEY)
    last_time = datetime.fromisoformat(last_time_str) if last_time_str else None
    newest_time: datetime | None = None

    imported = 0
    skipped = 0
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

        # 增量：上次导入时间之后的才需要导入
        if last_time is not None and dinitime <= last_time:
            skipped += 1
            continue

        try:
            _import_one(item, dinitime, session)
        except Exception as e:
            errors.append(f"导入失败: {e}")
            continue

        imported += 1
        if newest_time is None or dinitime > newest_time:
            newest_time = dinitime

    # 更新 last_import_time，只向前不倒退——防止导入旧文件后 checkpoint 回退
    if newest_time is not None:
        if last_time is None or newest_time > last_time:
            set_config(session, _CONFIG_KEY, newest_time.isoformat())

    return {"imported": imported, "skipped": skipped, "errors": errors}


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
