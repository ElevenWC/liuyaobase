"""卦例请求/响应 Schema"""
from datetime import datetime
from typing import Optional
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


class YaoItemSchema(BaseModel):
    """单爻信息（guali_yao 表全部 20 字段）"""
    yao_position: int
    liushen: Optional[str] = ""
    yimao_liuqin: Optional[str] = ""
    yimao_dizhi: Optional[str] = ""
    zengshan_exists: bool = False
    zengshan_liuqin: Optional[str] = ""
    zengshan_dizhi: Optional[str] = ""
    ben_yao_type: Optional[str] = ""
    ben_liuqin: Optional[str] = ""
    ben_tiangan: Optional[str] = ""
    ben_dizhi: Optional[str] = ""
    ben_shi_ying: Optional[str] = ""
    is_dong: bool = False
    is_an_dong: bool = False
    zhi_yao_type: Optional[str] = ""
    zhi_liuqin: Optional[str] = ""
    zhi_tiangan: Optional[str] = ""
    zhi_dizhi: Optional[str] = ""
    zhi_shi_ying: Optional[str] = ""


class GualiListResponse(BaseModel):
    """列表卡片（不含 zhanduan 全文）"""
    id: int
    zhanwen_time: datetime
    zhanwen_shiyou: Optional[str] = None
    ben_code: str
    tags: list[str] = []


class GualiDetailResponse(BaseModel):
    """详情（5 表拼装）"""
    id: int
    zhanwen_time: datetime
    zhanwen_shiyou: Optional[str] = None
    zhanduan: Optional[str] = None
    ben_code: str
    yao_bian_code: str
    zhi_code: str
    # guali_time
    year_pillar: Optional[str] = None
    year_gan: Optional[str] = None
    year_zhi: Optional[str] = None
    month_pillar: Optional[str] = None
    month_gan: Optional[str] = None
    month_zhi: Optional[str] = None
    day_pillar: Optional[str] = None
    day_gan: Optional[str] = None
    day_zhi: Optional[str] = None
    xun_kong: Optional[str] = None
    # guali_shensha
    gan_lu: Optional[str] = None
    yi_ma: Optional[str] = None
    yang_ren: Optional[str] = None
    tao_hua: Optional[str] = None
    zai_sha: Optional[str] = None
    jie_sha: Optional[str] = None
    # guali_gua
    ben_palace: Optional[str] = None
    ben_palace_type: Optional[str] = None
    ben_special_type: Optional[str] = None
    zhi_palace: Optional[str] = None
    zhi_palace_type: Optional[str] = None
    zhi_special_type: Optional[str] = None
    fan_yin_yimao: Optional[str] = None
    fan_yin_yaobian: Optional[str] = None
    fu_yin: Optional[str] = None
    # guali_yao
    yaos: list[YaoItemSchema] = []
    # 标签
    tags: list[str] = []


class GualiUpdateRequest(BaseModel):
    """更新请求——仅允许修改事由和占断"""
    zhanwen_shiyou: Optional[str] = None
    zhanduan: Optional[str] = None


class GualiBatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int]


class GualiTagRequest(BaseModel):
    """标签关联请求"""
    tag_id: int
