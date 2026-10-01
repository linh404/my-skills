# 114. upload_attachment_file

- Bruno: `Resignation Letter/upload_attachment_file.bru`
- Flow: `resignation`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/resignation-letter/upload_files/upload_attachment_file`
- Backend model: `resignation.letter`
- Backend method: `upload_attachment_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:774`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
