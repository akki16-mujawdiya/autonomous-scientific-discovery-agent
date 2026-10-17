
from unittest.mock import MagicMock

import pytest

from src.vector_store.milvus_store import (
    COLLECTION_NAME,
    VECTOR_DIMENSION,
    create_papers_collection,
    search_similar_papers,
    store_paper,
)


def test_create_collection_when_it_already_exists():
    client = MagicMock()
    client.has_collection.return_value = True

    create_papers_collection(client)

    client.load_collection.assert_called_once_with(
        collection_name=COLLECTION_NAME
    )
    client.create_collection.assert_not_called()


def test_store_paper_success():
    client = MagicMock()
    embedding = [0.1] * VECTOR_DIMENSION

    store_paper(
        client,
        123,
        "Test Paper",
        "Test summary",
        embedding,
    )

    client.upsert.assert_called_once_with(
        collection_name=COLLECTION_NAME,
        data=[
            {
                "id": 123,
                "title": "Test Paper",
                "summary": "Test summary",
                "vector": embedding,
            }
        ],
    )
    client.insert.assert_not_called()


def test_store_paper_rejects_wrong_embedding_dimension():
    client = MagicMock()

    with pytest.raises(ValueError, match="Embedding must contain"):
        store_paper(
            client,
            123,
            "Test Paper",
            "Test summary",
            [0.1] * 10,
        )

    client.upsert.assert_not_called()


def test_search_similar_papers_success():
    client = MagicMock()
    embedding = [0.1] * VECTOR_DIMENSION
    expected_results = [{"id": 123, "distance": 0.95}]
    client.search.return_value = expected_results

    results = search_similar_papers(client, embedding, limit=3)

    client.load_collection.assert_called_once_with(
        collection_name=COLLECTION_NAME
    )
    client.search.assert_called_once_with(
        collection_name=COLLECTION_NAME,
        data=[embedding],
        anns_field="vector",
        limit=3,
        output_fields=["title", "summary"],
    )
    assert results == expected_results


def test_search_rejects_wrong_embedding_dimension():
    client = MagicMock()

    with pytest.raises(ValueError, match="Embedding must contain"):
        search_similar_papers(client, [0.1] * 10)

    client.search.assert_not_called()


def test_store_paper_rejects_non_integer_id():
    client = MagicMock()

    with pytest.raises(TypeError, match="paper_id must be an integer"):
        store_paper(
            client,
            "paper-123",
            "Test Paper",
            "Test summary",
            [0.1] * VECTOR_DIMENSION,
        )

    client.upsert.assert_not_called()


def test_search_rejects_invalid_limit():
    client = MagicMock()

    with pytest.raises(ValueError, match="limit must be at least 1"):
        search_similar_papers(
            client,
            [0.1] * VECTOR_DIMENSION,
            limit=0,
        )

    client.search.assert_not_called()
