# Odoo CI POT Workflow

## Contents

1. Fixed flow
2. Responsibility boundaries
3. Export contract
4. Local validation
5. GitLab integration
6. Weblate synchronization
7. Acceptance test
8. Failure handling
9. Current documentation

For the complete choice between Full Export and Changed Module Export, including impact classification, Manifestoo dependency analysis, and safe fallback rules, read [odoo-ci-job-solutions.md](odoo-ci-job-solutions.md).

## 1. Fixed flow

Use this sequence:

1. Developer adds or changes an Odoo source string.
2. Developer opens a code MR into `dev`.
3. The code MR follows the existing GitLab review process and is merged.
4. The existing post-merge pipeline starts and runs `export-i18n`.
5. GitLab Runner invokes a project wrapper or Odoo CLI command.
6. The exporter regenerates the module POT files.
7. If no POT changed, create no export commit and continue deployment.
8. If a POT changed, the CI identity commits only the POT diff into `dev`; the changed-POT path does not deploy yet.
9. GitLab sends a Push-event webhook to Weblate.
10. Weblate fetches `dev`, reloads the POT, and updates configured PO files.
11. BA translates directly in Weblate.
12. Weblate batches PO changes, pushes `weblate-translations`, and opens an MR into `dev`.
13. CTO reviews and merges the translation MR.
14. The existing post-merge pipeline runs again, including `export-i18n`. The POT should be unchanged, so this pipeline deploys the code together with the merged PO changes.

Do not add a Weblate review step. Do not make developers export POT manually.

## 2. Responsibility boundaries

| Area | Owner | Responsibility |
| --- | --- | --- |
| Source code and source strings | Developer | Add valid translatable strings in Python, XML, and JavaScript |
| Job trigger and execution environment | GitLab CI / Runner | Run export after merge with the approved image, variables, database, and addons |
| Translation extraction | Odoo CLI or project wrapper | Export intended modules and produce valid deterministic POT files |
| POT files | CI export process | Regenerate deterministically and commit changed POT files |
| Repository-to-Weblate notification | GitLab webhook | Notify Weblate after the POT commit reaches `dev` |
| PO `msgstr` values | Weblate and BA | Translate, validate, and batch PO changes |
| Translation approval | CTO in GitLab | Review the Weblate-created MR |
| Quality gates and deployment | Existing GitLab pipeline | Run after merge and deploy according to existing policy |

The runner does not translate. Weblate does not run the Odoo exporter.

The ban on direct pushes to `dev` applies to Weblate PO delivery. The CI identity is the sole exception and can write only the generated POT files required by this flow.

## 3. Export contract

Confirm these inputs before writing the job:

- Exact Odoo version and executable or wrapper.
- Database template or disposable database used for export.
- Installed module state and module list.
- Addons path and all required dependencies.
- One deterministic POT output path per module.
- Existing CI image, services, variables, cache, and network requirements.
- CI identity allowed to write generated POT files to `dev`.
- Loop-prevention mechanism accepted by the project.

The underlying Odoo command follows this shape:

```bash
odoo-bin \
  --database=<export_database> \
  --addons-path=<addons_paths> \
  --modules=<module_name> \
  --i18n-export=<supported_export_output> \
  --stop-after-init
```

Treat this as a command contract, not a copy-paste production command. Match the actual wrapper and Odoo image used by the project.

Odoo 18 CLI documentation describes `--i18n-export` output as CSV, PO, or TGZ. Do not assume stock `odoo-bin` accepts a `.pot` destination merely because the target workflow needs POT files. Verify one of these project contracts:

- The approved `cli-odoo` wrapper directly generates a valid POT.
- The wrapper exports a supported source-only PO representation and deterministically converts it to the module POT.
- The project uses another tested Odoo export entry point that produces the same valid POT.

Whichever contract is selected, validate that every non-header `msgstr` is empty, Gettext syntax is valid, the module and source references are correct, and identical inputs produce byte-stable output.

After export:

1. Normalize only known nondeterministic metadata if the project explicitly permits it.
2. Inspect `git diff -- */i18n/*.pot`.
3. Fail if the diff contains files outside the allowed POT paths.
4. Exit successfully without a commit when the POT diff is empty.
5. Commit and push only the expected POT files when the diff is non-empty.

Do not update PO `msgstr` values in this job. Weblate owns them.

## 4. Local validation

Validate the exporter independently from the protected company runner:

1. Use the same Odoo version, addons, module state, and representative database as CI.
2. Add one harmless source string.
3. Run the exporter.
4. Confirm the intended POT contains the new `msgid`.
5. Run the exporter a second time without source changes.
6. Confirm the second run produces no Git diff.
7. Remove or revert the harmless source string only after recording the expected result.

If local and CI output differ, compare image version, installed modules, database contents, locale, addons path, and wrapper arguments before changing Weblate.

## 5. GitLab integration

Insert `export-i18n` into the existing post-merge path rather than replacing the current pipeline. Keep normal lint, test, approval, and deployment behavior intact.

Before testing the CI write step, enable the project setting:

`Project → Settings → CI/CD → Job token permissions → Permissions → Allow Git push requests to the repository`

This allows the job's `CI_JOB_TOKEN` to authenticate the generated POT push. The setting is separate from Weblate's Git/API credentials and does not bypass protected-branch rules. Confirm that the protected `dev` branch and the user who starts the pipeline allow this CI push. The job must still configure Git to use `CI_JOB_TOKEN`, restrict the diff to approved POT paths, and apply loop prevention.

Use rules that distinguish:

- Code and translation MRs: follow the existing review and merge policy.
- A merge into `dev`: run the existing pipeline, including `export-i18n`.
- A CI-generated POT commit: do not recursively create another POT commit.

If POT generation fails, expose the exporter logs and fail the job. Do not commit partial output or continue as though source strings were synchronized.

Never embed a write token in the CI YAML or remote URL. Use the project's protected CI secret mechanism and a dedicated bot or project identity where available.

## 6. Weblate synchronization

Configure the GitLab Push-event webhook:

```text
https://weblate.example.com/hooks/gitlab/
```

The webhook notifies Weblate; it does not carry the POT file and does not perform export. Weblate fetches the repository after matching the event to the component.

For each module component configure:

- Repository branch: `dev`
- Template for new translations: the module POT path relative to the component root
- File mask: the module PO pattern, such as `i18n/*.po`
- Push branch: `weblate-translations`
- Version control system: `GitLab merge request`
- Add-on: `Update PO files to match POT (msgmerge)`

Inspect the component root before choosing paths. Do not blindly prepend the module path when the component root is already the module directory.

## 7. Acceptance test

Record evidence for all of these checkpoints:

| Checkpoint | Evidence |
| --- | --- |
| Code MR reviewed and merged | GitLab MR state |
| Export job ran after merge | Job URL and exporter log |
| POT changed exactly once | POT diff and CI-generated commit |
| Changed-POT path paused deployment | Original post-merge pipeline state |
| Webhook delivered | GitLab webhook request history |
| Weblate loaded the new unit | Component source unit visible |
| BA translation saved | Updated PO unit in Weblate |
| Translation MR created | Open MR from `weblate-translations` to `dev` |
| CTO review applied | GitLab approval state |
| Post-merge pipeline ran | GitLab pipeline state |
| No export loop | Post-merge export reports no POT diff |
| Deployment continued | Existing deployment job state |

A pushed branch without an open MR does not satisfy the translation-delivery checkpoint.

## 8. Failure handling

| Symptom | Diagnose first |
| --- | --- |
| POT misses a new source string | Module installation state, source markup, addons path, exporter arguments |
| POT changes on every identical run | Nondeterministic headers, database state, Odoo version, wrapper behavior |
| Export commit triggers forever | CI rules and generated-commit loop prevention |
| Weblate does not see the POT | Commit actually reached `dev`, webhook delivery, component branch and template path |
| PO files do not gain new units | POT template setting and `msgmerge` add-on |
| Weblate pushes a branch but no MR | GitLab VCS backend, API credential, push branch, target branch |
| Translation MR modifies POT or source code | Weblate ownership boundaries, component paths, unexpected repository operations |
| Local export differs from CI | Image, database, installed modules, addons, environment, command arguments |
| Deployment starts before the changed-POT translation cycle finishes | Job conditions and dependency graph between export, POT decision, and deploy |

## 9. Current documentation

- Odoo 18 CLI: `https://www.odoo.com/documentation/18.0/developer/reference/cli.html`
- Weblate component files: `https://docs.weblate.org/en/weblate-2026.7/admin/projects.html`
- Weblate Gettext msgmerge add-on: `https://docs.weblate.org/en/weblate-2026.7/admin/addons.html#update-po-files-to-match-pot-msgmerge`
