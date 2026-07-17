from pydantic import BaseModel
from typing import Literal, Annotated

Category = Literal["billing", "technical", "account", "general"]


# PromptConfig needs:
# 1. version
# 2. feature_name
# 3. categories
# 4. system_prompt

# GoldenTestCase needs:
# 1. id - Category
# 2. input - Category
# 3. expected_category - Category
# 4. expected_summary - Category
# 5. difficulty - Category
# 6. notes - Category

# LLMOutput needs:
# 1. category - Category
# 2. summary - Category

# EvalResult needs:
# 1. case_id - Category
# 2. expected_category - Category
# 3. predicted_category - Category
# 4. category_match - bool
# 5. predicted_summary - Category


class PromptConfig(BaseModel):
    version: str
    feature_name: str
    categories: dict[str, str]
    system_prompt: str


class GoldenTestCase(BaseModel):
    id: str
    input: str
    expected_category: Category
    expected_summary: str
    difficulty: str
    notes: str


class LLMOutput(BaseModel):
    category: Category
    summary: str


class EvalResult(BaseModel):
    case_id: str
    expected_category: Category
    predicted_category: Category
    category_match: bool
    predicted_summary: str