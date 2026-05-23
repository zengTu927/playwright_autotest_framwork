import argparse
import json
from typing import Optional

import requests

from common.allure_result_parser import parse_allure_results


def send_feishu_text(webhook: str, content: str) -> None:
    """
    发送飞书文本消息
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }

    response = requests.post(
        webhook,
        headers=headers,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=10,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"飞书通知发送失败，状态码：{response.status_code}，响应：{response.text}"
        )

    result = response.json()

    if result.get("code") != 0:
        raise RuntimeError(f"飞书通知发送失败：{result}")


def format_case_list(title: str, cases: list[str], max_count: int = 10) -> str:
    """
    格式化失败/异常/跳过用例列表
    """
    if not cases:
        return ""

    lines = [f"\n{title}："]

    for index, case_name in enumerate(cases[:max_count], start=1):
        lines.append(f"{index}. {case_name}")

    if len(cases) > max_count:
        lines.append(f"... 还有 {len(cases) - max_count} 条未展示")

    return "\n".join(lines)


def build_message(
    job_name: str,
    build_number: str,
    build_status: str,
    test_env: str,
    test_mark: str,
    browsers: str,
    reruns: str,
    build_url: str,
    allure_url: Optional[str],
    allure_results_dir: str,
) -> str:
    """
    构建飞书通知文本
    """
    stats = parse_allure_results(allure_results_dir)

    if build_status == "SUCCESS":
        status_icon = "✅"
    elif build_status == "FAILURE":
        status_icon = "❌"
    elif build_status == "UNSTABLE":
        status_icon = "⚠️"
    else:
        status_icon = "ℹ️"

    message = f"""UI 自动化测试通知

状态：{status_icon} {build_status}
项目名称：{job_name}
构建编号：#{build_number}
测试环境：{test_env}
测试标签：{test_mark}
浏览器：{browsers}
失败重试：{reruns}

测试结果：
总数：{stats["total"]}
通过：{stats["passed"]}
失败：{stats["failed"]}
异常：{stats["broken"]}
跳过：{stats["skipped"]}
未知：{stats["unknown"]}
通过率：{stats["pass_rate"]}
"""

    message += format_case_list("失败用例", stats["failed_cases"])
    message += format_case_list("异常用例", stats["broken_cases"])
    message += format_case_list("跳过用例", stats["skipped_cases"])

    message += f"""

Jenkins 构建：
{build_url}
"""

    if allure_url:
        message += f"""
Allure 报告：
{allure_url}
"""

    return message


def main():
    parser = argparse.ArgumentParser(description="发送飞书测试通知")

    parser.add_argument("--webhook", required=True, help="飞书机器人 Webhook")
    parser.add_argument("--job-name", required=True, help="Jenkins Job 名称")
    parser.add_argument("--build-number", required=True, help="Jenkins 构建编号")
    parser.add_argument("--build-status", required=True, help="Jenkins 构建状态")
    parser.add_argument("--test-env", required=True, help="测试环境")
    parser.add_argument("--test-mark", required=True, help="测试标签")
    parser.add_argument("--browsers", required=True, help="浏览器")
    parser.add_argument("--reruns", required=True, help="失败重试次数")
    parser.add_argument("--build-url", required=True, help="Jenkins 构建地址")
    parser.add_argument("--allure-url", required=False, default="", help="Allure 报告地址")
    parser.add_argument(
        "--allure-results-dir",
        required=False,
        default="reports/allure-results",
        help="Allure 结果目录",
    )

    args = parser.parse_args()

    message = build_message(
        job_name=args.job_name,
        build_number=args.build_number,
        build_status=args.build_status,
        test_env=args.test_env,
        test_mark=args.test_mark,
        browsers=args.browsers,
        reruns=args.reruns,
        build_url=args.build_url,
        allure_url=args.allure_url,
        allure_results_dir=args.allure_results_dir,
    )

    send_feishu_text(args.webhook, message)


if __name__ == "__main__":
    main()