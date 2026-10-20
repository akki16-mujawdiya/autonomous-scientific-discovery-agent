
from unittest.mock import MagicMock, patch

import pytest

from src.agents.rag_retriever import retrieve_relevant_papers


@patch("src.agents.rag_retriever.create_milvus_client")
@patch("src.agents.rag_retriever.generate_embedding")
def test_retrieve_relevant_papers_success(
    mock_embedding,
    mock_create_client,
):
    mock_embedding.return_value = [0.1] * 384

    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    search_results = [[
        {
            "id": 123,
            "distance": 0.95,
            "entity": {
                "title": "AI in Science",
                "summary": "AI can help scientific research.",
            },
        }
    ]]

    with patch(
        "src.agents.rag_retriever.search_similar_papers",
        return_value=search_results,
    ), patch(
        "src.agents.rag_retriever.create_papers_collection"
    ):
        papers = retrieve_relevant_papers("AI in science", limit=3)

    assert len(papers) == 1
    assert papers[0]["title"] == "AI in Science"
    assert papers[0]["id"] == 123
    assert papers[0]["similarity_score"] == 0.95

    mock_embedding.assert_called_once_with("AI in science")
    mock_client.close.assert_called_once()


@pytest.mark.parametrize("query", ["", "   ", "\n"])
def test_retrieve_relevant_papers_rejects_empty_query(query):
    with pytest.raises(ValueError, match="query cannot be empty"):
        retrieve_relevant_papers(query)


@pytest.mark.parametrize("limit", [0, -1, 1.5, True])
def test_retrieve_relevant_papers_rejects_invalid_limit(limit):
    with pytest.raises(ValueError, match="positive integer"):
        retrieve_relevant_papers("machine learning", limit=limit)


@patch("src.agents.rag_retriever.create_milvus_client")
@patch("src.agents.rag_retriever.generate_embedding")
def test_retrieve_relevant_papers_closes_client_on_error(
    mock_embedding,
    mock_create_client,
):
    mock_embedding.return_value = [0.1] * 384

    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    with patch(
        "src.agents.rag_retriever.create_papers_collection",
        side_effect=RuntimeError("Database error"),
    ):
        with pytest.raises(RuntimeError, match="Database error"):
            retrieve_relevant_papers("machine learning")

    mock_client.close.assert_called_once()
