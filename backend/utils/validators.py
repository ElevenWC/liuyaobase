# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 验证器模块

实现CSV格式验证等功能
"""
from typing import Dict, Any, List, Tuple, Optional
import re
import io
import csv

from backend.core.enums import ZhongGua
from backend.core.converter import parse_standard_format, validate_standard_format


# CSV列定义
CSV_COLUMNS = [
    "year_month_day",  # 年;月.日
    "ben_gua",         # 本卦名
    "zhi_gua",         # 之卦名（可为空）
    "zhan_wen",        # 占问事由（可为空）
    "zhan_duan",       # 占断（可为空）
    "image_path"       # 图片路径（可为空）
]


def validate_time_format(time_str: str) -> Tuple[bool, Optional[str], Optional[Dict[str, int]]]:
    """
    验证时间格式

    格式: "年;月.日" (如 "2024;02.12")

    Args:
        time_str: 时间字符串

    Returns:
        (是否有效, 错误信息, 解析结果)
    """
    time_str = time_str.strip()

    # 匹配 "年;月.日" 格式
    pattern = r'^(\d{4});(\d{1,2})\.(\d{1,2})$'
    match = re.match(pattern, time_str)

    if not match:
        return False, f"时间格式错误: {time_str}，期望格式: 年;月.日 (如 2024;02.12)", None

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))

    # 验证范围
    if not (1900 <= year <= 2100):
        return False, f"年份 {year} 超出有效范围 (1900-2100)", None
    if not (1 <= month <= 12):
        return False, f"月份 {month} 超出有效范围 (1-12)", None
    if not (1 <= day <= 31):
        return False, f"日期 {day} 超出有效范围 (1-31)", None

    return True, None, {"year": year, "month": month, "day": day}


def validate_gua_name(gua_name: str, allow_empty: bool = True) -> Tuple[bool, Optional[str], Optional[ZhongGua]]:
    """
    验证卦名

    Args:
        gua_name: 卦名
        allow_empty: 是否允许为空

    Returns:
        (是否有效, 错误信息, ZhongGua对象)
    """
    gua_name = gua_name.strip()

    # 检查是否为空
    if not gua_name:
        if allow_empty:
            return True, None, None
        else:
            return False, "卦名不能为空", None

    # 验证卦名
    gua = ZhongGua.from_name(gua_name)
    if not gua:
        return False, f"无效的卦名: {gua_name}", None

    return True, None, gua


def validate_csv_row(row: List[str], row_num: int) -> Dict[str, Any]:
    """
    验证单行CSV数据

    CSV格式: 年;月.日,本卦,之卦,占问事由,占断,图片路径

    Args:
        row: CSV行数据
        row_num: 行号（用于错误提示）

    Returns:
        {
            "valid": bool,
            "errors": List[str],
            "data": Dict (如果验证通过)
        }
    """
    errors = []

    # 检查列数（至少需要时间、本卦）
    if len(row) < 2:
        return {
            "valid": False,
            "errors": [f"行 {row_num}: 列数不足，至少需要2列（时间、本卦）"],
            "data": None
        }

    # 补齐空列
    while len(row) < 6:
        row.append("")

    # 解析各列
    time_str = row[0].strip()
    ben_gua_name = row[1].strip()
    zhi_gua_name = row[2].strip() if len(row) > 2 else ""
    zhan_wen = row[3].strip() if len(row) > 3 else ""
    zhan_duan = row[4].strip() if len(row) > 4 else ""
    image_path = row[5].strip() if len(row) > 5 else ""

    # 验证时间
    time_valid, time_error, time_data = validate_time_format(time_str)
    if not time_valid:
        errors.append(f"行 {row_num}: {time_error}")

    # 验证本卦（必填）
    ben_gua_valid, ben_gua_error, ben_gua = validate_gua_name(ben_gua_name, allow_empty=False)
    if not ben_gua_valid:
        errors.append(f"行 {row_num}: {ben_gua_error}")

    # 验证之卦（可选）
    zhi_gua_valid, zhi_gua_error, zhi_gua = validate_gua_name(zhi_gua_name, allow_empty=True)
    if not zhi_gua_valid:
        errors.append(f"行 {row_num}: {zhi_gua_error}")

    # 如果有错误，返回错误
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "data": None
        }

    # 构建数据
    data = {
        "solar_year": time_data["year"],
        "solar_month": time_data["month"],
        "solar_day": time_data["day"],
        "ben_gua_name": ben_gua_name,
        "zhi_gua_name": zhi_gua_name if zhi_gua_name else None,
        "zhan_wen": zhan_wen if zhan_wen else None,
        "zhan_duan": zhan_duan if zhan_duan else None,
        "image_path": image_path if image_path else None
    }

    return {
        "valid": True,
        "errors": [],
        "data": data
    }


def validate_csv_format(csv_content: str) -> Dict[str, Any]:
    """
    验证CSV文件内容

    Args:
        csv_content: CSV文件内容字符串

    Returns:
        {
            "valid": bool,
            "total_rows": int,
            "valid_rows": int,
            "invalid_rows": int,
            "errors": List[str],
            "data": List[Dict]
        }
    """
    # 解析CSV
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)

    if not rows:
        return {
            "valid": False,
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": ["CSV文件为空"],
            "data": []
        }

    total_rows = len(rows)
    valid_data = []
    all_errors = []
    valid_count = 0
    invalid_count = 0

    # 验证每一行
    for i, row in enumerate(rows, start=1):
        # 跳过空行
        if not any(cell.strip() for cell in row):
            continue

        result = validate_csv_row(row, i)

        if result["valid"]:
            valid_data.append(result["data"])
            valid_count += 1
        else:
            all_errors.extend(result["errors"])
            invalid_count += 1

    return {
        "valid": invalid_count == 0,
        "total_rows": total_rows,
        "valid_rows": valid_count,
        "invalid_rows": invalid_count,
        "errors": all_errors,
        "data": valid_data
    }


def validate_csv_file(file_content: bytes, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    验证CSV文件（字节数据）

    Args:
        file_content: 文件字节数据
        encoding: 文件编码

    Returns:
        验证结果（同validate_csv_format）
    """
    # 尝试不同编码
    encodings_to_try = [encoding, "utf-8", "gbk", "gb2312", "utf-8-sig"]

    content = None
    used_encoding = None

    for enc in encodings_to_try:
        try:
            content = file_content.decode(enc)
            # 如果使用utf-8解码带BOM的文件，需要手动移除BOM
            if content.startswith('\ufeff'):
                content = content[1:]
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        return {
            "valid": False,
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": ["无法解码文件，请确保文件编码为UTF-8或GBK"],
            "data": [],
            "encoding": None
        }

    result = validate_csv_format(content)
    result["encoding"] = used_encoding

    return result


def parse_csv_to_guali_inputs(csv_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    解析CSV内容并转换为卦例输入数据

    Args:
        csv_content: CSV文件内容字符串

    Returns:
        (有效数据列表, 错误列表)
    """
    result = validate_csv_format(csv_content)
    return result["data"], result["errors"]
