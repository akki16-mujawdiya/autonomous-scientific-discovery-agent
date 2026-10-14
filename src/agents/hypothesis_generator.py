
def generate_hypotheses(papers):
    """
    Generate basic research hypothesis suggestions
    from research paper summaries.
    """
    hypotheses = []

    for paper in papers:
        title = paper.get("title", "Unknown research paper")
        summary = paper.get("summary", "").strip()

        if not summary:
            continue

        hypotheses.append({
            "source_paper": title,
            "hypothesis": (
                f"Further research could investigate: {summary[:200]}"
            ),
        })

    return hypotheses
