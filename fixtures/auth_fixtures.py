from pathlib import Path

import pytest
from filelock import FileLock
from playwright.sync_api import Browser

from common.logger import logger
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def auth_state_file(tmp_path_factory, worker_id, browser: Browser, env_config):
    """
    多进程并行时复用登录态。
    所有 worker 共用同一个 storage_state 文件。
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

            page.wait_for_load_state("networkidle", timeout=60000)

            context.storage_state(path=str(state_path))
            context.close()

            logger.info(f"登录态已生成：{state_path}")
        else:
            logger.info(f"复用已有登录态：{state_path}")

    return str(state_path)


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