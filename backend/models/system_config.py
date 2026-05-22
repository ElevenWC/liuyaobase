"""系统配置表（key-value）"""
from typing import Optional
from sqlalchemy import TEXT
from sqlmodel import Field, SQLModel


class SystemConfig(SQLModel, table=True):
    __tablename__ = "system_config"
    config_key: str = Field(primary_key=True, max_length=50)
    config_value: Optional[str] = Field(default=None, sa_type=TEXT)
