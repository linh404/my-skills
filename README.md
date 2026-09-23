# my-skills

A personal collection of reusable skills for Codex and related coding workflows.

## Current repository layout

```text
my-skills/
├── skills/
│   ├── configure-weblate-gitlab-v2/
│   ├── bruno-test-runner/
│   ├── odoo-wlc/
│   └── uml-mdj-drawing/
├── scripts/
├── tests/
├── docs/
└── .github/workflows/
```

Only reviewed, imported skills are kept in the repository. New skills should be
added as directories directly under `skills/`; each skill directory must contain
a `SKILL.md` entrypoint.

## Adding a skill

1. Create a directory directly under `skills/`.
2. Add a `SKILL.md` file as the skill entrypoint.
3. Keep supporting references, scripts, assets, and tests next to the skill entrypoint.
4. Run `scripts/validate-skills.sh` before committing.

This repository is intentionally organized as a monorepo so related skills can be versioned and maintained together.
