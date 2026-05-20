# from typing import Any, Dict, Optional

# from app.schemas.incident import IncidentRecord, ReferenceField


# def _reference_value(reference: Optional[ReferenceField]) -> str:
#     """Return the best stable identifier from a ServiceNow reference field."""

#     if reference is None:
#         return ""

#     # ServiceNow reference objects include both a value and a link. The value is
#     # usually the referenced record sys_id, which is a stable identifier for
#     # metadata, filtering, and later API lookups.
#     return reference.value or reference.link


# def _add_line(lines: list[str], label: str, value: Any) -> None:
#     """Append a labeled text line only when the value is present."""

#     if value:
#         lines.append(f"{label}: {value}")


# def normalize_incident(incident: IncidentRecord) -> Dict[str, Any]:
#     """Convert a ServiceNow-style incident into embedding-ready text."""

#     # A normalization layer is needed before embeddings because raw enterprise
#     # records often contain nested objects, inconsistent field ordering, and
#     # optional values. Embeddings work better when similar records are converted
#     # into clean, predictable text with the same labels and structure each time.
#     lines: list[str] = []

#     _add_line(lines, "Incident Number", incident.number)
#     _add_line(lines, "Short Description", incident.short_description)
#     _add_line(lines, "Description", incident.description)
#     _add_line(lines, "Category", incident.category)
#     _add_line(lines, "Subcategory", incident.subcategory)
#     _add_line(lines, "Priority", incident.priority)
#     _add_line(lines, "Severity", incident.severity)
#     _add_line(lines, "State", incident.state)
#     _add_line(lines, "Incident State", incident.incident_state)
#     _add_line(lines, "Impact", incident.impact)
#     _add_line(lines, "Urgency", incident.urgency)
#     _add_line(lines, "Assignment Group", _reference_value(incident.assignment_group))
#     _add_line(lines, "Assigned To", _reference_value(incident.assigned_to))
#     _add_line(lines, "Caller", _reference_value(incident.caller_id))
#     _add_line(lines, "Configuration Item", _reference_value(incident.cmdb_ci))
#     _add_line(lines, "Close Notes", incident.close_notes)
#     _add_line(lines, "Resolution Notes", incident.resolution_notes)

#     # Keep structured metadata separate from embedding text. The text is for
#     # semantic search quality, while metadata is for exact filtering, tracing,
#     # access control, debugging, and linking results back to source systems.
#     metadata = {
#         "sys_id": incident.sys_id,
#         "number": incident.number,
#         "assignment_group": _reference_value(incident.assignment_group),
#         "priority": incident.priority,
#         "category": incident.category,
#         "state": incident.state,
#         "opened_at": incident.opened_at,
#         "sys_created_on": incident.sys_created_on,
#     }

#     # Returning both keeps the future vectorization step simple: embed the clean
#     # text, but store metadata alongside the vector for enterprise retrieval.
#     return {
#         "text": "\n".join(lines),
#         "metadata": metadata,
#     }






"""
Incident normaliser: converts a ServiceNow record into embedding-ready text
and a structured metadata dict.
"""

from typing import Any, Dict, Optional

from app.schemas.incident import IncidentRecord, ReferenceField


def _reference_value(reference: Optional[ReferenceField]) -> str:
    if reference is None:
        return ""
    return reference.value or reference.link


def _add_line(lines: list, label: str, value: Any) -> None:
    if value:
        lines.append(f"{label}: {value}")


def normalize_incident(incident: IncidentRecord) -> Dict[str, Any]:
    """Convert a ServiceNow-style incident into embedding-ready text + metadata."""

    lines: list = []

    _add_line(lines, "Incident Number", incident.number)
    _add_line(lines, "Short Description", incident.short_description)
    _add_line(lines, "Description", incident.description)
    _add_line(lines, "Category", incident.category)
    _add_line(lines, "Subcategory", incident.subcategory)
    _add_line(lines, "Priority", incident.priority)
    _add_line(lines, "Severity", incident.severity)
    _add_line(lines, "State", incident.state)
    _add_line(lines, "Incident State", incident.incident_state)
    _add_line(lines, "Impact", incident.impact)
    _add_line(lines, "Urgency", incident.urgency)
    _add_line(lines, "Assignment Group", _reference_value(incident.assignment_group))
    _add_line(lines, "Assigned To", _reference_value(incident.assigned_to))
    _add_line(lines, "Caller", _reference_value(incident.caller_id))
    _add_line(lines, "Configuration Item", _reference_value(incident.cmdb_ci))
    _add_line(lines, "Close Notes", incident.close_notes)
    _add_line(lines, "Resolution Notes", incident.resolution_notes)

    metadata = {
        "sys_id": incident.sys_id,
        "number": incident.number,
        "assignment_group": _reference_value(incident.assignment_group),
        "priority": incident.priority,
        "category": incident.category,
        "state": incident.state,
        "opened_at": incident.opened_at,
        "sys_created_on": incident.sys_created_on,
        "servicenow_link": incident.servicenow_link,
    }

    return {
        "text": "\n".join(lines),
        "metadata": metadata,
    }