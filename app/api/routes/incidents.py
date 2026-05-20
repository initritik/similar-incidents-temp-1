# from typing import Any, Dict, List

# from fastapi import APIRouter, Query

# from app.schemas.incident import IncidentRecord, ReferenceField


# router = APIRouter()


# ASSIGNMENT_GROUPS = [
#     ("Network Operations", "287ebd7da9fe198100f92cc8d1d2154e"),
#     ("Email Support", "7f2a1c9e0b124af2a6e45018bcd401ab"),
#     ("Application Support", "5b3d7d3c0f9c4ce196b4c16dbf0f3119"),
#     ("Desktop Support", "0f61d3a12b5d48e7988fb9447f3e9ac2"),
#     ("Security Operations", "31a22fb02f2e4e2e9653ceaa1c79d18f"),
# ]

# INCIDENT_TEMPLATES = [
#     {
#         "short_description": "VPN users unable to connect",
#         "description": "Remote users report VPN authentication failures after password reset.",
#         "category": "network",
#         "subcategory": "vpn",
#         "priority": "2 - High",
#         "severity": "2 - Major",
#         "impact": "2 - Medium",
#         "urgency": "1 - High",
#     },
#     {
#         "short_description": "Email delivery delayed",
#         "description": "Users are receiving external email with delays greater than 30 minutes.",
#         "category": "software",
#         "subcategory": "email",
#         "priority": "3 - Moderate",
#         "severity": "3 - Minor",
#         "impact": "3 - Low",
#         "urgency": "2 - Medium",
#     },
#     {
#         "short_description": "Payroll application login error",
#         "description": "Employees see a 500 error when signing in to the payroll portal.",
#         "category": "application",
#         "subcategory": "authentication",
#         "priority": "1 - Critical",
#         "severity": "1 - Critical",
#         "impact": "1 - High",
#         "urgency": "1 - High",
#     },
#     {
#         "short_description": "Laptop disk encryption recovery required",
#         "description": "Corporate laptop repeatedly prompts for BitLocker recovery on boot.",
#         "category": "hardware",
#         "subcategory": "laptop",
#         "priority": "4 - Low",
#         "severity": "3 - Minor",
#         "impact": "3 - Low",
#         "urgency": "3 - Low",
#     },
#     {
#         "short_description": "Customer portal search returning no results",
#         "description": "Knowledge base search returns empty results for common support terms.",
#         "category": "application",
#         "subcategory": "portal",
#         "priority": "2 - High",
#         "severity": "2 - Major",
#         "impact": "2 - Medium",
#         "urgency": "2 - Medium",
#     },
#     {
#         "short_description": "Shared printer unavailable",
#         "description": "Users on the third floor cannot print to the shared office printer.",
#         "category": "hardware",
#         "subcategory": "printer",
#         "priority": "4 - Low",
#         "severity": "4 - Low",
#         "impact": "3 - Low",
#         "urgency": "3 - Low",
#     },
#     {
#         "short_description": "Suspicious sign-in alert",
#         "description": "Security monitoring detected repeated failed sign-ins from a new location.",
#         "category": "security",
#         "subcategory": "identity",
#         "priority": "2 - High",
#         "severity": "2 - Major",
#         "impact": "2 - Medium",
#         "urgency": "1 - High",
#     },
# ]

# STATES = [
#     ("1 - New", True),
#     ("2 - In Progress", True),
#     ("3 - On Hold", True),
#     ("6 - Resolved", False),
# ]


# def build_reference(table: str, sys_id: str) -> ReferenceField:
#     """Create a ServiceNow-style reference object for related records."""

#     return ReferenceField(
#         link=f"https://example.service-now.com/api/now/table/{table}/{sys_id}",
#         value=sys_id,
#     )


# def build_mock_incidents(total_records: int = 35) -> List[IncidentRecord]:
#     """Generate enough mock incidents to make pagination behavior visible."""

#     incidents = []

#     for index in range(total_records):
#         template = INCIDENT_TEMPLATES[index % len(INCIDENT_TEMPLATES)]
#         group_name, group_id = ASSIGNMENT_GROUPS[index % len(ASSIGNMENT_GROUPS)]
#         state, active = STATES[index % len(STATES)]
#         sequence = index + 1

#         incidents.append(
#             IncidentRecord(
#                 sys_id=f"{sequence:032x}",
#                 number=f"INC{sequence:07d}",
#                 short_description=f"{template['short_description']} - {group_name}",
#                 description=template["description"],
#                 category=template["category"],
#                 subcategory=template["subcategory"],
#                 priority=template["priority"],
#                 severity=template["severity"],
#                 state=state,
#                 incident_state=state,
#                 impact=template["impact"],
#                 urgency=template["urgency"],
#                 active=active,
#                 opened_at=f"2026-05-{(sequence % 15) + 1:02d} 09:{sequence % 60:02d}:00",
#                 sys_created_on=f"2026-05-{(sequence % 15) + 1:02d} 09:{sequence % 60:02d}:00",
#                 sys_updated_on=f"2026-05-{(sequence % 15) + 1:02d} 10:{sequence % 60:02d}:00",
#                 close_notes="Resolved and confirmed with caller." if not active else "",
#                 resolution_notes="Workaround applied and service restored." if not active else "",
#                 assignment_group=build_reference("sys_user_group", group_id),
#                 assigned_to=build_reference("sys_user", f"{sequence + 1000:032x}"),
#                 caller_id=build_reference("sys_user", f"{sequence + 2000:032x}"),
#                 cmdb_ci=build_reference("cmdb_ci", f"{sequence + 3000:032x}"),
#             )
#         )

#     return incidents


# # Mock data stays in memory for now. This replaces ServiceNow only while we are
# # developing the API shape; no database, vector search, embeddings, or AI layer
# # is involved here.
# MOCK_INCIDENTS = build_mock_incidents()


# @router.get("/incidents", response_model=Dict[str, Any])
# def get_incidents(
#     limit: int = Query(default=10, ge=1),
#     offset: int = Query(default=0, ge=0),
# ):
#     """Return paginated mock ServiceNow-style incidents."""

#     total_records = len(MOCK_INCIDENTS)
#     paginated_incidents = MOCK_INCIDENTS[offset : offset + limit]

#     # Pagination is critical in enterprise APIs because incident tables can
#     # contain thousands or millions of records. ServiceNow APIs handle large
#     # datasets with limit/offset-style batch retrieval so clients can process
#     # data safely in chunks instead of pulling everything at once.
#     #
#     # This same batch pattern matters before embeddings or vectorization later:
#     # records must be retrieved predictably in controlled pages before any
#     # downstream indexing pipeline can process them reliably.
#     return {
#         "result": paginated_incidents,
#         "pagination": {
#             "total_records": total_records,
#             "returned_records": len(paginated_incidents),
#             "limit": limit,
#             "offset": offset,
#             "has_more": offset + len(paginated_incidents) < total_records,
#         },
#     }


# claude code below

"""
Mock ServiceNow incident data and paginated list endpoint.

All incidents mimic the ServiceNow Table API response shape so swapping in a
real ServiceNow integration later only requires changing the data source, not
the downstream schema or services.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from app.schemas.incident import IncidentRecord, ReferenceField

router = APIRouter()

# ── Constants ────────────────────────────────────────────────────────────────

SERVICENOW_INSTANCE = "https://example.service-now.com"

ASSIGNMENT_GROUPS = [
    ("Network Operations", "287ebd7da9fe198100f92cc8d1d2154e"),
    ("Email Support", "7f2a1c9e0b124af2a6e45018bcd401ab"),
    ("Application Support", "5b3d7d3c0f9c4ce196b4c16dbf0f3119"),
    ("Desktop Support", "0f61d3a12b5d48e7988fb9447f3e9ac2"),
    ("Security Operations", "31a22fb02f2e4e2e9653ceaa1c79d18f"),
    ("Database Administration", "a9c3b12e4f7d11e8a56f23bc9d04e871"),
    ("Cloud Infrastructure", "bc4d27f15a9e22f7b67031cd8e15f982"),
]

INCIDENT_TEMPLATES = [
    {
        "short_description": "VPN users unable to connect after password reset",
        "description": (
            "Remote users report VPN authentication failures after a mandatory "
            "password reset. The Cisco AnyConnect client returns error 'Login "
            "failed' even with correct new credentials. Affects approximately "
            "40 remote workers across all departments."
        ),
        "category": "network",
        "subcategory": "vpn",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "2 - Medium",
        "urgency": "1 - High",
        "resolution_notes": (
            "Root cause: RADIUS server cached old password hashes. Fix: flushed "
            "RADIUS cache and restarted the authentication service. Users advised "
            "to wait 10 minutes after password change before reconnecting VPN."
        ),
        "close_notes": "Resolved and confirmed with affected users.",
        "group_key": "Network Operations",
    },
    {
        "short_description": "External email delivery delayed over 30 minutes",
        "description": (
            "Users are receiving external email with delays greater than 30 "
            "minutes. Internal email is unaffected. Exchange Online mail flow "
            "dashboard shows a spike in queued messages from 09:15 UTC. "
            "Marketing and Sales teams report missed customer replies."
        ),
        "category": "software",
        "subcategory": "email",
        "priority": "3 - Moderate",
        "severity": "3 - Minor",
        "impact": "3 - Low",
        "urgency": "2 - Medium",
        "resolution_notes": (
            "MX record TTL had propagated incorrectly after a DNS migration. "
            "Corrected MX record and cleared DNS caches on all mail relay nodes. "
            "Mail flow normalised within 15 minutes of change."
        ),
        "close_notes": "Mail flow restored. No data loss.",
        "group_key": "Email Support",
    },
    {
        "short_description": "Payroll application returns 500 error on login",
        "description": (
            "Employees see a 500 Internal Server Error when signing in to the "
            "payroll portal (pay.internal.corp). Error began at 08:00 UTC on "
            "payday. Approximately 600 employees cannot access pay slips. "
            "HR team reporting high call volume."
        ),
        "category": "application",
        "subcategory": "authentication",
        "priority": "1 - Critical",
        "severity": "1 - Critical",
        "impact": "1 - High",
        "urgency": "1 - High",
        "resolution_notes": (
            "Database connection pool exhausted due to a runaway reporting query "
            "scheduled overnight. Query was killed, connection pool restarted, "
            "and application recovered. Reporting job rescheduled to off-peak hours."
        ),
        "close_notes": "Portal restored. Payroll data intact.",
        "group_key": "Application Support",
    },
    {
        "short_description": "Laptop BitLocker recovery key prompted on every boot",
        "description": (
            "Corporate laptop repeatedly prompts for the BitLocker recovery key "
            "on every boot after a Windows Update last night. User is a senior "
            "analyst who stores client data locally. Productivity fully blocked."
        ),
        "category": "hardware",
        "subcategory": "laptop",
        "priority": "4 - Low",
        "severity": "3 - Minor",
        "impact": "3 - Low",
        "urgency": "3 - Low",
        "resolution_notes": (
            "TPM PCR values changed after BIOS update included in the Windows "
            "patch. Suspended BitLocker, applied patch, resumed protection. "
            "Recovery key prompt no longer appears."
        ),
        "close_notes": "BitLocker functioning normally after BIOS patch.",
        "group_key": "Desktop Support",
    },
    {
        "short_description": "Knowledge base search returns empty results",
        "description": (
            "Customer portal knowledge base search returns zero results for "
            "any query including known article titles. Elasticsearch index "
            "health shows red status. Began after last night's scheduled "
            "maintenance window."
        ),
        "category": "application",
        "subcategory": "portal",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "2 - Medium",
        "urgency": "2 - Medium",
        "resolution_notes": (
            "Elasticsearch index mapping was lost during a snapshot restore. "
            "Re-indexed all 12,000 knowledge articles from the source database. "
            "Search operational within 45 minutes. Added index health monitoring alert."
        ),
        "close_notes": "Search restored. Monitoring alert configured.",
        "group_key": "Application Support",
    },
    {
        "short_description": "Third floor shared printer offline",
        "description": (
            "Users on the third floor cannot print to the shared HP LaserJet Pro. "
            "Print jobs queue but never complete. Printer display shows Ready. "
            "Rebooting the printer did not help."
        ),
        "category": "hardware",
        "subcategory": "printer",
        "priority": "4 - Low",
        "severity": "4 - Low",
        "impact": "3 - Low",
        "urgency": "3 - Low",
        "resolution_notes": (
            "Print spooler service had crashed on the print server. Restarted "
            "spooler service and cleared the print queue. All queued jobs released."
        ),
        "close_notes": "Printer operational.",
        "group_key": "Desktop Support",
    },
    {
        "short_description": "Suspicious repeated failed sign-ins from unknown location",
        "description": (
            "Security monitoring detected 47 failed sign-in attempts for a user "
            "account from a Tor exit node IP over 20 minutes. Account not yet "
            "locked. User confirmed they are not travelling."
        ),
        "category": "security",
        "subcategory": "identity",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "2 - Medium",
        "urgency": "1 - High",
        "resolution_notes": (
            "Account locked, user notified, MFA reset completed, and conditional "
            "access policy updated to block Tor exit nodes. No successful login "
            "detected. SIEM alert tuned to auto-lock after 10 failures."
        ),
        "close_notes": "Account secured. Policy hardened.",
        "group_key": "Security Operations",
    },
    {
        "short_description": "Production database latency spike causing app timeouts",
        "description": (
            "Application response times spiked to over 10 seconds. Database "
            "monitoring shows average query time increased from 20ms to 4000ms. "
            "No schema changes deployed. Affects order processing and reporting modules."
        ),
        "category": "database",
        "subcategory": "performance",
        "priority": "1 - Critical",
        "severity": "1 - Critical",
        "impact": "1 - High",
        "urgency": "1 - High",
        "resolution_notes": (
            "Missing index on orders.customer_id detected after autovacuum ran "
            "and table statistics were reset. Re-created index concurrently. "
            "Query times returned to baseline within 5 minutes."
        ),
        "close_notes": "Performance restored. Index monitoring added.",
        "group_key": "Database Administration",
    },
    {
        "short_description": "AWS EC2 instance unreachable after security group change",
        "description": (
            "Production web server became unreachable after a security group "
            "rule was updated to restrict SSH. HTTP and HTTPS also stopped "
            "responding. Change was made without peer review."
        ),
        "category": "cloud",
        "subcategory": "access",
        "priority": "1 - Critical",
        "severity": "1 - Critical",
        "impact": "1 - High",
        "urgency": "1 - High",
        "resolution_notes": (
            "Reverted security group to previous version via AWS console. Instance "
            "became reachable immediately. Implemented change management policy "
            "requiring peer approval for production security group modifications."
        ),
        "close_notes": "Instance restored. Change control policy updated.",
        "group_key": "Cloud Infrastructure",
    },
    {
        "short_description": "MFA authenticator app not generating valid codes",
        "description": (
            "Several users report the Microsoft Authenticator app is not "
            "generating valid TOTP codes. Codes are always rejected at sign-in. "
            "Affects users who recently got new phones. Approximately 15 users "
            "locked out of corporate systems."
        ),
        "category": "security",
        "subcategory": "mfa",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "2 - Medium",
        "urgency": "1 - High",
        "resolution_notes": (
            "Device clock drift of over 30 seconds on new phones caused TOTP "
            "validation to fail. Instructed users to enable automatic time sync. "
            "Re-enrolled MFA for all 15 affected accounts."
        ),
        "close_notes": "MFA re-enrolled for all affected users.",
        "group_key": "Security Operations",
    },
    {
        "short_description": "SharePoint document library sync errors on all Macs",
        "description": (
            "All macOS users report OneDrive for Business showing sync errors "
            "for SharePoint document libraries. Windows users are unaffected. "
            "Error: Cannot connect to the server. Began after macOS 15.3 update."
        ),
        "category": "software",
        "subcategory": "collaboration",
        "priority": "3 - Moderate",
        "severity": "3 - Minor",
        "impact": "2 - Medium",
        "urgency": "2 - Medium",
        "resolution_notes": (
            "macOS 15.3 changed keychain access permissions for OneDrive tokens. "
            "Workaround: re-authenticate OneDrive and grant full disk access in "
            "System Settings. Reported to Microsoft; patch expected in next release."
        ),
        "close_notes": "Workaround applied to all 87 Mac users.",
        "group_key": "Desktop Support",
    },
    {
        "short_description": "ERP system slow during month-end reporting",
        "description": (
            "SAP ERP is responding in 30-60 seconds for standard transactions "
            "during the month-end financial close period. Normal response is "
            "under 3 seconds. Finance team unable to complete period-end reports "
            "on schedule."
        ),
        "category": "application",
        "subcategory": "performance",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "1 - High",
        "urgency": "1 - High",
        "resolution_notes": (
            "Month-end batch jobs competing with online users for database I/O. "
            "Rescheduled batch jobs to run between 22:00 and 06:00 UTC. "
            "Added read replica for reporting queries to offload the primary DB."
        ),
        "close_notes": "Batch schedule updated. Read replica provisioned.",
        "group_key": "Database Administration",
    },
    {
        "short_description": "SSL certificate expired on customer API gateway",
        "description": (
            "External partners and customers receiving SSL handshake errors when "
            "calling the REST API at api.corp.com. Certificate expired at "
            "00:00 UTC today. Alert was sent 30 days ago but renewal was not "
            "tracked. Estimated 200 API calls per hour failing."
        ),
        "category": "network",
        "subcategory": "ssl",
        "priority": "1 - Critical",
        "severity": "1 - Critical",
        "impact": "1 - High",
        "urgency": "1 - High",
        "resolution_notes": (
            "Renewed certificate from DigiCert and deployed to all API gateway "
            "nodes. Service restored in 12 minutes. Added certificate expiry "
            "monitoring with 60-day and 30-day alerts to PagerDuty."
        ),
        "close_notes": "Certificate renewed. Monitoring added.",
        "group_key": "Network Operations",
    },
    {
        "short_description": "CI/CD pipeline failing on all Python 3.12 builds",
        "description": (
            "All Jenkins pipeline jobs for Python services started failing after "
            "the base image was updated to python:3.12-slim. Error: "
            "ImportError: cannot import name X from deprecated module. "
            "18 microservices affected. Deployments blocked."
        ),
        "category": "application",
        "subcategory": "devops",
        "priority": "2 - High",
        "severity": "2 - Major",
        "impact": "2 - Medium",
        "urgency": "2 - Medium",
        "resolution_notes": (
            "Python 3.12 removed several deprecated stdlib modules used by "
            "third-party packages. Pinned base image to python:3.11-slim and "
            "opened tickets with package maintainers. Migration plan to 3.12 "
            "scheduled for next sprint."
        ),
        "close_notes": "Pipeline unblocked. 3.12 migration planned.",
        "group_key": "Cloud Infrastructure",
    },
    {
        "short_description": "Wi-Fi dropping on floor 2 near conference rooms",
        "description": (
            "Users on the second floor, particularly near the conference rooms, "
            "report frequent Wi-Fi disconnections every 10-15 minutes. VoIP "
            "calls dropping mid-meeting. Started after facilities installed new "
            "LED lighting panels last week."
        ),
        "category": "network",
        "subcategory": "wireless",
        "priority": "3 - Moderate",
        "severity": "3 - Minor",
        "impact": "2 - Medium",
        "urgency": "2 - Medium",
        "resolution_notes": (
            "New LED driver units emitting RF interference on 2.4GHz band. "
            "Changed affected access points to 5GHz only and adjusted channel "
            "plans. Interference eliminated."
        ),
        "close_notes": "Wi-Fi stable after channel change.",
        "group_key": "Network Operations",
    },
]

STATES = [
    ("6 - Resolved", False),
    ("6 - Resolved", False),
    ("6 - Resolved", False),
    ("2 - In Progress", True),
    ("1 - New", True),
]

GROUP_BY_NAME: Dict[str, tuple] = {name: (name, gid) for name, gid in ASSIGNMENT_GROUPS}


def build_reference(table: str, sys_id: str) -> ReferenceField:
    """Create a ServiceNow-style reference object for related records."""
    return ReferenceField(
        link=f"{SERVICENOW_INSTANCE}/api/now/table/{table}/{sys_id}",
        value=sys_id,
    )


def _make_date(days_ago: float, hour: int = 9, minute: int = 0) -> str:
    """Return a ServiceNow-style datetime string offset from today."""
    dt = datetime.utcnow() - timedelta(days=days_ago)
    return dt.replace(hour=hour, minute=minute, second=0, microsecond=0).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def build_mock_incidents(total_records: int = 50) -> List[IncidentRecord]:
    """
    Generate rich mock incidents spanning the past ~35 days to simulate
    one month of ServiceNow data with paginated retrieval.
    """
    incidents: List[IncidentRecord] = []

    for index in range(total_records):
        template = INCIDENT_TEMPLATES[index % len(INCIDENT_TEMPLATES)]
        state, active = STATES[index % len(STATES)]
        sequence = index + 1

        # Spread incidents across the past 35 days (oldest first)
        days_ago = 35.0 - (index * 35.0 / total_records)
        opened_at = _make_date(days_ago, hour=8 + (index % 10), minute=(index * 7) % 60)
        created_on = opened_at
        updated_on = _make_date(max(0.0, days_ago - 1), hour=10, minute=(index * 13) % 60)

        # Resolve assignment group from template preference
        group_key = template.get("group_key", ASSIGNMENT_GROUPS[index % len(ASSIGNMENT_GROUPS)][0])
        group_name, group_id = GROUP_BY_NAME.get(
            group_key,
            ASSIGNMENT_GROUPS[index % len(ASSIGNMENT_GROUPS)],
        )

        # Deterministic UUID so Qdrant point ids are stable across restarts
        sys_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"mock-incident-{sequence}"))

        # The ServiceNow deep link that users can click to open the incident
        servicenow_link = (
            f"{SERVICENOW_INSTANCE}/nav_to.do"
            f"?uri=incident.do%3Fsys_id%3D{sys_id.replace('-', '')}"
        )

        incidents.append(
            IncidentRecord(
                sys_id=sys_id,
                number=f"INC{sequence:07d}",
                short_description=template["short_description"],
                description=template["description"],
                category=template["category"],
                subcategory=template["subcategory"],
                priority=template["priority"],
                severity=template["severity"],
                state=state,
                incident_state=state,
                impact=template["impact"],
                urgency=template["urgency"],
                active=active,
                opened_at=opened_at,
                sys_created_on=created_on,
                sys_updated_on=updated_on,
                close_notes=template.get("close_notes", "") if not active else "",
                resolution_notes=template.get("resolution_notes", "") if not active else "",
                servicenow_link=servicenow_link,
                assignment_group=build_reference("sys_user_group", group_id),
                assigned_to=build_reference(
                    "sys_user",
                    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user-{sequence}")),
                ),
                caller_id=build_reference(
                    "sys_user",
                    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"caller-{sequence}")),
                ),
                cmdb_ci=build_reference(
                    "cmdb_ci",
                    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ci-{sequence}")),
                ),
            )
        )

    return incidents


# Built once at startup; serves as both the REST endpoint data source and the
# ingestion pipeline source so both always use the same records.
MOCK_INCIDENTS = build_mock_incidents()


@router.get("/incidents", response_model=Dict[str, Any])
def get_incidents(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated mock ServiceNow-style incidents."""

    total_records = len(MOCK_INCIDENTS)
    paginated_incidents = MOCK_INCIDENTS[offset : offset + limit]

    return {
        "result": paginated_incidents,
        "pagination": {
            "total_records": total_records,
            "returned_records": len(paginated_incidents),
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(paginated_incidents) < total_records,
        },
    }