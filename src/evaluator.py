import json

from pathlib import Path

import yaml

from schemas import GoldenTestCase, PromptConfig

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

print(f"Loaded {len(test_cases)} test cases")

for test_case in test_cases:
    print(test_case.id, test_case.expected_category)

print(prompt_config.version)
print(prompt_config.feature_name)
print(list(prompt_config.categories.keys()))

