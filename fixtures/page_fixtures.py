import pytest
from playwright.sync_api import Browser,Page

from pages.login_page import LoginPage


@pytest.fixture()
def no_auth_context(browser: Browser, browser_context_args):
    """
    不带登录态的 context。
    专门用于登录、注册、忘记密码等用例。
    """
    args = browser_context_args.copy()
    args.pop("storage_state", None)

    context = browser.new_context(**args)
    yield context
    context.close()


@pytest.fixture()
def no_auth_page(no_auth_context):
    """
    不带登录态的 page。
    """
    page = no_auth_context.new_page()
    yield page
    page.close()


@pytest.fixture()
def login_page(page:Page,timeout_config):
    """
    返回页面对象，为什么scope为function，第一page fixture是function级别的夹具，
    一个大的作用域依赖小的作用域会导致在执行session级别的夹具时，function级别的夹具还没有准备好，
    调用也没有意义，第二playwright本来是就一条case一个page，如果是session级别的夹具会导致所有的case都使用同一个page对象，造成环境的污染
    """
    return LoginPage(page,timeout_config["expect"])