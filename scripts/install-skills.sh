#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
FORCE=0

usage() {
    cat <<USAGE
Usage: $(basename "$0") [--force]

Install skills from this repository into $CODEX_HOME/skills (default: ~/.codex/skills).
Existing skill directories are skipped unless --force is supplied.
USAGE
}

for arg in "$@"; do
    case "$arg" in
        --force) FORCE=1 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
    esac
done

mkdir -p "$TARGET_DIR"
installed=0
skipped=0

while IFS= read -r -d '' skill_file; do
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    destination="$TARGET_DIR/$skill_name"
    if [[ -e "$destination" && "$FORCE" -ne 1 ]]; then
        printf 'SKIP  %s (already exists)\n' "$skill_name"
        skipped=$((skipped + 1))
        continue
    fi
    if [[ -e "$destination" ]]; then
        rm -rf "$destination"
    fi
    cp -a "$skill_dir" "$destination"
    printf 'COPY  %s\n' "$skill_name"
    installed=$((installed + 1))
done < <(find "$ROOT_DIR/skills" -type f -name SKILL.md -print0 | sort -z)

printf 'Installed %d skill(s); skipped %d.\n' "$installed" "$skipped"
