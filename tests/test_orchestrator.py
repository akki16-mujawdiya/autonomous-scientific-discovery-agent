
from src.agents.orchestrator import run_workflow


def test_run_workflow():
    papers = [
        {
            "title": "AI in Science",
            "summary": "AI can help researchers analyze scientific data.",
            "authors": ["Amit"],
            "link": "https://example.com/paper",
        }
    ]

    result = run_workflow(
        papers,
        python_code="x = 10",
    )

    assert len(result["reviewed_papers"]) == 1
    assert len(result["hypotheses"]) == 1
    assert result["code_validation"]["valid"] is True


def test_run_workflow_without_code():
    result = run_workflow([])

    assert result["reviewed_papers"] == []
    assert result["hypotheses"] == []
    assert result["code_validation"] is None
