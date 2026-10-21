from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.research_pipeline import run_research_pipeline


@patch("src.ingestion.research_pipeline.search_similar_papers")
@patch("src.ingestion.research_pipeline.store_paper")
@patch("src.ingestion.research_pipeline.generate_embedding")
@patch("src.ingestion.research_pipeline.create_papers_collection")
@patch("src.ingestion.research_pipeline.create_milvus_client")
@patch("src.ingestion.research_pipeline.fetch_papers")
def test_pipeline_fetches_stores_and_searches_papers(
    mock_fetch,
    mock_create_client,
    mock_create_collection,
    mock_generate_embedding,
    mock_store_paper,
    mock_search,
):
    papers = [
        {
            "title": "AI in Science",
            "summary": "AI helps scientific research.",
            "authors": ["Test Author"],
            "link": "https://example.com/paper-1",
            "published": "2026",
        },
        {
            "title": "Machine Learning Research",
            "summary": "Machine learning helps analyze data.",
            "authors": ["Another Author"],
            "link": "https://example.com/paper-2",
            "published": "2026",
        },
    ]

    mock_fetch.return_value = papers
    mock_generate_embedding.return_value = [0.1] * 384
    mock_search.return_value = [{"id": 1, "distance": 0.99}]

    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    result = run_research_pipeline("artificial intelligence", 2)

    assert result["papers_fetched"] == 2
    assert result["papers_stored"] == 2
    assert len(result["search_results"]) == 1

    mock_fetch.assert_called_once_with(
        search_query="artificial intelligence",
        max_results=2,
    )
    assert mock_generate_embedding.call_count == 2
    assert mock_store_paper.call_count == 2

    mock_search.assert_called_once_with(
        mock_client,
        [0.1] * 384,
        limit=2,
    )
    mock_client.close.assert_called_once()


@patch("src.ingestion.research_pipeline.fetch_papers")
def test_pipeline_returns_empty_result_when_no_papers(mock_fetch):
    mock_fetch.return_value = []

    result = run_research_pipeline("unknown topic", 5)

    assert result == {
        "papers_fetched": 0,
        "papers_stored": 0,
        "search_results": [],
    }


@patch("src.ingestion.research_pipeline.create_milvus_client")
@patch("src.ingestion.research_pipeline.fetch_papers")
def test_pipeline_closes_client_when_processing_fails(
    mock_fetch,
    mock_create_client,
):
    mock_fetch.return_value = [
        {
            "title": "Test paper",
            "summary": "Test summary",
            "link": "https://example.com/paper",
        }
    ]

    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    with patch(
        "src.ingestion.research_pipeline.create_papers_collection"
    ), patch(
        "src.ingestion.research_pipeline.generate_embedding",
        side_effect=RuntimeError("Embedding failed"),
    ):
        with pytest.raises(RuntimeError, match="Embedding failed"):
            run_research_pipeline("test", 1)

    mock_client.close.assert_called_once()


@patch("src.ingestion.research_pipeline.fetch_pubmed_papers")
@patch("src.ingestion.research_pipeline.fetch_papers")
def test_pipeline_fetches_from_both_sources(
    mock_fetch_arxiv,
    mock_fetch_pubmed,
):
    mock_fetch_arxiv.return_value = [
        {
            "title": "Arxiv Paper",
            "summary": "Arxiv research summary",
            "source": "arxiv",
            "link": "https://arxiv.org/abs/test-001",
        }
    ]

    mock_fetch_pubmed.return_value = [
        {
            "title": "PubMed Paper",
            "summary": "PubMed research summary",
            "source": "pubmed",
            "link": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        }
    ]

    with patch(
        "src.ingestion.research_pipeline.create_milvus_client"
    ) as mock_create_client, patch(
        "src.ingestion.research_pipeline.create_papers_collection"
    ), patch(
        "src.ingestion.research_pipeline.generate_embedding",
        return_value=[0.1] * 384,
    ), patch(
        "src.ingestion.research_pipeline.store_paper"
    ), patch(
        "src.ingestion.research_pipeline.search_similar_papers",
        return_value=[],
    ):
        mock_create_client.return_value = MagicMock()

        result = run_research_pipeline(
            "test topic",
            1,
            source="both",
        )

    assert result["papers_fetched"] == 2
    assert result["papers_stored"] == 2
    assert result["sources"] == ["arxiv", "pubmed"]

    mock_fetch_arxiv.assert_called_once_with(
        search_query="test topic",
        max_results=1,
    )
    mock_fetch_pubmed.assert_called_once_with(
        search_query="test topic",
        max_results=1,
    )
