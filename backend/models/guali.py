"""卦例主表"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlalchemy import TEXT
from sqlmodel import Field, Relationship, SQLModel

from backend.models.tag import GualiTag, Tag


class Guali(SQLModel, table=True):
    __tablename__ = "guali"
    id: Optional[int] = Field(default=None, primary_key=True)
    zhanwen_time: datetime
    zhanwen_shiyou: Optional[str] = Field(default=None, sa_type=TEXT)
    zhanduan: Optional[str] = Field(default=None, sa_type=TEXT)
    ben_code: str = Field(max_length=6)
    yao_bian_code: str = Field(default="000000", max_length=6)
    zhi_code: str = Field(default="000000", max_length=6)

    tags: List[Tag] = Relationship(back_populates="gualis", link_model=GualiTag)
