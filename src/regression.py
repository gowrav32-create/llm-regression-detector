def calculate_regression(
    current_pass_rate: float,
    previous_pass_rate: float | None
) -> tuple[float | None, bool]:
    if previous_pass_rate is None:
        return None, False
    
    pass_rate_change = round(
        current_pass_rate - previous_pass_rate,
        2
    )

    regression_detected = pass_rate_change < 0

    return pass_rate_change, regression_detected


def find_case_regressions(
    current_results: list[dict],
    previous_results: list[dict]
) -> list[str]:
    previous_results_by_case = {
        result["case_id"]: result["category_match"]
        for result in previous_results
    }


    regressions = []

    for current_result in current_results:
        case_id = current_result["case_id"]


        previously_passed = {
            previous_results_by_case.get(case_id) is True
        }

        currently_failed = (
            current_result["category_match"] is False
        )

        if previously_passed and currently_failed:
            regressions.append(case_id)


    return regressions
