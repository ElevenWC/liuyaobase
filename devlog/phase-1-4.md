# 阶段1-4：核心枚举、业务类、时间转换、纳甲装卦

---

## 阶段一：核心枚举定义

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 1.1 五行枚举 | ✓ | 木、火、土、金、水 + 相生相克 |
| 1.2 天干枚举 | ✓ | 甲乙丙丁戊己庚辛壬癸 + 五行 |
| 1.3 地支枚举 | ✓ | 子丑寅卯辰巳午未申酉戌亥 + 五行 |
| 1.4 地支相合 | ✓ | 子丑、寅亥、卯戌、辰酉、巳申、午未 |
| 1.5 地支相冲 | ✓ | 子午、丑未、寅申、卯酉、辰戌、巳亥 |
| 1.6 地支三合局 | ✓ | 申子辰水、亥卯未木、寅午戌火、巳酉丑金 |
| 1.7 单卦枚举 | ✓ | 乾坤震巽坎离艮兑 + 3位代码 |
| 1.8 重卦枚举 | ✓ | 64卦 + 6位代码 + 八宫归属 |
| 1.9 代码解析 | ✓ | from_code, from_name |
| 1.10 六亲枚举 | ✓ | 父母、官鬼、子孙、妻财、兄弟 |
| 1.11 六神枚举 | ✓ | 青龙、朱雀、勾陈、螣蛇、白虎、玄武 |
| 1.12 神煞枚举 | ✓ | 干禄、驿马、羊刃、桃花 |

### 核心数据结构

**五行相生**: 金→水→木→火→土→金
**五行相克**: 金→木→土→水→火→金

**单卦代码**: 乾(111) 兑(110) 离(101) 震(100) 巽(011) 坎(010) 艮(001) 坤(000)

**重卦代码**: 高3位=内卦，低3位=外卦

### 文件
- `backend/core/enums.py` (~700行)
- `backend/tests/test_enums.py` (~500行)

---

## 阶段二：核心业务类实现

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 2.1 Yao类基础 | ✓ | dataclass定义 |
| 2.2 Yao类wuxing属性 | ✓ | 从地支获取 |
| 2.3 Guali类基础 | ✓ | 完整属性定义 |
| 2.4 Guali类爻列表初始化 | ✓ | 自动初始化6个爻 |

### Yao类属性
```python
@dataclass
class Yao:
    position: int      # 1-6
    yao_type: int      # 1=阳, 0=阴
    state: int         # 1=动, 0=静
    dizhi: Dizhi       # 爻地支
    liuqin: LiuQin     # 六亲
    liushen: LiuShen   # 六神
    is_world: bool     # 是否世爻
    is_response: bool  # 是否应爻
```

### Guali类属性
```python
@dataclass
class Guali:
    id: int
    solar_year, solar_month, solar_day: int  # 公历
    ganzhi_year, ganzhi_month, ganzhi_day: str  # 干支
    xunkong: str
    ben_gua: ZhongGua
    zhi_gua: ZhongGua
    yao_bian_code: int
    zhan_wen, zhan_duan: str
    yaos: List[Yao]
```

### Guali类方法
- `set_nama()` - 纳甲装卦
- `set_shiying()` - 世应设置
- `set_liuqin()` - 六亲计算
- `set_liushen()` - 六神设置
- `calculate_all()` - 计算所有派生属性

### 文件
- `backend/core/models.py`
- `backend/tests/test_models.py`

---

## 阶段三：时间转换模块

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 3.1 lunar-python集成 | ✓ | 库可用性检查 |
| 3.2 公历转年柱 | ✓ | solar_to_ganzhi_year |
| 3.3 公历转月柱 | ✓ | solar_to_ganzhi_month |
| 3.4 公历转日柱 | ✓ | solar_to_ganzhi_day |
| 3.5 旬空计算 | ✓ | get_xunkong |
| 3.6 完整时间转换 | ✓ | solar_to_ganzhi_full |
| 3.7 日干日支提取 | ✓ | extract_tiangan_dizhi |

### 核心函数
```python
solar_to_ganzhi_full(2024, 2, 12)
# 返回: {"year": "甲辰", "month": "丙寅", "day": "丙午", "xunkong": "寅卯"}
```

### 文件
- `backend/core/time_converter.py`
- `backend/tests/test_time_converter.py`

---

## 阶段四：纳甲装卦模块

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 4.1 映射表定义 | ✓ | NAMA_DIZHI_NEIGUA/WAIGUA |
| 4.2 获取地支 | ✓ | get_dizhi_from_dan_gua |
| 4.3 重卦装地支 | ✓ | load_dizhi_to_guali |
| 4.4 Guali集成 | ✓ | set_nama方法 |

### 纳甲装卦规则

| 单卦 | 内卦(初二三) | 外卦(四五上) |
|------|-------------|-------------|
| 乾 | 子寅辰 | 午申戌 |
| 震 | 子寅辰 | 午申戌 |
| 坎 | 寅辰午 | 申戌子 |
| 艮 | 辰午申 | 戌子寅 |
| 坤 | 未巳卯 | 丑亥酉 |
| 巽 | 丑亥酉 | 未巳卯 |
| 离 | 卯丑亥 | 酉未巳 |
| 兑 | 巳卯丑 | 亥酉未 |

### 文件
- `backend/core/nama.py`
- `backend/tests/test_nama.py`
