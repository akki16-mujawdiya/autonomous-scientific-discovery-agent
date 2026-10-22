
import pytest

from src.agents.research_memory import (
    save_research_memory,
    search_research_memory,
)


def test_save_and_search_memory(tmp_path):
    db_path = str(tmp_path / "research.db")

    memory_id = save_research_memory(
        content="Test hypothesis about machine learning",
        memory_type="hypothesis",
        metadata={"source": "paper-123"},
        db_path=db_path,
    )

    results = search_research_memory(
        "machine learning",
        db_path=db_path,
    )

    assert memory_id == 1
    assert len(results) == 1
    assert results[0]["content"] == (
        "Test hypothesis about machine learning"
    )
    assert results[0]["memory_type"] == "hypothesis"
    assert results[0]["metadata"]["source"] == "paper-123"


def test_search_filters_by_memory_type(tmp_path):
    db_path = str(tmp_path / "research.db")

    save_research_memory(
        "Machine learning hypothesis",
        memory_type="hypothesis",
        db_path=db_path,
    )
    save_research_memory(
        "Machine learning result",
        memory_type="result",
        db_path=db_path,
    )

    results = search_research_memory(
        "machine learning",
        memory_type="result",
        db_path=db_path,
    )

    assert len(results) == 1
    assert results[0]["memory_type"] == "result"


def test_search_returns_empty_for_missing_database(tmp_path):
    db_path = str(tmp_path / "missing.db")

    results = search_research_memory(
        "anything",
        db_path=db_path,
    )

    assert results == []


def test_memory_persists_between_calls(tmp_path):
    db_path = str(tmp_path / "research.db")

    save_research_memory(
        "Experiment result was reproducible",
        memory_type="result",
        db_path=db_path,
    )

    # Search uses a new database connection.
    results = search_research_memory(
        "reproducible",
        db_path=db_path,
    )

    assert len(results) == 1
    assert results[0]["content"] == (
        "Experiment result was reproducible"
    )


def test_save_rejects_empty_content(tmp_path):
    with pytest.raises(ValueError, match="content"):
        save_research_memory(
            "   ",
            db_path=str(tmp_path / "research.db"),
        )


def test_search_rejects_empty_query(tmp_path):
    with pytest.raises(ValueError, match="query"):
        search_research_memory(
            " ",
            db_path=str(tmp_path / "research.db"),
        )


def test_search_rejects_invalid_limit(tmp_path):
    with pytest.raises(ValueError, match="limit"):
        search_research_memory(
            "research",
            limit=0,
            db_path=str(tmp_path / "research.db"),
        )
