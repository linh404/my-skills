#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
while IFS= read -r -d '' skill_file; do
    printf '%s\n' "${skill_file#"$ROOT_DIR/"}"
done < <(find "$ROOT_DIR/skills" -type f -name SKILL.md -print0 | sort -z)
