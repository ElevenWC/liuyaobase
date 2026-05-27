# AI 接手提示词 — liuyaobase

> 新对话开始时粘贴以下内容给 AI，快速接手项目。

---

## 项目概况

- **名称**：liuyaobase（六爻数据库系统）
- **技术栈**：Python FastAPI + SQLModel + MySQL + Vue 3 + Vite + Pinia + lunar-python
- **仓库**：`ElevenWC/liuyaobase`，分支 `main`
- **数据库**：MySQL，localhost:3306，root/020508，库名 liuyao
- **当前进度**：v0.0 ~ v0.3 全部完成（48 Issue），v0.5 全部完成（5 Issue），v0.4 进行中（8/11 Issue 完成）

---

## 工作流程

```
用户选 Issue → AI 读 .specs/ 规划文档 + .AIDiscuss/ 设计文档
  → 先切分支 feat/issue-N → 写代码
  → 【必须】自审两遍再提交：
      第一遍：对照规划文档 §7 陷阱 + §9 审查清单
      第二遍：逐行模拟运行时路径，检查边界/空值/参数绑定/安全
  → 跑测试命令 → commit + push（不创建 PR！）
  → 用户跑测试验收 → AI 创建 PR → squash merge → 删除本地+远程分支
  → merge 后必查：Issue 是否关闭 / 分支是否删除 / git status 干净
```

---

## 里程碑完成情况

| 里程碑 | Issue 数 | 状态 |
|--------|:------:|:--:|
| v0.0 项目骨架+数据库 | 9 | ✅ |
| v0.1 核心算法层 | 15 | ✅ |
| v0.2 数据导入+预计算 | 8 | ✅ |
| v0.3 C1 卦例显示 | 16 | ✅ |
| v0.4 C3 复杂检索 | 11 | 🔄 8/11 完成（#96–#103） |
| v0.5 C2 解卦模块 | 5 | ✅ |
| v0.6 C4 股票关联 | — | 🔜 |

---

## v0.4 当前状态（接手后继续 #107）

### 已完成（#96–#103）

| Issue | 内容 | 分支 |
|:--:|------|------|
| #96 | backend/schemas/search.py | 已合并 |
| #97 | backend/services/search_service.py（动态 SQL 引擎） | 已合并 |
| #98 | backend/services/export_service.py（导出）+ condition_group_ref 实现 | 已合并 |
| #99 | backend/api/routers/search.py（检索 API） | 已合并 |
| #100 | frontend/stores/useSearchStore.js（Pinia 检索状态 + localStorage 方案） | 已合并 |
| #101 | frontend/components/Search/ConditionBuilder.vue（条件构建器） | 已合并 |
| #102 | frontend/components/Search/FieldLibrary.vue（字段库面板） | 已合并 |
| #103 | frontend/components/Search/ResultList.vue（结果列表） | 已合并 |

### 待完成

| Issue | 内容 | 优先级 |
|:--:|------|:--:|
| ~~#107~~ | ~~frontend/views/Search.vue（检索主页面）~~ | ✅ 已完成 |
| ~~#104~~ | ~~CompareMode.vue（对比模式）~~ | ❌ 已取消 |
| #105 | RecommendedSchemes.vue（自定义方案管理——仅 localStorage） | P2 |

### v0.4 后续迭代待办（首版简化的功能）

1. 逻辑链可视化 AND/OR/NOT 编辑
2. scope=null 全部来源
3. 字段库拖拽交互
4. 条件组折叠/展开
5. _assemble_logic 静默错误改为抛异常

### v0.4 代码审核发现（2026-05-26 两遍制审核）

#### BUG（需修复）

| # | 文件 | 问题 | 严重度 |
|:--:|------|------|:--:|
| B1 | search_service.py:253-254 | condition_group_ref 子查询中引用含神煞字段(s.)的条件时，子查询未 JOIN guali_shensha 表，SQL 报错 | 中 |

**B1 详述**：`_build_relation_clause` 的 `resolve_dz` 函数在解析 `condition_group_ref` 时，会创建一个只 JOIN guali_yao 的子查询，并用字符串替换将 `y.` 换为新的表别名。但如果被引用的条件包含神煞字段（如 `s.ben_is_ganlu`），该 `s.` 引用在子查询中无效——因为子查询中没有 JOIN guali_shensha。触发条件：关系条件的右对象引用了一个包含神煞判断的条件组。

#### 设计偏离（与规划文档不一致）

| # | 文件 | 规划要求 | 当前实现 | 影响 |
|:--:|------|---------|---------|:--:|
| D1 | export_service.py:27 | §6 陷阱：大数据量时"CSV 流式写出，避免全量加载到内存" | page_size=99999 一次性取全量写入 | 数据量上千条时内存占用高 |
| D2 | search.py (router):14 | §6 陷阱：检索超时 10s，超时返回提示 | 无超时控制 | 复杂查询可能超时无反馈 |
| D3 | ConditionBuilder.vue | §6 陷阱：选了来源"变爻"→字段下拉应只显示变爻支持的字段（联动过滤） | scope 选择器和 field 选择器独立，无联动过滤 | 用户可能选了不兼容的字段/来源组合 |
| D4 | FieldLibrary.vue | §6 陷阱：某些字段只在特定来源下可用→标灰色提示 | 无灰色提示 | 用户可能选了不可用的字段 |
| D5 | ConditionBuilder.vue | §4 交互：神煞条件模板（[对象][是/带/是或带][神煞]） | 神煞只在 FieldLibrary 中以独立字段形式出现，ConditionBuilder 无神煞专用模板 | 神煞条件需通过 FieldLibrary 点击添加，不能在 ConditionBuilder 直接构建 |
| D6 | _assemble_logic | §7 陷阱：逻辑链深嵌套保护最多5层括号 | 无括号深度校验 | 恶意输入可导致深层嵌套 |

#### 已确认合理的设计简化

以下与设计文档有差异，但属于首版合理简化，无需立即修复：

- 条件组折叠/展开 → 已列入后续迭代待办 #4
- 字段库拖拽交互 → 已列入后续迭代待办 #3
- 逻辑链可视化编辑 → 已列入后续迭代待办 #1

---

## 当前代码结构

```
backend/
├── main.py, config.py, requirements.txt
├── core/          # 14 个算法文件
├── crud/          # 11 个 CRUD 文件
├── services/      # 6 个服务文件（新增 search_service / export_service）
├── models/        # 18 个 SQLModel 表定义
├── schemas/       # guali.py + tag.py + search.py（新增）
├── api/routers/   # guali / tags / import_data / jiegua / bagong / search（新增）
├── db/            # connection / init_db / stored_functions/
├── exports/       # 检索导出临时文件
└── tests/         # 12 个测试文件
frontend/src/
├── api/index.js        # axios 封装（24 个 API 函数）
├── stores/
│   ├── index.js        # Pinia 全局状态（C1）
│   └── useSearchStore.js  # Pinia 检索状态（C3，新增）
├── router/index.js     # 路由（/guali /jiegua/bagong /jiegua/hugua /jiegua/graph /input /import /tags /search）
├── style.css           # CSS 变量系统
├── views/
│   ├── Home.vue        # C1 左右分栏主布局
│   ├── GualiList.vue   # 左侧列表
│   ├── GualiDetail.vue # 右侧详情（含解卦双按钮：八宫/互卦）
│   ├── GualiInput.vue  # 手动导入
│   ├── ImportJson.vue  # JSON 批量导入
│   ├── TagManager.vue  # 标签管理
│   ├── BagongPage.vue  # C2 八宫变化页面（4行布局+图谱小窗）
│   ├── HuguaPage.vue   # C2 互卦页面（双列+爻位高亮）
│   └── GraphPage.vue   # C2 网络图谱全屏
└── components/
    ├── NavBar.vue           # 导航栏（解卦下拉：八宫/互卦/图谱）
    ├── shared/
    │   ├── GuaCiFloat.vue    # 卦爻辞浮窗（共享，爻辞结构化渲染）
    │   └── NetworkGraph.vue  # SVG 力导向图谱（共享，供 C2/C4 复用）
    └── Search/               # C3 检索组件（新增）
        ├── ConditionBuilder.vue
        ├── FieldLibrary.vue
        └── ResultList.vue
```

---

## 关键技术决策

- **CSS 变量系统**：全部颜色/圆角/阴影/间距定义在 `style.css` 的 `:root {}`，组件禁止裸色值
- **深色主题**：`#0F172A` 底 + `#1E293B` 卡片 + `#6366F1` 靛蓝品牌色
- **标签颜色**：8 色卡，按一级标签 ID 取模，刷新稳定
- **标签两级筛选**：一级选父标签→自动包含子标签卦例；打二级标签自动去一级关联
- **之卦六亲**：用本卦卦宫五行计算（不是之卦卦宫）
- **天干双值**：28 个乾坤相关卦，夏至/冬至两套天干
- **去重逻辑**：去掉 zhanwen_time 唯一约束（同日多卦例），增量用 last_import_time
- **卦象绘制**：flexbox + background 渲染爻线，阳爻/阴爻统一占位高度
- **GuaCiFloat 爻辞**：后端 `_parse_json_field` 处理双编码，前端结构化渲染爻辞+小象传
- **网络图谱**：纯 SVG + 自建力导向物理引擎（斥力/弹簧力/向心力/阻尼），参数按画布等比缩放
- **检索 SQL**：全部参数化查询，字段名白名单校验，禁止字符串拼接
- **解卦入口**：NavBar 下拉菜单（八宫变化/互卦/网络图谱），GualiDetail 双按钮

---

## 重要约定

1. **使用中文交流**
2. **先切分支再写代码**：`feat/issue-N`
3. **每次只做一个 Issue**，不要跨 Issue 编码
4. **提交前自审两遍**：第一遍对照规划文档，第二遍逐行跟踪
5. **前端复用优先**：写前端代码前先找已有组件/CSS/交互能否复用，禁止为同样效果重复造轮子
6. **编辑优先于新建**
7. **Markdown 表格前加空行**
8. **commit 格式**：`feat/fix/chore: <中文简述>`
9. **squash merge 后检查**：Issue 关闭 / 本地分支 / 远程分支（git fetch --prune）/ 工作区
10. **审查强度**：★★ 逐条审查 / ★ 重点审查 / 无标记 正常
11. **遗留占位追踪**：代码中用 `raise NotImplementedError()` 替代空函数
12. **占位追踪 grep**：`grep -rn "NotImplementedError|TODO|FIXME" backend/ --include="*.py"`

---

## 启动命令

```bash
# 后端
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
# 前端
cd frontend && npm run dev
# 一键
run.bat
# Swagger
http://localhost:8001/docs
```

---

## 关键文件索引

| 想看什么 | 文件 |
|---------|------|
| AI 协作规范 | `CLAUDE.md` |
| 设计文档 | `.AIDiscuss/`（.A1 .A2 .B .C1~.C4 .C31 .C32 .C33 .C33-1 .Z） |
| 规划文档 | `.specs/`（7 个里程碑） |
| 开发架构总览 | `.specs/READMEsp.md` |
| v0.4 规划 | `.specs/v0.4C3复杂检索/`（12 个文件） |
| v0.5 规划 | `.specs/v0.5C2解卦模块/`（6 个文件） |
| v0.4 设计 | `.AIDiscuss/.C31*.md` `.AIDiscuss/.C32*.md` `.AIDiscuss/.C33*.md` |
| search_service 审查 | `.user/search_service代码审查文档.md` |
| 测试数据 | `.user/测试数据.json` |
| 六爻规则 | `.user/六爻基本规则.md` |
| GitHub 里程碑 | `v0.4 C3 复杂检索`（#5）、`v0.5 C2 解卦模块`（#6，已关闭） |
