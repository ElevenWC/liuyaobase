# 阶段零：环境准备与项目初始化

**完成时间**: 2026-02-18

---

## 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 0.1 后端项目结构创建 | ✓ | 目录和__init__.py |
| 0.2 前端项目初始化 | ✓ | README说明 |
| 0.3 后端依赖安装与配置 | ✓ | requirements.txt |
| 0.4 数据库连接配置 | ✓ | connection.py |

---

## 创建的目录结构

```
backend/
├── __init__.py
├── api/           # API接口层
├── core/          # 核心业务逻辑层
├── db/            # 数据访问层
├── services/      # 服务层
├── utils/         # 工具类
├── tests/         # 测试文件
└── scripts/       # 脚本文件
docs/              # 文档
images/            # 图片存储
```

---

## 依赖列表 (requirements.txt)

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pymysql==1.1.0
aiomysql==0.2.0
pydantic==2.5.3
pydantic-settings==2.1.0
lunar-python==1.3.6
python-dotenv==1.0.0
python-multipart==0.0.6
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

---

## 数据库表结构

1. `guali` - 卦例表（主表）
2. `yao_detail` - 爻详情表
3. `yanqing` - 占验情况表

---

## 启动命令

```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 初始化前端
npm create vite@latest frontend -- --template vue
cd frontend && npm install element-plus pinia vue-router@4 axios echarts vue-echarts

# 配置数据库
cp backend/.env.example backend/.env
# 编辑.env填写数据库信息

# 初始化数据库
python scripts/init_db.py

# 启动后端
cd backend && python -m uvicorn api.main:app --reload --port 8000
```
