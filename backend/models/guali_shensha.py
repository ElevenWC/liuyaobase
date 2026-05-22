"""神煞扩展表 — 1行/卦例，37字段"""
from typing import Optional
from sqlmodel import Field, SQLModel


class GualiShensha(SQLModel, table=True):
    __tablename__ = "guali_shensha"
    id: Optional[int] = Field(default=None, primary_key=True)
    guali_id: int = Field(foreign_key="guali.id")

    # 神煞地支（4个）
    gan_lu: Optional[str] = Field(default=None, max_length=2)
    yi_ma: Optional[str] = Field(default=None, max_length=2)
    yang_ren: Optional[str] = Field(default=None, max_length=2)
    tao_hua: Optional[str] = Field(default=None, max_length=2)

    # 易冒伏神-神煞状态（8个）
    yimao_is_ganlu: str = Field(default="", max_length=10)
    yimao_dai_ganlu: str = Field(default="", max_length=10)
    yimao_is_yima: str = Field(default="", max_length=10)
    yimao_dai_yima: str = Field(default="", max_length=10)
    yimao_is_yangren: str = Field(default="", max_length=10)
    yimao_dai_yangren: str = Field(default="", max_length=10)
    yimao_is_taohua: str = Field(default="", max_length=10)
    yimao_dai_taohua: str = Field(default="", max_length=10)

    # 增删伏神-神煞状态（8个）
    zengshan_is_ganlu: str = Field(default="", max_length=10)
    zengshan_dai_ganlu: str = Field(default="", max_length=10)
    zengshan_is_yima: str = Field(default="", max_length=10)
    zengshan_dai_yima: str = Field(default="", max_length=10)
    zengshan_is_yangren: str = Field(default="", max_length=10)
    zengshan_dai_yangren: str = Field(default="", max_length=10)
    zengshan_is_taohua: str = Field(default="", max_length=10)
    zengshan_dai_taohua: str = Field(default="", max_length=10)

    # 本卦-神煞状态（8个）
    ben_is_ganlu: str = Field(default="", max_length=10)
    ben_dai_ganlu: str = Field(default="", max_length=10)
    ben_is_yima: str = Field(default="", max_length=10)
    ben_dai_yima: str = Field(default="", max_length=10)
    ben_is_yangren: str = Field(default="", max_length=10)
    ben_dai_yangren: str = Field(default="", max_length=10)
    ben_is_taohua: str = Field(default="", max_length=10)
    ben_dai_taohua: str = Field(default="", max_length=10)

    # 之卦-神煞状态（8个）
    zhi_is_ganlu: str = Field(default="", max_length=10)
    zhi_dai_ganlu: str = Field(default="", max_length=10)
    zhi_is_yima: str = Field(default="", max_length=10)
    zhi_dai_yima: str = Field(default="", max_length=10)
    zhi_is_yangren: str = Field(default="", max_length=10)
    zhi_dai_yangren: str = Field(default="", max_length=10)
    zhi_is_taohua: str = Field(default="", max_length=10)
    zhi_dai_taohua: str = Field(default="", max_length=10)
