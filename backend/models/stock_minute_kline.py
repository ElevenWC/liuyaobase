"""股票分钟K线表（OHLC 结构）"""
from datetime import datetime
from typing import Optional
from sqlalchemy import BIGINT, DECIMAL
from sqlmodel import Field, SQLModel


class StockMinuteKline(SQLModel, table=True):
    __tablename__ = "stock_minute_kline"
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stock_info.id")
    trade_time: datetime
    open_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    high_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    low_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    close_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    volume: Optional[int] = Field(default=None, sa_type=BIGINT)
