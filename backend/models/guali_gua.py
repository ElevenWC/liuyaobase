"""卦类扩展表 — 1行/卦例，14字段"""
from typing import Optional
from sqlmodel import Field, SQLModel


class GualiGua(SQLModel, table=True):
    __tablename__ = "guali_gua"
    id: Optional[int] = Field(default=None, primary_key=True)
    guali_id: int = Field(foreign_key="guali.id")

    # 本卦信息
    ben_inner_code: Optional[str] = Field(default=None, max_length=3)
    ben_outer_code: Optional[str] = Field(default=None, max_length=3)
    ben_palace: Optional[str] = Field(default=None, max_length=10)
    ben_palace_type: Optional[str] = Field(default=None, max_length=10)
    ben_special_type: Optional[str] = Field(default=None, max_length=10)

    # 之卦信息
    zhi_inner_code: Optional[str] = Field(default=None, max_length=3)
    zhi_outer_code: Optional[str] = Field(default=None, max_length=3)
    zhi_palace: Optional[str] = Field(default=None, max_length=10)
    zhi_palace_type: Optional[str] = Field(default=None, max_length=10)
    zhi_special_type: Optional[str] = Field(default=None, max_length=10)

    # 反吟伏吟
    fan_yin_yimao: Optional[str] = Field(default=None, max_length=4)
    fan_yin_yaobian: Optional[str] = Field(default=None, max_length=4)
    fu_yin: Optional[str] = Field(default=None, max_length=4)
