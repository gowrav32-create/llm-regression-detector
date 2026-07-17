from schemas import LLMOutput


def classify_email(email_text: str) -> LLMOutput:
    return LLMOutput(
        category="general",
        summary="The customer is requesting help with an order."
    )