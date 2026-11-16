---
name: odoo-commit
description: Prepare focused branches, commits, rebases, and pushes for Odoo repositories across projects.
---

# Odoo Commit

Use this skill for branch creation, commit messages, rebases, and pushes in any
Odoo repository. Follow repository-specific contribution instructions when they
exist. Inspect the repository's guidance and remotes to identify the push remote
and the actual merge target; do not assume remote names or target branches.

Keep each standalone change on a focused branch and one logical commit when
practical.

Do not stage or commit `.gitignore` changes as part of a feature or issue fix.
Leave local `.gitignore` modifications untouched unless the user explicitly asks
for that `.gitignore` change to be included.

## Repository workflow

- For every standalone change that is not a rebase/amend continuation, create a fresh dedicated branch from the actual merge target branch. Do not commit directly on a default branch or an unrelated branch.
- Prefix every new branch with `linhlh/`, then use `<change-type>/<module>-<short-description>[-<issue>]` in lowercase kebab-case, using the actual module name and issue number when available. Keep `<short-description>` to at most four words. For example: `linhlh/fix/barett-sales-plan-adjustment-flow`.

## Commit messages

For functionality or non-issue changes:

```text
[TYPE] <module_name>: <mô tả ngắn bằng tiếng Việt>
```

For issue fixes:

```text
[FIX] <module/model>: <mô tả ngắn bằng tiếng Việt> (#<issue>)
```

Write the description after `:` in concise Vietnamese. Keep it short while clearly naming the changed behavior or affected model/view.

Add `Fixes #<issue>` in the body when the issue should close automatically after merge.

The `<description>` must state clearly what the issue fixes, including the affected
module/model/view or user-visible behavior. Do not use a generic description such
as `fix issue` or only repeat the issue number. For example:

```text
[FIX] hr.employee: ẩn trường VDX trên form (#4)
```

If no issue number is provided, do not invent one; use the module format for a
non-issue commit or ask for the issue number when the change is explicitly an
issue fix.

## New change

```bash
git fetch <target-remote>
git switch -c linhlh/<change-type>/<module>-<short-description>[-<issue>] <target-remote>/<target-branch>
# make changes
git add <files>
git commit -m "[TYPE] module: mô tả thay đổi ngắn gọn"
git push -u <push-remote> linhlh/<change-type>/<module>-<short-description>[-<issue>]
```

Create the merge request from `<push-remote>/<branch>` into the actual merge target.

## Rebase or non-fast-forward

When the merge target moved or GitLab requires a rebase:

```bash
git fetch --all --prune
git switch linhlh/<type>/<short-name>
# For substantial or complex logic changes only:
git branch backup/linhlh-<short-name>-before-rebase
git rebase <target-remote>/<target-branch>
# resolve conflicts, then: git add <file> && git rebase --continue
git push --force-with-lease <push-remote> linhlh/<type>/<short-name>
```

If the pushed branch contains commits not present locally, integrate it before
rebasing onto the merge target:

```bash
git fetch --all --prune
git rebase <push-remote>/linhlh/<type>/<short-name>
git rebase <target-remote>/<target-branch>
git push --force-with-lease <push-remote> linhlh/<type>/<short-name>
```

For small mechanical changes, such as Ruff-only fixes or unit-test-only changes, skip creating the backup branch before rebasing. For substantial or complex logic changes, create it before rewriting history.

Rules:

- Use `git push --force-with-lease` after a rebase; never plain `git push --force`.
- Do not use `git pull` blindly; it can merge the wrong branch.
- Compare against the actual merge target, not only the push remote's default branch.
- For a standalone single-fix branch, prefer rebase/amend over merging the target branch into it.
