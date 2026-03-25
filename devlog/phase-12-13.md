# 阶段12-13：Guali整合、数据库表

---

## 阶段十二：Guali类整合计算

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 12.1 calculate_all方法框架 | ✓ | 验证方法完整性 |
| 12.2 完整卦例计算测试 | ✓ | 216个测试用例 |

### calculate_all方法调用顺序

```python
def calculate_all(self):
    self.fill_ganzhi_time()     # 填充干支时间
    self.set_nama()             # 纳甲装卦
    self.set_shiying()          # 世应设置
    self.set_liuqin()           # 六亲计算
    self.set_liushen()          # 六神设置
    self.set_fushen()           # 伏神计算
    self.set_fanyin_fuyin()     # 反吟伏吟
    self.set_shensha()          # 神煞计算
    self.set_shengwang_mujue()  # 生旺墓绝
```

### 测试覆盖

- TestGualiCalculateAllFramework: 方法框架测试 (6个)
- TestCompleteGualiCalculation: 完整卦例计算测试 (4个)
- TestAllZhongGua: 全64卦验证测试 (192个)
- TestSpecialGua: 特殊卦例测试 (4个)
- TestCreateGualiFromInput: 工厂函数测试 (4个)
- TestGualiDisplay: 显示方法测试 (3个)
- TestBoundaryConditions: 边界条件测试 (3个)

### 文件
- `backend/tests/test_guali_calculate_all.py`

---

## 阶段十三：数据库表创建

**完成时间**: 2026-02-18

### 任务清单

| 任务 | 状态 | 说明 |
|------|------|------|
| 13.1 卦例表SQL | ✓ | create_guali_table.sql |
| 13.2 爻详情表SQL | ✓ | create_yao_detail_table.sql |
| 13.3 GualiModel | ✓ | SQLAlchemy模型 |
| 13.4 YaoDetailModel | ✓ | SQLAlchemy模型 |
| 13.5 初始化脚本 | ✓ | init_db.py |

### GualiModel 属性

```python
class GualiModel(Base):
    __tablename__ = 'guali'

    id = Column(Integer, primary_key=True)
    # 时间字段
    solar_year = Column(Integer, nullable=False)
    solar_month = Column(Integer, nullable=False)
    solar_day = Column(Integer, nullable=False)
    ganzhi_year = Column(String(4), nullable=False)
    ganzhi_month = Column(String(4), nullable=False)
    ganzhi_day = Column(String(4), nullable=False)
    xunkong = Column(String(8), nullable=False)
    # 卦象字段
    ben_gua_code = Column(Integer, nullable=False)
    zhi_gua_code = Column(Integer, nullable=True)
    yao_bian_code = Column(Integer, nullable=False, default=0)
    gongwei = Column(String(8), nullable=False)
    gongwei_index = Column(String(8), nullable=False)
    # 文本字段
    zhan_wen = Column(Text, nullable=True)
    zhan_duan = Column(Text, nullable=True)
    image_path = Column(String(512), nullable=True)
    # 时间戳
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    # 关系
    yao_details = relationship("YaoDetailModel", back_populates="guali")
```

### YaoDetailModel 属性

```python
class YaoDetailModel(Base):
    __tablename__ = 'yao_detail'

    id = Column(Integer, primary_key=True)
    guali_id = Column(Integer, ForeignKey('guali.id', ondelete='CASCADE'))
    position = Column(Integer, nullable=False)      # 1-6
    yao_type = Column(Integer, nullable=False)      # 1=阳, 0=阴
    state = Column(Integer, nullable=False)         # 1=动, 0=静
    dizhi = Column(String(4), nullable=False)
    liuqin = Column(String(8), nullable=True)
    liushen = Column(String(8), nullable=True)
    is_world = Column(Boolean, default=False)
    is_response = Column(Boolean, default=False)
    # 关系
    guali = relationship("GualiModel", back_populates="yao_details")
```

### YanqingModel 属性（占验情况）

```python
class YanqingModel(Base):
    __tablename__ = 'yanqing'

    id = Column(Integer, primary_key=True)
    guali_id = Column(Integer, unique=True, nullable=False)
    status = Column(String(8), nullable=False)      # 应验/模糊/不验
    note = Column(Text, nullable=True)
    annotated_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
```

### 文件
- `scripts/create_guali_table.sql`
- `scripts/create_yao_detail_table.sql`
- `scripts/init_db.py`
- `backend/db/models.py`
