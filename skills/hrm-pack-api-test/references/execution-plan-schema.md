# Execution-plan schema

The generated plan can be YAML or JSON. Keep it machine-readable and preserve evidence.

```yaml
metadata:
  collection_root: /path/to/collection
  source_root: /path/to/backend
  generated_at: YYYY-MM-DD
  analysis_mode: source_and_collection
  execution_allowed: false

phases:
  - id: auth
    purpose: establish_session
    steps: [auth.login]

nodes:
  - id: auth.login
    bruno_path: Authentication & System/login.bru
    method: POST
    operation: auth
    side_effect: session_only
    depends_on: []
    preconditions: []
    inputs:
      - name: user
        source: environment
        sensitive: true
    captures:
      - name: token
        destination: bruno_secret.token
        sensitive: true
    expected:
      http_status: [200]
      business_state: authenticated
    evidence: COLLECTION_VERIFIED
    retry: safe_after_auth_failure_review

edges:
  - from: master.create
    to: employee.create
    kind: data_dependency
    reason: employee.division_id_required
    evidence: SOURCE_VERIFIED

constraints:
  - node: employee.create
    type: foreign_key
    field: division_id
    prerequisite: master.division.create
    evidence: SOURCE_VERIFIED

unknowns:
  - id: unknown-001
    node: some.request
    question: Which endpoint creates the required reference fixture?
    impact: blocks_execution
    evidence: UNKNOWN
```

## Required distinctions

- `SOURCE_VERIFIED`: backed by route/controller/model/constraint/security code.
- `COLLECTION_VERIFIED`: backed by `.bru` method, URL, payload, tests, or scripts.
- `INFERRED`: plausible from naming or consistent flow but not proven.
- `UNKNOWN`: evidence missing; ask or inspect further.
- `BLOCKED`: cannot continue safely without a decision, fixture, permission, or source evidence.

`side_effect` should distinguish at least `read_only`, `session_only`, `create`, `update`,
`delete`, `upload`, `workflow_transition`, and `external_call`.
