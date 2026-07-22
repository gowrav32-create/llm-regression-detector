import pytest
from pydantic import ValidationError

from src.schemas import LLMOutput


def test_llm_output_accepts_valid_category():
    output = LLMOutput(
        category="billing",
        summary="The customer has a billing question."
    )

    assert output.category == "billing"
    assert output.summary == "The customer has a billing question."


def test_llm_output_rejects_invalid_category():
    with pytest.raises(ValidationError):
        LLMOutput(
            category="shipping",
            summary="The customer is asking about shipping."
        )