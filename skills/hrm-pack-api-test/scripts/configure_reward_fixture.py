#!/usr/bin/env python3
"""Create an owned approved reward fixture for read-only report APIs.

The collection exposes only read-only Reward & Discipline routes.  This
wrapper creates the prerequisite transaction through the Odoo ORM instead of
inventing a production API endpoint.  It is dry-run/rollback by default;
pass ``--apply`` only for the explicitly selected test database.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "configure_reward_fixture_orm.py"
DEFAULT_ODOO_BIN = Path("/home/linh/odoo/odoo-bin")
DEFAULT_CONFIG = Path("/home/linh/odoo/config/kg.conf")
DEFAULT_ODOO_PYTHON = Path("/home/linh/vdx/kg-odoo-hrm/.venv/bin/python")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="target database name")
    parser.add_argument(
        "--user",
        required=True,
        help="exact API user selector: numeric id, login, email, or unique name",
    )
    parser.add_argument(
        "--reward-type",
        help="optional exact reward type selector: numeric id, code, or name",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="JSON report path (default: /tmp/hrm-pack-api-test/reward-fixture-<db>-<timestamp>.json)",
    )
    parser.add_argument(
        "--odoo-bin",
        type=Path,
        default=Path(os.environ.get("ODOO_BIN", DEFAULT_ODOO_BIN)),
    )
    parser.add_argument(
        "--odoo-python",
        type=Path,
        default=Path(os.environ.get("ODOO_PYTHON", DEFAULT_ODOO_PYTHON)),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("ODOO_CONFIG", DEFAULT_CONFIG)),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="commit ORM changes; default is dry-run/rollback",
    )
    args = parser.parse_args()

    for path, label in (
        (PAYLOAD, "ORM payload"),
        (args.odoo_bin, "odoo-bin"),
        (args.odoo_python, "Odoo Python interpreter"),
        (args.config, "Odoo config"),
    ):
        if not path.is_file():
            raise SystemExit(f"{label} not found: {path}")

    report = args.report or Path("/tmp/hrm-pack-api-test") / (
        f"reward-fixture-{args.db}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    )
    prelude = (
        f"APPLY = {bool(args.apply)!r}\n"
        f"USER_SELECTOR = {args.user!r}\n"
        f"REWARD_TYPE_SELECTOR = {args.reward_type!r}\n"
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
    print(f"user: {args.user}")
    print(f"reward type: {args.reward_type or '<first active reward type>'}")
    print(f"report: {report}")
    print(f"mode: {'APPLY/COMMIT' if args.apply else 'DRY-RUN/ROLLBACK'}")
    completed = subprocess.run(
        command,
        input=prelude + PAYLOAD.read_text(encoding="utf-8"),
        text=True,
        capture_output=True,
        check=False,
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
