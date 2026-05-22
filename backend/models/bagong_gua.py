"""八宫卦序表（64条记录）"""
from sqlmodel import Field, SQLModel


class BagongGua(SQLModel, table=True):
    __tablename__ = "bagong_gua"
    code: str = Field(primary_key=True, max_length=6)
    name: str = Field(max_length=20)
    palace: str = Field(max_length=10)
    element: str = Field(max_length=5)
    palace_type: str = Field(max_length=10)
