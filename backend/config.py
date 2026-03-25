"""
六爻卦例分析系统 - 配置模块
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
import os


# 计算.env文件路径
_BACKEND_ENV = os.path.join(os.path.dirname(__file__), ".env")
_ROOT_ENV = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
_ENV_FILE = _BACKEND_ENV if os.path.exists(_BACKEND_ENV) else _ROOT_ENV


class Settings(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 应用信息
    app_name: str = Field(default="六爻卦例分析系统", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")

    # 数据库配置
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    db_name: str = Field(default="liuyao", alias="DB_NAME")

    # 图片存储配置
    image_storage_path: str = Field(default="./images", alias="IMAGE_STORAGE_PATH")
    image_allowed_extensions: str = Field(default="jpg,jpeg,png,gif,bmp", alias="IMAGE_ALLOWED_EXTENSIONS")
    image_max_size: int = Field(default=10 * 1024 * 1024, alias="IMAGE_MAX_SIZE")  # 10MB

    # 服务器配置
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def async_database_url(self) -> str:
        """获取异步数据库连接URL"""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def image_extensions_list(self) -> List[str]:
        """获取允许的图片扩展名列表"""
        return [ext.strip().lower() for ext in self.image_allowed_extensions.split(',')]

    @property
    def image_storage_absolute_path(self) -> str:
        """获取图片存储的绝对路径"""
        if os.path.isabs(self.image_storage_path):
            return self.image_storage_path
        return os.path.abspath(self.image_storage_path)

    def ensure_image_directory(self) -> str:
        """
        确保图片存储目录存在

        Returns:
            图片存储目录的绝对路径
        """
        abs_path = self.image_storage_absolute_path
        if not os.path.exists(abs_path):
            os.makedirs(abs_path, exist_ok=True)
        return abs_path


# 全局配置实例
settings = Settings()
