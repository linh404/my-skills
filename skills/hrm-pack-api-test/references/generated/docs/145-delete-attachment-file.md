# 145. delete_attachment_file

- Bruno: `Resignation Letter/delete_attachment_file.bru`
- Flow: `resignation`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/api/models/resignation-letter/execute/delete_attachment_file`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`
- `Resignation Letter/upload_attachment_file.bru`

## Inputs
`attachment_id`, `letter_id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
