# Playwright UI 自动化测试框架

## 1. 项目介绍

本项目是基于 Playwright + pytest + Allure + Jenkins + 飞书搭建的 UI 自动化测试框架。

主要能力包括：

- Playwright 浏览器自动化
- pytest 用例管理
- Page Object 页面对象封装
- YAML 配置和测试数据管理
- Allure 测试报告
- 失败截图
- Playwright Trace
- 失败视频
- 日志记录
- Jenkins 持续集成
- 飞书测试结果通知

---

## 2. 技术栈

| 技术 | 作用 |
|---|---|
| Python | 自动化脚本语言 |
| pytest | 测试用例组织和执行 |
| Playwright | 浏览器自动化 |
| Allure | 测试报告 |
| Jenkins | 持续集成 |
| 飞书机器人 | 测试结果通知 |
| PyYAML | YAML 配置读取 |
| requests | 飞书 Webhook 请求 |

---

## 3. 项目结构

```text
playwright_autotest_framwork/
│
├── common/
│   ├── logger.py
│   ├── read_yaml.py
│   ├── file_utils.py
│   ├── allure_result_parser.py
│   └── lark.py
│
├── config/
│   └── config.yaml
│
├── data/
│   └── login_data.yaml
│
├── pages/
│   ├── base_page.py
│   └── login_page.py
│
├── reports/
│   ├── allure-results/
│   ├── screenshots/
│   ├── traces/
│   ├── logs/
│   └── playwright-output/
│
├── tests/
│   └── test_login.py
│
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Jenkinsfile
└── README.md