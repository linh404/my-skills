# KG Odoo HRM API — Bruno collection

Bruno collection generated from:

- Source: `/home/linh/Downloads/hrm_package.postman_collection.json`
- Layout/template: `/home/linh/vdx/odoo-hrm-api`

The collection contains **146 request files** after removing the obsolete Salary Payslip requests. One Postman item without a URL (`New Request`) was skipped because it is not an executable request.

## Usage

1. Open this folder as a Bruno collection.
2. Select `environments/KG - local.bru` or `environments/KG.bru`.
3. Replace placeholder database, credentials, host, and external API keys.
4. Replace `test-upload/placeholder.txt` with real files for multipart requests.
5. Run the login request first; its response script stores `access_token` in the secret `token` variable. Bruno's default cookie jar stores the Odoo `session_id` returned by login and sends it to later generic/upload requests; do not add a hardcoded Cookie header.
6. Canonical create/upload requests capture flow-scoped IDs with `bru.setVar` (for example `leave_id`, `ticket_id`, and `ticket_attachment_id`) and downstream requests reference those variables. Standalone requests with fixture IDs remain manual and must be checked against the selected database.

Secrets and project-specific credentials from the Postman export were intentionally replaced with environment placeholders. No backend/API code was changed by this conversion.
