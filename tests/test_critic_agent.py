
import pytest

from src.agents.critic_agent import evaluate_statistical_results


def valid_results(**overrides):
    results = {
        "p_value": 0.03,
        "confidence_interval": [1.2, 2.4],
        "sample_size": 100,
        "assumptions": ["independent observations"],
        "effect_size": 0.4,
    }
    results.update(overrides)
    return results


def test_valid_statistical_results():
    report = evaluate_statistical_results(valid_results())

    assert report["valid_input"] is True
    assert report["requires_human_review"] is True
    assert any(
        "below 0.05" in item for item in report["findings"]
    )
    assert "warnings" in report


def test_missing_statistical_values():
    report = evaluate_statistical_results({})

    assert "P-value is missing." in report["findings"]
    assert "Confidence interval is missing." in report["findings"]
    assert "Sample size is missing." in report["findings"]
    assert report["requires_human_review"] is True


@pytest.mark.parametrize("p_value", [-0.1, 1.1])
def test_invalid_p_value_range(p_value):
    report = evaluate_statistical_results(
        valid_results(p_value=p_value)
    )

    assert (
        "P-value must be between 0 and 1."
        in report["findings"]
    )


@pytest.mark.parametrize("p_value", [True, float("nan"), float("inf"), "0.03"])
def test_invalid_p_value_type_or_nonfinite(p_value):
    report = evaluate_statistical_results(
        valid_results(p_value=p_value)
    )

    assert "P-value must be a finite number." in report["findings"]


def test_invalid_confidence_interval():
    report = evaluate_statistical_results(
        valid_results(confidence_interval=[5, 2])
    )

    assert (
        "Confidence interval lower bound exceeds upper bound."
        in report["findings"]
    )


@pytest.mark.parametrize(
    "interval",
    [
        [1],
        [1, 2, 3],
        ["low", 2],
        [float("nan"), 2],
        [True, 2],
    ],
)
def test_malformed_confidence_interval(interval):
    report = evaluate_statistical_results(
        valid_results(confidence_interval=interval)
    )

    assert any(
        "Confidence interval must contain" in item
        for item in report["findings"]
    )


def test_confidence_interval_includes_zero():
    report = evaluate_statistical_results(
        valid_results(confidence_interval=[-0.5, 0.8])
    )

    assert any(
        "includes zero" in item for item in report["findings"]
    )


def test_confidence_interval_excludes_zero():
    report = evaluate_statistical_results(
        valid_results(confidence_interval=[0.1, 0.8])
    )

    assert any(
        "excludes zero" in item for item in report["findings"]
    )


def test_invalid_sample_size():
    report = evaluate_statistical_results(
        valid_results(sample_size=0)
    )

    assert (
        "Sample size must be a positive integer."
        in report["findings"]
    )


@pytest.mark.parametrize("sample_size", [True, 2.5, -1, "100"])
def test_invalid_sample_size_types(sample_size):
    report = evaluate_statistical_results(
        valid_results(sample_size=sample_size)
    )

    assert (
        "Sample size must be a positive integer."
        in report["findings"]
    )


def test_small_sample_size_warning():
    report = evaluate_statistical_results(
        valid_results(sample_size=15)
    )

    assert any(
        "below 30" in item for item in report["warnings"]
    )


def test_missing_effect_size():
    report = evaluate_statistical_results(
        valid_results(effect_size=None)
    )

    assert any(
        "Effect size is missing" in item
        for item in report["findings"]
    )


def test_invalid_effect_size():
    report = evaluate_statistical_results(
        valid_results(effect_size=float("nan"))
    )

    assert (
        "Effect size must be a finite number."
        in report["findings"]
    )


def test_missing_assumptions():
    report = evaluate_statistical_results(
        valid_results(assumptions=[])
    )

    assert (
        "Statistical assumptions are missing or not documented."
        in report["findings"]
    )


def test_invalid_assumptions_type():
    report = evaluate_statistical_results(
        valid_results(assumptions=123)
    )

    assert (
        "Assumptions must be provided as a string, list, or tuple."
        in report["findings"]
    )


def test_non_dictionary_input():
    with pytest.raises(TypeError):
        evaluate_statistical_results([])


def test_human_review_is_always_required():
    report = evaluate_statistical_results(valid_results())

    assert report["requires_human_review"] is True
