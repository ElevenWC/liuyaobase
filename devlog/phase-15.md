# 阶段十五：格式转换模块

**完成时间**: 2026-02-18

---

## 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 15.1 卦名转代码 | ✓ | gua_name_to_code |
| 15.2 代码转卦名 | ✓ | code_to_gua_name |
| 15.3 时间部分解析 | ✓ | parse_time_part |
| 15.4 重卦部分解析 | ✓ | parse_gua_part |
| 15.5 语句部分解析 | ✓ | parse_text_part |
| 15.6 完整标准格式解析 | ✓ | parse_standard_format |
| 15.7 标准格式转Guali对象 | ✓ | standard_format_to_guali |

---

## 创建的文件

### backend/core/converter.py

```python
def gua_name_to_code(name: str) -> Optional[int]
    """卦名转代码（0-63的整数）"""

def code_to_gua_name(code: int) -> Optional[str]
    """代码转卦名（中文名称）"""

def parse_time_part(time_str: str) -> Dict[str, int]
    """解析时间部分：年;月.日, -> {year, month, day}"""

def parse_gua_part(gua_str: str) -> Dict[str, Optional[str]]
    """解析重卦部分：本卦,之卦, -> {ben_gua_name, zhi_gua_name}"""

def parse_text_part(text_str: str) -> Dict[str, Optional[str]]
    """解析语句部分：占问,占断 -> {zhan_wen, zhan_duan}"""

def parse_standard_format(input_str: str) -> Dict[str, Any]
    """解析完整标准格式"""

def standard_format_to_guali(input_str: str) -> Guali
    """将标准格式转换为Guali业务对象"""

def guali_to_standard_format(guali: Guali) -> str
    """将Guali业务对象转换为标准格式字符串"""

def validate_standard_format(input_str: str) -> Tuple[bool, Optional[str]]
    """验证标准格式是否有效"""
```

---

## 标准格式定义

```
格式: "年;月.日,本卦,之卦,占问事由,占断"
示例: "2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨"
```

- 之卦留空则无动爻
- 占问和占断为可选字段

---

## 测试文件

### backend/tests/test_converter.py

- 38个测试用例
- 覆盖：卦名代码转换、各部分解析、完整格式解析、Guali转换

---

## Bug修复

### Bug: code_to_gua_name返回英文枚举名而非中文名

**问题**: 使用 `gua.name` 返回的是Python枚举成员名（如 `QIAN_WEI_TIAN`）

**修复**: 改用 `gua.gua_name` 属性获取中文名称

### Bug: parse_standard_format正则表达式问题

**问题**: 原正则表达式无法正确分割包含多个逗号的输入

**修复**: 改用简单的 `split(',')` 方法分割各部分

---

## 已知问题

### 枚举代码重复

`地水师` 和 `水地比` 有相同的代码值 `0b010000`，这是枚举定义中的问题，`from_code` 方法会返回第一个匹配的卦。建议后续修复枚举定义。
