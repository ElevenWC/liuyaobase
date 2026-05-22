"""卦爻辞表（64条，含 JSON 字段）"""
from typing import Any, Optional
from sqlalchemy import JSON, TEXT
from sqlmodel import Field, SQLModel


class Guaci(SQLModel, table=True):
    __tablename__ = "guaci"
    code: str = Field(primary_key=True, max_length=6, foreign_key="bagong_gua.code")
    gua_ci: Optional[str] = Field(default=None, sa_type=TEXT)
    tuan_zhuan: Optional[str] = Field(default=None, sa_type=TEXT)
    xiang_zhuan: Optional[str] = Field(default=None, sa_type=TEXT)
    yao_ci: Optional[dict[str, Any]] = Field(default=None, sa_type=JSON)
    wenyan: Optional[str] = Field(default=None, sa_type=TEXT)
    yong: Optional[dict[str, Any]] = Field(default=None, sa_type=JSON)
