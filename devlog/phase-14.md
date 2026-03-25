# 阶段十四：数据库CRUD操作

**完成时间**: 2026-02-18

---

## 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 14.1 Session上下文管理器 | ✓ | 已在connection.py中实现 |
| 14.2 卦例CRUD - 创建 | ✓ | create_guali, create_from_guali |
| 14.3 卦例CRUD - 查询 | ✓ | get_guali_by_id, get_all_gualis, search_gualis |
| 14.4 卦例CRUD - 更新 | ✓ | update_guali（只允许更新语句字段） |
| 14.5 卦例CRUD - 删除 | ✓ | delete_guali（级联删除爻详情） |
| 14.6 爻详情CRUD - 批量插入 | ✓ | save_yao_details, get_yao_details |

---

## 创建的文件

### backend/db/repositories.py

```python
class GualiRepository:
    """卦例数据仓库"""

    def create_guali(...)       # 创建卦例
    def create_from_guali(...)  # 从业务对象创建
    def get_guali_by_id(...)    # 根据ID获取
    def get_all_gualis(...)     # 分页获取所有
    def get_gualis_by_year(...) # 按年份获取
    def get_gualis_by_gongwei(...) # 按卦宫获取
    def search_gualis(...)      # 搜索卦例
    def update_guali(...)       # 更新（只允许语句字段）
    def delete_guali(...)       # 删除（级联删除爻详情）
    def model_to_guali(...)     # 模型转业务对象

class YaoDetailRepository:
    """爻详情数据仓库"""

    def save_yao_details(...)   # 批量保存
    def get_yao_details(...)    # 获取卦例的所有爻详情
    def get_yao_detail_by_position(...) # 获取指定位置的爻

class YanqingRepository:
    """占验情况数据仓库"""

    def annotate(...)           # 标注占验情况
    def get_by_guali_id(...)    # 根据卦例ID获取
    def delete_by_guali_id(...) # 删除
    def get_all_by_status(...)  # 按状态获取列表
```

---

## 测试文件

### backend/tests/test_repositories.py

- 29个测试用例
- 覆盖：创建、查询、更新、删除、转换、集成测试

---

## Bug修复

### Bug: 测试用例中卦代码格式问题

**问题**: 测试用例使用 `111111` 作为卦代码，但实际 `0b111111` 的十进制值是 `63`

**修复**: 将测试用例中的代码改为 `0b111111` 格式

### Bug: Session事务隔离问题

**问题**: 删除操作后查询仍返回数据

**修复**: 在删除操作后添加 `db_session.flush()` 和 `db_session.expire_all()` 来刷新会话状态

---

## 设计要点

1. **时间字段和卦象字段禁止修改**，只允许更新语句字段（占问事由、占断）
2. **删除卦例时级联删除爻详情**（通过SQLAlchemy的cascade设置）
3. **支持传入外部Session**，便于事务管理
4. **占验情况独立存储**，与主数据库弱耦合
