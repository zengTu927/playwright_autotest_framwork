import re
from pathlib import Path
from datetime import datetime
from typing import Union, Literal, Callable

import allure
from playwright.sync_api import Page,expect,Locator,BrowserContext

from common.logger import logger


class BasePage:
    def __init__(self,page:Page,expect_timeout:int=30000):
        self.page = page
        self.expect_timeout = expect_timeout

    def _get_locator(self,target:Union[str,Locator]) -> Locator:
        """
        获取locator对象
        :param target: 可以传字符串，对应css或者xpath，也可以传locator
        :return:
        """
        if isinstance(target,str):
            return self.page.locator( target)
        return  target

    def open(self,url:str):
        """
        打开网页
        :param url: 网页url
        :return:
        """
        with allure.step(f"打开网页：{url}"):
            logger.info(f"打开网页：{url}")
            self.page.goto(url,wait_until="domcontentloaded")

    def click(self,target:Union[str,Locator],desc:str = "点击元素"):
        """点击元素"""
        with allure.step(f"{desc}:{target}"):
            logger.info(f"{desc}：{target}")
            locator = self._get_locator(target)
            locator.click()

    def fill(self,target:Union[str,Locator],value:str,desc:str="输入内容"):
        """输入内容"""
        with allure.step(f"定位元素{target},{desc}：{value}"):
            logger.info(f"定位元素{target},{desc}：{value}")
            locator = self._get_locator(target)
            locator.fill(value)

    def get_text(self,target:Union[str,Locator],desc:str="获取元素文本")-> str:
        """获取元素文本"""
        with allure.step(f"获取元素文本：{target}"):
            logger.info(f"{ desc}：{target}")
            locator = self._get_locator(target)
            return locator.inner_text()

    def is_visible(self,target:Union[str,Locator])-> bool:
        """判断元素是否可见"""
        with allure.step(f"判断元素是否可见：{target}"):
            logger.info(f"判断元素是否可见：{target}")
            locator = self._get_locator(target)
            return locator.is_visible()

    def expect_visible(self,target:Union[str,Locator]):
        """等待元素可见"""
        with allure.step(f"等待元素可见：{target}"):
            logger.info(f"等待元素可见：{target}")
            locator = self._get_locator(target)
            expect(locator).to_be_visible(timeout=self.expect_timeout)

    def expect_text(self,target:Union[str,Locator],text:str):
        """断言元素含指定文本"""
        with allure.step(f"断言{target}元素含指定文本：{text}"):
            logger.info(f"断言{target}元素含指定文本：{text}")
            locator = self._get_locator(target)
            expect(locator).to_contain_text(text,timeout=self.expect_timeout)

    def expect_title_contains(self,title:str):
        """断言页面标题包含指定内容"""
        with allure.step(f"断言页面标题包含指定内容：{title}"):
            logger.info(f"断言页面标题包含指定内容：{title}")
            expect(self.page).to_have_title(re.compile(title),timeout=self.expect_timeout)

    def expect_url_contains(self,url:str):
        """断言页面url包含指定内容"""
        with allure.step(f"断言页面url包含指定内容：{url}"):
            logger.info(f"断言页面url包含指定内容：{url}")
            pattern = re.compile(f".*{re.escape(url)}.*")
            expect(self.page).to_have_url(pattern,timeout=self.expect_timeout)

    def screenshot(self, name: str = "screenshot", full_page: bool = True) -> str:
        """截图并返回截图路径"""
        screenshot_dir = Path("reports/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = screenshot_dir / f"{name}_{timestamp}.png"

        self.page.screenshot(path=str(file_path), full_page=full_page)

        logger.info(f"截图已保存: {file_path}")
        allure.attach.file(
            str(file_path),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

        return str(file_path)
    def wait(self,timeout:int=3000):
        """强制等待"""
        with allure.step(f"强制等待：{timeout}毫秒"):
            logger.info(f"强制等待：{timeout}毫秒")
            self.page.wait_for_timeout(timeout)

    def wait_for_page_status(self,status:Literal["load","domcontentloaded","networkidle"]="domcontentloaded",timeout:int=10000):
        """等待页面加载状态"""
        with allure.step(f"等待页面加载状态：{status}"):
            logger.info(f"等待页面加载状态：{status}")
            self.page.wait_for_load_state(state=status,timeout=timeout)

    def expect_new_page_by_context(self,context:BrowserContext,action: Callable[[], None],wait_until:str="load"):
        """
        通过context等待新页面打开
        :param context:
        :param action:
        :param wait_until:
        :return:
        """
        with allure.step(f"通过context等待新页面打开,打开新页面前的操作为{action}"):
            logger.info(f"通过context等待新页面打开,打开新页面前的操作为{action}")
            with context.expect_page() as new_page_info:
                action()
            new_page = new_page_info.value
            new_page.wait_for_load_state(wait_until)
            return new_page

    def expect_popup_by_page(
            self,
            action: Callable[[], None],
            wait_until: str = "load",
    ) -> Page:
        """
        执行某个动作，并等待当前 page 打开 popup。
        """
        with allure.step(f"执行某个动作，并等待当前 page 打开 popup,打开 popup前的操作为{action}"):
            logger.info(f"执行某个动作，并等待当前 page 打开 popup,打开 popup前的操作为{action}")
            with self.page.expect_popup() as popup_info:
                action()
            popup = popup_info.value
            popup.wait_for_load_state(wait_until)
            return popup



    def expect_popup_by_context(
            self,
            context: BrowserContext,
            action: Callable[[], None],
            wait_until: str = "load",
    ) -> Page:
        """
        执行某个动作，并等待当前 context 创建的 popup。
        """
        with allure.step(f"执行某个动作，并等待当前 context 创建的 popup,打开 popup前的操作为{action}"):
            logger.info(f"执行某个动作，并等待当前 context 创建的 popup,打开 popup前的操作为{action}")
        self.page.locator("").select_option(["value1","value2"])
        expect(self.page.locator()).to_have_values(["value1","value2"])
        self.page.locator().select_option(["value1","value2"])
        expect(self.page.locator()).to_have_values()
        self.page.clock.set_fixed_time()
        self.page.clock.install()
        self.page.clock.pause_at()
        self.page.clock.fast_forward()
        self.page.clock.resume()
        self.page.clock.run_for()
        def handle_dialog(dialog):
            if dialog.type == "alert":
                dialog.accept()
            elif dialog.type == "confirm":
                dialog.accept()
            elif dialog.type == "prompt":
                dialog.accept("")
        self.page.on("dialog", handle_dialog)
        self.page.close(run_before_unload=True)