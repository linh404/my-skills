---
name: barett-automation-test
description: >-
  Test the local Barett Odoo ERP project through a browser automation
  workflow. Use for Barett BA acceptance checks, regression tests, and issue
  verification. Do not use for other Odoo projects or production systems.
---

# Barett Odoo automation testing

This is the `barett` project-specific skill. Keep Barett's custom workflows, routes,
fixtures, database rules, and issue set here; do not route this project through
a generic Odoo test profile.

## Target and MCP

- Repository: `/home/linh/vdx/barett-odoo-erp`
- Local URL: `http://localhost:8069/odoo`
- Test database for this project: `barett-dev-3`; verify the running process
  and config before every run.
- Config: `/home/linh/odoo-versions/config/barret.conf`
- Odoo executable: `/home/linh/odoo-versions/18.0/odoo-bin`
- Python: `/home/linh/vdx/barett-odoo-erp/.venv/bin/python`
- Addons include `/home/linh/vdx/barett-odoo-erp/addons/vdx`.
- Odoo application login is the local project credential `admin/admin`; never
  print it or use it outside this exact local URL/database.
- For each test run, handle the Chrome/DevTools MCP connection yourself by
  connecting one MCP to one temporary Chrome profile and using that profile for
  the whole run.
- Follow [references/chrome-devtools-mcp.md](references/chrome-devtools-mcp.md)
  to start, handshake, verify, and retain that isolated browser connection.
- Before opening the requested Odoo or IssueList workflow, complete the
  snapshot preflight in that reference. A successful handshake alone is not
  enough; `take_snapshot` must return on `about:blank` and then on the Odoo
  login page.

## Browser-first rule

- Use the browser automation context for acceptance actions:
  navigate, snapshot, inspect DOM/a11y state, click, fill, keyboard, and
  cancel/close exploratory dialogs.
- Do not use RPC/JSON-RPC to simulate an acceptance action or to claim a UI,
  workflow, validation, permission, or domain test as passed. In particular,
  do not call `/web/dataset/call_kw` for create/write/unlink/approve/reject.
- If the UI cannot expose a needed fact, use source inspection and read-only SQL
  for corroboration. RPC is diagnostic-only and requires an explicit reason;
  it is never the primary evidence for an acceptance result.

## Fixture completion before `NOT TESTED`

Do not report `NOT TESTED` merely because a required record, state, role,
partner, line, or approval setup is missing. First inspect whether the
precondition can be created or prepared entirely through the Odoo UI in the
local `barett-dev-3` database. If it can be made safely, create a disposable
fixture and continue the requested criterion in the same run.

- Use a clearly searchable QA marker containing the run ID, avoid changing an
  existing business record, and keep the fixture setup in the browser flow.
- Record the fixture URL, before/after state, created values, resulting side
  effects, and retention status in the test-run report. Promote the setup flow
  to the canonical workflow when it is reusable.
- Use only UI create/write/state-transition actions for the fixture. Do not
  use RPC, direct SQL writes, or a service restart to manufacture coverage.
- Fixture cleanup is not required and must not be performed automatically.
  Leave the QA fixture in the local test database, clearly marked with its run
  ID, and report it as retained. Only delete or otherwise clean up a fixture
  through the UI when the user or the requested criterion explicitly requires
  cleanup and the operation is safe; never silently restore an existing record.
- If the fixture cannot be created through the UI because of permissions,
  unavailable dependencies, or an unsafe irreversible side effect, report
  `BLOCKED` with the missing condition. Reserve `NOT TESTED` for a criterion
  that cannot be executed and has no safely UI-creatable fixture path, with
  that reason recorded.

## Fallback methods and evidence paths

When an operation fails, do not repeat the same failed method blindly. Classify
the failure and use another permitted method that can establish the same fact:

- If a DB query fails, check the active config/credentials and then use an
  equivalent read-only DB path, source inspection, Odoo UI, process logs, or
  installed-module metadata as appropriate.
- If source lookup fails, locate the owning module with `rg`, inspect its
  manifest/imports, then trace the model, view, field, or route from the
  nearest known reference.
- If a browser route fails, try the known menu/action/direct route while
  verifying the same database and browser context.
- If UI cannot expose the fact, combine source and read-only DB evidence. Do
  not replace an acceptance click with RPC; RPC is diagnostic-only and cannot
  be the primary `PASS` evidence.
- Record the failed method, the replacement method, why it is equivalent, and
  the evidence obtained. On the next run, start with the recorded replacement
  instead of repeating the known-bad method.
- A product-behavior failure must remain `FAIL`; changing the inspection method
  is for reaching evidence, not for hiding a validation, domain, permission,
  or workflow defect. If no permitted method can establish the fact, report
  `BLOCKED` and state what is missing.

## Issue list and scope

- IssueList: [Google Sheets issue list](https://docs.google.com/spreadsheets/d/1QWhfXGtb2Y88rM-CDQAZ2IZU2PMAk2I2MODcBfwovvQ/edit?gid=418735784#gid=418735784).
- Open/read the IssueList only when the user explicitly asks to consult it or
  requests a test of an issue using its IssueList criteria. Otherwise, do not
  open it. When requested, use the browser context for the test and locate the
  row whose `STT` in column A equals the requested issue number. For example,
  issue 41 means the cell containing `41` in column A; use that row's criteria,
  status, and supporting details as the test scope.
- Do not impose a hardcoded issue-number allowlist. Any issue present in column
  A may be inspected and tested when requested. Do not edit the sheet.
- If the requested `STT` is missing, ambiguous, or its acceptance criteria are
  not readable, report `BLOCKED` and state the missing evidence instead of
  guessing.

Source and runtime evidence must stay attached to each result: issue ID, BA
criterion, source file/line, action or record URL, database, active Odoo
process/config, precondition, observed UI text/state, and result
`PASS|FAIL|BLOCKED|NOT TESTED`.

## Test-run archive and reusable UI workflows

Every browser-based test run that reaches an Odoo view must leave a durable
test-run record, including runs that end in `FAIL`, `BLOCKED`, or `NOT TESTED`.
Do not rely on chat history as the test record. Store records under:

- `references/test-runs/YYYY/MM/YYYY-MM-DD--HHmmss--<scope>.md` for an
  immutable record of one execution. Use Asia/Ho_Chi_Minh time, and never
  overwrite an earlier run; a new execution gets a new file.
- `references/workflows/<area>/<workflow-slug>.md` for a canonical, reusable
  UI workflow. Use a model/menu area such as `purchase-request`,
  `purchase-order`, `sales-plan`, `users`, or `shared`.

Before opening or acting in the browser, search the workflow archive and reuse
the closest verified flow. After the run, update or create the canonical flow
only when the observed route, labels, controls, preconditions, or fixture
retention/side-effect steps are new or changed. The run record must link every
workflow it used and must still contain the exact observed action sequence for
that run; a link
alone is not sufficient evidence.

Each run record must include frontmatter that is easy to query with `rg`:
`run_id`, `executed_at`, `timezone`, `scope`, `issue_ids`, `database`,
`odoo_url`, `config`, `active_pid`, `chrome_profile`, `result`, and
`workflow_refs`. Never store credentials, cookies, tokens, or other secrets.
For every Odoo view criterion,
record a numbered UI flow with
the starting URL/menu, visible label or stable DOM/a11y anchor, input/click or
navigation, expected result, observed result, evidence, and fixture-retention
or side-effect state. Record dynamic IDs as variables rather than copying them
into a reusable workflow. Never store passwords, cookies, tokens, or other
secrets in either archive.

Canonical workflows must state their purpose, applicable issue/criterion,
preconditions and fixture state, numbered reusable steps, expected visible
states, fixture-retention/side-effect notes, source/runtime references, and known
pitfalls. A workflow is a navigation/action reference, not a substitute for
the result of a particular run. Keep durable product discoveries in
`references/lessons.md` separately.

Use [references/test-recording.md](references/test-recording.md) for the
record schemas and query examples. The archive directories have their own
short routing notes at [references/test-runs/index.md](references/test-runs/index.md)
and [references/workflows/index.md](references/workflows/index.md).

## Barett routes and high-value records

- Purchase requests: `/odoo/action-529` or `/odoo/purchase.request/<id>`.
- RFQs/POs: `/odoo/purchase` or `/odoo/purchase/<id>`.
- Users: `/odoo/users`; open the new form only to inspect fields unless an
  authorized disposable-user test is available.
- Sales plans: `/odoo/action-793` (annual) and `/odoo/action-794` (monthly).
- Existing useful records: PR `9`, `14`, `18`, `23`, `26`, `27`, `28`; PO/RFQ
  `11`, `14`, `15`; sales-plan QA records marked `[QA-ISSUE-18-21]`.
- A prior test left monthly plan ID `73` in `confirmed` state after the
  approval flow. Treat it as changed test data and do not assume it was draft.

## Barett-specific checks

- PR tier approval and RFQ policy/price approval are different systems. Do not
  use the RFQ rejection wizard as evidence for PR issue 34.
- For PRs, inspect the rendered header by state. The relevant custom view is
  `addons/vdx/barett_purchase_request/views/purchase_request_views.xml` and
  the server guard is
  `addons/vdx/barett_purchase_request/models/purchase_request.py`.
- For RFQs, inspect both approval badges and header buttons. The relevant view
  is `addons/vdx/barett_purchase_request/views/purchase_order_views.xml`.
- For the PR-to-RFQ supplier popup, inspect autocomplete suggestions and
  corroborate partner `supplier_rank` with read-only SQL. A Python context
  such as `res_partner_search_mode=supplier` is not proof that the runtime
  domain works.
- For translation issues, verify visible Vietnamese labels in both the PR
  form and line list/form; a loaded page alone is not enough.

## Runtime freshness and reporting

If the browser reports an undefined field, missing view, Owl error, stale
translation, or a source/runtime mismatch:

- Read [references/runtime-diagnostics.md](references/runtime-diagnostics.md)
  and perform read-only diagnosis. Report the evidence and likely cause to the
  user; do not change the database, update modules, restart services, or run a
  fix unless the user explicitly asks for that action.

1. Record URL, database, active PID, config, addons paths, owning module, and
   the exact error.
2. Check the source declaration and installed module state. If source contains
   the field/view but runtime says it is undefined, treat it as stale registry,
   wrong addons path, stale view, or missing module update before calling it a
   code defect.
3. Check read-only process information for an existing `--stop-after-init`
   operation targeting the same DB. Do not start, wait for, stop, or interfere
   with an update; report any matching process and its observed state.
4. Report the exact evidence, diagnosis, and a concise suggested next action.
   Do not execute the suggested fix without an explicit user request.

## Ownership and extension

This is the standalone automation skill for `/home/linh/vdx/barett-odoo-erp`.
Keep its browser workflow, source maps, fixture guidance, runtime diagnostics,
and lessons here. When another Odoo project is introduced, create a separate
project-named skill with its own workflow instead of adding another project
branch here. Record only verified Barett findings in
[references/lessons.md](references/lessons.md).
