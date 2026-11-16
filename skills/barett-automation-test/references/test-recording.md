# Barett test recording convention

This reference defines the durable record format for browser-based Barett
tests. It keeps individual evidence separate from reusable UI knowledge.

## Archive split

```text
references/
├── test-runs/
│   └── YYYY/MM/YYYY-MM-DD--HHmmss--<scope>.md
├── workflows/
│   └── <area>/<workflow-slug>.md
├── lessons.md
└── runtime-diagnostics.md
```

- `test-runs/` is an append-only execution archive. One file represents one
  browser test run and remains useful even when the result is not a pass.
- `workflows/` is the maintained catalog of UI flows that can be reused by
  later runs. Update it when a verified flow changes; do not create a new
  copy merely because the same flow was executed again.
- `lessons.md` contains durable Barett product/testing discoveries, not routine
  click logs.
- `runtime-diagnostics.md` contains the source/runtime mismatch procedure.

## Run-record schema

Start every run record with compact YAML frontmatter. Keep values plain and
searchable; do not put credentials or session material in the file.

```yaml
---
run_id: 2026-11-04--143015--issue-41
executed_at: 2026-11-04 14:30:15
timezone: Asia/Ho_Chi_Minh
scope: issue-41
issue_ids: [41]
database: barett-dev-3
odoo_url: http://localhost:8069/odoo
config: /home/linh/odoo-versions/config/barret.conf
active_pid: "<verified PID>"
chrome_profile: MCP isolated temporary profile, fresh and non-headless
result: PASS
workflow_refs:
  - references/workflows/purchase-order/issue-41-positive-line-validation.md
---
```

Then use this body structure:

```markdown
# Test run — Issue 41

## Scope and preconditions

- BA criterion:
- User/company/language:
- Record URL(s):
- Fixture state before the run:
- Source/runtime references:

## UI flow executed

1. Start at `<URL or menu>`; verify `<visible anchor>`.
2. Click/fill `<visible label or stable anchor>` with `<safe value>`.
3. Observe `<expected UI state>`; actual: `<observed state>`.
4. ...

## Evidence and result

- Expected:
- Observed:
- Evidence:
- Side effects and cleanup:
- Result: `PASS|FAIL|BLOCKED|NOT TESTED`

## Deviations or replacement methods

- Failed method:
- Replacement method and why it is equivalent:
- Evidence obtained:
```

For multiple criteria, repeat `## UI flow executed` and `## Evidence and
result` per criterion, or use one numbered flow with clearly labeled branches.
Never omit the action sequence because a canonical workflow already exists.

## Fixture completion and result classification

When a precondition is missing, record the fixture setup before the acceptance
steps. If the fixture can be created safely through the Odoo UI on
`barett-dev-3`, create it with a run-ID QA marker and continue the criterion;
do not classify that branch as `NOT TESTED`. Include the fixture URL, created
values, before/after state, side effects, and cleanup status in the same run
record.

Use the result states in this order:

1. `PASS` or `FAIL` after executing the criterion with an existing or
   UI-created fixture.
2. `BLOCKED` when a UI-created fixture is not possible because of permission,
   missing dependency, or unsafe irreversible side effect.
3. `NOT TESTED` only when the criterion cannot be executed and there is no
   safely UI-creatable fixture path; state the reason explicitly.

## Canonical workflow schema

Store one workflow at `references/workflows/<area>/<workflow-slug>.md`:

```markdown
---
workflow_id: purchase-order-issue-41-positive-line-validation
area: purchase-order
models: [purchase.order, purchase.order.line]
views: [purchase.order.form]
issue_ids: [41]
status: verified
last_verified: 2026-11-04
---

# Positive-line validation before approval

## Purpose

## Preconditions and fixtures

## Reusable UI steps

1. ...

## Expected visible states

## Side effects and cleanup

## Source/runtime references

## Known pitfalls
```

Keep steps anchored to visible labels, menu names, URLs, and stable a11y/DOM
anchors. Replace record-specific IDs, timestamps, and generated values with
`<record id>`-style variables, while keeping the concrete record URL in the
individual run report.

## Querying the archive

Use `rg` against frontmatter and headings before a new run:

```bash
rg -n "issue_ids:.*41|workflow_id:.*purchase-order|views:.*purchase.order" \
  /home/linh/.codex/skills/barett-automation-test/references/workflows \
  /home/linh/.codex/skills/barett-automation-test/references/test-runs
```

List the newest run records without reading every file:

```bash
rg --files /home/linh/.codex/skills/barett-automation-test/references/test-runs \
  | sort -r
```

If no matching workflow exists, create it from the verified steps in the new
run record. If an existing workflow no longer matches the UI, preserve the
run's observed steps, update the canonical workflow with the verified change,
and note the deviation in the run record.
