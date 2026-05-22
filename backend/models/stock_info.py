"""股票信息表"""
from datetime import datetime as dt
from typing import Optional
from sqlmodel import Field, SQLModel


class StockInfo(SQLModel, table=True):
    __tablename__ = "stock_info"
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_code: str = Field(max_length=20, unique=True)
    stock_name: str = Field(max_length=50)
    exchange: Optional[str] = Field(default=None, max_length=20)
    data_source: Optional[str] = Field(default=None, max_length=20)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    created_at: Optional[dt] = Field(default=None)
