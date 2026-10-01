#!/usr/bin/env python3
"""Ensure an Odoo language (default: ``vi_VN``) is installed and active.

The wrapper runs an ORM payload in an isolated Odoo shell. It is a dry-run by
default; ``--apply`` is required before any database write. The script only
installs/activates the requested language. It does not silently change every
user's preferred language.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "configure_language_orm.py"
DEFAULT_ODOO_BIN = Path("/home/linh/odoo/odoo-bin")
DEFAULT_CONFIG = Path("/home/linh/odoo/config/kg.conf")
DEFAULT_ODOO_PYTHON = Path("/home/linh/vdx/kg-odoo-hrm/.venv/bin/python")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="target database name")
    parser.add_argument("--language", default="vi_VN", help="language code (default: vi_VN)")
    parser.add_argument("--name", default="Vietnamese / Tiếng Việt", help="display name when creating a language")
    parser.add_argument("--odoo-bin", type=Path, default=Path(os.environ.get("ODOO_BIN", DEFAULT_ODOO_BIN)))
    parser.add_argument("--odoo-python", type=Path, default=Path(os.environ.get("ODOO_PYTHON", DEFAULT_ODOO_PYTHON)))
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("ODOO_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--apply", action="store_true", help="commit ORM changes; default is dry-run/rollback")
    parser.add_argument("--report", type=Path, help="JSON report path")
    args = parser.parse_args()

    for path, label in ((PAYLOAD, "ORM payload"), (args.odoo_bin, "odoo-bin"), (args.odoo_python, "Odoo Python"), (args.config, "Odoo config")):
        if not path.is_file():
            raise SystemExit(f"{label} not found: {path}")
    if not args.language.strip():
        raise SystemExit("language code must not be empty")

    report = args.report or Path("/tmp/hrm-pack-api-test") / (
        f"language-config-{args.db}-{args.language}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    )
    payload = PAYLOAD.read_text(encoding="utf-8")
    prelude = (
        f"APPLY = {bool(args.apply)!r}\n"
        f"LANGUAGE_CODE = {args.language.strip()!r}\n"
        f"LANGUAGE_NAME = {args.name!r}\n"
        f"REPORT_PATH = {str(report)!r}\n"
    )
    command = [
        str(args.odoo_python), str(args.odoo_bin), "shell", "-c", str(args.config),
        "-d", args.db, "--no-http",
    ]
    print(f"database: {args.db}")
    print(f"language: {args.language}")
    print(f"mode: {'APPLY/COMMIT' if args.apply else 'DRY-RUN/ROLLBACK'}")
    print(f"report: {report}")
    completed = subprocess.run(command, input=prelude + payload, text=True, capture_output=True, check=False)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
