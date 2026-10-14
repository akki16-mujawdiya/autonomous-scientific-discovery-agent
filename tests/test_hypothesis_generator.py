
from src.agents.hypothesis_generator import generate_hypotheses


def test_generate_hypotheses():
    papers = [
        {
            "title": "AI in Science",
            "summary": "AI can help researchers analyze scientific data.",
        }
    ]

    result = generate_hypotheses(papers)

    assert len(result) == 1
    assert result[0]["source_paper"] == "AI in Science"
    assert "AI can help researchers" in result[0]["hypothesis"]


def test_generate_hypotheses_empty_list():
    result = generate_hypotheses([])

    assert result == []


def test_generate_hypotheses_missing_summary():
    papers = [{"title": "Paper without summary", "summary": ""}]

    result = generate_hypotheses(papers)

    assert result == []
