"""卦爻属性表 — 64卦 × 6爻 = 384条，联合主键 (code, yao_index)"""
from typing import Optional
from sqlmodel import Field, SQLModel


class StaticGuaYaoInfo(SQLModel, table=True):
    __tablename__ = "static_gua_yao_info"
    code: str = Field(primary_key=True, max_length=6, foreign_key="bagong_gua.code")
    yao_index: int = Field(primary_key=True)
    dizhi: str = Field(max_length=1)
    tiangan: Optional[str] = Field(default=None, max_length=1)
    tiangan_summer: Optional[str] = Field(default=None, max_length=1)
    tiangan_winter: Optional[str] = Field(default=None, max_length=1)
    liuqin: str = Field(max_length=10)
