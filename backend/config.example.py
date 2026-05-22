"""
六爻数据库系统 — 配置模板
复制为 config.py 后填入真实值，或通过环境变量设置。
"""
import os

# 数据库
DATABASE_HOST = os.environ.get("LIUYAO_DB_HOST", "localhost")
DATABASE_PORT = int(os.environ.get("LIUYAO_DB_PORT", "3306"))
DATABASE_USER = os.environ.get("LIUYAO_DB_USER", "root")
DATABASE_PASSWORD = os.environ.get("LIUYAO_DB_PASSWORD", "your_password_here")
DATABASE_NAME = os.environ.get("LIUYAO_DB_NAME", "liuyao")
DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# 服务
SERVER_HOST = os.environ.get("LIUYAO_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("LIUYAO_SERVER_PORT", "8001"))

# AKShare
AKSHARE_RATE_LIMIT = float(os.environ.get("LIUYAO_AKSHARE_RATE_LIMIT", "0.5"))
AKSHARE_TIMEOUT = int(os.environ.get("LIUYAO_AKSHARE_TIMEOUT", "30"))
