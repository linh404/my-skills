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
- Name branches as `<change-type>/<module>-<short-description>[-<issue>]` in lowercase kebab-case, using the actual module name and issue number when available. Keep `<short-description>` to at most four words.

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

The `<description>` must state clearly what the issue fixes, including the affected
module/model/view or user-visible behavior. Do not use a generic description such
as `fix issue` or only repeat the issue number. For example:

```text
[FIX] issue: hide VDX employee fields on hr.employee form (#4)
```

If no issue number is provided, do not invent one; use the module format for a
non-issue commit or ask for the issue number when the change is explicitly an
issue fix.

## New change

```bash
git fetch <target-remote>
git switch -c <change-type>/<module>-<short-description>[-<issue>] <target-remote>/<target-branch>
# make changes
git add <files>
git commit -m "[TYPE] module: describe the change"
git push -u <push-remote> <change-type>/<module>-<short-description>[-<issue>]
```

Create the merge request from `<push-remote>/<branch>` into the actual merge target.

## Rebase or non-fast-forward

When the merge target moved or GitLab requires a rebase:

```bash
git fetch --all --prune
git switch <type>/<short-name>
git branch backup/<short-name>-before-rebase
git rebase <target-remote>/<target-branch>
# resolve conflicts, then: git add <file> && git rebase --continue
git push --force-with-lease <push-remote> <type>/<short-name>
```

If the pushed branch contains commits not present locally, integrate it before
rebasing onto the merge target:

```bash
git fetch --all --prune
git rebase <push-remote>/<type>/<short-name>
git rebase <target-remote>/<target-branch>
git push --force-with-lease <push-remote> <type>/<short-name>
```

Rules:

- Use `git push --force-with-lease` after a rebase; never plain `git push --force`.
- Create a backup branch before rewriting history.
- Do not use `git pull` blindly; it can merge the wrong branch.
- Compare against the actual merge target, not only the push remote's default branch.
- For a standalone single-fix branch, prefer rebase/amend over merging the target branch into it.
