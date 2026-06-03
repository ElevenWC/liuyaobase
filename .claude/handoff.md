# AI 接手提示词 — liuyaobase

> 新对话开始时粘贴以下内容给 AI，快速接手项目。2026-06-03 更新。

---

## 项目概况

- **名称**：liuyaobase（六爻数据库系统）
- **技术栈**：Python FastAPI + SQLModel + MySQL + Vue 3 + Vite + Pinia + Tiptap + lunar-python
- **仓库**：`ElevenWC/liuyaobase`，分支 `main`
- **数据库**：MySQL，localhost:3306，root/020508，库名 liuyao
- **前端端口**：5174（已从 5173 改过来，避免与其他应用冲突）
- **当前进度**：v0.0~v0.5 全部完成，v0.6 C4 股票关联为下一里程碑

---

## 工作流程

```
用户选 Issue → AI 读 .specs/ 规划文档 + .AIDiscuss/ 设计文档
  → 切分支 feat/issue-N → 写代码
  → 【必须】自审两遍再提交
  → 涉及数据库改表？→ 先跑 alembic revision --autogenerate + alembic upgrade head
  → commit + push（不创建 PR！）
  → 用户跑测试验收 → AI 创建 PR → squash merge → 删除本地+远程分支
```

**协作习惯**：需求有歧义时优先用 AskUserQuestion 确认，编码前先列 TodoWrite。

---

## 里程碑

| 里程碑 | 状态 |
|--------|:--:|
| v0.0 项目骨架+数据库 | ✅ |
| v0.1 核心算法层 | ✅ |
| v0.2 数据导入+预计算 | ✅ |
| v0.3 C1 卦例显示 | ✅ |
| v0.4 C3 复杂检索 | ✅ |
| v0.5 C2 解卦模块 | ✅ |
| v0.6 C4 股票关联 | 🔜 |

---

## 当前代码结构

### 前端共享组件 (frontend/src/components/shared/)

```
shared/
├── zCounter.js           # 全局 z-index 计数器（从 100 递增）
├── GuaCiFloat.vue        # 卦爻辞浮窗（可拖动，各模块共用）
├── CalendarFloat.vue     # 干支日历浮窗（拖动+翻页+节气标注）
├── NoteFloat.vue         # 浮动笔记（Tiptap编辑器+Markdown+多篇管理）
├── ZhanduanFloat.vue     # 占断内容浮窗（纯textarea+自动保存）
├── GuaLinkExtension.js   # Tiptap自定义Node——**数字**→#数字超链接
├── NetworkGraph.vue      # 纯SVG力导向网络图谱
├── SameYaoGroup.vue      # 同一爻条件组
├── SamePositionGroup.vue # 同爻位条件组
├── FeishenGroup.vue      # 飞神条件组
├── RecommendedSchemes.vue # 保存检索方案（localStorage）
├── FieldLibrary.vue      # 检索字段库面板
├── ConditionBuilder.vue  # 检索条件构建器核心
└── ResultList.vue        # 检索结果列表（分页+导出+批量操作）
```

### 后端关键模块

```
backend/
├── core/shensha.py       # 神煞计算（6神煞：干禄/驿马/羊刃/桃花/灾煞/劫煞）
├── core/time_converter.py # 干支节气计算（含 get_calendar_month）
├── services/sync_watcher.py # watchdog监控sync/文件夹自动导入
├── alembic/              # 数据库版本控制（初始版本 35f5f2ff8a03）
```

---

## 已完成的 Issue 和 PR（v0.4 及后续优化）

### v0.4 核心（11 个 Issue）

| Issue | 内容 |
|:--:|------|
| #96~#103 | C3 后端+前端基础组件 |
| #107 | Search.vue 检索主页面 + 条件组完整实现 |
| #105 | RecommendedSchemes.vue 自定义方案管理 |
| #118 | 数目判断（COUNT 子查询） |
| #120 | 逻辑链可视化编辑（AND/OR/NOT/括号） |
| #121 | 关系对象扩展（六神/状态/伏神飞神 + 来源选择） |
| #122 | 标签筛选 + 占问事由文本搜索 + 批量打标签 |
| #119 | 检索页右栏卦例查看——复用 GualiDetail.vue |

### 批量优化（PR #128~#132，2026-05-29~06-03）

| PR | 主要内容 |
|:--:|------|
| #128 | 导入去重（四层级联）、干支日历浮窗、C1批量查找/侧栏折叠/搜索增强、C3导出、八宫页卦名二级选择、GUA_CODES错码修复 |
| #129 | 编辑按钮一次保存+点击外部退出、运算符精简(→=和≠)、README完整编写、浮动笔记(Tiptap+Markdown语法) |
| #130 | 系统标签(占验情况+时间周期)、标签拖拽排序(sort_order列)、sync自动导入、C3全选交互统一 |
| #131 | 占断内容浮窗编辑(ZhanduanFloat) |
| #132 | 新增神煞灾煞+劫煞(日支三合局查表)、Alembic数据库版本控制、sync监控修复(on_moved+路径)、笔记拖拽排序、run.bat精简 |
| — | 前端端口5173→5174 |

### 已取消

| Issue | 内容 |
|:--:|------|
| #104 | CompareMode.vue（对比模式） |
| — | 条件组折叠/展开、字段库拖拽、scope 全部来源 |

---

## C3 检索条件总览

### 运算符（已精简为 2 个）

仅 `= (等于)` 和 `≠ (不等于)`。数目判断另有独立运算符集（含 > < ≥ ≤）。

### 神煞（当前 6 种）

干禄、驿马、羊刃、桃花、灾煞、劫煞。每种有 `是`/`带`/`是或带` 三种查询模式。后端 `SHENSHA_MAP` 在 search_service.py。前端 `SHENSHA_TYPES` 在 ConditionBuilder.vue。

**新增神煞操作指南**：`.user/新增神煞操作指南.md`，包含 10 个文件修改步骤、5 个踩坑记录。

---

## 关键注意事项

### 数据库版本控制（Alembic）

已配置在 `backend/alembic/`。改模型后：
```bash
cd backend
../venv/Scripts/alembic revision --autogenerate -m "描述"  # 生成
../venv/Scripts/alembic upgrade head                        # 执行
```
初始版本 `35f5f2ff8a03`，其 downgrade 切勿执行（会删库）。

### Sync 自动导入

`backend/services/sync_watcher.py` 监控项目根目录下的 `sync/` 文件夹。需同时监听 `on_created` 和 `on_moved`（Syncthing 用原子重命名）。`SYNC_DIR` 路径是 `parent.parent.parent`（3 级）。

### GUA_CODES 错码

核心公式：`hexagram_code = outer_trigram + inner_trigram`。三处曾含错码的文件已修复：`GualiInput.vue`（CODES）、`BagongPage.vue`（GUA_CODES）。

### ShallowRef 陷阱

`useEditor` 返回 ShallowRef，不能用 `watch` 监听内部变化。Tiptap 编辑器内容保存必须用 `onUpdate` 回调。

### 导入去重

四层级联：`SELECT WHERE zhanwen_shiyou = :v`（前缀索引 `idx_zhanwen_shiyou(100)`）→ Python 过滤 time/ben_code/zhi_code。

### 标签排序

tag 表有 `sort_order` 列。`_build_tree` 按此列排序。`POST /tags/reorder` 更新顺序。

### 系统标签

`tag.is_system = TRUE`。两种：占验情况（含 C1/C3 独立选择器）+ 时间周期。TagManager 显示灰色不可删。新部署 `init_db.py` 自动创建。

### 前端端口

已改为 `5174`（vite.config.js + run.bat + README）。

---

## 启动命令

```bash
# 一键
run.bat
# 或分别启动：
venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
cd frontend && npm run dev
```

---

## 文件索引

| 想看什么 | 文件 |
|---------|------|
| 项目协作规范 | `CLAUDE.md` |
| 设计文档 | `.AIDiscuss/`（.A1 .A2 .B .C1~.C4 .C31 .C32 .C33 .C33-1 .Z） |
| 规划文档 | `.specs/`（7 个里程碑） |
| v0.4 规划 | `.specs/v0.4C3复杂检索/` |
| v0.6 规划 | `.specs/v0.6C4股票关联/` |
| 新增神煞指南 | `.user/新增神煞操作指南.md` |
| C3 检索字段指南 | `.user/C3检索字段使用指南.md` |
| Alembic 工作流 | `memory/alembic_workflow.md` |
| README | `README.md`（面向用户的功能介绍） |

---

## v0.6 C4 股票关联 — 前置待办

v0.4 收尾检查结果：**无遗留占位**。v0.6 规划文档位于 `.specs/v0.6C4股票关联/`，7 个规划单元（06.1~06.13）。

| 单元 | 内容 | 标记 |
|------|------|:--:|
| 06.1~06.4 | 后端 CRUD + Models + Schemas | — |
| 06.5 | stock_data_service.py（AKShare 数据拉取） | ★ |
| 06.6 | market_service.py（行情预计算） | ★★ |
| 06.7~06.9 | 后端 API routers + schemas | — |
| 06.10 | StockAnalysis.vue（股票分析主页） | ★ |
| 06.11 | KlineChart.vue（K线图，ECharts） | ★★ |
| 06.12~06.13 | IntradayChart + 关联卦例浮窗 | — |
