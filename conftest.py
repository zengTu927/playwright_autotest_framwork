from datetime import datetime
import re
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page,BrowserContext,Browser
from filelock import FileLock


from common.read_yaml import ReadYaml
from common.logger import logger,LOG_FILE
from pages.login_page import LoginPage
from common.file_finder import find_latest_file
from common.file_utils import safe_file_name,ensure_dir,clean_directory


def pytest_addoption(parser):
    parser.addoption("--env",action="store",default=None,help="指定运行环境")

@pytest.fixture(scope="session")
def config():
    """开始读取yaml配置"""
    config_data = ReadYaml("config/config.yaml").read()
    logger.info(f"配置文件读取成功：{config_data}")
    return config_data

@pytest.fixture(scope="session")
def timeout_config(config):
    """获取超时时间"""
    timeout = config.get("timeout",{})
    return timeout

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
def env(config,request):
    """获取运行环境"""
    cli_env = request.config.getoption("--env")

    config_env = config.get("env")
    current_env = cli_env or config_env
    if not current_env:
        raise ValueError("未指定运行环境，请使用 --env 或在 config.yaml 中配置 env")
    if current_env not in config:
        raise ValueError(f"config.yaml 中不存在环境配置：{current_env}")
    logger.info(f"当前运行环境为：{current_env}")
    return current_env
@pytest.fixture(scope="session")
def env_config(config,env):
    """获取当前环境的运行配置"""
    current_env_config = config.get(env)
    if not current_env_config:
        raise ValueError(f"配置文件yaml中缺少{env}环境配置")
    logger.info(f"当前环境配置为：{current_env_config}")
    return current_env_config
@pytest.fixture(scope="session")
def base_url(env_config):
    """获取当前运行环境的base_url"""
    current_base_url = env_config.get("base_url")
    if not current_base_url:
        raise ValueError(f"当前环境配置中缺少base_url")
    logger.info(f"当前环境base_url为：{current_base_url}")
    return current_base_url
@pytest.fixture(scope="session")
def get_browser_config(config):
    """获取浏览器运行配置"""
    browser_config = config.get("browser",{})
    logger.info(f"浏览器配置为：{browser_config}")
    return browser_config

@pytest.fixture(autouse=True)
def case_start_and_end():
    """case开始和结束执行的标志"""
    logger.info("开始执行用例")
    yield
    logger.info("结束执行用例")

@pytest.fixture()
def login_page(page:Page):
    """
    返回页面对象，为什么scope为function，第一page fixture是function级别的夹具，
    一个大的作用域依赖小的作用域会导致在执行session级别的夹具时，function级别的夹具还没有准备好，
    调用也没有意义，第二playwright本来是就一条case一个page，如果是session级别的夹具会导致所有的case都使用同一个page对象，造成环境的污染
    """
    return LoginPage(page)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    获取每条用例的执行结果
    set_up:前置阶段
    call:测试用例执行阶段
    teardown:后置阶段
    :param item:
    :return:
    """
    outcome = yield
    result = outcome.get_result()
    setattr(item,f"rep_{result.when}", result)


# @pytest.fixture(autouse=True)
# def screenshot_on_failure(request, page: Page):
#     """
#     用例执行失败时自动截图，并附加到allure报告
#     :param request:
#     :param page:
#     :return:
#     """
#     yield
#     if hasattr(request.node,"rep_call") and request.node.rep_call.failed:
#         screen_name = safe_file_name(request.node.name)
#         screen_bytes = page.screenshot(full_page=True)
#         allure.attach(
#             screen_bytes,
#             name=f"{screen_name}_failure_screenshots",
#             attachment_type=allure.attachment_type.PNG,
#         )
#         logger.error(f"用例执行失败，已将失败截图添加到allure：{screen_name}")
#
# @pytest.fixture(autouse=True)
# def trace_on_failure(request,context:BrowserContext):
#     """
#     用例执行失败时自动录制trace，并附加到allure报告
#     :param request:
#     :param context:
#     :return:
#     """
#     case_name = safe_file_name(request.node.name)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     trace_dir = Path("reports/traces")
#     trace_dir.mkdir(parents=True, exist_ok=True)
#     trace_path = trace_dir / f"{case_name}_{timestamp}_trace.zip"
#     context.tracing.start(
#         screenshots=True,
#         snapshots=True,
#         sources=True,
#     )
#     yield
#     failed = hasattr(request.node,"rep_call") and request.node.rep_call.failed
#     if failed:
#         context.tracing.stop(path=str(trace_path))
#         allure.attach.file(
#             str(trace_path),
#             name = f"{case_name}_trace",
#             attachment_type="application/zip",
#             extension="zip"
#         )
#         logger.error(f"用例执行失败，已将失败trace添加到allure：{case_name}")
#     else:
#         context.tracing.stop()

# @pytest.fixture(autouse=True)
# def video_on_failure(request):
    # """
    #     用例失败后把 Playwright 自动保留的视频附加到 Allure 报告
    #
    #     注意：
    #     Playwright 官方明确说明：视频只有在页面或浏览器上下文关闭后才可用
    #     pytest-playwright 的 video 文件通常在 page/context 关闭后才真正落盘。
    #     因此这个 fixture 不依赖 page/context，尽量让它在 page/context teardown 之后执行。
    #     """
    # yield
    # if hasattr(request.node,"rep_call") and request.node.rep_call.failed:
    #     video_file = find_latest_file("reports/playwright-output", ".webm")
    #     if video_file:
    #         allure.attach.file(
    #             str(video_file),
    #             name=f"{safe_file_name(request.node.name)}失败视频",
    #             attachment_type=allure.attachment_type.WEBM
    #         )
    #         logger.error(f"用例执行失败，失败视频已添加到 Allure：{video_file}")
    #     else:
    #          logger.warning(f"用例执行失败，但未找到失败视频：{request.node.name}")

@pytest.fixture(autouse=True)
def failure_artifacts(request,page: Page,context: BrowserContext):
    """
    用例执行失败时，把所有失败的截图、trace、日志都附加到allure报告
    :param request:
    :param page:
    :param context:
    :return:
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
    failed = hasattr(request.node,"rep_call") and request.node.rep_call.failed
    """
    如果使用了pytest-rerunfailures来实现case执行失败重试时，failed为false，因为第一次执行失败的标记结果是rerun，不是failed，所以不会进行截图和trace的保留
    """
    if failed:
        logger.info(f"用例执行失败，开始收集失败信息{case_name}")
        try:
            page.screenshot(path=str(screenshot_path),full_page=True)
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
                extension="zip"
            )
            logger.error(f"用例执行失败，已添加失败trace：{trace_path}")
        except Exception as e:
            logger.error(f"用例执行失败，添加失败trace失败：{e}")

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
            logger.error(f"用例执行成功，停止trace失败：{e}")




def pytest_sessionstart(session):
    """
    session开始时，清理报告目录
    :param session:
    :return:
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



@pytest.fixture(scope="session")
def auth_state_file(tmp_path_factory, worker_id, browser: Browser, env_config):
    """
    多进程并行时复用登录态。

    实现逻辑：
    1. 所有 worker 共用同一个 storage_state 文件
    2. 第一个 worker 负责登录并写入文件
    3. 其他 worker 等待文件生成后直接复用
    """

    auth_dir = Path("playwright/.auth")
    auth_dir.mkdir(parents=True, exist_ok=True)

    state_path = auth_dir / "state.json"
    lock_path = auth_dir / "state.lock"

    with FileLock(str(lock_path)):
        if not state_path.exists():
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            page = context.new_page()

            login_page = LoginPage(page)
            login_page.open_login_page(env_config["base_url"])
            login_page.login(
                env_config["username"],
                env_config["password"],
                validate_code=env_config.get("validate_code", "lemon"),
            )

            # 根据你的系统实际登录成功标志修改
            page.wait_for_load_state("networkidle", timeout=60000)

            context.storage_state(path=str(state_path))
            context.close()

            logger.info(f"登录态已生成：{state_path}")
        else:
            logger.info(f"复用已有登录态：{state_path}")

    return str(state_path)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, get_browser_config, auth_state_file):
    """
    修改 playwright 默认浏览器上下文配置，并注入登录态。
    """

    viewport = get_browser_config.get("viewport")

    return {
        **browser_context_args,
        "viewport": {
            "width": viewport.get("width"),
            "height": viewport.get("height"),
        },
        "ignore_https_errors": True,
        "storage_state": auth_state_file,
    }


"""
多进程运行时，每个进程使用不同的账号登录态
gw0 使用 test_user_0
gw1 使用 test_user_1
gw2 使用 test_user_2

test:
    base_url: "http://mall.lemonban.com/admin/#/login"
    users:
      gw0:
        username: "test_user_0"
        password: "123456"
        validate_code: "lemon"
      gw1:
        username: "test_user_1"
        password: "123456"
        validate_code: "lemon"
      gw2:
        username: "test_user_2"
        password: "123456"
        validate_code: "lemon"
      master:
        username: "test_user_0"
        password: "123456"
        validate_code: "lemon"

@pytest.fixture(scope="session")
def current_user(env_config, worker_id):
    users = env_config.get("users", {})

    # 单进程运行时 worker_id 是 master
    if worker_id in users:
        return users[worker_id]

    # worker 数超过账号数时，兜底使用 gw0
    return users.get("gw0")

@pytest.fixture(scope="session")
def current_user(env_config, worker_id):
    """"""
    根据 xdist worker 分配测试账号。
    单进程运行时 worker_id 为 master。
    """"""

    users = env_config.get("users")

    if not users:
        return {
            "username": env_config["username"],
            "password": env_config["password"],
            "validate_code": env_config.get("validate_code", "lemon"),
        }

    if worker_id in users:
        return users[worker_id]

    return users["gw0"]


@pytest.fixture(scope="session")
def auth_state_file(worker_id, browser: Browser, env_config, current_user):
    """"""
    每个 worker 使用独立账号和独立登录态文件。
    """"""

    auth_dir = Path("playwright/.auth")
    auth_dir.mkdir(parents=True, exist_ok=True)

    state_path = auth_dir / f"state_{worker_id}.json"
    lock_path = auth_dir / f"state_{worker_id}.lock"

    with FileLock(str(lock_path)):
        if not state_path.exists():
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            page = context.new_page()

            login_page = LoginPage(page)
            login_page.open_login_page(env_config["base_url"])
            login_page.login(
                current_user["username"],
                current_user["password"],
                validate_code=current_user.get("validate_code", "lemon"),
            )

            page.wait_for_load_state("networkidle", timeout=60000)

            context.storage_state(path=str(state_path))
            context.close()

            logger.info(f"{worker_id} 登录态已生成：{state_path}")
        else:
            logger.info(f"{worker_id} 复用已有登录态：{state_path}")

    return str(state_path)
"""