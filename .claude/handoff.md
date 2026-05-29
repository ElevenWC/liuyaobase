# AI 接手提示词 — liuyaobase

> 新对话开始时粘贴以下内容给 AI，快速接手项目。2026-05-29 更新（v0.4 全部完成 + 批量优化合并，v0.6 待开始）。

---

## 项目概况

- **名称**：liuyaobase（六爻数据库系统）
- **技术栈**：Python FastAPI + SQLModel + MySQL + Vue 3 + Vite + Pinia + lunar-python
- **仓库**：`ElevenWC/liuyaobase`，分支 `main`
- **数据库**：MySQL，localhost:3306，root/020508，库名 liuyao
- **当前进度**：v0.0~v0.5 全部完成，v0.6 C4 股票关联为下一里程碑

---

## 工作流程

```
用户选 Issue → AI 读 .specs/ 规划文档 + .AIDiscuss/ 设计文档
  → 切分支 feat/issue-N → 写代码
  → 【必须】自审两遍再提交
  → commit + push（不创建 PR！）
  → 用户跑测试验收 → AI 创建 PR → squash merge → 删除本地+远程分支
```

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

## v0.4 全部完成 ✅

| Issue | 内容 |
|:--:|------|
| #96~#103 | C3 后端+前端基础组件 |
| #107 | Search.vue 检索主页面 + 条件组完整实现 |
| #105 | RecommendedSchemes.vue 自定义方案管理 |
| #118 | 数目判断（COUNT 子查询） |
| #120 | 逻辑链可视化编辑（AND/OR/NOT/括号） |
| #121 | 关系对象扩展（六神/状态/伏神飞神 + 来源选择） |
| #122 | 标签筛选 + 占问事由文本搜索 + 批量打标签 |
| #119 | 检索页右栏卦例查看——复用 GualiDetail.vue，三栏布局 |

### PR #128 批量优化（2026-05-29）

| 功能 | 说明 |
|------|------|
| 导入去重 | 串行级联四层判定（事由→时间→本卦→之卦），`zhanwen_shiyou(100)` 前缀索引 |
| 文件去重 | 同名文件二次导入整批跳过，`system_config.imported_files` 记录 |
| 干支日历 | CalendarFloat.vue 浮窗，点击柱行触发，逐日干支+节气标注，可拖动 |
| 批量查找 | C1 搜索栏 CSV/JSON 按 ID 批量检索 |
| 导出 | C3 结果 CSV/JSON 导出，文件名输入+按钮在分页信息行右侧 |
| C1 侧栏折叠 | 复用 C3 fl-toggle，16px 窄条+◂/▸ |
| 搜索增强 | 编号/日期(YYMMDD/MMDD)/文本混合搜索，前导零不查 ID |
| 八宫页 | 卦名二级选择+预览、网络图谱卦名常驻、GUA_CODES 错码修复 |
| 手动导入修复 | 二级选择失效(GUA_CODES 错码)、重复不提示(HTTP 200 假成功) |
| UI 修复 | 导航栏 z-index、之卦列静卦留空、关闭按钮下移、卦名显示等 10+ 项 |

### 已取消

| Issue | 内容 |
|:--:|------|
| #104 | CompareMode.vue（对比模式） |
| — | 条件组折叠/展开、字段库拖拽、scope 全部来源 |

---

## 当前代码结构

### frontend/src/components/Search/

```
Search/
├── ConditionBuilder.vue      # 条件构建器核心——所有条件类型的渲染+按钮
├── FieldLibrary.vue           # 字段库面板——9 大分类可折叠
├── ResultList.vue             # 结果列表——分页+多选+GuaCiFloat
├── SameYaoGroup.vue           # 同一爻条件组（来源 OR）
├── SamePositionGroup.vue      # 同爻位条件组（同爻位 AND）
├── FeishenGroup.vue           # 飞神条件组
├── RecommendedSchemes.vue     # 自定义方案管理（localStorage）
shared/
├── zCounter.js                # 全局 z-index 计数器
├── GuaCiFloat.vue             # 卦爻辞浮窗（可拖动，各模块共用）
├── CalendarFloat.vue          # 干支日历浮窗（可拖动，点击柱行触发）
├── NetworkGraph.vue           # 纯 SVG 力导向网络图谱
stores/
├── useSearchStore.js          # C3 Pinia store——conditions/logicChain/results
├── index.js                   # C1 全局 store——tagTree
```

---

## C3 检索条件总览

### 条件构建器按钮顺序（与字段库一致）

`+ 时间` `+ 卦类` `+ 爻属性` `+ 关系` `+ 神煞` `+ 数目` `+ 文本搜索` `+ 标签` | `+ 同一爻` `+ 同爻位` `+ 飞神`

### 条件类型

| 类型 | field 标识 | 说明 |
|------|-----------|------|
| 爻属性/卦类/时间 | 普通字段名 | 有 scope 来源选择（本卦/变爻/之卦静爻/易冒伏神/增删伏神） |
| 关系 | `_rel` | 左右对象+关系类型，三合有中对象，有 scope 选择 |
| 神煞 | `is_*/dai_*` | 爻对象+是/带/是或带+神煞类型，可选条件组引用 |
| 数目 | `_count` | 统计范围+属性=值+的数目+运算符+数字，COUNT 子查询 |
| 文本搜索 | `_keyword` | 占问事由 LIKE %keyword% |
| 标签 | `_tag` | 两级级联下拉，JOIN guali_tag 表 |
| 条件组 | `groupType` | same_yao / same_position / feishen |

### 逻辑链

store.logicChain 维护条件间逻辑关系。支持 AND/OR 切换按钮、NOT 取反、`「」`括号分组（最多 5 层）。后端 `_assemble_logic` 解析生成 SQL WHERE。

---

## 关键注意事项

### Vue scoped CSS 隔离

ConditionBuilder.vue 的 `.cb-sel`/`.cb-btn`/`.cb-input` 样式不会穿透到子组件。各条件组组件需在自身 `<style scoped>` 中重定义这些类。

### 布尔值 MySQL 兼容

`is_dong`/`is_an_dong`/`zengshan_exists` 是 MySQL TINYINT(1)。前端传字符串 `'true'/'false'` 需在后端 `_norm_bool()` 转为 `1/0`。

### Pydantic 额外字段

Condition Schema 的 `countAttr`/`countValue`/`tagId`/`tagId2` 需显式定义为 Optional 字段，否则 Pydantic 默认忽略。

### 路由顺序

FastAPI 字面路径（如 `/batch`）必须定义在路径参数（如 `/{id}`）之前。

### 条件组引用

关系条件 `right_type='condition_group_ref'` 可引用条件组 ID。后端 `resolve_dz` 用独立表别名重建子查询。神煞也可引用条件组（`_build_shensha_clause` 支持 cond_clauses）。

### 导入去重机制

`import_service.py` 的 `is_duplicate()` 串行级联判定：`SELECT WHERE zhanwen_shiyou = :v`（前缀索引）→ Python 中过滤 time/ben_code/zhi_code。同名文件通过 `system_config.imported_files`（JSON 数组）记录，二次导入整批跳过。手动导入同样走四层判定，重复抛 `ValueError`。

### GUA_CODES 错码

项目中曾有三处 `GUA_CODES` 数组含错码（水雷屯 `010001`→正确 `010100`，及其他）。已修复的文件：`GualiInput.vue`（CODES 数组）、`BagongPage.vue`（GUA_CODES 数组）。核心公式：`hexagram_code = outer_trigram + inner_trigram`。`GualiDetail.vue` 不依赖此数组（通过 `CODE_TO_NAME` 字典映射）。未来新增文件如需 64 卦码表，务必以此公式验证。

### 日历组件

`CalendarFloat.vue` 复用 `GuaCiFloat` 的拖动+层叠架构，共用 `zCounter.js`。数据源为 `GET /jiegua/calendar?year=&month=`，后端 `time_converter.py` 逐日调用 `lunar-python` 计算。星期顺序：一二三四五六日（周一为首，`weekday=0`）。

---

## 启动命令

```bash
# 后端
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
# 前端
cd frontend && npm run dev
# Swagger: http://localhost:8001/docs
```

---

## 文件索引

| 想看什么 | 文件 |
|---------|------|
| 项目协作规范 | `CLAUDE.md` |
| 设计文档 | `.AIDiscuss/`（.A1 .A2 .B .C1~.C4 .C31 .C32 .C33 .C33-1 .Z） |
| 规划文档 | `.specs/`（7 个里程碑） |
| v0.4 规划 | `.specs/v0.4C3复杂检索/` |
| C3 检索字段指南 | `.user/C3检索字段使用指南.md` |
| C3 待补充功能 | `.user/C3待补充功能清单.md` |

---

## v0.6 C4 股票关联 — 前置待办

v0.4 收尾检查结果：**无遗留占位**（无 NotImplementedError/TODO/FIXME/暂/留空标记）。v0.6 可从零开始。

v0.6 规划文档位于 `.specs/v0.6C4股票关联/`，共 7 个规划单元（06.1~06.13）。

| 单元 | 内容 | 标记 |
|------|------|:--:|
| 06.1~06.4 | 后端 CRUD + Models + Schemas（stock_info/day_kline/minute_kline/futures） | — |
| 06.5 | stock_data_service.py（AKShare 数据拉取） | ★ |
| 06.6 | market_service.py（行情预计算：日涨跌/分时聚合/四价统一/干支索引） | ★★ |
| 06.7~06.9 | 后端 API routers + schemas（9 端点） | — |
| 06.10 | StockAnalysis.vue（股票分析主页面） | ★ |
| 06.11 | KlineChart.vue（K线图组件，ECharts） | ★★ |
| 06.12~06.13 | IntradayChart.vue（分时图）+ GualiFloatPanel（关联卦例浮窗面板） | — |
