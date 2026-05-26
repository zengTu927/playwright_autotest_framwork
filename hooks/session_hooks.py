from pathlib import Path

from common.file_utils import clean_directory
from common.logger import logger


def pytest_sessionstart(session):
    """
    session 开始时清理报告目录。
    注意：不要在这里清理 reports/logs。
    logs 应该在 pytest 启动前由 Jenkins 或 bash 清理。
    """

    if hasattr(session.config, "workerinput"):
        return

    clean_directory("reports/allure-results")
    clean_directory("reports/screenshots")
    clean_directory("reports/traces")
    clean_directory("reports/videos")
    clean_directory("reports/playwright-output")

    logger.info("清理报告目录成功")

    state_path = Path("playwright/.auth/state.json")
    lock_path = Path("playwright/.auth/state.lock")

    if state_path.exists():
        state_path.unlink()
        logger.info(f"已删除旧登录态文件：{state_path}")

    if lock_path.exists():
        lock_path.unlink()
        logger.info(f"已删除旧登录态锁文件：{lock_path}")