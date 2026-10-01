#!/usr/bin/env python3
"""Configure the shared fixtures required by remaining Group-A API flows."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "configure_group_a_fixtures_orm.py"
ODOO_BIN = Path(os.environ.get("ODOO_BIN", "/home/linh/odoo/odoo-bin"))
ODOO_PYTHON = Path(os.environ.get("ODOO_PYTHON", "/home/linh/vdx/kg-odoo-hrm/.venv/bin/python"))
CONFIG = Path(os.environ.get("ODOO_CONFIG", "/home/linh/odoo/config/kg.conf"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--user", default="admin")
    parser.add_argument("--apply", action="store_true", help="commit fixture changes")
    args = parser.parse_args()
    for path, label in ((PAYLOAD, "payload"), (ODOO_BIN, "odoo-bin"), (ODOO_PYTHON, "odoo python"), (CONFIG, "config")):
        if not path.is_file():
            raise SystemExit(f"{label} not found: {path}")
    prelude = f"APPLY = {bool(args.apply)!r}\nUSER_SELECTOR = {args.user!r}\n"
    command = [str(ODOO_PYTHON), str(ODOO_BIN), "shell", "-c", str(CONFIG), "-d", args.db, "--no-http"]
    print(f"database: {args.db}; user: {args.user}; mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    completed = subprocess.run(command, input=prelude + PAYLOAD.read_text(encoding="utf-8"), text=True, capture_output=True, check=False)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
