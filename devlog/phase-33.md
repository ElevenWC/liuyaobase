# 阶段三十三：Bug修复与功能完善

**更新时间**: 2026-02-25

## 任务概述

修复已发现的警告和bug，完善检索API的待实现功能。

## 修复的Bug

### Bug 1: FastAPI on_event 弃用警告

**位置**: `backend/api/main.py`

**问题**:
```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead
```

**修复前**:
```python
@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")

@app.on_event("shutdown")
async def shutdown_event():
    print(f"👋 {settings.app_name} 已关闭")
```

**修复后**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    print(f"📁 图片存储路径: {settings.image_storage_path}")
    yield
    # Shutdown
    print(f"👋 {settings.app_name} 已关闭")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="六爻卦例的录入、存储、查看和复杂检索系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)
```

**状态**: ✓ 已修复

### Bug 2: StockAnalysis.vue 股票搜索函数绑定错误

**位置**: `frontend/src/views/StockAnalysis.vue:7`

**问题**:
`el-autocomplete` 的 `fetch-suggestions` 属性直接绑定了 Promise 类型的 `searchStock` 函数，而该属性需要回调类型的函数。

**修复前**:
```vue
<el-autocomplete
  v-model="searchKeyword"
  :fetch-suggestions="searchStock"
  ...
>
```

**修复后**:
```vue
<el-autocomplete
  v-model="searchKeyword"
  :fetch-suggestions="searchStockImpl"
  ...
>
```

**影响**: 股票搜索功能无法正常工作

**状态**: ✓ 已修复

## 完善的功能

### 功能 1: 检索API神煞查询

**位置**: `backend/api/routers/search.py`

**函数**: `build_shensha_condition(condition, session)`

**实现逻辑**:
1. 根据神煞类型（干禄/驿马/羊刃/桃花）确定计算基准（日干或日支）
2. 对于每种日干/日支，计算对应的神煞地支
3. 如果查询"是神煞"，只匹配神煞地支本身
4. 如果查询"带神煞"，匹配神煞地支及其相合、相冲的地支
5. 构建SQL子查询进行匹配

**使用示例**:
```json
{
  "field": "ganlu",
  "operator": "=",
  "value": "is"  // 或 "dai"
}
```

**状态**: ✓ 已完成

### 功能 2: 检索API关系条件

**位置**: `backend/api/routers/search.py`

**函数**: `build_relation_condition(source_field, relation_type, target_field, session)`

**实现逻辑**:
1. 解析源字段（如 `world_yao.dizhi`）
2. 根据关系类型（he/chong/sheng/ke）获取对应的关系映射
3. 构建SQL子查询匹配爻地支与日支的关系

**使用示例**:
```json
{
  "field": "world_yao.dizhi",
  "operator": "与",
  "relation_type": "he",
  "target_field": "day_dizhi"
}
```

**状态**: ✓ 已完成

### 功能 3: 伏神飞神/反吟伏吟查询

**位置**: `backend/api/routers/search.py`

**函数**: `build_special_condition(condition, session)`

**伏神飞神查询**:
- `has_fushen`: 查询六亲不全的卦例（通过子查询计算六亲数量）

**反吟伏吟查询**:
- `yimao_fanyin`: 易冒反吟（乾巽、坎离、艮坤、震兑互变）
- `yaobian_fanyin`: 爻变反吟（坤巽互变）
- `fuyin`: 伏吟（乾震互变）

**实现逻辑**:
- 通过本卦和之卦的内卦/外卦代码判断是否符合反吟伏吟关系
- 使用SQL位运算提取内卦/外卦代码

**使用示例**:
```json
{
  "field": "fanyin_fuyin",
  "operator": "=",
  "value": "yimao_fanyin"
}
```

**状态**: ✓ 已完成

## 测试结果

**语法检查**:
- backend/api/main.py: ✓
- backend/api/routers/search.py: ✓

**导入测试**:
- Search router: ✓
- Main app: ✓

## 修改的文件

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| backend/api/main.py | 重构 | 迁移到lifespan事件处理器 |
| backend/api/routers/search.py | 完善 | 实现神煞、关系、特殊条件查询 |
| frontend/src/views/StockAnalysis.vue | 修复 | 修正股票搜索函数绑定 |

## 待后续完善

1. 飞神伏神关系查询（飞克伏、伏克飞、飞生伏、伏生飞）的完整实现
2. 检索API的更完整测试覆盖
3. 前端复杂检索界面的关系运算符支持

## 结论

本次修复解决了所有已知的警告和关键bug，完善了检索API的核心功能。代码质量得到提升，功能更加完整。
