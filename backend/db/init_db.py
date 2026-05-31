"""数据库初始化——建表 + 填充基础数据 + 注册存储函数

🔴 核心文件：整个系统的数据基础
🟡 需仔细审核：18 张表需逐表核对
"""
import json
import os
from pathlib import Path
from sqlalchemy import Engine
from sqlmodel import Session
from backend.db.connection import engine

SQL_FILE = Path(__file__).resolve().parent / "create_tables.sql"
STORED_FUNCTIONS_DIR = Path(__file__).resolve().parent / "stored_functions"
ZHOuyi_DATA = Path(__file__).resolve().parent.parent.parent / ".user" / "zhouyiData.json"


def init_database():
    """主入口——建表 + 填充基础数据 + 注册存储函数

    安全开关：需设置环境变量 LIUYAO_ALLOW_DB_INIT=true 才执行。
    防止误删已导入的真实卦例数据。
    """
    if os.environ.get("LIUYAO_ALLOW_DB_INIT", "").lower() != "true":
        print("未设置 LIUYAO_ALLOW_DB_INIT=true，跳过数据库初始化。")
        print("如需初始化，请执行: $env:LIUYAO_ALLOW_DB_INIT='true' (PowerShell)")
        return

    create_tables(engine)
    with Session(engine) as session:
        seed_basic_data(session)
        seed_static_data(session)
    register_stored_functions(engine)
    print("数据库初始化完成")


def create_tables(engine: Engine):
    """执行建表 SQL（18 张表 + 36 个索引），按依赖顺序 DROP 再 CREATE。"""
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"建表 SQL 文件不存在: {SQL_FILE}")

    sql = SQL_FILE.read_text(encoding="utf-8")
    _execute_sql_script(engine, sql)
    print("建表 + 索引完成（18 张表 + 36 个索引）")


def seed_basic_data(session: Session):
    """填充 bagong_gua(64) + guaci(64) + system_config(1)

    数据来源：.user/zhouyiData.json
    """
    from backend.models.bagong_gua import BagongGua
    from backend.models.guaci import Guaci
    from backend.models.system_config import SystemConfig

    if not ZHOuyi_DATA.exists():
        raise FileNotFoundError(f"周易数据文件不存在: {ZHOuyi_DATA}")

    data = json.loads(ZHOuyi_DATA.read_text(encoding="utf-8"))
    basic = data["basic"]    # {卦名: {code, palace, element, palaceType}}
    content = data["content"]  # {卦名: {guaci, tuanZhuan, xiangZhuan, yao, wenyan, yongJiu}}

    # bagong_gua（64 条）
    for name, info in basic.items():
        session.add(BagongGua(
            code=info["code"],
            name=name,
            palace=info["palace"],
            element=info["element"],
            palace_type=info["palaceType"],
        ))

    # guaci（64 条），code 取自 basic 同名字段
    for name, info in content.items():
        session.add(Guaci(
            code=basic[name]["code"],
            gua_ci=info.get("guaci"),
            tuan_zhuan=info.get("tuanZhuan"),
            xiang_zhuan=info.get("xiangZhuan"),
            yao_ci=json.dumps(info["yao"], ensure_ascii=False) if info.get("yao") else None,
            wenyan=info.get("wenyan"),
            yong=json.dumps(info["yongJiu"], ensure_ascii=False) if info.get("yongJiu") else None,
        ))

    # system_config（1 条，初始值为空）
    session.add(SystemConfig(config_key="last_import_time", config_value=""))

    # 系统标签——占验情况组（不可删除）
    from backend.models.tag import Tag
    sys_tags = {"占验情况": None, "应验": "占验情况", "模糊": "占验情况", "不验": "占验情况", "未验": "占验情况"}
    tag_map: dict[str, Tag] = {}
    for name, parent_name in sys_tags.items():
        parent_id = tag_map[parent_name].id if parent_name else None
        t = Tag(name=name, parent_id=parent_id, is_system=True)
        session.add(t)
        session.flush()
        tag_map[name] = t

    # 系统标签——时间周期组
    cycle_tags = {"时间周期": None, "时级": "时间周期", "日级": "时间周期", "周级": "时间周期", "旬级": "时间周期", "月级": "时间周期", "年级": "时间周期"}
    tag_map2: dict[str, Tag] = {}
    for name, parent_name in cycle_tags.items():
        parent_id = tag_map2[parent_name].id if parent_name else None
        t = Tag(name=name, parent_id=parent_id, is_system=True)
        session.add(t)
        session.flush()
        tag_map2[name] = t

    session.commit()
    print("基础数据填充完成（bagong_gua 64 + guaci 64 + system_config 1 + 系统标签 11）")


def register_stored_functions(engine: Engine):
    """注册 MySQL 存储函数（从 stored_functions/*.sql 读取并执行）

    v0.0 阶段 stored_functions/ 可能尚未创建（等待 Issue #7），
    此函数会静默跳过而不会报错。
    """
    if not STORED_FUNCTIONS_DIR.exists():
        print("stored_functions/ 目录不存在，跳过存储函数注册（等待 Issue #7）")
        return

    sql_files = sorted(STORED_FUNCTIONS_DIR.glob("*.sql"))
    if not sql_files:
        print("stored_functions/ 目录为空，跳过存储函数注册")
        return

    for sql_file in sql_files:
        sql = sql_file.read_text(encoding="utf-8")
        _execute_sql_script(engine, sql, use_multi=True)

    print(f"存储函数注册完成（{len(sql_files)} 个）")


def seed_static_data(session: Session):
    """填充 static_* 三表数据（~832 条）

    调用 v0.1 核心算法生成：
    - static_gua_yao_info（64卦 × 6爻 = 384 条）
    - static_fushen_zengshan（~64 条）
    - static_fushen_yimao（64卦 × 6爻 = 384 条）
    """
    from backend.models.static_gua_yao_info import StaticGuaYaoInfo
    from backend.models.static_fushen_zengshan import StaticFushenZengshan
    from backend.models.static_fushen_yimao import StaticFushenYimao
    from backend.core.najia import get_yao_info
    from backend.core.liuqin import calc_liuqin
    from backend.core.fushen_zengshan import get_fushen as get_fushen_zs
    from backend.core.fushen_yimao import get_all_fushen as get_all_fushen_ym
    from backend.core.enums import CODE_TO_NAME, CODE_TO_ELEMENT

    codes = list(CODE_TO_NAME.keys())

    for code in codes:
        gua_element = CODE_TO_ELEMENT[code]

        # ① 纳甲装卦：每爻的地支 + 天干（含夏/冬两套）+ 六亲
        for yao in get_yao_info(code):
            session.add(StaticGuaYaoInfo(
                code=code,
                yao_index=yao["yao_index"],
                dizhi=yao["dizhi"],
                tiangan=yao.get("tiangan"),
                tiangan_summer=yao.get("tiangan_summer"),
                tiangan_winter=yao.get("tiangan_winter"),
                liuqin=calc_liuqin(gua_element, yao["dizhi"]),
            ))

        # ② 增删伏神（0~2 条/卦）
        for f in get_fushen_zs(code):
            session.add(StaticFushenZengshan(
                code=code,
                yao_index=f["yao_index"],
                missing_liuqin=f["missing_liuqin"],
                fushen_dizhi=f["fushen_dizhi"],
                fushen_liuqin=f["fushen_liuqin"],
                feishen_dizhi=f["feishen_dizhi"],
                feishen_liuqin=f["feishen_liuqin"],
            ))

        # ③ 易冒伏神（6 条/卦）
        for f in get_all_fushen_ym(code):
            session.add(StaticFushenYimao(
                code=code,
                yao_index=f["yao_index"],
                fushen_dizhi=f["fushen_dizhi"],
                fushen_liuqin=f["fushen_liuqin"],
            ))

    session.commit()
    count_yao = len(codes) * 6
    count_zs = session.query(StaticFushenZengshan).count()
    print(f"static_* 三表数据填充完成"
          f"（static_gua_yao_info {count_yao} +"
          f" static_fushen_zengshan {count_zs} +"
          f" static_fushen_yimao {count_yao}）")


def _execute_sql_script(engine: Engine, sql: str, use_multi: bool = False):
    """执行 SQL 脚本。

    use_multi=False（建表 SQL）：按 ; 分拆逐条执行。
    use_multi=True（存储函数）：手动拆分 DROP FUNCTION 和 CREATE FUNCTION，
    后者体内含 ; 不能简单分割。

    使用 raw_connection 确保 SET FOREIGN_KEY_CHECKS 等会话语句正确生效。
    """
    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        if use_multi:
            # 存储函数文件：DROP FUNCTION ...; + CREATE FUNCTION ... END;
            idx = sql.index("CREATE FUNCTION")
            drop_stmt = sql[:idx].strip().rstrip(";")
            create_stmt = sql[idx:].strip()
            cursor.execute(drop_stmt)
            cursor.execute(create_stmt)
        else:
            # 建表 SQL：去注释 → 按 ; 分割 → 逐条执行
            clean_lines = [
                line for line in sql.split("\n")
                if line.strip() and not line.strip().startswith("--")
            ]
            clean_sql = "\n".join(clean_lines)
            for statement in clean_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        raw_conn.commit()
    finally:
        cursor.close()
        raw_conn.close()
