# from typing import List

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field

# from app.services.similarity_search_service import search_similar_incidents


# router = APIRouter()


# class SimilarIncidentSearchRequest(BaseModel):
#     """Request body for semantic incident search."""

#     query_text: str = Field(..., min_length=1)
#     top_k: int = Field(default=5, ge=1)


# class SimilarIncidentResult(BaseModel):
#     """Single similar incident returned by the search API."""

#     incident_number: str
#     short_description: str
#     description: str
#     assignment_group: str
#     priority: str
#     category: str
#     resolution_notes: str
#     similarity_score: float


# class SimilarIncidentSearchResponse(BaseModel):
#     """Response body for semantic incident search."""

#     status: str
#     query_text: str
#     results: List[SimilarIncidentResult]


# @router.post(
#     "/search/similar-incidents",
#     response_model=SimilarIncidentSearchResponse,
# )
# def search_similar_incidents_endpoint(
#     request: SimilarIncidentSearchRequest,
# ) -> SimilarIncidentSearchResponse:
#     """Search Qdrant for incidents semantically similar to the query."""

#     # The frontend should call this backend API instead of Qdrant directly
#     # because the backend owns secrets, embedding generation, retrieval rules,
#     # validation, and response shaping. That keeps infrastructure details out of
#     # the browser and gives us one controlled place to evolve search behavior.
#     query_text = request.query_text.strip()

#     if not query_text:
#         raise HTTPException(status_code=400, detail="query_text cannot be empty.")

#     try:
#         # The backend should own embedding and retrieval logic because clients
#         # should not need to know which embedding model, vector database, filters,
#         # or ranking strategy the platform uses.
#         service_results = search_similar_incidents(
#             query_text=query_text,
#             top_k=request.top_k,
#         )
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Similar incident search failed.",
#         ) from exc

#     # This endpoint becomes the core retrieval service for a later chat UI: the
#     # chat layer can call it first, then use the returned incident context before
#     # any answer generation or summarization is added.
#     results = [
#         SimilarIncidentResult(
#             incident_number=result["number"],
#             short_description=result["short_description"],
#             description=result["description"],
#             assignment_group=result["assignment_group"],
#             priority=result["priority"],
#             category=result["category"],
#             resolution_notes=result["resolution_notes"],
#             similarity_score=result["similarity_score"],
#         )
#         for result in service_results
#     ]

#     return SimilarIncidentSearchResponse(
#         status="success",
#         query_text=query_text,
#         results=results,
#     )




"""
Semantic similarity search endpoint.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.similarity_search_service import search_similar_incidents

router = APIRouter()


class SimilarIncidentSearchRequest(BaseModel):
    query_text: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1)


class SimilarIncidentResult(BaseModel):
    incident_number: str = ""
    short_description: str = ""
    description: str = ""
    assignment_group: str = ""
    priority: str = ""
    category: str = ""
    resolution_notes: str = ""
    servicenow_link: str = ""
    similarity_score: float = 0.0


class SimilarIncidentSearchResponse(BaseModel):
    status: str
    query_text: str
    results: List[SimilarIncidentResult]


def _map_result(raw: Dict[str, Any]) -> SimilarIncidentResult:
    return SimilarIncidentResult(
        incident_number=raw.get("number", ""),
        short_description=raw.get("short_description", ""),
        description=raw.get("description", ""),
        assignment_group=raw.get("assignment_group", ""),
        priority=raw.get("priority", ""),
        category=raw.get("category", ""),
        resolution_notes=raw.get("resolution_notes", ""),
        servicenow_link=raw.get("servicenow_link", ""),
        similarity_score=raw.get("similarity_score", 0.0),
    )


@router.post(
    "/search/similar-incidents",
    response_model=SimilarIncidentSearchResponse,
)
def search_similar_incidents_endpoint(
    request: SimilarIncidentSearchRequest,
) -> SimilarIncidentSearchResponse:
    """Search Qdrant for incidents semantically similar to the query."""

    query_text = request.query_text.strip()

    if not query_text:
        raise HTTPException(status_code=400, detail="query_text cannot be empty.")

    try:
        service_results = search_similar_incidents(
            query_text=query_text,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Similar incident search failed.",
        ) from exc

    return SimilarIncidentSearchResponse(
        status="success",
        query_text=query_text,
        results=[_map_result(r) for r in service_results],
    )
