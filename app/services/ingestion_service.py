# from typing import Any, Dict, List

# from pydantic import ValidationError
# from qdrant_client.models import PointStruct

# from app.config.settings import settings
# from app.db.qdrant_client import create_collection_if_not_exists, get_qdrant_client
# from app.schemas.incident import IncidentRecord
# from app.services.embedding_service import generate_embedding
# from app.services.incident_normalizer import normalize_incident


# DEFAULT_BATCH_SIZE = 10


# def _to_incident_record(incident: Any) -> IncidentRecord:
#     """Validate incoming incident data against the existing incident schema."""

#     if isinstance(incident, IncidentRecord):
#         return incident

#     if isinstance(incident, dict):
#         return IncidentRecord.model_validate(incident)

#     raise TypeError("Incident must be an IncidentRecord or dictionary.")


# def _build_payload(incident: IncidentRecord, normalized: Dict[str, Any]) -> Dict[str, Any]:
#     """Build the metadata payload stored alongside the vector in Qdrant."""

#     metadata = normalized["metadata"]

#     # Embeddings are great for semantic similarity, but metadata is still needed
#     # for exact filtering, audit trails, permissions, and linking a result back
#     # to the original ServiceNow incident.
#     return {
#         "sys_id": metadata["sys_id"],
#         "number": metadata["number"],
#         "short_description": incident.short_description,
#         "description": incident.description,
#         "assignment_group": metadata["assignment_group"],
#         "priority": metadata["priority"],
#         "category": metadata["category"],
#         "state": metadata["state"],
#         "resolution_notes": incident.resolution_notes,
#         "opened_at": metadata["opened_at"],
#         "sys_created_on": metadata["sys_created_on"],
#     }


# def _batched(items: List[PointStruct], batch_size: int) -> list[List[PointStruct]]:
#     """Split Qdrant points into batches for safer bulk insertion."""

#     return [items[index : index + batch_size] for index in range(0, len(items), batch_size)]


# def ingest_incidents(incidents: list, batch_size: int = DEFAULT_BATCH_SIZE) -> Dict[str, int]:
#     """Normalize incidents, generate embeddings, and store them in Qdrant."""

#     if batch_size < 1:
#         raise ValueError("batch_size must be greater than zero.")

#     # Ingestion pipelines are critical in RAG systems because they transform
#     # source-system records into searchable knowledge. This is where raw
#     # ServiceNow data becomes clean text, embeddings, and metadata that a future
#     # retrieval layer can trust.
#     points: List[PointStruct] = []
#     summary = {
#         "received": len(incidents),
#         "prepared": 0,
#         "inserted": 0,
#         "skipped": 0,
#         "failed": 0,
#     }

#     for incident_data in incidents:
#         try:
#             incident = _to_incident_record(incident_data)

#             if not incident.sys_id:
#                 print("Skipped incident: missing sys_id.")
#                 summary["skipped"] += 1
#                 continue

#             normalized = normalize_incident(incident)

#             print(f"Generating embedding for incident {incident.number}.")
#             embedding = generate_embedding(normalized["text"])

#             payload = _build_payload(incident, normalized)

#             # The ServiceNow sys_id is used as the Qdrant point id so vector
#             # records can be updated deterministically when an incident changes.
#             points.append(
#                 PointStruct(
#                     id=incident.sys_id,
#                     vector=embedding,
#                     payload=payload,
#                 )
#             )
#             summary["prepared"] += 1
#         except (TypeError, ValidationError, ValueError) as exc:
#             print(f"Skipped invalid incident: {exc}")
#             summary["skipped"] += 1
#         except Exception as exc:
#             print(f"Failed to prepare incident embedding: {exc}")
#             summary["failed"] += 1

#     if not points:
#         print("No incident embeddings prepared for insertion.")
#         return summary

#     try:
#         create_collection_if_not_exists()
#         client = get_qdrant_client()
#     except Exception as exc:
#         print(f"Failed to initialize Qdrant collection: {exc}")
#         summary["failed"] += len(points)
#         return summary

#     # Batching matters in enterprise systems because datasets can be large.
#     # Controlled batches reduce memory pressure, make retries easier, and avoid
#     # sending one oversized request to the vector database.
#     for batch in _batched(points, batch_size):
#         try:
#             client.upsert(
#                 collection_name=settings.QDRANT_COLLECTION_NAME,
#                 points=batch,
#             )
#             summary["inserted"] += len(batch)
#             print(f"Successfully inserted {len(batch)} incident embeddings.")
#         except Exception as exc:
#             summary["failed"] += len(batch)
#             print(f"Failed to insert batch of {len(batch)} incident embeddings: {exc}")

#     return summary






# """
# Ingestion pipeline: normalise → embed → upsert into Qdrant.

# Sys-ids from the mock data are UUID strings, which Qdrant accepts natively
# as point ids (Qdrant supports both unsigned integers and UUID strings).
# """

# from typing import Any, Dict, List

# from pydantic import ValidationError
# from qdrant_client.models import PointStruct

# from app.config.settings import settings
# from app.db.qdrant_client import create_collection_if_not_exists, get_qdrant_client
# from app.schemas.incident import IncidentRecord
# from app.services.embedding_service import generate_embedding
# from app.services.incident_normalizer import normalize_incident


# DEFAULT_BATCH_SIZE = 10


# def _to_incident_record(incident: Any) -> IncidentRecord:
#     if isinstance(incident, IncidentRecord):
#         return incident
#     if isinstance(incident, dict):
#         return IncidentRecord.model_validate(incident)
#     raise TypeError("Incident must be an IncidentRecord or dictionary.")


# def _build_payload(incident: IncidentRecord, normalized: Dict[str, Any]) -> Dict[str, Any]:
#     metadata = normalized["metadata"]
#     return {
#         "sys_id": metadata["sys_id"],
#         "number": metadata["number"],
#         "short_description": incident.short_description,
#         "description": incident.description,
#         "assignment_group": metadata["assignment_group"],
#         "priority": metadata["priority"],
#         "category": metadata["category"],
#         "state": metadata["state"],
#         "resolution_notes": incident.resolution_notes,
#         "opened_at": metadata["opened_at"],
#         "sys_created_on": metadata["sys_created_on"],
#         # The ServiceNow deep-link stored in the vector payload so every
#         # search result can include a direct URL without an extra API call.
#         "servicenow_link": incident.servicenow_link,
#     }


# def _batched(items: List[PointStruct], batch_size: int) -> List[List[PointStruct]]:
#     return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


# def ingest_incidents(incidents: list, batch_size: int = DEFAULT_BATCH_SIZE) -> Dict[str, int]:
#     """Normalise incidents, generate embeddings, and store them in Qdrant."""

#     if batch_size < 1:
#         raise ValueError("batch_size must be greater than zero.")

#     points: List[PointStruct] = []
#     summary = {
#         "received": len(incidents),
#         "prepared": 0,
#         "inserted": 0,
#         "skipped": 0,
#         "failed": 0,
#     }

#     for incident_data in incidents:
#         try:
#             incident = _to_incident_record(incident_data)

#             if not incident.sys_id:
#                 print("Skipped incident: missing sys_id.")
#                 summary["skipped"] += 1
#                 continue

#             normalized = normalize_incident(incident)
#             print(f"Generating embedding for incident {incident.number}.")
#             embedding = generate_embedding(normalized["text"])
#             payload = _build_payload(incident, normalized)

#             # Qdrant accepts UUID strings directly as point ids.
#             points.append(
#                 PointStruct(
#                     id=incident.sys_id,
#                     vector=embedding,
#                     payload=payload,
#                 )
#             )
#             summary["prepared"] += 1

#         except (TypeError, ValidationError, ValueError) as exc:
#             print(f"Skipped invalid incident: {exc}")
#             summary["skipped"] += 1
#         except Exception as exc:
#             print(f"Failed to prepare incident embedding: {exc}")
#             summary["failed"] += 1

#     if not points:
#         print("No incident embeddings prepared for insertion.")
#         return summary

#     try:
#         create_collection_if_not_exists()
#         client = get_qdrant_client()
#     except Exception as exc:
#         print(f"Failed to initialise Qdrant collection: {exc}")
#         summary["failed"] += len(points)
#         return summary

#     for batch in _batched(points, batch_size):
#         try:
#             client.upsert(
#                 collection_name=settings.QDRANT_COLLECTION_NAME,
#                 points=batch,
#             )
#             summary["inserted"] += len(batch)
#             print(f"Successfully inserted {len(batch)} incident embeddings.")
#         except Exception as exc:
#             summary["failed"] += len(batch)
#             print(f"Failed to insert batch: {exc}")

#     return summary



"""
Ingestion pipeline: normalise → embed → upsert into Qdrant.

Sys-ids from the mock data are UUID strings, which Qdrant accepts natively
as point ids (Qdrant supports both unsigned integers and UUID strings).
"""

import time
from typing import Any, Dict, List

from pydantic import ValidationError
from qdrant_client.models import PointStruct

from app.config.settings import settings
from app.db.qdrant_client import create_collection_if_not_exists, get_qdrant_client
from app.schemas.incident import IncidentRecord
from app.services.embedding_service import generate_embedding
from app.services.incident_normalizer import normalize_incident


# Safe default for Qdrant Cloud free tier: each node has limited memory and
# short connection timeouts, so small batches with pauses between them are
# far more reliable than one large upsert.
DEFAULT_BATCH_SIZE = 5

# Seconds to wait between batches to avoid overwhelming the free-tier node.
INTER_BATCH_DELAY = 1.0

# Retry settings for transient Qdrant errors (timeouts, rate limits).
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3.0


def _to_incident_record(incident: Any) -> IncidentRecord:
    if isinstance(incident, IncidentRecord):
        return incident
    if isinstance(incident, dict):
        return IncidentRecord.model_validate(incident)
    raise TypeError("Incident must be an IncidentRecord or dictionary.")


def _build_payload(incident: IncidentRecord, normalized: Dict[str, Any]) -> Dict[str, Any]:
    metadata = normalized["metadata"]
    return {
        "sys_id": metadata["sys_id"],
        "number": metadata["number"],
        "short_description": incident.short_description,
        "description": incident.description,
        "assignment_group": metadata["assignment_group"],
        "priority": metadata["priority"],
        "category": metadata["category"],
        "state": metadata["state"],
        "resolution_notes": incident.resolution_notes,
        "opened_at": metadata["opened_at"],
        "sys_created_on": metadata["sys_created_on"],
        "servicenow_link": incident.servicenow_link,
    }


def _batched(items: List[PointStruct], batch_size: int) -> List[List[PointStruct]]:
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


def _upsert_with_retry(client, points: List[PointStruct], batch_num: int) -> None:
    """
    Upsert a batch of points, retrying on transient errors with backoff.

    Qdrant Cloud free-tier nodes time out under load. Retrying with
    increasing delays recovers from transient network or server-side hiccups
    without losing the whole batch.
    """
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=points,
            )
            return  # success
        except Exception as exc:
            last_exc = exc
            delay = RETRY_DELAY_SECONDS * attempt  # back off: 3s, 6s, 9s
            if attempt < MAX_RETRIES:
                print(
                    f"  Batch {batch_num} attempt {attempt}/{MAX_RETRIES} failed: {exc}. "
                    f"Retrying in {delay:.0f}s…"
                )
                time.sleep(delay)
            else:
                print(f"  Batch {batch_num} attempt {attempt}/{MAX_RETRIES} failed: {exc}. Giving up.")

    raise RuntimeError(f"Upsert failed after {MAX_RETRIES} attempts.") from last_exc


def ingest_incidents(incidents: list, batch_size: int = DEFAULT_BATCH_SIZE) -> Dict[str, int]:
    """Normalise incidents, generate embeddings, and store them in Qdrant."""

    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero.")

    points: List[PointStruct] = []
    summary = {
        "received": len(incidents),
        "prepared": 0,
        "inserted": 0,
        "skipped": 0,
        "failed": 0,
    }

    for incident_data in incidents:
        try:
            incident = _to_incident_record(incident_data)

            if not incident.sys_id:
                print("Skipped incident: missing sys_id.")
                summary["skipped"] += 1
                continue

            normalized = normalize_incident(incident)
            print(f"Generating embedding for incident {incident.number}.")
            embedding = generate_embedding(normalized["text"])
            payload = _build_payload(incident, normalized)

            points.append(
                PointStruct(
                    id=incident.sys_id,
                    vector=embedding,
                    payload=payload,
                )
            )
            summary["prepared"] += 1

        except (TypeError, ValidationError, ValueError) as exc:
            print(f"Skipped invalid incident: {exc}")
            summary["skipped"] += 1
        except Exception as exc:
            print(f"Failed to prepare incident embedding: {exc}")
            summary["failed"] += 1

    if not points:
        print("No incident embeddings prepared for insertion.")
        return summary

    try:
        create_collection_if_not_exists()
        client = get_qdrant_client()
    except Exception as exc:
        print(f"Failed to initialise Qdrant collection: {exc}")
        summary["failed"] += len(points)
        return summary

    batches = _batched(points, batch_size)
    print(f"Upserting {len(points)} points in {len(batches)} batch(es) of ≤{batch_size}…")

    for batch_num, batch in enumerate(batches, start=1):
        print(f"  Batch {batch_num}/{len(batches)}: {len(batch)} points…")
        try:
            _upsert_with_retry(client, batch, batch_num)
            summary["inserted"] += len(batch)
            print(f"  Batch {batch_num}/{len(batches)}: OK ({summary['inserted']} total inserted)")
        except Exception as exc:
            summary["failed"] += len(batch)
            print(f"  Batch {batch_num}/{len(batches)}: permanently failed — {exc}")

        # Pause between batches to stay within free-tier rate limits.
        # Skip the delay after the last batch.
        if batch_num < len(batches):
            time.sleep(INTER_BATCH_DELAY)

    return summary