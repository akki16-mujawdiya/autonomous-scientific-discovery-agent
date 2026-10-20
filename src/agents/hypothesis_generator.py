
def generate_hypotheses(papers):
    """
    Generate basic research hypothesis suggestions
    while preserving their supporting literature evidence.
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
            "evidence_summary": summary,
            "source_link": paper.get("link", ""),
            "source_id": paper.get("id"),
            "similarity_score": paper.get("similarity_score"),
        })

    return hypotheses
