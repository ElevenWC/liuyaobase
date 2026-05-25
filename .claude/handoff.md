# AI 接手提示词 — liuyaobase

> 新对话开始时粘贴以下内容给 AI，快速接手项目。

---

## 项目概况

- **名称**：liuyaobase（六爻数据库系统）
- **技术栈**：Python FastAPI + SQLModel + MySQL + Vue 3 + Vite + Pinia + lunar-python
- **仓库**：`ElevenWC/liuyaobase`，分支 `main`
- **数据库**：MySQL，localhost:3306，root/020508，库名 liuyao
- **当前进度**：v0.0 ~ v0.3 全部完成（48 个 Issue），v0.4 / v0.5 待开始

## 工作流程

```
用户选 Issue → AI 读 .specs/ 规划文档 + .AIDiscuss/ 设计文档
  → 先切分支 feat/issue-N → 写代码 → 自审两遍（对照 §7 陷阱）
  → 跑测试命令 → commit + push（不创建 PR！）
  → 用户跑测试验收 → AI 创建 PR → squash merge → 删除本地+远程分支
  → merge 后必查：Issue 是否关闭 / 分支是否删除 / git status 干净
```

## 里程碑完成情况

| 里程碑 | Issue 数 | 状态 |
|--------|:------:|:--:|
| v0.0 项目骨架+数据库 | 9 | ✅ |
| v0.1 核心算法层 | 15 | ✅ |
| v0.2 数据导入+预计算 | 8 | ✅ |
| v0.3 C1 卦例显示 | 16 | ✅ |
| v0.4 C3 复杂检索 | — | 🔜 |
| v0.5 C2 解卦模块 | — | 🔜 |
| v0.6 C4 股票关联 | — | 🔜 |

## 当前代码结构

```
backend/
├── main.py, config.py, requirements.txt
├── core/          # 14 个算法文件（六爻纯函数）
├── crud/          # 10 个 CRUD 文件
├── services/      # 4 个服务文件（precalculate/import/guali/tag）
├── models/        # 18 个 SQLModel 表定义
├── schemas/       # guali.py + tag.py
├── api/routers/   # guali / tags / import_data / guaci（临时）
├── db/            # connection / init_db / create_tables.sql / stored_functions/
└── tests/         # 12 个测试文件，69 个测试
frontend/src/
├── api/index.js        # axios 封装（17 个 API 函数）
├── stores/index.js     # Pinia 全局状态
├── router/index.js     # 路由（/guali /input /import /tags）
├── style.css           # CSS 变量系统（颜色/圆角/阴影/间距）
├── views/
│   ├── Home.vue        # 左右分栏主布局
│   ├── GualiList.vue   # 左侧列表（搜索/分页/两级标签筛选/批量删除）
│   ├── GualiDetail.vue # 右侧详情（卦象卡片/编辑/标签/浮窗）
│   ├── GualiInput.vue  # 手动导入（二级卦选择器）
│   ├── ImportJson.vue  # JSON 批量导入
│   └── TagManager.vue  # 标签管理
└── components/
    ├── NavBar.vue           # 导航栏（毛玻璃+链接）
    └── shared/GuaCiFloat.vue # 卦爻辞浮窗（可拖动/多开）
```

## 关键技术决策

- **CSS 变量系统**：全部颜色/圆角/阴影/间距定义在 `style.css` 的 `:root {}`，组件禁止裸色值
- **深色主题**：`#0F172A` 底 + `#1E293B` 卡片 + `#6366F1` 靛蓝品牌色
- **标签颜色**：8 色卡（柔和系），按一级标签 ID 取模，刷新稳定
- **标签两级筛选**：一级选父标签→自动包含子标签卦例；打二级标签自动去一级关联
- **之卦六亲**：用本卦卦宫五行计算（不是之卦卦宫）
- **天干双值**：28 个乾坤相关卦，夏至/冬至两套天干
- **去重逻辑**：去掉 zhanwen_time 唯一约束（同日多卦例），增量用 last_import_time
- **卦象绘制**：flexbox 固定宽度 + CSS 4px 粗爻线，阴爻两段等长

## 重要约定

1. **使用中文交流**
2. **先切分支再写代码**
3. **Markdown 表格前加空行**
4. **编辑优先于新建**
5. **commit 格式**：`feat/fix/chore: <中文简述>`，分支 `feat/issue-N`
6. **审查强度**：★★ 逐条审查 / ★ 重点审查 / 无标记 正常
7. **squash merge 后检查**：Issue 关闭 / 本地分支 / 远程分支（git fetch --prune）/ 工作区
8. **遗留占位追踪**：代码中用 `raise NotImplementedError()` 替代空函数，Issue 中写明前置依赖，里程碑收尾时 grep 汇总写入下一里程碑
9. **占位追踪 grep 命令**：
   ```
   grep -rn "NotImplementedError|TODO|FIXME|placeholder|暂|留空|v0." backend/ --include="*.py"
   ```

## 测试数据库

数据库中有 7 条真实卦例（用户从 App 导出），可通过 `GET /api/guali/53` 等查看。

## 启动命令

```bash
# 后端
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
# 前端
cd frontend && npm run dev
# 一键
run.bat
```

## 关键文件索引

| 类型 | 路径 |
|------|------|
| 设计文档 | `.AIDiscuss/`（.A1 .A2 .B .C1~.C4 .Z 共 13 个） |
| 规划文档 | `.specs/`（63 个，7 里程碑） |
| 开发架构总览 | `.specs/READMEsp.md` |
| AI 协作规范 | `CLAUDE.md` |
| 工作流程详解 | `.user/AI协作工作流程指南(项目开发阶段).md` |
| 六爻基本规则 | `.user/六爻基本规则.md` |
| 测试数据 | `.user/测试数据.json` |
