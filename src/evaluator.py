import sys

import json

import argparse

from .regression import calculate_regression, calculate_shared_case_pass_rates, find_case_regressions

from datetime import datetime

from pathlib import Path

import yaml

from .schemas import EvalResult, GoldenTestCase, PromptConfig

from .llm_feature import classify_email


def select_previous_report(
    runs_directory: Path,
    report_path: Path,
    baseline: str | None
) -> Path | None:
    if baseline:
        baseline_path = Path(baseline)

        if not baseline_path.exists():
            raise FileNotFoundError(
                f"Baseline report not found: {baseline_path}"
            )

        return baseline_path

    existing_reports = [
        report
        for report in runs_directory.glob("v*_20*.json")
        if report != report_path
    ]

    existing_reports.sort(
        key=lambda report: report.stat().st_mtime
    )

    if existing_reports:
        return existing_reports[-1]

    return None

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
        default="prompts/prompt_v4.yaml",
        help="Path to the prompt YAML file."
    )

    parser.add_argument(
        "--baseline",
        default=None,
        help="Optional path to a trusted baseline JSON report."
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

    try:
        previous_report_path = select_previous_report(
            runs_directory=runs_directory,
            report_path=report_path,
            baseline=args.baseline
        )
    except FileNotFoundError as error:
        parser.error(str(error))


    with dataset_path.open("r", encoding="utf-8") as file:
        dataset_data = json.load(file)

    test_cases = [
        GoldenTestCase(**case)
        for case in dataset_data
    ]


    print(f"Loaded {len(test_cases)} test cases")

    
    results = evaluate_cases(
        test_cases=test_cases,
        system_prompt=prompt_config.system_prompt,
        classifier=classify_email
    )

    for result in results:
        print(result.case_id, result.expected_category)

        if result.category_match:
            print("Pass")
        else:
            print("Fail")
            print("Case ID:", result.case_id)
            print("Expected category:", result.expected_category)
            print("Predicted category:", result.predicted_category)
        
        print(
            result.predicted_category,
            result.predicted_summary
        )

    passed_count = 0

    for result in results:
        if result.category_match:
            passed_count += 1

    total_count = len(results)

    pass_rate = (passed_count / total_count) * 100

    previous_results = []


    if previous_report_path:
        with previous_report_path.open("r", encoding="utf-8") as file:
            previous_report_data = json.load(file)

        previous_results = previous_report_data.get("results", [])

    current_results = [
        result.model_dump()
        for result in results
    ]

    shared_current_pass_rate, shared_previous_pass_rate = (
        calculate_shared_case_pass_rates(
            current_results=current_results,
            previous_results=previous_results
        )
    )

    if (
        shared_current_pass_rate is None
        or shared_previous_pass_rate is None
    ):
        pass_rate_change = None
        aggregate_regression_detected = False
    else:
        pass_rate_change, aggregate_regression_detected = (
            calculate_regression(
                current_pass_rate=shared_current_pass_rate,
                previous_pass_rate=shared_previous_pass_rate
            )
        )

    case_regressions = find_case_regressions(
        current_results=current_results,
        previous_results=previous_results
    )

    regression_detected = (
        aggregate_regression_detected
        or bool(case_regressions)
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
            "shared_current_pass_rate": shared_current_pass_rate,
            "shared_previous_pass_rate": shared_previous_pass_rate,
            "pass_rate_change": pass_rate_change,
            "aggregate_regression_detected": aggregate_regression_detected,
            "case_regressions": case_regressions,
            "regression_detected": regression_detected
        },
        "results": current_results
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

    print("Shared current pass rate:", shared_current_pass_rate)
    print("Shared previous pass rate:", shared_previous_pass_rate)
    print("Pass rate change:", pass_rate_change)
    print("Case regressions:", case_regressions)
    print("Regression detected:", regression_detected)

    if regression_detected: 
        print("Evaluation failed: regression detected.")
        sys.exit(1)

    print("Evaluation passed: no regression detected.")


if __name__ == "__main__":
    main()
