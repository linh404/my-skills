# Installation

After adding skills, validate and install them with:

```bash
./scripts/validate-skills.sh
./scripts/install-skills.sh
```

By default, skills are installed into `~/.codex/skills`. Set `CODEX_HOME` to
use another Codex home directory. Existing skill directories are preserved;
use `--force` only when replacement is intentional.
