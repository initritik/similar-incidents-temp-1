# from typing import Any, Dict, List, Optional

# from qdrant_client.models import Filter, ScoredPoint

# from app.config.settings import settings
# from app.db.qdrant_client import get_qdrant_client
# from app.services.embedding_service import generate_embedding


# def _build_qdrant_filter(filters: Optional[Dict[str, str]]) -> Optional[Filter]:
#     """Prepare a future Qdrant filter object from supported filter fields."""

#     # Filtering is intentionally not implemented yet. This placeholder keeps the
#     # public function ready for future exact filters such as assignment_group,
#     # category, and priority without changing the search function signature.
#     if not filters:
#         return None

#     supported_filters = {"assignment_group", "category", "priority"}
#     unsupported_filters = set(filters) - supported_filters

#     if unsupported_filters:
#         raise ValueError(
#             "Unsupported filters: " + ", ".join(sorted(unsupported_filters))
#         )

#     return None


# def _format_search_result(point: ScoredPoint) -> Dict[str, Any]:
#     """Convert a Qdrant scored point into an API-friendly incident result."""

#     payload = point.payload or {}

#     return {
#         "number": payload.get("number", ""),
#         "short_description": payload.get("short_description", ""),
#         "description": payload.get("description", ""),
#         "assignment_group": payload.get("assignment_group", ""),
#         "priority": payload.get("priority", ""),
#         "category": payload.get("category", ""),
#         "resolution_notes": payload.get("resolution_notes", ""),
#         "similarity_score": point.score,
#     }


# def search_similar_incidents(
#     query_text: str,
#     top_k: int = 5,
#     filters: Optional[Dict[str, str]] = None,
# ) -> List[Dict[str, Any]]:
#     """Search Qdrant for incidents semantically similar to the query text."""

#     # Semantic similarity search compares meaning, not just matching words.
#     # A query like "remote access broken after password change" can match a VPN
#     # incident even if the exact words do not appear in the stored record.
#     if not query_text or not query_text.strip():
#         raise ValueError("query_text is required for similarity search.")

#     if top_k < 1:
#         raise ValueError("top_k must be greater than zero.")

#     try:
#         # Step 1: turn the user's query into the same vector space used during
#         # ingestion. Embeddings outperform keyword search because they encode
#         # semantic meaning, synonyms, and related concepts as numeric vectors.
#         query_embedding = generate_embedding(query_text.strip())
#     except Exception as exc:
#         raise RuntimeError("Failed to generate query embedding.") from exc

#     try:
#         client = get_qdrant_client()
#         qdrant_filter = _build_qdrant_filter(filters)

#         # Step 2: Qdrant compares the query vector against stored incident
#         # vectors. The collection was configured with cosine distance, which
#         # measures how close two vectors are by direction. For embeddings, that
#         # direction is a strong signal of semantic similarity.
#         response = client.query_points(
#             collection_name=settings.QDRANT_COLLECTION_NAME,
#             query=query_embedding,
#             limit=top_k,
#             query_filter=qdrant_filter,
#             with_payload=True,
#         )
#     except ValueError:
#         raise
#     except Exception as exc:
#         raise RuntimeError("Qdrant similarity search failed.") from exc

#     points = list(response.points)

#     # Qdrant returns scored points, but sorting here makes the service contract
#     # explicit: highest similarity score first.
#     points.sort(key=lambda point: point.score, reverse=True)

#     return [_format_search_result(point) for point in points]





"""
Similarity search service.

Embeds the query, searches Qdrant, and returns results shaped according to
the RESULT_FIELDS setting so callers can add or remove fields without
touching route or frontend code.
"""

from typing import Any, Dict, List, Optional

from qdrant_client.models import Filter, ScoredPoint

from app.config.settings import settings
from app.db.qdrant_client import get_qdrant_client
from app.services.embedding_service import generate_embedding

# All fields that can appear in a search result.  Add new fields here when
# the ingestion payload is extended; remove them from RESULT_FIELDS in .env
# to hide them from API responses without code changes.
ALL_RESULT_FIELDS = {
    "number",
    "short_description",
    "description",
    "assignment_group",
    "priority",
    "category",
    "state",
    "resolution_notes",
    "opened_at",
    "servicenow_link",
    "similarity_score",
}


def _build_qdrant_filter(filters: Optional[Dict[str, str]]) -> Optional[Filter]:
    if not filters:
        return None

    supported_filters = {"assignment_group", "category", "priority"}
    unsupported_filters = set(filters) - supported_filters

    if unsupported_filters:
        raise ValueError(
            "Unsupported filters: " + ", ".join(sorted(unsupported_filters))
        )

    return None  # Exact-match filter implementation left for a future sprint


def _format_search_result(
    point: ScoredPoint,
    fields: set,
) -> Dict[str, Any]:
    """Return only the requested fields from a Qdrant scored point."""
    payload = point.payload or {}

    result: Dict[str, Any] = {}

    field_map = {
        "number": lambda: payload.get("number", ""),
        "short_description": lambda: payload.get("short_description", ""),
        "description": lambda: payload.get("description", ""),
        "assignment_group": lambda: payload.get("assignment_group", ""),
        "priority": lambda: payload.get("priority", ""),
        "category": lambda: payload.get("category", ""),
        "state": lambda: payload.get("state", ""),
        "resolution_notes": lambda: payload.get("resolution_notes", ""),
        "opened_at": lambda: payload.get("opened_at", ""),
        "servicenow_link": lambda: payload.get("servicenow_link", ""),
        "similarity_score": lambda: point.score,
    }

    for field in fields:
        if field in field_map:
            result[field] = field_map[field]()

    return result


def search_similar_incidents(
    query_text: str,
    top_k: int = 5,
    filters: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Search Qdrant for incidents semantically similar to the query text."""

    if not query_text or not query_text.strip():
        raise ValueError("query_text is required for similarity search.")

    if top_k < 1:
        raise ValueError("top_k must be greater than zero.")

    active_fields = settings.result_fields_set & ALL_RESULT_FIELDS
    if not active_fields:
        active_fields = ALL_RESULT_FIELDS

    try:
        query_embedding = generate_embedding(query_text.strip())
    except Exception as exc:
        raise RuntimeError("Failed to generate query embedding.") from exc

    try:
        client = get_qdrant_client()
        qdrant_filter = _build_qdrant_filter(filters)

        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Qdrant similarity search failed.") from exc

    points = list(response.points)
    points.sort(key=lambda p: p.score, reverse=True)

    return [_format_search_result(p, active_fields) for p in points]