"""sync/ 文件夹监控——检测新 .ly 文件 → 自动导入

集成到 FastAPI 启动/关闭事件中，后台线程运行。
"""
import os
import shutil
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from backend.db.connection import engine
from backend.services.import_service import import_from_json
from sqlmodel import Session

logger = logging.getLogger(__name__)

SYNC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sync"
IMPORTED_DIR = SYNC_DIR / "imported"
FAILED_DIR = SYNC_DIR / "failed"


class LyFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if not path.suffix == ".ly":
            return
        # 排除临时文件
        if path.name.endswith(".tmp") or ".sync" in path.name:
            return

        self._process(path)

    def _process(self, path: Path):
        # 等文件稳定（Syncthing 可能边写边传或有临时重命名延迟）
        time.sleep(2)
        if not path.exists():
            return

        logger.info(f"sync: 检测到新文件 {path.name}，开始导入...")
        try:
            with Session(engine) as session:
                result = import_from_json(str(path), session)

            imported = result.get("imported", 0)
            duplicates = result.get("duplicates", 0)
            errors = result.get("errors", [])

            if imported > 0 or (duplicates > 0 and not errors):
                dest = IMPORTED_DIR / path.name
                IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
                # 重名加时间戳
                if dest.exists():
                    dest = IMPORTED_DIR / f"{path.stem}_{int(time.time())}{path.suffix}"
                shutil.move(str(path), str(dest))
                logger.info(f"sync: {path.name} 导入完成——新增 {imported}，跳过重复 {duplicates}")
            else:
                dest = FAILED_DIR / path.name
                FAILED_DIR.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    dest = FAILED_DIR / f"{path.stem}_{int(time.time())}{path.suffix}"
                shutil.move(str(path), str(dest))
                logger.warning(f"sync: {path.name} 导入失败——新增 {imported}，错误: {errors}")

        except Exception as e:
            logger.error(f"sync: {path.name} 处理异常: {e}")
            try:
                dest = FAILED_DIR / path.name
                FAILED_DIR.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    shutil.move(str(path), str(dest))
            except Exception:
                pass


_observer: Observer | None = None


def start_watcher():
    """启动 sync/ 文件夹监控（后台线程）"""
    global _observer
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)

    _observer = Observer()
    _observer.schedule(LyFileHandler(), str(SYNC_DIR), recursive=False)
    _observer.start()
    logger.info(f"sync 文件夹监控已启动: {SYNC_DIR}")


def stop_watcher():
    """停止监控"""
    global _observer
    if _observer:
        _observer.stop()
        _observer.join()
        _observer = None
        logger.info("sync 文件夹监控已停止")
