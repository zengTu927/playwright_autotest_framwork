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
def test_login(login_page,env_config,new_context):
    new_page = new_context().new_page()
    new_page.goto("https://tool.liumingye.cn")
    login_page.open_login_page()
    login_page.login(env_config["username"],env_config["password"],validate_code=env_config["validate_code"])
    login_page.wait(3000)
    login_page.screenshot("登录成功")


@pytest.mark.parametrize("text",["L-maiill4后台","L-mall4后台","test"])
def test_login_fail(page: Page,text):
    page.goto("/admin/#/login")
    expect(page.get_by_text(text)).to_be_visible()