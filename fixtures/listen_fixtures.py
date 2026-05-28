import pytest

from common.logger import logger

from playwright.sync_api import Page,BrowserContext

@pytest.fixture(autouse=True)
def listen_page_events(page:Page):
    def handle_console(msg):
        if msg.type == "error":
            logger.error(f"[console error] {msg.text}")

    def handle_page_error(error):
        logger.error(f"[page error] {error}")

    def handle_request_failed(request):
        logger.error(f"[request failed] {request.method} {request.url} {request.failure}")

    page.on("console", handle_console)
    page.on("pageerror", handle_page_error)
    page.on("requestfailed", handle_request_failed)

    yield

    page.remove_listener("console", handle_console)
    page.remove_listener("pageerror", handle_page_error)
    page.remove_listener("requestfailed", handle_request_failed)

@pytest.fixture(autouse=True)
def listen_context_events(context:BrowserContext):
    def handle_console(msg):
        if msg.type == "error":
            logger.error(f"[console error] {msg.text}")

    def handle_request_failed(request):
        logger.error(f"[request failed] {request.method} {request.url} {request.failure}")

    context.on("console", handle_console)
    context.on("requestfailed", handle_request_failed)

    yield

    context.remove_listener("console", handle_console)
    context.remove_listener("requestfailed", handle_request_failed)


