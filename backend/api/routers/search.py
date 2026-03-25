"""
六爻卦例分析系统 - 复杂检索API路由

提供复杂的卦例检索功能，支持多种条件组合和关系查询。
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from backend.db.connection import get_session
from backend.db.models import GualiModel, YaoDetailModel
from backend.api.schemas import (
    SearchCondition,
    SearchRequest,
    SearchResponse,
    GualiResponse
)
from backend.core.enums import Dizhi, Wuxing, Tiangan, LiuQin, LiuShen
from backend.services.yanqing_service import get_yanqing_service


router = APIRouter(prefix="/api/search", tags=["复杂检索"])


# =============================================================================
# 辅助函数
# =============================================================================

def get_tiangan_value(tiangan_str: str) -> Optional[Tiangan]:
    """从字符串获取天干枚举"""
    tiangan_map = {
        '甲': Tiangan.JIA, '乙': Tiangan.YI, '丙': Tiangan.BING,
        '丁': Tiangan.DING, '戊': Tiangan.WU, '己': Tiangan.JI,
        '庚': Tiangan.GENG, '辛': Tiangan.XIN, '壬': Tiangan.REN,
        '癸': Tiangan.GUI
    }
    return tiangan_map.get(tiangan_str)


def get_dizhi_value(dizhi_str: str) -> Optional[Dizhi]:
    """从字符串获取地支枚举"""
    dizhi_map = {
        '子': Dizhi.ZI, '丑': Dizhi.CHOU, '寅': Dizhi.YIN,
        '卯': Dizhi.MAO, '辰': Dizhi.CHEN, '巳': Dizhi.SI,
        '午': Dizhi.WU, '未': Dizhi.WEI, '申': Dizhi.SHEN,
        '酉': Dizhi.YOU, '戌': Dizhi.XU, '亥': Dizhi.HAI
    }
    return dizhi_map.get(dizhi_str)


def get_wuxing_value(wuxing_str: str) -> Optional[Wuxing]:
    """从字符串获取五行枚举"""
    wuxing_map = {
        '金': Wuxing.JIN, '木': Wuxing.MU, '水': Wuxing.SHUI,
        '火': Wuxing.HUO, '土': Wuxing.TU
    }
    return wuxing_map.get(wuxing_str)


def get_liuqin_value(liuqin_str: str) -> Optional[LiuQin]:
    """从字符串获取六亲枚举"""
    liuqin_map = {
        '父母': LiuQin.FU_MU, '官鬼': LiuQin.GUAN_GUI,
        '子孙': LiuQin.ZI_SUN, '妻财': LiuQin.QI_CAI,
        '兄弟': LiuQin.XIONG_DI
    }
    return liuqin_map.get(liuqin_str)


def get_liushen_value(liushen_str: str) -> Optional[LiuShen]:
    """从字符串获取六神枚举"""
    liushen_map = {
        '青龙': LiuShen.QING_LONG, '朱雀': LiuShen.ZHU_QUE,
        '勾陈': LiuShen.GOU_CHEN, '螣蛇': LiuShen.TENG_SHE,
        '白虎': LiuShen.BAI_HU, '玄武': LiuShen.XUAN_WU
    }
    return liushen_map.get(liushen_str)


def get_he_dizhi(dizhi: Dizhi) -> Optional[Dizhi]:
    """获取相合地支"""
    he_map = {
        Dizhi.ZI: Dizhi.CHOU, Dizhi.CHOU: Dizhi.ZI,
        Dizhi.YIN: Dizhi.HAI, Dizhi.HAI: Dizhi.YIN,
        Dizhi.MAO: Dizhi.XU, Dizhi.XU: Dizhi.MAO,
        Dizhi.CHEN: Dizhi.YOU, Dizhi.YOU: Dizhi.CHEN,
        Dizhi.SI: Dizhi.SHEN, Dizhi.SHEN: Dizhi.SI,
        Dizhi.WU: Dizhi.WEI, Dizhi.WEI: Dizhi.WU
    }
    return he_map.get(dizhi)


def get_chong_dizhi(dizhi: Dizhi) -> Optional[Dizhi]:
    """获取相冲地支"""
    chong_map = {
        Dizhi.ZI: Dizhi.WU, Dizhi.WU: Dizhi.ZI,
        Dizhi.CHOU: Dizhi.WEI, Dizhi.WEI: Dizhi.CHOU,
        Dizhi.YIN: Dizhi.SHEN, Dizhi.SHEN: Dizhi.YIN,
        Dizhi.MAO: Dizhi.YOU, Dizhi.YOU: Dizhi.MAO,
        Dizhi.CHEN: Dizhi.XU, Dizhi.XU: Dizhi.CHEN,
        Dizhi.SI: Dizhi.HAI, Dizhi.HAI: Dizhi.SI
    }
    return chong_map.get(dizhi)


# =============================================================================
# 条件解析
# =============================================================================

def build_simple_condition(condition: SearchCondition, session: Session):
    """构建简单条件查询"""
    field = condition.field
    operator = condition.operator
    value = condition.value

    conditions = []

    # 时间类字段
    if field == 'solar_year':
        if operator == '=':
            conditions.append(GualiModel.solar_year == int(value))
        elif operator == '≠':
            conditions.append(GualiModel.solar_year != int(value))
        elif operator == '>':
            conditions.append(GualiModel.solar_year > int(value))
        elif operator == '<':
            conditions.append(GualiModel.solar_year < int(value))
        elif operator == '≥':
            conditions.append(GualiModel.solar_year >= int(value))
        elif operator == '≤':
            conditions.append(GualiModel.solar_year <= int(value))

    elif field == 'ganzhi_day':
        if operator == '=':
            conditions.append(GualiModel.ganzhi_day == value)
        elif operator == '≠':
            conditions.append(GualiModel.ganzhi_day != value)

    elif field == 'ganzhi_month':
        if operator == '=':
            conditions.append(GualiModel.ganzhi_month == value)
        elif operator == '≠':
            conditions.append(GualiModel.ganzhi_month != value)

    elif field == 'ganzhi_year':
        if operator == '=':
            conditions.append(GualiModel.ganzhi_year == value)
        elif operator == '≠':
            conditions.append(GualiModel.ganzhi_year != value)

    elif field == 'day_tiangan':
        # 日干
        day_gan = value[0] if value else None
        if operator == '=' and day_gan:
            conditions.append(GualiModel.ganzhi_day.like(f'{day_gan}%'))
        elif operator == '≠' and day_gan:
            conditions.append(~GualiModel.ganzhi_day.like(f'{day_gan}%'))

    elif field == 'day_dizhi':
        # 日支
        if operator == '=' and value:
            conditions.append(GualiModel.ganzhi_day.like(f'%{value}'))
        elif operator == '≠' and value:
            conditions.append(~GualiModel.ganzhi_day.like(f'%{value}'))

    elif field == 'xunkong':
        if operator == '=':
            conditions.append(GualiModel.xunkong.like(f'%{value}%'))
        elif operator == '≠':
            conditions.append(~GualiModel.xunkong.like(f'%{value}%'))

    # 卦类字段
    elif field == 'ben_gua_name':
        from backend.core.converter import code_to_gua_name
        from backend.core.enums import ZhongGua
        if operator == '=':
            gua = ZhongGua.from_name(value)
            if gua:
                conditions.append(GualiModel.ben_gua_code == gua.code)
        elif operator == '≠':
            gua = ZhongGua.from_name(value)
            if gua:
                conditions.append(GualiModel.ben_gua_code != gua.code)
        elif operator == '包含':
            # 模糊搜索
            conditions.append(text(f"ben_gua_code IN (SELECT code FROM zhonggua WHERE name LIKE '%{value}%')"))
        elif operator == '不包含':
            conditions.append(text(f"ben_gua_code NOT IN (SELECT code FROM zhonggua WHERE name LIKE '%{value}%')"))

    elif field == 'zhi_gua_name':
        from backend.core.enums import ZhongGua
        if operator == '=':
            gua = ZhongGua.from_name(value)
            if gua:
                conditions.append(GualiModel.zhi_gua_code == gua.code)
            else:
                conditions.append(GualiModel.zhi_gua_code.is_(None))
        elif operator == '≠':
            gua = ZhongGua.from_name(value)
            if gua:
                conditions.append(GualiModel.zhi_gua_code != gua.code)

    elif field == 'gongwei':
        if operator == '=':
            conditions.append(GualiModel.gongwei == value)
        elif operator == '≠':
            conditions.append(GualiModel.gongwei != value)

    elif field == 'gongwei_index':
        if operator == '=':
            conditions.append(GualiModel.gongwei_index == value)
        elif operator == '≠':
            conditions.append(GualiModel.gongwei_index != value)

    elif field == 'special_type':
        # 特殊类型：六冲卦/六合卦
        if value == 'liuchong':
            liuchong_codes = [0b111111, 0b100100, 0b010010, 0b001001,
                            0b000000, 0b011011, 0b101101, 0b110110,
                            0b111100, 0b100111]  # 六冲卦代码
            conditions.append(GualiModel.ben_gua_code.in_(liuchong_codes))
        elif value == 'liuhe':
            liuhe_codes = [0b000111, 0b010001, 0b101000, 0b110101,
                          0b111000, 0b100011, 0b001101, 0b011100]  # 六合卦代码
            conditions.append(GualiModel.ben_gua_code.in_(liuhe_codes))

    # 其他字段
    elif field == 'zhan_wen':
        if operator == '包含':
            conditions.append(GualiModel.zhan_wen.like(f'%{value}%'))
        elif operator == '不包含':
            conditions.append(~GualiModel.zhan_wen.like(f'%{value}%'))
        elif operator == '=':
            conditions.append(GualiModel.zhan_wen == value)

    elif field == 'zhan_duan':
        if operator == '包含':
            conditions.append(GualiModel.zhan_duan.like(f'%{value}%'))
        elif operator == '不包含':
            conditions.append(~GualiModel.zhan_duan.like(f'%{value}%'))
        elif operator == '=':
            conditions.append(GualiModel.zhan_duan == value)

    elif field == 'yanqing_status':
        # 占验情况筛选
        yanqing_service = get_yanqing_service()
        yanqing_data = yanqing_service.get_by_status(value)
        guali_ids = [data['guali_id'] for data in yanqing_data]
        if guali_ids:
            conditions.append(GualiModel.id.in_(guali_ids))
        else:
            # 没有匹配的占验记录，返回不可能满足的条件
            conditions.append(GualiModel.id < 0)

    return conditions


def build_yao_condition(condition: SearchCondition, session: Session):
    """构建爻类条件查询 - 通过子查询"""
    field = condition.field
    operator = condition.operator
    value = condition.value

    # 爻属性条件
    yao_conditions = []

    if field == 'liuqin':
        if operator == '=':
            yao_conditions.append(YaoDetailModel.liuqin == value)
        elif operator == '≠':
            yao_conditions.append(YaoDetailModel.liuqin != value)

    elif field == 'liushen':
        if operator == '=':
            yao_conditions.append(YaoDetailModel.liushen == value)
        elif operator == '≠':
            yao_conditions.append(YaoDetailModel.liushen != value)

    elif field == 'dizhi':
        if operator == '=':
            yao_conditions.append(YaoDetailModel.dizhi == value)
        elif operator == '≠':
            yao_conditions.append(YaoDetailModel.dizhi != value)

    elif field == 'yao_type':
        if operator == '=':
            yao_conditions.append(YaoDetailModel.yao_type == int(value))
        elif operator == '≠':
            yao_conditions.append(YaoDetailModel.yao_type != int(value))

    elif field == 'yao_state':
        if operator == '=':
            yao_conditions.append(YaoDetailModel.state == int(value))
        elif operator == '≠':
            yao_conditions.append(YaoDetailModel.state != int(value))

    elif field == 'shi_ying':
        if value == 'world':
            yao_conditions.append(YaoDetailModel.is_world == True)
        elif value == 'response':
            yao_conditions.append(YaoDetailModel.is_response == True)

    elif field == 'andong':
        # 暗动：爻地支与日支相冲
        # 需要先查日支，再判断
        pass  # 这个需要更复杂的处理

    return yao_conditions


def build_compound_condition(condition: SearchCondition, session: Session):
    """构建复合字段条件查询"""
    field = condition.field
    operator = condition.operator
    value = condition.value
    relation_type = condition.relation_type
    target_field = condition.target_field

    # 解析复合字段
    parts = field.split('.')
    if len(parts) != 2:
        return []

    entity, attr = parts
    conditions = []

    # 世爻/应爻条件
    if entity in ['world_yao', 'response_yao']:
        is_world = entity == 'world_yao'
        is_response = entity == 'response_yao'

        if attr == 'liuqin':
            subq = session.query(YaoDetailModel.guali_id).filter(
                YaoDetailModel.is_world == is_world,
                YaoDetailModel.is_response == is_response,
                YaoDetailModel.liuqin == value
            )
            conditions.append(GualiModel.id.in_(subq))

        elif attr == 'dizhi':
            subq = session.query(YaoDetailModel.guali_id).filter(
                YaoDetailModel.is_world == is_world,
                YaoDetailModel.is_response == is_response,
                YaoDetailModel.dizhi == value
            )
            conditions.append(GualiModel.id.in_(subq))

        elif attr == 'liushen':
            subq = session.query(YaoDetailModel.guali_id).filter(
                YaoDetailModel.is_world == is_world,
                YaoDetailModel.is_response == is_response,
                YaoDetailModel.liushen == value
            )
            conditions.append(GualiModel.id.in_(subq))

    # 六亲爻条件（如妻财爻、子孙爻等）
    elif entity in ['qicai_yao', 'zisun_yao', 'guangui_yao', 'fumu_yao', 'xiongdi_yao']:
        liuqin_map = {
            'qicai_yao': '妻财',
            'zisun_yao': '子孙',
            'guangui_yao': '官鬼',
            'fumu_yao': '父母',
            'xiongdi_yao': '兄弟'
        }
        liuqin_value = liuqin_map.get(entity)

        if attr == 'dizhi':
            subq = session.query(YaoDetailModel.guali_id).filter(
                YaoDetailModel.liuqin == liuqin_value,
                YaoDetailModel.dizhi == value
            )
            conditions.append(GualiModel.id.in_(subq))

    # 关系运算符处理
    if operator == '与' and relation_type and target_field:
        conditions.extend(build_relation_condition(field, relation_type, target_field, session))

    elif operator == 'WITH' and relation_type and target_field:
        conditions.extend(build_with_condition(field, relation_type, target_field, session))

    return conditions


def build_relation_condition(source_field: str, relation_type: str, target_field: str, session: Session):
    """
    构建关系条件（与运算符）

    例如：世爻.地支 与 日支 = 相合
    意思是世爻的地支与日支相合

    Args:
        source_field: 源字段，如 'world_yao.dizhi'
        relation_type: 关系类型，如 'he', 'chong', 'sheng', 'ke'
        target_field: 目标字段，如 'day_dizhi'
        session: 数据库会话

    Returns:
        SQLAlchemy条件列表
    """
    from backend.core.enums import Dizhi, Wuxing

    conditions = []

    # 解析源字段
    source_parts = source_field.split('.')
    if len(source_parts) != 2:
        return conditions

    source_entity, source_attr = source_parts

    # 地支相合相冲映射
    he_map = {
        '子': '丑', '丑': '子', '寅': '亥', '亥': '寅',
        '卯': '戌', '戌': '卯', '辰': '酉', '酉': '辰',
        '巳': '申', '申': '巳', '午': '未', '未': '午'
    }
    chong_map = {
        '子': '午', '午': '子', '丑': '未', '未': '丑',
        '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'
    }
    # 五行相生映射
    sheng_map = {
        '子': '申', '亥': '申',  # 水生木，金生水
        '寅': '子', '卯': '亥',  # 木生火，水生木
        '巳': '寅', '午': '卯',  # 火生土，木生火
        '辰': '巳', '戌': '巳', '丑': '午', '未': '午',  # 土生金，火生土
        '申': '辰', '酉': '巳',  # 金生水，火生金
    }
    # 简化的五行相克映射（基于地支）
    ke_map = {
        '子': '巳', '亥': '巳',  # 水克火
        '寅': '辰', '卯': '辰',  # 木克土
        '巳': '申', '午': '申',  # 火克金
        '辰': '子', '戌': '亥', '丑': '子', '未': '亥',  # 土克水
        '申': '寅', '酉': '卯',  # 金克木
    }

    # 处理爻类字段与日支的关系
    if target_field == 'day_dizhi' and source_attr == 'dizhi':
        # 确定爻的筛选条件
        yao_filter = None
        if source_entity == 'world_yao':
            yao_filter = (YaoDetailModel.is_world == True)
        elif source_entity == 'response_yao':
            yao_filter = (YaoDetailModel.is_response == True)
        elif source_entity.startswith(('first', 'second', 'third', 'fourth', 'fifth', 'sixth')):
            position_map = {
                'first': 1, 'second': 2, 'third': 3,
                'fourth': 4, 'fifth': 5, 'sixth': 6
            }
            pos = position_map.get(source_entity.replace('_yao', ''))
            if pos:
                yao_filter = (YaoDetailModel.position == pos)

        if yao_filter is None:
            return conditions

        # 构建关系查询
        if relation_type == 'he':
            # 爻地支与日支相合
            case_conditions = []
            for dizhi, he_dizhi in he_map.items():
                case_conditions.append(
                    f"(y.dizhi = '{dizhi}' AND g.ganzhi_day LIKE '%{he_dizhi}')"
                )
            if case_conditions:
                subq = text(f"""
                    SELECT DISTINCT g.id FROM guali g
                    JOIN yao_detail y ON g.id = y.guali_id
                    WHERE y.is_world = {source_entity == 'world_yao'}
                       OR y.is_response = {source_entity == 'response_yao'}
                       AND ({' OR '.join(case_conditions)})
                """)
                conditions.append(GualiModel.id.in_(subq))

        elif relation_type == 'chong':
            # 爻地支与日支相冲
            case_conditions = []
            for dizhi, chong_dizhi in chong_map.items():
                case_conditions.append(
                    f"(y.dizhi = '{dizhi}' AND g.ganzhi_day LIKE '%{chong_dizhi}')"
                )
            if case_conditions:
                subq = text(f"""
                    SELECT DISTINCT g.id FROM guali g
                    JOIN yao_detail y ON g.id = y.guali_id
                    WHERE y.is_world = {source_entity == 'world_yao'}
                       OR y.is_response = {source_entity == 'response_yao'}
                       AND ({' OR '.join(case_conditions)})
                """)
                conditions.append(GualiModel.id.in_(subq))

    return conditions


def build_with_condition(source_field: str, relation_type: str, target_field: str, session: Session):
    """构建WITH条件（存在性判断）"""
    conditions = []

    # WITH运算符：判断是否存在某爻与目标字段有指定关系
    # 例如：dizhi WITH day_dizhi = chong（存在爻与日支相冲）

    if source_field == 'dizhi' and target_field == 'day_dizhi':
        if relation_type == 'chong':
            # 存在爻地支与日支相冲
            # 需要JOIN查询
            subq = text("""
                SELECT DISTINCT g.id FROM guali g
                JOIN yao_detail y ON g.id = y.guali_id
                WHERE (
                    (y.dizhi = '子' AND g.ganzhi_day LIKE '%午') OR
                    (y.dizhi = '午' AND g.ganzhi_day LIKE '%子') OR
                    (y.dizhi = '丑' AND g.ganzhi_day LIKE '%未') OR
                    (y.dizhi = '未' AND g.ganzhi_day LIKE '%丑') OR
                    (y.dizhi = '寅' AND g.ganzhi_day LIKE '%申') OR
                    (y.dizhi = '申' AND g.ganzhi_day LIKE '%寅') OR
                    (y.dizhi = '卯' AND g.ganzhi_day LIKE '%酉') OR
                    (y.dizhi = '酉' AND g.ganzhi_day LIKE '%卯') OR
                    (y.dizhi = '辰' AND g.ganzhi_day LIKE '%戌') OR
                    (y.dizhi = '戌' AND g.ganzhi_day LIKE '%辰') OR
                    (y.dizhi = '巳' AND g.ganzhi_day LIKE '%亥') OR
                    (y.dizhi = '亥' AND g.ganzhi_day LIKE '%巳')
                )
            """)
            conditions.append(GualiModel.id.in_(subq))

        elif relation_type == 'he':
            # 存在爻地支与日支相合
            subq = text("""
                SELECT DISTINCT g.id FROM guali g
                JOIN yao_detail y ON g.id = y.guali_id
                WHERE (
                    (y.dizhi = '子' AND g.ganzhi_day LIKE '%丑') OR
                    (y.dizhi = '丑' AND g.ganzhi_day LIKE '%子') OR
                    (y.dizhi = '寅' AND g.ganzhi_day LIKE '%亥') OR
                    (y.dizhi = '亥' AND g.ganzhi_day LIKE '%寅') OR
                    (y.dizhi = '卯' AND g.ganzhi_day LIKE '%戌') OR
                    (y.dizhi = '戌' AND g.ganzhi_day LIKE '%卯') OR
                    (y.dizhi = '辰' AND g.ganzhi_day LIKE '%酉') OR
                    (y.dizhi = '酉' AND g.ganzhi_day LIKE '%辰') OR
                    (y.dizhi = '巳' AND g.ganzhi_day LIKE '%申') OR
                    (y.dizhi = '申' AND g.ganzhi_day LIKE '%巳') OR
                    (y.dizhi = '午' AND g.ganzhi_day LIKE '%未') OR
                    (y.dizhi = '未' AND g.ganzhi_day LIKE '%午')
                )
            """)
            conditions.append(GualiModel.id.in_(subq))

    return conditions


def build_shensha_condition(condition: SearchCondition, session: Session):
    """
    构建神煞条件查询

    神煞查询逻辑：
    1. 根据日干/日支计算神煞地支
    2. 如果是"是神煞"，只匹配神煞地支本身
    3. 如果是"带神煞"，匹配神煞地支及其相合、相冲的地支

    Args:
        condition: 检索条件
        session: 数据库会话

    Returns:
        SQLAlchemy条件列表
    """
    from backend.core.shensha import (
        get_ganlu, get_yima, get_yangren, get_taohua,
        get_shensha_with_chonghe
    )
    from backend.core.enums import Tiangan, Dizhi

    field = condition.field
    value = condition.value  # 'is' 或 'dai'

    conditions = []

    # 神煞类型到获取函数和基表的映射
    shensha_map = {
        'ganlu': {
            'get_func': get_ganlu,
            'base_type': 'tiangan',  # 基于日干
            'tiangan_index': 0,      # ganzhi_day的第一个字符
        },
        'yima': {
            'get_func': get_yima,
            'base_type': 'dizhi',    # 基于日支
            'dizhi_index': 1,        # ganzhi_day的第二个字符
        },
        'yangren': {
            'get_func': get_yangren,
            'base_type': 'tiangan',
            'tiangan_index': 0,
        },
        'taohua': {
            'get_func': get_taohua,
            'base_type': 'dizhi',
            'dizhi_index': 1,
        },
    }

    if field not in shensha_map:
        return conditions

    shensha_info = shensha_map[field]
    get_func = shensha_info['get_func']

    # 构建SQL子查询
    # 需要根据日干日支动态计算神煞地支，然后匹配爻地支

    # 获取天干地支列表
    tiangan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    dizhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 构建每个日干/日支对应的查询条件
    case_conditions = []

    if shensha_info['base_type'] == 'tiangan':
        # 基于日干的神煞（干禄、羊刃）
        for i, tg_char in enumerate(tiangan_list):
            tiangan = Tiangan.from_char(tg_char)
            if tiangan:
                try:
                    shensha_dizhi = get_func(tiangan)
                    if value == 'is':
                        # 只匹配神煞地支本身
                        target_dizhis = [shensha_dizhi.value]
                    else:  # 'dai'
                        # 匹配神煞地支及其相合、相冲的地支
                        target_dizhis = [d.value for d in get_shensha_with_chonghe(shensha_dizhi)]

                    # 构建条件：日干为tg_char，且存在爻地支在target_dizhis中
                    dizhi_conditions = " OR ".join([f"y.dizhi = '{dz}'" for dz in target_dizhis])
                    case_conditions.append(
                        f"(g.ganzhi_day LIKE '{tg_char}%' AND ({dizhi_conditions}))"
                    )
                except Exception:
                    continue
    else:
        # 基于日支的神煞（驿马、桃花）
        for dz_char in dizhi_list:
            dizhi = Dizhi.from_char(dz_char)
            if dizhi:
                try:
                    shensha_dizhi = get_func(dizhi)
                    if value == 'is':
                        target_dizhis = [shensha_dizhi.value]
                    else:  # 'dai'
                        target_dizhis = [d.value for d in get_shensha_with_chonghe(shensha_dizhi)]

                    dizhi_conditions = " OR ".join([f"y.dizhi = '{dz}'" for dz in target_dizhis])
                    case_conditions.append(
                        f"(g.ganzhi_day LIKE '%{dz_char}' AND ({dizhi_conditions}))"
                    )
                except Exception:
                    continue

    if case_conditions:
        # 构建完整子查询
        subq = text(f"""
            SELECT DISTINCT g.id FROM guali g
            JOIN yao_detail y ON g.id = y.guali_id
            WHERE {' OR '.join(case_conditions)}
        """)
        conditions.append(GualiModel.id.in_(subq))

    return conditions


def build_special_condition(condition: SearchCondition, session: Session):
    """
    构建特殊条件查询（伏神飞神、反吟伏吟）

    Args:
        condition: 检索条件
        session: 数据库会话

    Returns:
        SQLAlchemy条件列表
    """
    from backend.core.fanyin_fuyin import (
        is_zhonggua_yimao_fanyin, is_zhonggua_fuyin,
        YIMAO_FANYIN_MAP, FUYIN_MAP
    )
    from backend.core.enums import DanGua, ZhongGua

    field = condition.field
    value = condition.value

    conditions = []

    if field == 'fushen_feishen':
        # 伏神飞神查询
        # 有伏神的卦例：六亲不全的卦例
        # 这需要检查爻详情中是否有缺失的六亲

        if value == 'has_fushen':
            # 查找有伏神的卦例（六亲不全）
            # 通过子查询找到只包含少于5种六亲的卦例
            subq = text("""
                SELECT g.id FROM guali g
                WHERE (
                    SELECT COUNT(DISTINCT y.liuqin) FROM yao_detail y
                    WHERE y.guali_id = g.id AND y.liuqin IS NOT NULL
                ) < 5
            """)
            conditions.append(GualiModel.id.in_(subq))

        elif value in ['fu_ke_fei', 'fei_ke_fu', 'fu_sheng_fei', 'fei_sheng_fu']:
            # 飞神伏神的关系查询
            # 这需要更复杂的计算，暂时返回空
            # TODO: 实现飞神伏神关系的动态计算
            pass

    elif field == 'fanyin_fuyin':
        # 反吟伏吟查询
        if value == 'yimao_fanyin':
            # 易冒反吟：乾巽互变、坎离互变、艮坤互变、震兑互变
            # 本卦和之卦的内卦或外卦符合上述关系
            # 获取符合易冒反吟条件的卦代码对
            fanyin_pairs = []
            for gua in ZhongGua:
                try:
                    neigua = gua.neigua
                    waigua = gua.waigua
                    # 检查内卦或外卦是否符合反吟关系
                    if neigua in YIMAO_FANYIN_MAP or waigua in YIMAO_FANYIN_MAP:
                        fanyin_pairs.append(gua.code)
                except Exception:
                    continue

            if fanyin_pairs:
                # 找出有动爻且本卦与之卦形成反吟关系的卦例
                subq = text(f"""
                    SELECT g.id FROM guali g
                    WHERE g.zhi_gua_code IS NOT NULL
                    AND g.yao_bian_code != 0
                    AND (
                        -- 内卦反吟
                        ((
                            (g.ben_gua_code & 7) IN (
                                SELECT code FROM (
                                    SELECT 0 as code UNION SELECT 1 UNION SELECT 2 UNION
                                    SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
                                ) AS codes
                            )
                            AND (g.zhi_gua_code & 7) IN (
                                SELECT code FROM (
                                    SELECT 0 as code UNION SELECT 1 UNION SELECT 2 UNION
                                    SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
                                ) AS codes
                            )
                        ))
                        OR
                        -- 外卦反吟
                        ((
                            ((g.ben_gua_code >> 3) & 7) IN (
                                SELECT code FROM (
                                    SELECT 0 as code UNION SELECT 1 UNION SELECT 2 UNION
                                    SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
                                ) AS codes
                            )
                            AND ((g.zhi_gua_code >> 3) & 7) IN (
                                SELECT code FROM (
                                    SELECT 0 as code UNION SELECT 1 UNION SELECT 2 UNION
                                    SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
                                ) AS codes
                            )
                        ))
                    )
                """)
                conditions.append(GualiModel.id.in_(subq))

        elif value == 'yaobian_fanyin':
            # 爻变反吟：坤巽互变
            subq = text("""
                SELECT g.id FROM guali g
                WHERE g.zhi_gua_code IS NOT NULL
                AND g.yao_bian_code != 0
                AND (
                    ((g.ben_gua_code & 7) = 0 AND (g.zhi_gua_code & 7) = 3)
                    OR ((g.ben_gua_code & 7) = 3 AND (g.zhi_gua_code & 7) = 0)
                    OR (((g.ben_gua_code >> 3) & 7) = 0 AND ((g.zhi_gua_code >> 3) & 7) = 3)
                    OR (((g.ben_gua_code >> 3) & 7) = 3 AND ((g.zhi_gua_code >> 3) & 7) = 0)
                )
            """)
            conditions.append(GualiModel.id.in_(subq))

        elif value == 'fuyin':
            # 伏吟：乾震互变
            subq = text("""
                SELECT g.id FROM guali g
                WHERE g.zhi_gua_code IS NOT NULL
                AND g.yao_bian_code != 0
                AND (
                    ((g.ben_gua_code & 7) = 7 AND (g.zhi_gua_code & 7) = 4)
                    OR ((g.ben_gua_code & 7) = 4 AND (g.zhi_gua_code & 7) = 7)
                    OR (((g.ben_gua_code >> 3) & 7) = 7 AND ((g.zhi_gua_code >> 3) & 7) = 4)
                    OR (((g.ben_gua_code >> 3) & 7) = 4 AND ((g.zhi_gua_code >> 3) & 7) = 7)
                )
            """)
            conditions.append(GualiModel.id.in_(subq))

    return conditions


# =============================================================================
# API接口
# =============================================================================

@router.post("", response_model=SearchResponse)
async def search_guali(
    request: SearchRequest,
    session: Session = Depends(get_session)
):
    """
    复杂检索接口

    支持多种条件组合：
    - 时间类条件
    - 卦类条件
    - 爻类条件
    - 关系类条件
    - 神煞类条件
    - 复合字段条件
    """
    try:
        all_conditions = []

        for cond in request.conditions:
            field = cond.field

            # 判断条件类型
            if '.' in field:
                # 复合字段
                all_conditions.extend(build_compound_condition(cond, session))
            elif field in ['solar_year', 'ganzhi_year', 'ganzhi_month', 'ganzhi_day',
                          'day_tiangan', 'day_dizhi', 'xunkong', 'ben_gua_name',
                          'zhi_gua_name', 'gongwei', 'gongwei_index', 'special_type',
                          'zhan_wen', 'zhan_duan', 'yanqing_status']:
                # 简单条件
                all_conditions.extend(build_simple_condition(cond, session))
            elif field in ['liuqin', 'liushen', 'dizhi', 'yao_type', 'yao_state', 'shi_ying']:
                # 爻类条件
                yao_conds = build_yao_condition(cond, session)
                if yao_conds:
                    subq = session.query(YaoDetailModel.guali_id).filter(*yao_conds)
                    all_conditions.append(GualiModel.id.in_(subq))
            elif field in ['ganlu', 'yima', 'yangren', 'taohua']:
                # 神煞条件
                all_conditions.extend(build_shensha_condition(cond, session))
            elif field in ['fushen_feishen', 'fanyin_fuyin']:
                # 伏神飞神、反吟伏吟条件
                all_conditions.extend(build_special_condition(cond, session))

        # 构建最终查询
        if all_conditions:
            # 按逻辑组合条件
            logic = request.logic or 'and'
            if logic == 'and':
                query = session.query(GualiModel).filter(and_(*all_conditions))
            else:
                query = session.query(GualiModel).filter(or_(*all_conditions))
        else:
            query = session.query(GualiModel)

        # 计算总数
        total = query.count()

        # 分页
        page = request.page or 1
        page_size = request.page_size or 20
        offset = (page - 1) * page_size

        items = query.order_by(GualiModel.id.desc()).offset(offset).limit(page_size).all()

        return SearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[GualiResponse.model_validate(item) for item in items]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/fields")
async def get_search_fields():
    """获取可检索字段列表"""
    return {
        "time_fields": [
            {"key": "solar_year", "label": "公历年", "type": "number"},
            {"key": "ganzhi_year", "label": "年柱", "type": "select"},
            {"key": "ganzhi_month", "label": "月柱", "type": "select"},
            {"key": "ganzhi_day", "label": "日柱", "type": "select"},
            {"key": "day_tiangan", "label": "日干", "type": "select"},
            {"key": "day_dizhi", "label": "日支", "type": "select"},
            {"key": "xunkong", "label": "旬空", "type": "select"}
        ],
        "gua_fields": [
            {"key": "ben_gua_name", "label": "本卦名", "type": "input"},
            {"key": "zhi_gua_name", "label": "之卦名", "type": "input"},
            {"key": "gongwei", "label": "卦宫", "type": "select"},
            {"key": "gongwei_index", "label": "宫位", "type": "select"},
            {"key": "special_type", "label": "特殊类型", "type": "select"}
        ],
        "yao_fields": [
            {"key": "liuqin", "label": "六亲", "type": "select"},
            {"key": "liushen", "label": "六神", "type": "select"},
            {"key": "dizhi", "label": "地支", "type": "select"}
        ],
        "other_fields": [
            {"key": "zhan_wen", "label": "占问事由", "type": "input"},
            {"key": "zhan_duan", "label": "占断", "type": "input"},
            {"key": "yanqing_status", "label": "占验情况", "type": "select", "options": ["应验", "模糊", "不验"]}
        ]
    }
