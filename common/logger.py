
import os
import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """日志封装类"""

    def __init__(self, name: str = "ui_autotest"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if self.logger.handlers:
            return

        log_dir = Path("reports/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
        log_file = log_dir / f"run_{worker_id}_{timestamp}.log"

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.log_file = str(log_file)

    def get_logger(self):
        return self.logger


logger_instance = Logger()
logger = logger_instance.get_logger()
LOG_FILE = logger_instance.log_file