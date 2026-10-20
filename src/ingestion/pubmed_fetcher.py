
import requests
import xml.etree.ElementTree as ET

PUBMED_API_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
)
PUBMED_SUMMARY_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
)
REQUEST_TIMEOUT = 30


def fetch_pubmed_papers(search_query="machine learning", max_results=5):
    """Fetch paper metadata from PubMed.

    Peer-review status is marked unverified because the API response
    alone does not confirm that an individual paper was peer-reviewed.
    """

    if not isinstance(search_query, str) or not search_query.strip():
        raise ValueError("Search query cannot be empty.")

    if (
        not isinstance(max_results, int)
        or isinstance(max_results, bool)
        or max_results < 1
    ):
        raise ValueError("max_results must be a positive integer.")

    search_params = {
        "db": "pubmed",
        "term": search_query.strip(),
        "retmax": max_results,
        "retmode": "json",
    }

    try:
        response = requests.get(
            PUBMED_API_URL,
            params=search_params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        paper_ids = response.json()["esearchresult"]["idlist"]

        if not paper_ids:
            return []

        summary_params = {
            "db": "pubmed",
            "id": ",".join(paper_ids),
            "retmode": "xml",
        }

        response = requests.get(
            PUBMED_SUMMARY_URL,
            params=summary_params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        print(f"Error fetching papers from PubMed: {error}")
        return []

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as error:
        print(f"Error parsing PubMed response: {error}")
        return []

    papers = []

    for article in root.findall(".//DocSum"):
        paper_id = article.findtext("Id", default="")
        title = ""
        authors = []
        doi = ""
        published = ""

        for item in article.findall("Item"):
            item_name = item.get("Name", "")

            if item_name == "Title":
                title = item.text or ""

            elif item_name == "PubDate":
                published = item.text or ""

            elif item_name == "Author":
                author_name = item.text or ""
                if author_name:
                    authors.append(author_name)

            elif item_name == "DOI":
                doi = item.text or ""

        papers.append({
            "title": title or "No title available",
            "authors": authors,
            "summary": "",
            "link": (
                f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
                if paper_id else ""
            ),
            "published": published,
            "source": "PubMed",
            "doi": doi,
            "peer_reviewed": None,
            "peer_review_status": "unverified",
        })

    return papers
