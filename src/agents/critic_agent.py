
def evaluate_statistical_results(results):
    """
    Evaluate statistical results and flag missing information
    or potential issues without inventing conclusions.
    """
    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    findings = []
    p_value = results.get("p_value")
    confidence_interval = results.get("confidence_interval")
    sample_size = results.get("sample_size")
    assumptions = results.get("assumptions")

    # Check p-value
    if p_value is None:
        findings.append("P-value is missing.")
    elif isinstance(p_value, bool) or not isinstance(p_value, (int, float)):
        findings.append("P-value must be a number.")
    elif not 0 <= p_value <= 1:
        findings.append("P-value must be between 0 and 1.")
    elif p_value < 0.05:
        findings.append(
            "P-value is below 0.05; assess the result "
            "alongside effect size and study design."
        )
    else:
        findings.append(
            "P-value is not below 0.05; this alone "
            "does not prove that there is no effect."
        )

    # Check confidence interval
    if confidence_interval is None:
        findings.append("Confidence interval is missing.")
    elif (
        not isinstance(confidence_interval, (list, tuple))
        or len(confidence_interval) != 2
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            for value in confidence_interval
        )
    ):
        findings.append(
            "Confidence interval must contain two numeric bounds."
        )
    elif confidence_interval[0] > confidence_interval[1]:
        findings.append(
            "Confidence interval lower bound exceeds upper bound."
        )

    # Check sample size
    if sample_size is None:
        findings.append("Sample size is missing.")
    elif (
        isinstance(sample_size, bool)
        or not isinstance(sample_size, int)
        or sample_size <= 0
    ):
        findings.append("Sample size must be a positive integer.")

    # Check assumptions
    if not assumptions:
        findings.append(
            "Statistical assumptions are missing or not documented."
        )

    return {
        "valid_input": True,
        "findings": findings,
        "requires_human_review": True,
    }
