# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 股票数据API路由

本模块实现股票数据获取和与卦例关联的API接口
数据来源: Akshare库

功能:
- 股票搜索
- K线数据获取
- 分时数据获取
- 股票名称与卦例匹配
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import functools

router = APIRouter(prefix="/api/stock", tags=["Stock"])

# =============================================================================
# 数据缓存机制
# =============================================================================

# 简单的内存缓存
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_EXPIRE_SECONDS = 300  # 5分钟缓存过期


def get_cache(key: str) -> Optional[Any]:
    """获取缓存数据"""
    if key in _cache:
        data = _cache[key]
        if datetime.now() < data["expire_time"]:
            return data["value"]
        else:
            del _cache[key]
    return None


def set_cache(key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_SECONDS) -> None:
    """设置缓存数据"""
    _cache[key] = {
        "value": value,
        "expire_time": datetime.now() + timedelta(seconds=expire_seconds)
    }


def clear_cache() -> None:
    """清除所有缓存"""
    _cache.clear()


# =============================================================================
# Akshare数据获取函数
# =============================================================================

def check_akshare_available() -> bool:
    """检查Akshare库是否可用"""
    try:
        import akshare
        return True
    except ImportError:
        return False


def search_stock_impl(keyword: str) -> List[Dict[str, str]]:
    """
    搜索股票实现函数

    Args:
        keyword: 搜索关键词（股票名称或代码）

    Returns:
        匹配的股票列表
    """
    cache_key = f"search_{keyword}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    if not check_akshare_available():
        raise ImportError("Akshare库未安装，请运行: pip install akshare")

    import akshare as ak

    try:
        # 获取A股股票列表
        stock_info = ak.stock_zh_a_spot_em()

        # 搜索匹配的股票
        results = []
        for _, row in stock_info.iterrows():
            code = str(row.get('代码', ''))
            name = str(row.get('名称', ''))

            # 按关键词匹配
            if keyword in code or keyword in name:
                results.append({
                    "code": code,
                    "name": name,
                    "display": f"{name}({code})"
                })

                # 最多返回20个结果
                if len(results) >= 20:
                    break

        set_cache(cache_key, results)
        return results

    except Exception as e:
        print(f"搜索股票失败: {e}")
        return []


def get_kline_data_impl(
    code: str,
    start_date: str,
    end_date: str,
    adjust: str = "qfq"
) -> List[Dict[str, Any]]:
    """
    获取K线数据实现函数

    Args:
        code: 股票代码
        start_date: 开始日期 (YYYYMMDD)
        end_date: 结束日期 (YYYYMMDD)
        adjust: 复权类型 (qfq-前复权, hfq-后复权, 空-不复权)

    Returns:
        K线数据列表
    """
    cache_key = f"kline_{code}_{start_date}_{end_date}_{adjust}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    if not check_akshare_available():
        raise ImportError("Akshare库未安装，请运行: pip install akshare")

    import akshare as ak

    try:
        # 获取日K线数据
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )

        results = []
        for _, row in df.iterrows():
            date_str = str(row.get('日期', ''))

            # 计算干支时间
            ganzhi_info = {}
            try:
                # 解析日期
                if '-' in date_str:
                    parts = date_str.split('-')
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

                    from backend.core.time_converter import solar_to_ganzhi_month, solar_to_ganzhi_day
                    ganzhi_info = {
                        "month": solar_to_ganzhi_month(year, month),
                        "day": solar_to_ganzhi_day(year, month, day)
                    }
            except Exception:
                pass

            results.append({
                "date": date_str,
                "open": float(row.get('开盘', 0)),
                "close": float(row.get('收盘', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "volume": float(row.get('成交量', 0)),
                "amount": float(row.get('成交额', 0)),
                "amplitude": float(row.get('振幅', 0)),
                "change_pct": float(row.get('涨跌幅', 0)),
                "change_amt": float(row.get('涨跌额', 0)),
                "turnover": float(row.get('换手率', 0)),
                "ganzhi": ganzhi_info
            })

        set_cache(cache_key, results, expire_seconds=600)  # K线数据缓存10分钟
        return results

    except Exception as e:
        print(f"获取K线数据失败: {e}")
        return []


def get_intraday_data_impl(code: str) -> List[Dict[str, Any]]:
    """
    获取当日分时数据实现函数

    Args:
        code: 股票代码

    Returns:
        分时数据列表
    """
    today = datetime.now().strftime("%Y%m%d")
    cache_key = f"intraday_{code}_{today}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    if not check_akshare_available():
        raise ImportError("Akshare库未安装，请运行: pip install akshare")

    import akshare as ak

    try:
        # 获取分时数据
        df = ak.stock_zh_a_minute(symbol=code, period="1", adjust="qfq")

        results = []
        for _, row in df.iterrows():
            results.append({
                "time": str(row.get('时间', '')),
                "open": float(row.get('开盘', 0)),
                "close": float(row.get('收盘', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "volume": float(row.get('成交量', 0)),
                "amount": float(row.get('成交额', 0))
            })

        # 分时数据缓存较短时间
        set_cache(cache_key, results, expire_seconds=60)
        return results

    except Exception as e:
        print(f"获取分时数据失败: {e}")
        return []


# =============================================================================
# API接口
# =============================================================================

@router.get("/search")
async def search_stock(
    keyword: str = Query(..., description="搜索关键词（股票名称或代码）")
):
    """
    搜索股票

    根据股票名称或代码搜索匹配的股票
    """
    try:
        results = search_stock_impl(keyword)
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/kline")
async def get_kline_data(
    code: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD 或 YYYYMMDD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD 或 YYYYMMDD)"),
    adjust: str = Query("qfq", description="复权类型: qfq-前复权, hfq-后复权, 空-不复权")
):
    """
    获取K线数据

    获取指定股票在指定时间范围内的日K线数据
    """
    try:
        # 格式化日期
        start = start_date.replace("-", "")
        end = end_date.replace("-", "")

        results = get_kline_data_impl(code, start, end, adjust)
        return {
            "success": True,
            "data": results,
            "code": code,
            "start_date": start_date,
            "end_date": end_date,
            "count": len(results)
        }
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


@router.get("/intraday")
async def get_intraday_data(
    code: str = Query(..., description="股票代码")
):
    """
    获取分时数据

    获取指定股票当日的分时走势数据
    """
    try:
        results = get_intraday_data_impl(code)
        return {
            "success": True,
            "data": results,
            "code": code,
            "count": len(results)
        }
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分时数据失败: {str(e)}")


@router.get("/guali-mapping")
async def get_guali_mapping(
    name: str = Query(..., description="股票名称"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """
    获取股票名称匹配的卦例

    在卦例的占问事由字段中搜索包含该股票名称的卦例
    返回数据按日期分组，每个日期可能包含多个卦例
    """
    try:
        from backend.db.repositories import guali_repository
        from backend.services.yanqing_service import yanqing_service

        # 搜索占问事由中包含股票名称的卦例
        gualis, total = guali_repository.search_gualis(
            zhan_wen_keyword=name,
            page=1,
            page_size=1000  # 获取所有匹配的卦例
        )

        # 按日期分组
        date_groups = {}
        for guali in gualis:
            # 构建日期字符串
            date_str = f"{guali.solar_year}-{guali.solar_month:02d}-{guali.solar_day:02d}"

            # 日期范围筛选
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue

            # 获取占验情况
            yanqing = yanqing_service.get_yanqing(guali.id)
            yanqing_status = yanqing.get("status") if yanqing else None

            guali_info = {
                "id": guali.id,
                "date": date_str,
                "solar_year": guali.solar_year,
                "solar_month": guali.solar_month,
                "solar_day": guali.solar_day,
                "zhan_wen": guali.zhan_wen,
                "zhan_duan": guali.zhan_duan,
                "ben_gua_code": guali.ben_gua_code,
                "ben_gua_name": guali.ben_gua_name,
                "zhi_gua_name": guali.zhi_gua_name,
                "gongwei": guali.gongwei,
                "gongwei_index": guali.gongwei_index,
                "yanqing_status": yanqing_status
            }

            if date_str not in date_groups:
                date_groups[date_str] = {
                    "date": date_str,
                    "gualis": [],
                    "primary_guali_id": None,  # 用户选择的基准卦例ID
                    "yanqing_status": None  # K线颜色依据的占验状态
                }

            date_groups[date_str]["gualis"].append(guali_info)

        # 转换为列表格式，确定默认基准卦例
        results = []
        for date_str in sorted(date_groups.keys()):
            group = date_groups[date_str]
            gualis_list = group["gualis"]

            # 默认选择第一个卦例作为基准
            if gualis_list:
                # 优先选择有占验情况的卦例
                primary = None
                for g in gualis_list:
                    if g["yanqing_status"]:
                        primary = g
                        break
                if not primary:
                    primary = gualis_list[0]

                group["primary_guali_id"] = primary["id"]
                group["yanqing_status"] = primary["yanqing_status"]

            results.append(group)

        return {
            "success": True,
            "stock_name": name,
            "data": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取卦例映射失败: {str(e)}")


@router.get("/cache/clear")
async def clear_stock_cache():
    """
    清除股票数据缓存

    用于手动清除缓存的股票数据
    """
    clear_cache()
    return {
        "success": True,
        "message": "缓存已清除"
    }


@router.get("/status")
async def get_stock_status():
    """
    获取股票模块状态

    返回Akshare库是否可用等信息
    """
    return {
        "success": True,
        "akshare_available": check_akshare_available(),
        "cache_size": len(_cache)
    }
