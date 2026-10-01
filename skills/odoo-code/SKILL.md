---
name: odoo-code
description: Code, debug, test, refactor, and review scoped Odoo changes in the SCA repository using source-first implementation rules.
---

# Odoo Code

Use this skill for coding, debugging, testing, refactoring, or code review work in:

```text
/home/linh/vdx/sca
```

The repository is an Odoo codebase. Keep changes focused on the requested module,
FS, issue, or acceptance criteria.

## Source of truth

- Answer questions and make decisions from actual source content and runtime data, not filenames, Git status, Git statistics, metadata, or assumptions.
- Treat source content as authoritative. Git metadata can help locate evidence but must never be the sole basis for a conclusion.
- When determining whether files or revisions are identical, inspect their actual contents or byte-level hashes; use a complete diff for text.
- Before destructive or potentially data-losing Git operations, verify the exact source revision/content and preserve relevant local state.
- If evidence is incomplete, state that the result is unverified instead of guessing.
- Do not claim a change was preserved, restored, or recovered unless the actual content was checked against the source state.

## Scope and relation tracing

- Start from the exact field, model, method, view, test, or FS item named by the request.
- Read the field declaration and direct consumers first. Stop once the requested behavior is supported by verified evidence.
- Do not trace into the related model of a `Many2one`, `Many2many`, or `One2many` merely because the relation exists.
- Inspect a related model only when the requested behavior needs its field, domain/validation, computed value, join, constraint, output, lifecycle rule, or domain understanding that cannot be established from direct source.
- Keep these layers separate: reading a relation value, identifying its target, and inspecting target fields. Only inspect target fields when the requirement or direct source requires it.
- If a related rule may matter but is outside scope, record it as an open question instead of implementing or presenting it as required.

## Implementation discipline

- Inspect relevant source, existing module patterns, and tests before editing.
- Prefer existing real fields and relations over proxy or duplicate fields.
- Do not expand a direct field mapping into unrelated UI domains, business rules, reports, or model redesign.
- Match actual technical values in source selections; do not filter by translated labels.
- Add or update focused tests for changed behavior. Do not change unrelated tests or behavior.
- For FS work, distinguish fields used for output values, user-entered filters, UI domain/validation, and fields outside scope.
- When source and FS disagree, report the exact conflict and avoid silently choosing a rule unless the task authorizes that decision.
