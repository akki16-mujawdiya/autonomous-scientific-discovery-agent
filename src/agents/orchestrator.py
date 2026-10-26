
from src.agents.literature_reviewer import review_papers
from src.agents.hypothesis_generator import generate_hypotheses
from src.agents.code_executor import validate_python_code
from src.agents.rag_retriever import retrieve_relevant_papers
from src.agents.self_debugger import run_with_self_debugging
from src.agents.critic_agent import evaluate_statistical_results

from src.agents.research_memory import (
    save_research_memory,
    search_research_memory,
    build_research_context,
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
    context_query=None,
    context_max_chars=4000,
):
    """
    Coordinate the scientific research workflow.

    Features:
    - Retrieve and review relevant research papers.
    - Generate research hypotheses from reviewed papers.
    - Validate Python code or run it with self-debugging.
    - Evaluate supplied statistical results.
    - Save and search persistent research memories.
    - Build bounded context for long-running experiments.

    Note:
    Context size is limited by characters, not exact LLM tokens.
    """

    # 1. Retrieve relevant papers when a research query is supplied.
    retrieved_papers = []

    if research_query is not None:
        retrieved_papers = retrieve_relevant_papers(research_query)

    # 2. Select papers for review.
    papers_to_review = (
        retrieved_papers if research_query is not None else papers
    )

    reviewed_papers = review_papers(papers_to_review)

    # 3. Build research context for long-running experiments.
    research_context = None

    if context_query is not None:
        research_context = build_research_context(
            query=context_query,
            max_chars=context_max_chars,
        )

    # 4. Generate hypotheses from reviewed papers.
    # Research context is returned separately below.
    hypotheses = generate_hypotheses(reviewed_papers)

    # 5. Validate Python code or run it with self-debugging.
    code_validation = None
    execution_result = None

    if python_code is not None:
        if debugger is not None:
            execution_result = run_with_self_debugging(
                python_code,
                debugger=debugger,
                max_attempts=3,
            )

            code_to_validate = execution_result["final_code"]
            code_validation = validate_python_code(code_to_validate)

        else:
            code_validation = validate_python_code(python_code)

    # 6. Review supplied statistical results.
    critic_report = None

    if statistical_results is not None:
        critic_report = evaluate_statistical_results(statistical_results)

    # 7. Save a new research memory if content is provided.
    saved_memory_id = None

    if memory_content is not None:
        saved_memory_id = save_research_memory(
            content=memory_content,
            memory_type=memory_type,
            metadata=memory_metadata,
        )

    # 8. Search previously saved memories.
    found_memories = []

    if memory_query is not None:
        found_memories = search_research_memory(
            query=memory_query,
        )

    # 9. Return workflow outputs.
    return {
        "reviewed_papers": reviewed_papers,
        "hypotheses": hypotheses,
        "code_validation": code_validation,
        "execution_result": execution_result,
        "retrieved_papers": retrieved_papers,
        "critic_report": critic_report,
        "saved_memory_id": saved_memory_id,
        "found_memories": found_memories,
        "research_context": research_context,
    }
