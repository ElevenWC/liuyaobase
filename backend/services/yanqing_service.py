# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 占验情况服务

占验情况用于记录卦例的实际应验结果，与主数据库弱耦合，独立存储。

占验状态:
- 应验: 占断与实际结果一致
- 模糊: 无法确定或部分应验
- 不验: 占断与实际结果不一致
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import threading

from backend.config import settings


class YanqingService:
    """
    占验情况服务类

    使用JSON文件存储占验情况数据，与主数据库弱耦合。
    支持标注、查询、批量导入/导出功能。
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化占验情况服务

        Args:
            storage_path: 存储文件路径，默认使用配置中的数据目录
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(settings.base_dir) / "data" / "yanqing.json"

        # 确保目录存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用线程锁保证并发安全
        self._lock = threading.Lock()

        # 内存缓存
        self._cache: Dict[int, Dict] = {}
        self._loaded = False

    def _load_data(self) -> Dict[int, Dict]:
        """
        加载占验情况数据

        Returns:
            占验情况字典，key为卦例ID
        """
        if self._loaded:
            return self._cache

        with self._lock:
            if self.storage_path.exists():
                try:
                    with open(self.storage_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 转换key为整数
                        self._cache = {int(k): v for k, v in data.items()}
                except (json.JSONDecodeError, IOError):
                    self._cache = {}
            else:
                self._cache = {}

            self._loaded = True
            return self._cache

    def _save_data(self) -> None:
        """
        保存占验情况数据到文件
        """
        with self._lock:
            # 创建备份
            if self.storage_path.exists():
                backup_path = self.storage_path.with_suffix('.json.bak')
                try:
                    import shutil
                    shutil.copy2(self.storage_path, backup_path)
                except IOError:
                    pass  # 备份失败不影响保存

            # 保存数据
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def annotate(
        self,
        guali_id: int,
        status: str,
        note: Optional[str] = None
    ) -> Dict:
        """
        标注占验情况

        Args:
            guali_id: 卦例ID
            status: 占验状态（应验、模糊、不验）
            note: 备注说明

        Returns:
            标注后的占验情况数据

        Raises:
            ValueError: 状态值无效
        """
        # 验证状态值
        valid_statuses = ['应验', '模糊', '不验']
        if status not in valid_statuses:
            raise ValueError(f"无效的占验状态: {status}，有效值: {valid_statuses}")

        self._load_data()

        now = datetime.now().isoformat()

        # 检查是否已存在标注
        existing = self._cache.get(guali_id)

        yanqing_data = {
            'guali_id': guali_id,
            'status': status,
            'note': note or '',
            'created_at': existing.get('created_at', now) if existing else now,
            'updated_at': now
        }

        self._cache[guali_id] = yanqing_data
        self._save_data()

        return yanqing_data

    def get_by_guali_id(self, guali_id: int) -> Optional[Dict]:
        """
        获取指定卦例的占验情况

        Args:
            guali_id: 卦例ID

        Returns:
            占验情况数据，不存在则返回None
        """
        self._load_data()
        return self._cache.get(guali_id)

    def get_by_ids(self, guali_ids: List[int]) -> Dict[int, Dict]:
        """
        批量获取多个卦例的占验情况

        Args:
            guali_ids: 卦例ID列表

        Returns:
            占验情况字典，key为卦例ID
        """
        self._load_data()
        return {gid: self._cache[gid] for gid in guali_ids if gid in self._cache}

    def get_all(self) -> Dict[int, Dict]:
        """
        获取所有占验情况

        Returns:
            所有占验情况字典
        """
        self._load_data()
        return self._cache.copy()

    def get_by_status(self, status: str) -> List[Dict]:
        """
        按状态获取占验情况列表

        Args:
            status: 占验状态

        Returns:
            匹配的占验情况列表
        """
        self._load_data()
        return [data for data in self._cache.values() if data.get('status') == status]

    def delete(self, guali_id: int) -> bool:
        """
        删除占验情况标注

        Args:
            guali_id: 卦例ID

        Returns:
            是否成功删除
        """
        self._load_data()

        if guali_id in self._cache:
            del self._cache[guali_id]
            self._save_data()
            return True

        return False

    def export_data(self) -> str:
        """
        导出所有占验情况数据为JSON字符串

        Returns:
            JSON格式的占验情况数据
        """
        self._load_data()
        return json.dumps(self._cache, ensure_ascii=False, indent=2)

    def import_data(self, json_data: str, merge: bool = True) -> int:
        """
        从JSON字符串导入占验情况数据

        Args:
            json_data: JSON格式的占验情况数据
            merge: 是否合并现有数据（True=合并，False=覆盖）

        Returns:
            导入的记录数

        Raises:
            ValueError: JSON格式无效
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式: {e}")

        self._load_data()

        # 转换key为整数
        new_data = {int(k): v for k, v in data.items()}

        if merge:
            # 合并数据，新数据覆盖旧数据
            self._cache.update(new_data)
        else:
            # 覆盖现有数据
            self._cache = new_data

        self._save_data()

        return len(new_data)

    def get_statistics(self) -> Dict[str, int]:
        """
        获取占验情况统计信息

        Returns:
            统计信息字典
        """
        self._load_data()

        stats = {
            'total': len(self._cache),
            '应验': 0,
            '模糊': 0,
            '不验': 0
        }

        for data in self._cache.values():
            status = data.get('status')
            if status in stats:
                stats[status] += 1

        return stats

    def clear_cache(self) -> None:
        """
        清除内存缓存，下次操作将重新从文件加载
        """
        with self._lock:
            self._cache = {}
            self._loaded = False


# 全局单例
_yanqing_service: Optional[YanqingService] = None


def get_yanqing_service() -> YanqingService:
    """
    获取占验情况服务单例

    Returns:
        YanqingService实例
    """
    global _yanqing_service
    if _yanqing_service is None:
        _yanqing_service = YanqingService()
    return _yanqing_service
