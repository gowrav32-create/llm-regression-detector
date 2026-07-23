import os

import pytest

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

def test_select_previous_report_uses_explicit_baseline(tmp_path):
    baseline_path = tmp_path / "trusted-baseline.json"
    baseline_path.write_text(
        '{"pass_rate": 100.0}',
        encoding="utf-8"
    )

    current_report_path = tmp_path / "v4_2026-07-22_18-00-00.json"

    selected_report = evaluator.select_previous_report(
        runs_directory=tmp_path,
        report_path=current_report_path,
        baseline=str(baseline_path)
    )

    assert selected_report == baseline_path

def test_select_previous_report_rejects_missing_baseline(tmp_path):
    missing_baseline_path = tmp_path / "missing-report.json"
    current_report_path = tmp_path / "v4_2026-07-22_18-00-00.json"

    with pytest.raises(
        FileNotFoundError,
        match="Baseline report not found"
    ):
        evaluator.select_previous_report(
            runs_directory=tmp_path,
            report_path=current_report_path,
            baseline=str(missing_baseline_path)
        )

def test_select_previous_report_uses_newest_report(tmp_path):
    old_report = tmp_path / "v2_2026-07-22_10-00-00.json"
    newest_report = tmp_path / "v3_2026-07-22_11-00-00.json"
    current_report = tmp_path / "v4_2026-07-22_12-00-00.json"

    old_report.write_text("{}", encoding="utf-8")
    newest_report.write_text("{}", encoding="utf-8")
    current_report.write_text("{}", encoding="utf-8")

    os.utime(old_report, (100, 100))
    os.utime(newest_report, (200, 200))
    os.utime(current_report, (300, 300))

    selected_report = evaluator.select_previous_report(
        runs_directory=tmp_path,
        report_path=current_report,
        baseline=None
    )

    assert selected_report == newest_report


def test_select_previous_report_returns_none_when_empty(tmp_path):
    current_report = tmp_path / "v3_2026-07-22_12-00-00.json"

    selected_report = evaluator.select_previous_report(
        runs_directory=tmp_path,
        report_path=current_report,
        baseline=None
    )

    assert selected_report is None