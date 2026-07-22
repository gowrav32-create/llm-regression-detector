from src import evaluator

from src.schemas import GoldenTestCase, LLMOutput


def test_evaluator_main_is_callable():
    assert callable(evaluator.main)


def fake_classifier(email_text, system_prompt):
    return LLMOutput(
        category="billing",
        summary="The customer has a billing question."
    )


def test_evaluate_cases_records_correct_match():
    test_case = GoldenTestCase(
        id="case_test_001",
        input="Why was I charged twice?",
        expected_category="billing",
        expected_summary="The customer reports a duplicate charge.",
        difficulty="easy",
        notes="Unit-test case."
    )


    results = evaluator.evaluate_cases(
        test_cases=[test_case],
        system_prompt="Classify this email.",
        classifier=fake_classifier
    )

    assert len(results) == 1
    assert results[0].case_id == "case_test_001"
    assert results[0].predicted_category == "billing"
    assert results[0].category_match is True

