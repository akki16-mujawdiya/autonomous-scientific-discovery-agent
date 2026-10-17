
from unittest.mock import MagicMock

import pytest

from src.vector_store.milvus_store import (
    COLLECTION_NAME,
    VECTOR_DIMENSION,
    create_papers_collection,
    store_paper,
    search_similar_papers,
)


def test_create_collection_if_already_exists():
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

    client.insert.assert_called_once()


def test_store_paper_rejects_wrong_embedding_dimension():
    client = MagicMock()
    embedding = [0.1] * 10

    with pytest.raises(ValueError):
        store_paper(
            client,
            123,
            "Test Paper",
            "Test summary",
            embedding,
        )

    client.insert.assert_not_called()


def test_search_similar_papers_success():
    client = MagicMock()
    embedding = [0.1] * VECTOR_DIMENSION
    client.search.return_value = [[
        {
            "id": 123,
            "distance": 1.0,
            "entity": {
                "title": "Test Paper",
                "summary": "Test summary",
            },
        }
    ]]

    results = search_similar_papers(client, embedding, limit=1)

    client.load_collection.assert_called_once_with(
        collection_name=COLLECTION_NAME
    )
    client.search.assert_called_once()
    assert results[0][0]["entity"]["title"] == "Test Paper"


def test_search_rejects_wrong_embedding_dimension():
    client = MagicMock()

    with pytest.raises(ValueError):
        search_similar_papers(client, [0.1] * 10)

    client.search.assert_not_called()
