from pathlib import Path
from typing import Any

import yaml


class ReadYaml:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"配置文件不存在：{self.file_path}")
        self._cache = None  # 添加缓存

    def read(self) -> dict[str, Any]:
        if self._cache is None:  # 只在首次读取
            with self.file_path.open("r", encoding="utf-8") as file:
                self._cache = yaml.safe_load(file) or {}
        return self._cache

    def get(self, key: str, default: Any = None) -> Any:
        data = self.read()
        # 支持嵌套key如 "database.host"
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def reload(self):
        """强制重新加载配置文件"""
        self._cache = None
        return self.read()


