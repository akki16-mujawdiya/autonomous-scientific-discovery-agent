import pytest

from src.agents.research_synthesis import (
    generate_latex_abstract,
    _escape_latex,
)


def test_generate_latex_abstract():
    abstract = generate_latex_abstract(
        title="Test Experiment",
        objective="Evaluate a model.",
        methodology="Train a classifier.",
        results={"accuracy": 0.91},
        conclusion="Further research is needed.",
    )

    assert r"\begin{abstract}" in abstract
    assert r"\end{abstract}" in abstract
    assert r"\textbf{Methodology:}" in abstract
    assert r"\textbf{Results:}" in abstract
    assert r"\textbf{Conclusion:}" in abstract


def test_latex_special_characters_are_escaped():
    assert _escape_latex("p_value") == r"p\_value"
    assert _escape_latex("50%") == r"50\%"
    assert _escape_latex("A & B") == r"A \& B"


def test_citations_are_included():
    abstract = generate_latex_abstract(
        title="Test",
        objective="Study a model.",
        methodology="Run an experiment.",
        results={"accuracy": 0.9},
        conclusion="Results need further validation.",
        citations=["Research Paper (2025)"],
    )

    assert r"\textbf{References:}" in abstract
    assert "Research Paper (2025)" in abstract


def test_empty_objective_is_rejected():
    with pytest.raises(ValueError):
        generate_latex_abstract(
            title="Test",
            objective="",
            methodology="Run an experiment.",
            results={"accuracy": 0.9},
            conclusion="Test conclusion.",
        )


def test_results_must_be_dictionary():
    with pytest.raises(TypeError):
        generate_latex_abstract(
            title="Test",
            objective="Study a model.",
            methodology="Run an experiment.",
            results="accuracy 0.9",
            conclusion="Test conclusion.",
        )


def test_invalid_citations_are_rejected():
    with pytest.raises(TypeError):
        generate_latex_abstract(
            title="Test",
            objective="Study a model.",
            methodology="Run an experiment.",
            results={"accuracy": 0.9},
            conclusion="Test conclusion.",
            citations="not a list",
        )
