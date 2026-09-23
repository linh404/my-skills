# Bruno CLI run reference

Use this reference for local and CI execution. Check `bru run --help` because flags can vary by the installed CLI version.

## Common commands

```bash
bru run request.bru --env Local
bru run requests/users --env Local
bru run folder -r --env Local
bru run --env Local --tests-only --bail
```

The repository also includes a generic runner that accepts any Bruno
collection path:

```bash
skills/bruno-test-runner/scripts/run_collection.sh \
  read --collection /path/to/collection --env Local
```

Without `--collection`, it prompts for the path when attached to a terminal.
The `read` mode selects actual HTTP `GET` requests and names that indicate
read-like APIs, while `all` requires `--allow-mutations`.

Useful options:

- `--env NAME` or `--env-file PATH` — select the environment explicitly.
- `--env-var NAME=value` — override one variable for this run only.
- `--output PATH --format json|junit|html` — write machine-readable or HTML results.
- `--reporter-json PATH`, `--reporter-junit PATH`, `--reporter-html PATH` — write a report without relying on terminal output.
- `--reporter-skip-body` — omit request and response bodies from the report.
- `--reporter-skip-all-headers` — omit headers that may contain credentials.
- `--tests-only` — skip requests that have no test or active assertion; this is not a full collection run.
- `--bail` — stop after the first request, test, or assertion failure.
- `--cacert PATH` — provide a trusted CA certificate.
- `--insecure` — disable TLS verification; use only for an explicitly approved diagnostic run.
- `--delay MS` — pace requests when the service or rate limit requires it.

## Reading results

Report these separately:

1. HTTP status and request transport outcome.
2. Bruno test/assertion count and failures.
3. Environment/variable/configuration errors.
4. Whether the request is read-only or mutating.

A terminal summary with `Requests: N (N Passed)` and `Tests: 0/0` means only that requests completed from the CLI's perspective; it is not proof that response content or payloads satisfy the API contract. Add explicit status/body assertions or run a contract checker before claiming functional success.

## CI pattern

1. Use the project-pinned Bruno CLI or the approved CLI image/action.
2. Inject base URLs and credentials through CI variables or a secret manager.
3. Run the narrowest safe target and write a JUnit/JSON report.
4. Upload the report even when the command fails.
5. Let a non-zero exit status fail the job; do not turn a failed assertion into success.

Keep reports free of request/response bodies when they may contain credentials or personal data.

## Failure triage

- **Collection not found:** run from the collection root and verify `bruno.json` plus the requested path.
- **Environment not found:** use the exact environment filename/name and verify variable precedence.
- **401/403:** check that login/authentication ran in the same flow and that the token variable is available; do not print the token.
- **Unexpected 4xx/5xx:** compare the endpoint, payload variables, expected status, and server logs; do not weaken assertions to hide a contract failure.
- **No tests executed:** inspect for `tests {}` blocks or active assertions; `--tests-only` cannot test a collection that contains none.
- **Timeout/flakiness:** verify service readiness, data isolation, rate limits, and request ordering before adding delay/retry options.
