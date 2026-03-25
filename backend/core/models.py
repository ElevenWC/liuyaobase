"""
六爻卦例分析系统 - 核心业务类定义

本模块定义六爻预测学的核心业务类，包括：
- Yao（爻）类：表示卦中的一个爻
- Guali（卦例）类：表示一个完整的卦例
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import date

from backend.core.enums import (
    Wuxing, Tiangan, Dizhi, DanGua, ZhongGua, LiuQin, LiuShen,
    get_shiying_by_gongwei
)
from backend.core.time_converter import solar_to_ganzhi_full
from backend.core.nama import load_dizhi_to_guali
from backend.core.fushen import calculate_fushen_for_guali
from backend.core.fanyin_fuyin import calculate_fanyin_fuyin_for_guali
from backend.core.shensha import calculate_shensha_for_guali
from backend.core.shengwang_mujue import calculate_shengwang_mujue_for_guali


# =============================================================================
# Yao（爻）类
# =============================================================================

@dataclass
class Yao:
    """
    爻类 - 表示卦中的一个爻

    爻位从1到6，分别对应初爻、二爻、三爻、四爻、五爻、上爻。

    Attributes:
        position: 爻位 (1-6)
        yao_type: 爻类型 (1=阳爻, 0=阴爻)
        state: 爻状态 (1=动爻, 0=静爻)
        dizhi: 爻地支
        liuqin: 六亲
        liushen: 六神
        is_world: 是否世爻
        is_response: 是否应爻
    """
    position: int                      # 爻位 (1-6)
    yao_type: int                      # 爻类型 (1=阳爻, 0=阴爻)
    state: int = 0                     # 爻状态 (1=动爻, 0=静爻)
    dizhi: Optional[Dizhi] = None      # 爻地支
    liuqin: Optional[LiuQin] = None    # 六亲
    liushen: Optional[LiuShen] = None  # 六神
    is_world: bool = False             # 是否世爻
    is_response: bool = False          # 是否应爻

    @property
    def wuxing(self) -> Optional[Wuxing]:
        """
        获取爻的五行属性（从地支五行获取）

        Returns:
            爻地支对应的五行，如果地支为None则返回None
        """
        if self.dizhi is None:
            return None
        return self.dizhi.wuxing

    @property
    def position_name(self) -> str:
        """
        获取爻位名称

        Returns:
            爻位的中文名称（初爻、二爻、三爻、四爻、五爻、上爻）
        """
        names = {1: "初爻", 2: "二爻", 3: "三爻", 4: "四爻", 5: "五爻", 6: "上爻"}
        return names.get(self.position, f"未知爻位({self.position})")

    @property
    def yao_type_name(self) -> str:
        """
        获取爻类型名称

        Returns:
            爻类型的中文名称（阳爻、阴爻）
        """
        return "阳爻" if self.yao_type == 1 else "阴爻"

    @property
    def state_name(self) -> str:
        """
        获取爻状态名称

        Returns:
            爻状态的中文名称（动爻、静爻）
        """
        return "动爻" if self.state == 1 else "静爻"

    def __repr__(self) -> str:
        """字符串表示"""
        parts = [f"{self.position_name}({self.yao_type_name}"]
        if self.state == 1:
            parts.append("动")
        parts.append(")")
        if self.dizhi:
            parts.append(f" {self.dizhi.value}")
        if self.liuqin:
            parts.append(f" {self.liuqin.value}")
        if self.liushen:
            parts.append(f"[{self.liushen.value}]")
        if self.is_world:
            parts.append(" 世")
        if self.is_response:
            parts.append(" 应")
        return "".join(parts)


# =============================================================================
# Guali（卦例）类
# =============================================================================

@dataclass
class Guali:
    """
    卦例类 - 表示一个完整的六爻卦例

    Attributes:
        id: 卦例ID
        solar_year: 公历年
        solar_month: 公历月
        solar_day: 公历日
        ganzhi_year: 年柱干支
        ganzhi_month: 月柱干支
        ganzhi_day: 日柱干支
        xunkong: 旬空
        ben_gua: 本卦
        zhi_gua: 之卦（可为空，表示无动爻）
        yao_bian_code: 爻变代码
        zhan_wen: 占问事由
        zhan_duan: 占断
        image_path: 图片路径
        yaos: 六个爻的列表
    """
    # 基本信息
    id: Optional[int] = None

    # 公历时间
    solar_year: Optional[int] = None
    solar_month: Optional[int] = None
    solar_day: Optional[int] = None

    # 干支时间
    ganzhi_year: Optional[str] = None
    ganzhi_month: Optional[str] = None
    ganzhi_day: Optional[str] = None
    xunkong: Optional[str] = None

    # 卦信息
    ben_gua: Optional[ZhongGua] = None
    zhi_gua: Optional[ZhongGua] = None
    yao_bian_code: int = 0

    # 文本信息
    zhan_wen: Optional[str] = None
    zhan_duan: Optional[str] = None
    image_path: Optional[str] = None

    # 爻列表（在__post_init__中初始化）
    yaos: List[Yao] = field(default_factory=list)

    # 伏神信息（在set_fushen中计算）
    fushen: Dict = field(default_factory=dict)

    # 反吟伏吟信息（在set_fanyin_fuyin中计算）
    fanyin_fuyin: Dict = field(default_factory=dict)

    # 神煞信息（在set_shensha中计算）
    shensha: Dict = field(default_factory=dict)

    # 生旺墓绝信息（在set_shengwang_mujue中计算）
    shengwang_mujue: Dict = field(default_factory=dict)

    def __post_init__(self):
        """
        初始化后处理

        根据本卦和之卦信息初始化六个爻
        """
        if self.ben_gua is not None and len(self.yaos) == 0:
            self._init_yaos()

    def _init_yaos(self):
        """
        初始化六个爻

        根据本卦代码初始化六个爻的类型
        根据爻变代码初始化六个爻的状态
        """
        if self.ben_gua is None:
            return

        # 获取本卦代码
        ben_gua_code = self.ben_gua.code

        # 初始化六个爻
        for pos in range(1, 7):
            # 从代码中提取爻类型（从低位到高位：初爻到上爻）
            # 爻位1对应最低位，爻位6对应最高位
            yao_type = (ben_gua_code >> (pos - 1)) & 1

            # 从爻变代码中提取爻状态
            # 如果有之卦，检查该爻是否为动爻
            state = 0
            if self.yao_bian_code != 0:
                state = (self.yao_bian_code >> (pos - 1)) & 1

            yao = Yao(
                position=pos,
                yao_type=yao_type,
                state=state
            )
            self.yaos.append(yao)

    @property
    def ben_gua_code(self) -> int:
        """获取本卦代码"""
        return self.ben_gua.code if self.ben_gua else 0

    @property
    def zhi_gua_code(self) -> int:
        """获取之卦代码"""
        return self.zhi_gua.code if self.zhi_gua else 0

    @property
    def has_zhi_gua(self) -> bool:
        """判断是否有之卦（是否有动爻）"""
        return self.zhi_gua is not None and self.yao_bian_code != 0

    @property
    def gongwei(self) -> Optional[str]:
        """获取卦宫"""
        return self.ben_gua.gongwei if self.ben_gua else None

    @property
    def gongwei_index(self) -> Optional[str]:
        """获取宫位"""
        return self.ben_gua.gongwei_index if self.ben_gua else None

    @property
    def gongwuxing(self) -> Optional[Wuxing]:
        """获取卦宫五行"""
        return self.ben_gua.gongwuxing if self.ben_gua else None

    @property
    def ben_gua_name(self) -> Optional[str]:
        """获取本卦名"""
        return self.ben_gua.gua_name if self.ben_gua else None

    @property
    def zhi_gua_name(self) -> Optional[str]:
        """获取之卦名"""
        return self.zhi_gua.gua_name if self.zhi_gua else None

    @property
    def gua_display_name(self) -> str:
        """
        获取卦名显示字符串

        Returns:
            如果有之卦返回"本卦名之之卦名"，否则返回"本卦名"
        """
        if self.ben_gua is None:
            return "未知卦"

        if self.has_zhi_gua:
            return f"{self.ben_gua_name}之{self.zhi_gua_name}"
        return self.ben_gua_name

    @property
    def day_tiangan(self) -> Optional[Tiangan]:
        """获取日干"""
        if self.ganzhi_day and len(self.ganzhi_day) >= 1:
            return Tiangan.from_char(self.ganzhi_day[0])
        return None

    @property
    def day_dizhi(self) -> Optional[Dizhi]:
        """获取日支"""
        if self.ganzhi_day and len(self.ganzhi_day) >= 2:
            return Dizhi.from_char(self.ganzhi_day[1])
        return None

    @property
    def moving_yaos(self) -> List[Yao]:
        """获取所有动爻"""
        return [yao for yao in self.yaos if yao.state == 1]

    @property
    def world_yao(self) -> Optional[Yao]:
        """获取世爻"""
        for yao in self.yaos:
            if yao.is_world:
                return yao
        return None

    @property
    def response_yao(self) -> Optional[Yao]:
        """获取应爻"""
        for yao in self.yaos:
            if yao.is_response:
                return yao
        return None

    def get_yao_by_position(self, position: int) -> Optional[Yao]:
        """
        根据爻位获取爻

        Args:
            position: 爻位 (1-6)

        Returns:
            对应的爻，如果不存在返回None
        """
        for yao in self.yaos:
            if yao.position == position:
                return yao
        return None

    def set_shiying(self):
        """
        设置世应爻

        根据宫位设置世爻和应爻
        """
        if self.ben_gua is None:
            return

        gongwei_index = self.ben_gua.gongwei_index
        shi_pos, ying_pos = get_shiying_by_gongwei(gongwei_index)

        for yao in self.yaos:
            yao.is_world = (yao.position == shi_pos)
            yao.is_response = (yao.position == ying_pos)

    def set_nama(self):
        """
        设置纳甲（为六爻装地支）

        根据本卦的内卦和外卦为六个爻设置地支
        """
        load_dizhi_to_guali(self)

    def set_liuqin(self):
        """
        设置六亲

        根据卦宫五行和爻地支五行计算六亲
        """
        if self.ben_gua is None:
            return

        gongwuxing = self.ben_gua.gongwuxing

        for yao in self.yaos:
            if yao.dizhi is not None:
                yao_wuxing = yao.dizhi.wuxing
                yao.liuqin = LiuQin.calculate(gongwuxing, yao_wuxing)

    def set_liushen(self):
        """
        设置六神

        根据日干和爻位设置六神
        """
        tiangan = self.day_tiangan
        if tiangan is None:
            return

        for yao in self.yaos:
            yao.liushen = LiuShen.get_by_tiangan_and_position(tiangan, yao.position)

    def set_fushen(self):
        """
        设置伏神

        检查六亲是否齐全，若有缺失则计算伏神
        """
        self.fushen = calculate_fushen_for_guali(self)

    def set_fanyin_fuyin(self):
        """
        设置反吟伏吟

        比较本卦和之卦的内卦外卦，判断是否存在反吟伏吟关系
        """
        self.fanyin_fuyin = calculate_fanyin_fuyin_for_guali(self)

    def set_shensha(self):
        """
        设置神煞

        根据日干和日支计算所有神煞（干禄、驿马、羊刃、桃花）
        """
        self.shensha = calculate_shensha_for_guali(self)

    def set_shengwang_mujue(self):
        """
        设置生旺墓绝

        计算各爻与日支的生旺墓绝关系
        """
        self.shengwang_mujue = calculate_shengwang_mujue_for_guali(self)

    def calculate_all(self):
        """
        计算所有派生属性

        包括：纳甲装卦、世应位置、六亲、六神、伏神、反吟伏吟、神煞、生旺墓绝
        """
        self.set_nama()           # 纳甲装卦
        self.set_shiying()
        self.set_liuqin()
        self.set_liushen()
        self.set_fushen()         # 伏神
        self.set_fanyin_fuyin()   # 反吟伏吟
        self.set_shensha()        # 神煞
        self.set_shengwang_mujue() # 生旺墓绝

    def fill_ganzhi_time(self):
        """
        填充干支时间

        根据公历时间自动填充年柱、月柱、日柱和旬空
        """
        if self.solar_year is None or self.solar_month is None or self.solar_day is None:
            return

        try:
            ganzhi = solar_to_ganzhi_full(self.solar_year, self.solar_month, self.solar_day)
            self.ganzhi_year = ganzhi["year"]
            self.ganzhi_month = ganzhi["month"]
            self.ganzhi_day = ganzhi["day"]
            self.xunkong = ganzhi["xunkong"]
        except Exception:
            # 如果转换失败，保持原值
            pass

    def __repr__(self) -> str:
        """字符串表示"""
        parts = [f"Guali(id={self.id}, "]
        parts.append(f"卦={self.gua_display_name}, ")
        parts.append(f"时间={self.solar_year}/{self.solar_month}/{self.solar_day}")
        if self.zhan_wen:
            parts.append(f", 占问={self.zhan_wen[:20]}...")
        parts.append(")")
        return "".join(parts)

    def display(self) -> str:
        """
        生成卦例的显示字符串

        Returns:
            格式化的卦例信息字符串
        """
        lines = []

        # 卦名
        lines.append(f"【{self.gua_display_name}】")
        lines.append(f"  卦宫: {self.gongwei} ({self.gongwei_index})")
        lines.append("")

        # 时间
        if self.solar_year:
            lines.append(f"  公历: {self.solar_year}年{self.solar_month}月{self.solar_day}日")
        if self.ganzhi_day:
            lines.append(f"  日柱: {self.ganzhi_day}")
        if self.xunkong:
            lines.append(f"  旬空: {self.xunkong}")
        lines.append("")

        # 占问占断
        if self.zhan_wen:
            lines.append(f"  占问: {self.zhan_wen}")
        if self.zhan_duan:
            lines.append(f"  占断: {self.zhan_duan}")
        lines.append("")

        # 六爻
        lines.append("  六爻:")
        for yao in reversed(self.yaos):  # 从上爻到初爻显示
            yao_str = f"    {yao.position_name}: "
            if yao.dizhi:
                yao_str += f"{yao.dizhi.value}"
            if yao.liuqin:
                yao_str += f" {yao.liuqin.value}"
            if yao.liushen:
                yao_str += f" [{yao.liushen.value}]"
            if yao.is_world:
                yao_str += " 世"
            if yao.is_response:
                yao_str += " 应"
            if yao.state == 1:
                yao_str += " ○"  # 动爻标记
            lines.append(yao_str)

        # 伏神信息
        if self.fushen and self.fushen.get("has_fushen"):
            lines.append("")
            lines.append("  伏神:")
            for fs in self.fushen.get("fushen_list", []):
                fs_str = f"    {fs['liuqin']}: 伏{fs['fushen_position']}爻{fs['fushen_dizhi']}({fs['fushen_wuxing']})"
                fs_str += f" / 飞神{fs['feishen_dizhi']}({fs['feishen_liuqin']})"
                fs_str += f" - {fs['relation']}"
                lines.append(fs_str)

        # 神煞信息
        if self.shensha:
            lines.append("")
            lines.append("  神煞:")
            shensha_parts = []
            for name, info in self.shensha.items():
                if info.get("is_in_gua"):
                    yao_positions = [str(y["position"]) for y in info.get("yaos", [])]
                    shensha_parts.append(f"{info['dizhi']}({name}{'在' + ','.join(yao_positions) + '爻' if yao_positions else ''})")
            if shensha_parts:
                lines.append("    " + "  ".join(shensha_parts))

        # 反吟伏吟信息
        if self.fanyin_fuyin and (self.fanyin_fuyin.get("has_fanyin") or self.fanyin_fuyin.get("has_fuyin")):
            lines.append("")
            lines.append("  反吟伏吟:")
            for detail in self.fanyin_fuyin.get("details", []):
                lines.append(f"    {detail['position']}: {detail['from']}→{detail['to']} ({detail['type']})")

        return "\n".join(lines)


# =============================================================================
# 工厂函数
# =============================================================================

def create_guali_from_input(
    solar_year: int,
    solar_month: int,
    solar_day: int,
    ben_gua_name: str,
    zhi_gua_name: Optional[str] = None,
    zhan_wen: Optional[str] = None,
    zhan_duan: Optional[str] = None
) -> Guali:
    """
    从输入创建卦例

    这是一个工厂函数，用于从用户输入创建卦例对象。
    后续需要调用calculate_all()计算派生属性。

    Args:
        solar_year: 公历年
        solar_month: 公历月
        solar_day: 公历日
        ben_gua_name: 本卦名
        zhi_gua_name: 之卦名（可选）
        zhan_wen: 占问事由（可选）
        zhan_duan: 占断（可选）

    Returns:
        初始化的卦例对象
    """
    # 从卦名获取枚举
    ben_gua = ZhongGua.from_name(ben_gua_name)
    if ben_gua is None:
        raise ValueError(f"无效的本卦名: {ben_gua_name}")

    zhi_gua = None
    if zhi_gua_name:
        zhi_gua = ZhongGua.from_name(zhi_gua_name)
        if zhi_gua is None:
            raise ValueError(f"无效的之卦名: {zhi_gua_name}")

    # 计算爻变代码
    yao_bian_code = 0
    if zhi_gua:
        yao_bian_code = ben_gua.code ^ zhi_gua.code

    guali = Guali(
        solar_year=solar_year,
        solar_month=solar_month,
        solar_day=solar_day,
        ben_gua=ben_gua,
        zhi_gua=zhi_gua,
        yao_bian_code=yao_bian_code,
        zhan_wen=zhan_wen,
        zhan_duan=zhan_duan
    )

    return guali
