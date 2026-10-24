
from src.agents.literature_reviewer import review_papers
from src.agents.hypothesis_generator import generate_hypotheses
from src.agents.code_executor import validate_python_code
from src.agents.rag_retriever import retrieve_relevant_papers
from src.agents.self_debugger import run_with_self_debugging
from src.agents.critic_agent import evaluate_statistical_results
from src.agents.research_memory import (
    save_research_memory,
    search_research_memory,
)


def run_workflow(
    papers,
    python_code=None,
    research_query=None,
    debugger=None,
    statistical_results=None,
    memory_query=None,
    memory_content=None,
    memory_type="note",
    memory_metadata=None,
):
    """Coordinate research, code validation, statistical review, and memory."""

    retrieved_papers = []
    if research_query is not None:
        retrieved_papers = retrieve_relevant_papers(research_query)

    papers_to_review = (
        retrieved_papers if research_query is not None else papers
    )
    reviewed_papers = review_papers(papers_to_review)
    hypotheses = generate_hypotheses(reviewed_papers)

    code_validation = None
    execution_result = None

    if python_code is not None:
        if debugger is not None:
            execution_result = run_with_self_debugging(
                python_code, debugger=debugger, max_attempts=3
            )
            code_validation = validate_python_code(
                execution_result["final_code"]
            )
        else:
            code_validation = validate_python_code(python_code)

    critic_report = None
    if statistical_results is not None:
        critic_report = evaluate_statistical_results(statistical_results)

    saved_memory_id = None
    if memory_content is not None:
        saved_memory_id = save_research_memory(
            content=memory_content,
            memory_type=memory_type,
            metadata=memory_metadata,
        )

    found_memories = []
    if memory_query is not None:
        found_memories = search_research_memory(memory_query)

    return {
        "reviewed_papers": reviewed_papers,
        "hypotheses": hypotheses,
        "code_validation": code_validation,
        "execution_result": execution_result,
        "retrieved_papers": retrieved_papers,
        "critic_report": critic_report,
        "saved_memory_id": saved_memory_id,
        "found_memories": found_memories,
    }
