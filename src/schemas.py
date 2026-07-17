from pydantic import BaseModel


# PromptConfig needs:
# 1. version
# 2. feature_name
# 3. categories
# 4. system_prompt

# GoldenTestCase needs:
# 1. id - str
# 2. input - str
# 3. expected_category - str
# 4. expected_summary - str
# 5. difficulty - str
# 6. notes - str

# LLMOutput needs:
# 1. category - str
# 2. summary - str


class PromptConfig(BaseModel):
    version: str
    feature_name: str
    categories: dict[str, str]
    system_prompt: str
    

class GoldenTestCase(BaseModel):
    id: str
    input: str
    expected_category: str
    expected_summary: str
    difficulty: str
    notes: str


class LLMOutput(BaseModel):
    category: str
    summary: str