# 六爻卦例分析系统 - 最小可分割开发测试计划

## 说明

本计划将整个项目拆分为**最小可执行单元**，每个单元均可独立编码和测试。
每个单元完成并测试通过后，方可进行下一个单元的开发。

---

## 阶段零：环境准备与项目初始化

### 任务 0.1 - 后端项目结构创建
**目标**: 创建后端项目基础目录结构
**操作**:
- 创建 `backend/` 目录及子目录
  - `backend/api/`
  - `backend/core/`
  - `backend/db/`
  - `backend/services/`
  - `backend/utils/`
  - `backend/tests/`
- 创建各目录下的 `__init__.py` 文件
**测试**: 验证目录结构完整，各 `__init__.py` 可正常导入

---

### 任务 0.2 - 前端项目初始化
**目标**: 创建Vue3前端项目骨架
**操作**:
- 使用Vite创建Vue3项目到 `frontend/` 目录
- 安装Element Plus
- 安装Pinia状态管理
- 配置路由 vue-router
- 创建基础目录结构: `src/api/`, `src/components/`, `src/views/`, `src/router/`
**测试**:
- `npm run dev` 能正常启动
- 访问首页能显示欢迎信息

---

### 任务 0.3 - 后端依赖安装与配置
**目标**: 安装Python依赖并配置基础环境
**操作**:
- 创建 `backend/requirements.txt`
- 安装依赖: FastAPI, SQLAlchemy, PyMySQL, lunar-python, pytest
- 创建 `backend/.env` 配置文件模板
- 创建 `backend/config.py` 配置读取模块
**测试**:
- `pip install -r requirements.txt` 成功无报错
- 运行Python能导入所有依赖

---

### 任务 0.4 - 数据库连接配置
**目标**: 实现数据库连接功能
**操作**:
- 编写 `backend/db/connection.py`
- 实现数据库连接池配置
- 实现Session管理
- 创建数据库（如果不存在）
**测试**:
- 编写测试脚本 `tests/test_connection.py`
- 测试能成功连接数据库
- 测试能创建Session并正常关闭

---

## 阶段一：核心枚举定义（纯数据层）

### 任务 1.1 - 五行枚举实现
**目标**: 定义五行枚举及生克关系
**操作**:
- 创建 `backend/core/enums.py`
- 定义 `Wuxing` 枚举（木、火、土、金、水）
- 定义五行相生关系映射表 `WUXING_SHENG`
- 定义五行相克关系映射表 `WUXING_KE`
- 实现 `generates(other)` 方法
- 实现 `overcomes(other)` 方法
**测试**:
```python
# tests/test_enums_1_1.py
assert Wuxing.JIN.generates(Wuxing.SHUI) == True   # 金生水
assert Wuxing.SHUI.generates(Wuxing.MU) == True    # 水生木
assert Wuxing.MU.generates(Wuxing.HUO) == True     # 木生火
assert Wuxing.HUO.generates(Wuxing.TU) == True     # 火生土
assert Wuxing.TU.generates(Wuxing.JIN) == True      # 土生金
assert Wuxing.JIN.overcomes(Wuxing.MU) == True     # 金克木
# ... 测试所有组合
```

---

### 任务 1.2 - 天干枚举实现
**目标**: 定义天干枚举及其五行属性
**操作**:
- 在 `backend/core/enums.py` 中定义 `Tiangan` 枚举
- 为每个天干定义五行属性
- 实现 `wuxing` 属性
**测试**:
```python
# tests/test_enums_1_2.py
assert Tiangan.JIA.wuxing == Wuxing.MU
assert Tiangan.YI.wuxing == Wuxing.MU
assert Tiangan.BING.wuxing == Wuxing.HUO
assert Tiangan.DING.wuxing == Wuxing.HUO
# ... 测试所有天干
```

---

### 任务 1.3 - 地支枚举实现
**目标**: 定义地支枚举及其五行属性
**操作**:
- 在 `backend/core/enums.py` 中定义 `Dizhi` 枚举
- 为每个地支定义五行属性
- 实现 `wuxing` 属性
**测试**:
```python
# tests/test_enums_1_3.py
assert Dizhi.ZI.wuxing == Wuxing.SHUI
assert Dizhi.CHOU.wuxing == Wuxing.TU
assert Dizhi.YIN.wuxing == Wuxing.MU
# ... 测试所有地支
```

---

### 任务 1.4 - 地支相合关系实现
**目标**: 实现地支相合关系判断
**操作**:
- 在 `backend/core/enums.py` 中定义地支相合映射表 `DIZHI_HE`
- 实现判断方法 `is_he(other)`
**测试**:
```python
# tests/test_enums_1_4.py
assert Dizhi.ZI.is_he(Dizhi.CHOU) == True
assert Dizhi.YIN.is_he(Dizhi.HAI) == True
assert Dizhi.MAO.is_he(Dizhi.XU) == True
assert Dizhi.CHEN.is_he(Dizhi.YOU) == True
assert Dizhi.SI.is_he(Dizhi.SHEN) == True
assert Dizhi.WU.is_he(Dizhi.WEI) == True
assert Dizhi.ZI.is_he(Dizhi.WU) == False  # 子午不相合
```

---

### 任务 1.5 - 地支相冲关系实现
**目标**: 实现地支相冲关系判断
**操作**:
- 在 `backend/core/enums.py` 中定义地支相冲映射表 `DIZHI_CHONG`
- 实现判断方法 `is_chong(other)`
**测试**:
```python
# tests/test_enums_1_5.py
assert Dizhi.ZI.is_chong(Dizhi.WU) == True
assert Dizhi.CHOU.is_chong(Dizhi.WEI) == True
assert Dizhi.YIN.is_chong(Dizhi.SHEN) == True
assert Dizhi.MAO.is_chong(Dizhi.YOU) == True
assert Dizhi.CHEN.is_chong(Dizhi.XU) == True
assert Dizhi.SI.is_chong(Dizhi.HAI) == True
assert Dizhi.ZI.is_chong(Dizhi.CHOU) == False  # 子丑不相冲
```

---

### 任务 1.6 - 地支三合局关系实现
**目标**: 实现地支三合局关系判断
**操作**:
- 定义三合局映射表 `DIZHI_SANHE`
- 实现判断方法 `is_sanhe(other1, other2)`
- 实现获取三合局五行方法 `get_sanhe_wuxing()`
**测试**:
```python
# tests/test_enums_1_6.py
assert Dizhi.SHEN.is_sanhe(Dizhi.ZI, Dizhi.CHEN) == True
assert Dizhi.SHEN.get_sanhe_wuxing([Dizhi.ZI, Dizhi.CHEN]) == Wuxing.SHUI
assert Dizhi.HAI.is_sanhe(Dizhi.MAO, Dizhi.WEI) == True
assert Dizhi.YIN.is_sanhe(Dizhi.WU, Dizhi.XU) == True
assert Dizhi.SI.is_sanhe(Dizhi.YOU, Dizhi.CHOU) == True
```

---

### 任务 1.7 - 单卦枚举实现
**目标**: 定义八单卦枚举及其代码、五行属性
**操作**:
- 在 `backend/core/enums.py` 中定义 `DanGua` 枚举
- 为每个单卦定义代码值（3位二进制）
- 为每个单卦定义五行属性
- 实现 `code` 属性
- 实现 `wuxing` 属性
**测试**:
```python
# tests/test_enums_1_7.py
assert DanGua.QIAN.code == 111
assert DanGua.DUI.code == 110
assert DanGua.LI.code == 101
assert DanGua.ZHEN.code == 100
assert DanGua.XUN.code == 011
assert DanGua.KAN.code == 010
assert DanGua.GEN.code == 001
assert DanGua.KUN.code == 000

assert DanGua.KAN.wuxing == Wuxing.SHUI
assert DanGua.ZHEN.wuxing == Wuxing.MU
assert DanGua.XUN.wuxing == Wuxing.MU
# ... 测试所有单卦
```

---

### 任务 1.8 - 重卦枚举实现
**目标**: 定义六十四重卦枚举
**操作**:
- 在 `backend/core/enums.py` 中定义 `ZhongGua` 枚举
- 为每个重卦定义：
  - 代码值（6位二进制）
  - 卦名
  - 内卦（前3位对应的单卦）
  - 外卦（后3位对应的单卦）
  - 卦宫
  - 宫位
  - 卦宫五行
- 实现 `code`, `name`, `neigua`, `waigua`, `gongwei`, `gongwei_index`, `gongwuxing` 属性
**测试**:
```python
# tests/test_enums_1_8.py
gua = ZhongGua.QIAN_WEI_TIAN
assert gua.code == 111111
assert gua.name == "乾为天"
assert gua.neigua == DanGua.QIAN
assert gua.waigua == DanGua.QIAN
assert gua.gongwei == "乾宫"
assert gua.gongwei_index == "本宫"
assert gua.gongwuxing == Wuxing.JIN

# 测试所有64个重卦
assert len(ZhongGua) == 64
```

---

### 任务 1.9 - 重卦代码到单卦解析
**目标**: 实现从重卦代码解析出内卦外卦
**操作**:
- 在 `ZhongGua` 枚举中添加从代码解析的方法
- 实现通过代码获取对应的 `ZhongGua` 枚举值
**测试**:
```python
# tests/test_enums_1_9.py
gua = ZhongGua.from_code(111111)
assert gua == ZhongGua.QIAN_WEI_TIAN
assert gua.get_neigua_from_code() == DanGua.QIAN
assert gua.get_waigua_from_code() == DanGua.QIAN
```

---

### 任务 1.10 - 六亲枚举实现
**目标**: 定义六亲枚举
**操作**:
- 在 `backend/core/enums.py` 中定义 `LiuQin` 枚举
- 定义：父母、官鬼、子孙、妻财、兄弟
**测试**:
```python
# tests/test_enums_1_10.py
assert LiuQin.FU_MU.value == "父母"
assert LiuQin.GUAN_GUI.value == "官鬼"
assert LiuQin.ZI_SUN.value == "子孙"
assert LiuQin.QI_CAI.value == "妻财"
assert LiuQin.XIONG_DI.value == "兄弟"
```

---

### 任务 1.11 - 六神枚举实现
**目标**: 定义六神枚举
**操作**:
- 在 `backend/core/enums.py` 中定义 `LiuShen` 枚举
- 定义：青龙、朱雀、勾陈、螣蛇、白虎、玄武
**测试**:
```python
# tests/test_enums_1_11.py
assert LiuShen.QING_LONG.value == "青龙"
assert LiuShen.ZHU_QUE.value == "朱雀"
# ... 测试所有六神
```

---

### 任务 1.12 - 神煞枚举实现
**目标**: 定义神煞枚举
**操作**:
- 在 `backend/core/enums.py` 中定义 `ShenSha` 枚举
- 定义：干禄、驿马、羊刃、桃花
**测试**:
```python
# tests/test_enums_1_12.py
assert ShenSha.GAN_LU.value == "干禄"
assert ShenSha.YI_MA.value == "驿马"
# ... 测试所有神煞
```

---

## 阶段二：核心业务类实现

### 任务 2.1 - Yao（爻）类基础结构
**目标**: 定义Yao类的数据结构
**操作**:
- 创建 `backend/core/models.py`
- 定义 `Yao` 类
- 定义属性：`position`, `yao_type`, `state`, `dizhi`, `liuqin`, `liushen`, `is_world`, `is_response`
- 实现 `__init__` 方法
**测试**:
```python
# tests/test_models_2_1.py
yao = Yao(
    position=1,
    yao_type=1,  # 阳爻
    state=0,     # 静爻
    dizhi=Dizhi.ZI,
    liuqin=LiuQin.ZI_SUN,
    liushen=LiuShen.QING_LONG,
    is_world=False,
    is_response=False
)
assert yao.position == 1
assert yao.yao_type == 1
assert yao.dizhi == Dizhi.ZI
```

---

### 任务 2.2 - Yao类 - wuxing属性
**目标**: 实现Yao类的wuxing属性（从地支五行获取）
**操作**:
- 在 `Yao` 类中实现 `wuxing` 属性
- 通过 `dizhi.wuxing` 获取五行
**测试**:
```python
# tests/test_models_2_2.py
yao = Yao(position=1, yao_type=1, state=0, dizhi=Dizhi.ZI)
assert yao.wuxing == Wuxing.SHUI
yao2 = Yao(position=2, yao_type=0, state=0, dizhi=Dizhi.MAO)
assert yao2.wuxing == Wuxing.MU
```

---

### 任务 2.3 - Guali（卦例）类基础结构
**目标**: 定义Guali类的基础数据结构
**操作**:
- 在 `backend/core/models.py` 中定义 `Guali` 类
- 定义基础属性：`id`, `time_solar`, `time_ganzhi`, `ben_gua`, `zhi_gua`, `yao_bian_code`
- 定义文本属性：`zhan_wen`, `zhan_duan`, `image_path`
- 实现 `__init__` 方法
**测试**:
```python
# tests/test_models_2_3.py
guali = Guali(
    id=1,
    time_solar=datetime(2024, 2, 12),
    ben_gua=ZhongGua.QIAN_WEI_TIAN,
    zhi_gua=None,
    zhan_wen="测试占问"
)
assert guali.ben_gua == ZhongGua.QIAN_WEI_TIAN
assert guali.zhi_gua is None
```

---

### 任务 2.4 - Guali类 - 爻列表初始化
**目标**: 实现初始化卦例时生成六个爻
**操作**:
- 在 `Guali` 类的 `__init__` 中初始化 `yaos` 列表
- 根据本卦代码初始化六个爻的类型
- 根据爻变代码初始化六个爻的状态
**测试**:
```python
# tests/test_models_2_4.py
guali = Guali(
    ben_gua=ZhongGua.QIAN_WEI_TIAN,  # 111111
    zhi_gua=None,
    yao_bian_code=0
)
assert len(guali.yaos) == 6
assert guali.yaos[0].yao_type == 1  # 初爻阳爻
assert guali.yaos[0].state == 0    # 静爻
```

---

## 阶段三：时间转换模块

### 任务 3.1 - 集成lunar-python库
**目标**: 集成lunar-python库并测试基本功能
**操作**:
- 确认 `lunar-python` 已安装
- 创建 `backend/core/time_converter.py`
- 编写测试用例验证lunar-python的基本用法
**测试**:
```python
# tests/test_time_converter_3_1.py
from lunar import Lunar, Solar
solar = Solar(2024, 2, 12)
lunar = solar.getLunar()
assert lunar.getYearGanZhi() is not None
assert lunar.getMonthGanZhi() is not None
assert lunar.getDayGanZhi() is not None
```

---

### 任务 3.2 - 公历转干支 - 年柱
**目标**: 实现公历年份转年柱干支
**操作**:
- 在 `time_converter.py` 中实现 `solar_to_ganzhi_year(year)` 方法
**测试**:
```python
# tests/test_time_converter_3_2.py
assert solar_to_ganzhi_year(2024) == "甲辰"
assert solar_to_ganzhi_year(2025) == "乙巳"
```

---

### 任务 3.3 - 公历转干支 - 月柱
**目标**: 实现公历年月转月柱干支
**操作**:
- 在 `time_converter.py` 中实现 `solar_to_ganzhi_month(year, month)` 方法
**测试**:
```python
# tests/test_time_converter_3_3.py
assert solar_to_ganzhi_month(2024, 2) == "丙寅"
```

---

### 任务 3.4 - 公历转干支 - 日柱
**目标**: 实现公历年月日转日柱干支
**操作**:
- 在 `time_converter.py` 中实现 `solar_to_ganzhi_day(year, month, day)` 方法
**测试**:
```python
# tests/test_time_converter_3_4.py
assert solar_to_ganzhi_day(2024, 2, 12) == "甲午"
```

---

### 任务 3.5 - 旬空计算
**目标**: 实现旬空计算
**操作**:
- 在 `time_converter.py` 中实现 `get_xunkong(year, month, day)` 方法
- 使用lunar-python库获取旬空
**测试**:
```python
# tests/test_time_converter_3_5.py
xunkong = get_xunkong(2024, 2, 12)
assert xunkong is not None
# 根据实际日期验证旬空结果
```

---

### 任务 3.6 - 完整时间转换
**目标**: 实现完整的公历转干支转换
**操作**:
- 在 `time_converter.py` 中实现 `solar_to_ganzhi_full(year, month, day)` 方法
- 返回包含年柱、月柱、日柱、旬空的字典
**测试**:
```python
# tests/test_time_converter_3_6.py
result = solar_to_ganzhi_full(2024, 2, 12)
assert "year" in result
assert "month" in result
assert "day" in result
assert "xunkong" in result
assert len(result["year"]) == 2  # 两个字
assert len(result["month"]) == 2
assert len(result["day"]) == 2
```

---

### 任务 3.7 - 日干日支提取
**目标**: 实现从日柱中提取日干和日支
**操作**:
- 在 `time_converter.py` 中实现 `extract_tiangan_dizhi_from_ganzhi(ganzhi_str)` 方法
**测试**:
```python
# tests/test_time_converter_3_7.py
tiangan, dizhi = extract_tiangan_dizhi_from_ganzhi("甲午")
assert tiangan == "甲"
assert dizhi == "午"
```

---

## 阶段四：纳甲装卦模块

### 任务 4.1 - 纳甲装卦映射表定义
**目标**: 定义单卦到地支的映射表
**操作**:
- 创建 `backend/core/nama.py`
- 定义单卦地支映射字典（内卦初二三爻、外卦四五上爻）
- 参考《编码规则.md》3.6章节
**测试**:
```python
# tests/test_nama_4_1.py
assert NAMA_DIZHI_NEIGUA[DanGua.QIAN] == (Dizhi.ZI, Dizhi.YIN, Dizhi.CHEN)
assert NAMA_DIZHI_WAIGUA[DanGua.QIAN] == (Dizhi.WU, Dizhi.SHEN, Dizhi.XU)
```

---

### 任务 4.2 - 根据单卦获取地支
**目标**: 实现根据单卦获取对应地支的方法
**操作**:
- 在 `nama.py` 中实现 `get_dizhi_from_dan_gua(dan_gua, position)` 方法
- position: 1-6，对应初爻到上爻
- 返回对应的地支
**测试**:
```python
# tests/test_nama_4_2.py
# 乾卦内卦：初爻子、二爻寅、三爻辰
assert get_dizhi_from_dan_gua(DanGua.QIAN, 1) == Dizhi.ZI
assert get_dizhi_from_dan_gua(DanGua.QIAN, 2) == Dizhi.YIN
assert get_dizhi_from_dan_gua(DanGua.QIAN, 3) == Dizhi.CHEN
# 乾卦外卦：四爻午、五爻申、上爻戌
assert get_dizhi_from_dan_gua(DanGua.QIAN, 4) == Dizhi.WU
assert get_dizhi_from_dan_gua(DanGua.QIAN, 5) == Dizhi.SHEN
assert get_dizhi_from_dan_gua(DanGua.QIAN, 6) == Dizhi.XU
```

---

### 任务 4.3 - 重卦装地支
**目标**: 实现为重卦的六个爻装地支
**操作**:
- 在 `nama.py` 中实现 `load_dizhi_to_guali(guali)` 方法
- 根据重卦的内卦外卦为六个爻设置地支
**测试**:
```python
# tests/test_nama_4_3.py
guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
load_dizhi_to_guali(guali)
assert guali.yaos[0].dizhi == Dizhi.ZI   # 初爻子
assert guali.yaos[1].dizhi == Dizhi.YIN  # 二爻寅
assert guali.yaos[2].dizhi == Dizhi.CHEN # 三爻辰
assert guali.yaos[3].dizhi == Dizhi.WU   # 四爻午
assert guali.yaos[4].dizhi == Dizhi.SHEN # 五爻申
assert guali.yaos[5].dizhi == Dizhi.XU   # 上爻戌
```

---

## 阶段五：六亲计算模块

### 任务 5.1 - 五行生克判断辅助函数
**目标**: 实现五行生克判断辅助函数
**操作**:
- 创建 `backend/core/wuxing_helper.py`
- 实现 `wuxing_sheng(a, b)` 判断a是否生b
- 实现 `wuxing_ke(a, b)` 判断a是否克b
**测试**:
```python
# tests/test_wuxing_helper_5_1.py
assert wuxing_sheng(Wuxing.JIN, Wuxing.SHUI) == True   # 金生水
assert wuxing_sheng(Wuxing.SHUI, Wuxing.JIN) == False
assert wuxing_ke(Wuxing.JIN, Wuxing.MU) == True        # 金克木
assert wuxing_ke(Wuxing.MU, Wuxing.JIN) == False
```

---

### 任务 5.2 - 单爻六亲计算
**目标**: 实现根据卦宫五行和爻地支五行计算六亲
**操作**:
- 在 `wuxing_helper.py` 中实现 `calculate_liuqin(gong_wuxing, yao_wuxing)` 方法
- 根据《编码规则.md》3.7章节的规则
**测试**:
```python
# tests/test_wuxing_helper_5_2.py
# 爻地支五行生卦宫五行：父母
assert calculate_liuqin(Wuxing.JIN, Wuxing.SHUI) == LiuQin.FU_MU
# 爻地支五行克卦宫五行：官鬼
assert calculate_liuqin(Wuxing.SHUI, Wuxing.HUO) == LiuQin.GUAN_GUI
# 卦宫五行生爻地支五行：子孙
assert calculate_liuqin(Wuxing.SHUI, Wuxing.MU) == LiuQin.ZI_SUN
# 卦宫五行克爻地支五行：妻财
assert calculate_liuqin(Wuxing.MU, Wuxing.TU) == LiuQin.QI_CAI
# 卦宫五行与爻地支五行相同：兄弟
assert calculate_liuqin(Wuxing.MU, Wuxing.MU) == LiuQin.XIONG_DI
```

---

### 任务 5.3 - 卦例六亲计算
**目标**: 为卦例的六个爻计算六亲
**操作**:
- 在 `Guali` 类中实现 `_calculate_liuqin()` 方法
- 根据卦宫五行和各爻地支五行计算六亲
**测试**:
```python
# tests/test_wuxing_helper_5_3.py
guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)  # 乾宫，五行金
load_dizhi_to_guali(guali)  # 装地支
guali._calculate_liuqin()
assert guali.yaos[0].liuqin == LiuQin.ZI_SUN  # 子水，金生水
assert guali.yaos[1].liuqin == LiuQin.FU_MU   # 寅木，金克木
# 测试所有六个爻
```

---

## 阶段六：六神计算模块

### 任务 6.1 - 六神映射表定义
**目标**: 定义日干到六神的映射表
**操作**:
- 创建 `backend/core/liushen.py`
- 定义六神映射字典（参考《编码规则.md》3.11章节）
**测试**:
```python
# tests/test_liushen_6_1.py
assert LIUSHEN_MAP[("甲", "乙")][0] == LiuShen.QING_LONG
assert LIUSHEN_MAP[("甲", "乙")][1] == LiuShen.ZHU_QUE
# ... 测试所有日干
```

---

### 任务 6.2 - 根据日干计算六神
**目标**: 实现根据日干获取各爻位的六神
**操作**:
- 在 `liushen.py` 中实现 `get_liushen_by_tiangan(tiangan)` 方法
- 返回六个爻位对应的六神列表
**测试**:
```python
# tests/test_liushen_6_2.py
# 甲乙日：初爻青龙、二爻朱雀、三爻勾陈、四爻螣蛇、五爻白虎、上爻玄武
result = get_liushen_by_tiangan("甲")
assert result[0] == LiuShen.QING_LONG
assert result[1] == LiuShen.ZHU_QUE
assert result[2] == LiuShen.GOU_CHEN
assert result[3] == LiuShen.TENG_SHE
assert result[4] == LiuShen.BAI_HU
assert result[5] == LiuShen.XUAN_WU
```

---

### 任务 6.3 - 卦例六神计算
**目标**: 为卦例的六个爻设置六神
**操作**:
- 在 `Guali` 类中实现 `_calculate_liushen()` 方法
- 根据日干设置各爻的六神
**测试**:
```python
# tests/test_liushen_6_3.py
guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
guali.time_ganzhi = {"day": "甲午", "tiangan_day": "甲"}
guali._calculate_liushen()
assert guali.yaos[0].liushen == LiuShen.QING_LONG
assert guali.yaos[1].liushen == LiuShen.ZHU_QUE
# ... 测试所有六个爻
```

---

## 阶段七：世应定位模块

### 任务 7.1 - 世应映射表定义
**目标**: 定义宫位到世应爻位的映射表
**操作**:
- 创建 `backend/core/shiying.py`
- 定义 `SHI_YING_MAP` 字典（参考《基本规则.md》3.2章节）
**测试**:
```python
# tests/test_shiying_7_1.py
assert SHI_YING_MAP["本宫"] == (6, 3)
assert SHI_YING_MAP["一世"] == (1, 4)
assert SHI_YING_MAP["二世"] == (2, 5)
assert SHI_YING_MAP["三世"] == (3, 6)
assert SHI_YING_MAP["四世"] == (4, 1)
assert SHI_YING_MAP["五世"] == (5, 2)
assert SHI_YING_MAP["游魂"] == (4, 1)
assert SHI_YING_MAP["归魂"] == (3, 6)
```

---

### 任务 7.2 - 根据宫位获取世应爻位
**目标**: 实现根据宫位获取世应爻位的方法
**操作**:
- 在 `shiying.py` 中实现 `get_shiying_by_gongwei(gongwei_index)` 方法
**测试**:
```python
# tests/test_shiying_7_2.py
world_pos, response_pos = get_shiying_by_gongwei("本宫")
assert world_pos == 6
assert response_pos == 3
```

---

### 任务 7.3 - 卦例世应设置
**目标**: 为卦例的爻设置世应属性
**操作**:
- 在 `Guali` 类中实现 `_set_shiying()` 方法
- 根据卦宫的宫位设置世爻和应爻
**测试**:
```python
# tests/test_shiying_7_3.py
guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)  # 本宫卦
guali._set_shiying()
assert guali.yaos[5].is_world == True   # 上爻世爻
assert guali.yaos[2].is_response == True  # 三爻应爻
```

---

## 阶段八：伏神计算模块

### 任务 8.1 - 检查六亲是否齐全
**目标**: 实现检查六个爻是否包含所有六亲的方法
**操作**:
- 创建 `backend/core/fushen.py`
- 实现 `check_liuqin_complete(yaos)` 方法
- 返回缺少的六亲列表
**测试**:
```python
# tests/test_fushen_8_1.py
yaos = [
    Yao(position=1, liuqin=LiuQin.FU_MU),
    Yao(position=2, liuqin=LiuQin.GUAN_GUI),
    Yao(position=3, liuqin=LiuQin.ZI_SUN),
    Yao(position=4, liuqin=LiuQin.QI_CAI),
    Yao(position=5, liuqin=LiuQin.XIONG_DI),
    Yao(position=6, liuqin=LiuQin.FU_MU)
]
missing = check_liuqin_complete(yaos)
assert len(missing) == 0  # 六亲齐全
```

---

### 任务 8.2 - 获取本宫卦
**目标**: 实现根据卦宫获取本宫卦的方法
**操作**:
- 在 `fushen.py` 中实现 `get_ben_gong_gua(gongwei)` 方法
**测试**:
```python
# tests/test_fushen_8_2.py
ben_gong = get_ben_gong_gua("乾宫")
assert ben_gong == ZhongGua.QIAN_WEI_TIAN
ben_gong = get_ben_gong_gua("震宫")
assert ben_gong == ZhongGua.ZHEN_WEI_LEI
```

---

### 任务 8.3 - 查找伏神
**目标**: 实现从本宫卦中查找缺少的六亲对应的爻
**操作**:
- 在 `fushen.py` 中实现 `find_fushen(guali, missing_liuqin)` 方法
- 返回伏神信息列表
**测试**:
```python
# tests/test_fushen_8_3.py
guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)  # 乾宫一世卦
# 假设缺少妻财爻
fushen_list = find_fushen(guali, [LiuQin.QI_CAI])
assert len(fushen_list) > 0
assert fushen_list[0]["liuqin"] == LiuQin.QI_CAI
```

---

### 任务 8.4 - 卦例伏神计算
**目标**: 为卦例计算伏神
**操作**:
- 在 `Guali` 类中实现 `_calculate_fushen()` 方法
- 初始化 `fu_shen` 属性
**测试**:
```python
# tests/test_fushen_8_4.py
guali = Guali(ben_gua=ZhongGua.TIAN_FENG_GOU)
load_dizhi_to_guali(guali)
guali._calculate_liuqin()
guali._calculate_fushen()
assert isinstance(guali.fu_shen, dict)
```

---

## 阶段九：反吟伏吟计算模块

### 任务 9.1 - 易冒反吟判断
**目标**: 实现易冒反吟判断
**操作**:
- 创建 `backend/core/fanyin_fuyin.py`
- 定义易冒反吟映射表（乾巽互变、坎离互变、艮坤互变、震兑互变）
- 实现 `is_yimao_fanyin(dan_gua1, dan_gua2)` 方法
**测试**:
```python
# tests/test_fanyin_fuyin_9_1.py
assert is_yimao_fanyin(DanGua.QIAN, DanGua.XUN) == True
assert is_yimao_fanyin(DanGua.XUN, DanGua.QIAN) == True
assert is_yimao_fanyin(DanGua.KAN, DanGua.LI) == True
assert is_yimao_fanyin(DanGua.LI, DanGua.KAN) == True
assert is_yimao_fanyin(DanGua.GEN, DanGua.KUN) == True
assert is_yimao_fanyin(DanGua.KUN, DanGua.GEN) == True
assert is_yimao_fanyin(DanGua.ZHEN, DanGua.DUI) == True
assert is_yimao_fanyin(DanGua.DUI, DanGua.ZHEN) == True
assert is_yimao_fanyin(DanGua.QIAN, DanGua.KUN) == False
```

---

### 任务 9.2 - 爻变反吟判断
**目标**: 实现爻变反吟判断
**操作**:
- 在 `fanyin_fuyin.py` 中定义爻变反吟映射表（坤巽互变）
- 实现 `is_yaobian_fanyin(dan_gua1, dan_gua2)` 方法
**测试**:
```python
# tests/test_fanyin_fuyin_9_2.py
assert is_yaobian_fanyin(DanGua.KUN, DanGua.XUN) == True
assert is_yaobian_fanyin(DanGua.XUN, DanGua.KUN) == True
assert is_yaobian_fanyin(DanGua.QIAN, DanGua.XUN) == False
```

---

### 任务 9.3 - 伏吟判断
**目标**: 实现伏吟判断
**操作**:
- 在 `fanyin_fuyin.py` 中定义伏吟映射表（乾震互变）
- 实现 `is_fuyin(dan_gua1, dan_gua2)` 方法
**测试**:
```python
# tests/test_fanyin_fuyin_9_3.py
assert is_fuyin(DanGua.QIAN, DanGua.ZHEN) == True
assert is_fuyin(DanGua.ZHEN, DanGua.QIAN) == True
assert is_fuyin(DanGua.QIAN, DanGua.XUN) == False
```

---

### 任务 9.4 - 卦例反吟伏吟计算
**目标**: 为卦例计算反吟伏吟状态
**操作**:
- 在 `Guali` 类中实现 `_calculate_fanyin_fuyin()` 方法
- 比较本卦和之卦的内卦外卦
**测试**:
```python
# tests/test_fanyin_fuyin_9_4.py
# 火天大有(111101)之火风鼎(011101)，内卦易冒反吟
guali = Guali(
    ben_gua=ZhongGua.HUO_TIAN_DA_YOU,
    zhi_gua=ZhongGua.HUO_FENG_DING
)
guali._calculate_fanyin_fuyin()
assert guali.fan_yin["neigua"] == ["易冒反吟"]
```

---

## 阶段十：神煞计算模块

### 任务 10.1 - 干禄计算
**目标**: 实现干禄计算
**操作**:
- 创建 `backend/core/shensha.py`
- 定义干禄映射表（参考《编码规则.md》4.1章节）
- 实现 `get_ganlu(tiangan)` 方法
**测试**:
```python
# tests/test_shensha_10_1.py
assert get_ganlu("甲") == Dizhi.YIN
assert get_ganlu("乙") == Dizhi.MAO
assert get_ganlu("丙") == Dizhi.SI
assert get_ganlu("戊") == Dizhi.SI
assert get_ganlu("庚") == Dizhi.SHEN
```

---

### 任务 10.2 - 驿马计算
**目标**: 实现驿马计算
**操作**:
- 在 `shensha.py` 中定义驿马映射表（参考《编码规则.md》4.2章节）
- 实现 `get_yima(dizhi)` 方法
**测试**:
```python
# tests/test_shensha_10_2.py
assert get_yima(Dizhi.SHEN) == Dizhi.YIN
assert get_yima(Dizhi.ZI) == Dizhi.YIN
assert get_yima(Dizhi.CHEN) == Dizhi.YIN
assert get_yima(Dizhi.HAI) == Dizhi.SI
```

---

### 任务 10.3 - 羊刃计算
**目标**: 实现羊刃计算
**操作**:
- 在 `shensha.py` 中定义羊刃映射表（参考《编码规则.md》4.3章节）
- 实现 `get_yangren(tiangan)` 方法
**测试**:
```python
# tests/test_shensha_10_3.py
assert get_yangren("甲") == Dizhi.MAO
assert get_yangren("乙") == Dizhi.YIN
assert get_yangren("丙") == Dizhi.WU
assert get_yangren("庚") == Dizhi.YOU
```

---

### 任务 10.4 - 桃花计算
**目标**: 实现桃花计算
**操作**:
- 在 `shensha.py` 中定义桃花映射表（参考《编码规则.md》4.4章节）
- 实现 `get_taohua(dizhi)` 方法
**测试**:
```python
# tests/test_shensha_10_4.py
assert get_taohua(Dizhi.SHEN) == Dizhi.YOU
assert get_taohua(Dizhi.ZI) == Dizhi.YOU
assert get_taohua(Dizhi.HAI) == Dizhi.ZI
```

---

### 任务 10.5 - 神煞传播（合冲地支）
**目标**: 实现神煞通过合冲关系传播
**操作**:
- 在 `shensha.py` 中实现 `get_all_shensha_dizhi(tiangan, dizhi)` 方法
- 找到神煞地支后，同时返回其相合和相冲的地支
**测试**:
```python
# tests/test_shensha_10_5.py
# 假设子是干禄，则丑也带干禄（子丑合），午也带干禄（子午冲）
result = get_all_shensha_dizhi("壬", Dizhi.ZI)  # 壬禄在子
assert Dizhi.ZI in result[ShenSha.GAN_LU]
assert Dizhi.CHOU in result[ShenSha.GAN_LU]  # 子丑合
assert Dizhi.WU in result[ShenSha.GAN_LU]    # 子午冲
```

---

### 任务 10.6 - 卦例神煞计算
**目标**: 为卦例计算神煞
**操作**:
- 在 `Guali` 类中实现 `_calculate_shensha()` 方法
- 根据日干和日支计算所有神煞
**测试**:
```python
# tests/test_shensha_10_6.py
guali = Guali(ben_gua=ZhongGua.QIAN_WEI_TIAN)
guali.time_ganzhi = {"day": "甲午", "tiangan_day": "甲", "dizhi_day": Dizhi.WU}
guali._calculate_shensha()
assert ShenSha.GAN_LU in guali.shensha
assert Dizhi.YIN in guali.shensha[ShenSha.GAN_LU]
```

---

## 阶段十一：生旺墓绝计算模块

### 任务 11.1 - 生旺墓绝映射表
**目标**: 定义生旺墓绝映射表
**操作**:
- 创建 `backend/core/shengwangmujue.py`
- 定义生旺墓绝映射字典（参考《基本规则.md》2.6章节）
**测试**:
```python
# tests/test_shengwangmujue_11_1.py
assert SHENGWANGMUJUE[Dizhi.YIN]["changsheng"] == Dizhi.HAI
assert SHENGWANGMUJUE[Dizhi.YIN]["diwang"] == Dizhi.MAO
assert SHENGWANGMUJUE[Dizhi.YIN]["mu"] == Dizhi.WEI
assert SHENGWANGMUJUE[Dizhi.YIN]["jue"] == Dizhi.SHEN
```

---

### 任务 11.2 - 生旺墓绝状态判断
**目标**: 实现判断地支的生旺墓绝状态
**操作**:
- 在 `shengwangmujue.py` 中实现 `get_shengwangmujue_state(dizhi, target_dizhi)` 方法
**测试**:
```python
# tests/test_shengwangmujue_11_2.py
# 寅木，亥为长生
assert get_shengwangmujue_state(Dizhi.YIN, Dizhi.HAI) == "长生"
# 寅木，卯为帝旺
assert get_shengwangmujue_state(Dizhi.YIN, Dizhi.MAO) == "帝旺"
# 寅木，未为墓
assert get_shengwangmujue_state(Dizhi.YIN, Dizhi.WEI) == "墓"
# 寅木，申为绝
assert get_shengwangmujue_state(Dizhi.YIN, Dizhi.SHEN) == "绝"
```

---

## 阶段十二：Guali类整合计算

### 任务 12.1 - Guali类calculate_all方法框架
**目标**: 实现Guali类的calculate_all方法框架
**操作**:
- 在 `Guali` 类中实现 `calculate_all()` 方法
- 依次调用各个计算子方法
**测试**:
```python
# tests/test_guali_12_1.py
guali = Guali(
    id=1,
    time_solar=datetime(2024, 2, 12),
    ben_gua=ZhongGua.QIAN_WEI_TIAN,
    zhi_gua=None
)
guali.calculate_all()
assert all(yao.dizhi is not None for yao in guali.yaos)
assert all(yao.liuqin is not None for yao in guali.yaos)
assert all(yao.liushen is not None for yao in guali.yaos)
```

---

### 任务 12.2 - 完整卦例计算测试
**目标**: 测试完整卦例的所有计算
**操作**:
- 创建一个完整的测试卦例
- 验证所有计算结果正确
**测试**:
```python
# tests/test_guali_12_2.py
guali = Guali(
    id=1,
    time_solar=datetime(2024, 2, 12),
    ben_gua=ZhongGua.SHAN_FENG_GU,
    zhi_gua=ZhongGua.HUO_DI_JIN
)
guali.calculate_all()
# 验证时间转换
assert guali.time_ganzhi is not None
# 验证爻变代码
assert guali.yao_bian_code == 100  # 山风蛊001011，火地晋000101，差值000100
# 验证纳甲装卦
assert guali.yaos[0].dizhi == Dizhi.CHOU
# 验证六亲
assert guali.yaos[0].liuqin is not None
# 验证六神
assert guali.yaos[0].liushen is not None
# 验证世应
assert any(y.is_world for y in guali.yaos)
assert any(y.is_response for y in guali.yaos)
# 验证神煞
assert len(guali.shensha) > 0
# 验证反吟伏吟
assert isinstance(guali.fan_yin, dict)
```

---

## 阶段十三：数据库表创建

### 任务 13.1 - 卦例表SQL创建
**目标**: 创建卦例表的SQL脚本
**操作**:
- 创建 `scripts/create_guali_table.sql`
- 编写CREATE TABLE语句（参考Plan.md 3.3章节）
**测试**:
- 手动执行SQL脚本
- 验证表创建成功
- 查看表结构正确

---

### 任务 13.2 - 爻详情表SQL创建
**目标**: 创建爻详情表的SQL脚本
**操作**:
- 创建 `scripts/create_yao_detail_table.sql`
- 编写CREATE TABLE语句
**测试**:
- 手动执行SQL脚本
- 验证表创建成功
- 查看表结构正确

---

### 任务 13.3 - SQLAlchemy模型定义 - Guali
**目标**: 定义卦例表的ORM模型
**操作**:
- 创建 `backend/db/models.py`
- 定义 `GualiModel` 类
- 使用SQLAlchemy的DeclarativeBase
**测试**:
```python
# tests/test_db_models_13_3.py
from backend.db.models import GualiModel
model = GualiModel(
    solar_year=2024,
    solar_month=2,
    solar_day=12,
    ganzhi_year="甲辰",
    ganzhi_month="丙寅",
    ganzhi_day="甲午",
    xunkong="辰巳",
    ben_gua_code=111111,
    zhi_gua_code=None,
    yao_bian_code=0,
    gongwei="乾宫",
    gongwei_index="本宫"
)
assert model.solar_year == 2024
assert model.ben_gua_code == 111111
```

---

### 任务 13.4 - SQLAlchemy模型定义 - YaoDetail
**目标**: 定义爻详情表的ORM模型
**操作**:
- 在 `backend/db/models.py` 中定义 `YaoDetailModel` 类
- 设置外键关系
**测试**:
```python
# tests/test_db_models_13_4.py
from backend.db.models import YaoDetailModel
model = YaoDetailModel(
    guali_id=1,
    position=1,
    yao_type=1,
    state=0,
    dizhi="子",
    liuqin="子孙",
    liushen="青龙",
    is_world=True,
    is_response=False
)
assert model.position == 1
assert model.dizhi == "子"
```

---

### 任务 13.5 - 数据库表初始化脚本
**目标**: 创建数据库表初始化脚本
**操作**:
- 创建 `scripts/init_db.py`
- 使用SQLAlchemy的create_all方法
**测试**:
```bash
# 运行脚本
python scripts/init_db.py
# 验证表已创建
# 连接数据库查看表列表
```

---

## 阶段十四：数据库操作

### 任务 14.1 - 数据库Session上下文管理器
**目标**: 实现数据库Session的上下文管理器
**操作**:
- 在 `backend/db/connection.py` 中实现 `get_session()` 方法
- 使用contextmanager
**测试**:
```python
# tests/test_db_connection_14_1.py
with get_session() as session:
    assert session is not None
    result = session.execute(text("SELECT 1"))
    assert result.scalar() == 1
```

---

### 任务 14.2 - 卦例CRUD - 创建
**目标**: 实现卦例的创建操作
**操作**:
- 创建 `backend/db/repositories.py`
- 实现 `GualiRepository.create_guali()` 方法
**测试**:
```python
# tests/test_repositories_14_2.py
repo = GualiRepository()
guali = repo.create_guali(
    solar_year=2024,
    solar_month=2,
    solar_day=12,
    ganzhi_year="甲辰",
    ganzhi_month="丙寅",
    ganzhi_day="甲午",
    xunkong="辰巳",
    ben_gua_code=111111,
    gongwei="乾宫",
    gongwei_index="本宫"
)
assert guali.id > 0
```

---

### 任务 14.3 - 卦例CRUD - 查询
**目标**: 实现卦例的查询操作
**操作**:
- 在 `GualiRepository` 中实现 `get_guali_by_id()` 方法
- 实现 `get_all_gualis()` 方法
**测试**:
```python
# tests/test_repositories_14_3.py
repo = GualiRepository()
guali = repo.get_guali_by_id(1)
assert guali is not None
assert guali.id == 1

all_gualis = repo.get_all_gualis()
assert len(all_gualis) > 0
```

---

### 任务 14.4 - 卦例CRUD - 更新
**目标**: 实现卦例的更新操作
**操作**:
- 在 `GualiRepository` 中实现 `update_guali()` 方法
- 只允许更新语句字段
**测试**:
```python
# tests/test_repositories_14_4.py
repo = GualiRepository()
repo.update_guali(1, zhan_wen="更新后的占问事由")
guali = repo.get_guali_by_id(1)
assert guali.zhan_wen == "更新后的占问事由"
```

---

### 任务 14.5 - 卦例CRUD - 删除
**目标**: 实现卦例的删除操作
**操作**:
- 在 `GualiRepository` 中实现 `delete_guali()` 方法
**测试**:
```python
# tests/test_repositories_14_5.py
repo = GualiRepository()
# 先创建一个测试卦例
test_guali = repo.create_guali(...)
# 删除
repo.delete_guali(test_guali.id)
# 验证已删除
guali = repo.get_guali_by_id(test_guali.id)
assert guali is None
```

---

### 任务 14.6 - 爻详情CRUD - 批量插入
**目标**: 实现爻详情的批量插入操作
**操作**:
- 在 `GualiRepository` 中实现 `save_yao_details()` 方法
**测试**:
```python
# tests/test_repositories_14_6.py
repo = GualiRepository()
yaos = [
    YaoDetailModel(...),
    YaoDetailModel(...),
    # ... 六个爻
]
repo.save_yao_details(1, yaos)
# 验证插入成功
details = repo.get_yao_details(1)
assert len(details) == 6
```

---

## 阶段十五：格式转换模块

### 任务 15.1 - 卦名转代码
**目标**: 实现卦名到代码的转换
**操作**:
- 创建 `backend/core/converter.py`
- 实现 `gua_name_to_code(name)` 方法
**测试**:
```python
# tests/test_converter_15_1.py
assert gua_name_to_code("乾为天") == 111111
assert gua_name_to_code("山风蛊") == 001011
assert gua_name_to_code("火地晋") == 000101
```

---

### 任务 15.2 - 代码转卦名
**目标**: 实现代码到卦名的转换
**操作**:
- 在 `converter.py` 中实现 `code_to_gua_name(code)` 方法
**测试**:
```python
# tests/test_converter_15_2.py
assert code_to_gua_name(111111) == "乾为天"
assert code_to_gua_name(001011) == "山风蛊"
assert code_to_gua_name(000101) == "火地晋"
```

---

### 任务 15.3 - 标准格式解析 - 时间部分
**目标**: 实现标准格式中的时间部分解析
**操作**:
- 在 `converter.py` 中实现 `parse_time_part(input_str)` 方法
- 解析 `[2024;02.12,` 格式
**测试**:
```python
# tests/test_converter_15_3.py
result = parse_time_part("2024;02.12,")
assert result["year"] == 2024
assert result["month"] == 2
assert result["day"] == 12
```

---

### 任务 15.4 - 标准格式解析 - 重卦部分
**目标**: 实现标准格式中的重卦部分解析
**操作**:
- 在 `converter.py` 中实现 `parse_gua_part(input_str)` 方法
- 解析 `山风蛊,火地晋,` 格式（注意：之卦名不需要带*符号）
**测试**:
```python
# tests/test_converter_15_4.py
result = parse_gua_part("山风蛊,火地晋,")
assert result["ben_gua_name"] == "山风蛊"
assert result["zhi_gua_name"] == "火地晋"
result2 = parse_gua_part("乾为天,,")
assert result2["ben_gua_name"] == "乾为天"
assert result2["zhi_gua_name"] is None
```

---

### 任务 15.5 - 标准格式解析 - 语句部分
**目标**: 实现标准格式中的语句部分解析
**操作**:
- 在 `converter.py` 中实现 `parse_text_part(input_str)` 方法
- 解析占问事由和占断（注意：]{符号不是语句部分，实际输入时不需要）
**测试**:
```python
# tests/test_converter_15_5.py
result = parse_text_part("占问股票走势,占断上涨")
assert result["zhan_wen"] == "占问股票走势"
assert result["zhan_duan"] == "占断上涨"
```

---

### 任务 15.6 - 完整标准格式解析
**目标**: 实现完整的标准格式解析
**操作**:
- 在 `converter.py` 中实现 `parse_standard_format(input_str)` 方法
- 解析 `2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨` 格式（注意：实际输入不需要*和]{符号）
**测试**:
```python
# tests/test_converter_15_6.py
result = parse_standard_format("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")
assert result["solar_year"] == 2024
assert result["ben_gua_name"] == "山风蛊"
assert result["zhi_gua_name"] == "火地晋"
assert result["zhan_wen"] == "占问股票走势"
assert result["zhan_duan"] == "占断上涨"
```

---

### 任务 15.7 - 标准格式转Guali对象
**目标**: 实现将标准格式转换为Guali对象
**操作**:
- 在 `converter.py` 中实现 `standard_format_to_guali(input_str)` 方法
**测试**:
```python
# tests/test_converter_15_7.py
guali = standard_format_to_guali("2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨")
assert isinstance(guali, Guali)
assert guali.time_solar.year == 2024
assert guali.ben_gua == ZhongGua.SHAN_FENG_GU
assert guali.zhi_gua == ZhongGua.HUO_DI_JIN
assert guali.zhan_wen == "占问股票走势"
```

---

## 阶段十六：FastAPI基础

### 任务 16.1 - FastAPI应用初始化
**目标**: 创建FastAPI应用基础框架
**操作**:
- 创建 `backend/api/main.py`
- 创建FastAPI应用实例
- 配置CORS
- 添加根路由
**测试**:
```bash
# 启动服务
uvicorn backend.api.main:app --reload
# 访问 http://localhost:8000
# 验证返回 {"message": "Welcome to LiuyaoBase API"}
```

---

### 任务 16.2 - 健康检查接口
**目标**: 实现健康检查接口
**操作**:
- 在 `main.py` 中添加 `/health` 路由
- 返回数据库连接状态
**测试**:
```bash
curl http://localhost:8000/health
# 验证返回 {"status": "ok", "database": "connected"}
```

---

### 任务 16.3 - Pydantic模型 - GualiCreate
**目标**: 定义卦例创建的请求模型
**操作**:
- 创建 `backend/api/schemas.py`
- 定义 `GualiCreate` Pydantic模型
**测试**:
```python
# tests/test_schemas_16_3.py
from backend.api.schemas import GualiCreate
data = GualiCreate(
    solar_year=2024,
    solar_month=2,
    solar_day=12,
    ben_gua_name="乾为天",
    zhi_gua_name=None,
    zhan_wen="测试占问"
)
assert data.solar_year == 2024
```

---

### 任务 16.4 - Pydantic模型 - GualiResponse
**目标**: 定义卦例响应的模型
**操作**:
- 在 `schemas.py` 中定义 `GualiResponse` Pydantic模型
**测试**:
```python
# tests/test_schemas_16_4.py
from backend.api.schemas import GualiResponse
response = GualiResponse(id=1, solar_year=2024, ben_gua_name="乾为天")
assert response.id == 1
```

---

## 阶段十七：卦例API

### 任务 17.1 - 创建卦例接口
**目标**: 实现创建卦例的API接口
**操作**:
- 创建 `backend/api/routers/guali.py`
- 实现 `POST /api/guali` 接口
- 调用格式转换和计算引擎
- 保存到数据库
**测试**:
```bash
curl -X POST http://localhost:8000/api/guali \
  -H "Content-Type: application/json" \
  -d '{
    "solar_year": 2024,
    "solar_month": 2,
    "solar_day": 12,
    "ben_gua_name": "乾为天",
    "zhan_wen": "测试占问"
  }'
# 验证返回卦例ID
```

---

### 任务 17.2 - 获取卦例接口
**目标**: 实现获取单个卦例的API接口
**操作**:
- 实现 `GET /api/guali/{id}` 接口
**测试**:
```bash
curl http://localhost:8000/api/guali/1
# 验证返回卦例详情
```

---

### 任务 17.3 - 获取卦例列表接口
**目标**: 实现获取卦例列表的API接口
**操作**:
- 实现 `GET /api/guali` 接口
- 支持分页
**测试**:
```bash
curl "http://localhost:8000/api/guali?page=1&page_size=10"
# 验证返回卦例列表和分页信息
```

---

### 任务 17.4 - 更新卦例接口
**目标**: 实现更新卦例的API接口
**操作**:
- 实现 `PUT /api/guali/{id}` 接口
- 只允许更新语句字段
**测试**:
```bash
curl -X PUT http://localhost:8000/api/guali/1 \
  -H "Content-Type: application/json" \
  -d '{"zhan_wen": "更新后的占问"}'
# 验证更新成功
```

---

### 任务 17.5 - 删除卦例接口
**目标**: 实现删除卦例的API接口
**操作**:
- 实现 `DELETE /api/guali/{id}` 接口
**测试**:
```bash
curl -X DELETE http://localhost:8000/api/guali/1
# 验证删除成功
```

---

## 阶段十八：卦例详情计算API

### 任务 18.1 - 卦例完整详情接口
**目标**: 实现返回卦例完整计算详情的API接口
**操作**:
- 实现 `GET /api/guali/{id}/detail` 接口
- 返回包含所有卦理计算结果
**测试**:
```bash
curl http://localhost:8000/api/guali/1/detail
# 验证返回完整的卦理信息
```

---

## 阶段十九：CSV导入功能

### 任务 19.1 - CSV格式验证
**目标**: 实现CSV格式的验证
**操作**:
- 创建 `backend/utils/validators.py`
- 实现 `validate_csv_format()` 方法
**测试**:
```python
# tests/test_validators_19_1.py
valid_csv = "2024;02.12,乾为天,,占问,占断,test.jpg"
result = validate_csv_format(valid_csv)
assert result["valid"] == True
```

---

### 任务 19.2 - CSV导入接口
**目标**: 实现CSV文件导入的API接口
**操作**:
- 实现 `POST /api/guali/import-csv` 接口
- 支持文件上传
- 解析并批量创建卦例
**测试**:
```bash
curl -X POST http://localhost:8000/api/guali/import-csv \
  -F "file=@test.csv"
# 验证返回导入结果
```

---

## 阶段二十：图片存储

### 任务 20.1 - 图片存储配置
**目标**: 配置图片存储路径
**操作**:
- 在 `config.py` 中配置图片存储路径
- 创建图片存储目录
- 添加获取图片存储配置的API接口 `GET /api/images/config`
- 前端可调用此接口获取图片存储路径，显示给用户以便将图片存到正确位置
**测试**:
```bash
# 验证目录创建成功
ls -la ./images

# 获取图片存储配置
curl http://localhost:8000/api/images/config
# 返回: {"storage_path": "./images", "absolute_path": "...", "allowed_extensions": [...], "max_file_size": ...}
```

---

### 任务 20.2 - 图片上传接口
**目标**: 实现图片上传的API接口
**操作**:
- 实现 `POST /api/images/upload` 接口
- 验证图片格式
- 保存图片并返回路径和访问URL
**测试**:
```bash
curl -X POST http://localhost:8000/api/images/upload \
  -F "file=@test.jpg"
# 验证返回图片路径和访问URL
```

---

### 任务 20.3 - 图片访问接口
**目标**: 实现图片访问的API接口
**操作**:
- 实现 `GET /api/images/{filename}` 接口
- 返回图片文件
- 添加路径遍历攻击防护
**测试**:
```bash
curl http://localhost:8000/api/images/test.jpg --output downloaded.jpg
# 验证图片下载成功
```

---

### 任务 20.4 - 图片列表和删除接口（可选）
**目标**: 实现图片管理接口
**操作**:
- 实现 `GET /api/images` 获取图片列表
- 实现 `DELETE /api/images/{filename}` 删除图片
**测试**:
```bash
# 获取图片列表
curl http://localhost:8000/api/images

# 删除图片
curl -X DELETE http://localhost:8000/api/images/test.jpg
```

---

## 阶段二十一：前端基础页面

### 任务 21.1 - 首页组件
**目标**: 创建首页组件
**操作**:
- 创建 `frontend/src/views/Home.vue`
- 显示欢迎信息和导航链接
**测试**:
- 访问首页，验证显示正常

---

### 任务 21.2 - 导航菜单组件
**目标**: 创建导航菜单组件
**操作**:
- 创建 `frontend/src/components/NavBar.vue`
- 使用Element Plus的Menu组件
**测试**:
- 验证菜单显示正常
- 点击菜单项能跳转

---

### 任务 21.3 - 路由配置
**目标**: 配置前端路由
**操作**:
- 创建 `frontend/src/router/index.js`
- 配置路由表
**测试**:
- 访问各路由，验证页面正常

---

## 阶段二十二：卦例输入页面

### 任务 22.1 - 手动输入表单
**目标**: 创建手动输入卦例的表单组件
**操作**:
- 创建 `frontend/src/views/GualiInput.vue`
- 使用Element Plus的Form组件
- 添加年份、月日、本卦、之卦、占问事由等字段
**测试**:
- 填写表单，验证字段显示正常

---

### 任务 22.2 - 卦名文本输入
**目标**: 实现卦名的文本输入
**操作**:
- 添加本卦、之卦的文本输入框
- 添加卦名格式提示（用户会按标准卦名输入）
**测试**:
- 输入标准卦名（如"乾为天"），验证值正确
- 输入错误格式，验证显示提示

---

### 任务 22.3 - 表单验证
**目标**: 实现表单验证
**操作**:
- 添加必填项验证
- 添加卦名有效性验证
**测试**:
- 提交空表单，验证显示错误提示
- 输入错误卦名，验证显示错误提示

---

### 任务 22.4 - 提交卦例
**目标**: 实现卦例提交功能
**操作**:
- 创建API调用函数 `createGuali()`
- 调用后端接口创建卦例
- 显示成功/失败提示
**测试**:
- 填写完整表单并提交
- 验证提示成功
- 查看数据库验证卦例已保存

---

## 阶段二十三：CSV导入页面

### 任务 23.1 - CSV上传组件
**目标**: 创建CSV文件上传组件
**操作**:
- 创建 `frontend/src/views/CsvImport.vue`
- 使用Element Plus的Upload组件
**测试**:
- 选择CSV文件，验证文件名显示

---

### 任务 23.2 - CSV导入提交
**目标**: 实现CSV导入提交功能
**操作**:
- 调用后端CSV导入接口
- 显示导入进度
- 显示导入结果统计
**测试**:
- 上传测试CSV文件
- 验证导入成功
- 查看数据库验证卦例已保存

---

## 阶段二十四：卦例列表页面

### 任务 24.1 - 卦例列表组件
**目标**: 创建卦例列表展示组件
**操作**:
- 创建 `frontend/src/views/GualiList.vue`
- 使用Element Plus的Table组件
- 显示卦例基本信息
**测试**:
- 验证列表显示卦例
- 验证分页功能

---

### 任务 24.2 - 删除卦例
**目标**: 实现删除卦例功能
**操作**:
- 添加删除按钮
- 调用删除API
- 刷新列表
**测试**:
- 点击删除按钮
- 确认删除
- 验证卦例已从列表移除

---

## 阶段二十五：卦例详情页面

### 任务 25.1 - 详情页面布局
**目标**: 创建卦例详情页面布局
**操作**:
- 创建 `frontend/src/views/GualiDetail.vue`
- 设计详情展示布局
**测试**:
- 访问详情页，验证布局正常

---

### 任务 25.2 - 卦理信息展示
**目标**: 实现卦理信息的展示（按照输入输出查找规则.md中单卦例输出查看章节的要求）
**操作**:
- 展示占问和占断
- 展示时间（公历年月日）
- 展示神煞（干禄、驿马、羊刃、桃花）
- 展示年柱、月柱、日柱、旬空
- 展示本卦和之卦的六爻详情（爻位、六神、地支、六亲、世/应标记）
- 展示伏神信息（如果有）
**测试**:
- 验证所有卦理信息正确显示

---

### 任务 25.3 - 图片展示
**目标**: 实现卦例图片的展示
**操作**:
- 添加图片展示区域
- 从后端获取图片
**测试**:
- 验证图片正常显示

---

## 阶段二十六：复杂检索 - 自定义检索

### 任务 26.1 - 检索页面框架
**目标**: 创建检索页面框架
**操作**:
- 创建 `frontend/src/views/Search.vue`
- 设计左右分栏布局（左侧条件构建区，右侧结果展示区）
**测试**:
- 访问检索页，验证布局正常

---

### 任务 26.2 - 字段库组件
**目标**: 创建可拖拽的字段库
**操作**:
- 创建 `frontend/src/components/Search/FieldLibrary.vue`
- 分类展示所有可检索字段：
  - 时间类：公历年（手动输入）、公历月日（手动输入）、年柱（下拉选择）、月柱（下拉选择）、日柱（下拉选择）、日干（下拉选择）、日支（下拉选择）、旬空（下拉选择）
  - 卦类：本卦名（手动输入）、之卦名（手动输入）、内卦（下拉选择）、外卦（下拉选择）、卦宫（下拉选择）、宫位（下拉选择）、特殊类型（下拉选择）
  - 爻类：爻位（下拉选择）、爻类型（下拉选择）、爻状态（下拉选择）、六亲（下拉选择）、六神（下拉选择）、地支（下拉选择）、爻地支五行（下拉选择）、暗动（下拉选择：有暗动/无暗动）、世应（下拉选择）
  - 关系类：地支相合、地支相冲、地支相合地支、地支相冲地支、三合局、五行相生、五行相克、生旺墓绝（需严格顺序）、反吟伏吟（下拉选择后拖拽）、伏神飞神（下拉选择后拖拽）
  - 神煞类：干禄（下拉选择：是干禄/带干禄）、驿马（下拉选择：是驿马/带驿马）、羊刃（下拉选择：是羊刃/带羊刃）、桃花（下拉选择：是桃花/带桃花）
  - 其他：占问事由（手动输入）、占断（手动输入）
**测试**:
- 验证字段库显示所有字段
- 验证字段分类正确
- 验证神煞类字段提供三个选项

---

### 任务 26.3 - 运算符组件
**目标**: 创建运算符选择组件
**操作**:
- 创建 `frontend/src/components/Search/OperatorSelector.vue`
- 提供运算符：=、≠、>、<、≥、≤、包含、不包含
- 关系运算符：与（用于两个字段间的关系判断）
- 提供 "." 运算符，用于字段属性访问（如 `世爻.六亲`）
- 提供 WITH 运算符，用于字段间关系存在性判断
- 详细说明WITH运算符的使用方法和判断逻辑（参考《复杂检索界面设计.md》13.8章节）
**测试**:
- 验证运算符显示
- 验证运算符选择功能
- 验证WITH运算符的详细说明正确展示

---

### 任务 26.4 - 条件构建器
**目标**: 创建可视化条件构建器
**操作**:
- 创建 `frontend/src/components/Search/ConditionBuilder.vue`
- 实现字段拖拽到构建区
- 实现运算符选择
- 实现值输入（支持文本、数字、下拉选择）
- 实现条件卡片显示
- 添加编辑、删除按钮
**测试**:
- 拖拽字段到构建区
- 验证字段显示
- 验证条件卡片正常显示

---

### 任务 26.5 - 逻辑运算符组件
**目标**: 实现AND/OR逻辑运算
**操作**:
- 在条件构建器中添加逻辑运算符选择
- 支持括号分组
- 实现条件的数据结构
**测试**:
- 添加多个条件
- 添加AND/OR运算符
- 添加括号分组
- 验证逻辑表达式正确

---

### 任务 26.6 - 条件表达式生成
**目标**: 生成检索条件表达式
**操作**:
- 实现从条件卡片生成查询JSON
- 实现表达式预览
**测试**:
- 构建多个条件
- 验证生成的JSON正确
- 验证表达式预览正确

---

### 任务 26.7 - 推荐方案组件
**目标**: 创建推荐方案功能
**操作**:
- 创建 `frontend/src/components/Search/RecommendedSchemes.vue`
- 预设常用检索方案：
  - "世爻为子孙爻"
  - "带干禄且地支为卯"
  - "六合卦且世爻为官鬼"
  - "游魂卦"
  - "带伏神的卦例"
  - "易冒反吟"
  - "六冲卦"
  - "驿马和桃花"
  - "官鬼持世"
  - "子孙爻被合"
  - "日支与妻财爻相冲"
  - "存在爻与日支相冲"
- 支持一键加载推荐方案
- 支持用户保存自定义方案
**测试**:
- 点击推荐方案，验证加载成功
- 保存自定义方案，验证保存成功
- 加载自定义方案，验证数据正确

---

### 任务 26.8 - 检索后端实现
**目标**: 实现检索的后端逻辑
**操作**:
- 创建 `backend/api/routers/search.py`
- 实现 `POST /api/search` 接口
- 解析条件表达式
- 实现数据库查询逻辑
- 支持字段组合关系（如世爻.六亲、妻财爻.地支）
- 支持关系运算符（与、WITH、相合、相冲、生克等）
**测试**:
```bash
# 测试基础检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": [
      {"field": "ben_gua_name", "operator": "=", "value": "乾为天"}
    ],
    "logic": "and"
  }'

# 测试关系检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": [
      {
        "field1": "妻财爻.地支",
        "relation": "相冲",
        "field2": "日支"
      }
    ]
  }'

# 验证返回匹配的卦例
```

---

## 阶段二十七：检索结果展示

### 任务 27.1 - 结果列表展示
**目标**: 实现检索结果的列表展示
**操作**:
- 创建 `frontend/src/components/Search/ResultList.vue`
- 显示匹配的卦例列表
- 添加高亮显示
**测试**:
- 执行检索
- 验证结果列表显示

---

### 任务 27.2 - 结果分页
**目标**: 实现检索结果的分页
**操作**:
- 添加分页组件
- 实现分页切换
**测试**:
- 切换页码
- 验证结果正确

---

### 任务 27.3 - 结果导出
**目标**: 实现检索结果的导出功能
**操作**:
- 添加导出按钮
- 调用后端导出接口
- 下载文件
**测试**:
- 点击导出
- 验证文件下载成功

---

## 阶段二十八：ECharts集成

**重要说明**: 本阶段功能依据`股票-卦例显示规则.md`实现。股票数据来源为**Akshare**库，使用前需详细阅读其使用文档。

### 任务 28.1 - 后端Akshare集成与股票数据接口
**目标**: 集成Akshare库并实现股票数据获取接口
**操作**:
- 安装 akshare 库：`pip install akshare`
- 创建 `backend/api/routers/stock.py`
- 实现 `GET /api/stock/search` 股票搜索接口（支持股票名称/代码搜索）
- 实现 `GET /api/stock/kline` K线数据获取接口
  - 参数：股票代码、开始日期、结束日期
  - 返回：日期、开盘价、收盘价、最高价、最低价、成交量等
- 实现数据缓存机制，避免频繁请求（按规则：不要一直获取股票数据，需要时再去获取）
**测试**:
```bash
# 测试股票搜索
curl "http://localhost:8000/api/stock/search?keyword=贵州茅台"
# 验证返回股票代码和名称列表

# 测试K线数据获取
curl "http://localhost:8000/api/stock/kline?code=600519&start=2024-01-01&end=2024-03-01"
# 验证返回K线数据格式正确
```

---

### 任务 28.2 - 股票名称匹配卦例接口
**目标**: 实现根据股票名称在卦例占问事由中搜索的接口
**操作**:
- 在 `backend/api/routers/stock.py` 中实现
- 实现 `GET /api/stock/guali-mapping` 接口
  - 参数：股票名称
  - 功能：在卦例的`zhan_wen`（占问事由）字段中模糊搜索包含该股票名称的卦例
  - 返回：匹配的卦例列表，包含卦例ID、日期、占问事由、占验情况
- 按日期组织数据，便于前端与K线对应
**测试**:
```bash
# 测试股票与卦例匹配
curl "http://localhost:8000/api/stock/guali-mapping?name=贵州茅台"
# 验证返回包含"贵州茅台"关键词的卦例列表
# 验证每个卦例包含：id, solar_year, solar_month, solar_day, zhan_wen, yanqing_status
```

---

### 任务 28.3 - 前端ECharts环境搭建
**目标**: 安装并配置ECharts
**操作**:
- 安装依赖：`npm install echarts vue-echarts --save`
- 在 `frontend/src/main.js` 中全局注册ECharts组件
- 创建 `frontend/src/components/Stock/KlineChart.vue` K线图组件基础结构
**测试**:
- 验证依赖安装成功
- 渲染一个简单的示例K线图
- 验证图表显示正常

---

### 任务 28.4 - K线图基础渲染
**目标**: 实现标准K线图的渲染（同花顺风格）
**操作**:
- 在 `KlineChart.vue` 中使用ECharts的candlestick图表类型
- 实现基础K线图配置：
  - X轴：日期
  - Y轴：价格
  - 红色阳线（收盘>开盘）、绿色阴线（收盘<开盘）
- 添加成交量柱状图（副图）
- 实现图表缩放和拖拽功能（dataZoom组件）
**测试**:
- 使用模拟数据渲染K线图
- 验证红色阳线、绿色阴线显示正确
- 验证缩放和拖拽功能正常

---

### 任务 28.5 - K线图横轴时间双显示
**目标**: K线图横轴同时显示公历时间和干支时间（月柱、日柱）
**操作**:
- 修改K线图X轴配置
- 使用ECharts的axisLabel formatter实现双行显示：
  - 第一行：公历日期（如"02-12"）
  - 第二行：月柱日柱（如"丙寅甲午"）
- 实现数据预处理，为每个K线数据点添加对应的干支时间
**测试**:
- 渲染K线图
- 验证X轴同时显示公历日期和干支时间
- 验证干支时间与公历日期对应正确

---

### 任务 28.6 - 三种K线样式实现
**目标**: 实现三种不同类型的K线样式（依据占验情况）
**操作**:
- 定义三种K线样式：
  1. **无对应卦例**：空心K线，红色阳线，绿色阴线
  2. **有卦例且占验为"应验"**：实心K线，红色阳线，绿色阴线
  3. **有卦例且占验为"模糊"或"不验"**：空心K线+内部黄色填充，红色阳线，绿色阴线
- 实现K线数据与卦例/占验情况的关联逻辑
- 使用ECharts的itemStyle配置不同样式
**测试**:
- 准备三种类型的测试数据
- 验证无卦例的K线为空心
- 验证应验卦例的K线为实心
- 验证模糊/不验卦例的K线为空心+黄色填充
- 验证红绿颜色正确

---

### 任务 28.7 - 股票搜索页面
**目标**: 创建股票搜索界面
**操作**:
- 创建 `frontend/src/views/StockAnalysis.vue` 股票分析页面
- 实现搜索输入框，支持输入标准格式的股票/期货名称
- 实现搜索建议下拉列表（调用后端搜索接口）
- 记录搜索历史（localStorage存储）
- 设计页面布局：左侧搜索区+右侧K线图展示区
**测试**:
- 输入股票名称，验证搜索建议显示
- 选择股票，验证跳转到K线图展示
- 验证搜索历史记录功能

---

### 任务 28.8 - 分时图浮窗组件
**目标**: 创建分时图浮窗组件
**操作**:
- 创建 `frontend/src/components/Stock/IntradayChart.vue` 分时图组件
- 后端实现 `GET /api/stock/intraday` 接口获取当日分时数据
- 使用ECharts的line图表渲染分时走势
- 实现浮窗样式（可拖拽、关闭）
- 显示当日开盘价、收盘价、最高价、最低价
**测试**:
- 打开分时图浮窗
- 验证分时走势正确渲染
- 验证浮窗可拖拽和关闭

---

### 任务 28.9 - 卦例浮窗组件
**目标**: 创建卦例详情浮窗组件
**操作**:
- 创建 `frontend/src/components/Stock/GualiFloatPanel.vue` 卦例浮窗组件
- 复用 `GualiDetail.vue` 的展示逻辑，按`输入输出查找规则.md`单卦例输出格式展示
- 在浮窗中添加占验情况修改功能（复用 `YanqingAnnotation.vue`）
- 如果当日无对应卦例，显示提示语"当日无对应卦例"
**测试**:
- 点击有卦例的K线，验证浮窗显示卦例详情
- 验证占验情况修改功能正常
- 点击无卦例的K线，验证显示提示语

---

### 任务 28.10 - K线点击双浮窗联动
**目标**: 实现双击K线显示分时图和卦例两个浮窗
**操作**:
- 为K线图添加dblclick事件监听
- 点击时获取对应的日期
- 同时打开分时图浮窗和卦例浮窗
- 实现浮窗位置自动排列（避免重叠）
- 根据日期查询对应的卦例，若没有则显示提示
**测试**:
- 双击某根K线
- 验证分时图浮窗正常打开并显示当日分时数据
- 验证卦例浮窗正常打开
- 验证无卦例时显示提示

---

### 任务 28.11 - K线图数据加载与卦例关联
**目标**: 实现股票数据加载并与卦例数据关联
**操作**:
- 实现完整的股票搜索流程：
  1. 用户输入股票名称搜索
  2. 获取股票历史K线数据
  3. 根据股票名称在卦例占问事由中搜索匹配的卦例
  4. 将卦例数据按日期与K线数据关联
  5. 根据占验情况设置K线样式
- 实现loading状态显示
- 实现错误处理（股票代码不存在、数据获取失败等）
**测试**:
- 搜索一个股票
- 验证K线图正确渲染
- 验证有卦例的K线样式正确
- 验证数据加载状态显示
- 测试错误情况处理

---

### 任务 28.12 - 股票分析窗口多窗功能
**目标**: 实现股票分析页面的多窗查看功能
**操作**:
- 复用 `WindowManager.vue` 组件的思路
- 在股票分析页面添加"新建窗口"按钮
- 使用 `window.open()` 打开新窗口
- 通过URL参数传递当前股票代码/名称
- 支持不同窗口查看不同股票的K线图
**测试**:
- 点击"新建窗口"按钮
- 验证新窗口打开并显示独立的分析页面
- 在新窗口搜索不同股票
- 验证两个窗口独立运行，互不影响

---

### 任务 28.13 - K线图响应式与性能优化
**目标**: 优化K线图的响应式布局和性能
**操作**:
- 实现K线图容器自适应大小
- 监听窗口resize事件，调用ECharts的resize方法
- 大数据量时启用ECharts的large模式
- 实现数据分页加载（滚动加载更多历史数据）
- 优化后端数据缓存策略
**测试**:
- 改变窗口大小，验证K线图自适应
- 加载大量K线数据（如一年数据），验证性能
- 测试滚动加载功能

---

### 任务 28.14 - 添加路由和导航菜单
**目标**: 将股票分析页面添加到系统路由和导航
**操作**:
- 在 `frontend/src/router/index.js` 中添加 `/stock` 路由
- 在 `NavBar.vue` 中添加"股票分析"菜单项
- 配置页面标题和meta信息
**测试**:
- 访问 `/stock` 路由，验证页面正常显示
- 点击导航菜单"股票分析"，验证跳转正确

---

### 任务 28.15 - 股票分析端到端测试
**目标**: 测试股票分析完整流程
**操作**:
- 测试完整流程：
  1. 进入股票分析页面
  2. 搜索股票（如"贵州茅台"）
  3. 验证K线图显示
  4. 验证横轴双时间显示
  5. 双击某日K线，验证分时图和卦例浮窗
  6. 修改占验情况，验证K线样式更新
  7. 打开新窗口，搜索不同股票
- 测试边界情况：
  - 搜索不存在的股票
  - 无卦例对应的K线
  - 网络错误处理
**测试**:
- 执行完整流程测试
- 验证所有功能正常
- 验证边界情况处理正确

---

## 阶段二十九：占验情况系统

### 任务 29.1 - 占验情况数据结构设计
**目标**: 设计占验情况数据结构
**操作**:
- 创建独立的数据存储结构（JSON文件或NoSQL）
- 设计占验情况数据模型：卦例ID、占验状态、标注时间、备注
- 实现数据备份与恢复机制
**测试**:
```python
# tests/test_yanqing_28_1.py
yanqing_data = {
    "guali_id": 1,
    "status": "应验",
    "timestamp": "2024-03-15T14:30:00",
    "note": "实际走势与占断一致"
}
# 验证数据结构完整
```

---

### 任务 29.2 - 占验情况存储服务
**目标**: 实现占验情况存储服务
**操作**:
- 创建 `backend/services/yanqing_service.py`
- 实现标注占验情况方法
- 实现查询占验情况方法
- 实现批量导入/导出方法
**测试**:
```python
# tests/test_yanqing_28_2.py
yanqing_service = YanqingService()
yanqing_service.annotate(1, "应验", "实际走势一致")
result = yanqing_service.get_by_guali_id(1)
assert result["status"] == "应验"
```

---

### 任务 29.3 - 占验情况标注API
**目标**: 实现占验情况标注的API接口
**操作**:
- 创建 `backend/api/routers/yanqing.py`
- 实现 `POST /api/yanqing/annotate` 接口
- 实现 `GET /api/yanqing/{guali_id}` 接口
- 实现 `PUT /api/yanqing/{guali_id}` 接口
**测试**:
```bash
curl -X POST http://localhost:8000/api/yanqing/annotate \
  -H "Content-Type: application/json" \
  -d '{
    "guali_id": 1,
    "status": "应验",
    "note": "实际走势一致"
  }'
# 验证标注成功
```

---

### 任务 29.4 - 占验情况前端标注界面
**目标**: 创建占验情况标注的前端界面
**操作**:
- 在卦例详情页面添加占验情况标注组件
- 创建 `frontend/src/components/YanqingAnnotation.vue`
- 实现占验状态选择（应验、模糊、不验）
- 实现备注输入和保存功能
**测试**:
- 访问卦例详情页
- 选择占验状态并保存
- 验证标注成功

---

### 任务 29.5 - 占验情况检索集成
**目标**: 在复杂检索中集成占验情况检索
**操作**:
- 在字段库中添加"占验情况"字段
- 在条件构建器中支持占验情况筛选
- 修改检索后端逻辑，支持占验情况过滤
- 修改检索API，包含占验情况数据
**测试**:
- 使用占验情况条件检索
- 验证结果正确包含占验状态
- 验证多条件组合检索正确

---

## 阶段三十：多窗检索功能

### 任务 30.1 - 多窗检索入口
**目标**: 实现多窗检索入口
**操作**:
- 在检索结果页面添加"新建检索窗口"按钮
- 添加"对比模式"按钮
- 实现窗口管理组件
**测试**:
- 点击"新建检索窗口"
- 验证新窗口正常打开

---

### 任务 30.2 - 新窗口参数传递
**目标**: 实现窗口间参数传递
**操作**:
- 使用URL参数传递检索条件
- 实现条件序列化和反序列化
- 支持条件继承和修改
**测试**:
```bash
# 测试URL参数传递
# http://localhost:5173/search?condition={"field":"ben_gua_name","operator":"=","value":"乾为天"}
# 验证条件正确加载
```

---

### 任务 30.3 - 窗口间通信
**目标**: 实现窗口间通信机制
**操作**:
- 使用postMessage API实现窗口通信
- 实现主窗口与子窗口的消息传递
- 实现窗口间条件共享
**测试**:
- 打开多个窗口
- 在一个窗口修改条件
- 验证其他窗口能接收到更新

---

### 任务 30.4 - 对比模式
**目标**: 实现多窗口对比模式
**操作**:
- 创建对比模式组件
- 实现多窗口结果并排展示
- 添加对比表格，显示各窗口的关键差异
**测试**:
- 选择多个窗口进行对比
- 验证对比结果正确显示

---

### 任务 30.5 - 窗口合并
**目标**: 实现窗口合并功能
**操作**:
- 添加"合并窗口"按钮
- 实现窗口关闭和条件合并
- 将多个窗口的条件合并到主窗口
**测试**:
- 打开多个窗口
- 点击合并窗口
- 验证条件正确合并

---

## 阶段三十一：集成测试

### 任务 31.1 - 端到端测试 - 录入流程
**目标**: 测试完整的卦例录入流程
**操作**:
- 手动输入一个卦例
- CSV导入一批卦例
- 验证所有卦例正确保存
**测试**:
- 执行完整流程
- 检查数据库
- 验证结果正确

---

### 任务 31.2 - 端到端测试 - 占验情况流程
**目标**: 测试占验情况标注和检索流程
**操作**:
- 查看卦例详情
- 标注占验情况
- 使用占验条件检索
- 验证结果正确
**测试**:
- 执行完整流程
- 验证占验情况正确存储
- 验证检索结果正确

---

### 任务 31.3 - 端到端测试 - 多窗检索流程
**目标**: 测试多窗检索流程
**操作**:
- 打开多个检索窗口
- 在不同窗口设置不同检索条件
- 使用对比模式对比结果
- 合并窗口
**测试**:
- 执行完整流程
- 验证窗口间通信正常
- 验证对比结果正确

---

### 任务 31.4 - 端到端测试 - 完整综合流程
**目标**: 测试完整的综合业务流程
**操作**:
- 导入卦例数据
- 标注多个卦例的占验情况
- 使用多种检索条件查询
- 开启多窗口对比不同检索结果
- 导出检索结果
**测试**:
- 执行完整综合流程
- 验证所有功能正常
- 验证数据一致性

---

### 任务 31.5 - 性能测试
**目标**: 测试系统性能
**操作**:
- 批量导入大量卦例
- 执行复杂检索
- 测试多窗口并发检索
- 测试响应时间
**测试**:
- 导入1000个卦例
- 执行复杂检索
- 开启5个检索窗口并发
- 验证响应时间在可接受范围

---

## 总结

本测试计划共包含 **31个阶段，约135个最小可分割任务**。

### 阶段概览

| 阶段 | 名称 | 任务数 | 状态 |
|------|------|--------|------|
| 阶段零 | 环境准备 | 4 | 已完成 |
| 阶段一 | 核心枚举定义 | 12 | 已完成 |
| 阶段二 | 核心业务类 | 4 | 已完成 |
| 阶段三 | 时间转换模块 | 7 | 已完成 |
| 阶段四 | 纳甲装卦模块 | 3 | 已完成 |
| 阶段五 | 六亲计算模块 | 3 | 已完成 |
| 阶段六 | 六神计算模块 | 3 | 已完成 |
| 阶段七 | 世应定位模块 | 3 | 已完成 |
| 阶段八 | 伏神计算模块 | 4 | 已完成 |
| 阶段九 | 反吟伏吟计算 | 4 | 已完成 |
| 阶段十 | 神煞计算模块 | 6 | 已完成 |
| 阶段十一 | 生旺墓绝计算 | 2 | 已完成 |
| 阶段十二 | Guali整合计算 | 2 | 已完成 |
| 阶段十三 | 数据库表创建 | 5 | 已完成 |
| 阶段十四 | 数据库操作 | 6 | 已完成 |
| 阶段十五 | 格式转换模块 | 7 | 已完成 |
| 阶段十六 | FastAPI基础 | 4 | 已完成 |
| 阶段十七 | 卦例API | 5 | 已完成 |
| 阶段十八 | 卦例详情API | 1 | 已完成 |
| 阶段十九 | CSV导入功能 | 2 | 已完成 |
| 阶段二十 | 图片存储 | 4 | 已完成 |
| 阶段二十一 | 前端基础页面 | 3 | 已完成 |
| 阶段二十二 | 卦例输入页面 | 4 | 已完成 |
| 阶段二十三 | CSV导入页面 | 2 | 已完成 |
| 阶段二十四 | 卦例列表页面 | 2 | 已完成 |
| 阶段二十五 | 卦例详情页面 | 3 | 已完成 |
| 阶段二十六 | 复杂检索-自定义 | 8 | 已完成 |
| 阶段二十七 | 检索结果展示 | 3 | 已完成 |
| **阶段二十八** | **ECharts集成** | **15** | **待开发** |
| 阶段二十九 | 占验情况系统 | 5 | 已完成 |
| 阶段三十 | 多窗检索功能 | 5 | 已完成 |
| 阶段三十一 | 集成测试 | 5 | 已完成 |

每个任务遵循：
1. **编写代码**
2. **编写测试**
3. **运行测试**
4. **修复问题**
5. **测试通过后进入下一任务**

建议的开发节奏：
- 每天完成1-3个任务
- 每个任务完成后立即测试
- 每阶段完成后进行阶段集成测试
