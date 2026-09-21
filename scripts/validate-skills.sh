#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
found=0
errors=0

while IFS= read -r -d '' skill_file; do
    found=$((found + 1))
    relative_path="${skill_file#"$ROOT_DIR/"}"
    if [[ ! -s "$skill_file" ]]; then
        printf 'ERROR: missing or empty %s\n' "$relative_path" >&2
        errors=$((errors + 1))
        continue
    fi
    if ! grep -Eq '^[[:space:]]*(name:|#)' "$skill_file"; then
        printf 'ERROR: %s has no recognizable heading or name field\n' "$relative_path" >&2
        errors=$((errors + 1))
    fi
done < <(find "$SKILLS_DIR" -type f -name SKILL.md -print0 | sort -z)

printf 'Validated %d skill(s).\n' "$found"
if (( errors > 0 )); then
    printf '%d validation error(s) found.\n' "$errors" >&2
    exit 1
fi
