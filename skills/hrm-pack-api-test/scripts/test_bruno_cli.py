#!/usr/bin/env python3
"""Run a lifecycle HRM flow through Bruno CLI.

Dry-run is the default phase for lifecycle execution. Execute only against a
disposable local/test database after reviewing the printed dependency order.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_api_sequence.py"
CHECKER = HERE / "check_bruno_cli.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow", default="employee_context")
    parser.add_argument("--env", default="KG - local.bru")
    parser.add_argument("--bru", default=os.environ.get("BRU_BIN", "bru"))
    parser.add_argument("--execute", action="store_true", help="send requests; default is dry-run")
    parser.add_argument("--max-steps", type=int, default=2)
    parser.add_argument("--allow-mutations", action="store_true")
    parser.add_argument("--allow-hardcoded-fixtures", action="store_true")
    parser.add_argument("--allow-db-binding", action="store_true")
    parser.add_argument("--allow-generic-session", action="store_true")
    args = parser.parse_args()

    check = subprocess.run([sys.executable, str(CHECKER), "--bru", args.bru], check=False)
    if check.returncode:
        return check.returncode
    command = [
        sys.executable,
        str(RUNNER),
        "--flow",
        args.flow,
        "--env",
        args.env,
        "--bru",
        args.bru,
        "--max-steps",
        str(args.max_steps),
    ]
    if args.execute:
        command.append("--execute")
    for flag in ("allow_mutations", "allow_hardcoded_fixtures", "allow_db_binding", "allow_generic_session"):
        if getattr(args, flag):
            command.append("--" + flag.replace("_", "-"))
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
