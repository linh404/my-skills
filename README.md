# my-skills

A personal collection of reusable skills for Codex and related coding workflows.

## Repository layout

```text
my-skills/
├── skills/
│   ├── odoo/
│   │   ├── task/
│   │   └── technical/
│   ├── productivity/
│   ├── code-quality/
│   ├── integrations/
│   └── codex/
├── scripts/
├── tests/
├── docs/
└── .github/workflows/
```

## Adding a skill

1. Create a directory under the appropriate category in `skills/`.
2. Add a `SKILL.md` file as the skill entrypoint.
3. Keep supporting references, scripts, assets, and tests next to the skill entrypoint.
4. Run `scripts/validate-skills.sh` before committing.

This repository is intentionally organized as a monorepo so related skills can be versioned and maintained together.

## Status

The repository structure is ready. Skills will be added selectively as they are reviewed and approved.
