
from src.agents.literature_reviewer import review_papers
from src.agents.hypothesis_generator import generate_hypotheses
from src.agents.code_executor import validate_python_code


def run_workflow(papers, python_code=None):
    """Coordinate the basic scientific discovery workflow."""

    reviewed_papers = review_papers(papers)
    hypotheses = generate_hypotheses(reviewed_papers)

    code_validation = None

    if python_code is not None:
        code_validation = validate_python_code(python_code)

    return {
        "reviewed_papers": reviewed_papers,
        "hypotheses": hypotheses,
        "code_validation": code_validation,
    }
