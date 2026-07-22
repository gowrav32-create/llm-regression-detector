from src.regression import calculate_regression


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

    