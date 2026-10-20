
import requests
import feedparser

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_FETCH_TIMEOUT = 30


def fetch_papers(search_query="machine learning", max_results=5):
    """Fetch research papers from arXiv with source metadata."""

    if not isinstance(search_query, str) or not search_query.strip():
        raise ValueError("Search query cannot be empty.")

    if (
        not isinstance(max_results, int)
        or isinstance(max_results, bool)
        or max_results < 1
    ):
        raise ValueError("max_results must be a positive integer.")

    params = {
        "search_query": f"all:{search_query.strip()}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(
            ARXIV_API_URL,
            params=params,
            timeout=ARXIV_FETCH_TIMEOUT,
        )
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("Error: arXiv API request timed out.")
        return []

    except requests.exceptions.RequestException as error:
        print(f"Error fetching papers from arXiv: {error}")
        return []

    feed = feedparser.parse(response.text)
    papers = []

    for entry in feed.entries:
        authors = [
            getattr(author, "name", "")
            for author in getattr(entry, "authors", [])
        ]

        paper = {
            "title": getattr(entry, "title", "No title available").strip(),
            "authors": authors,
            "summary": getattr(
                entry, "summary", "No summary available"
            ).strip(),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
            "source": "arXiv",
            "doi": "",
            "peer_reviewed": None,
            "peer_review_status": "unverified",
        }

        papers.append(paper)

    return papers
