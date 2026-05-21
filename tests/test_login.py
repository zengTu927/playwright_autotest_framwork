import re
import pytest

import allure
from playwright.sync_api import Page,expect

from pages.login_page import LoginPage

@allure.epic("playwright framework")
@allure.feature("登录模块")
@allure.story("首页登录")
@allure.title("登录成功")
@pytest.mark.smoke
def test_login(login_page,env_config):
    login_page.open_login_page(env_config["base_url"])
    login_page.login(env_config["username"],env_config["password"],validate_code=env_config["validate_code"])
    login_page.wait(3000)
    login_page.screenshot("登录成功")

def test_login_fail(page: Page):
    page.goto("http://mall.lemonban.com/admin/#/login")
    expect(page.get_by_text("L-maiill4后台")).to_be_visible()