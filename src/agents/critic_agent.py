
import math


def evaluate_statistical_results(results):
    """
    Evaluate experimental statistical results.

    Checks:
    - P-value validity and interpretation
    - Confidence interval validity
    - Sample size
    - Effect size
    - Statistical assumptions
    - Consistency between supplied statistics

    This function reviews supplied statistics. It does not calculate
    p-values or confidence intervals from raw experimental data.
    Human review is always required.
    """
    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    findings = []
    warnings = []

    p_value = results.get("p_value")
    confidence_interval = results.get("confidence_interval")
    sample_size = results.get("sample_size")
    assumptions = results.get("assumptions")
    effect_size = results.get("effect_size")

    # 1. Validate p-value
    valid_p_value = False

    if p_value is None:
        findings.append("P-value is missing.")

    elif (
        isinstance(p_value, bool)
        or not isinstance(p_value, (int, float))
        or not math.isfinite(p_value)
    ):
        findings.append("P-value must be a finite number.")

    elif not 0 <= p_value <= 1:
        findings.append("P-value must be between 0 and 1.")

    else:
        valid_p_value = True

        if p_value < 0.05:
            findings.append(
                "P-value is below 0.05; assess the result "
                "alongside effect size and study design."
            )
        else:
            findings.append(
                "P-value is not below 0.05; this alone "
                "does not prove that there is no effect."
            )

    # 2. Validate confidence interval
    valid_ci = False

    if confidence_interval is None:
        findings.append("Confidence interval is missing.")

    elif (
        not isinstance(confidence_interval, (list, tuple))
        or len(confidence_interval) != 2
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in confidence_interval
        )
    ):
        findings.append(
            "Confidence interval must contain two finite numeric bounds."
        )

    elif confidence_interval[0] > confidence_interval[1]:
        findings.append(
            "Confidence interval lower bound exceeds upper bound."
        )

    else:
        valid_ci = True
        lower, upper = confidence_interval

        if lower <= 0 <= upper:
            findings.append(
                "Confidence interval includes zero. For a difference "
                "measure, zero is compatible with the interval."
            )
        else:
            findings.append(
                "Confidence interval excludes zero. For a difference "
                "measure, interpret this alongside the test and study design."
            )

    # 3. Validate sample size
    if sample_size is None:
        findings.append("Sample size is missing.")

    elif (
        isinstance(sample_size, bool)
        or not isinstance(sample_size, int)
        or sample_size <= 0
    ):
        findings.append("Sample size must be a positive integer.")

    elif sample_size < 30:
        warnings.append(
            "Sample size is below 30. Assess statistical power "
            "and whether the test assumptions are appropriate."
        )

    # 4. Validate effect size
    if effect_size is None:
        findings.append(
            "Effect size is missing; practical importance cannot "
            "be assessed from the supplied effect size."
        )

    elif (
        isinstance(effect_size, bool)
        or not isinstance(effect_size, (int, float))
        or not math.isfinite(effect_size)
    ):
        findings.append("Effect size must be a finite number.")

    # 5. Check statistical assumptions
    if not assumptions:
        findings.append(
            "Statistical assumptions are missing or not documented."
        )

    elif not isinstance(assumptions, (list, tuple, str)):
        findings.append(
            "Assumptions must be provided as a string, list, or tuple."
        )

    # 6. Check compatibility of supplied statistics
    if valid_p_value and valid_ci:
        warnings.append(
            "Verify that the p-value and confidence interval use "
            "compatible methods and evaluate the same hypothesis."
        )

    # Human review is always required for scientific conclusions.
    return {
        "valid_input": True,
        "findings": findings,
        "warnings": warnings,
        "requires_human_review": True,
    }
