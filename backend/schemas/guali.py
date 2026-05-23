"""卦例请求/响应 Schema（v0.2 最小版，v0.3 扩充）"""
from datetime import datetime
from pydantic import BaseModel


class ManualImportSchema(BaseModel):
    """手动导入单个卦例"""
    zhanwen_time: datetime
    zhanwen_shiyou: str
    zhanduan: str = ""
    ben_code: str | None = None
    ben_name: str | None = None
    zhi_code: str | None = None
    zhi_name: str | None = None
