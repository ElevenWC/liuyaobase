"""
数据库初始化脚本

运行此脚本创建所有数据库表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.connection import init_db, test_connection, Base


def main():
    """初始化数据库"""
    print("=" * 50)
    print("六爻卦例分析系统 - 数据库初始化")
    print("=" * 50)

    # 测试连接
    print("\n[1/2] 测试数据库连接...")
    if test_connection():
        print("[OK] 数据库连接成功")
    else:
        print("[FAIL] 数据库连接失败，请检查配置")
        return

    # 创建表
    print("\n[2/2] 创建数据库表...")
    try:
        init_db()
        print("[OK] 数据库表创建成功")
    except Exception as e:
        print(f"[FAIL] 数据库表创建失败: {e}")
        return

    print("\n" + "=" * 50)
    print("数据库初始化完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
