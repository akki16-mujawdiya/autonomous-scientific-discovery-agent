
import pytest

from src.agents.critic_agent import evaluate_statistical_results


def test_valid_statistical_results():
    results = {
        "p_value": 0.03,
        "confidence_interval": [1.2, 2.4],
        "sample_size": 100,
        "assumptions": ["independent observations"],
    }

    report = evaluate_statistical_results(results)

    assert report["valid_input"] is True
    assert report["requires_human_review"] is True
    assert any("below 0.05" in item for item in report["findings"])


def test_missing_statistical_values():
    report = evaluate_statistical_results({})

    assert "P-value is missing." in report["findings"]
    assert "Confidence interval is missing." in report["findings"]
    assert "Sample size is missing." in report["findings"]
    assert report["requires_human_review"] is True


@pytest.mark.parametrize("p_value", [-0.1, 1.1])
def test_invalid_p_value_range(p_value):
    report = evaluate_statistical_results({
        "p_value": p_value,
        "confidence_interval": [1, 2],
        "sample_size": 10,
        "assumptions": ["independence"],
    })

    assert "P-value must be between 0 and 1." in report["findings"]


def test_invalid_confidence_interval():
    report = evaluate_statistical_results({
        "p_value": 0.2,
        "confidence_interval": [5, 2],
        "sample_size": 10,
        "assumptions": ["independence"],
    })

    assert (
        "Confidence interval lower bound exceeds upper bound."
        in report["findings"]
    )


def test_invalid_sample_size():
    report = evaluate_statistical_results({
        "p_value": 0.2,
        "confidence_interval": [1, 2],
        "sample_size": 0,
        "assumptions": ["independence"],
    })

    assert "Sample size must be a positive integer." in report["findings"]


def test_non_dictionary_input():
    with pytest.raises(TypeError):
        evaluate_statistical_results([])
