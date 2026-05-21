# liuyaobase 项目开发规格书

> 本文档是整个项目的开发蓝图。它把设计文档拆解为可开发、可测试的小单元，标注重要程度和依赖关系，供开发时逐单元推进。
> 每个单元开发前，AI 应阅读对应的设计文档章节，在对应 Issue 评论中写实现计划。

---

## 一、项目架构总览

<style>
  .arch { font-family: 'Microsoft YaHei', sans-serif; font-size: 13px; }
  .arch-box { border: 2px solid #333; border-radius: 6px; padding: 10px; margin: 6px 0; }
  .arch-box h4 { margin: 0 0 6px 0; padding: 4px 8px; border-radius: 3px; }
  .critical { border-color: #d32f2f; background: #ffebee; }
  .critical h4 { background: #d32f2f; color: #fff; }
  .important { border-color: #e64a19; background: #fff3e0; }
  .important h4 { background: #e64a19; color: #fff; }
  .normal { border-color: #2e7d32; background: #e8f5e9; }
  .normal h4 { background: #2e7d32; color: #fff; }
  .shared { border-color: #1565c0; background: #e3f2fd; }
  .shared h4 { background: #1565c0; color: #fff; }
  .infra { border-color: #6a1b9a; background: #f3e5f5; }
  .infra h4 { background: #6a1b9a; color: #fff; }
  .flow-arrow { text-align: center; font-size: 18px; color: #555; margin: 2px 0; }
  .legend { display: flex; gap: 16px; flex-wrap: wrap; margin: 10px 0; }
  .legend-item { display: flex; align-items: center; gap: 4px; }
  .legend-dot { width: 14px; height: 14px; border-radius: 3px; border: 2px solid; }
  .milestone { border-left: 4px solid #ff9800; padding-left: 8px; margin: 8px 0; }
  .tag { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; margin: 0 2px; }
  .tag-red { background: #d32f2f; color: #fff; }
  .tag-orange { background: #e64a19; color: #fff; }
  .tag-blue { background: #1565c0; color: #fff; }
  .tag-green { background: #2e7d32; color: #fff; }
</style>

<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#ffebee;border-color:#d32f2f"></div> 🔴 核心/高难度</div>
  <div class="legend-item"><div class="legend-dot" style="background:#fff3e0;border-color:#e64a19"></div> 🟡 重要/需仔细审核</div>
  <div class="legend-item"><div class="legend-dot" style="background:#e8f5e9;border-color:#2e7d32"></div> 🟢 常规功能</div>
  <div class="legend-item"><div class="legend-dot" style="background:#e3f2fd;border-color:#1565c0"></div> 🔵 共享组件</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f3e5f5;border-color:#6a1b9a"></div> 🟣 基础设施</div>
</div>

<div class="arch">

<div class="arch-box infra">
<h4>🟣 数据库层 (MySQL)</h4>
<p><b>16张核心表 + 36个索引 + 8个存储函数</b></p>
<p>核心表: guali · tag · guali_tag · bagong_gua · guaci · system_config<br>
预存表(static_*): static_gua_yao_info · static_fushen_zengshan · static_fushen_yimao<br>
预存表(guali_*): guali_time · guali_shensha · guali_gua · guali_yao<br>
股票表: stock_info · stock_day_kline · stock_minute_kline(OHLC)<br>
期货表: futures_info · futures_minute_kline（日K不存表，分钟K聚合）<br>
存储函数: check_sheng · check_ke · check_he · check_chong · check_banhe · check_sanhe · check_shengwang · check_bagong_relation</p>
</div>

<div class="flow-arrow">▲ 读写 ▲</div>

<div class="arch-box important">
<h4>🟡 数据访问层 (backend/crud/)</h4>
<p>base.py · guali.py · tag.py · bagong_gua.py · guaci.py · guali_time.py · guali_shensha.py · guali_gua.py · guali_yao.py · stock_info.py · stock_day_kline.py · stock_minute_kline.py</p>
</div>

<div class="flow-arrow">▲ 调用 ▲</div>

<div class="arch-box normal">
<h4>🟢 服务层 (backend/services/)</h4>
<p>guali_service.py · tag_service.py · import_service.py · <span class="tag tag-red">precalculate_service.py</span> · <span class="tag tag-orange">search_service.py</span> · export_service.py · <span class="tag tag-orange">market_service.py</span> · stock_data_service.py · zhanyan_service.py</p>
</div>

<div class="flow-arrow">▲ 调用 ▲</div>

<div class="arch-box normal">
<h4>🟢 API层 (backend/api/routers/)</h4>
<p>guali.py (7端点) · tags.py (5端点) · import_data.py (3端点) · bagong.py · jiegua.py (4端点) · search.py (3端点) · stock.py (9端点)</p>
</div>

<div class="flow-arrow">▲ HTTP ▲</div>

<div class="arch-box normal">
<h4>🟢 前端页面 (frontend/src/views/)</h4>
<p>Home.vue · GualiList.vue · GualiDetail.vue · GualiInput.vue · CsvImport.vue · <span class="tag tag-orange">Search.vue</span> · <span class="tag tag-orange">StockAnalysis.vue</span></p>
</div>

<div class="flow-arrow">▲ 组合 ▲</div>

<div class="arch-box normal">
<h4>🟢 前端组件 (frontend/src/components/)</h4>
<p>NavBar.vue · <span class="tag tag-blue">shared/GuaCiFloat.vue</span> · Search/* (6组件) · Stock/* (3组件)</p>
</div>

<div style="margin-top:12px; display:flex; gap:12px;">
<div class="arch-box critical" style="flex:1;">
<h4>🔴 核心算法层 (backend/core/) — 独立于数据库</h4>
<p>enums.py · <span class="tag tag-red">time_converter.py</span> · <span class="tag tag-red">najia.py</span> · <span class="tag tag-red">liuqin.py</span> · liushen.py · an_dong.py · <span class="tag tag-orange">shi_ying.py</span> · <span class="tag tag-red">fushen_zengshan.py</span> · <span class="tag tag-red">fushen_yimao.py</span> · <span class="tag tag-red">shensha.py</span> · gua_type.py · hugua.py · bagong_bian.py · dizhi_relation.py</p>
</div>
</div>

</div>

---

## 二、里程碑与开发顺序

| 里程碑 | 内容 | 预计文件数 | 依赖 |
|:--:|------|:--:|------|
| **v0.0** | 项目骨架 + 数据库建表 + static_* 填充 | ~20 | — |
| **v0.1** | 核心算法层 B1-B9 | ~15 | v0.0 |
| **v0.2** | 数据导入 + 预计算服务 | ~8 | v0.1 |
| **v0.3** | C1 卦例显示（前后端） | ~15 | v0.2 |
| **v0.4** | C3 复杂检索（前后端） | ~12 | v0.2 |
| **v0.5** | C2 解卦模块（前后端） | ~8 | v0.2 |
| **v0.6** | C4 股票关联（前后端） | ~9 | v0.3, v0.4 |

> **原则**：每个里程碑内，优先完成不依赖其他单元的文件，将有依赖关系的文件排在后面。

---

## 三、单元清单

### 图例

| 标记 | 含义 |
|:--:|------|
| 🔴 | 核心/高难度 — 对整个系统至关重要，实现复杂，需用户仔细审核 |
| 🟡 | 需要仔细审核 — 涉及关键规则或数据一致性 |
| 🔗 | 需联合测试 — 与标注的其他单元一起测试，不能孤立验证 |
| 📦 | 可并行开发 — 与同标记单元互不依赖，可以同时开工 |
| 👤 | 用户参与测试 — 用户需要实际运行并验证结果 |

---

### v0.0 — 项目骨架 + 数据库

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 00.1 | `backend/config.py` | 数据库连接串、AKShare 限流配置、端口等 | 🟣 |
| 00.2 | `backend/main.py` | FastAPI 应用入口，注册路由、CORS | 🟣 |
| 00.3 | `backend/requirements.txt` | Python 依赖清单 | 🟣 |
| 00.4 | `backend/db/connection.py` | SQLModel 引擎创建、session 管理 | 🟣 |
| 00.5 | `backend/db/init_db.py` | 执行建表 SQL + static_* 三表数据填充 | 🟡 🔴 |
| 00.6 | `backend/models/` (全部 15 个) | SQLModel 表定义，与 16 张表一一对应 | 🟣 |
| 00.7 | `backend/db/stored_functions/` (8个.sql) | MySQL 存储函数，建表后注册 | 🔴 |
| 00.8 | `frontend/` 项目骨架 | `package.json` + `vite.config.js` + `main.js` + `router/` + `App.vue` | 🟣 |
| 00.9 | `.gitignore` | 排除 .user/ / venv/ / node_modules/ 等 | 🟣 |

**00.5 特别说明**：init_db.py 需要读取 `.user/zhouyiData.json` 中的八宫卦序和卦爻辞数据填充 bagong_gua 和 guaci 表，同时根据纳甲规则生成 static_gua_yao_info（384条）、static_fushen_zengshan（~64条）、static_fushen_yimao（384条）。数据正确性直接影响整个系统。👤

**00.7 特别说明**：8 个存储函数中，check_sheng/check_ke/check_he/check_chong 相对简单，check_banhe/check_sanhe/check_shengwang/check_bagong_relation 涉及多分支判断。函数需要在 Python 层先写参考实现和单元测试，验证通过后再移植为 SQL。

🔗 00.5 + 00.7 需一起验证：建表后注册函数，抽样查询确认数据完整。

---

### v0.1 — 核心算法层

> 📖 设计文档：.B核心算法.md

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 01.1 | `backend/core/enums.py` | 五行、六亲、六神、天干、地支、宫位等枚举常量 | 🟣 📦 |
| 01.2 | `backend/core/time_converter.py` | B1: 公历→干支（年柱/月柱/日柱/旬空），含 `get_jieqi_dates()` | 🔴 👤 |
| 01.3 | `backend/core/najia.py` | B2: 纳甲装卦——64卦×6爻地支+天干，28个乾坤卦双天干 | 🔴 👤 |
| 01.4 | `backend/core/liuqin.py` | B3: 六亲计算——5种对象（本卦/变爻/之卦/易冒/增删）共用规则 | 🔴 👤 |
| 01.5 | `backend/core/liushen.py` | B3: 六神排列——根据日干排6爻 | 🟢 📦 |
| 01.6 | `backend/core/an_dong.py` | B3.5: 暗动判断——日支冲本卦静爻 | 🟢 |
| 01.7 | `backend/core/shi_ying.py` | B4: 世应定位——8种宫位类型的世应位置表 | 🟡 |
| 01.8 | `backend/core/fushen_zengshan.py` | B4: 增删伏神——缺失六亲→查本宫卦→飞伏关系 | 🔴 👤 |
| 01.9 | `backend/core/fushen_yimao.py` | B4: 易冒伏神——4种卦类型不同规则，384条 | 🔴 👤 |
| 01.10 | `backend/core/shensha.py` | B5: 神煞计算（干禄/驿马/羊刃/桃花）+ 传播（是/带） | 🔴 👤 |
| 01.11 | `backend/core/gua_type.py` | B6: 特殊卦判断（六冲10个/六合8个/反吟/伏吟） | 🟡 |
| 01.12 | `backend/core/hugua.py` | B7: 互卦计算——取二三四爻+三四五爻重组 | 🟢 |
| 01.13 | `backend/core/bagong_bian.py` | B8: 八宫变化——一世变到归魂变，7种变化 | 🟡 |
| 01.14 | `backend/core/dizhi_relation.py` | B9: 地支关系——生克合冲/半合/三合/生旺墓绝 Python 参考实现 | 🔴 |
| 01.15 | `backend/tests/test_*.py` | 每个 core/ 模块对应一个测试文件 | 🔗 👤 |

**依赖关系**：

```
enums.py (01.1) ──→ 所有模块都依赖它
time_converter.py (01.2) ──→ liushen.py (01.5) / an_dong.py (01.6) / shensha.py (01.10)
najia.py (01.3) ──→ liuqin.py (01.4) / shi_ying.py (01.7) / gua_type.py (01.11)
liuqin.py (01.4) ──→ fushen_zengshan.py (01.8) / fushen_yimao.py (01.9)
dizhi_relation.py (01.14) ──→ shensha.py (01.10) / an_dong.py (01.6) / gua_type.py (01.11)
```

📦 可并行开发组：
- 组 A：01.2 (time_converter) + 01.5 (liushen) + 01.6 (an_dong)
- 组 B：01.3 (najia) + 01.7 (shi_ying) 完成后 → 01.4 (liuqin) + 01.11 (gua_type)
- 组 C：01.4 完成后 → 01.8 (fushen_zengshan) + 01.9 (fushen_yimao) 📦（两个伏神互不依赖）
- 组 D：01.14 (dizhi_relation) → 01.10 (shensha)
- 组 E：01.12 (hugua) + 01.13 (bagong_bian) 📦（互不依赖）

🔗 需联合测试：01.3 + 01.4 + 01.7 → 装卦后验证六亲和世应正确；01.10 + 01.5 + 01.6 → 同一卦例验证神煞传播和六神暗动。

👤 **用户审核重点**：
- 01.2 节气日期是否正确（节气当日即变月）
- 01.3 28 个乾坤卦的两套天干是否正确
- 01.4 六亲生克方向（爻克宫→官鬼，宫克爻→妻财）
- 01.8/01.9 两种伏神的区别和飞伏对应关系
- 01.10 神煞传播规则（"是"=本支="带"=冲或合）
- 01.14 三合局四个局的三个地支是否完整

---

### v0.2 — 数据导入 + 预计算服务

> 📖 设计文档：.C1卦例显示.md §二、.B核心算法.md §调用者与数据流向

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 02.1 | `backend/crud/guali.py` | 卦例主表 CRUD | 🟢 |
| 02.2 | `backend/crud/guali_time.py` | 时间扩展表 CRUD | 🟢 |
| 02.3 | `backend/crud/guali_yao.py` | 爻类扩展表 CRUD（20字段×6行） | 🟡 |
| 02.4 | `backend/crud/guali_shensha.py` | 神煞扩展表 CRUD（37字段） | 🟢 |
| 02.5 | `backend/crud/guali_gua.py` | 卦类扩展表 CRUD（14字段） | 🟢 |
| 02.6 | `backend/services/import_service.py` | JSON 解析、字段映射、dyaolist 转换、增量导入 | 🟡 👤 |
| 02.7 | `backend/services/precalculate_service.py` | **预计算调度中心**——串联 B1-B6 全部算法，结果分存 4 张 guali_* 表 | 🔴 👤 |
| 02.8 | `backend/api/routers/import_data.py` | POST /api/import/json + /api/import/manual + GET /api/import/status | 🟢 |

**依赖关系**：

```
crud/guali.py (02.1) ──→ 02.2 ~ 02.5 (guali_* CRUD) 📦 四个可并行
services/import_service.py (02.6) ──→ services/precalculate_service.py (02.7) ──→ core/* 全部 + crud/guali_* 
```

🔗 02.6 + 02.7 必须联合测试：导入一个真实 JSON → 预计算调度 → 验证 4 张 guali_* 表数据完整。

👤 **用户审核重点**：
- 02.6 dyaolist 转换是否正确（′○″× 四种符号）
- 02.6 占问时间提取（dTitle 中的 MM.DD + dIniTime 年份）
- 02.6 增量导入——第二次导入不应产生重复数据
- 02.7 预计算结果抽查——与已知卦例对照六亲/六神/神煞/暗动

---

### v0.3 — C1 卦例显示

> 📖 设计文档：.C1卦例显示.md

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 03.1 | `backend/services/guali_service.py` | 卦例列表查询（分页/搜索/标签筛选） + 详情拼装（5表JOIN） | 🟡 |
| 03.2 | `backend/services/tag_service.py` | 标签 CRUD + 树形结构 | 🟢 |
| 03.3 | `backend/crud/tag.py` | 标签表 CRUD | 🟢 |
| 03.4 | `backend/crud/bagong_gua.py` | 八宫卦序表查询（卦名→代码、代码→卦宫等） | 🟢 |
| 03.5 | `backend/crud/guaci.py` | 卦爻辞表查询 | 🟢 |
| 03.6 | `backend/api/routers/guali.py` | GET/PUT/DELETE /api/guali + 标签关联 | 🟢 |
| 03.7 | `backend/api/routers/tags.py` | GET/POST/PUT/DELETE /api/tags | 🟢 |
| 03.8 | `backend/schemas/guali.py` | 卦例请求/响应 Pydantic 模型 | 🟢 |
| 03.9 | `backend/schemas/tag.py` | 标签请求/响应 Pydantic 模型 | 🟢 |
| 03.10 | `frontend/src/views/GualiList.vue` | 左侧卦例列表——卡片展示、搜索、标签筛选、分页 | 🟡 |
| 03.11 | `frontend/src/views/GualiDetail.vue` | 右侧卦例详情——11列×6行卦象表格、编辑、标签 | 🔴 👤 |
| 03.12 | `frontend/src/views/GualiInput.vue` | 手动导入表单——卦名选择→代码转换 | 🟢 |
| 03.13 | `frontend/src/components/shared/GuaCiFloat.vue` | 共享卦爻辞浮窗——可拖动、可多开 | 🔵 |
| 03.14 | `frontend/src/api/index.js` | 前端 API 调用封装（axios） | 🟣 |
| 03.15 | `frontend/src/stores/index.js` | 全局状态（当前卦例、标签树等） | 🟡 |

**依赖关系**：

```
03.4 + 03.5 (基础CRUD) ──→ 03.1 (guali_service)
03.1 + 03.2 + 03.3 + 03.8 + 03.9 ──→ 03.6 + 03.7 (API)
03.6 + 03.7 ──→ 03.10 + 03.11 + 03.12 (前端页面)
03.13 (GuaCiFloat) ──→ 03.11 引用，也供 C2/C3/C4 使用
```

📦 可并行开发组：
- 后端：03.3 + 03.4 + 03.5（基础CRUD，互不依赖）
- 后端：03.1 + 03.2 + 03.8 + 03.9 → 03.6 + 03.7
- 前端：03.10 + 03.12 可并行；03.11 依赖 03.13

🔗 前后端联调：03.6 + 03.7 完成后，前端 03.10 → 03.14 → 03.6 形成完整链路。

👤 **用户审核重点**：
- 03.11 卦象显示——11 列数据是否与设计一致（六神/六亲/地支/天干/世应/动暗/伏神/卦象/之卦六亲/之卦地支/之卦卦象）
- 03.11 天干显示开关——开关打开后"甲子"而非"子"
- 03.11 世应标记、动爻○、暗动△ 是否正确
- 03.13 GuaCiFloat 浮窗——点击卦名触发、可拖动、可多开、内容完整（卦辞/彖传/象传/爻辞）
- 03.12 手动导入——输入本卦名+之卦名→正确计算爻变代码和之卦代码

---

### v0.4 — C3 复杂检索

> 📖 设计文档：.C31复杂检索技术方案.md、.C32预存表设计.md、.C33前端字段构建方案.md、.C33-1前端字段构建方案附录.md

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 04.1 | `backend/schemas/search.py` | 检索请求/响应 Schema——Condition、LogicItem、SearchRequest | 🟡 |
| 04.2 | `backend/services/search_service.py` | **检索核心**——条件解析、SQL 动态组装、存储函数调用 | 🔴 👤 |
| 04.3 | `backend/services/export_service.py` | 检索结果导出（CSV/JSON） | 🟢 |
| 04.4 | `backend/api/routers/search.py` | POST /api/search + GET /api/search/schemes + POST /api/search/export | 🟢 |
| 04.5 | `frontend/src/stores/useSearchStore.js` | Pinia 检索状态管理——conditions、logicChain、results、pagination | 🟡 |
| 04.6 | `frontend/src/components/Search/ConditionBuilder.vue` | **条件构建器**——字段选择、运算符、值输入、条件组 | 🔴 👤 |
| 04.7 | `frontend/src/components/Search/FieldLibrary.vue` | 字段库面板——时间/卦类/爻属性/关系/神煞/数目字段分类 | 🟡 |
| 04.8 | `frontend/src/components/Search/ResultList.vue` | 检索结果列表——分页、排序、卦名点击弹出 GuaCiFloat | 🟢 |
| 04.9 | `frontend/src/components/Search/CompareMode.vue` | 对比模式——两组结果并排显示 | 🟢 |
| 04.10 | `frontend/src/components/Search/RecommendedSchemes.vue` | 推荐方案——预设检索模板 | 🟢 |
| 04.11 | `frontend/src/components/Search/WindowManager.vue` | 浮窗管理器——多结果浮窗协调 | 🟢 |
| 04.12 | `frontend/src/views/Search.vue` | 检索主页面——组合以上所有组件 | 🟡 |

**依赖关系**：

```
04.1 (schema) ──→ 04.2 (search_service) ──→ 04.4 (API)
04.5 (store) ──→ 04.6 + 04.7 + 04.8 (组件)
04.6 + 04.7 + 04.8 + 04.9 + 04.10 + 04.11 ──→ 04.12 (Search.vue)
04.4 (API) ←── 04.12 通过 04.5 → 04.14 调用
```

📦 可并行开发组：
- 后端：04.1 → 04.2 + 04.3 📦 → 04.4
- 前端：04.5 → 04.6 + 04.7 + 04.8 + 04.9 + 04.10 + 04.11 📦（六个组件互不依赖）→ 04.12

🔗 04.2 依赖 db/stored_functions/ 全部 8 个函数和 guali_* 表全部索引。必须在 v0.0（存储函数）和 v0.2（预存表有数据）完成后才能开始。

👤 **用户审核重点**：
- 04.2 SQL 生成的正确性——不同条件类型生成不同 SQL 结构
- 04.6 条件构建器交互——条件组的 OR/AND 逻辑是否正确
- 04.6 关系字段——生克/合冲/半合/三合/生旺墓绝 各类型的交互模板
- 04.6 神煞字段——"是/带/是或带"三种选项
- 04.6 数目判断——运算符（=/≠/>/</≥/≤/范围）

---

### v0.5 — C2 解卦模块

> 📖 设计文档：.C2解卦模块.md

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 05.1 | `backend/services/` (复用 core/) | 八宫变化和互卦直接调用 core/bagong_bian.py 和 core/hugua.py | 🟢 |
| 05.2 | `backend/api/routers/bagong.py` | GET /api/jiegua/bagong/{gua_code} | 🟢 |
| 05.3 | `backend/api/routers/jiegua.py` | GET /api/jiegua/hugua/{gua_code} + /graph/{type} + /guaci/{code} | 🟢 |
| 05.4 | `frontend/src/views/` (八宫变化页) | 八宫变化展示——7卦图形+网络图谱 | 🟡 👤 |
| 05.5 | `frontend/src/views/` (互卦页) | 互卦展示——本卦互卦+之卦互卦 | 🟢 |
| 05.6 | `frontend/src/views/` (网络图谱页) | 力导向布局图谱 | 🟡 |

**特点**：C2 是相对独立的模块，核心算法已在 v0.1 完成。本里程碑主要是前端可视化页面 + 简单 API 路由。依赖 guali 表和 bagong_gua 表数据。

📦 05.4 + 05.5 + 05.6 三个页面可并行开发。

---

### v0.6 — C4 股票关联

> 📖 设计文档：.C4股票关联.md

| # | 文件 | 说明 | 标记 |
|:--:|------|------|:--:|
| 06.1 | `backend/crud/stock_info.py` | 股票信息 CRUD | 🟢 |
| 06.2 | `backend/crud/stock_day_kline.py` | 日K数据 CRUD | 🟢 |
| 06.3 | `backend/crud/stock_minute_kline.py` | 股票分钟K CRUD（OHLC） | 🟢 |
| 06.4 | `backend/models/stock_*.py` | 股票三表 SQLModel 定义 | 🟢 |
| 06.5 | `backend/services/stock_data_service.py` | AKShare 数据获取 + 增量更新 + 限流（0.5 QPS） | 🟡 👤 |
| 06.6 | `backend/services/market_service.py` | K线查询 + **农历月K/年K聚合**（节气范围） + 卦例匹配 | 🔴 👤 |
| 06.7 | `backend/services/zhanyan_service.py` | 占验标签管理（增/删/改 guali_tag） | 🟢 |
| 06.8 | `backend/api/routers/stock.py` | 9 个股票相关端点 | 🟢 |
| 06.9 | `backend/schemas/stock.py` | 股票请求/响应 Schema | 🟢 |
| 06.10 | `frontend/src/views/StockAnalysis.vue` | 股票管理 + K线图主界面 | 🔴 👤 |
| 06.11 | `frontend/src/components/Stock/KlineChart.vue` | ECharts K线图——三种样式（空心/实心/灰底）+ 双击浮窗 | 🔴 👤 |
| 06.12 | `frontend/src/components/Stock/IntradayChart.vue` | 分时图浮窗 | 🟢 |
| 06.13 | `frontend/src/components/Stock/GualiFloatPanel.vue` | 卦例详情浮窗——复用 C1 5 表查询，含天干开关 | 🟡 |

**依赖关系**：

```
06.1 + 06.2 + 06.3 + 06.4 (股票基础CRUD) ──→ 06.5 (数据获取)
06.5 ──→ 06.6 (K线+聚合)
06.6 + 06.7 ──→ 06.8 + 06.9 (API)
06.10 ──→ 06.11 + 06.12 + 06.13 (组件)
```

📦 可并行开发组：
- 后端：06.1+06.2+06.3+06.4 → 06.5 + 06.7 📦 → 06.6 → 06.8+06.9
- 前端：06.11 + 06.12 + 06.13 📦 → 06.10

🔗 06.6 依赖 B1 的 `get_jieqi_dates()`（已在 v0.1 完成）和 stock_day_kline 表数据。
🔗 06.10 的 K线图需要 06.8 的 klines 端点返回数据后才能联调。

👤 **用户审核重点**：
- 06.5 AKShare 数据获取——首次添加标的时数据是否完整
- 06.6 农历月K聚合——节气范围是否正确（如卯月=惊蛰→清明）
- 06.6 卦例匹配——日卦/月卦/年卦与 K 线的对应关系
- 06.11 K线三种样式——应验/待验/无卦例的区分是否清晰
- 06.13 浮窗数据与 C1 是否一致（复用同一查询逻辑）

---

## 四、跨模块共享单元

以下文件被多个模块依赖，开发时需要注意修改的影响范围：

| 文件 | 被依赖方 | 修改影响 |
|------|---------|---------|
| `backend/core/enums.py` | 全部模块 | 新增枚举值需检查所有引用处 |
| `backend/core/time_converter.py` | C1(导入)、C4(月K聚合) | 修改干支规则影响所有卦例时间 |
| `backend/crud/guali.py` | C1、C2、C3、C4 | 修改查询逻辑影响全部四模块 |
| `backend/crud/guali_yao.py` | C1、C3、C4 | 浮窗+检索都依赖此表 |
| `backend/db/stored_functions/*.sql` | C3 | 函数签名变更需同步更新 search_service |
| `frontend/src/components/shared/GuaCiFloat.vue` | C1、C2、C3、C4 | 修改影响全部四模块的卦爻辞浮窗 |
| `frontend/src/api/index.js` | 全部前端页面 | API 封装变更影响所有页面 |
| `frontend/src/stores/` | C1(全局)、C3(检索) | store 结构调整影响相关组件 |

---

## 五、测试策略概要

### 5.1 单元测试（AI 负责）

每个 `backend/core/*.py` 完成后立即写对应 `backend/tests/test_*.py`。测试要点：
- 输入边界值（如日柱为甲子旬边界）
- 查表结果与已知对照表一致（如抽查 5 个卦的纳甲地支）
- 错误输入的处理

### 5.2 集成测试（AI + 用户）

- **v0.1→v0.2 衔接**：导入一个已知卦例的 JSON → 预计算 → 人工核对 guali_yao 表中六亲/六神/世应/暗动
- **v0.2→v0.3 衔接**：C1 详情页显示的数据与预存表是否一致
- **v0.4 独立验证**：选 5 个典型检索条件（动爻带神煞、世爻是驿马、本卦六冲等），手动验证结果
- **v0.6 独立验证**：添加一只股票 → 导入历史数据 → 关联卦例 → 检查 K 线样式

### 5.3 用户测试（每个里程碑完成后）

用户在实际浏览器中按验收标准逐条测试。发现问题写在 GitHub Issue 中（或在对应 Issue 下评论），AI 切 `fix/issue-N` 分支修复。

---

## 六、快速索引

| 我想了解... | 看哪个设计文档 |
|-----------|-------------|
| 数据库有哪些表、字段、索引 | .A1数据库设计.md |
| 后端怎么分层、API 有哪些 | .A2后端架构.md |
| 六爻算法怎么算（纳甲/六亲/神煞...） | .B核心算法.md |
| 卦例怎么导入和显示 | .C1卦例显示.md |
| 八宫变化和互卦怎么做 | .C2解卦模块.md |
| 复杂检索怎么查 | .C31 + .C32 + .C33 + .C33-1 |
| 股票 K 线怎么和卦例关联 | .C4股票关联.md |
| 整个项目现在是什么状态 | .Z项目总结.md |

---

*文档版本：v1.0*
*创建时间：2026-05-09*
*用途：项目开发蓝图，与 .AIDiscuss/ 设计文档配合使用*
