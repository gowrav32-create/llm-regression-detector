import json

from pathlib import Path

import yaml

from schemas import EvalResult, GoldenTestCase, PromptConfig

from llm_feature import classify_email

dataset_path = Path("datasets/golden_dataset_v1.json")

prompt_path = Path("prompts/prompt_v1.yaml")

with prompt_path.open("r", encoding="utf-8") as file:
    prompt_data = yaml.safe_load(file)

prompt_config = PromptConfig(**prompt_data)

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

    prediction = classify_email(test_case.input)
    category_match = prediction.category == test_case.expected_category
    if category_match:
        print("Pass")
    else:
        print("Fail")
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

print(f"Passed: {passed_count}/{total_count}")
print(f"Pass rate: {pass_rate:.2f}%")

print(f"Stored {len(results)} evaluation results")
print(prompt_config.version)
print(prompt_config.feature_name)
print(list(prompt_config.categories.keys()))

