import sys

import json

import argparse

from .regression import calculate_regression

from datetime import datetime

from pathlib import Path

import yaml

from .schemas import EvalResult, GoldenTestCase, PromptConfig

from .llm_feature import classify_email


def evaluate_cases(test_cases, system_prompt, classifier):
    results = []

    for test_case in test_cases:
        prediction = classifier(
            test_case.input,
            system_prompt
        )

        category_match = (
            prediction.category == test_case.expected_category
        )

        evaluation_result = EvalResult(
            case_id=test_case.id,
            expected_category=test_case.expected_category,
            predicted_category=prediction.category,
            category_match=category_match,
            predicted_summary=prediction.summary
        )

        results.append(evaluation_result)

    return results


def main():
    dataset_path = Path("datasets/golden_dataset_v1.json")

    parser = argparse.ArgumentParser(
        description="Evaluate an LLM prompt against the golden dataset."
    )

    parser.add_argument(
        "--prompt",
        default="prompts/prompt_v3.yaml",
        help="Path to the prompt YAML file."
    )

    args = parser.parse_args()

    prompt_path = Path(args.prompt)

    with prompt_path.open("r", encoding="utf-8") as file:
        prompt_data = yaml.safe_load(file)

    prompt_config = PromptConfig(**prompt_data)


    model_name = "llama3.2:3b"


    runs_directory = Path("runs")
    runs_directory.mkdir(exist_ok=True)


    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    report_path = runs_directory / f"{prompt_config.version}_{timestamp}.json"

    existing_reports = [
            report
            for report in runs_directory.glob("v*_20*.json")
            if report != report_path
        ]


    existing_reports.sort(
        key=lambda path: path.stat().st_mtime
    )


    previous_report_path = (
        existing_reports[-1]
        if existing_reports
        else None
    )


    with dataset_path.open("r", encoding="utf-8") as file:
        dataset_data = json.load(file)

    test_cases = [
        GoldenTestCase(**case)
        for case in dataset_data
    ]

    results = []

    print(f"Loaded {len(test_cases)} test cases")

    for test_case in test_cases:
        print(test_case.id, test_case.expected_category)

        prediction = classify_email(test_case.input, prompt_config.system_prompt)
        category_match = prediction.category == test_case.expected_category
        if category_match:
            print("Pass")
        else:
            print("Fail")
            print("Case ID:", test_case.id)
            print("Expected category:", test_case.expected_category)
            print("Predicted category:", prediction.category)
        evaluation_result = EvalResult(
            case_id = test_case.id,
            expected_category = test_case.expected_category,
            predicted_category = prediction.category,
            category_match = category_match,
            predicted_summary = prediction.summary
        )
        results.append(evaluation_result)

        print(prediction.category, prediction.summary)

    passed_count = 0
    for result in results:
        if result.category_match:
            passed_count += 1

    total_count = len(results)

    pass_rate = (passed_count / total_count) * 100

    previous_pass_rate = None


    if previous_report_path:
        with previous_report_path.open("r", encoding="utf-8") as file:
            previous_report_data = json.load(file)

        previous_pass_rate = previous_report_data["pass_rate"]
        
    pass_rate_change, regression_detected = calculate_regression(
        current_pass_rate=pass_rate,
        previous_pass_rate=previous_pass_rate
    )

    report_data = {
        "timestamp": timestamp,
        "prompt_version": prompt_config.version,
        "model": model_name,
        "total_cases": total_count,
        "passed_cases": passed_count,
        "pass_rate": round(pass_rate, 2),
        "comparison": {
            "previous_report": (
                previous_report_path.name
                if previous_report_path
                else None
            ),
            "previous_pass_rate": previous_pass_rate,
            "pass_rate_change": pass_rate_change,
            "regression_detected": regression_detected
        },
        "results": [
            result.model_dump()
            for result in results
        ]
    }

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=2)

    print(f"Passed: {passed_count}/{total_count}")
    print(f"Pass rate: {pass_rate:.2f}%")
    print(f"Stored {len(results)} evaluation results")
    print(prompt_config.version)
    print(prompt_config.feature_name)
    print(list(prompt_config.categories.keys()))
    print("Report saved:", report_path)

    if previous_report_path:
        print("Previous report:", previous_report_path)
    else:
        print("No previous report found.")

    print("Previous pass rate:", previous_pass_rate)
    print("Pass rate change:", pass_rate_change)
    print("Regression detected:", regression_detected)

    if regression_detected: 
        print("Evaluation failed: regression detected.")
        sys.exit(1)

    print("Evaluation passed: no regression detected.")


if __name__ == "__main__":
    main()
