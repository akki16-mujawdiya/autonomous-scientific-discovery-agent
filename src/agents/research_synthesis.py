"""
Research Synthesis Module.

Formats experimental findings into a LaTeX-style research abstract.
This module formats supplied information; it does not invent or verify results.
"""


def _escape_latex(value):
    """Escape special LaTeX characters in plain text."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    return "".join(replacements.get(char, char) for char in str(value))


def generate_latex_abstract(
    title,
    objective,
    methodology,
    results,
    conclusion,
    citations=None,
):
    """
    Generate a LaTeX abstract from supplied research information.

    Args:
        title: Research experiment title.
        objective: Research objective.
        methodology: Method or experiment description.
        results: Dictionary of experimental findings.
        conclusion: Conclusion based on supplied findings.
        citations: Optional list of paper titles or references.

    Returns:
        A LaTeX-formatted abstract as a string.
    """
    required_fields = {
        "title": title,
        "objective": objective,
        "methodology": methodology,
        "results": results,
        "conclusion": conclusion,
    }

    for field, value in required_fields.items():
        if value is None or value == "" or value == {}:
            raise ValueError(f"{field} must not be empty")

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    if citations is not None and not isinstance(citations, list):
        raise TypeError("citations must be a list or None")

    result_text = "; ".join(
        f"{key}: {value}" for key, value in results.items()
    )

    sections = [
        r"\begin{abstract}",
        _escape_latex(objective),
        "",
        r"\textbf{Methodology:} " + _escape_latex(methodology),
        "",
        r"\textbf{Results:} " + _escape_latex(result_text),
        "",
        r"\textbf{Conclusion:} " + _escape_latex(conclusion),
    ]

    if citations:
        citation_text = "; ".join(str(item) for item in citations)
        sections.extend([
            "",
            r"\textbf{References:} " + _escape_latex(citation_text),
        ])

    sections.append(r"\end{abstract}")

    return "\n".join(sections)
