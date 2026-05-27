"""C3 检索结果导出——CSV / JSON"""
import csv
import json
import os
import uuid
from datetime import date, datetime
from sqlmodel import Session
from backend.schemas.search import SearchRequest
from backend.services.search_service import execute_search

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
BATCH_SIZE = 500  # 每批读取行数，避免全量加载


def export_results(session: Session, request: SearchRequest, fmt: str = "csv") -> str:
    """分批执行检索 → 流式写出为文件 → 返回下载路径"""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    filename = f"search_{uuid.uuid4().hex[:8]}.{fmt}"
    filepath = os.path.join(EXPORT_DIR, filename)

    if fmt == "csv":
        _write_csv_batched(session, request, filepath)
    elif fmt == "json":
        _write_json_batched(session, request, filepath)
    else:
        raise ValueError(f"不支持的导出格式: {fmt}")

    return filepath


def _write_csv_batched(session: Session, request: SearchRequest, filepath: str):
    """分批查询 + 增量写入 CSV"""
    writer = None
    output_file = open(filepath, "w", encoding="utf-8-sig", newline="")
    try:
        page = 1
        while True:
            request.pagination.page = page
            request.pagination.page_size = BATCH_SIZE
            resp = execute_search(session, request)
            rows = resp.data.get("results", []) if resp.data else []
            if not rows:
                break

            if writer is None:
                headers = list(rows[0].keys())
                writer = csv.DictWriter(output_file, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()

            writer.writerows(rows)
            if len(rows) < BATCH_SIZE:
                break
            page += 1
    finally:
        output_file.close()


def _write_json_batched(session: Session, request: SearchRequest, filepath: str):
    """分批查询 + 增量写入 JSON 数组"""
    output_file = open(filepath, "w", encoding="utf-8")
    output_file.write("[\n")
    first = True
    page = 1
    try:
        while True:
            request.pagination.page = page
            request.pagination.page_size = BATCH_SIZE
            resp = execute_search(session, request)
            rows = resp.data.get("results", []) if resp.data else []
            if not rows:
                break

            for row in rows:
                if not first:
                    output_file.write(",\n")
                json.dump(row, output_file, ensure_ascii=False, default=_json_serialize)
                first = False

            if len(rows) < BATCH_SIZE:
                break
            page += 1
    finally:
        output_file.write("\n]")
        output_file.close()


def _json_serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"不可序列化的类型: {type(obj)}")
