# Project defaults: KG Odoo HRM Bruno collection

Use these defaults only when the paths exist; explicit user paths take precedence.

| Purpose | Path |
|---|---|
| Bruno collection | `/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection` |
| Custom/backend source | `/home/linh/vdx/hrm-package` |
| Bruno runner skill | `/home/linh/Workspace/my-skills/skills/bruno-test-runner` |
| Local environment | `/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection/environments/KG - local.bru` |
| Shared/test environment | `/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection/environments/KG.bru` |
| Login request | `/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection/Authentication & System/login.bru` |
| Upload fixture placeholder | `/home/linh/Workspace/my-skills/skills/hrm-pack-api-test/collection/test-upload/placeholder.txt` |
| Bruno CLI dependency | `@usebruno/cli@4.2.0` (`bru`) |

## Collection facts to verify, not blindly assume

- The collection currently contains 146 executable `.bru` requests after removing the obsolete Salary Payslip requests.
- Login is expected to store an access token in secret variable `token`.
- Environment files contain placeholders for host, database, credentials, and external API keys; values are sensitive.
- Multipart requests may require replacing `test-upload/placeholder.txt` with an approved fixture.
- The sequence runner passes all selected requests to one Bruno CLI process so the cookie jar and `bru.setVar` chaining remain available.

## Domain grouping hints

The current folder names suggest domains such as authentication, employee, contract/job,
attendance, attendance explanation, leave/overtime, helpdesk, resignation, staff transfer,
reward/discipline, driver attendance, and company/users. Treat these as
navigation hints only. Confirm dependencies from request payloads and backend source.
