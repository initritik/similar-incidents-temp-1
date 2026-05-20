# from typing import Any, Dict

# from fastapi import APIRouter, HTTPException, Query

# from app.api.routes.incidents import MOCK_INCIDENTS
# from app.services.ingestion_service import ingest_incidents


# router = APIRouter()


# @router.post("/ingest/incidents", response_model=Dict[str, Any])
# def ingest_mock_incidents(
#     limit: int = Query(default=10, ge=1),
#     offset: int = Query(default=0, ge=0),
# ):
#     """Trigger ingestion of paginated mock incidents into Qdrant."""

#     # In POCs, ingestion is often triggered by an API so developers can manually
#     # test sync behavior, inspect failures, and re-run small batches without
#     # setting up schedulers, workers, or production orchestration too early.
#     try:
#         fetched_incidents = MOCK_INCIDENTS[offset : offset + limit]
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to fetch mock incidents for ingestion.",
#         ) from exc

#     if not fetched_incidents:
#         return {
#             "status": "success",
#             "message": "No incidents found for the requested page",
#             "total_fetched": 0,
#             "total_ingested": 0,
#             "failed": 0,
#         }

#     try:
#         # This endpoint is useful during testing and manual sync because it
#         # exercises the full normalization, embedding, and Qdrant insertion path
#         # using a controlled slice of mock ServiceNow data.
#         summary = ingest_incidents(fetched_incidents)
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Incident ingestion failed.",
#         ) from exc

#     # In production, this kind of trigger would usually move behind a scheduled
#     # job, background task, message queue, or workflow runner. Keeping it as an
#     # explicit API for now makes the POC easy to test step by step.
#     failed_count = summary["failed"] + summary["skipped"]

#     if failed_count > 0:
#         return {
#             "status": "partial_success",
#             "message": "Incident ingestion completed with failures",
#             "total_fetched": len(fetched_incidents),
#             "total_ingested": summary["inserted"],
#             "failed": failed_count,
#         }

#     return {
#         "status": "success",
#         "message": "Incidents ingested successfully",
#         "total_fetched": len(fetched_incidents),
#         "total_ingested": summary["inserted"],
#         "failed": failed_count,
#     }


# """
# Ingestion routes.

# /ingest/incidents  – paginated ingestion (existing behaviour)
# /ingest/all        – ingest every mock incident in one call, iterating all pages
# """

# from typing import Any, Dict

# from fastapi import APIRouter, HTTPException, Query

# from app.api.routes.incidents import MOCK_INCIDENTS
# from app.services.ingestion_service import ingest_incidents

# router = APIRouter()

# DEFAULT_INGEST_BATCH = 10


# @router.post("/ingest/incidents", response_model=Dict[str, Any])
# def ingest_mock_incidents(
#     limit: int = Query(default=10, ge=1),
#     offset: int = Query(default=0, ge=0),
# ):
#     """Trigger ingestion of a paginated slice of mock incidents into Qdrant."""

#     try:
#         fetched_incidents = MOCK_INCIDENTS[offset : offset + limit]
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to fetch mock incidents for ingestion.",
#         ) from exc

#     if not fetched_incidents:
#         return {
#             "status": "success",
#             "message": "No incidents found for the requested page",
#             "total_fetched": 0,
#             "total_ingested": 0,
#             "failed": 0,
#         }

#     try:
#         summary = ingest_incidents(fetched_incidents)
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail="Incident ingestion failed.",
#         ) from exc

#     failed_count = summary["failed"] + summary["skipped"]

#     if failed_count > 0:
#         return {
#             "status": "partial_success",
#             "message": "Incident ingestion completed with failures",
#             "total_fetched": len(fetched_incidents),
#             "total_ingested": summary["inserted"],
#             "failed": failed_count,
#         }

#     return {
#         "status": "success",
#         "message": "Incidents ingested successfully",
#         "total_fetched": len(fetched_incidents),
#         "total_ingested": summary["inserted"],
#         "failed": failed_count,
#     }


# @router.post("/ingest/all", response_model=Dict[str, Any])
# def ingest_all_mock_incidents(
#     batch_size: int = Query(default=DEFAULT_INGEST_BATCH, ge=1, le=50),
# ):
#     """
#     Ingest every mock incident into Qdrant in one API call.

#     Iterates all records in batches without requiring the caller to manage
#     pagination.  This mirrors how a production scheduler would pull all
#     incidents from the past month and push them through the embedding pipeline.
#     """
#     all_incidents = MOCK_INCIDENTS

#     if not all_incidents:
#         return {
#             "status": "success",
#             "message": "No mock incidents to ingest",
#             "total_fetched": 0,
#             "total_ingested": 0,
#             "failed": 0,
#         }

#     try:
#         summary = ingest_incidents(all_incidents, batch_size=batch_size)
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Full ingestion failed: {exc}",
#         ) from exc

#     failed_count = summary["failed"] + summary["skipped"]
#     status = "partial_success" if failed_count > 0 else "success"

#     return {
#         "status": status,
#         "message": (
#             f"Ingested {summary['inserted']} of {summary['received']} incidents."
#             + (f" {failed_count} failed or skipped." if failed_count else "")
#         ),
#         "total_fetched": summary["received"],
#         "total_ingested": summary["inserted"],
#         "failed": failed_count,
#     }



"""
Ingestion routes.

/ingest/incidents  – paginated ingestion (one page at a time)
/ingest/all        – ingest every mock incident, iterating all pages automatically
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from app.api.routes.incidents import MOCK_INCIDENTS
from app.services.ingestion_service import DEFAULT_BATCH_SIZE, ingest_incidents

router = APIRouter()

# Hard cap for the free-tier Qdrant Cloud node. Sending more than ~5-10 points
# per upsert call on the free tier frequently times out. The ingestion service
# already adds inter-batch delays, so keeping batches small is the right trade.
MAX_BATCH_SIZE = 10


@router.post("/ingest/incidents", response_model=Dict[str, Any])
def ingest_mock_incidents(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    batch_size: int = Query(default=DEFAULT_BATCH_SIZE, ge=1, le=MAX_BATCH_SIZE),
):
    """Trigger ingestion of a paginated slice of mock incidents into Qdrant."""

    try:
        fetched_incidents = MOCK_INCIDENTS[offset : offset + limit]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch mock incidents for ingestion.",
        ) from exc

    if not fetched_incidents:
        return {
            "status": "success",
            "message": "No incidents found for the requested page",
            "total_fetched": 0,
            "total_ingested": 0,
            "failed": 0,
        }

    try:
        summary = ingest_incidents(fetched_incidents, batch_size=batch_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Incident ingestion failed.") from exc

    failed_count = summary["failed"] + summary["skipped"]
    status = "partial_success" if failed_count > 0 else "success"
    message = "Incidents ingested successfully" if not failed_count else "Incident ingestion completed with failures"

    return {
        "status": status,
        "message": message,
        "total_fetched": len(fetched_incidents),
        "total_ingested": summary["inserted"],
        "failed": failed_count,
    }


@router.post("/ingest/all", response_model=Dict[str, Any])
def ingest_all_mock_incidents(
    batch_size: int = Query(default=DEFAULT_BATCH_SIZE, ge=1, le=MAX_BATCH_SIZE),
):
    """
    Ingest every mock incident into Qdrant in one API call.

    Iterates all records in small batches with inter-batch delays to stay
    within Qdrant Cloud free-tier limits. This mirrors how a production
    scheduler would pull incidents from the past month and push them through
    the embedding pipeline without overwhelming the vector database.

    Default batch_size is 5. Maximum is 10. If you see timeouts, reduce
    batch_size further (e.g. ?batch_size=3).
    """
    all_incidents = MOCK_INCIDENTS

    if not all_incidents:
        return {
            "status": "success",
            "message": "No mock incidents to ingest",
            "total_fetched": 0,
            "total_ingested": 0,
            "failed": 0,
        }

    try:
        summary = ingest_incidents(all_incidents, batch_size=batch_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Full ingestion failed: {exc}",
        ) from exc

    failed_count = summary["failed"] + summary["skipped"]
    status = "partial_success" if failed_count > 0 else "success"

    return {
        "status": status,
        "message": (
            f"Ingested {summary['inserted']} of {summary['received']} incidents."
            + (f" {failed_count} failed or skipped." if failed_count else "")
        ),
        "total_fetched": summary["received"],
        "total_ingested": summary["inserted"],
        "failed": failed_count,
    }