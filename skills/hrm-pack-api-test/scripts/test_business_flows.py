#!/usr/bin/env python3
"""Run the HRM API collection as isolated, dependency-ordered business flows.

The business manifest is intentionally separate from the generated API graph:
the graph describes every endpoint, while this runner selects one reviewed
happy path (and an optional approval/rejection variant) per HRM nghiệp vụ.
Each business is run in its own Bruno process so cookies and runtime variables
cannot leak between unrelated transactions.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
DEFAULT_MANIFEST = SKILL_ROOT / "references" / "business-test-plan.yaml"
DEFAULT_PLAN = SKILL_ROOT / "references" / "generated" / "api-execution-order.json"
DEFAULT_COLLECTION = Path("/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection")
SECRETS_RE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._-]{16,}|(cookie\s*:\s*)[^\n]+|"
    r"((?:token|password|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+"
)


def sanitize(text: str) -> str:
    return SECRETS_RE.sub(
        lambda match: (match.group(1) or match.group(2) or match.group(3) or "") + "<redacted>",
        text,
    )


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise SystemExit("PyYAML is required to read business-test-plan.yaml") from exc
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"cannot read business manifest: {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise SystemExit(f"invalid business manifest YAML: {path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("businesses"), list):
        raise SystemExit(f"business manifest must contain a businesses list: {path}")
    return payload


def load_plan_nodes(plan_path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read generated execution plan: {plan_path}: {exc}") from exc
    nodes = {
        str(node.get("bruno_path")): node
        for node in payload.get("nodes", [])
        if node.get("bruno_path") and node.get("id")
    }
    if not nodes:
        raise SystemExit(f"generated execution plan has no bruno_path nodes: {plan_path}")
    return nodes


def evaluate_checkpoint(
    checkpoint_path: Path,
    steps: list[dict[str, Any]],
    plan_nodes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate checks that are safe to derive from the body-free checkpoint.

    Bruno response bodies are deliberately omitted from reports to avoid
    leaking tokens/PII.  HTTP status and request-script outcomes are therefore
    automatic; body/state assertions remain declared checks for operator
    review.
    """
    try:
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"available": False, "reason": "checkpoint unreadable"}
    entries = {str(item.get("node")): item for item in payload.get("steps", [])}
    status_failures: list[str] = []
    http_failures: list[str] = []
    deferred: list[dict[str, Any]] = []
    script_checks: list[str] = []
    for step in steps:
        path = str(step["path"])
        node = plan_nodes.get(path, {})
        entry = entries.get(str(node.get("id")))
        expected = step.get("expected", {})
        if entry is None:
            status_failures.append(f"{path}: missing checkpoint entry")
            continue
        if entry.get("status") != "pass":
            status_failures.append(f"{path}: status={entry.get('status')}")
        allowed = expected.get("http_status")
        if allowed and entry.get("http_status") is not None and entry.get("http_status") not in allowed:
            http_failures.append(f"{path}: got HTTP {entry.get('http_status')}, expected {allowed}")
        if expected.get("captures"):
            # Canonical collection requests throw from their post-response
            # script when an expected ID is absent. A passing Bruno request
            # therefore proves the capture script itself completed.
            script_checks.append(f"{path}: captures {expected['captures']}")
        for key in ("body_fields_any", "response_present", "state_change", "state_in"):
            if key in expected:
                if key == "response_present" and entry.get("http_status") is not None:
                    script_checks.append(f"{path}: response_present")
                else:
                    deferred.append({"path": path, "check": key, "expected": expected[key]})
    return {
        "available": True,
        "request_status_failures": status_failures,
        "http_status_failures": http_failures,
        "script_checks_passed": script_checks,
        "deferred_body_or_state_checks": deferred,
        "all_transport_checks_pass": not status_failures and not http_failures,
        "review_required": bool(deferred),
    }


def index_businesses(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for business in manifest["businesses"]:
        business_id = str(business.get("id", "")).strip()
        if not business_id or business_id in result:
            raise SystemExit(f"business manifest has duplicate/empty id: {business_id!r}")
        result[business_id] = business
    return result


def selected_steps(
    business: dict[str, Any],
    *,
    auth_step: str | None,
    variant: str,
    include_optional: bool,
    runtime_producers: dict[str, list[str]],
    plan_nodes: dict[str, dict[str, Any]],
    include_manual: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return steps with runtime producers inserted before each consumer.

    The business manifest is intentionally readable and may list a consumer
    without repeating its setup calls.  The explicit producer map is the
    executable source of truth: every mapped producer is inserted recursively
    before the consumer and deduplicated in the final sequence.  This keeps
    Bruno's cookie/bru.setVar state in one process while preventing a consumer
    from being sent with a stale fixture ID.
    """
    steps: list[dict[str, Any]] = []
    excluded: list[str] = []
    visiting: set[str] = set()

    def producer_step(path: str, consumer: str) -> dict[str, Any]:
        node = plan_nodes.get(path)
        if node is None:
            raise SystemExit(
                f"runtime producer {path!r} for {consumer!r} is absent from generated plan"
            )
        if not node.get("default_execution", True):
            raise SystemExit(
                f"runtime producer {path!r} for {consumer!r} is an alias/deferred request"
            )
        return {
            "id": f"runtime-producer:{path}",
            "path": path,
            "mode": "required",
            "runtime_producer_for": consumer,
        }

    def add_with_producers(step: dict[str, Any], source: str) -> None:
        path = str(step["path"])
        if path in visiting:
            chain = " -> ".join([*visiting, path])
            raise SystemExit(f"runtime producer cycle detected: {chain}")
        visiting.add(path)
        for producer in runtime_producers.get(path, []):
            add_with_producers(producer_step(producer, path), f"runtime-producer:{path}")
        visiting.remove(path)
        add(step, source)

    def add(step: dict[str, Any], source: str) -> None:
        node = plan_nodes.get(str(step["path"]))
        if node is not None and not node.get("default_execution", True):
            excluded.append(f"{source}: alias/deferred (aliases remain untouched)")
            return
        mode = str(step.get("mode", "required"))
        if mode == "manual":
            # A canonical manual step becomes executable once its producer
            # chain is explicitly mapped.  Only unmapped/manual requests
            # still require operator review; aliases were filtered above.
            if not include_manual and str(step["path"]) not in runtime_producers:
                excluded.append(f"{source}: manual step (use --include-manual)")
                return
        if mode == "optional" and not include_optional:
            excluded.append(f"{source}: optional (use --include-optional)")
            return
        steps.append(step)

    # Login is a session prerequisite for every business.  Keeping it out of
    # each domain definition avoids duplication while preserving its position
    # before all producer/consumer requests.
    if auth_step and business.get("id") != "authentication":
        add_with_producers({"id": "login", "path": auth_step, "mode": "required"}, "login")

    for step in business.get("steps", []):
        if not isinstance(step, dict) or not step.get("path"):
            raise SystemExit(f"business {business.get('id')} has an invalid step: {step!r}")
        add_with_producers(step, str(step.get("id", step["path"])))

    if variant != "none":
        alternatives = business.get("alternatives", [])
        match = next((item for item in alternatives if item.get("id") == variant), None)
        if match is None and alternatives:
            available = ", ".join(str(item.get("id")) for item in alternatives)
            raise SystemExit(
                f"business {business.get('id')} has no variant {variant!r}; available variants: {available} (or none)"
            )
        if match:
            for step in match.get("steps", []):
                add_with_producers(step, f"variant:{variant}:{step.get('id', step.get('path'))}")

    for step in business.get("final_checks", []):
        if not isinstance(step, dict) or not step.get("path"):
            raise SystemExit(f"business {business.get('id')} has an invalid final check: {step!r}")
        add_with_producers(step, f"final:{step.get('id', step['path'])}")

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for step in steps:
        path = str(step["path"])
        if path not in seen:
            seen.add(path)
            deduped.append(step)
    return deduped, excluded


def command_for_business(
    *,
    business_steps: list[dict[str, Any]],
    runner: Path,
    plan: Path,
    collection: Path,
    env: str | None,
    bru: str,
    report_dir: Path,
    args: argparse.Namespace,
) -> list[str]:
    command = [
        sys.executable,
        str(runner),
        "--plan",
        str(plan),
        "--collection",
        str(collection),
        "--bru",
        bru,
        "--no-dependency-closure",
        "--report-dir",
        str(report_dir),
    ]
    if env:
        command.extend(["--env", env])
    for step in business_steps:
        command.extend(["--request", str(step["path"])])
    if args.execute:
        command.append("--execute")
    if args.allow_mutations:
        command.append("--allow-mutations")
    if args.allow_hardcoded_fixtures:
        command.append("--allow-hardcoded-fixtures")
    if args.allow_db_binding:
        command.append("--allow-db-binding")
    if args.allow_generic_session:
        command.append("--allow-generic-session")
    if args.include_error_body:
        command.append("--include-error-body")
    if args.include_aliases:
        command.append("--include-aliases")
    return command


def list_businesses(businesses: dict[str, dict[str, Any]]) -> None:
    for business_id, business in businesses.items():
        safety = business.get("safety", "unspecified")
        title = business.get("title", business_id)
        print(f"{business_id:24} [{safety:12}] {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--collection", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--business", action="append", help="business id to run (repeatable)")
    parser.add_argument("--all", action="store_true", help="run every business, one Bruno process per business")
    parser.add_argument("--all-read-only", action="store_true", help="run businesses marked safety=read_only")
    parser.add_argument("--list", action="store_true", help="list available business groups")
    parser.add_argument("--variant", default="approve", help="approval variant: approve, reject, or none")
    parser.add_argument("--include-optional", action="store_true", help="include optional/upload steps")
    parser.add_argument(
        "--include-manual",
        action="store_true",
        help="include reviewed manual steps after their mapped runtime producers",
    )
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument("--env", default="KG - local.bru")
    parser.add_argument("--bru", default=os.environ.get("BRU_BIN", "bru"))
    parser.add_argument("--execute", action="store_true", help="send requests; default is dry-run")
    parser.add_argument("--allow-mutations", action="store_true")
    parser.add_argument("--allow-hardcoded-fixtures", action="store_true")
    parser.add_argument("--allow-db-binding", action="store_true")
    parser.add_argument("--allow-generic-session", action="store_true")
    parser.add_argument(
        "--include-error-body",
        action="store_true",
        help="retain only redacted response bodies for failed requests",
    )
    parser.add_argument("--include-aliases", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=Path("/tmp/hrm-pack-api-test"))
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    plan_path = args.plan.resolve()
    collection = args.collection.resolve()
    if not manifest_path.is_file():
        raise SystemExit(f"business manifest not found: {manifest_path}")
    if not plan_path.is_file():
        raise SystemExit(f"generated plan not found: {plan_path}")
    if not collection.is_dir():
        raise SystemExit(f"collection not found: {collection}")

    manifest = load_manifest(manifest_path)
    businesses = index_businesses(manifest)
    if args.list:
        list_businesses(businesses)
        return 0
    if args.all and args.all_read_only:
        raise SystemExit("choose only one of --all or --all-read-only")

    if args.all:
        selected_ids = list(businesses)
    elif args.all_read_only:
        selected_ids = [key for key, value in businesses.items() if value.get("safety") == "read_only"]
    elif args.business:
        selected_ids = args.business
    else:
        raise SystemExit("select --business <id>, --all-read-only, or --all (use --list first)")

    unknown = [business_id for business_id in selected_ids if business_id not in businesses]
    if unknown:
        raise SystemExit("unknown business id(s): " + ", ".join(unknown))

    plan_nodes = load_plan_nodes(plan_path)
    plan_paths = set(plan_nodes)
    raw_runtime_producers = manifest.get("runtime_producers", {})
    if not isinstance(raw_runtime_producers, dict):
        raise SystemExit("business manifest runtime_producers must be a mapping")
    runtime_producers: dict[str, list[str]] = {}
    for consumer, producers in raw_runtime_producers.items():
        if not isinstance(producers, list) or not all(isinstance(item, str) for item in producers):
            raise SystemExit(f"runtime_producers[{consumer!r}] must be a list of paths")
        runtime_producers[str(consumer)] = [str(item) for item in producers]
    invalid_runtime_map: list[str] = []
    for consumer, producers in runtime_producers.items():
        if consumer not in plan_nodes:
            invalid_runtime_map.append(f"consumer missing from plan: {consumer}")
        for producer in producers:
            node = plan_nodes.get(producer)
            if node is None:
                invalid_runtime_map.append(f"producer missing from plan: {producer} (for {consumer})")
            elif not node.get("default_execution", True):
                invalid_runtime_map.append(f"alias producer is deferred: {producer} (for {consumer})")
    if invalid_runtime_map:
        raise SystemExit("invalid runtime producer map:\n- " + "\n- ".join(invalid_runtime_map))
    auth_step = manifest.get("execution_defaults", {}).get("auth_step")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = args.report_dir.resolve() / f"business-{stamp}"
    run_root.mkdir(parents=True, exist_ok=True)
    aggregate: dict[str, Any] = {
        "manifest": str(manifest_path),
        "plan": str(plan_path),
        "collection": str(collection),
        "started_at": stamp,
        "execute": bool(args.execute),
        "variant": args.variant,
        "businesses": [],
    }

    overall_rc = 0
    for business_id in selected_ids:
        business = businesses[business_id]
        steps, excluded = selected_steps(
            business,
            auth_step=auth_step,
            variant=args.variant,
            include_optional=args.include_optional,
            runtime_producers=runtime_producers,
            plan_nodes=plan_nodes,
            include_manual=args.include_manual,
        )
        missing = [str(step["path"]) for step in steps if str(step["path"]) not in plan_paths]
        if missing:
            raise SystemExit(f"business {business_id} references paths absent from generated plan: {', '.join(missing)}")
        missing_collection = [str(step["path"]) for step in steps if not (collection / str(step["path"])).is_file()]
        if missing_collection:
            raise SystemExit(f"business {business_id} references missing collection files: {', '.join(missing_collection)}")

        business_report_dir = run_root / business_id
        command = command_for_business(
            business_steps=steps,
            runner=HERE / "run_api_sequence.py",
            plan=plan_path,
            collection=collection,
            env=args.env,
            bru=args.bru,
            report_dir=business_report_dir,
            args=args,
        )
        print(f"\n=== BUSINESS: {business_id} ({business.get('title', business_id)}) ===")
        print(f"safety: {business.get('safety', 'unspecified')}; steps: {len(steps)}; variant: {args.variant}")
        if excluded:
            print("excluded: " + "; ".join(excluded))
        fixture_steps = [
            step
            for step in steps
            if step.get("fixture_required")
            and str(step["path"]) not in runtime_producers
            and not args.allow_hardcoded_fixtures
        ]
        if fixture_steps:
            output = (
                "BLOCKED preflight (business fixture): manifest marks these steps as fixture-required; "
                "pass --allow-hardcoded-fixtures only after verifying the IDs/data in the target DB:\n"
                + "\n".join(f"- {step['path']}" for step in fixture_steps)
            )
            completed_returncode = 2
        else:
            completed = subprocess.run(command, text=True, capture_output=True, check=False)
            output = sanitize(completed.stdout + ("\n" + completed.stderr if completed.stderr else ""))
            completed_returncode = completed.returncode
        (business_report_dir / "business.log").parent.mkdir(parents=True, exist_ok=True)
        (business_report_dir / "business.log").write_text(output, encoding="utf-8")
        print(output.rstrip())

        checkpoint_candidates = sorted(str(path) for path in business_report_dir.rglob("checkpoint.json"))
        automatic_checks: dict[str, Any] = {
            "available": False,
            "reason": "dry-run or preflight stopped before a checkpoint was written",
        }
        if checkpoint_candidates:
            automatic_checks = evaluate_checkpoint(Path(checkpoint_candidates[-1]), steps, plan_nodes)

        if automatic_checks.get("available") and not automatic_checks.get("all_transport_checks_pass", False):
            # The child runner can return 0 when an endpoint technically
            # passed but its declared expected HTTP status did not match.
            # Promote that mismatch to a business-level failure.
            if overall_rc == 0:
                overall_rc = 1
            if completed_returncode == 0:
                completed_returncode = 1

        if completed_returncode == 0:
            if not args.execute:
                status = "dry_run"
            elif automatic_checks.get("review_required"):
                status = "passed_transport_review_required"
            else:
                status = "passed"
        elif completed_returncode == 2 and "BLOCKED preflight" in output:
            status = "blocked"
        else:
            status = "failed"
        if completed_returncode and overall_rc == 0:
            overall_rc = completed_returncode
        aggregate["businesses"].append(
            {
                "id": business_id,
                "title": business.get("title", business_id),
                "safety": business.get("safety"),
                "status": status,
                "returncode": completed_returncode,
                "steps": [str(step["path"]) for step in steps],
                "excluded": excluded,
                "declared_preconditions": business.get("preconditions", []),
                "declared_expected_checks": [step.get("expected", {}) for step in steps if step.get("expected")],
                "automatic_checks": automatic_checks,
                "business_assertions_review_required": bool(automatic_checks.get("review_required")),
                "checkpoint_candidates": checkpoint_candidates,
                "log": str(business_report_dir / "business.log"),
            }
        )
        if completed_returncode and not args.continue_on_failure:
            print("STOP: business failed/blocked; use --continue-on-failure to inspect remaining businesses", file=sys.stderr)
            break

    aggregate["finished_at"] = datetime.now(timezone.utc).isoformat()
    report_path = run_root / "business-report.json"
    report_path.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nBusiness report: {report_path}")
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
