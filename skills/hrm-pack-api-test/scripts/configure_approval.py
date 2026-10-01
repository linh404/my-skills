#!/usr/bin/env python3
"""Idempotently configure the repository's dynamic approval framework.

The script launches ``odoo-bin shell`` and performs ORM configuration in the
selected database. It is a dry-run by default. Use ``--apply`` only after
reviewing the planned changes and explicitly selecting an approver.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "configure_approval_orm.py"
DEFAULT_ODOO_BIN = Path("/home/linh/odoo/odoo-bin")
DEFAULT_CONFIG = Path("/home/linh/odoo/config/kg.conf")
DEFAULT_ODOO_PYTHON = Path("/home/linh/vdx/kg-odoo-hrm/.venv/bin/python")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="target database name")
    parser.add_argument("--approver", required=True, help="exact approver user id, login, email, or name")
    parser.add_argument(
        "--originator",
        help="exact originator user id, login, email, or name (defaults to --approver)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow replacing a non-empty ir.model approval mapping (default: fail safely)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="JSON report path (default: /tmp/hrm-pack-api-test/approval-config-<db>-<timestamp>.json)",
    )
    parser.add_argument("--odoo-bin", type=Path, default=Path(os.environ.get("ODOO_BIN", DEFAULT_ODOO_BIN)))
    parser.add_argument("--odoo-python", type=Path, default=Path(os.environ.get("ODOO_PYTHON", DEFAULT_ODOO_PYTHON)))
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("ODOO_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--apply", action="store_true", help="commit ORM changes; default is dry-run/rollback")
    args = parser.parse_args()

    if not PAYLOAD.is_file():
        raise SystemExit(f"ORM payload not found: {PAYLOAD}")
    if not args.odoo_bin.is_file():
        raise SystemExit(f"odoo-bin not found: {args.odoo_bin}")
    if not args.odoo_python.is_file():
        raise SystemExit(f"Odoo Python interpreter not found: {args.odoo_python}")
    if not args.config.is_file():
        raise SystemExit(f"Odoo config not found: {args.config}")
    payload = PAYLOAD.read_text(encoding="utf-8")
    report = args.report or Path(
        "/tmp/hrm-pack-api-test"
    ) / f"approval-config-{args.db}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    prelude = (
        f"APPLY = {bool(args.apply)!r}\n"
        f"APPROVER_SELECTOR = {args.approver!r}\n"
        f"ORIGINATOR_SELECTOR = {(args.originator or args.approver)!r}\n"
        f"FORCE = {bool(args.force)!r}\n"
        f"REPORT_PATH = {str(report)!r}\n"
    )
    command = [
        str(args.odoo_python),
        str(args.odoo_bin),
        "shell",
        "-c",
        str(args.config),
        "-d",
        args.db,
        "--no-http",
    ]
    print(f"database: {args.db}")
    print(f"approver: {args.approver}")
    print(f"originator: {args.originator or args.approver}")
    print(f"report: {report}")
    print(f"force: {args.force}")
    print(f"mode: {'APPLY/COMMIT' if args.apply else 'DRY-RUN/ROLLBACK'}")
    completed = subprocess.run(
        command,
        input=prelude + payload,
        text=True,
        capture_output=True,
        check=False,
    )
    sys.stdout.write(completed.stdout)
    if completed.returncode:
        sys.stderr.write(completed.stderr)
    elif completed.stderr:
        # Odoo shell emits useful registry warnings on stderr; preserve them
        # without turning a successful configuration into a false failure.
        sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
