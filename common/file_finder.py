from pathlib import Path


def find_latest_file(root_dir: str, suffix: str):
    """
    在指定目录下查找最新生成的指定后缀文件
    """
    root_path = Path(root_dir)

    if not root_path.exists():
        return None

    files = list(root_path.rglob(f"*{suffix}"))

    if not files:
        return None

    return max(files, key=lambda file: file.stat().st_mtime)