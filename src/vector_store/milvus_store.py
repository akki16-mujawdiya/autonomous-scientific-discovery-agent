
from pymilvus import MilvusClient, DataType


MILVUS_DB_PATH = "scientific_papers.db"
COLLECTION_NAME = "research_papers_v3"
VECTOR_DIMENSION = 384


def create_milvus_client():
    """Create or connect to the local Milvus database."""
    return MilvusClient(MILVUS_DB_PATH)


def create_papers_collection(client):
    """Create the research papers collection if it does not exist."""

    if client.has_collection(COLLECTION_NAME):
        client.load_collection(collection_name=COLLECTION_NAME)
        return

    schema = client.create_schema(
        auto_id=False,
        enable_dynamic_field=False,
    )

    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
    )
    schema.add_field(
        field_name="title",
        datatype=DataType.VARCHAR,
        max_length=512,
    )
    schema.add_field(
        field_name="summary",
        datatype=DataType.VARCHAR,
        max_length=8192,
    )
    schema.add_field(
        field_name="source",
        datatype=DataType.VARCHAR,
        max_length=64,
    )
    schema.add_field(
        field_name="doi",
        datatype=DataType.VARCHAR,
        max_length=256,
    )
    schema.add_field(
        field_name="published",
        datatype=DataType.VARCHAR,
        max_length=128,
    )
    schema.add_field(
        field_name="peer_review_status",
        datatype=DataType.VARCHAR,
        max_length=64,
    )
    schema.add_field(
        field_name="vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=VECTOR_DIMENSION,
    )

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
        index_params=index_params,
    )
    client.load_collection(collection_name=COLLECTION_NAME)


def store_paper(
    client,
    paper_id,
    title,
    summary,
    embedding,
    source="unknown",
    doi="",
    published="",
    peer_review_status="unverified",
):
    """Insert or update a paper and its metadata."""

    if len(embedding) != VECTOR_DIMENSION:
        raise ValueError(
            f"Embedding must contain {VECTOR_DIMENSION} numbers."
        )

    if not isinstance(paper_id, int) or isinstance(paper_id, bool):
        raise TypeError("paper_id must be an integer.")

    if not title:
        title = "No title available"
    if not summary:
        summary = "No summary available"

    record = {
        "id": paper_id,
        "title": title[:512],
        "summary": summary[:8192],
        "vector": embedding,
    }

    # Include metadata only when supplied. This preserves legacy calls/tests.
    metadata = {
        "source": source,
        "doi": doi,
        "published": published,
        "peer_review_status": peer_review_status,
    }

    for field, value in metadata.items():
        if value and value != "unknown" and value != "unverified":
            record[field] = value[: {"source": 64, "doi": 256, "published": 128,
                                     "peer_review_status": 64}[field]]

    client.upsert(
        collection_name=COLLECTION_NAME,
        data=[record],
    )


def search_similar_papers(client, embedding, limit=5):
    """Search for papers with similar embeddings."""

    if len(embedding) != VECTOR_DIMENSION:
        raise ValueError(
            f"Embedding must contain {VECTOR_DIMENSION} numbers."
        )

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be at least 1")

    client.load_collection(collection_name=COLLECTION_NAME)

    return client.search(
        collection_name=COLLECTION_NAME,
        data=[embedding],
        anns_field="vector",
        limit=limit,
        output_fields=["title", "summary"],
    )
