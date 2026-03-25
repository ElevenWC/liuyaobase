# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 格式转换模块

实现标准格式的解析和转换功能
标准格式: [年(公历);月日(公历),本卦,之卦*,占问事由*,占断*]{图片}
示例: 2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨
"""
from typing import Optional, Dict, Any, Tuple
import re

from backend.core.enums import ZhongGua, Dizhi
from backend.core.models import Guali, create_guali_from_input


def gua_name_to_code(name: str) -> Optional[int]:
    """
    卦名转代码

    Args:
        name: 卦名（如"乾为天"）

    Returns:
        卦代码（0-63的整数），无效返回None
    """
    gua = ZhongGua.from_name(name)
    return gua.code if gua else None


def code_to_gua_name(code: int) -> Optional[str]:
    """
    代码转卦名

    Args:
        code: 卦代码（0-63的整数）

    Returns:
        卦名（中文名称），无效返回None
    """
    gua = ZhongGua.from_code(code)
    return gua.gua_name if gua else None


def parse_time_part(time_str: str) -> Dict[str, int]:
    """
    解析标准格式中的时间部分

    格式: "年;月.日," 或 "年;月.日"

    Args:
        time_str: 时间字符串（如"2024;02.12,"或"2024;02.12"）

    Returns:
        包含year, month, day的字典

    Raises:
        ValueError: 格式无效时抛出
    """
    # 移除尾部逗号
    time_str = time_str.rstrip(',').strip()

    # 尝试匹配 "年;月.日" 格式
    pattern = r'^(\d{4});(\d{1,2})\.(\d{1,2})$'
    match = re.match(pattern, time_str)

    if not match:
        raise ValueError(f"Invalid time format: {time_str}. Expected format: YYYY;MM.DD")

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))

    # 简单的日期验证
    if not (1900 <= year <= 2100):
        raise ValueError(f"Year {year} out of valid range (1900-2100)")
    if not (1 <= month <= 12):
        raise ValueError(f"Month {month} out of valid range (1-12)")
    if not (1 <= day <= 31):
        raise ValueError(f"Day {day} out of valid range (1-31)")

    return {
        "year": year,
        "month": month,
        "day": day
    }


def parse_gua_part(gua_str: str) -> Dict[str, Optional[str]]:
    """
    解析标准格式中的重卦部分

    格式: "本卦,之卦," 或 "本卦,,"

    Args:
        gua_str: 重卦字符串（如"山风蛊,火地晋,"或"乾为天,,"）

    Returns:
        包含ben_gua_name和zhi_gua_name的字典

    Raises:
        ValueError: 格式无效或卦名无效时抛出
    """
    # 分割
    parts = gua_str.split(',')

    if len(parts) < 2:
        raise ValueError(f"Invalid gua format: {gua_str}. Expected format: 本卦,之卦, or 本卦,,")

    ben_gua_name = parts[0].strip()
    zhi_gua_name = parts[1].strip() if len(parts) > 1 else None

    # 处理空字符串
    if zhi_gua_name == '':
        zhi_gua_name = None

    # 验证本卦名
    if ben_gua_name:
        ben_gua = ZhongGua.from_name(ben_gua_name)
        if not ben_gua:
            raise ValueError(f"Invalid ben_gua name: {ben_gua_name}")

    # 验证之卦名
    if zhi_gua_name:
        zhi_gua = ZhongGua.from_name(zhi_gua_name)
        if not zhi_gua:
            raise ValueError(f"Invalid zhi_gua name: {zhi_gua_name}")

    return {
        "ben_gua_name": ben_gua_name if ben_gua_name else None,
        "zhi_gua_name": zhi_gua_name
    }


def parse_text_part(text_str: str) -> Dict[str, Optional[str]]:
    """
    解析标准格式中的语句部分

    格式: "占问事由,占断"

    Args:
        text_str: 语句字符串（如"占问股票走势,占断上涨"）

    Returns:
        包含zhan_wen和zhan_duan的字典
    """
    # 分割
    parts = text_str.split(',', 1)

    zhan_wen = parts[0].strip() if len(parts) > 0 else None
    zhan_duan = parts[1].strip() if len(parts) > 1 else None

    # 处理空字符串
    if zhan_wen == '':
        zhan_wen = None
    if zhan_duan == '':
        zhan_duan = None

    return {
        "zhan_wen": zhan_wen,
        "zhan_duan": zhan_duan
    }


def parse_standard_format(input_str: str) -> Dict[str, Any]:
    """
    解析完整标准格式

    格式: "年;月.日,本卦,之卦,占问事由,占断"
    示例: "2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨"

    Args:
        input_str: 标准格式字符串

    Returns:
        包含所有解析结果的字典

    Raises:
        ValueError: 格式无效时抛出
    """
    input_str = input_str.strip()

    # 移除首尾的[]{}符号（如果有）
    input_str = input_str.strip('[]{}')

    # 按逗号分割
    parts = input_str.split(',')

    if len(parts) < 3:
        raise ValueError(f"Invalid standard format: {input_str}. Expected at least 3 comma-separated parts")

    # 第一部分是时间
    time_part = parts[0].strip()
    time_result = parse_time_part(time_part + ',')

    # 第二部分是本卦
    ben_gua = parts[1].strip() if len(parts) > 1 else None

    # 第三部分是之卦
    zhi_gua = parts[2].strip() if len(parts) > 2 else None

    # 第四部分是占问
    zhan_wen = parts[3].strip() if len(parts) > 3 else None

    # 第五部分及之后是占断（可能包含逗号）
    zhan_duan = ','.join(parts[4:]).strip() if len(parts) > 4 else None

    # 验证卦名
    if ben_gua:
        ben_gua_obj = ZhongGua.from_name(ben_gua)
        if not ben_gua_obj:
            raise ValueError(f"Invalid ben_gua name: {ben_gua}")

    zhi_gua_name = None
    if zhi_gua:
        zhi_gua_obj = ZhongGua.from_name(zhi_gua)
        if not zhi_gua_obj:
            raise ValueError(f"Invalid zhi_gua name: {zhi_gua}")
        zhi_gua_name = zhi_gua

    # 处理空字符串
    if ben_gua == '':
        ben_gua = None
    if zhi_gua == '':
        zhi_gua_name = None
    if zhan_wen == '':
        zhan_wen = None
    if zhan_duan == '':
        zhan_duan = None

    return {
        "solar_year": time_result["year"],
        "solar_month": time_result["month"],
        "solar_day": time_result["day"],
        "ben_gua_name": ben_gua,
        "zhi_gua_name": zhi_gua_name,
        "zhan_wen": zhan_wen,
        "zhan_duan": zhan_duan
    }


def standard_format_to_guali(input_str: str) -> Guali:
    """
    将标准格式转换为Guali业务对象

    格式: "年;月.日,本卦,之卦,占问事由,占断"
    示例: "2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨"

    Args:
        input_str: 标准格式字符串

    Returns:
        Guali业务对象

    Raises:
        ValueError: 格式无效时抛出
    """
    # 解析标准格式
    parsed = parse_standard_format(input_str)

    # 创建Guali对象
    guali = create_guali_from_input(
        solar_year=parsed["solar_year"],
        solar_month=parsed["solar_month"],
        solar_day=parsed["solar_day"],
        ben_gua_name=parsed["ben_gua_name"],
        zhi_gua_name=parsed["zhi_gua_name"],
        zhan_wen=parsed["zhan_wen"],
        zhan_duan=parsed["zhan_duan"]
    )

    # 填充干支时间和计算所有属性
    guali.fill_ganzhi_time()
    guali.calculate_all()

    return guali


def guali_to_standard_format(guali: Guali) -> str:
    """
    将Guali业务对象转换为标准格式字符串

    Args:
        guali: Guali业务对象

    Returns:
        标准格式字符串
    """
    parts = []

    # 时间部分
    parts.append(f"{guali.solar_year};{guali.solar_month:02d}.{guali.solar_day:02d}")

    # 卦象部分
    ben_gua_name = guali.ben_gua.gua_name if guali.ben_gua else ""
    zhi_gua_name = guali.zhi_gua.gua_name if guali.zhi_gua else ""
    parts.append(ben_gua_name)
    parts.append(zhi_gua_name)

    # 语句部分
    parts.append(guali.zhan_wen or "")
    parts.append(guali.zhan_duan or "")

    return ",".join(parts)


def validate_standard_format(input_str: str) -> Tuple[bool, Optional[str]]:
    """
    验证标准格式是否有效

    Args:
        input_str: 标准格式字符串

    Returns:
        (是否有效, 错误信息)
    """
    try:
        parse_standard_format(input_str)
        return True, None
    except ValueError as e:
        return False, str(e)
