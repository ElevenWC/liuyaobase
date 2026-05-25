"""C3 检索结果导出——CSV / JSON"""
import csv
import json
import os
import uuid
from datetime import date, datetime
from sqlmodel import Session
from backend.schemas.search import SearchRequest
from backend.services.search_service import execute_search


class _JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def export_results(session: Session, request: SearchRequest, fmt: str = "csv") -> str:
    """执行检索 → 导出为文件 → 返回下载路径"""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # 不分页，取全量
    request.pagination.page = 1
    request.pagination.page_size = 99999
    resp = execute_search(session, request)
    rows = resp.data.get("results", []) if resp.data else []

    filename = f"search_{uuid.uuid4().hex[:8]}.{fmt}"
    filepath = os.path.join(EXPORT_DIR, filename)

    if fmt == "csv":
        _write_csv(filepath, rows)
    elif fmt == "json":
        _write_json(filepath, rows)
    else:
        raise ValueError(f"不支持的导出格式: {fmt}")

    return filepath


def _write_csv(filepath: str, rows: list[dict]):
    if not rows:
        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write("")
        return

    headers = list(rows[0].keys())
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(filepath: str, rows: list[dict]):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2, cls=_JsonEncoder)
