# from typing import Optional

# from pydantic import BaseModel


# # Schemas define the shape of data that enters or leaves the application.
# # In enterprise systems, this creates a stable contract between our backend,
# # external platforms, frontend clients, tests, and future integration code.
# class ReferenceField(BaseModel):
#     """ServiceNow-style reference object."""

#     # ServiceNow often returns related records as reference objects instead of
#     # plain strings. The value is the related record sys_id, and the link points
#     # to the API resource that can be used to fetch the full related record.
#     link: str
#     value: str


# class IncidentRecord(BaseModel):
#     """ServiceNow-style incident record schema."""

#     # Core ServiceNow incident fields. Keeping names close to ServiceNow makes
#     # future API integration simpler because less mapping code is required.
#     sys_id: str
#     number: str
#     short_description: str
#     description: str
#     category: str
#     subcategory: str
#     priority: str
#     severity: str
#     state: str
#     incident_state: str
#     impact: str
#     urgency: str
#     active: bool
#     opened_at: str
#     sys_created_on: str
#     sys_updated_on: str
#     close_notes: str
#     resolution_notes: str

#     # Reference fields represent relationships to other ServiceNow records.
#     # Modeling them as nested schemas preserves both the sys_id and API link,
#     # which helps later when the backend needs to enrich, join, or trace data.
#     assignment_group: ReferenceField
#     assigned_to: Optional[ReferenceField] = None
#     caller_id: Optional[ReferenceField] = None
#     cmdb_ci: Optional[ReferenceField] = None


# class IncidentResponse(BaseModel):
#     """Outer ServiceNow response wrapper."""

#     # ServiceNow table APIs commonly wrap a single record inside a result key.
#     # Matching that structure makes this schema useful for real integrations
#     # without adding routes, mock data, vector databases, embeddings, or AI code.
#     result: IncidentRecord






from typing import Optional

from pydantic import BaseModel


class ReferenceField(BaseModel):
    """ServiceNow-style reference object."""
    link: str
    value: str


class IncidentRecord(BaseModel):
    """ServiceNow-style incident record schema."""

    sys_id: str
    number: str
    short_description: str
    description: str
    category: str
    subcategory: str
    priority: str
    severity: str
    state: str
    incident_state: str
    impact: str
    urgency: str
    active: bool
    opened_at: str
    sys_created_on: str
    sys_updated_on: str
    close_notes: str
    resolution_notes: str

    # Direct link to open this incident in the ServiceNow UI.
    # Stored alongside the vector so search results include a clickable link
    # without requiring a second lookup.
    servicenow_link: str = ""

    assignment_group: ReferenceField
    assigned_to: Optional[ReferenceField] = None
    caller_id: Optional[ReferenceField] = None
    cmdb_ci: Optional[ReferenceField] = None


class IncidentResponse(BaseModel):
    """Outer ServiceNow response wrapper."""
    result: IncidentRecord