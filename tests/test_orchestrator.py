
from src.agents.orchestrator import run_workflow


def test_run_workflow():
    papers = [
        {
            "title": "AI in Science",
            "summary": "AI can help researchers analyze scientific data.",
            "authors": ["Amit"],
            "link": "https://example.com/paper",
        }
    ]

    result = run_workflow(
        papers,
        python_code="x = 10",
    )

    assert len(result["reviewed_papers"]) == 1
    assert len(result["hypotheses"]) == 1
    assert result["code_validation"]["valid"] is True
    assert result["critic_report"] is None
    assert result["saved_memory_id"] is None
    assert result["found_memories"] == []


def test_run_workflow_without_code():
    result = run_workflow([])

    assert result["reviewed_papers"] == []
    assert result["hypotheses"] == []
    assert result["code_validation"] is None
    assert result["critic_report"] is None


def test_run_workflow_with_statistical_results():
    results = {
        "p_value": 0.03,
        "confidence_interval": [1.2, 2.4],
        "sample_size": 100,
        "assumptions": ["independent observations"],
    }

    workflow_result = run_workflow(
        papers=[],
        statistical_results=results,
    )

    report = workflow_result["critic_report"]

    assert report is not None
    assert report["valid_input"] is True
    assert report["requires_human_review"] is True
    assert any(
        "below 0.05" in finding
        for finding in report["findings"]
    )


def test_run_workflow_saves_research_memory(tmp_path, monkeypatch):
    from src.agents import orchestrator
    from src.agents.research_memory import (
        save_research_memory,
        search_research_memory,
    )

    db_path = str(tmp_path / "research.db")

    def save_test_database(
        content,
        memory_type="note",
        metadata=None,
    ):
        return save_research_memory(
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            db_path=db_path,
        )

    def search_test_database(
        query,
        memory_type=None,
        limit=10,
    ):
        return search_research_memory(
            query=query,
            memory_type=memory_type,
            limit=limit,
            db_path=db_path,
        )

    monkeypatch.setattr(
        orchestrator,
        "save_research_memory",
        save_test_database,
    )
    monkeypatch.setattr(
        orchestrator,
        "search_research_memory",
        search_test_database,
    )

    result = run_workflow(
        papers=[],
        memory_content="Machine learning improves scientific discovery",
        memory_type="note",
        memory_metadata={"source": "test"},
    )

    assert result["saved_memory_id"] == 1

    memories = search_test_database("machine learning")

    assert len(memories) == 1
    assert memories[0]["content"] == (
        "Machine learning improves scientific discovery"
    )
    assert memories[0]["memory_type"] == "note"
    assert memories[0]["metadata"]["source"] == "test"


def test_run_workflow_searches_research_memory(tmp_path, monkeypatch):
    from src.agents import orchestrator
    from src.agents.research_memory import (
        save_research_memory,
        search_research_memory,
    )

    db_path = str(tmp_path / "research.db")

    save_research_memory(
        content="Machine learning research hypothesis",
        memory_type="hypothesis",
        db_path=db_path,
    )

    def search_test_database(
        query,
        memory_type=None,
        limit=10,
    ):
        return search_research_memory(
            query=query,
            memory_type=memory_type,
            limit=limit,
            db_path=db_path,
        )

    monkeypatch.setattr(
        orchestrator,
        "search_research_memory",
        search_test_database,
    )

    result = run_workflow(
        papers=[],
        memory_query="machine learning",
    )

    assert len(result["found_memories"]) == 1
    assert (
        result["found_memories"][0]["content"]
        == "Machine learning research hypothesis"
    )
    assert (
        result["found_memories"][0]["memory_type"]
        == "hypothesis"
    )
