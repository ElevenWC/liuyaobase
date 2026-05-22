"""易冒伏神表 — 64卦 × 6爻 = 384条，联合主键 (code, yao_index)"""
from sqlmodel import Field, SQLModel


class StaticFushenYimao(SQLModel, table=True):
    __tablename__ = "static_fushen_yimao"
    code: str = Field(primary_key=True, max_length=6, foreign_key="bagong_gua.code")
    yao_index: int = Field(primary_key=True)
    fushen_dizhi: str = Field(max_length=1)
    fushen_liuqin: str = Field(max_length=10)
