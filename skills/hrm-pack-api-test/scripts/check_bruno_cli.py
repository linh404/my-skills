#!/usr/bin/env python3
"""Verify that the pinned Bruno CLI dependency is installed and callable."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


VERSION_RE = re.compile(r"(?:Bru CLI\s+)?(\d+\.\d+\.\d+)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bru", default=os.environ.get("BRU_BIN", "bru"))
    parser.add_argument("--minimum-version", default="4.2.0")
    args = parser.parse_args()

    resolved = shutil.which(args.bru) if os.path.basename(args.bru) == args.bru else str(Path(args.bru).expanduser().resolve())
    if not resolved:
        print(f"ERROR: Bruno CLI not found: {args.bru}", file=sys.stderr)
        return 2
    try:
        result = subprocess.run([resolved, "--version"], text=True, capture_output=True, check=False)
    except OSError as exc:
        print(f"ERROR: unable to execute Bruno CLI {resolved}: {exc}", file=sys.stderr)
        return 2
    output = (result.stdout or result.stderr).strip()
    match = VERSION_RE.search(output)
    if result.returncode != 0 or not match:
        print(f"ERROR: Bruno CLI version check failed: {output or '<no output>'}", file=sys.stderr)
        return 2
    version = tuple(int(part) for part in match.group(1).split("."))
    minimum = tuple(int(part) for part in args.minimum_version.split("."))
    if version < minimum:
        print(f"ERROR: Bruno CLI {match.group(1)} is older than required {args.minimum_version}", file=sys.stderr)
        return 2
    print(f"PASS: Bruno CLI {match.group(1)} ({resolved})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
