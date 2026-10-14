
def review_papers(papers):
    """
    Review research papers and extract their key information.
    """
    reviewed_papers = []

    for paper in papers:
        reviewed_papers.append({
            "title": paper.get("title", "No title available"),
            "summary": paper.get("summary", "No summary available"),
            "authors": paper.get("authors", []),
            "link": paper.get("link", ""),
        })

    return reviewed_papers
