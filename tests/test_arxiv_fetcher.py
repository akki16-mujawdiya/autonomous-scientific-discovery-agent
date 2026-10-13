
from unittest.mock import Mock, patch

from src.ingestion.arxiv_fetcher import fetch_papers


@patch("src.ingestion.arxiv_fetcher.requests.get")
def test_fetch_papers_success(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = """
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <title>Test Research Paper</title>
            <author>
                <name>Test Author</name>
            </author>
            <summary>This is a test summary.</summary>
            <link href="https://example.com/paper" />
            <published>2026-10-11T10:00:00Z</published>
        </entry>
    </feed>
    """
    mock_get.return_value = mock_response

    papers = fetch_papers(
        search_query="machine learning",
        max_results=1,
    )

    assert len(papers) == 1
    assert papers[0]["title"] == "Test Research Paper"
    assert papers[0]["authors"] == ["Test Author"]
    assert papers[0]["summary"] == "This is a test summary."
    assert papers[0]["link"] == "https://example.com/paper"
    assert papers[0]["published"] == "2026-10-11T10:00:00Z"


@patch("src.ingestion.arxiv_fetcher.requests.get")
def test_fetch_papers_timeout(mock_get):
    import requests

    mock_get.side_effect = requests.exceptions.Timeout

    papers = fetch_papers()

    assert papers == []
