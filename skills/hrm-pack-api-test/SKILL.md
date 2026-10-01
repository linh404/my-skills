---
name: hrm-pack-api-test
description: Execute the prebuilt, source-backed HRM Bruno API sequences in dependency order, enforcing known constraints, fixture/credential safety, and checkpointed failure reporting; use for this project's HRM-style backend API smoke flows.
---

# HRM Pack API Test

This skill is the **built artifact** for the KG/Odoo HRM API collection. The skill-owned runtime collection is `collection/`; the separate `/home/linh/vdx/kg-odoo-hrm-api` collection is kept human-readable for manual Bruno testing. Backend analysis is baked into the generated plan, per-API documents, constraints, aliases, and unknowns under `references/generated/`. Runtime use executes the approved sequence; it does not perform a new analysis mode.

Bruno runtime assumptions are explicit: the login request selects `db_name`, returns the bearer API key, and establishes the Odoo session. Bruno's default cookie settings (`storeCookies: true`, `sendCookies: true`) persist the `session_id` cookie and send it to later requests in the same collection/environment. Do not hardcode a cookie or force an `X-Odoo-Database` header alongside that session; verify the environment database before execution instead.

## Runtime dependency

Execution requires the pinned official Bruno CLI package:

```text
@usebruno/cli@4.2.0 -> bru
```

Install globally with:

```bash
npm install --global @usebruno/cli@4.2.0
```

The same pin is recorded in `package.json`. Verify the installation with:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/check_bruno_cli.py
```

For a local (non-global) install, point the scripts at the local binary with
`BRU_BIN=/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/node_modules/.bin/bru`.

## Execution modes

The skill has exactly two API-test modes:

- **business** (default): run one reviewed HRM business flow, with optional
  steps and destructive cleanup excluded unless the manifest explicitly maps a
  fresh-resource chain.
- **lifecycle**: run a dependency-ordered collection flow, including the
  producer/capture/verify/cleanup rules from
  `references/full-collection-lifecycle-rules.md`.

Both modes start as a dry-run. **Execute only against a disposable local/test
database. Never target shared, staging, or production data.** The environment
file name alone is not proof that the database is safe.

## Runtime entrypoint

Use the sequence runner:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/run_api_sequence.py \
  --mode business \
  --flow leave \
  --env 'KG - local.bru'
```

The command above is a **dry run**. Review the printed ordered steps first. To execute, add `--execute`; to run state-changing or fixture-dependent requests, also add the explicit flags:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/run_api_sequence.py \
  --mode business \
  --flow leave \
  --env 'KG - local.bru' \
  --execute \
  --allow-mutations \
  --allow-hardcoded-fixtures \
  --allow-db-binding \
  --allow-generic-session \
  --include-error-body
```

For lifecycle coverage, select one flow at a time with `--mode lifecycle`:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/run_api_sequence.py \
  --mode lifecycle \
  --flow leave \
  --env 'KG - local.bru'
```

The equivalent package command is:

```bash
npm run test:lifecycle -- --flow leave --env 'KG - local.bru'
```

Do not run the entire collection as one flat test. Select one flow at a time:

- `authentication`
- `reference_data`
- `employee_context`
- `leave`
- `overtime`
- `attendance_explanation`
- `gps_attendance`
- `resignation`
- `staff_transfer`
- `helpdesk`
- `read_only_reports`
- `external_services`

## Auto-configure approval on a new database

After the `approval` module and the modules that define the HRM approval models
are installed in a new database, the ORM configurator can create the required
state mappings, shared approval stage, stage approver line, and one template per
model. It is idempotent for records owned by this skill (the records carry the
marker `[hrm-pack-api-test:approval-config:v1]`) and does not touch
`hr.overtime.request`, which has a separate workflow.

The command is **dry-run/rollback by default**:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_approval.py \
  --db kg-dev-5 \
  --approver admin \
  --originator admin \
  --odoo-bin /home/linh/odoo/odoo-bin \
  --odoo-python /home/linh/vdx/kg-odoo-hrm/.venv/bin/python \
  --config /home/linh/odoo/config/kg.conf
```

Review the JSON report under `/tmp/hrm-pack-api-test/approval-config-*.json`.
Only after confirming the target database, selected users, and the preview,
run the same command with `--apply`. If an existing non-empty state mapping
does not match the source-backed mapping, the script stops safely; add
`--force` only when intentionally replacing that mapping. `--originator`
defaults to `--approver`, but separate users can be supplied.

The script requires an exact user selector (numeric ID, login, email, or a
unique name), checks that `approval` is installed and all 12 expected models
and state values exist, and rolls back on any error. After apply it invokes the
approval registry update and verifies the dynamic fields/methods. It does not
restart Odoo or mutate module source code; a long-running HTTP worker may need
an operator-controlled reload before API requests see the new registry.

`--apply` is a database write: templates use `create_check=True`, so records
created by the selected originator enter the approval flow. Use an explicit
test user on test databases such as `kg-dev-5`; do not use this default setup
for production without reviewing the stage/approver policy.

## Create a calendar fixture for attendance-explanation APIs

`resource.calendar/get_infor_calendar` does not return every calendar in the
database. It returns calendars linked through the logged-in employee's
`job_id.resource_calendar_ids`. On a blank/test database, create an owned
fixture calendar, copy the company's existing attendance schedule (or use the
safe weekday fallback), create/link a job when the employee has none, and
assign the calendar to that job:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_calendar.py \
  --db kg-dev-4 \
  --user admin \
  --odoo-bin /home/linh/odoo/odoo-bin \
  --odoo-python /home/linh/vdx/kg-odoo-hrm/.venv/bin/python \
  --config /home/linh/odoo/config/kg.conf
```

The command is **dry-run/rollback by default**. Review the report under
`/tmp/hrm-pack-api-test/calendar-config-*.json`, then repeat with `--apply`
only after confirming the database and API user. The operation is idempotent
for records marked `[hrm-pack-api-test:calendar-fixture:v1]`; it never uses a
hardcoded calendar ID and does not modify Odoo source code. After apply, run
the attendance-explanation flow so `get_infor_calendar` captures the new
runtime ID before `create_or_update_explanation`.

### Create a leave-allocation fixture for leave APIs

`create_or_update_hr_leave` uses Odoo's standard quota validation. When the
selected leave type has `requires_allocation=True`, the logged-in employee
must have a validated `hr.leave.allocation` covering the generated future
date. On a blank/test database, create the owned allocation fixture with:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_leave_allocation.py \
  --db kg-dev-4 \
  --user admin \
  --odoo-bin /home/linh/odoo/odoo-bin \
  --odoo-python /home/linh/vdx/kg-odoo-hrm/.venv/bin/python \
  --config /home/linh/odoo/config/kg.conf
```

The command is **dry-run/rollback by default**. Review the JSON report under
`/tmp/hrm-pack-api-test/leave-allocation-config-*.json`, then repeat with
`--apply` for the explicitly selected test database. By default it targets the
first active non-overtime leave type requiring allocation (normally `Paid Time
Off`) and allocates 30 days from today with no end date. Use `--leave-type` and
`--days` when the API flow intentionally selects another quota-based type.
The operation is idempotent for the marker
`[hrm-pack-api-test:leave-allocation-fixture:v1]`; it only creates or adjusts
that owned record and validates it through the ORM. It does not restart Odoo
or change module source code.

### Create a reward fixture for read-only report APIs

The collection exposes Reward & Discipline list/detail APIs but no create
route. `get_list_reward_discipline` returns only approved reward transactions,
so a blank/test database may legitimately have no runtime `reward_id`. Create
the owned prerequisite through the ORM fixture script rather than inventing a
new production API endpoint:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_reward_fixture.py \
  --db kg-dev-4 \
  --user admin \
  --odoo-bin /home/linh/odoo/odoo-bin \
  --odoo-python /home/linh/vdx/kg-odoo-hrm/.venv/bin/python \
  --config /home/linh/odoo/config/kg.conf
```

The wrapper is dry-run/rollback by default; add `--apply` only for the
explicitly selected test database. The fixture stores the owned marker
`[hrm-pack-api-test:reward-fixture:v1]` in `reward.discipline.content`,
resolves the selected API user's employee and a reward-capable
`type.reward.discipline`, and creates/updates only that owned record. It is
idempotent and reports its JSON result under `/tmp/hrm-pack-api-test/`. After
apply, rerun `read_only_reports` so the list response captures `reward_id`
before calling the detail endpoint.

### Ensure `vi_VN` is available

The API may carry `vi_VN` as its request language. On a blank database where
only `en_US` is installed, Odoo raises `Invalid language code: vi_VN` while
computing approval metadata. The language configurator installs/activates the
requested language without changing every user's preferred language:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_language.py \
  --db kg-dev-5 \
  --language vi_VN \
  --odoo-bin /home/linh/odoo/odoo-bin \
  --odoo-python /home/linh/vdx/kg-odoo-hrm/.venv/bin/python \
  --config /home/linh/odoo/config/kg.conf
```

Review the dry-run report, then repeat with `--apply` to write the DB. The
operation is idempotent: it creates `res.lang` only when missing, otherwise
activates the existing row. It does not restart Odoo or set all users to
Vietnamese automatically.

### Configure Group-A API fixtures

For the remaining Group-A flows, prepare the shared test fixtures in one
idempotent step:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/configure_group_a_fixtures.py \
  --db kg-dev-4 --user admin --apply
```

This owns only marked test records for an area category, an overtime leave
type, and the employee's validated overtime allocation. It does not change
application source or mask backend errors such as the resignation
`onboard_time=False` comparison. Review the dry-run first on another DB.

The runner resolves dependency closure, prints the exact order, runs the
selected `.bru` requests in **one Bruno CLI process** (required for cookie
session and `bru.setVar` ID chaining), writes body/header-free JSON reports,
and stops at the first failure. Checkpoints are written under
`/tmp/hrm-pack-api-test/<timestamp>/`.

When testing all APIs, use the reviewed business/lifecycle sequences rather
than a flat per-file scan. `--all` on `test_business_flows.py` means one
dependency-ordered Bruno process per business; it does not mean that every
collection file is sent independently. A request omitted from a business
sequence is a mapping/coverage gap to resolve, not an invitation to execute it
standalone.

The business runner reads `runtime_producers` from
`references/business-test-plan.yaml` and recursively inserts each canonical
producer before its consumer. Therefore a request such as a detail, workflow,
attachment, or cleanup endpoint is tested as a real chain (`lookup/create or
upload -> capture runtime ID -> consumer`), not skipped merely because it
needs runtime data. Aliases are never inserted into these chains.

The canonical create-to-detail/upload/workflow branches now use Bruno response
scripts (`bru.setVar`) to chain IDs at runtime. The runner still does **not**
rewrite request bodies or infer IDs for standalone fixture requests; those
requests remain operator-managed and require explicit fixture confirmation.

Quick CLI smoke test (dry-run by default):

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/test_bruno_cli.py \
  --flow employee_context \
  --env 'KG - local.bru'
```

Add `--execute` and the required approval flags only when you intentionally
want to send requests.

## Test theo từng nghiệp vụ

Use the business runner when the goal is to verify an HRM nghiệp vụ end to
end, rather than execute an arbitrary API flow. The source-backed manifest is
[`references/business-test-plan.yaml`](references/business-test-plan.yaml). It
keeps each business in a reviewed order, prepends login once, selects one
approval variant, and starts a separate Bruno process/session for every
business so cookies and runtime IDs cannot leak across transactions.

List the available business groups:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/test_business_flows.py --list
```

Run one business as a dry-run (the runner prints the exact ordered
requests and reports any missing explicit approvals):

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/test_business_flows.py \
  --business leave \
  --variant approve
```

Execute one stateful business only after confirming the target database and
fixtures. `--allow-mutations`, `--allow-hardcoded-fixtures`,
`--allow-db-binding`, and `--allow-generic-session` are independent safety
confirmations; add only the ones that apply:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/test_business_flows.py \
  --business leave \
  --variant approve \
  --execute \
  --allow-mutations \
  --allow-hardcoded-fixtures \
  --allow-db-binding \
  --allow-generic-session
```

Approval branches are alternatives, not one combined sequence. Use
`--variant reject` to exercise rejection, or `--variant none` to stop after
submission/final read checks. Optional uploads and device/attachment steps
are excluded unless `--include-optional` is supplied. Use `--all` only when
every business has been intentionally approved. `--continue-on-failure` collects remaining
results instead of stopping at the first failed business.

The aggregate report and one sanitized log per business are written below
`/tmp/hrm-pack-api-test/business-<timestamp>/`. A business is successful only
when Bruno reports every selected request as passing and the declared
preconditions/response checks have been reviewed; an HTTP 2xx by itself is
not a business assertion. The report automatically verifies checkpoint
request status and declared HTTP-status ranges; body-field/state assertions
remain explicitly listed for review (the status is
`passed_transport_review_required`) because response bodies are omitted from
the persisted report to avoid leaking tokens or PII. Manifest steps marked
`fixture_required` are blocked until `--allow-hardcoded-fixtures` is supplied.
The business runner never includes arbitrary destructive cleanup in default
paths; any cleanup that is present must be explicitly mapped to a fresh
resource in the reviewed manifest.

Use `--include-error-body` when debugging a failed API. It keeps only a
recursively redacted response body for failed requests; successful response
bodies and all headers remain removed.

## Full collection lifecycle rules

The normal business mode intentionally avoids destructive cleanup and
operator-owned fixtures. Lifecycle mode uses the source-of-truth policy in
[`references/full-collection-lifecycle-rules.md`](references/full-collection-lifecycle-rules.md).
The important rules are:

- Delete/cancel/reset/reject requests must run only against a fresh record
  created in the same sequence; capture and reuse its runtime ID.
- Account deletion is always `sign_up -> verify/login -> delete` for the new
  account. Never delete or change the configured operator/admin account.
- Employee document tests are `upload -> capture attachment ID -> verify ->
  delete` for a designated test employee and a non-sensitive placeholder file.
- Detail/workflow/attachment/cleanup requests without a producer for their
  runtime ID are mapping gaps; create the prerequisite fixture or classify the
  result as `fixture_unavailable`.
- A runtime-dependent consumer must never run standalone: call the producer
  listed in `references/full-collection-lifecycle-rules.md` first, keep both
  requests in the same Bruno process, capture the returned ID with
  `bru.setVar`, and only then send the consumer request. If the producer does
  not return a valid ID, stop that chain and report `fixture_unavailable` (or
  the concrete backend error); do not fall back to a historical ID.
- **Both business and lifecycle modes must resolve dependencies before sending a request.**
  A full sweep is not permission to fire each `.bru` file independently. For
  every endpoint, inspect its source-backed dependency/runtime map and add the
  required producer(s) to the business sequence. If no producer chain exists,
  fix the mapping or classify the endpoint as `fixture_unavailable`; do not run
  it merely to collect an error response.
- Results from a standalone probe of a runtime-dependent endpoint must never
  be counted as a backend failure or a passed API. Only the same-business
  producer -> capture -> consumer chain is authoritative for that endpoint.
- `_2`/other duplicate route files are aliases, not new capabilities. Leave
  aliases untouched and deferred in this phase; do not rename, rewrite, map, or
  execute them. The canonical route remains the source of truth.
- `manual`/`fixture_required` steps must be converted to a reviewed setup chain
  for a full sweep; never guess a historical numeric ID.

## Safety contract

- Confirm the exact environment/database before `--execute`; use only a disposable local/test DB. Never use shared, staging, or production data.
- Never expose bearer tokens, cookies, passwords, or external API keys.
- `--allow-mutations` is required for create/update/upload/workflow/delete/preview operations.
- `--allow-hardcoded-fixtures` is required when standalone collection bodies still contain numeric IDs. Prefer the canonical create-to-detail chains; the runner does not silently rewrite request bodies.
- `--allow-db-binding` is required for execution after verifying that login/session and database selection target the intended database. This is an operator confirmation, not an unresolved code blocker.
- `--allow-generic-session` is required for `/api/models/*` generic/upload routes because their backend declaration uses `auth="user"` and needs the persisted Odoo session cookie that Bruno carries after login, not only a bearer token. This is an accepted runtime constraint.
- `Staff Transfer/create_or_update_staff_transfer_2.bru` is a non-default alias. Literal bearer/Cookie headers were removed; prefer the canonical JSON-2 request.
- Do not run destructive APIs as standalone smoke requests. In a full sweep,
  run them only through the fresh-resource lifecycle rules above, with cleanup
  IDs captured from that lifecycle.
- Do not delete the configured account or change its password. Account-delete
  coverage must create a unique test account first and delete only that account.
- Do not delete hardcoded employee/attachment fixtures. Upload a placeholder
  document, capture its returned ID, and delete that exact attachment.
- Leave duplicate aliases untouched for now. The generated plan marks aliases
  such as `*_2` and the generic staff-transfer variant with
  `default_execution: false`; they are deferred, not silently treated as
  tested coverage.
- Do not claim business success from HTTP `2xx` alone. Verify returned `id`, `state`, approval progress, and the Bruno report. This collection currently has no meaningful request assertions beyond login's token script.
- No Docker/service start or restart is performed by this skill.

## Built-in flow order

The baked guide uses a common prefix and independent domain branches:

```text
login
  -> current employee/reference context
  -> one selected business flow
  -> capture/verify record id/state (manual or response-script dependent)
  -> detail/list verification
  -> optional upload
  -> submit
  -> approve OR reject
  -> final detail/progress verification
```

Canonical branches are documented in [references/kg-odoo-hrm-flows.md](references/kg-odoo-hrm-flows.md). The exact per-request order is in `references/generated/api-execution-order.json`; one Markdown file per ordered request is in `references/generated/docs/`.

## Important baked constraints

- Login creates a 30-day API key and stores it as Bruno secret `token`.
- Most business APIs require the authenticated user to map to `hr.employee`.
- Canonical create responses are chained into later IDs using flow-scoped variables (`leave_id`, `overtime_id`, `explanation_id`, `resignation_id`, `staff_transfer_id`, `ticket_id`, `attendance_log_id`); remaining standalone numeric IDs are manual fixtures, not automatically inferred.
- Leave requires a valid employee, leave type, quota/date validity, and approval configuration.
- Leave business tests no longer use a fixed historical date: the canonical
  availability request generates one random weekday 3–45 days in the future
  and stores it in runtime variables reused by leave creation. The generated
  date is process-scoped and is not persisted to the environment file.
- Overtime has a same-day date constraint.
- Attendance explanation requires employee/date/reason/calendar and unique employee/date; time intervals must be valid.
- GPS attendance requires a job with `allow_gps_attendance=True`; a second create call can toggle check-in to check-out.
- Resignation and staff-transfer approval require configured approval templates/stages and an authorized approver, not only the correct record state.
- Helpdesk attachment deletion uses `ticket_attachment`, matching the model and upload/detail paths. The previous `evidence_attachment` mismatch was fixed and verified against a fresh create → upload → delete flow on `kg-dev-4` (the already-running HTTP process must reload the module before serving the patched method).
- Reward/report endpoints are read-only and require existing approved/validated data; an empty result on a blank DB is not automatically an API failure.

## Targeted validation record

- Before the source fix, the live Helpdesk API returned HTTP 500 with an
  `evidence_attachment` attribute error after a fresh create → upload → delete
  sequence.
- After changing the source to `ticket_attachment`, upgrading `vdx_hr_custom`
  on `kg-dev-4`, and running the same operation through an Odoo shell loaded
  from the current source, deletion returned `success: true` and removed the
  attachment. The long-running HTTP process was not restarted by this skill;
  reload/restart it before claiming the live HTTP route is fixed.

## Generated build artifacts

- `references/business-test-plan.yaml` — reviewed per-business sequences,
  preconditions, expected checks, fixtures, safety levels, and approval
  alternatives.
- `scripts/test_business_flows.py` — executes one isolated business at a time
  and writes an aggregate checkpoint/report.
- `references/generated/api-execution-order.json` — 147 executable request nodes, deterministic dependency order, operation/alias/evidence metadata.
- `references/generated/api-execution-order.yaml` — same plan in the skill's YAML-named artifact format.
- `references/generated/api-dependency-graph.yaml` — dependency edges.
- `references/generated/api-constraints.yaml` — constraints, fixture risks, and side effects.
- `references/generated/api-unknowns.yaml` — unresolved/cycle findings (must be reviewed before execution).
- `references/generated/docs/NNN-*.md` — one ordered document per API.

The build-time scanner remains available for refreshing the artifacts after a backend/collection change:

```bash
python3 /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/scripts/build_api_guide.py \
  --collection /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection \
  --source /home/linh/vdx/kg-odoo-hrm \
  --out /home/linh/Workspace/my-skills/skills/hrm-pack-api-test/references/generated
```

Refreshing is a build/maintenance operation, not a runtime `analyze` mode. After refresh, review unknowns and generated order before executing flows.
