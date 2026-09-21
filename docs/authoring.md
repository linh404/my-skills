# Skill authoring guide

Each skill must have a `SKILL.md` entrypoint. Supporting files should remain
inside the same skill directory so the skill can be moved or installed as a
self-contained unit.

Recommended contents:

- Clear purpose and scope
- Activation or usage guidance
- Constraints and safety notes
- References, scripts, assets, and tests when needed

Keep instructions in English and avoid committing secrets, machine-specific
credentials, generated caches, or private runtime configuration.
