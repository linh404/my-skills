---
name: bruno-test-runner
description: Run and report Bruno collection tests safely with the Bruno CLI. Use when executing .bru requests, selecting environments, checking HTTP/test outcomes, generating CI reports, or diagnosing collection-run failures; do not author new API tests unless explicitly requested.
---

# Bruno test runner

Use this skill to execute an existing Bruno collection and report what actually ran. The primary deliverable is a reproducible run result, not new `.bru` test design.

## Run workflow

1. **Preflight the collection.** Locate `bruno.json`, request folders, environment files, and any existing `tests {}` blocks or active assertions. Check the installed Bruno CLI version and use the project's pinned version when available.
2. **Choose the target and environment.** Resolve the exact request/folder/collection path and environment name. Confirm the base URL, authentication prerequisites, and whether the target is local, test, staging, or production. Never print secrets.
3. **Classify side effects.** Treat login and read-only requests separately from create, update, delete, upload, approval, cancel, or other mutating requests. Do not run a full collection containing mutations on a shared or production environment without explicit approval.
4. **Run in increasing scope.** Start with one request or a small read-only flow, then the relevant folder, then the full collection only when the scope and data safety are clear. Use `--bail` when debugging the first failure and a reporter file for CI evidence.
5. **Interpret the result correctly.** Distinguish:
   - request/transport result (HTTP status, connection, timeout);
   - Bruno test/assertion result (`tests {}` and active assertions);
   - payload/contract validation (only proven by explicit assertions or an external contract check).
   A request receiving HTTP `401` or `500` can still appear as a passed request when no assertion defines the expected status. Never report “API tests passed” when the run has `Tests 0/0`.
6. **Report evidence.** Include the exact command, collection path, environment, request count, HTTP outcomes, test/assertion counts, report path, skipped requests, and any safety limitation. Keep response bodies and headers out of logs when they may contain credentials or personal data.

## Safe command patterns

Run commands from the Bruno collection root:

```bash
COLLECTION=/path/to/bruno-collection
cd "$COLLECTION"

# one request
bru run 'path/to/request.bru' --env 'Local'

# a folder, recursively when it contains nested folders
bru run 'path/to/folder' -r --env 'Local'

# only requests that contain tests/assertions
bru run --env 'Local' --tests-only --bail

# machine-readable evidence without response bodies
bru run --env 'Local' \
  --reporter-junit /tmp/bruno-results.xml \
  --reporter-skip-body
```

Use `--env-var NAME=value` only for an intentional one-off override. Prefer CI secret injection or an approved secret provider for credentials. Do not commit generated reports unless the repository explicitly tracks them.

For a reusable runner that accepts a collection path, use the bundled helper:

```bash
skills/bruno-test-runner/scripts/run_collection.sh \
  read --collection /path/to/bruno-collection --env Local
```

If `--collection` is omitted in an interactive shell, the helper asks for the
path. It defaults to read-like requests, writes body-free JSON/JUnit reports,
and exits non-zero for HTTP errors unless `--allow-http-errors` is supplied.
Use `all --allow-mutations` only for an explicitly approved test environment.

Read [references/cli.md](references/cli.md) for reporter options and CI handling.

## Payload and test limitations

- Executing a request proves only that Bruno sent the current payload and received a response.
- A `2xx` response does not prove that every field, type, enum, or business rule is correct.
- To claim payload correctness, require Bruno assertions or a separate schema/contract check for required fields, types, and expected status codes.
- If the collection has no assertions, report the run as an HTTP smoke check and state that payload correctness remains unverified.
- Do not silently edit request payloads while running tests. If a payload is missing variables or fixtures, stop and report the prerequisite.

## Safety and failure handling

- Never expose tokens, passwords, API keys, cookies, or full sensitive response bodies in output.
- Do not start, restart, recreate, or stop Docker containers or application services. Report the prerequisite and wait for explicit approval if a service is missing.
- Do not use `--insecure` just to hide certificate problems; use the correct CA or obtain explicit approval for a controlled diagnostic run.
- A request failure, assertion failure, and environment/configuration failure are different findings. Preserve the first failing request and its sanitized error output.
- If a run times out, check service readiness, DNS/base URL, authentication, request ordering, and test data before adding retries or delays.
- Keep the repository unchanged unless the user explicitly asks to add/fix tests, payloads, environments, or CI configuration.
