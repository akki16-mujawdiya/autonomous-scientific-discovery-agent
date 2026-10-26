
import pytest

from src.agents.research_memory import (
    save_research_memory,
    search_research_memory,
    build_research_context,
)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def create_test_memory(db_path, **overrides):
    """Create a valid research memory for testing."""
    memory = {
        "content": "Machine learning experiment result",
        "memory_type": "note",
        "metadata": {"source": "test-paper"},
        "db_path": str(db_path),
    }
    memory.update(overrides)
    return save_research_memory(**memory)


# --------------------------------------------------
# Tests for save_research_memory()
# --------------------------------------------------

def test_save_and_search_memory(tmp_path):
    db_path = tmp_path / "research.db"

    memory_id = save_research_memory(
        content="Test hypothesis about machine learning",
        memory_type="hypothesis",
        metadata={"source": "paper-123"},
        db_path=str(db_path),
    )

    results = search_research_memory(
        "machine learning",
        db_path=str(db_path),
    )

    assert memory_id == 1
    assert len(results) == 1
    assert results[0]["content"] == (
        "Test hypothesis about machine learning"
    )
    assert results[0]["memory_type"] == "hypothesis"
    assert results[0]["metadata"]["source"] == "paper-123"


def test_save_memory_strips_whitespace(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "  Important research finding  ",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "Important research finding",
        db_path=str(db_path),
    )

    assert results[0]["content"] == "Important research finding"


def test_save_memory_with_default_values(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Research note",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "Research note",
        db_path=str(db_path),
    )

    assert results[0]["memory_type"] == "note"
    assert results[0]["metadata"] == {}


@pytest.mark.parametrize("content", ["", " ", "\n\t", None, 123])
def test_save_rejects_invalid_content(tmp_path, content):
    with pytest.raises(ValueError, match="content"):
        save_research_memory(
            content,
            db_path=str(tmp_path / "research.db"),
        )


@pytest.mark.parametrize("memory_type", ["", " ", None, 123])
def test_save_rejects_invalid_memory_type(tmp_path, memory_type):
    with pytest.raises(ValueError, match="memory_type"):
        save_research_memory(
            "Research finding",
            memory_type=memory_type,
            db_path=str(tmp_path / "research.db"),
        )


def test_save_rejects_invalid_metadata(tmp_path):
    with pytest.raises(TypeError, match="metadata"):
        save_research_memory(
            "Research finding",
            metadata=["invalid"],
            db_path=str(tmp_path / "research.db"),
        )


# --------------------------------------------------
# Tests for search_research_memory()
# --------------------------------------------------

def test_search_filters_by_memory_type(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Machine learning hypothesis",
        memory_type="hypothesis",
        db_path=str(db_path),
    )
    save_research_memory(
        "Machine learning result",
        memory_type="result",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "Machine learning",
        memory_type="result",
        db_path=str(db_path),
    )

    assert len(results) == 1
    assert results[0]["memory_type"] == "result"


def test_search_returns_empty_for_missing_database(tmp_path):
    results = search_research_memory(
        "anything",
        db_path=str(tmp_path / "missing.db"),
    )

    assert results == []


def test_search_is_case_insensitive(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Machine Learning Experiment",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "machine learning",
        db_path=str(db_path),
    )

    assert len(results) == 1


def test_search_respects_result_limit(tmp_path):
    db_path = tmp_path / "research.db"

    for number in range(5):
        save_research_memory(
            f"Research experiment {number}",
            db_path=str(db_path),
        )

    results = search_research_memory(
        "Research experiment",
        limit=2,
        db_path=str(db_path),
    )

    assert len(results) == 2


def test_search_returns_newest_memories_first(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Research finding alpha",
        db_path=str(db_path),
    )
    save_research_memory(
        "Research finding beta",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "Research finding",
        db_path=str(db_path),
    )

    assert results[0]["content"] == "Research finding beta"
    assert results[1]["content"] == "Research finding alpha"


@pytest.mark.parametrize("query", ["", " ", None, 123])
def test_search_rejects_invalid_query(tmp_path, query):
    with pytest.raises(ValueError, match="query"):
        search_research_memory(
            query,
            db_path=str(tmp_path / "research.db"),
        )


@pytest.mark.parametrize("limit", [0, -1, True, 1.5, "10"])
def test_search_rejects_invalid_limit(tmp_path, limit):
    with pytest.raises(ValueError, match="limit"):
        search_research_memory(
            "research",
            limit=limit,
            db_path=str(tmp_path / "research.db"),
        )


def test_memory_persists_between_calls(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Experiment result was reproducible",
        memory_type="result",
        db_path=str(db_path),
    )

    results = search_research_memory(
        "reproducible",
        db_path=str(db_path),
    )

    assert len(results) == 1
    assert results[0]["content"] == (
        "Experiment result was reproducible"
    )


# --------------------------------------------------
# Tests for build_research_context()
# --------------------------------------------------

def test_build_context_returns_matching_memories(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Machine learning hypothesis",
        memory_type="hypothesis",
        db_path=str(db_path),
    )
    save_research_memory(
        "Machine learning experimental result",
        memory_type="result",
        db_path=str(db_path),
    )
    save_research_memory(
        "Unrelated astronomy observation",
        db_path=str(db_path),
    )

    context = build_research_context(
        "Machine learning",
        db_path=str(db_path),
    )

    assert "Machine learning hypothesis" in context
    assert "Machine learning experimental result" in context
    assert "Unrelated astronomy observation" not in context


def test_build_context_respects_character_budget(tmp_path):
    db_path = tmp_path / "research.db"

    for number in range(5):
        save_research_memory(
            f"Machine learning finding {number} " + "A" * 100,
            db_path=str(db_path),
        )

    context = build_research_context(
        "Machine learning",
        max_chars=200,
        db_path=str(db_path),
    )

    assert len(context) <= 200


def test_build_context_returns_empty_when_no_match(tmp_path):
    context = build_research_context(
        "unknown topic",
        db_path=str(tmp_path / "research.db"),
    )

    assert context == ""


def test_build_context_contains_memory_type_and_id(tmp_path):
    db_path = tmp_path / "research.db"

    save_research_memory(
        "Hypothesis about model accuracy",
        memory_type="hypothesis",
        db_path=str(db_path),
    )

    context = build_research_context(
        "model accuracy",
        db_path=str(db_path),
    )

    assert "[hypothesis | ID: 1]" in context
    assert "Hypothesis about model accuracy" in context


@pytest.mark.parametrize("max_chars", [0, -1, True, 1.5, "100"])
def test_build_context_rejects_invalid_character_budget(
    tmp_path, max_chars
):
    with pytest.raises(ValueError, match="max_chars"):
        build_research_context(
            "research",
            max_chars=max_chars,
            db_path=str(tmp_path / "research.db"),
        )


@pytest.mark.parametrize("limit", [0, -1, True, 1.5, "10"])
def test_build_context_rejects_invalid_limit(tmp_path, limit):
    with pytest.raises(ValueError, match="limit"):
        build_research_context(
            "research",
            limit=limit,
            db_path=str(tmp_path / "research.db"),
        )


@pytest.mark.parametrize("query", ["", " ", None, 123])
def test_build_context_rejects_invalid_query(tmp_path, query):
    with pytest.raises(ValueError, match="query"):
        build_research_context(
            query,
            db_path=str(tmp_path / "research.db"),
        )
