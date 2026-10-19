
from src.utils.embedding_generator import generate_embedding
from src.vector_store.milvus_store import (
    create_milvus_client,
    create_papers_collection,
    search_similar_papers,
)


def retrieve_relevant_papers(query, limit=5):
    """
    Retrieve research papers relevant to a research question
    using embeddings and Milvus similarity search.
    """
    if not query or not query.strip():
        raise ValueError("Research query cannot be empty.")

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("Limit must be a positive integer.")

    query_embedding = generate_embedding(query)

    client = create_milvus_client()

    try:
        create_papers_collection(client)

        results = search_similar_papers(
            client,
            query_embedding,
            limit=limit,
        )

        relevant_papers = []

        for result_group in results:
            for result in result_group:
                paper = result.get("entity", {})

                relevant_papers.append({
                    "title": paper.get("title", "No title available"),
                    "summary": paper.get("summary", "No summary available"),
                    "id": result.get("id"),
                    "similarity_score": result.get("distance"),
                })

        return relevant_papers

    finally:
        client.close()
