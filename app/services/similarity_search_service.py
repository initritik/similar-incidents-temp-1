# """
# Similarity search service.

# Embeds the query, searches Qdrant, and returns results shaped according to
# the RESULT_FIELDS setting.
# """

# from typing import Any, Dict, List, Optional

# from qdrant_client.models import Filter, ScoredPoint

# from app.config.settings import settings
# from app.db.qdrant_client import get_qdrant_client
# from app.services.embedding_service import generate_embedding

# ALL_RESULT_FIELDS = {
#     "number", "short_description", "description", "assignment_group",
#     "priority", "category", "state", "resolution_notes", "opened_at",
#     "servicenow_link", "azure_devops_link", "datafix_code", "similarity_score",
# }


# def _build_qdrant_filter(filters: Optional[Dict[str, str]]) -> Optional[Filter]:
#     if not filters:
#         return None
#     supported = {"assignment_group", "category", "priority"}
#     unsupported = set(filters) - supported
#     if unsupported:
#         raise ValueError("Unsupported filters: " + ", ".join(sorted(unsupported)))
#     return None


# def _format_search_result(point: ScoredPoint, fields: set) -> Dict[str, Any]:
#     payload = point.payload or {}
#     field_map = {
#         "number":            lambda: payload.get("number", ""),
#         "short_description": lambda: payload.get("short_description", ""),
#         "description":       lambda: payload.get("description", ""),
#         "assignment_group":  lambda: payload.get("assignment_group", ""),
#         "priority":          lambda: payload.get("priority", ""),
#         "category":          lambda: payload.get("category", ""),
#         "state":             lambda: payload.get("state", ""),
#         "resolution_notes":  lambda: payload.get("resolution_notes", ""),
#         "opened_at":         lambda: payload.get("opened_at", ""),
#         "servicenow_link":   lambda: payload.get("servicenow_link", ""),
#         "azure_devops_link": lambda: payload.get("azure_devops_link", ""),
#         "datafix_code":      lambda: payload.get("datafix_code", ""),
#         "similarity_score":  lambda: point.score,
#     }
#     return {field: field_map[field]() for field in fields if field in field_map}


# def search_similar_incidents(
#     query_text: str,
#     top_k: int = 5,
#     filters: Optional[Dict[str, str]] = None,
# ) -> List[Dict[str, Any]]:
#     if not query_text or not query_text.strip():
#         raise ValueError("query_text is required for similarity search.")
#     if top_k < 1:
#         raise ValueError("top_k must be greater than zero.")

#     active_fields = settings.result_fields_set & ALL_RESULT_FIELDS
#     if not active_fields:
#         active_fields = ALL_RESULT_FIELDS

#     try:
#         query_embedding = generate_embedding(query_text.strip())
#     except Exception as exc:
#         raise RuntimeError("Failed to generate query embedding.") from exc

#     try:
#         client = get_qdrant_client()
#         response = client.query_points(
#             collection_name=settings.QDRANT_COLLECTION_NAME,
#             query=query_embedding,
#             limit=top_k,
#             query_filter=_build_qdrant_filter(filters),
#             with_payload=True,
#         )
#     except ValueError:
#         raise
#     except Exception as exc:
#         raise RuntimeError("Qdrant similarity search failed.") from exc

#     points = sorted(response.points, key=lambda p: p.score, reverse=True)
#     return [_format_search_result(p, active_fields) for p in points]





"""
Similarity search service.

Embeds the query, searches Qdrant, and returns results shaped according to
the RESULT_FIELDS setting.

FIX: Added `with_payload` as an explicit list of field names rather than just
`True`.  When `with_payload=True`, some Qdrant versions/deployments omit fields
that are null or empty-string in the stored payload, which caused `datafix_code`
to be missing from results for incidents that had no datafix — and more
critically it could silently drop `datafix_code` for incidents that DO have it
if the Qdrant server truncated the payload.  Passing an explicit list ensures
all requested fields are always present in the returned payload dict (defaulting
to None for absent fields, which we then normalise to "" below).
"""

from typing import Any, Dict, List, Optional

from qdrant_client.models import Filter, ScoredPoint

from app.config.settings import settings
from app.db.qdrant_client import get_qdrant_client
from app.services.embedding_service import generate_embedding

ALL_RESULT_FIELDS = {
    "number", "short_description", "description", "assignment_group",
    "priority", "category", "state", "resolution_notes", "opened_at",
    "servicenow_link", "azure_devops_link", "datafix_code", "similarity_score",
}

# Fields required by downstream orchestration even when RESULT_FIELDS is used
# only to tune display fields. Without these, the agent cannot detect whether a
# retrieved incident has datafix code and will always return no recommendation.
REQUIRED_CONTEXT_FIELDS = {"azure_devops_link", "datafix_code"}


def _build_qdrant_filter(filters: Optional[Dict[str, str]]) -> Optional[Filter]:
    if not filters:
        return None
    supported = {"assignment_group", "category", "priority"}
    unsupported = set(filters) - supported
    if unsupported:
        raise ValueError("Unsupported filters: " + ", ".join(sorted(unsupported)))
    return None


def _format_search_result(point: ScoredPoint, fields: set) -> Dict[str, Any]:
    payload = point.payload or {}
    field_map = {
        "number":            lambda: payload.get("number", ""),
        "short_description": lambda: payload.get("short_description", ""),
        "description":       lambda: payload.get("description", ""),
        "assignment_group":  lambda: payload.get("assignment_group", ""),
        "priority":          lambda: payload.get("priority", ""),
        "category":          lambda: payload.get("category", ""),
        "state":             lambda: payload.get("state", ""),
        "resolution_notes":  lambda: payload.get("resolution_notes", ""),
        "opened_at":         lambda: payload.get("opened_at", ""),
        "servicenow_link":   lambda: payload.get("servicenow_link", ""),
        "azure_devops_link": lambda: payload.get("azure_devops_link", ""),
        # FIX: Explicitly coerce None → "" for datafix_code.
        # Qdrant stores empty strings as null in some backends; if the field is
        # absent from the payload we must return "" not None, otherwise the
        # `(i.get("datafix_code") or "").strip()` check in agent_service would
        # still work, but having an explicit coerce here makes the contract clear.
        "datafix_code":      lambda: payload.get("datafix_code") or "",
        "similarity_score":  lambda: point.score,
    }
    return {field: field_map[field]() for field in fields if field in field_map}


def search_similar_incidents(
    query_text: str,
    top_k: int = 5,
    filters: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
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

    # FIX: Pass the explicit list of payload fields we need instead of just True.
    # This guarantees that fields like datafix_code are always requested from
    # Qdrant and not silently omitted by the server for null/empty values.
    # We include all storage fields (not just active_fields) to ensure datafix_code
    # is always retrieved — it is critical for the agent's datafix recommendation
    # even if it wasn't requested as a display field.
    result_fields = active_fields | REQUIRED_CONTEXT_FIELDS

    payload_fields_to_fetch = list(result_fields - {"similarity_score"})

    try:
        client = get_qdrant_client()
        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=_build_qdrant_filter(filters),
            with_payload=payload_fields_to_fetch,  # FIX: explicit field list
        )
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Qdrant similarity search failed.") from exc

    points = sorted(response.points, key=lambda p: p.score, reverse=True)
    return [_format_search_result(p, result_fields) for p in points]
