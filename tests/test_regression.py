from src.regression import calculate_regression, calculate_shared_case_pass_rates, find_case_regressions


def test_detects_regression():
    change, detected = calculate_regression(80.0, 100.0)

    
    assert change == -20.0
    assert detected is True


def test_detects_no_regression_when_performance_is_stable():
    change, detected = calculate_regression(100.0, 100.0)


    assert change == 0.0
    assert detected is False


def test_handles_missing_previous_run():
    change, detected = calculate_regression(100.0, None)

    
    assert change is None
    assert detected is False


def test_finds_case_level_regression():
    previous_results = [
        {
            "case_id": "case_001",
            "category_match": True
        },
        {
            "case_id": "case_002",
            "category_match": True
        }
    ]

    current_results = [
        {
            "case_id": "case_001",
            "category_match": True
        },
        {
            "case_id": "case_002",
            "category_match": False
        }
    ]

    regressions = find_case_regressions(
        current_results=current_results,
        previous_results=previous_results
    )


    assert regressions == ["case_002"]


def test_new_failing_case_is_not_a_regression():
    previous_results = [
        {
            "case_id": "case_001",
            "category_match": True
        }
    ]

    current_results = [
        {
            "case_id": "case_001",
            "category_match": True
        },
        {
            "case_id": "case_011",
            "category_match": False
        }
    ]

    regressions = find_case_regressions(
        current_results=current_results,
        previous_results=previous_results
    )

    assert regressions == []


def test_shared_case_pass_rates_ignore_new_cases():
    previous_results = [
        {
            "case_id": "case_001",
            "category_match": True
        },
        {
            "case_id": "case_002",
            "category_match": True
        }
    ]

    current_results = [
        {
            "case_id": "case_001",
            "category_match": True
        },
        {
            "case_id": "case_002",
            "category_match": True
        },
        {
            "case_id": "case_011",
            "category_match": False
        }
    ]

    current_rate, previous_rate = calculate_shared_case_pass_rates(
        current_results=current_results,
        previous_results=previous_results
    )

    assert current_rate == 100.0
    assert previous_rate == 100.0
    