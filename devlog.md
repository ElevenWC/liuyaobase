# 六爻卦例分析系统 - 开发日志

## 当前状态

**更新时间**: 2026-02-27

**总测试数**: 800
**通过率**: 100%
**跳过数**: 1
**执行时间**: 2.85秒
**前端构建**: 成功

### 已完成阶段

| 阶段 | 名称 | 状态 | 文档 |
|------|------|------|------|
| 阶段零 | 环境准备 | ✓ | [phase-0.md](./devlog/phase-0.md) |
| 阶段1-4 | 枚举/业务类/时间/纳甲 | ✓ | [phase-1-4.md](./devlog/phase-1-4.md) |
| 阶段5-8 | 六亲/六神/世应/伏神 | ✓ | [phase-5-8.md](./devlog/phase-5-8.md) |
| 阶段9-11 | 反吟伏吟/神煞/生旺墓绝 | ✓ | [phase-9-11.md](./devlog/phase-9-11.md) |
| 阶段12-13 | Guali整合/数据库 | ✓ | [phase-12-13.md](./devlog/phase-12-13.md) |
| 阶段14 | 数据库CRUD操作 | ✓ | [phase-14.md](./devlog/phase-14.md) |
| 阶段15 | 格式转换模块 | ✓ | [phase-15.md](./devlog/phase-15.md) |
| 阶段16 | FastAPI基础 | ✓ | [phase-16.md](./devlog/phase-16.md) |
| 阶段17-18 | 卦例API及详情接口 | ✓ | [phase-17-18.md](./devlog/phase-17-18.md) |
| 阶段19-20 | CSV导入与图片存储 | ✓ | [phase-19-20.md](./devlog/phase-19-20.md) |
| 阶段21-22 | 前端基础页面与卦例输入 | ✓ | [phase-21-22.md](./devlog/phase-21-22.md) |
| 阶段23-25 | 前端功能完善 | ✓ | [phase-23-25.md](./devlog/phase-23-25.md) |
| 阶段26-27 | 复杂检索功能 | ✓ | [phase-26-27.md](./devlog/phase-26-27.md) |
| 阶段28 | ECharts集成 | ✓ | [phase-28.md](./devlog/phase-28.md) |
| 阶段29-30 | 占验情况/多窗检索 | ✓ | [bugs.md](./devlog/bugs.md) |
| 阶段31 | 集成测试 | ✓ | [phase-31.md](./devlog/phase-31.md) |
| 阶段32 | 代码审查与测试 | ✓ | [phase-32.md](./devlog/phase-32.md) |
| 阶段33 | Bug修复与功能完善 | ✓ | [phase-33.md](./devlog/phase-33.md) |
| 阶段34 | 多卦例支持与占断编辑 | ✓ | 见下方日志 |

**Bug记录**: [bugs.md](./devlog/bugs.md)

---

## 项目结构

### 后端目录结构

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py               # FastAPI应用入口
│   ├── schemas.py            # Pydantic模型
│   └── routers/
│       ├── __init__.py
│       ├── guali.py          # 卦例API路由
│       ├── images.py         # 图片API路由
│       └── search.py         # 复杂检索API
├── core/
│   ├── enums.py              # 核心枚举
│   ├── models.py             # 业务类
│   ├── time_converter.py     # 时间转换
│   ├── nama.py               # 纳甲装卦
│   ├── wuxing_helper.py      # 五行辅助
│   ├── liushen.py            # 六神计算
│   ├── shiying.py            # 世应定位
│   ├── fushen.py             # 伏神计算
│   ├── fanyin_fuyin.py       # 反吟伏吟
│   ├── shensha.py            # 神煞计算
│   ├── shengwang_mujue.py    # 生旺墓绝
│   └── converter.py          # 格式转换
├── db/
│   ├── connection.py
│   ├── models.py             # SQLAlchemy模型
│   └── repositories.py       # 数据仓库CRUD
├── services/
│   └── yanqing_service.py    # 占验情况服务
├── utils/
│   └── validators.py         # CSV验证
├── config.py                 # 配置模块
└── tests/                    # 测试文件
```

### 前端目录结构

```
frontend/
├── src/
│   ├── api/
│   │   └── index.js           # API调用模块
│   ├── components/
│   │   ├── NavBar.vue         # 导航菜单组件
│   │   └── Search/            # 复杂检索组件
│   │       ├── FieldLibrary.vue
│   │       ├── ConditionBuilder.vue
│   │       ├── RecommendedSchemes.vue
│   │       ├── ResultList.vue
│   │       └── WindowManager.vue
│   ├── router/
│   │   └── index.js           # 路由配置
│   ├── stores/
│   │   └── index.js           # Pinia状态管理
│   ├── views/
│   │   ├── Home.vue           # 首页
│   │   ├── GualiInput.vue     # 卦例录入
│   │   ├── CsvImport.vue      # CSV导入
│   │   ├── GualiList.vue      # 卦例列表
│   │   ├── GualiDetail.vue    # 卦例详情
│   │   ├── Search.vue         # 复杂检索
│   │   ├── ImageConfig.vue    # 图片配置
│   │   └── NotFound.vue       # 404页面
│   ├── App.vue
│   ├── main.js
│   └── style.css
├── vite.config.js
└── package.json
```

---

## API接口列表

```
# 卦例管理
POST   /api/guali              - 创建卦例
GET    /api/guali              - 获取卦例列表（分页）
GET    /api/guali?year=2024    - 按年份筛选
GET    /api/guali/{id}         - 获取单个卦例
PUT    /api/guali/{id}         - 更新卦例
DELETE /api/guali/{id}         - 删除卦例
GET    /api/guali/{id}/detail  - 获取卦例完整详情
POST   /api/guali/import-csv   - CSV批量导入卦例

# 图片管理
GET    /api/images/config      - 获取图片存储配置
POST   /api/images/upload      - 上传图片
GET    /api/images             - 获取图片列表
GET    /api/images/{filename}  - 访问图片
DELETE /api/images/{filename}  - 删除图片

# 复杂检索
POST   /api/search             - 复杂检索接口
GET    /api/search/fields      - 获取可检索字段列表

# 系统状态
GET    /api/health             - 健康检查
```

---

## 下一步工作

| 序号 | 任务 | 状态 |
|------|------|------|
| 1 | 配置MySQL数据库 | ✓ |
| 2 | 完成FastAPI基础 | ✓ |
| 3 | 完成API接口开发（阶段17-18） | ✓ |
| 4 | CSV导入功能（阶段19） | ✓ |
| 5 | 图片存储功能（阶段20） | ✓ |
| 6 | 开发前端基础界面（阶段21-22） | ✓ |
| 7 | 完善前端功能（阶段23-25） | ✓ |
| 8 | 实现复杂检索功能（阶段26-27） | ✓ |
| 9 | ECharts集成（阶段28） | ✓ |
| 10 | 占验情况系统（阶段29） | ✓ |
| 11 | 多窗检索功能（阶段30） | ✓ |
| 12 | 集成测试（阶段31） | ✓ |
| 13 | 代码审查与测试（阶段32） | ✓ |
| 14 | Bug修复与功能完善（阶段33） | ✓ |

### 待完善功能

| 序号 | 任务 | 优先级 |
|------|------|--------|
| 1 | 飞神伏神关系查询完整实现 | 中 |
| 2 | 前端复杂检索界面关系运算符支持 | 中 |
| 3 | 检索API更完整测试覆盖 | 低 |

---

## 快速命令

```bash
# 运行后端测试
pytest backend/tests/ --ignore=backend/tests/test_connection.py -v

# 启动后端
cd backend && python -m uvicorn api.main:app --reload --port 8000

# 启动前端
cd frontend && npm run dev

# 构建前端
cd frontend && npm run build

# 初始化数据库
python scripts/init_db.py

# API文档
# http://localhost:8000/docs

# 前端访问
# http://localhost:5173
```

---

## 阶段三十四：多卦例支持与占断编辑

**更新时间**: 2026-02-27

### 功能需求

1. **多卦例支持**：一根K线可能对应多个卦例，需要显示所有卦例，由用户选择基准卦例决定K线颜色
2. **占断编辑**：在卦例详情页、卦例浮窗等位置支持编辑占断字段

### 任务完成情况

| 任务 | 内容 | 状态 |
|------|------|------|
| 34.1 | 后端guali-mapping接口返回多卦例结构 | ✓ |
| 34.2 | GualiFloatPanel支持多卦例显示 | ✓ |
| 34.3 | GualiFloatPanel支持占断编辑 | ✓ |
| 34.4 | KlineChart支持多卦例数据结构 | ✓ |
| 34.5 | StockAnalysis处理多卦例事件 | ✓ |
| 34.6 | 更新Plan.md文档 | ✓ |

### 修改文件

#### 后端
- `backend/api/routers/stock.py`
  - 修改 `get_guali_mapping` 接口，返回按日期分组的多卦例数据结构
  - 每个日期组包含 `gualis` 数组、`primary_guali_id`、`yanqing_status`

#### 前端
- `frontend/src/components/Stock/GualiFloatPanel.vue`
  - 支持显示多个卦例
  - 添加基准卦例选择功能
  - 添加占断字段编辑功能
  - 其他卦例在折叠面板中展示

- `frontend/src/components/Stock/KlineChart.vue`
  - 修改 `getKlineStyle` 函数支持新的数据结构
  - 修改双击事件传递 `gualiGroup` 而非单个 `guali`
  - 修改 tooltip 显示多卦例信息

- `frontend/src/views/StockAnalysis.vue`
  - 修改数据结构处理多卦例
  - 添加 `handlePrimaryChanged` 方法处理基准卦例变更
  - 添加 `handleZhanDuanUpdated` 方法处理占断更新

### 数据结构设计

```javascript
// 新的卦例映射数据结构
{
  "2024-01-15": {
    "date": "2024-01-15",
    "gualis": [
      {
        "id": 1,
        "zhan_wen": "占问股票走势",
        "zhan_duan": "占断上涨",
        "ben_gua_name": "乾为天",
        "yanqing_status": "应验"
      }
    ],
    "primary_guali_id": 1,
    "yanqing_status": "应验"
  }
}
```

### 新增功能说明

#### 1. 多卦例显示
- 当一根K线对应多个卦例时，浮窗顶部显示提示信息和选择框
- 用户可通过下拉框选择基准卦例
- 其他卦例在可展开的折叠面板中显示

#### 2. 基准卦例选择
- 用户选择的基准卦例决定该日期K线的颜色
- 支持在其他卦例的操作按钮中快速设为基准

#### 3. 占断编辑
- 主卦例的占断可直接编辑
- 其他卦例的占断也可在折叠面板中编辑
- 编辑后自动保存并更新本地状态

### 测试情况

- 后端测试：800 passed, 1 skipped
- 前端构建：成功