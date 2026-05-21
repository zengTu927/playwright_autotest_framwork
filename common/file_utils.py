import re
import shutil
from pathlib import Path


def safe_file_name(name: str) -> str:
    """
    清洗文件名，避免参数化用例名称中包含特殊字符

    例如：
    test_login[chromium] -> test_login_chromium_
    """
    return re.sub(r"[^\w\u4e00-\u9fa5.-]", "_", name)


def ensure_dir(path: str | Path) -> Path:
    """确保目录存在"""
    target_dir = Path(path)
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def clean_directory(path: str | Path):
    """清空目录，如果目录不存在则创建"""
    target_dir = Path(path)

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        return

    for item in target_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()