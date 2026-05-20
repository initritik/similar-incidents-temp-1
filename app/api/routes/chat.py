# from typing import List, Optional

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field

# from app.schemas.incident import IncidentRecord
# from app.services.incident_fetch_service import fetch_incident_by_identifier
# from app.services.incident_parser_service import extract_incident_identifier
# from app.services.llm_response_service import generate_incident_response
# from app.services.similarity_search_service import search_similar_incidents


# router = APIRouter()


# class IncidentChatRequest(BaseModel):
#     """Request body for incident chat orchestration."""

#     user_query: Optional[str] = Field(default=None, min_length=1)
#     incident_link: Optional[str] = Field(default=None, min_length=1)
#     incident_number: Optional[str] = Field(default=None, min_length=1)
#     top_k: int = Field(default=5, ge=1)


# class IncidentChatResult(BaseModel):
#     """Raw retrieved incident returned alongside the AI answer."""

#     incident_number: str
#     short_description: str
#     description: str
#     assignment_group: str
#     priority: str
#     category: str
#     resolution_notes: str
#     similarity_score: float


# class IncidentChatResponse(BaseModel):
#     """Response body for the incident chat endpoint."""

#     status: str
#     user_query: str
#     results: List[IncidentChatResult]
#     answer: str


# def _reference_value(reference: object) -> str:
#     """Return a useful value from a ServiceNow reference object."""

#     if reference is None:
#         return ""

#     return getattr(reference, "value", "") or getattr(reference, "link", "")


# def _build_query_from_incident(incident: IncidentRecord) -> str:
#     """Build a consistent semantic search query from an incident record."""

#     # Backend query construction improves consistency because every incident
#     # link follows the same field selection strategy. That avoids each frontend
#     # client inventing slightly different prompts or missing important fields.
#     query_parts = [
#         incident.short_description,
#         incident.description,
#         incident.category,
#         _reference_value(incident.assignment_group),
#         incident.resolution_notes,
#     ]

#     query_text = "\n".join(part for part in query_parts if part)

#     if not query_text.strip():
#         raise ValueError("Fetched incident does not contain searchable text.")

#     return query_text


# def _resolve_chat_query(request: IncidentChatRequest) -> str:
#     """Resolve user text, incident number, or incident link into a search query."""

#     provided_inputs = [
#         bool(request.incident_link and request.incident_link.strip()),
#         bool(request.incident_number and request.incident_number.strip()),
#         bool(request.user_query and request.user_query.strip()),
#     ]

#     if sum(provided_inputs) > 1:
#         raise ValueError("Provide only one of user_query, incident_link, or incident_number.")

#     if request.incident_link:
#         identifier = extract_incident_identifier(request.incident_link)
#         incident = fetch_incident_by_identifier(identifier)
#         return _build_query_from_incident(incident)

#     if request.incident_number:
#         identifier = extract_incident_identifier(request.incident_number)
#         incident = fetch_incident_by_identifier(identifier)
#         return _build_query_from_incident(incident)

#     if request.user_query and request.user_query.strip():
#         return request.user_query.strip()

#     raise ValueError("Provide user_query, incident_link, or incident_number.")


# @router.post("/chat/incidents", response_model=IncidentChatResponse)
# def chat_about_incidents(request: IncidentChatRequest) -> IncidentChatResponse:
#     """Search similar incidents and format the answer with an LLM."""

#     # Orchestration should live in the backend because it coordinates protected
#     # systems: OpenAI, Qdrant, retrieval rules, validation, and response shape.
#     # The frontend should call one chat endpoint instead of chaining multiple
#     # services so the UI stays simple and the backend remains authoritative.
#     try:
#         # This mimics real ServiceNow assistant workflows: a support analyst can
#         # paste a ticket link or incident number, and the backend turns that
#         # incident into a consistent semantic search query automatically.
#         user_query = _resolve_chat_query(request)
#     except LookupError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc

#     try:
#         retrieved_incidents = search_similar_incidents(
#             query_text=user_query,
#             top_k=request.top_k,
#         )
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Similar incident search failed.",
#         ) from exc

#     try:
#         # This is the core chat pattern: retrieve grounded incident context
#         # first, then ask the LLM to format an answer from only that context.
#         answer = generate_incident_response(
#             user_query=user_query,
#             similar_incidents=retrieved_incidents,
#         )
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="LLM incident response generation failed.",
#         ) from exc

#     results = [
#         IncidentChatResult(
#             incident_number=result["number"],
#             short_description=result["short_description"],
#             description=result["description"],
#             assignment_group=result["assignment_group"],
#             priority=result["priority"],
#             category=result["category"],
#             resolution_notes=result["resolution_notes"],
#             similarity_score=result["similarity_score"],
#         )
#         for result in retrieved_incidents
#     ]

#     return IncidentChatResponse(
#         status="success",
#         user_query=user_query,
#         results=results,
#         answer=answer,
#     )







"""
Chat orchestration endpoint.

Resolves the user's input (free text, incident number, or incident URL)
into a search query, retrieves the top-k similar incidents from Qdrant,
then passes them to the LLM service to produce a human-readable answer.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.incident import IncidentRecord
from app.services.incident_fetch_service import fetch_incident_by_identifier
from app.services.incident_parser_service import extract_incident_identifier
from app.services.llm_response_service import generate_incident_response
from app.services.similarity_search_service import search_similar_incidents

router = APIRouter()


class IncidentChatRequest(BaseModel):
    user_query: Optional[str] = Field(default=None, min_length=1)
    incident_link: Optional[str] = Field(default=None, min_length=1)
    incident_number: Optional[str] = Field(default=None, min_length=1)
    top_k: int = Field(default=5, ge=1)


class IncidentChatResult(BaseModel):
    incident_number: str = ""
    short_description: str = ""
    description: str = ""
    assignment_group: str = ""
    priority: str = ""
    category: str = ""
    resolution_notes: str = ""
    servicenow_link: str = ""
    similarity_score: float = 0.0


class IncidentChatResponse(BaseModel):
    status: str
    user_query: str
    results: List[IncidentChatResult]
    answer: str


def _reference_value(reference: object) -> str:
    if reference is None:
        return ""
    return getattr(reference, "value", "") or getattr(reference, "link", "")


def _build_query_from_incident(incident: IncidentRecord) -> str:
    query_parts = [
        incident.short_description,
        incident.description,
        incident.category,
        _reference_value(incident.assignment_group),
        incident.resolution_notes,
    ]
    query_text = "\n".join(part for part in query_parts if part)

    if not query_text.strip():
        raise ValueError("Fetched incident does not contain searchable text.")

    return query_text


def _resolve_chat_query(request: IncidentChatRequest) -> str:
    provided_inputs = [
        bool(request.incident_link and request.incident_link.strip()),
        bool(request.incident_number and request.incident_number.strip()),
        bool(request.user_query and request.user_query.strip()),
    ]

    if sum(provided_inputs) > 1:
        raise ValueError(
            "Provide only one of user_query, incident_link, or incident_number."
        )

    if request.incident_link:
        identifier = extract_incident_identifier(request.incident_link)
        incident = fetch_incident_by_identifier(identifier)
        return _build_query_from_incident(incident)

    if request.incident_number:
        identifier = extract_incident_identifier(request.incident_number)
        incident = fetch_incident_by_identifier(identifier)
        return _build_query_from_incident(incident)

    if request.user_query and request.user_query.strip():
        return request.user_query.strip()

    raise ValueError("Provide user_query, incident_link, or incident_number.")


def _map_result(raw: Dict[str, Any]) -> IncidentChatResult:
    return IncidentChatResult(
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


@router.post("/chat/incidents", response_model=IncidentChatResponse)
def chat_about_incidents(request: IncidentChatRequest) -> IncidentChatResponse:
    """Search similar incidents and format the answer with an LLM."""

    try:
        user_query = _resolve_chat_query(request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        retrieved_incidents = search_similar_incidents(
            query_text=user_query,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Similar incident search failed.",
        ) from exc

    try:
        answer = generate_incident_response(
            user_query=user_query,
            similar_incidents=retrieved_incidents,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="LLM incident response generation failed.",
        ) from exc

    return IncidentChatResponse(
        status="success",
        user_query=user_query,
        results=[_map_result(r) for r in retrieved_incidents],
        answer=answer,
    )