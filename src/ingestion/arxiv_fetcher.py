
import requests
import feedparser

ARXIV_API_URL = "https://export.arxiv.org/api/query"


def fetch_papers(search_query="machine learning", max_results=5):
    params = {
        "search_query": f"all:{search_query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(
            ARXIV_API_URL,
            params=params,
            timeout=30,
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
        paper = {
            "title": getattr(entry, "title", "No title available"),
            "authors": [
                author.name for author in getattr(entry, "authors", [])
            ],
            "summary": getattr(entry, "summary", "No summary available"),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
        }

        papers.append(paper)

    return papers