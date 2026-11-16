---
name: odoo-code
description: Code, debug, test, refactor, and review scoped Odoo changes in any Odoo project using source-first implementation rules.
---

# Odoo Code

Use this skill for coding, debugging, testing, refactoring, or code review work in
any Odoo project. Determine the active repository and project conventions from
the user's context and the checked-out source; do not assume a fixed repository
path or product-specific structure. Keep changes focused on the requested module,
feature specification (FS), issue, or acceptance criteria.

## Local Odoo source roots

- `/home/linh/odoo-versions` contains Odoo Community source trees.
- `/home/linh/odoo-enterprise-versions` contains Odoo Enterprise source trees.
- When a task concerns Odoo upstream source and the user has not specified a
  checkout, use the relevant root to locate the Community or Enterprise code,
  then inspect the actual checkout and version before drawing conclusions or
  making changes. Explicit repository context from the user takes precedence.

## Explicit-request rules

- Treat this as a standing rule for Odoo work: never create, edit, delete, rename, or move files in an `i18n/` directory, and never create, delete, rename, or move an `i18n/` directory. If a task appears to require an i18n change, leave it untouched and explain the constraint unless the user explicitly revises this standing rule.
- Do not create or modify Odoo access permissions, including ACLs, record rules, or group access assignments, unless the user explicitly requests them.
- Do not write, add, or update unit tests unless the user explicitly requests them.
- Do not run tests unless the user explicitly requests them.
- Do not create or modify database migration scripts unless the user explicitly requests them.
- For requests that may require Odoo code changes, first inspect the relevant source and present the proposed solution for the user to review. Do not edit or implement code until the user explicitly confirms that implementation should proceed.

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
- Do not use `lambda` expressions merely to make code shorter. Prefer a named
  function or explicit control flow when that makes the code easier to read,
  debug, or maintain.
- Do not add implicit backend behavior unless the user explicitly requests it. This applies to `create`, `write`, constraints, computed fields, hooks, and other server-side paths. If you think such behavior is needed but was not requested, explain the expected behavior and wait for confirmation before implementing it.
- When requested or proposed behavior could use `@api.onchange`, a computed field, or an existing Odoo base feature, tell the user which Odoo-native options fit and ask them to confirm the implementation approach before proceeding. Proceed without another confirmation only when the user explicitly specifies the mechanism or has already confirmed it.
- Prefer existing real fields and relations over proxy or duplicate fields.
- Do not expand a direct field mapping into unrelated UI domains, business rules, reports, or model redesign.
- Match actual technical values in source selections; do not filter by translated labels.
- For FS work, distinguish fields used for output values, user-entered filters, UI domain/validation, and fields outside scope.
- Treat an FS as implementation guidance, not unquestionable authority. Check its requirements for consistency with the source, technical constraints, and coherent behavior. If an FS requirement is unreasonable or conflicts with those, report it to the user immediately with evidence; do not silently implement it as written.
- When source and FS disagree, report the exact conflict and avoid silently choosing a rule unless the task authorizes that decision.
