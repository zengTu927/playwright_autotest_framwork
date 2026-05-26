from datetime import datetime
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page, BrowserContext

from common.logger import logger, LOG_FILE
from common.file_utils import safe_file_name, ensure_dir


@pytest.fixture(autouse=True)
def failure_artifacts(request, page: Page, context: BrowserContext):
    """
    用例执行失败时，把截图、trace、日志附加到 Allure
    """

    case_name = safe_file_name(request.node.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    screenshot_dir = ensure_dir("reports/screenshots")
    trace_dir = ensure_dir("reports/traces")

    screenshot_path = screenshot_dir / f"执行失败截图_{case_name}_{timestamp}.png"
    trace_path = trace_dir / f"执行失败trace_{case_name}_{timestamp}_trace.zip"

    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )

    yield

    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    if failed:
        logger.info(f"用例执行失败，开始收集失败信息：{case_name}")

        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name=f"{case_name}_{timestamp}_失败截图",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.error(f"用例执行失败，已添加失败截图：{screenshot_path}")
        except Exception as e:
            logger.error(f"用例执行失败，添加失败截图失败：{e}")

        try:
            context.tracing.stop(path=str(trace_path))
            allure.attach.file(
                str(trace_path),
                name=f"{case_name}_{timestamp}_失败trace",
                attachment_type="application/zip",
                extension="zip",
            )
            logger.error(f"用例执行失败，已添加失败 trace：{trace_path}")
        except Exception as e:
            logger.error(f"用例执行失败，添加失败 trace 失败：{e}")

        try:
            if Path(LOG_FILE).exists():
                allure.attach.file(
                    LOG_FILE,
                    name=f"{case_name}_{timestamp}_失败日志",
                    attachment_type=allure.attachment_type.TEXT,
                )
                logger.error(f"用例执行失败，已添加失败日志：{LOG_FILE}")
        except Exception as e:
            logger.error(f"用例执行失败，添加失败日志失败：{e}")

    else:
        try:
            context.tracing.stop()
        except Exception as e:
            logger.error(f"用例执行成功，停止 trace 失败：{e}")