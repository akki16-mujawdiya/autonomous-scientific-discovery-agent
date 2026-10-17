
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def generate_embedding(text):
    """Convert research paper text into a 384-dimensional vector."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    model = SentenceTransformer(MODEL_NAME)
    embedding = model.encode(text)

    if hasattr(embedding, "tolist"):
        return embedding.tolist()

    return list(embedding)
