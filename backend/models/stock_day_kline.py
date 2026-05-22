"""股票日K数据表"""
from datetime import date
from typing import Optional
from sqlalchemy import BIGINT, DECIMAL
from sqlmodel import Field, SQLModel


class StockDayKline(SQLModel, table=True):
    __tablename__ = "stock_day_kline"
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stock_info.id")
    trade_date: date
    open_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    high_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    low_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    close_price: Optional[float] = Field(default=None, sa_type=DECIMAL(10, 2))
    volume: Optional[int] = Field(default=None, sa_type=BIGINT)
