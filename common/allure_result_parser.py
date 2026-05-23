import json
from pathlib import Path
from typing import Any


def parse_allure_results(allure_results_dir: str) -> dict[str, Any]:
    """
    解析 Allure 原始结果目录，统计测试结果
    """
    result_dir = Path(allure_results_dir)

    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "broken": 0,
        "skipped": 0,
        "unknown": 0,
        "pass_rate": "0.00%",
        "failed_cases": [],
        "broken_cases": [],
        "skipped_cases": [],
    }

    if not result_dir.exists():
        return stats

    result_files = list(result_dir.glob("*-result.json"))

    for result_file in result_files:
        try:
            with result_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            continue

        status = data.get("status", "unknown")
        name = data.get("name", "未知用例")

        stats["total"] += 1

        if status == "passed":
            stats["passed"] += 1
        elif status == "failed":
            stats["failed"] += 1
            stats["failed_cases"].append(name)
        elif status == "broken":
            stats["broken"] += 1
            stats["broken_cases"].append(name)
        elif status == "skipped":
            stats["skipped"] += 1
            stats["skipped_cases"].append(name)
        else:
            stats["unknown"] += 1

    if stats["total"] > 0:
        pass_rate = stats["passed"] / stats["total"] * 100
        stats["pass_rate"] = f"{pass_rate:.2f}%"

    return stats