# from typing import Optional

# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams

# from app.config.settings import settings


# VECTOR_SIZE = 1536

# _qdrant_client: Optional[QdrantClient] = None


# def get_qdrant_client() -> QdrantClient:
#     """Return a reusable Qdrant client instance."""

#     global _qdrant_client

#     if _qdrant_client is not None:
#         return _qdrant_client

#     if not settings.QDRANT_URL:
#         raise ValueError("QDRANT_URL is not configured.")

#     # A vector database stores embedding vectors and lets us retrieve records by
#     # semantic similarity instead of only exact keyword matches. Qdrant is a good
#     # fit because it is purpose-built for vector search, supports metadata
#     # payloads, and can run locally or as a managed service.
#     print(settings.QDRANT_URL,settings.QDRANT_API_KEY)
#     _qdrant_client = QdrantClient(
#         url=settings.QDRANT_URL,
#         api_key=settings.QDRANT_API_KEY or None,
#         cloud_inference=True
#     )

#     return _qdrant_client


# def create_collection_if_not_exists() -> None:
#     """Create the incidents vector collection when it does not already exist."""

#     client = get_qdrant_client()
#     collection_name = settings.QDRANT_COLLECTION_NAME 
#     if client.collection_exists(collection_name=collection_name): 
#         return

#     # Cosine similarity compares the direction of two vectors. For text
#     # embeddings, this is useful because we care about semantic closeness more
#     # than raw vector magnitude.
#     #
#     # The vector size must match the embedding model output exactly. The
#     # text-embedding-3-small model returns 1536-dimensional vectors, so Qdrant
#     # must create the collection with size=1536 or future inserts will fail.
#     client.create_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(
#             size=VECTOR_SIZE,
#             distance=Distance.COSINE,
#         ),
#     )






"""
Qdrant client factory.

Vector size is 1536 to match both the OpenAI text-embedding-3-small model
and the local mock embedding fallback (which also outputs 1536 dimensions).
"""

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config.settings import settings

VECTOR_SIZE = 1536

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """Return a reusable Qdrant client instance."""

    global _qdrant_client

    if _qdrant_client is not None:
        return _qdrant_client

    if not settings.QDRANT_URL:
        raise ValueError(
            "QDRANT_URL is not configured. "
            "Set it in your .env file (see .env.example)."
        )

    _qdrant_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )

    return _qdrant_client


def create_collection_if_not_exists() -> None:
    """Create the incidents vector collection when it does not already exist."""

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    if client.collection_exists(collection_name=collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(f"Created Qdrant collection '{collection_name}' with {VECTOR_SIZE}-dim vectors.")