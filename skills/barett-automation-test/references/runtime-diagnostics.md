# Barett runtime diagnostics and reporting

Use this reference when a local Barett test shows an error that could be
caused by a stale registry, view, translation, module, or running process.
It is for read-only diagnosis and reporting. It does not authorize changes to
the database, module updates, service starts/restarts, or other fixes. Report
the evidence and likely cause to the user, and wait for an explicit request
before executing a fix.

## Identify the exact target

Record:

- Odoo URL and authenticated user/company/language.
- Database name.
- Odoo executable, config file, addons paths, HTTP port, and active process.
- Relevant module names from the manifest, model, view, or error.

For Barett, the expected local target is `barett-dev-3`, the config is
`/home/linh/odoo-versions/config/barret.conf`, and the addons include
`/home/linh/vdx/barett-odoo-erp/addons/vdx`. Verify the active process and
database for every run; do not select a database from a directory name or
guess credentials from the Odoo application login.

For each acceptance criterion, keep both sides of the evidence: the source
file/line that defines the model, view, field, or translation, and the exact
database and active Odoo process used by the browser test. Use read-only
inspection such as `ps`, `ss`, and `rg`; redact credentials from config output.

## Classify the mismatch first

Compare source and runtime before deciding that an update is the fix:

- Source contains the field/view but runtime says it is undefined: suspect a
  stale registry/view, wrong addons path, wrong process, or missing dependency.
- Source does not contain the field/view: an update cannot invent the
  implementation; report a source/view issue.
- Source and runtime both contain it: inspect inherited views, dependencies,
  database metadata, browser assets, data, and permissions.
- Missing records, access rights, or disabled buttons are data/permission
  problems, not reasons to update every module.

## Check for an existing update (read-only)

Use read-only process inspection to look for an Odoo process using
`--stop-after-init`. Record its observed database, config, arguments, and
state when available. Do not wait for it, launch a competing update, stop it,
or otherwise interfere. Report an unknown or conflicting target to the user.

## Report findings

Include the exact URL, database, active PID, config, addons paths, owning
module, error, source/runtime comparison, and any matching update process.
State the likely cause and the next action that would address it, but do not
perform that action unless the user explicitly asks.
