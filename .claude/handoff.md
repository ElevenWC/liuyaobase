# AI 接手提示词 — liuyaobase

> 新对话开始时，将本文档内容粘贴给 AI，即可快速接手。

---

## 项目概况

- **名称**：liuyaobase（六爻数据库系统）
- **技术栈**：Python FastAPI + SQLModel + MySQL + Vue 3 + Vite + AKShare + lunar-python
- **仓库**：`ElevenWC/liuyaobase`，分支 `main`
- **数据库**：MySQL，localhost:3306，root/020508，库名 liuyao

## 当前阶段：编码实现阶段

详细规划已完成（63 个规划文档在 `.specs/` 下，13 个设计文档在 `.AIDiscuss/` 下），当前正在**按 Issue → 分支 → PR** 流程逐单元编码。

## 工作流程

```
用户选 Issue（对应一个 .specs/ 规划文档）
  → AI 读规划文档 + 设计文档
  → 有疑问在 Issue 评论提问
  → AI 切分支 feat/issue-N，写代码
  → AI 自审两遍（对照规划文档 §7 陷阱）
  → 跑规划文档 §6 的测试命令
  → commit + push（不创建 PR）
  → 用户跑测试命令验收
  → 验收通过 → AI 创建 PR → squash merge → 删除分支
  → AI 逐项检查：Issue关闭/本地分支/远程分支/工作区干净
  → 验收有问题 → 同分支修改 → push → 用户再测
```

## 当前进度

v0.0 里程碑的 9 个 Issue 已全部创建完毕，**待开发**：

| Issue | 标题 | 标记 |
|:--:|------|:--:|
| [#1](https://github.com/ElevenWC/liuyaobase/issues/1) | 00.1 backend/config.py | 普通 |
| [#2](https://github.com/ElevenWC/liuyaobase/issues/2) | 00.2 backend/main.py | 普通 |
| [#3](https://github.com/ElevenWC/liuyaobase/issues/3) | 00.3 backend/requirements.txt | 普通 |
| [#4](https://github.com/ElevenWC/liuyaobase/issues/4) | 00.4 backend/db/connection.py | 普通 |
| [#5](https://github.com/ElevenWC/liuyaobase/issues/5) | ★00.5 backend/db/init_db.py | ★需逐条审查 |
| [#6](https://github.com/ElevenWC/liuyaobase/issues/6) | 00.6 backend/models/ (17个) | 普通 |
| [#7](https://github.com/ElevenWC/liuyaobase/issues/7) | ★00.7 stored_functions/ (8个) | ★需逐条审查 |
| [#8](https://github.com/ElevenWC/liuyaobase/issues/8) | 00.8 frontend/ 骨架 | 普通 |
| [#9](https://github.com/ElevenWC/liuyaobase/issues/9) | 00.9 .gitignore | 普通 |

**建议开发顺序**：

```
第1步: Issue #3  requirements.txt     ← 先装依赖
第2步: Issue #1  config.py            ← 数据库连接参数
第3步: Issue #4  connection.py        ← 数据库引擎
第4步: Issue #2  main.py              ← 启动入口
第5步: Issue #6  models/              ← 表定义（📦 可与第4步并行）
第6步: Issue #5  ★init_db.py          ← 建表+填充数据（★逐条审查）
第7步: Issue #7  ★stored_functions    ← 存储函数注册（★逐条审查）
第8步: Issue #9  .gitignore           ← 📦 可与第9步并行
第9步: Issue #8  frontend/            ← 📦 可与第8步并行
```

## 关键文件索引

| 想看什么 | 文件 |
|---------|------|
| 开发架构总览、文件清单、里程碑 | `.specs/READMEsp.md` |
| 数据库表结构（18张表+36索引+建表SQL） | `.AIDiscuss/.A1数据库设计.md` |
| 后端架构和 API 设计 | `.AIDiscuss/.A2后端架构.md` |
| 六爻算法规则（纳甲/六亲/神煞…） | `.AIDiscuss/.B核心算法.md` |
| 各模块功能设计 | `.AIDiscuss/.C1~.C4*.md` |
| 项目全局状态 | `.AIDiscuss/.Z项目总结.md` |
| 开发流程详细规范 | `.user/AI协作工作流程指南(项目开发阶段).md` |
| v0.0 规划文档 | `.specs/v0.0项目骨架_数据库/` |

## 重要约定

1. **使用中文交流**
2. **编码前先读 Issue 对应的规划文档**（§3 接口、§4 逻辑、§7 陷阱），规划文档 = 实现计划
3. **Git 规范**：分支 `feat/issue-N`，commit 格式 `feat: <中文简述>`，禁止 force push、禁止 `--no-verify`
4. **敏感信息**：`backend/config.py` 含数据库密码，已在 `.gitignore` 中，不提交
5. **审查强度**：★★ 标记的文件需用户逐条审查代码逻辑，★ 标记需重点审查关键函数
6. **测试**：每个 Issue 有用户测试命令（复制到终端即可执行），AI 写完代码后先自测
7. **编辑优先于新建**：修改现有文件用 Edit 工具，不要随意新建文件
8. **Markdown 表格前加空行**，否则表格无法渲染
9. **CSV/数据文件只读前几行**确认格式，不读全部
10. **不要主动提交代码**，等用户明确要求时再 commit

## 7 个里程碑概览

| 里程碑 | 内容 | Issue 数 |
|:--:|------|:--:|
| v0.0 | 项目骨架 + 数据库建表 | 9 |
| v0.1 | 核心算法层 B1-B9 | ~15 |
| v0.2 | 数据导入 + 预计算服务 | ~8 |
| v0.3 | C1 卦例显示 | ~15 |
| v0.4 | C3 复杂检索 | ~12 |
| v0.5 | C2 解卦模块 | ~8 |
| v0.6 | C4 股票关联 | ~9 |

## 已确认的关键设计决定

- 土的生旺墓绝 = 水（申子辰巳），不是火
- guali_tag 是纯关联表，不建独立 model 文件
- check_sanhe 不形成三合时返回 `''`（空串），不返回 NULL
- 建表 SQL 放独立文件 `backend/db/create_tables.sql`（与 init_db.py 分离）
- static_* 三表 v0.0 建空表，v0.1 回填数据
- v0.0 不加 Alembic、不加开发依赖（black/ruff/mypy）
