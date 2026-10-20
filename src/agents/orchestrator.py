
from src.agents.literature_reviewer import review_papers
from src.agents.hypothesis_generator import generate_hypotheses
from src.agents.code_executor import validate_python_code
from src.agents.rag_retriever import retrieve_relevant_papers
from src.agents.self_debugger import run_with_self_debugging


def run_workflow(papers, python_code=None, research_query=None, debugger=None):
    """Coordinate literature review, hypotheses, and optional code execution."""

    retrieved_papers = []
    if research_query is not None:
        retrieved_papers = retrieve_relevant_papers(research_query)

    papers_to_review = retrieved_papers if research_query is not None else papers
    reviewed_papers = review_papers(papers_to_review)
    hypotheses = generate_hypotheses(reviewed_papers)

    code_validation = None
    execution_result = None

    if python_code is not None:
        if debugger is not None:
            execution_result = run_with_self_debugging(
                python_code, debugger=debugger, max_attempts=3
            )
            code_validation = validate_python_code(execution_result["final_code"])
        else:
            code_validation = validate_python_code(python_code)

    return {
        "reviewed_papers": reviewed_papers,
        "hypotheses": hypotheses,
        "code_validation": code_validation,
        "execution_result": execution_result,
        "retrieved_papers": retrieved_papers,
    }
