#!/usr/bin/env bash
set -Eeuo pipefail

# Run an existing Bruno collection without modifying it.
# If --collection is omitted, ask the operator for the collection path.

COLLECTION_INPUT=""
MODE="read"
ENV_NAME=""
BRU_BIN="${BRU_BIN:-$(command -v bru 2>/dev/null || true)}"
REPORT_DIR="${BRUNO_REPORT_DIR:-${TMPDIR:-/tmp}/bruno-test-runner}"
ALLOW_MUTATIONS=0
ALLOW_HTTP_ERRORS=0
DRY_RUN=0
BAIL=0
TESTS_ONLY=0

usage() {
    cat <<'USAGE'
Usage: run_collection.sh [read|all] [options]

Run an existing Bruno collection. The default read mode selects actual HTTP GET
requests plus request names that indicate read-only APIs (get/list/search_read,
matrix/v4, and app_get). Login requests are placed first when present.

Modes:
  read                 Run read-like requests (default).
  all                  Run every .bru request; requires --allow-mutations.

Options:
  --collection PATH    Bruno collection directory. If omitted, ask interactively.
  --env NAME           Bruno environment name.
  --bru PATH           Bruno CLI executable (default: bru in PATH or BRU_BIN).
  --report-dir DIR     Report directory (default: \${TMPDIR:-/tmp}/bruno-test-runner).
  --allow-mutations    Required for all mode.
  --allow-http-errors  Do not fail only because an HTTP status is >= 400.
  --tests-only         Run only requests containing Bruno tests/assertions.
  --bail               Stop after the first Bruno request/test/assertion failure.
  --dry-run            Print selected requests without executing them.
  -h, --help           Show this help.

Examples:
  run_collection.sh read --collection /path/to/collection --env Local
  run_collection.sh --collection /path/to/collection --env Local
  run_collection.sh all --collection /path/to/collection --env Test --allow-mutations
USAGE
}

while (($#)); do
    case "$1" in
        read|all)
            MODE="$1"
            shift
            ;;
        --collection)
            [[ $# -ge 2 ]] || { echo "error: --collection requires a path" >&2; exit 2; }
            COLLECTION_INPUT="$2"
            shift 2
            ;;
        --env)
            [[ $# -ge 2 ]] || { echo "error: --env requires a value" >&2; exit 2; }
            ENV_NAME="$2"
            shift 2
            ;;
        --bru)
            [[ $# -ge 2 ]] || { echo "error: --bru requires a path" >&2; exit 2; }
            BRU_BIN="$2"
            shift 2
            ;;
        --report-dir)
            [[ $# -ge 2 ]] || { echo "error: --report-dir requires a path" >&2; exit 2; }
            REPORT_DIR="$2"
            shift 2
            ;;
        --allow-mutations)
            ALLOW_MUTATIONS=1
            shift
            ;;
        --allow-http-errors)
            ALLOW_HTTP_ERRORS=1
            shift
            ;;
        --tests-only)
            TESTS_ONLY=1
            shift
            ;;
        --bail)
            BAIL=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -z "$COLLECTION_INPUT" ]]; then
    if [[ -t 0 ]]; then
        read -r -p 'Bruno collection path: ' COLLECTION_INPUT
    else
        echo 'error: --collection is required in non-interactive mode' >&2
        exit 2
    fi
fi

if [[ ! -d "$COLLECTION_INPUT" ]]; then
    echo "error: collection directory not found: $COLLECTION_INPUT" >&2
    exit 2
fi
COLLECTION_DIR="$(cd "$COLLECTION_INPUT" && pwd -P)"
if [[ ! -f "$COLLECTION_DIR/bruno.json" ]]; then
    echo "error: not a Bruno collection (missing bruno.json): $COLLECTION_DIR" >&2
    exit 2
fi

if [[ "$MODE" == all && "$ALLOW_MUTATIONS" -ne 1 ]]; then
    echo 'error: all mode can mutate data; pass --allow-mutations explicitly' >&2
    exit 2
fi

if [[ "$DRY_RUN" -eq 0 && ( -z "$BRU_BIN" || ! -x "$BRU_BIN" ) ]]; then
    cat >&2 <<'MSG'
error: Bruno CLI not found.
Install the approved Bruno CLI or set BRU_BIN=/path/to/bru.
MSG
    exit 2
fi

mapfile -t REQUESTS < <(ROOT_DIR="$COLLECTION_DIR" MODE="$MODE" python3 - <<'PY'
import os
from pathlib import Path

root = Path(os.environ['ROOT_DIR'])
mode = os.environ['MODE']
all_paths = []

for path in sorted(root.glob('**/*.bru')):
    rel = path.relative_to(root)
    rel_text = str(rel)
    if rel_text.startswith('environments/'):
        continue
    if mode == 'all':
        all_paths.append(rel_text)
        continue

    text = path.read_text(encoding='utf-8', errors='replace')
    method = next(
        (line.strip().split()[0].lower()
         for line in text.splitlines()
         if line.strip().lower() in {
             'get {', 'post {', 'put {', 'patch {', 'delete {',
             'head {', 'options {'
         }),
        '',
    )
    stem = path.stem.lower()
    read_like_name = (
        stem.startswith(('get_', 'list_', 'search_read', 'app_get'))
        or stem in {'matrix', 'v4'}
    )
    auth_like_name = stem in {'login', 'sign_in', 'signin', 'authenticate'}
    if method == 'get' or read_like_name or auth_like_name:
        all_paths.append(rel_text)

# Put login/authentication requests before dependent bearer-authenticated reads.
login_paths = [
    p for p in all_paths
    if Path(p).stem.lower() in {'login', 'sign_in', 'signin', 'authenticate'}
]
other_paths = [p for p in all_paths if p not in login_paths]
for path in login_paths + other_paths:
    print(path)
PY
)

if ((${#REQUESTS[@]} == 0)); then
    echo "error: no requests selected in $COLLECTION_DIR" >&2
    exit 2
fi

printf 'collection: %s\n' "$COLLECTION_DIR"
printf 'mode: %s\n' "$MODE"
printf 'environment: %s\n' "${ENV_NAME:-<not specified>}"
printf 'requests: %d\n' "${#REQUESTS[@]}"

if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '%s\n' "${REQUESTS[@]}"
    exit 0
fi

mkdir -p "$REPORT_DIR"
stamp="$(date +%Y%m%d-%H%M%S)"
json_report="$REPORT_DIR/bruno-$MODE-$stamp.json"
junit_report="$REPORT_DIR/bruno-$MODE-$stamp.xml"

args=(run "${REQUESTS[@]}"
      --reporter-json "$json_report"
      --reporter-junit "$junit_report"
      --reporter-skip-body
      --reporter-skip-all-headers)
[[ -n "$ENV_NAME" ]] && args+=(--env "$ENV_NAME")
[[ "$TESTS_ONLY" -eq 1 ]] && args+=(--tests-only)
[[ "$BAIL" -eq 1 ]] && args+=(--bail)

set +e
"$BRU_BIN" "${args[@]}"
bru_exit=$?
set -e

if [[ ! -f "$json_report" ]]; then
    echo "error: Bruno did not write a JSON report: $json_report" >&2
    exit "$bru_exit"
fi

set +e
python3 - "$json_report" "$ALLOW_HTTP_ERRORS" <<'PY'
import json
import sys
from collections import Counter

report_path = sys.argv[1]
allow_http_errors = sys.argv[2] == '1'
data = json.load(open(report_path, encoding='utf-8'))
results = [result for batch in data for result in batch.get('results', [])]
statuses = Counter(result.get('response', {}).get('status') for result in results)
summary = data[0].get('summary', {}) if data else {}
print('HTTP status counts:', dict(sorted(statuses.items(), key=lambda item: str(item[0]))))
print('Bruno tests:', summary.get('totalTests', 0), 'assertions:', summary.get('totalAssertions', 0))
if not summary.get('totalTests') and not summary.get('totalAssertions'):
    print('WARNING: no Bruno tests/assertions ran; this is an HTTP run only.')
http_errors = [
    (result.get('response', {}).get('status'), result.get('test', {}).get('filename'))
    for result in results
    if isinstance(result.get('response', {}).get('status'), int)
    and result['response']['status'] >= 400
]
for status, filename in http_errors:
    print(f'HTTP_ERROR {status}: {filename}')
if http_errors and not allow_http_errors:
    print('HTTP errors found; exiting non-zero. Use --allow-http-errors only when expected.')
    raise SystemExit(1)
PY
parser_exit=$?
set -e

printf 'json_report: %s\n' "$json_report"
printf 'junit_report: %s\n' "$junit_report"
if ((bru_exit != 0)); then
    exit "$bru_exit"
fi
exit "$parser_exit"
