

import pytest

from common.read_yaml import ReadYaml
from common.logger import logger


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=None, help="指定运行环境")


@pytest.fixture(scope="session")
def config():
    """读取 yaml 配置"""
    config_data = ReadYaml("config/config.yaml").read()
    logger.info(f"配置文件读取成功：{config_data}")
    return config_data


@pytest.fixture(scope="session")
def timeout_config(config):
    """获取超时时间配置"""
    return config.get("timeout", {})


@pytest.fixture(scope="session")
def env(config, request):
    """获取当前运行环境"""
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
def env_config(config, env):
    """获取当前环境配置"""
    current_env_config = config.get(env)

    if not current_env_config:
        raise ValueError(f"配置文件 yaml 中缺少 {env} 环境配置")

    logger.info(f"当前环境配置为：{current_env_config}")
    return current_env_config


@pytest.fixture(scope="session")
def runtime_base_url(env_config):
    """
    获取运行时的env，判断使用test环境还是prod环境的url
    :param env:
    :return:
    """
    base_url = env_config.get("base_url")

    if not base_url:
        raise ValueError("当前环境配置中缺少 base_url")

    base_url = base_url.rstrip("/")
    logger.info(f"当前运行 base_url 为：{base_url}")

    return base_url




@pytest.fixture(scope="session")
def get_context_config(config):
    """获取浏览器配置"""
    current_browser_config = config.get("context", {})
    logger.info(f"浏览器配置为：{current_browser_config}")
    return current_browser_config