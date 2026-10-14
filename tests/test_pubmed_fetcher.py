
from unittest.mock import Mock, patch

import requests

from src.ingestion.pubmed_fetcher import fetch_pubmed_papers


@patch("src.ingestion.pubmed_fetcher.requests.get")
def test_fetch_pubmed_papers_success(mock_get):
    search_response = Mock()
    search_response.raise_for_status.return_value = None
    search_response.json.return_value = {
        "esearchresult": {"idlist": ["12345"]}
    }

    summary_response = Mock()
    summary_response.raise_for_status.return_value = None
    summary_response.text = """
    <eSummaryResult>
        <DocSum>
            <Id>12345</Id>
            <Item Name="Title" Type="String">AI in Science</Item>
        </DocSum>
    </eSummaryResult>
    """

    mock_get.side_effect = [search_response, summary_response]

    papers = fetch_pubmed_papers("machine learning", max_results=1)

    assert len(papers) == 1
    assert papers[0]["title"] == "AI in Science"
    assert papers[0]["link"] == "https://pubmed.ncbi.nlm.nih.gov/12345/"
    assert papers[0]["authors"] == []
    assert papers[0]["summary"] == ""


@patch("src.ingestion.pubmed_fetcher.requests.get")
def test_fetch_pubmed_papers_no_results(mock_get):
    search_response = Mock()
    search_response.raise_for_status.return_value = None
    search_response.json.return_value = {
        "esearchresult": {"idlist": []}
    }
    mock_get.return_value = search_response

    papers = fetch_pubmed_papers()

    assert papers == []
    assert mock_get.call_count == 1


@patch("src.ingestion.pubmed_fetcher.requests.get")
def test_fetch_pubmed_papers_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout

    papers = fetch_pubmed_papers()

    assert papers == []
