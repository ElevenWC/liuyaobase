"""爻类扩展表 — 6行/卦例，20字段"""
from typing import Optional
from sqlmodel import Field, SQLModel


class GualiYao(SQLModel, table=True):
    __tablename__ = "guali_yao"
    id: Optional[int] = Field(default=None, primary_key=True)
    guali_id: int = Field(foreign_key="guali.id")
    yao_position: int

    # 六神
    liushen: Optional[str] = Field(default=None, max_length=10)

    # 易冒伏神
    yimao_liuqin: Optional[str] = Field(default=None, max_length=10)
    yimao_dizhi: Optional[str] = Field(default=None, max_length=2)

    # 增删伏神
    zengshan_exists: bool = Field(default=False)
    zengshan_liuqin: Optional[str] = Field(default=None, max_length=10)
    zengshan_dizhi: Optional[str] = Field(default=None, max_length=2)

    # 本卦
    ben_yao_type: Optional[str] = Field(default=None, max_length=2)
    ben_liuqin: Optional[str] = Field(default=None, max_length=10)
    ben_tiangan: Optional[str] = Field(default=None, max_length=2)
    ben_dizhi: Optional[str] = Field(default=None, max_length=2)
    ben_shi_ying: Optional[str] = Field(default=None, max_length=4)

    # 爻变
    is_dong: bool = Field(default=False)
    is_an_dong: bool = Field(default=False)

    # 之卦
    zhi_yao_type: Optional[str] = Field(default=None, max_length=2)
    zhi_liuqin: Optional[str] = Field(default=None, max_length=10)
    zhi_tiangan: Optional[str] = Field(default=None, max_length=2)
    zhi_dizhi: Optional[str] = Field(default=None, max_length=2)
    zhi_shi_ying: Optional[str] = Field(default=None, max_length=4)
