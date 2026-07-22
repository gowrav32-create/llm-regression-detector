from src import evaluator


def test_evaluator_main_is_callable():
    assert callable(evaluator.main)