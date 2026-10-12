# 121. delete_attachment_file

- Bruno: `Resignation Letter/delete_attachment_file.bru`
- Flow: `resignation`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/delete_attachment_file`
- Backend model: `resignation.letter`
- Backend method: `delete_attachment_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:777`
- Evidence: **SOURCE_VERIFIED**

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
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
- state-changing request; explicit execution approval required
