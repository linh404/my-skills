#!/usr/bin/env python3
"""Inventory Bruno .bru files without executing or modifying the collection."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
TOKEN_RE = re.compile(r"\{\{([^{}]+)\}\}")
FILE_RE = re.compile(r"(?:path|file|filename)\s*:\s*([^\s}]+)", re.I)


def block(text: str, header: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(header)}\s*\{{", text)
    if not match:
        return ""
    start = match.end()
    depth = 1
    i = start
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def first_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def classify(stem: str, method: str, url: str, text: str) -> tuple[str, str]:
    stem_value = stem.lower()
    value = f"{stem_value} {url}".lower()
    if stem_value in {"login", "sign_in", "signin", "authenticate"} or "/api/login" in value:
        return "auth", "session/authentication"
    if stem_value in {"forgot_password", "reset_password"}:
        return "mutate", "account recovery sends a stateful side effect"
    if stem_value in {"get_attendance_explanation_2", "get_hr_leave_details_2", "get_overtime_register_details_2"}:
        return "transient_preview", "wizard/transient computation despite get-like name"
    if "approval_progress" in stem_value or stem_value == "get_create_date_infor":
        return "read", "approval/metadata read despite workflow-like wording"
    # Check deletion before generic file/attachment keywords; delete_att_file
    # is a destructive operation, not an upload.
    if any(word in value for word in ("approve", "reject", "submit", "cancel", "draft", "approval")):
        return "workflow_transition", "state-changing workflow operation"
    if method == "delete" or any(word in value for word in ("delete", "remove")):
        return "delete", "record/file deletion"
    if any(word in value for word in ("upload", "attach", "attachment", "file")):
        return "upload", "file or attachment side effect"
    if any(word in value for word in ("create", "update", "write", "change", "set_", "signup", "sign_up")):
        return "mutate", "create/update or account mutation"
    if "googleapis" in value or "vietmap" in value or "external" in value:
        return "external_call", "external service call"
    if method == "get" or any(
        word in value
        for word in ("get_", "list_", "search", "detail", "details", "infor", "matrix", "report", "count", "total", "profile")
    ):
        return "read", "read/query candidate"
    return "unknown", "requires source inspection"


def inspect(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = block(text, "meta")
    method = "unknown"
    request_body = ""
    for candidate in METHODS:
        candidate_block = block(text, candidate)
        if candidate_block:
            method = candidate.upper()
            request_body = candidate_block
            break
    name = first_value(meta, "name") or path.stem
    url = first_value(request_body, "url") or ""
    auth = first_value(request_body, "auth") or ""
    body_kind = first_value(request_body, "body") or ""
    tokens = sorted(set(TOKEN_RE.findall(text)))
    files = sorted(set(FILE_RE.findall(text)))
    operation, reason = classify(path.stem, method.lower(), url, text)
    return {
        "path": path.relative_to(root).as_posix(),
        "name": name,
        "seq": first_value(meta, "seq"),
        "method": method,
        "url": url,
        "auth": auth,
        "body": body_kind,
        "variables": tokens,
        "file_references": files,
        "has_tests": bool(re.search(r"(?m)^\s*tests?\s*\{", text)),
        "has_scripts": bool(re.search(r"(?m)^\s*(script|script:)[^\n]*\{", text)),
        "operation": operation,
        "classification_reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", type=Path)
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = parser.parse_args()
    root = args.collection.resolve()
    if not root.is_dir():
        parser.error(f"collection directory not found: {root}")
    requests = []
    for path in sorted(root.rglob("*.bru")):
        if "environments" in path.relative_to(root).parts:
            continue
        requests.append(inspect(path, root))
    counts: dict[str, int] = {}
    for item in requests:
        counts[item["operation"]] = counts.get(item["operation"], 0) + 1
    result = {
        "collection": str(root),
        "request_count": len(requests),
        "operation_counts": dict(sorted(counts.items())),
        "requests": requests,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
