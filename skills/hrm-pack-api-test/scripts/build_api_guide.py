#!/usr/bin/env python3
"""Build a static, source-backed execution guide for the KG HRM Bruno collection.

This is a build-time tool. It performs no HTTP calls and never edits the collection
or backend source. The generated plan is consumed by run_api_sequence.py.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from inventory_bru import inspect

MODEL_RE = re.compile(r"_(?:name|inherit)\s*=\s*['\"]([^'\"]+)['\"]")
DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", re.M)
ROUTE_JSON2_RE = re.compile(r"/json/2/([^/]+)/([^/\s}]+)")
ROUTE_GENERIC_RE = re.compile(r"/api/models/([^/]+)/([^/]+)/([^/\s}]+)")
ROUTE_EXEC_RE = re.compile(r"/api/models/([^/]+)/execute/([^/\s}]+)")
ROUTE_UPLOAD_RE = re.compile(r"/api/models/([^/]+)/upload_files/([^/\s}]+)")
KEY_RE = re.compile(r"[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']\s*:")
ID_RE = re.compile(r"[\"']([A-Za-z_][A-Za-z0-9_]*id)[\"']\s*:\s*(\d+)", re.I)
TOKEN_RE = re.compile(r"(?:bearer|cookie|token|authorization)\s*[:=].{0,100}", re.I)

REFERENCE_NAMES = {
    "get_infor_employee_division", "get_infor_employee_department", "get_infor_employee_group",
    "get_infor_job", "get_infor_job_title", "get_infor_calendar", "get_infor_area_category",
    "get_infor_departure_reason", "get_holiday_status_id_and_days", "get_overtime_holiday_status_id",
    "get_infor_explanation_reason", "get_infor_day_type", "get_infor_allocation",
}
CONTEXT_NAMES = {
    "get_employee_infor", "get_list_employee_infor", "get_contract_infor",
    "get_employee_profile_attachments", "get_employee_health_insurance",
    "get_employee_social_insurance", "get_employee_taxes", "get_org_chart",
}
READ_HINTS = ("get_", "list_", "search", "details", "detail", "report", "count", "total", "profile", "matrix", "v4")
DESTRUCTIVE_HINTS = ("delete", "remove", "cancel", "reject", "draft")
WORKFLOW_HINTS = ("approval", "submit", "accept", "approve", "reject", "cancel", "draft")

CONTROLLER_ROUTES = {
    "/api/login": {"source": "vdx_hr/controllers/user.py", "line": 13, "method": "mobile_login", "evidence": "SOURCE_VERIFIED"},
    "/app/signup/user": {"source": "vdx_hr/controllers/main.py", "line": 299, "method": "app_signup_user", "evidence": "SOURCE_VERIFIED"},
    "/app/forgot-password": {"source": "vdx_hr/controllers/main.py", "line": 384, "method": "app_forgot_password", "evidence": "SOURCE_VERIFIED"},
    "/api/update-device-token": {"source": "vdx_hr/controllers/fcm_token.py", "line": 46, "method": "update_device_token", "evidence": "SOURCE_VERIFIED"},
    "/api/app/login-logo": {"source": "vdx_hr/controllers/main.py", "line": 412, "method": "get_mobile_login_logo", "evidence": "SOURCE_VERIFIED"},
}

FLOW_SPECS = {
    "leave": {
        "match": ("HR Leave & Overtime/",),
        "order": [
            "get_holiday_status_id_and_days", "create_or_update_hr_leave", "get_hr_leave_details",
            "get_list_leaves", "app_approval_submit", "app_approval_accept",
            "app_approval_reject", "get_hr_leave_approval_progress",
        ],
        "constraints": ["employee context required", "holiday_status_id must exist", "quota/date validity enforced"],
    },
    "attendance_explanation": {
        "match": ("HR Attendance Explanation/",),
        "order": [
            "get_infor_explanation_reason", "get_infor_day_type", "get_infor_allocation",
            "create_or_update_explanation",
            "get_attendance_explanation_details", "app_approval_submit", "app_approval_accept",
            "app_approval_reject", "get_attendance_explanation_approval_progress",
        ],
        "constraints": ["employee/date/reason/calendar required", "unique employee/date", "time interval validation"],
    },
    "overtime": {
        "match": ("HR Leave & Overtime/",),
        "order": ["get_overtime_holiday_status_id", "create_or_update_overtime_register", "get_overtime_register_details", "app_approval_submit_2", "app_approval_accept_2", "app_approval_reject_2", "get_list_overtime_register"],
        "constraints": ["overtime dates must satisfy same-day source constraint"],
    },
    "resignation": {
        "match": ("Resignation Letter/",),
        "order": ["get_infor_departure_reason", "create_or_update_resignation_letter", "get_resignation_letter", "get_resignation_letter_details", "get_resignation_letter_approval_progress", "app_approval_submit", "app_approval_accept", "app_approval_reject"],
        "constraints": ["employee/resignation date/day-off/departure reason required", "employee.onboard_time must be configured before create", "duplicate active records rejected"],
    },
    "staff_transfer": {
        "match": ("Staff Transfer/",),
        "order": ["get_infor_area_category", "get_infor_job_title", "create_or_update_staff_transfer", "get_staff_transfer", "get_staff_transfer_details", "get_staff_transfer_approval_progress", "app_approval_submit", "app_approval_accept", "app_approval_reject"],
        "constraints": ["type/employee/effective date required", "duplicate employee/type/date rejected unless cancelled"],
    },
    "helpdesk": {
        "match": ("Helpdesk Ticket/",),
        "order": ["create_or_update_helpdesk_ticket", "get_helpdesk_ticket_details", "get_list_helpdesk_ticket"],
        "constraints": ["authenticated user must link to employee", "type is feedback or propose", "upload requires ticket res_id"],
    },
    "gps_attendance": {
        "match": ("HR Attendance/",),
        "order": ["app_get_address_from_coords", "create_attendance_gps", "get_attendance_today", "get_attendance_in_month", "get_attendance_for_one_employee", "get_attendance_violation_details", "get_attendance_violation_report", "upload_attendance_image"],
        "constraints": ["job.allow_gps_attendance must be true", "second create can toggle check-in/check-out"],
    },
}

# Runtime data dependencies are stronger than the collection's lexical order.
# They are injected into the generated graph so selecting a consumer request
# automatically includes the producer chain in the same Bruno process.  This
# deliberately lists only canonical requests; aliases remain deferred.
RUNTIME_PRODUCER_EDGES = {
    "leave": {
        "get_hr_leave_details": ["create_or_update_hr_leave"],
        "get_list_leaves": ["create_or_update_hr_leave"],
        "attach_files": ["create_or_update_hr_leave"],
        "app_approval_submit": ["create_or_update_hr_leave"],
        "app_approval_accept": ["create_or_update_hr_leave", "app_approval_submit"],
        "app_approval_reject": ["create_or_update_hr_leave", "app_approval_submit"],
        "get_hr_leave_approval_progress": ["create_or_update_hr_leave"],
        "app_approval_set_to_cancel": ["create_or_update_hr_leave", "app_approval_submit"],
        "app_approval_set_to_draft": ["create_or_update_hr_leave", "app_approval_submit"],
        "app_delete_hr_leave": ["create_or_update_hr_leave"],
        "delete_att_file": ["create_or_update_hr_leave", "attach_files", "app_approval_submit"],
    },
    "overtime": {
        "create_or_update_overtime_register": ["get_overtime_holiday_status_id", "get_employee_infor"],
        "get_overtime_register_details": ["create_or_update_overtime_register"],
        "app_delete_overtime_register": ["create_or_update_overtime_register"],
    },
    "attendance_explanation": {
        "create_or_update_explanation": [
            "get_infor_explanation_reason",
            "get_infor_day_type",
            "get_infor_allocation",
            "get_infor_calendar",
        ],
        "get_attendance_explanation_details": ["create_or_update_explanation"],
        "attach_files": ["create_or_update_explanation"],
        "app_approval_submit": ["create_or_update_explanation"],
        "app_approval_accept": ["create_or_update_explanation", "app_approval_submit"],
        "app_approval_reject": ["create_or_update_explanation", "app_approval_submit"],
        "get_attendance_explanation_approval_progress": ["create_or_update_explanation"],
        "app_cancel": ["create_or_update_explanation"],
        "app_draft": ["create_or_update_explanation", "app_approval_submit"],
        "app_delete_hr_attendance_explanation": ["create_or_update_explanation"],
        "delete_explanation_file": ["create_or_update_explanation", "attach_files"],
    },
    "helpdesk": {
        "get_helpdesk_ticket_details": ["create_or_update_helpdesk_ticket"],
        "get_list_helpdesk_ticket": ["create_or_update_helpdesk_ticket"],
        "attach_files": ["create_or_update_helpdesk_ticket"],
        "delete_att_file": ["create_or_update_helpdesk_ticket", "attach_files"],
    },
    "resignation": {
        "create_or_update_resignation_letter": ["update_employee_onboard_time"],
        "get_resignation_letter": ["create_or_update_resignation_letter"],
        "get_resignation_letter_details": ["create_or_update_resignation_letter"],
        "get_resignation_letter_approval_progress": ["create_or_update_resignation_letter"],
        "upload_attachment_file": ["create_or_update_resignation_letter"],
        "app_approval_submit": ["create_or_update_resignation_letter"],
        "app_approval_accept": ["create_or_update_resignation_letter", "app_approval_submit"],
        "app_approval_reject": ["create_or_update_resignation_letter", "app_approval_submit"],
        "app_btn_cancel": ["create_or_update_resignation_letter", "app_approval_submit"],
        "app_btn_to_draft": ["create_or_update_resignation_letter", "app_approval_submit"],
        "app_delete_resignation_letter": ["create_or_update_resignation_letter"],
        "delete_attachment_file": ["create_or_update_resignation_letter", "upload_attachment_file"],
    },
    "staff_transfer": {
        "get_staff_transfer": ["create_or_update_staff_transfer"],
        "get_staff_transfer_details": ["create_or_update_staff_transfer"],
        "get_staff_transfer_approval_progress": ["create_or_update_staff_transfer"],
        "app_approval_submit": ["create_or_update_staff_transfer"],
        "app_approval_accept": ["create_or_update_staff_transfer", "app_approval_submit"],
        "app_approval_reject": ["create_or_update_staff_transfer", "app_approval_submit"],
        "app_cancel": ["create_or_update_staff_transfer", "app_approval_submit"],
        "app_draft": ["create_or_update_staff_transfer", "app_approval_submit"],
        "app_delete_staff_transfer": ["create_or_update_staff_transfer"],
    },
    "read_only_reports": {
        "get_reward_discipline_details": ["get_list_reward_discipline"],
          },
    "employee_context": {
        "update_employee_onboard_time": ["get_employee_infor"],
        "change_avatar": ["get_employee_infor"],
        "upload_birth_certificate": ["get_employee_infor"],
        "delete_birth_certificate_file": ["get_employee_infor", "upload_birth_certificate"],
        "upload_citizen_id": ["get_employee_infor"],
        "delete_citizen_id_card_file": ["get_employee_infor", "upload_citizen_id"],
        "upload_curriculum_vitae": ["get_employee_infor"],
        "delete_curriculum_vitae_file": ["get_employee_infor", "upload_curriculum_vitae"],
        "upload_cv_file": ["get_employee_infor"],
        "delete_cv_file_file": ["get_employee_infor", "upload_cv_file"],
        "upload_diploma": ["get_employee_infor"],
        "delete_diploma_file": ["get_employee_infor", "upload_diploma"],
        "upload_employee_other_document": ["get_employee_infor"],
        "delete_employee_other_document_file": ["get_employee_infor", "upload_employee_other_document"],
        "upload_health_check": ["get_employee_infor"],
        "delete_health_check_file": ["get_employee_infor", "upload_health_check"],
        "upload_personnel_guarantee_letter": ["get_employee_infor"],
        "delete_personnel_guarantee_letter_file": ["get_employee_infor", "upload_personnel_guarantee_letter"],
        "upload_residence_certificate": ["get_employee_infor"],
        "delete_residence_certificate_file": ["get_employee_infor", "upload_residence_certificate"],
        "upload_staff_confirmation_letter": ["get_employee_infor"],
        "delete_staff_confirmation_letter_file": ["get_employee_infor", "upload_staff_confirmation_letter"],
    },
}

ALIAS_OF = {
    "app_approval_submit_2": "app_approval_submit",
    "app_approval_accept_2": "app_approval_accept",
    "app_approval_reject_2": "app_approval_reject",
    "app_approval_set_to_cancel_2": "app_approval_set_to_cancel",
    "app_approval_set_to_draft_2": "app_approval_set_to_draft",
    "get_hr_leave_approval_progress_2": "get_hr_leave_approval_progress",
    "create_or_update_staff_transfer_2": "create_or_update_staff_transfer",
}

KNOWN_FINDINGS = [
    {
        "id": "ACCEPTED-DB-BINDING",
        "severity": "info",
        "scope": "all DB-bound requests",
        "finding": "The login request selects the target database and establishes the Odoo session used by subsequent requests; this deployment does not require an X-Odoo-Database header.",
        "evidence": "vdx_hr/controllers/user.py:19-42; Odoo HTTP session DB resolution; environments/KG - local.bru",
        "action": "Keep --allow-db-binding as an operator confirmation; verify db_name and the persisted session target the intended database.",
    },
    {
        "id": "ACCEPTED-GENERIC-AUTH",
        "severity": "info",
        "scope": "/api/models/*",
        "finding": "Generic and upload routes intentionally use auth=\"user\"; they require the persisted Odoo session established by login, while the bearer token remains the API credential.",
        "evidence": "vdx_hr/controllers/main.py:87-92,134-139",
        "action": "Keep --allow-generic-session as an operator confirmation and verify the current session cookie before generic/upload requests.",
    },
    {
        "id": "ACCEPTED-MANUAL-FIXTURES",
        "severity": "medium",
        "scope": "create/update/upload/workflow/detail/delete flows",
        "finding": "The collection keeps operator-supplied numeric fixture IDs for requests outside the canonical create-to-detail chains; response scripts now chain IDs for the canonical HRM flows.",
        "evidence": "collection-wide static body scan; canonical create/upload response scripts",
        "action": "Verify every remaining fixture ID against the selected database and pass --allow-hardcoded-fixtures; do not treat standalone fixture requests as automatically chained.",
    },
    {
        "id": "RESOLVED-STALE-CREDENTIAL",
        "severity": "info",
        "scope": "Staff Transfer/create_or_update_staff_transfer_2.bru",
        "finding": "The non-default alias previously contained literal Authorization and Cookie headers; those overrides were removed and the request now uses Bruno's dynamic bearer/session handling.",
        "evidence": "Staff Transfer/create_or_update_staff_transfer_2.bru:7-20",
        "action": "Keep this alias excluded from default execution and use the canonical JSON-2 request; re-scan if the file changes.",
    },
    {
        "id": "RESOLVED-HELPDESK-DELETE-MISMATCH",
        "severity": "info",
        "scope": "Helpdesk Ticket/delete_att_file.bru",
        "finding": "Delete now checks ticket_attachment, matching the model field and the upload/detail paths.",
        "evidence": "vdx_hr_custom/models/helpdesk_ticket.py:39,131,252,278",
        "action": "No execution block; keep the targeted create-upload-delete verification in the validation record.",
    },
    {
        "id": "WARNING-FORGOT-PASSWORD-JSONRPC",
        "severity": "medium",
        "scope": "Authentication & System/forgot_password.bru",
        "finding": "Backend route is type=jsonrpc but collection body is not a JSON-RPC params wrapper.",
        "evidence": "vdx_hr/controllers/main.py:371; Authentication & System/forgot_password.bru:13",
        "action": "Do not include in normal smoke flow; fix payload/route contract separately.",
    },
    {
        "id": "WARNING-PUBLIC-ATTACHMENT",
        "severity": "high",
        "scope": "/recheck/image/<attachment_id>",
        "finding": "Public auth=none download uses sudo and comments out the public check.",
        "evidence": "vdx_hr/controllers/main.py:270-290",
        "action": "Do not use personal attachment IDs in tests.",
    },
]


def source_index(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    models: dict[str, dict[str, Any]] = {}
    methods: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in root.rglob("*.py"):
        if any(part in {".git", ".venv", "__pycache__", ".kilo"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        model_matches = list(MODEL_RE.finditer(text))
        defs = list(DEF_RE.finditer(text))
        for match in model_matches:
            model = match.group(1)
            line = text.count("\n", 0, match.start()) + 1
            entry = models.setdefault(model, {"model": model, "source": str(path), "line": line, "methods": {}})
            for d in defs:
                dline = text.count("\n", 0, d.start()) + 1
                entry["methods"].setdefault(d.group(1), {"source": str(path), "line": dline})
        for d in defs:
            line = text.count("\n", 0, d.start()) + 1
            methods[d.group(1)].append({"source": str(path), "line": line})
    return models, methods


def body_keys(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return sorted(set(KEY_RE.findall(text)) - {"args", "kwargs", "context"})


def route_info(url: str) -> tuple[str, str, str]:
    if match := ROUTE_JSON2_RE.search(url):
        return "json2", match.group(1), match.group(2)
    if match := ROUTE_UPLOAD_RE.search(url):
        return "upload", match.group(1).replace("-", "."), match.group(2)
    if match := ROUTE_EXEC_RE.search(url):
        return "generic", match.group(1).replace("-", "."), match.group(2)
    if url.startswith("http") and "{{base_url}}" not in url:
        return "external", "", ""
    return "custom", "", ""


def controller_info(url: str) -> dict[str, Any] | None:
    for prefix, info in CONTROLLER_ROUTES.items():
        if url.startswith("{{base_url}}" + prefix) or url.startswith(prefix):
            return dict(info)
    if "/recheck/image/" in url:
        return {"source": "vdx_hr/controllers/main.py", "line": 270, "method": "get_recheck_image", "evidence": "SOURCE_VERIFIED"}
    if "/employee/avatar/" in url:
        return {"source": "vdx_hr/controllers/employee.py", "line": 10, "method": "employee_avatar", "evidence": "SOURCE_VERIFIED"}
    return None


def flow_for(item: dict[str, Any]) -> str:
    path = item["path"]
    name = item["name"]
    if path.startswith("Authentication & System/"):
        return "authentication"
    if path.startswith("HR Contract & Job/") or path.startswith("Company & Users/"):
        return "reference_data"
    if path.startswith("HR Employee/"):
        return "employee_context"
    # Both leave and overtime requests live in the same Bruno folder.  Check
    # overtime first so runtime producer edges for overtime do not get
    # accidentally attached to the leave flow.
    if path.startswith("HR Leave & Overtime/") and "overtime" in name.lower():
        return "overtime"
    for flow, spec in FLOW_SPECS.items():
        if any(path.startswith(prefix) for prefix in spec["match"]):
            return flow
    if path.startswith("Reward & Discipline/") or path.startswith("Blog Post/"):
        return "read_only_reports"
    if path.startswith("External Services/") or path.startswith("Driver Attendance/"):
        return "external_services"
    return "other"


def operation(item: dict[str, Any], route_kind: str) -> str:
    name = item["name"].lower()
    if route_kind == "external":
        return "external_call"
    # Password-reset sends mail and is a stateful side effect even though the
    # collection inventory labels the public controller request as auth.
    if name == "forgot_password":
        return "mutate"
    if item["operation"] == "auth":
        return "auth"
    if name in {"get_attendance_explanation_2", "get_hr_leave_details_2", "get_overtime_register_details_2"}:
        return "transient_preview"
    if name in {"delete_att_file", "delete_explanation_file", "delete_attachment_file"}:
        return "delete"
    if name.startswith("get_") and "approval_progress" in name:
        return "read"
    if name.startswith("get_"):
        return "read"
    if item["operation"] in {"delete", "upload", "workflow_transition"}:
        return item["operation"]
    if any(h in name for h in WORKFLOW_HINTS):
        return "workflow_transition"
    if any(h in name for h in DESTRUCTIVE_HINTS):
        return "delete"
    if "create" in name or "update" in name or "change" in name or "signup" in name or name in {"sign_up", "forgot_password"}:
        return "mutate"
    if item["method"] == "GET" or any(name.startswith(h) or h in name for h in READ_HINTS):
        return "read"
    return "unknown"


def rank(item: dict[str, Any], flow: str, op: str) -> int:
    if flow == "authentication":
        return 10 if item["name"] == "login" else 20
    if flow == "external_services":
        return 35
    if flow == "reference_data":
        return 30
    if flow == "employee_context":
        return 40
    if op == "mutate":
        return 50
    if op == "transient_preview":
        return 45
    if op == "upload":
        return 60
    if op == "workflow_transition":
        return 70
    if op == "delete":
        return 90
    if op == "read":
        return 80
    return 85


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    collection = args.collection.resolve()
    source = args.source.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    docs = out / "docs"
    # The generated directory is a source-of-truth snapshot. Remove stale
    # per-request documents from a previous collection build so a deleted or
    # renamed request cannot survive unnoticed in the skill.
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir(parents=True, exist_ok=True)

    models, methods = source_index(source)
    requests = []
    unresolved = []
    for path in sorted(collection.rglob("*.bru")):
        if "environments" in path.relative_to(collection).parts:
            continue
        item = inspect(path, collection)
        kind, model, method = route_info(item["url"])
        controller = controller_info(item["url"])
        flow = flow_for(item)
        op = operation(item, kind)
        source_match = models.get(model)
        method_match = None
        if source_match:
            method_match = source_match["methods"].get(method)
        if not method_match and method and methods.get(method):
            method_match = methods[method][0]
        if controller:
            method = controller["method"]
            method_match = {"source": str(source / controller["source"]), "line": controller["line"]}
        evidence = "SOURCE_VERIFIED" if (controller or (source_match and method_match)) else ("COLLECTION_VERIFIED" if kind != "custom" else "UNKNOWN_NEEDS_MANUAL_CONFIRMATION")
        constraints = []
        if flow in FLOW_SPECS:
            constraints.extend(FLOW_SPECS[flow]["constraints"])
        hardcoded_ids = [{"field": key, "value": value} for key, value in ID_RE.findall(path.read_text(encoding="utf-8", errors="replace"))]
        risks = []
        if hardcoded_ids:
            risks.append("request contains hardcoded numeric ID; replace with isolated fixture ID before execution")
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        hardcoded_secret = bool(re.search(r"(?i)(?:authorization\s*:\s*bearer\s+)(?!\{\{)[A-Za-z0-9._-]{24,}|cookie\s*:\s*[^\n{}]{24,}", raw_text))
        if hardcoded_secret:
            risks.append("possible hardcoded auth/cookie material; inspect before execution")
        if op in {"mutate", "upload", "workflow_transition", "delete"}:
            risks.append("state-changing request; explicit execution approval required")
        node_id = item["path"]
        node = {
            "order": 0,
            "id": node_id,
            "flow": flow,
            "bruno_path": node_id,
            "name": item["name"],
            "method": item["method"],
            "url": item["url"],
            "route_kind": kind,
            "model": model or None,
            "backend_method": method or None,
            "source": method_match or (source_match or {}),
            "operation": op,
            "variables": item["variables"],
            "body_keys": body_keys(path),
            "hardcoded_ids": hardcoded_ids,
            "constraints": constraints,
            "risks": risks,
            "evidence": evidence,
            "depends_on": ["Authentication & System/login.bru"] if item["name"] != "login" and item["url"].startswith("{{base_url}}") and flow != "authentication" else [],
            "alias_of": ALIAS_OF.get(item["name"]),
            "default_execution": item["name"] not in ALIAS_OF,
        }
        if item["name"] == "login":
            node["captures"] = ["token"]
        elif op in {"mutate", "upload"}:
            node["captures"] = ["id", "res_id", "state"]
        else:
            node["captures"] = []
        requests.append(node)
        if evidence == "UNKNOWN_NEEDS_MANUAL_CONFIRMATION":
            unresolved.append({"request": node_id, "reason": "route not mapped to a known backend model/controller"})

    by_name = defaultdict(list)
    for node in requests:
        by_name[node["name"]].append(node)

    def add_edge(
        target_name: str,
        source_names: list[str],
        flow: str | None = None,
        *,
        allow_cross_flow: bool = False,
    ) -> None:
        targets = [n for n in by_name.get(target_name, []) if flow is None or n["flow"] == flow]
        for target in targets:
            for source_name in source_names:
                for source_node in by_name.get(source_name, []):
                    if (
                        allow_cross_flow
                        or flow is None
                        or source_node["flow"] == flow
                        or source_node["flow"] == "authentication"
                    ):
                        if source_node["id"] != target["id"] and source_node["id"] not in target["depends_on"]:
                            target["depends_on"].append(source_node["id"])

    for flow, spec in FLOW_SPECS.items():
        sequence = spec["order"]
        for before, after in zip(sequence, sequence[1:]):
            add_edge(after, [before], flow)
    # Add explicit runtime producer edges after the happy-path edges.  These
    # cover requests that are selected independently (detail, workflow,
    # attachment, and cleanup endpoints) and guarantee that their producer
    # runs first without treating aliases as producers.
    for flow, consumers in RUNTIME_PRODUCER_EDGES.items():
        for consumer, producers in consumers.items():
            # Most producer names are reused across business flows (for
            # example ``attach_files`` and ``app_approval_submit``).  Keep
            # those edges inside the consumer's flow; otherwise selecting one
            # request would pull unrelated mutations from every flow.  The
            # resignation onboard-date helper is the one intentional
            # cross-flow dependency because its producer lives in the shared
            # employee-context flow.
            allow_cross_flow = flow == "resignation" and "update_employee_onboard_time" in producers
            add_edge(consumer, producers, flow, allow_cross_flow=allow_cross_flow)
    # All protected project APIs require login; external services do not.
    for node in requests:
        if node["url"].startswith("{{base_url}}") and node["name"] != "login" and "Authentication & System" not in node["bruno_path"]:
            if "Authentication & System/login.bru" not in node["depends_on"]:
                node["depends_on"].append("Authentication & System/login.bru")
        node["depends_on"] = sorted(set(node["depends_on"]))

    # Stable topological order: dependencies always precede their dependents.
    node_by_id = {node["id"]: node for node in requests}
    indegree = {node["id"]: 0 for node in requests}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for node in requests:
        for dep in node["depends_on"]:
            if dep in node_by_id:
                indegree[node["id"]] += 1
                outgoing[dep].append(node["id"])
    ready = sorted(
        [node_id for node_id, degree in indegree.items() if degree == 0],
        key=lambda node_id: (rank(node_by_id[node_id], node_by_id[node_id]["flow"], node_by_id[node_id]["operation"]), node_id),
    )
    ordered_ids: list[str] = []
    while ready:
        current = ready.pop(0)
        ordered_ids.append(current)
        for child in sorted(outgoing.get(current, [])):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort(key=lambda node_id: (rank(node_by_id[node_id], node_by_id[node_id]["flow"], node_by_id[node_id]["operation"]), node_id))
    cycles = [node_id for node_id, degree in indegree.items() if degree > 0]
    if cycles:
        ordered_ids.extend(sorted(cycles))
        unresolved.append({"request": "<dependency-graph>", "reason": "cycle or unresolved dependency: " + ", ".join(cycles)})
    requests = [node_by_id[node_id] for node_id in ordered_ids]
    for index, node in enumerate(requests, 1):
        node["order"] = index

    graph = [{"from": dep, "to": node["id"], "evidence": node["evidence"]} for node in requests for dep in node["depends_on"]]
    constraints = [
        {"request": node["id"], "flow": node["flow"], "constraints": node["constraints"], "hardcoded_ids": node["hardcoded_ids"], "risks": node["risks"], "evidence": node["evidence"]}
        for node in requests if node["constraints"] or node["hardcoded_ids"] or node["risks"]
    ]
    constraints.extend(KNOWN_FINDINGS)
    plan = {
        "metadata": {
            "collection_root": str(collection),
            "source_root": str(source),
            "request_count": len(requests),
            "generated_by": "hrm-pack-api-test build_api_guide.py",
            "http_execution_performed": False,
            "evidence_policy": "source-backed where mapped; unknowns are not guessed",
        },
        "phases": [
            {"order": 1, "id": "authentication", "purpose": "login/session"},
            {"order": 2, "id": "reference_data", "purpose": "read existing reference values"},
            {"order": 3, "id": "employee_context", "purpose": "resolve current employee and contract context"},
            {"order": 4, "id": "business_flows", "purpose": "run one isolated domain flow at a time"},
            {"order": 5, "id": "verification", "purpose": "detail/list/report reads"},
        ],
        "nodes": requests,
    }
    (out / "api-execution-order.yaml").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "api-execution-order.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "api-dependency-graph.yaml").write_text(json.dumps({"edges": graph}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "api-constraints.yaml").write_text(json.dumps({"constraints": constraints, "known_findings": KNOWN_FINDINGS}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "api-unknowns.yaml").write_text(json.dumps({"unknowns": unresolved}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for node in requests:
        safe = re.sub(r"[^a-z0-9]+", "-", node["name"].lower()).strip("-") or "request"
        file = docs / f"{node['order']:03d}-{safe}.md"
        deps = "\n".join(f"- `{d}`" for d in node["depends_on"]) or "- none"
        source_text = "unknown"
        if node["source"].get("source"):
            source_text = f"`{node['source']['source']}:{node['source'].get('line', '?')}`"
        file.write_text(
            f"# {node['order']:03d}. {node['name']}\n\n"
            f"- Bruno: `{node['bruno_path']}`\n- Flow: `{node['flow']}`\n- Operation: `{node['operation']}`\n"
            f"- Endpoint: `{node['method']} {node['url']}`\n- Backend model: `{node['model'] or 'unresolved'}`\n"
            f"- Backend method: `{node['backend_method'] or 'unresolved'}`\n- Source: {source_text}\n"
            f"- Evidence: **{node['evidence']}**\n\n## Must run after\n{deps}\n\n"
            f"## Inputs\n{', '.join(f'`{x}`' for x in node['body_keys']) or 'Inspect request body'}\n\n"
            f"## Captures\n{', '.join(f'`{x}`' for x in node['captures']) or 'none declared'}\n\n"
            f"## Constraints and risks\n{chr(10).join('- ' + x for x in (node['constraints'] + node['risks'])) or '- none recorded'}\n",
            encoding="utf-8",
        )

    overview = out / "00-overview.md"
    counts = defaultdict(int)
    for node in requests:
        counts[node["flow"]] += 1
    overview.write_text(
        "# HRM Pack API execution guide\n\n"
        f"Generated from {len(requests)} executable Bruno requests and the current backend source.\n\n"
        "## Important\n\n"
        "This is a static build-time guide. The runner must execute one flow at a time, "
        "capture IDs/state, and require approval for mutations. Hardcoded IDs are warnings, not reusable fixtures.\n\n"
        "## Flow counts\n\n" + "\n".join(f"- `{k}`: {v}" for k, v in sorted(counts.items())) +
        "\n\n## Files\n\n- `api-execution-order.yaml` — total deterministic order and nodes.\n- `api-dependency-graph.yaml` — dependency edges.\n- `api-constraints.yaml` — source/collection constraints and risks.\n- `api-unknowns.yaml` — unresolved routes/mappings.\n- `docs/NNN-*.md` — one document per API in execution order.\n",
        encoding="utf-8",
    )
    print(json.dumps({"request_count": len(requests), "unknown_count": len(unresolved), "output": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
