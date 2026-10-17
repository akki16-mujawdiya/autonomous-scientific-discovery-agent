
import requests
import xml.etree.ElementTree as ET

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def fetch_pubmed_papers(search_query="machine learning", max_results=5):
    """Fetch research paper details from PubMed."""
    search_params = {
        "db": "pubmed",
        "term": search_query,
        "retmax": max_results,
        "retmode": "json",
    }

    try:
        response = requests.get(
            PUBMED_API_URL,
            params=search_params,
            timeout=30,
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
            timeout=30,
        )
        response.raise_for_status()

    except (requests.exceptions.RequestException, ValueError, KeyError) as error:
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
        for item in article.findall("Item"):
            if item.get("Name") == "Title":
                title = item.text or ""
                break

        papers.append({
            "title": title or "No title available",
            "authors": [],
            "summary": "",
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/",
            "published": "",
        })

    return papers
