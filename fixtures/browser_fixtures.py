import pytest


@pytest.fixture(autouse=True)
def set_playwright_timeout(context, timeout_config):
    """
    统一设置 Playwright 超时时间
    """
    default_timeout = timeout_config.get("default", 10000)
    navigation_timeout = timeout_config.get("navigation", 30000)

    context.set_default_timeout(default_timeout)
    context.set_default_navigation_timeout(navigation_timeout)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, get_context_config, auth_state_file):
    """
    修改 playwright 默认浏览器上下文配置，并注入登录态。
    """

    viewport = get_context_config.get("viewport")
    ignore_https_errors = get_context_config.get("ignore_https_errors")
    return {
        **browser_context_args,
        "viewport": {
            "width": viewport.get("width"),
            "height": viewport.get("height"),
        },
        "ignore_https_errors": ignore_https_errors,
        "storage_state": auth_state_file,
    }