

from playwright.sync_api import Page

from pages.base_page import BasePage



class LoginPage(BasePage):
    def __init__(self,page:Page):
        super().__init__( page)
        self.login_page_title_selector = page.get_by_text("L-mall4后台")
        self.username_selector = page.get_by_role("textbox", name="用户名")
        self.password_selector = page.get_by_role("textbox", name="密码")
        self.validate_code_selector = page.get_by_role("textbox", name="验证码")
        self.login_button_selector = page.get_by_role("button", name="登录")

    def open_login_page(self,base_url:str):
        self.open(base_url)
        self.wait_for_page_status(status="load")
        self.expect_text(self.login_page_title_selector,"L-mall411后台")

    def login(self,username:str,password:str,validate_code:str="lemon"):
        self.fill(self.username_selector,username)
        self.fill(self.password_selector,password)
        self.fill(self.validate_code_selector,validate_code)
        self.click(self.login_button_selector)

