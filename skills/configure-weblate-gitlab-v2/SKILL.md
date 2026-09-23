---
name: configure-weblate-gitlab-v2
description: Configure, operate, and troubleshoot a self-hosted Docker Weblate instance connected to a self-hosted GitLab repository for Odoo continuous localization. Use when setting up Weblate infrastructure, GitLab credentials and protected-branch permissions, Weblate Workspace/Project/Component settings, CI-owned POT and Weblate-owned PO synchronization, translation merge requests, webhooks, optional machine translation, or end-to-end failures such as missing source strings, credential errors, 403 pushes, tunnel issues, and protected-branch conflicts.
---

# Configure Weblate GitLab v2

Use this skill to implement and verify the Odoo translation workflow end to end. Keep the skill's core rules below fixed; load the linked reference only for the subsystem being changed or diagnosed.

## Fixed architecture

Use one component per Odoo module when the modules have separate POT and PO paths.

| Area | Owner or policy |
| --- | --- |
| Source code and translatable source strings | Developer and normal code MR workflow |
| POT templates | GitLab CI `export-i18n` job; CI validates and writes only changed POT files |
| PO `msgstr` values | Weblate and BA/Translator |
| Source branch and translation MR target | `dev` |
| Weblate translation branch | `weblate-translations` |
| Translation content gate | BA/Translator; do not add a second Weblate review gate |
| MR review and merge | GitLab Maintainer/CTO |

Apply these invariants:

1. Keep the existing code MR, CI, approval, and deployment workflow.
2. Run the CI POT export after a code MR is merged into `dev`; do not require manual developer export.
3. Commit directly to `dev` only when the CI identity is explicitly allowed to write the generated POT paths. Use the agreed loop-prevention marker, normally `[skip ci]`.
4. Never let Weblate push PO changes directly to `dev`. Configure the `GitLab merge request` backend and push to `weblate-translations`.
5. Let GitLab's Push-event webhook notify Weblate after the CI POT commit. The webhook does not run Odoo export and does not create the outbound translation MR.
6. Let Weblate synchronize PO files from the CI-owned POT and create the translation MR. Review and merge that MR in GitLab.
7. Do not let another job rewrite Weblate-owned `msgstr` values or export POT from an inconsistent Odoo database.

Read [references/odoo-ci-pot-workflow.md](references/odoo-ci-pot-workflow.md) for the exporter contract and local/CI validation.

When choosing or reviewing the implementation strategy, read [references/odoo-ci-job-solutions.md](references/odoo-ci-job-solutions.md). Use Full Export for the simpler, conservative path. Use Changed Module Export only when file-to-module mapping, impact policy, dependency analysis, and a safe Full fallback are implemented. Manifestoo calculates dependency information; it does not replace Git diff classification or impact policy.

## Route the task to the right reference

Load only the detailed reference required by the request. Do not duplicate its complete procedures in the response.

| Request | Read |
| --- | --- |
| Docker Compose, environment file, PostgreSQL, Valkey, volumes, HTTPS, tunnel, reverse proxy, hardening | [references/weblate-self-hosted-deployment.md](references/weblate-self-hosted-deployment.md) |
| Git transport, credentials, CI Job Token, protected `dev`, webhook, GitLab MR, integration errors | [references/weblate-gitlab-integration.md](references/weblate-gitlab-integration.md) |
| Workspace, Project, Component, Version control, Files, POT template, PO mask, add-ons, languages, TM, Weblate UI errors | [references/weblate-settings-configuration.md](references/weblate-settings-configuration.md) |
| CI exporter contract, local validation, POT/PO loop | [references/odoo-ci-pot-workflow.md](references/odoo-ci-pot-workflow.md) |
| Full Export vs Changed Module Export, impact analysis, Manifestoo, dependency installation, fallback policy | [references/odoo-ci-job-solutions.md](references/odoo-ci-job-solutions.md) |
| Optional LibreTranslate, Ollama, or third-party machine translation | [references/weblate-machine-translation.md](references/weblate-machine-translation.md) |

The references are deliberately separated by ownership boundary:

- Self-hosting covers runtime and network infrastructure only.
- GitLab integration covers repository access, branch policy, API, CI permissions, and webhook only.
- Weblate settings covers the instance UI and component file mapping only.
- CI workflow covers Odoo export, validation, POT/PO ownership, and delivery checkpoints.
- CI solution reference covers Full Export, Changed Module Export, impact analysis, Manifestoo, and fallback policy.
- Machine translation covers suggestion providers only.

## Start safely

Before changing a live configuration, establish:

- Weblate version and whether it runs in Docker Compose.
- GitLab hostname, project path, fork status, target branch, and protected-branch rules.
- Whether GitLab is reachable only through corporate Wi-Fi/VPN and which Git transport the Weblate container can use.
- Odoo version, executable or wrapper, database, addons path, module-to-POT path, and existing CI stages.
- Weblate project/component names, component root, POT path, PO file mask, target language code, and translation branch.
- Whether the request concerns infrastructure, GitLab, Weblate UI, CI, or machine translation.

For the current local Shell Runner pilot, preserve `pipelines/i18n-test.yml`, the `local-shell` tag, the host PostgreSQL/Odoo environment, the `qms-local` database, and the tested Odoo virtualenv. Do not add Docker executor fields such as `image:` or `services:` to that job. Keep the CI job independent and artifact-only until the exporter output, dependency setup, and deterministic second run are verified.

Use the minimum change required. Inspect current settings before editing them and preserve unrelated user changes.

Never expose or copy real credentials. Mask tokens in logs, screenshots, UI output, documents, and responses. If a token or password was shown in chat, a URL, a repository, or a log, rotate it before continuing. Keep `WEBLATE_GITLAB_HOST` as a hostname without scheme or path.

## Self-hosted Docker baseline

For the current proof of concept, expect these service roles and names unless the user has explicitly changed them:

| Service | Role |
| --- | --- |
| `weblate` | Web UI, repository operations, PO commits, GitLab API calls |
| `database` | PostgreSQL persistence |
| `cache` | Valkey/Redis cache and background-task support |
| `ollama` | Optional local machine-translation runtime |

Apply these checks before debugging Weblate application settings:

- An `env_file` uses `KEY=value`; Compose `environment:` mappings use `KEY: value`. Do not mix the syntaxes.
- Inside Compose, use `POSTGRES_HOST=database` and `REDIS_HOST=cache`; `localhost` points back to the Weblate container.
- Keep persistent volumes for `/app/data`, `/app/cache`, PostgreSQL, and any model storage. PostgreSQL 18 baseline uses `/var/lib/postgresql` unless `PGDATA` is deliberately configured.
- If the Weblate container is `read_only`, keep its persistent mounts and `/run` and `/tmp` `tmpfs` mounts. Do not disable read-only mode merely to hide a missing writable path.
- After changing environment values, recreate the Weblate container with `docker compose up -d --force-recreate weblate` and inspect logs.
- An inbound Cloudflare or other tunnel exposes Weblate to GitLab and users; it does not provide the Weblate container with outbound access to a VPN-only GitLab.
- Quick tunnel hostnames are proof-of-concept only. Update `WEBLATE_SITE_DOMAIN`, `WEBLATE_ALLOWED_HOSTS`, and the GitLab webhook whenever the hostname changes.

For the exact Compose baseline, HTTPS/proxy headers, persistent-volume rules, hardening, and Docker error table, read the self-host reference.

## GitLab integration baseline

Keep credential roles separate:

| Operation | Credential or permission |
| --- | --- |
| Weblate clone/fetch | Git read access through SSH or HTTPS |
| Weblate push to `weblate-translations` | Git write access, normally `write_repository` |
| Weblate creates translation MR | GitLab API credential with `api` |
| CI commits generated POT to `dev` | `CI_JOB_TOKEN`, project permission, and protected-branch allowance |

For the CI exception, verify the project setting:

`Settings → CI/CD → Job token permissions → Allow Git push requests to the repository`

This setting does not bypass protected-branch rules. Keep `dev` protected, allow the narrowly scoped CI POT write according to the project's policy, and fail the job when the diff contains files outside the approved POT paths.

For Weblate, set `Repository branch=dev`, `Push branch=weblate-translations`, and use the `GitLab merge request` backend. Test Git reachability from the Weblate container, not only from the Docker host. Do not use the Weblate tunnel URL as the GitLab repository URL.

Configure the GitLab Push-event webhook at:

```text
https://<weblate-domain>/hooks/gitlab/
```

The expected direction is `GitLab push → Weblate webhook → Weblate fetch/update`. A successful webhook only proves delivery; if the source unit is still missing, check the POT commit, component branch/template, component lock, repository maintenance log, and `Update PO files to match POT (msgmerge)` add-on.

Read the GitLab reference for exact UI paths, transport choices, token handling, protected-branch behavior, webhook evidence, and the recorded errors `terminal prompts disabled`, `miss credentials`, `403`, `publickey`, `insufficient_scope`, invalid URL, branch-without-MR, and webhook-without-new-source-string.

## Weblate settings baseline

Map the hierarchy consistently:

- Workspace: organization-wide translation space.
- Project: the Odoo repository/system, for example `Odoo QMS`.
- Component: one Odoo module, for example `g10_access_management`.

For each component, verify:

| Setting area | Required result |
| --- | --- |
| Version control | `GitLab merge request`; repository branch `dev`; push branch `weblate-translations` |
| Files | Template for new translations points to that module's CI-generated POT |
| File mask | Matches only that component's PO files, such as `i18n/*.po` or `<module>/i18n/*.po` depending on component root |
| Source editing | `Edit base file` off; Weblate does not alter `msgid` or regenerate POT |
| Add-ons | Install `Update PO files to match POT (msgmerge)` at project scope so compatible components inherit it; use component scope only for an exception |
| Language | Target language and filename style match the repository, for example `vi` with `vi.po` or `vi_VN.po` |
| Review | No separate Weblate review gate; BA/Translator is the translation content gate |
| Machine translation | Optional suggestion/draft service; never a prerequisite for POT/PO sync or MR creation |

For a project containing multiple Odoo module components, install `Update PO files to match POT (msgmerge)` from `Project → Operations → Add-ons`. This project-wide add-on is inherited by compatible existing and newly created components and runs after repository updates. Verify the component's add-on page shows it as inherited from the project. The add-on does not configure `File mask` or `Template for new translations`: those paths remain component-specific because each Odoo module has its own POT and PO files. Glossary or non-compatible components do not run this gettext add-on.

If the component creation screen discovers PO files but does not show a POT, do not select a different module's PO as the template. Confirm that the CI-generated POT exists on `dev`, create or finish the component, then set the correct POT under `Settings → Files → Template for new translations`.

Selecting a POT defines the base template; it does not itself run `msgmerge`, create a missing PO, run machine translation, or create a GitLab MR. Use the add-on and the repository/MR settings for those separate operations.

Read the settings reference for component-root path resolution, language setup, Translation Memory, optional providers, and the complete Weblate UI troubleshooting table.

## End-to-end acceptance test

Run this on a test/fork repository before applying it to the company repository:

1. Add one harmless translatable Odoo source string using the project's normal marker.
2. Create and merge the code MR into `dev`.
3. Verify the post-merge pipeline runs `export-i18n` with the intended Odoo environment.
4. Verify the generated POT contains the new source string and is deterministic on a second run.
5. Verify the CI commit contains only changed POT files and the approved loop-prevention marker.
6. Verify GitLab sends the Push-event webhook and Weblate fetches the `dev` commit.
7. Verify the component exposes the new source unit and its PO files are updated by `msgmerge`.
8. Translate one unit as BA/Translator, commit and push from Weblate.
9. Verify GitLab has an MR from `weblate-translations` to `dev`; do not rely only on Weblate's “All repositories were pushed” message.
10. Review and merge the translation MR in GitLab.
11. Verify the post-merge pipeline runs and finds no new POT change.
12. Verify the existing deployment path continues without an export loop.

Capture evidence for the code MR, exporter log, POT-only commit, webhook request history, new Weblate source unit, translation MR, no-loop pipeline, and deployment result.

## Failure triage

Use the first failing boundary rather than changing all settings at once:

| First failing boundary | Inspect first |
| --- | --- |
| CI stage, Runner tag, Odoo executable, virtualenv, database, or Manifestoo | Current Shell Runner pilot constraints, host paths, role permissions, installed tools, and [references/odoo-ci-job-solutions.md](references/odoo-ci-job-solutions.md) |
| Containers or URL | Compose syntax, environment values, volumes, forwarded headers, logs |
| Weblate cannot clone | Container DNS/route, Git URL, Git read credential, VPN/firewall |
| Weblate cannot push | Git write credential, push URL, target branch, component lock |
| CI cannot push POT | Job-token permission, protected `dev`, pipeline user, POT-only diff, loop marker |
| MR not created | `GitLab merge request` backend, API host, `api` scope, translation branch |
| Webhook returns success but source is missing | POT commit on `dev`, component branch, POT template, component root, msgmerge add-on, repository maintenance log |
| Automatic suggestion missing | Provider installation, Docker hostname, language pair, model/service health |

Do not treat these as equivalent:

- A webhook success is not proof that Weblate fetched and processed the repository.
- A pushed branch is not proof that GitLab created an MR.
- A running Ollama container is not proof that Weblate is configured to use it.
- A selected POT template is not proof that PO files were synchronized.
- An enabled CI Job Token permission is not proof that a protected branch accepts the push.

When a component is locked, read the repository/add-on error first, fix the underlying cause, run repository maintenance, and unlock only after the cause is resolved.

## Change discipline

- Preserve user edits outside the requested subsystem.
- Do not replace the CI export contract with a PO-only workflow.
- Do not remove existing PO files or rewrite unrelated modules.
- Do not introduce direct Weblate pushes to `dev`.
- Do not enable Weblate review when the agreed architecture has BA/Translator as the only translation gate.
- Do not install machine translation just to make Git synchronization work.
- When labels differ by Weblate version, verify the installed version's official documentation and report the exact label observed.
