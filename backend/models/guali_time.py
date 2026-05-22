"""时间扩展表 — 1行/卦例，11字段"""
from typing import Optional
from sqlmodel import Field, SQLModel


class GualiTime(SQLModel, table=True):
    __tablename__ = "guali_time"
    id: Optional[int] = Field(default=None, primary_key=True)
    guali_id: int = Field(foreign_key="guali.id")
    year_pillar: Optional[str] = Field(default=None, max_length=4)
    year_gan: Optional[str] = Field(default=None, max_length=2)
    year_zhi: Optional[str] = Field(default=None, max_length=2)
    month_pillar: Optional[str] = Field(default=None, max_length=4)
    month_gan: Optional[str] = Field(default=None, max_length=2)
    month_zhi: Optional[str] = Field(default=None, max_length=2)
    day_pillar: Optional[str] = Field(default=None, max_length=4)
    day_gan: Optional[str] = Field(default=None, max_length=2)
    day_zhi: Optional[str] = Field(default=None, max_length=2)
    xun_kong: Optional[str] = Field(default=None, max_length=4)
