import argparse
import json
from typing import Any

import requests

from common.allure_result_parser import parse_allure_results


def send_lark_card(webhook: str, card: dict[str, Any]) -> None:
    """
    发送飞书消息卡片
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "msg_type": "interactive",
        "card": card,
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


def build_failed_case_text(failed_cases: list[str], broken_cases: list[str], max_count: int = 10) -> str:
    """
    构建失败 / 异常用例文本
    """
    cases = []

    for case in failed_cases:
        cases.append(f"失败：{case}")

    for case in broken_cases:
        cases.append(f"异常：{case}")

    if not cases:
        return "无"

    lines = []

    for index, case in enumerate(cases[:max_count], start=1):
        lines.append(f"{index}. {case}")

    if len(cases) > max_count:
        lines.append(f"... 还有 {len(cases) - max_count} 条未展示")

    return "\n".join(lines)


def get_card_color(build_status: str) -> str:
    """
    根据构建状态返回卡片颜色
    """
    if build_status == "SUCCESS":
        return "green"

    if build_status == "FAILURE":
        return "red"

    if build_status == "UNSTABLE":
        return "orange"

    return "grey"


def build_lark_card(
    job_name: str,
    build_number: str,
    build_status: str,
    test_env: str,
    test_mark: str,
    browsers: str,
    reruns: str,
    build_url: str,
    allure_url: str,
    allure_results_dir: str,
) -> dict[str, Any]:
    """
    构建飞书消息卡片
    """
    stats = parse_allure_results(allure_results_dir)

    color = get_card_color(build_status)

    failed_case_text = build_failed_case_text(
        failed_cases=stats["failed_cases"],
        broken_cases=stats["broken_cases"],
    )

    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": color,
            "title": {
                "tag": "plain_text",
                "content": "UI 自动化测试通知"
            }
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**状态：** {build_status}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**项目：** {job_name}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**构建编号：** #{build_number}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**环境：** {test_env}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**标签：** {test_mark}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**浏览器：** {browsers}"
                        }
                    },
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**总数：** {stats['total']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**通过：** {stats['passed']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**失败：** {stats['failed']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**异常：** {stats['broken']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**跳过：** {stats['skipped']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**通过率：** {stats['pass_rate']}"
                        }
                    },
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**失败 / 异常用例：**\n{failed_case_text}"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看 Jenkins 构建"
                        },
                        "url": build_url,
                        "type": "default",
                        "value": {}
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看 Allure 报告"
                        },
                        "url": allure_url,
                        "type": "primary",
                        "value": {}
                    }
                ]
            }
        ]
    }

    return card


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
    parser.add_argument("--allure-url", required=True, help="Allure 报告地址")
    parser.add_argument(
        "--allure-results-dir",
        default="reports/allure-results",
        help="Allure 结果目录",
    )

    args = parser.parse_args()

    card = build_lark_card(
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

    send_lark_card(args.webhook, card)


if __name__ == "__main__":
    main()