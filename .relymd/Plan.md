# 六爻卦例分析系统技术路线与开发流程规划

## 一、项目概述

### 1.1 项目目标
构建一个卦例分析系统，实现卦例的录入、存储、查看和复杂检索功能，并能与股票K线图结合展示。

### 1.2 核心功能模块
| 模块 | 功能描述 |
|------|----------|
| 卦例输入 | 手动输入/CSV批量导入 |
| 格式转换 | 标准格式 → 编码格式 |
| 数据库存储 | MySQL存储编码格式卦例 |
| 单卦例查看 | 详细信息展示（含图片） |
| 复杂检索 | 多条件批量查找卦例 |
| ECharts接口 | 与股票K线图结合 |

---

## 二、技术架构

### 2.1 技术栈选型

| 层次 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue 3 + Element Plus | 现代化UI框架 |
| 后端 | Python + FastAPI | 高性能异步框架 |
| 数据库 | MySQL 8.0 | 关系型数据库 |
| 日历库 | lunar-python | 公历干支转换 |
| 可视化 | ECharts | 股票K线图展示 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                        用户界面层                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │手动输入  │  │CSV导入   │  │卦例查看  │  │复杂检索│  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                        API接口层                        │
│              FastAPI RESTful API接口                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                        业务逻辑层                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │格式转换  │  │卦理计算  │  │检索逻辑  │  │股票映射│  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                        数据访问层                        │
│              SQLAlchemy ORM + 数据库操作                 │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    数据持久层                            │
│              MySQL数据库 + 文件系统(图片)                │
└─────────────────────────────────────────────────────────┘
```

---

## 三、核心数据模型

### 3.1 基础枚举与常量

```python
# 五行枚举
class Wuxing(Enum):
    MU = "木"
    HUO = "火"
    TU = "土"
    JIN = "金"
    SHUI = "水"

    # 五行生克关系
    def generates(self, other) -> bool: ...
    def overcomes(self, other) -> bool: ...

# 地支枚举
class Dizhi(Enum):
    ZI = "子"
    CHOU = "丑"
    YIN = "寅"
    MAO = "卯"
    CHEN = "辰"
    SI = "巳"
    WU = "午"
    WEI = "未"
    SHEN = "申"
    YOU = "酉"
    XU = "戌"
    HAI = "亥"

    @property
    def wuxing(self) -> Wuxing: ...

# 天干枚举
class Tiangan(Enum):
    JIA = "甲"
    YI = "乙"
    BING = "丙"
    DING = "丁"
    WU = "戊"
    JI = "己"
    GENG = "庚"
    XIN = "辛"
    REN = "壬"
    GUI = "癸"

# 单卦枚举（8个）
class DanGua(Enum):
    QIAN = (111, "乾")
    DUI = (110, "兑")
    LI = (101, "离")
    ZHEN = (100, "震")
    XUN = (011, "巽")
    KAN = (010, "坎")
    GEN = (001, "艮")
    KUN = (000, "坤")

    @property
    def wuxing(self) -> Wuxing: ...

# 重卦枚举（64个）
class ZhongGua(Enum):
    QIAN_WEI_TIAN = (111111, "乾为天", DanGua.QIAN, DanGua.QIAN, "乾宫", "本宫")
    ... (共64个)

    @property
    def code(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def neigua(self) -> DanGua: ...
    @property
    def waigua(self) -> DanGua: ...
    @property
    def gongwei(self) -> str: ...
    @property
    def gongwuxing(self) -> Wuxing: ...

# 六亲枚举
class LiuQin(Enum):
    FU_MU = "父母"
    GUAN_GUI = "官鬼"
    ZI_SUN = "子孙"
    QI_CAI = "妻财"
    XIONG_DI = "兄弟"

# 六神枚举
class LiuShen(Enum):
    QING_LONG = "青龙"
    ZHU_QUE = "朱雀"
    GOU_CHEN = "勾陈"
    TENG_SHE = "螣蛇"
    BAI_HU = "白虎"
    XUAN_WU = "玄武"

# 神煞枚举
class ShenSha(Enum):
    GAN_LU = "干禄"
    YI_MA = "驿马"
    YANG_REN = "羊刃"
    TAO_HUA = "桃花"
```

### 3.2 核心类设计

```python
# 爻类
class Yao:
    position: int           # 爻位：1-6（初爻到上爻）
    yao_type: int           # 爻类型：1=阳爻，0=阴爻
    state: int              # 爻状态：1=动爻，0=静爻
    dizhi: Dizhi            # 地支（纳甲装卦）
    liuqin: Optional[LiuQin]  # 六亲
    liushen: Optional[LiuShen] # 六神
    is_world: bool          # 是否世爻
    is_response: bool       # 是否应爻

    @property
    def wuxing(self) -> Wuxing: ...

# 卦例类
class Guali:
    # 基础信息
    id: int
    time_solar: datetime    # 公历时间
    time_ganzhi: dict       # 干支时间 {年柱, 月柱, 日柱, 旬空}
    ben_gua: ZhongGua       # 本卦
    zhi_gua: Optional[ZhongGua]  # 之卦
    yao_bian_code: int      # 爻变代码（6位二进制）

    # 爻信息
    yaos: List[Yao]         # 六爻列表
    changing_yaos: List[Yao] # 动爻/变爻列表

    # 六亲与伏神
    fu_shen: Dict[LiuQin, List[Yao]]  # 伏神映射 {六亲: [伏神爻]}

    # 卦理属性
    fan_yin: Dict[str, List[str]]  # 反吟 {内卦/外卦: [易冒/爻变]}
    fu_yin: Dict[str, List[str]]   # 伏吟 {内卦/外卦: []}

    # 神煞
    shensha: Dict[ShenSha, List[Dizhi]]  # 神煞映射 {神煞: [地支]}

    # 文本信息
    zhan_wen: str            # 占问事由
    zhan_duan: str           # 占断
    image_path: str          # 图片路径

    def calculate_all(self) -> None:
        """计算所有卦理属性"""
        self._calculate_ganzhi()
        self._calculate_yaos()
        self._calculate_liuqin()
        self._calculate_fushen()
        self._calculate_fanyin_fuyin()
        self._calculate_liushen()
        self._calculate_shensha()
```

### 3.3 数据库表设计

```sql
-- 卦例表
CREATE TABLE guali (
    id INT PRIMARY KEY AUTO_INCREMENT,
    solar_year INT NOT NULL COMMENT '公历年',
    solar_month INT NOT NULL COMMENT '公历月',
    solar_day INT NOT NULL COMMENT '公历日',
    ganzhi_year VARCHAR(4) NOT NULL COMMENT '年柱(干支)',
    ganzhi_month VARCHAR(4) NOT NULL COMMENT '月柱(干支)',
    ganzhi_day VARCHAR(4) NOT NULL COMMENT '日柱(干支)',
    xunkong VARCHAR(8) NOT NULL COMMENT '旬空',
    ben_gua_code INT NOT NULL COMMENT '本卦代码(6位)',
    zhi_gua_code INT COMMENT '之卦代码(6位)',
    yao_bian_code INT NOT NULL DEFAULT 0 COMMENT '爻变代码(6位)',
    gongwei VARCHAR(8) NOT NULL COMMENT '卦宫',
    gongwei_index VARCHAR(8) NOT NULL COMMENT '宫位',
    zhan_wen TEXT COMMENT '占问事由',
    zhan_duan TEXT COMMENT '占断',
    image_path VARCHAR(512) COMMENT '图片路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_time (solar_year, solar_month, solar_day),
    INDEX idx_gua (ben_gua_code, zhi_gua_code),
    INDEX idx_gongwei (gongwei)
);

-- 爻详情表（可选，用于快速检索）
CREATE TABLE yao_detail (
    id INT PRIMARY KEY AUTO_INCREMENT,
    guali_id INT NOT NULL,
    position INT NOT NULL COMMENT '爻位1-6',
    yao_type INT NOT NULL COMMENT '爻类型1=阳0=阴',
    state INT NOT NULL DEFAULT 0 COMMENT '爻状态1=动0=静',
    dizhi VARCHAR(4) NOT NULL COMMENT '地支',
    liuqin VARCHAR(8) COMMENT '六亲',
    liushen VARCHAR(8) COMMENT '六神',
    is_world BOOLEAN DEFAULT FALSE COMMENT '是否世爻',
    is_response BOOLEAN DEFAULT FALSE COMMENT '是否应爻',

    FOREIGN KEY (guali_id) REFERENCES guali(id),
    INDEX idx_guali_id (guali_id),
    INDEX idx_dizhi (dizhi),
    INDEX idx_liuqin (liuqin)
);
```

---

## 四、开发阶段规划

### 第一阶段：基础框架搭建（Week 1-2）

| 任务 | 内容 | 产出 |
|------|------|------|
| 项目初始化 | 创建前后端项目结构、配置开发环境 | 项目骨架 |
| 数据库设计 | 创建数据库表、编写ORM模型 | SQL脚本、模型文件 |
| API框架 | 搭建FastAPI基础接口 | 基础API端点 |
| 前端框架 | 搭建Vue3项目、配置路由 | 基础前端页面 |

### 第二阶段：核心数据结构实现（Week 3-4）

| 任务 | 内容 | 产出 |
|------|------|------|
| 枚举定义 | 实现五行、地支、天干、单卦、重卦等枚举 | 枚举模块 |
| 五行系统 | 实现五行生克关系判断 | Wuxing类 |
| 卦理基础 | 实现重卦、爻位、世应定位 | ZhongGua类 |
| 地支系统 | 实现地支相合、相冲、三合局判断 | Dizhi类 |

### 第三阶段：格式转换与计算引擎（Week 5-7）

| 任务 | 内容 | 产出 |
|------|------|------|
| 时间转换 | 集成lunar-python，实现公历→干支转换 | 时间转换模块 |
| 纳甲装卦 | 实现爻与地支的映射关系 | 纳甲装卦函数 |
| 六亲计算 | 实现卦宫五行与爻地支五行生克判断 | 六亲计算模块 |
| 六神计算 | 根据日干计算各爻六神 | 六神计算模块 |
| 伏神计算 | 实现伏神查找逻辑 | 伏神计算模块 |
| 反吟伏吟 | 实现反吟、伏吟判断 | 反吟伏吟判断模块 |
| 神煞计算 | 实现干禄、驿马、羊刃、桃花计算 | 神煞计算模块 |

### 第四阶段：输入功能开发（Week 8-10）

| 任务 | 内容 | 产出 |
|------|------|------|
| 手动输入界面 | 前端表单、后端验证接口 | 输入页面 |
| CSV导入 | 前端上传、后端解析处理 | 批量导入功能 |
| 格式验证 | 标准格式验证与错误提示 | 验证模块 |
| 图片存储 | 图片上传、路径映射 | 图片存储模块 |

### 第五阶段：输出查看功能（Week 11-12）

| 任务 | 内容 | 产出 |
|------|------|------|
| 卦例列表 | 展示所有卦例概览 | 列表页面 |
| 详情展示 | 单卦例详细信息展示 | 详情页面 |
| 图片展示 | 关联图片显示 | 图片组件 |

### 第六阶段：复杂检索功能（Week 13-15）

| 任务 | 内容 | 产出 |
|------|------|------|
| 检索界面 | 多条件筛选界面 | 检索页面 |
| 检索逻辑 | 实现复杂关系检索 | 检索引擎 |
| 多窗口展示 | 批量结果多窗口查看 | 结果展示组件 |

### 第七阶段：ECharts集成（Week 16）

| 任务 | 内容 | 产出 |
|------|------|------|
| 股票接口 | 获取股票K线数据 | 股票数据模块 |
| K线展示 | ECharts K线图 | K线组件 |
| 关联展示 | 卦例与K线联动 | 联动模块 |
| 关键词匹配 | 从占问事由提取股票名称 | 关键词匹配模块 |

### 第八阶段：测试与优化（Week 17-18）

| 任务 | 内容 |
|------|------|
| 单元测试 | 核心算法测试 |
| 集成测试 | 完整流程测试 |
| 性能优化 | 数据库查询优化 |
| 部署准备 | 生产环境配置 |

---

## 五、关键技术实现要点

### 5.1 五行生克关系

```python
# 五行生克映射表
WUXING_SHENG = {
    Wuxing.JIN: Wuxing.SHUI,
    Wuxing.SHUI: Wuxing.MU,
    Wuxing.MU: Wuxing.HUO,
    Wuxing.HUO: Wuxing.TU,
    Wuxing.TU: Wuxing.JIN,
}

WUXING_KE = {
    Wuxing.JIN: Wuxing.MU,
    Wuxing.MU: Wuxing.TU,
    Wuxing.TU: Wuxing.SHUI,
    Wuxing.SHUI: Wuxing.HUO,
    Wuxing.HUO: Wuxing.JIN,
}
```

### 5.2 地支相合相冲

```python
# 地支相合
DIZHI_HE = {
    Dizhi.ZI: Dizhi.CHOU, Dizhi.CHOU: Dizhi.ZI,
    Dizhi.YIN: Dizhi.HAI, Dizhi.HAI: Dizhi.YIN,
    Dizhi.MAO: Dizhi.XU, Dizhi.XU: Dizhi.MAO,
    Dizhi.CHEN: Dizhi.YOU, Dizhi.YOU: Dizhi.CHEN,
    Dizhi.SI: Dizhi.SHEN, Dizhi.SHEN: Dizhi.SI,
    Dizhi.WU: Dizhi.WEI, Dizhi.WEI: Dizhi.WU,
}

# 地支相冲
DIZHI_CHONG = {
    Dizhi.ZI: Dizhi.WU, Dizhi.WU: Dizhi.ZI,
    Dizhi.CHOU: Dizhi.WEI, Dizhi.WEI: Dizhi.CHOU,
    Dizhi.YIN: Dizhi.SHEN, Dizhi.SHEN: Dizhi.YIN,
    Dizhi.MAO: Dizhi.YOU, Dizhi.YOU: Dizhi.MAO,
    Dizhi.CHEN: Dizhi.XU, Dizhi.XU: Dizhi.CHEN,
    Dizhi.SI: Dizhi.HAI, Dizhi.HAI: Dizhi.SI,
}
```

### 5.3 纳甲装卦映射

```python
# 单卦地支映射（内卦、外卦）
NAMA_DIZHI = {
    # 内卦：初爻、二爻、三爻
    DanGua.QIAN: (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN),
    DanGua.DUI: (Dizhi.SI, Dizhi.MAO, Dizhi.CHOU),
    DanGua.LI: (Dizhi.MAO, Dizhi.CHOU, Dizhi.HAI),
    DanGua.ZHEN: (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN),
    DanGua.XUN: (Dizhi.CHOU, Dizhi.HAI, Dizhi.YOU),
    DanGua.KAN: (Dizhi.YIN, Dizhi.CHEN, Dizhi.WU),
    DanGua.GEN: (Dizhi.CHEN, Dizhi.WU, Dizhi.SHEN),
    DanGua.KUN: (Dizhi.WEI, Dizhi.SI, Dizhi.MAO),
}
```

### 5.4 世应定位

```python
# 宫位到世应爻位映射
SHI_YING_MAP = {
    "本宫": (6, 3),    # 世在上爻，应在三爻
    "一世": (1, 4),    # 世在初爻，应在四爻
    "二世": (2, 5),
    "三世": (3, 6),
    "四世": (4, 1),
    "五世": (5, 2),
    "游魂": (4, 1),
    "归魂": (3, 6),
}
```

---

## 六、目录结构规划

```
liuyaobase/
├── backend/
│   ├── api/                    # API接口层
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI入口
│   │   ├── schemas.py         # Pydantic模型
│   │   └── routers/           # 路由
│   │       ├── __init__.py
│   │       ├── guali.py       # 卦例接口
│   │       ├── images.py      # 图片接口
│   │       ├── search.py      # 检索接口
│   │       ├── yanqing.py     # 占验情况接口
│   │       └── stock.py       # 股票数据接口（阶段二十八）
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── enums.py           # 枚举定义
│   │   ├── models.py          # 业务数据模型
│   │   ├── time_converter.py  # 时间转换
│   │   ├── nama.py            # 纳甲装卦
│   │   ├── wuxing_helper.py   # 五行辅助
│   │   ├── liushen.py         # 六神计算
│   │   ├── shiying.py         # 世应定位
│   │   ├── fushen.py          # 伏神计算
│   │   ├── fanyin_fuyin.py    # 反吟伏吟
│   │   ├── shensha.py         # 神煞计算
│   │   ├── shengwang_mujue.py # 生旺墓绝
│   │   └── converter.py       # 格式转换
│   ├── db/                     # 数据访问层
│   │   ├── __init__.py
│   │   ├── connection.py      # 数据库连接
│   │   ├── models.py          # SQLAlchemy模型
│   │   └── repositories.py    # 数据仓库CRUD
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   └── yanqing_service.py # 占验情况服务
│   ├── utils/                  # 工具类
│   │   ├── __init__.py
│   │   └── validators.py      # 验证器
│   ├── config.py              # 配置模块
│   └── tests/                  # 测试文件
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js       # API调用模块
│   │   ├── components/
│   │   │   ├── NavBar.vue     # 导航菜单组件
│   │   │   ├── YanqingAnnotation.vue  # 占验标注组件
│   │   │   ├── Search/        # 复杂检索组件
│   │   │   │   ├── FieldLibrary.vue
│   │   │   │   ├── ConditionBuilder.vue
│   │   │   │   ├── RecommendedSchemes.vue
│   │   │   │   ├── ResultList.vue
│   │   │   │   ├── WindowManager.vue
│   │   │   │   └── CompareMode.vue
│   │   │   └── Stock/         # 股票分析组件（阶段二十八）
│   │   │       ├── KlineChart.vue
│   │   │       ├── IntradayChart.vue
│   │   │       └── GualiFloatPanel.vue
│   │   ├── router/
│   │   │   └── index.js       # 路由配置
│   │   ├── stores/
│   │   │   └── index.js       # Pinia状态管理
│   │   ├── views/
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── GualiInput.vue # 卦例录入
│   │   │   ├── CsvImport.vue  # CSV导入
│   │   │   ├── GualiList.vue  # 卦例列表
│   │   │   ├── GualiDetail.vue# 卦例详情
│   │   │   ├── Search.vue     # 复杂检索
│   │   │   ├── ImageConfig.vue# 图片配置
│   │   │   ├── StockAnalysis.vue  # 股票分析（阶段二十八）
│   │   │   └── NotFound.vue   # 404页面
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── vite.config.js
│   └── package.json
├── docs/                       # 文档
│   ├── 基本规则.md
│   ├── 编码规则.md
│   └── 输入输出查找规则.md
├── scripts/                    # 脚本
│   ├── init_db.py             # 数据库初始化
│   └── import_csv.py          # CSV导入
├── .relymd/                    # 规则与计划文档
│   ├── Plan.md
│   ├── TestPlan.md
│   ├── 股票-卦例显示规则.md
│   └── ...
├── requirements.txt
└── CLAUDE.md
```

---

## 七、ECharts集成与股票分析模块

### 7.1 股票数据来源
- **数据源**: Akshare（Python库）
- **安装**: `pip install akshare`
- **使用前**: 详细阅读Akshare使用文档

### 7.2 功能需求概览

| 功能 | 说明 |
|------|------|
| 日K图显示 | 同花顺风格，红色阳线，绿色阴线 |
| 横轴双时间 | 公历日期 + 月柱日柱干支 |
| K线点击 | 双击显示分时图浮窗和卦例浮窗 |
| 股票搜索 | 输入标准格式股票名称搜索 |
| 卦例关联 | 根据占问事由关键词匹配卦例 |
| 三种K线样式 | 无卦例/应验/模糊不验 |
| 多窗查看 | 支持多窗口对比不同股票 |
| 占验修改 | 在卦例浮窗中可修改占验情况 |
| **多卦例支持** | 一根K线对应多个卦例时，显示所有卦例，用户选择基准卦例决定K线颜色 |
| **占断编辑** | 在卦例浮窗和详情页可编辑占断字段并保存 |

### 7.3 多卦例支持与占断编辑

#### 7.3.1 多卦例场景处理
当一根K线对应多个卦例时：
1. **显示所有卦例**：在卦例浮窗中列出当日所有匹配的卦例
2. **基准卦例选择**：用户可选择其中一个卦例作为基准，该卦例的占验情况决定K线颜色
3. **其他卦例展示**：其余卦例在可展开的折叠面板中显示
4. **快速切换基准**：支持快速将其他卦例设为基准卦例

#### 7.3.2 占断字段编辑
支持在以下场景编辑占断字段：
- **卦例详情页**（GualiDetail.vue）：通过编辑对话框修改
- **卦例浮窗**（GualiFloatPanel.vue）：直接编辑主卦例或其他卦例的占断
- **复杂检索结果**：在查看详情时可编辑

#### 7.3.3 数据结构设计

```javascript
// 卦例映射数据结构（按日期分组）
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
      },
      {
        "id": 2,
        "zhan_wen": "占问股票操作",
        "zhan_duan": "占断持有",
        "ben_gua_name": "坤为地",
        "yanqing_status": "模糊"
      }
    ],
    "primary_guali_id": 1,  // 基准卦例ID
    "yanqing_status": "应验"  // K线颜色依据
  }
}
```

| 类型 | 样式 | 说明 |
|------|------|------|
| 无对应卦例 | 空心K线，红色阳线，绿色阴线 | 当日无匹配卦例 |
| 占验为"应验" | 实心K线，红色阳线，绿色阴线 | 卦例占验情况为应验 |
| 占验为"模糊"/"不验" | 空心K线+内部黄色填充，红色阳线，绿色阴线 | 卦例占验情况为模糊或不验 |

### 7.4 前端组件设计

```
frontend/src/
├── views/
│   └── StockAnalysis.vue       # 股票分析页面
├── components/
│   └── Stock/
│       ├── KlineChart.vue      # K线图组件
│       ├── IntradayChart.vue   # 分时图浮窗
│       └── GualiFloatPanel.vue # 卦例浮窗组件
```

### 7.5 后端API设计

```
backend/api/routers/stock.py
├── GET  /api/stock/search           # 股票搜索（名称/代码）
├── GET  /api/stock/kline            # K线数据获取
├── GET  /api/stock/intraday         # 分时数据获取
└── GET  /api/stock/guali-mapping    # 股票名称匹配卦例
```

### 7.6 数据缓存策略
- 不要频繁获取股票数据
- 后端实现数据缓存（建议使用内存缓存或Redis）
- 按需获取，用户搜索时才请求数据

### 7.7 性能优化建议
- ECharts启用large模式处理大数据量
- K线数据分页加载
- 分时数据懒加载
- 浮窗组件按需渲染

---

## 八、待确认事项

| 事项 | 说明 | 状态 |
|------|------|------|
| ~~复杂检索界面设计~~ | 需要专门文档规划检索条件和界面 | 已完成 |
| ~~股票数据来源~~ | 确认使用Akshare库 | 已确认 |
| 图片存储路径 | 需确认图片存储的默认路径 | 低优先级 |
| 部署环境 | 需确认生产环境配置 | 低优先级 |

---

## 九、开发建议

1. **核心算法优先**：优先实现卦理计算引擎，确保核心逻辑正确
2. **测试驱动**：每个计算模块都需要充分测试
3. **渐进式开发**：按阶段逐步实现功能，每阶段完成后进行验证
4. **文档完善**：保持代码注释和文档更新
5. **可扩展性**：考虑未来可能新增神煞或卦理规则，保持代码灵活性
