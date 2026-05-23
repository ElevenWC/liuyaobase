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

## 工作流程（重要！）

```
用户选 Issue（对应一个 .specs/ 规划文档）
  → AI 读规划文档 + 设计文档
  → 有疑问在 Issue 评论提问
  → AI 切分支 feat/issue-N，写代码
  → AI 自审两遍（对照规划文档 §7 陷阱）
  → 跑规划文档 §6 的测试命令
  → commit + push（不创建 PR！）
  → 通知用户跑测试命令
  → 用户验收通过 → AI 创建 PR → squash merge → 删除分支
  → AI 逐项检查（squash merge 后必做）：
      ├── Issue 是否已关闭？
      ├── 本地分支是否已删除？
      ├── 远程分支是否已删除？（git fetch --prune）
      └── git status 确认工作区干净
  → 验收有问题 → 同分支修改 → push → 用户再测
```

> **关键规则**：PR 在用户验收通过后才创建，不是在 push 时创建。确保 PR 内容一次性正确。

## 当前进度

### v0.0 里程碑：9 个 Issue，已完成 1 个

| Issue | 标题 | 状态 |
|:--:|------|:--:|
| [#1](https://github.com/ElevenWC/liuyaobase/issues/1) | 00.1 backend/config.py | ⬜ 待开发 |
| [#2](https://github.com/ElevenWC/liuyaobase/issues/2) | 00.2 backend/main.py | ⬜ 待开发 |
| [#3](https://github.com/ElevenWC/liuyaobase/issues/3) | 00.3 backend/requirements.txt | ✅ 已完成 |
| [#4](https://github.com/ElevenWC/liuyaobase/issues/4) | 00.4 backend/db/connection.py | ⬜ 待开发 |
| [#5](https://github.com/ElevenWC/liuyaobase/issues/5) | ★00.5 backend/db/init_db.py | ⬜ ★需逐条审查 |
| [#6](https://github.com/ElevenWC/liuyaobase/issues/6) | 00.6 backend/models/ (17个) | ⬜ 待开发 |
| [#7](https://github.com/ElevenWC/liuyaobase/issues/7) | ★00.7 stored_functions/ (8个) | ⬜ ★需逐条审查 |
| [#8](https://github.com/ElevenWC/liuyaobase/issues/8) | 00.8 frontend/ 骨架 | ⬜ 待开发 |
| [#9](https://github.com/ElevenWC/liuyaobase/issues/9) | 00.9 .gitignore | ⬜ 待开发 |

### 建议开发顺序

```
第1步: Issue #3  requirements.txt     ✅ 已完成
第2步: Issue #1  config.py            ← 下一步
第3步: Issue #4  connection.py
第4步: Issue #2  main.py
第5步: Issue #6  models/              （📦 可与第4步并行）
第6步: Issue #5  ★init_db.py          （★需逐条审查）
第7步: Issue #7  ★stored_functions    （★需逐条审查）
第8步: Issue #9  .gitignore           （📦 可与第9步并行）
第9步: Issue #8  frontend/            （📦 可与第8步并行）
```

### 已完成的 commit

```
ef20fc3 feat: 添加Python依赖清单(requirements.txt)
```
该 commit 同时包含了编码工作流程更新和 squash merge 后检查清单。

## 关键文件索引

| 想看什么 | 文件 |
|---------|------|
| 开发架构总览、文件清单、里程碑 | `.specs/READMEsp.md` |
| 数据库表结构（18张表+36索引+建表SQL） | `.AIDiscuss/.A1数据库设计.md` |
| 后端架构和 API 设计 | `.AIDiscuss/.A2后端架构.md` |
| 六爻算法规则（纳甲/六亲/神煞…） | `.AIDiscuss/.B核心算法.md` |
| 各模块功能设计 | `.AIDiscuss/.C1~.C4*.md` |
| 项目全局状态 | `.AIDiscuss/.Z项目总结.md` |
| 开发流程详细规范 | `.user/AI协作工作流程指南(项目开发阶段).md` v1.2 |
| AI 接手文档 | `.claude/handoff.md`（本文件） |
| v0.0 规划文档 | `.specs/v0.0项目骨架_数据库/` |

## 重要约定

1. **使用中文交流**
2. **编码前先读 Issue 对应的规划文档**（§3 接口、§4 逻辑、§7 陷阱），规划文档 = 实现计划
3. **先 push 后 PR**：commit + push 后等用户验收通过才创建 PR
4. **squash merge 后必做检查**：Issue关闭 / 本地分支 / 远程分支 / 工作区干净
5. **Git 规范**：分支 `feat/issue-N`，commit 格式 `feat: <中文简述>`，禁止 force push main，禁止 `--no-verify`
6. **敏感信息**：`backend/config.py` 含数据库密码，在 `.gitignore` 中，不提交
7. **审查强度**：★★ 需逐条审查代码逻辑，★ 需重点审查关键函数
8. **Markdown 表格前加空行**
9. **编辑优先于新建**，不要随意新建文件
10. **不要主动 commit**，等用户明确要求时再操作

## 已确认的关键设计决定

- 土的生旺墓绝 = 水（申子辰巳），不是火
- guali_tag 是纯关联表，不建独立 model 文件
- check_sanhe 不形成三合时返回 `''`（空串），不返回 NULL
- 建表 SQL 放独立文件 `backend/db/create_tables.sql`（与 init_db.py 分离）
- static_* 三表 v0.0 建空表，v0.1 回填数据
- v0.0 不加 Alembic、不加开发依赖（black/ruff/mypy）
- `.vscode/` 忽略，`.claude/` 保留跟踪
