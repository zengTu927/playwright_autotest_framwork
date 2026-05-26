import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    获取每条用例的执行结果。

    setup: 前置阶段
    call: 测试函数执行阶段
    teardown: 后置阶段
    """
    outcome = yield
    result = outcome.get_result()
    setattr(item, f"rep_{result.when}", result)