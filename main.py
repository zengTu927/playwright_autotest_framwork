import pytest

if __name__ == "__main__":
    pytest.main([
        "-s", "-v",
        "--browser", "chromium",
        "--env", "test",
        "--alluredir=reports/allure-results",
        # "-m", "smoke",
        # "-n", "2",
        # "--reruns", "1", "--reruns-delay", "2",
    ])
