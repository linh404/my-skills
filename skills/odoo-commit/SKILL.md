---
name: odoo-commit
description: Prepare focused SCA Odoo branches, commits, rebases, and pushes using the repository's fork-based contribution workflow.
---

# Odoo Commit

Use this skill for branch creation, commit messages, rebases, and pushes for the
SCA Odoo repository:

```text
/home/linh/vdx/sca
```

Keep each standalone change on a focused branch and one logical commit when
practical.

## Repository workflow

- `origin` is the contributor fork used for pushing source branches.
- `upstream` is the company repository and source of truth for the merge target.
- The normal merge target is `upstream/dev`, not `origin/dev`.
- For every standalone change that is not a rebase/amend continuation, create a fresh dedicated branch from `upstream/dev`; do not commit directly on `dev`, `origin/dev`, or an unrelated branch.
- Name branches as `<change-type>/<module>-<short-description>[-<issue>]` in lowercase kebab-case, using the actual module name and issue number when available.

## Commit messages

For functionality or non-issue changes:

```text
[TYPE] <module_name>: <description>
```

For issue fixes:

```text
[FIX] issue: <description> (#<issue>)
```

The issue format overrides the module format. Add `Fixes #<issue>` in the body when the issue should close automatically after merge.

## New change

```bash
git fetch upstream
git switch -c <change-type>/<module>-<short-description>[-<issue>] upstream/dev
# make changes
git add <files>
git commit -m "[FIX] module: describe the fix"
git push -u origin <change-type>/<module>-<short-description>[-<issue>]
```

Create the merge request from the new `origin/<branch>` into `upstream/dev`.

## Rebase or non-fast-forward

When the merge target moved or GitLab requires a rebase:

```bash
git fetch --all --prune
git switch <type>/<short-name>
git branch backup/<short-name>-before-rebase
git rebase upstream/dev
# resolve conflicts, then: git add <file> && git rebase --continue
git push --force-with-lease origin <type>/<short-name>
```

If the contributor fork contains commits not present locally, integrate it before
rebasing onto the company target:

```bash
git fetch --all --prune
git rebase origin/<type>/<short-name>
git rebase upstream/dev
git push --force-with-lease origin <type>/<short-name>
```

Rules:

- Use `git push --force-with-lease` after a rebase; never plain `git push --force`.
- Create a backup branch before rewriting history.
- Do not use `git pull` blindly; it can merge the wrong branch.
- Compare against the actual MR target, normally `upstream/dev`, not only `origin/dev`.
- For a standalone single-fix branch, prefer rebase/amend over merging the target branch into it.
