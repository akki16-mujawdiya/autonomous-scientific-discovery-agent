
import hashlib

from src.ingestion.arxiv_fetcher import fetch_papers
from src.ingestion.pubmed_fetcher import fetch_pubmed_papers
from src.utils.embedding_generator import generate_embedding
from src.vector_store.milvus_store import (
    create_milvus_client,
    create_papers_collection,
    store_paper,
    search_similar_papers,
)


def _generate_paper_id(paper):
    """Create a stable integer ID from a paper's link."""
    link = paper.get("link", "").strip()

    if not link:
        raise ValueError("Paper link cannot be empty.")

    digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
    return int(digest[:15], 16)


def _paper_text(paper):
    """Combine the paper title and summary for embedding."""
    title = paper.get("title", "").strip()
    summary = paper.get("summary", "").strip()

    text = f"{title}\n{summary}".strip()

    if not text:
        raise ValueError("Paper title and summary cannot both be empty.")

    return text


def run_research_pipeline(
    search_query="machine learning",
    max_results=5,
    source="arxiv",
):
    """Fetch, embed, store, and search research papers."""

    if source not in ("arxiv", "pubmed", "both"):
        raise ValueError("source must be 'arxiv', 'pubmed', or 'both'.")

    papers = []

    if source in ("arxiv", "both"):
        papers.extend(
            fetch_papers(search_query=search_query, max_results=max_results)
        )

    if source in ("pubmed", "both"):
        papers.extend(
            fetch_pubmed_papers(
                search_query=search_query,
                max_results=max_results,
            )
        )

    if not papers:
        return {
            "papers_fetched": 0,
            "papers_stored": 0,
            "search_results": [],
        }

    client = create_milvus_client()

    try:
        create_papers_collection(client)
        stored_count = 0
        first_embedding = None

        for paper in papers:
            embedding = generate_embedding(_paper_text(paper))

            if first_embedding is None:
                first_embedding = embedding

            store_paper(
                client=client,
                paper_id=_generate_paper_id(paper),
                title=paper.get("title", "No title available"),
                summary=paper.get("summary", "No summary available"),
                embedding=embedding,
                source=paper.get("source", "unknown"),
                doi=paper.get("doi", ""),
                published=paper.get("published", ""),
                peer_review_status=paper.get(
                    "peer_review_status", "unverified"
                ),
            )

            stored_count += 1

        search_results = search_similar_papers(
            client,
            first_embedding,
            limit=min(5, stored_count),
        )

        return {
            "papers_fetched": len(papers),
            "papers_stored": stored_count,
            "search_results": search_results,
            "sources": sorted({
                paper.get("source", "unknown") for paper in papers
            }),
        }

    finally:
        client.close()
