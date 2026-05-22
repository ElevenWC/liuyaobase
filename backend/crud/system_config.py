"""系统配置表 CRUD — key-value 读写"""
from sqlmodel import Session, select
from backend.models.system_config import SystemConfig


def get_config(session: Session, key: str) -> str | None:
    """读取配置值，不存在则返回 None"""
    row = session.exec(
        select(SystemConfig).where(SystemConfig.config_key == key)
    ).first()
    return row.config_value if row else None


def set_config(session: Session, key: str, value: str):
    """写入配置值（INSERT 或 UPDATE）"""
    row = session.exec(
        select(SystemConfig).where(SystemConfig.config_key == key)
    ).first()
    if row:
        row.config_value = value
    else:
        session.add(SystemConfig(config_key=key, config_value=value))
    session.commit()
