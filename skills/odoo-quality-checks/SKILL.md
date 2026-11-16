---
name: odoo-quality-checks
description: Run the established Ruff and Odoo unit-test workflow for /home/linh/vdx/barett-odoo-erp.
---

# Odoo Quality Checks

Use this workflow for the `barett-odoo-erp` checkout. It records the tested commands for Ruff and the `barett_sales_plan` Odoo tests so they do not need to be rediscovered. Do not reuse its absolute paths, database, or module outside this checkout.

## Authorization and scope

- Run unit tests only when the user explicitly asks to test or verify. A request to change code alone does not authorize a test run.
- Add or change tests only when explicitly requested.
- Run only the requested module or files. The established Odoo test target is `barett_sales_plan`.
- This workflow updates the installed module on database `barett-dev-3` before testing. The user explicitly selected this existing DB for the test workflow. Before each run, verify the exact DB and module state using the read-only commands below.
- Never start, restart, recreate, or launch Docker containers/services. If a required service is down, report it and wait for the user's explicit approval before starting it.

## Ruff

Use `uvx --from ruff ruff`; do not switch to a repository `.venv` runner.

Check the plan test files:

```bash
uvx --from ruff ruff check addons/vdx/barett_sales_plan/tests
```

For the model diagnostics used in this repo (`B023`, `E501`, `ARG005`, line length 180), preview autofixes on the affected model files:

```bash
uvx --from ruff ruff check \
  --select B023,E501,ARG005 \
  --line-length 180 \
  --fix --diff \
  addons/vdx/barett_sales_plan/models/sales_plan_month.py \
  addons/vdx/barett_sales_plan/models/sales_plan_year.py
```

`--fix --diff` previews changes; inspect the diff, then make only the required fixes. If the user says to fix without checking again, do not rerun Ruff or tests. Otherwise rerun the same scoped Ruff command after edits. Do not silently broaden rule selection or fix unrelated files.

## Odoo unit tests

Use the project launch configuration as the source of truth for the local Odoo runtime. Do not hardcode or guess an Odoo-version checkout path, and do not use the broken `odoo` wrapper.

Read the `Odoo: Run` entry in `.vscode/launch.json` and reuse its `python`, `program`, `cwd`, and `env.PYTHONPATH`. In this checkout, `python` points to the repo-root `.venv`. Resolve the values without printing or changing the launch configuration:

```bash
ODOO_PYTHON="$(python3 -c 'import json; print(next(c["python"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_BIN="$(python3 -c 'import json; print(next(c["program"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_CWD="$(python3 -c 'import json; print(next(c["cwd"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_ROOT="$(dirname "$ODOO_BIN")"
ODOO_PYTHONPATH="$(python3 -c 'import json; print(next(c.get("env", {}).get("PYTHONPATH", "") for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
cd "$ODOO_CWD"
PYTHONPATH="$ODOO_PYTHONPATH" "$ODOO_PYTHON" "$ODOO_BIN" --version
```

The verified runner returned `Odoo Server 18.0`. Reuse it for tests. Only if the configured root `.venv` cannot run Odoo because dependencies are missing, reuse an existing temporary Odoo venv; create one and install requirements derived from `"$ODOO_ROOT/requirements.txt"` only if no local runtime works. Do not modify the root `.venv` to repair it.

Check PostgreSQL and verify the selected database/module before updating anything:

```bash
pg_isready
psql -d barett-dev-3 -Atqc "SELECT current_database(), current_user, current_setting('server_version')"
psql -d barett-dev-3 -Atqc "SELECT name, state, latest_version FROM ir_module_module WHERE name IN ('base', 'barett_sales_plan') ORDER BY name"
```

Proceed only if the current database is `barett-dev-3`, it is the expected Odoo 18 database, and `barett_sales_plan` is installed. If these checks fail, stop and report the mismatch; do not select another database automatically.

Run the module suite with the established Odoo 18 command. `--update` refreshes the module before its tests; `--stop-after-init` exits the runner, `--test-tags` limits tests to the module, and the temporary data directory avoids using repo data files:

```bash
ODOO_PYTHON="$(python3 -c 'import json; print(next(c["python"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_BIN="$(python3 -c 'import json; print(next(c["program"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_CWD="$(python3 -c 'import json; print(next(c["cwd"] for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
ODOO_ROOT="$(dirname "$ODOO_BIN")"
ODOO_PYTHONPATH="$(python3 -c 'import json; print(next(c.get("env", {}).get("PYTHONPATH", "") for c in json.load(open(".vscode/launch.json"))["configurations"] if c["name"] == "Odoo: Run"))')"
cd "$ODOO_CWD"
PYTHONPATH="$ODOO_PYTHONPATH" "$ODOO_PYTHON" "$ODOO_BIN" \
  --addons-path="$ODOO_ROOT/odoo/addons,$ODOO_ROOT/addons,/home/linh/vdx/barett-odoo-erp/addons/vdx" \
  --database=barett-dev-3 \
  --db_user=linh \
  --db_host=/var/run/postgresql \
  --db_port=5432 \
  --update=barett_sales_plan \
  --stop-after-init \
  --test-enable \
  --test-tags=/barett_sales_plan \
  --http-interface=127.0.0.1 \
  --http-port=18069 \
  --data-dir=/tmp/codex-barett-sales-plan-odoo18-data
```

Port `8069` was occupied in the observed run, so use local port `18069` by default. If `18069` is also occupied, inspect the listener and choose another unused loopback port; do not stop the process already using a port.

## Syntax and results

When a quick syntax check is useful, use Python's AST parser on the test files:

```bash
python3 - <<'PY'
import ast
from pathlib import Path

for path in Path("addons/vdx/barett_sales_plan/tests").glob("*.py"):
    ast.parse(path.read_text())
print("Python syntax OK")
PY
```

Report the Ruff scope and result, the exact Odoo database/module, and the actual test pass/fail count. The recorded run passed 7/7 tests after fixing a fixture that reused a product name. That result predates later Ruff-only edits; do not claim those edits were retested unless the suite was run again.
