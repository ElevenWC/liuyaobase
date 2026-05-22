"""增删伏神表 — ~64条，联合主键 (code, yao_index)"""
from sqlmodel import Field, SQLModel


class StaticFushenZengshan(SQLModel, table=True):
    __tablename__ = "static_fushen_zengshan"
    code: str = Field(primary_key=True, max_length=6, foreign_key="bagong_gua.code")
    yao_index: int = Field(primary_key=True)
    missing_liuqin: str = Field(max_length=10)
    fushen_dizhi: str = Field(max_length=1)
    fushen_liuqin: str = Field(max_length=10)
    feishen_dizhi: str = Field(max_length=1)
    feishen_liuqin: str = Field(max_length=10)
