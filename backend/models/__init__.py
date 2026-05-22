"""backend/models — 导入所有模型，确保 SQLModel.metadata 能发现全部表"""
from backend.models.guali import Guali
from backend.models.tag import GualiTag, Tag
from backend.models.bagong_gua import BagongGua
from backend.models.guaci import Guaci
from backend.models.system_config import SystemConfig
from backend.models.static_gua_yao_info import StaticGuaYaoInfo
from backend.models.static_fushen_zengshan import StaticFushenZengshan
from backend.models.static_fushen_yimao import StaticFushenYimao
from backend.models.guali_time import GualiTime
from backend.models.guali_shensha import GualiShensha
from backend.models.guali_gua import GualiGua
from backend.models.guali_yao import GualiYao
from backend.models.stock_info import StockInfo
from backend.models.stock_day_kline import StockDayKline
from backend.models.stock_minute_kline import StockMinuteKline
from backend.models.futures_info import FuturesInfo
from backend.models.futures_minute_kline import FuturesMinuteKline

__all__ = [
    "Guali",
    "GualiTag",
    "Tag",
    "BagongGua",
    "Guaci",
    "SystemConfig",
    "StaticGuaYaoInfo",
    "StaticFushenZengshan",
    "StaticFushenYimao",
    "GualiTime",
    "GualiShensha",
    "GualiGua",
    "GualiYao",
    "StockInfo",
    "StockDayKline",
    "StockMinuteKline",
    "FuturesInfo",
    "FuturesMinuteKline",
]
