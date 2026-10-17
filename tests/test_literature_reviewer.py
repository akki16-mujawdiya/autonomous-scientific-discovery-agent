
from src.agents.literature_reviewer import review_papers


def test_review_papers():
    papers = [
        {
            "title": "AI in Science",
            "summary": "This paper studies AI.",
            "authors": ["Amit"],
            "link": "https://example.com/paper",
        }
    ]

    result = review_papers(papers)

    assert len(result) == 1
    assert result[0]["title"] == "AI in Science"
    assert result[0]["authors"] == ["Amit"]


def test_review_papers_empty_list():
    result = review_papers([])

    assert result == []
