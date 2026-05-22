"""期货分钟K线表（OHLC 结构，日K由此实时聚合）"""
from datetime import datetime
from typing import Optional
from sqlalchemy import BIGINT, DECIMAL
from sqlmodel import Field, SQLModel


class FuturesMinuteKline(SQLModel, table=True):
    __tablename__ = "futures_minute_kline"
    id: Optional[int] = Field(default=None, primary_key=True)
    futures_id: int = Field(foreign_key="futures_info.id")
    trade_time: datetime
    open_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    high_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    low_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    close_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    volume: Optional[int] = Field(default=None, sa_type=BIGINT)
