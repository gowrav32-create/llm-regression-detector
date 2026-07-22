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