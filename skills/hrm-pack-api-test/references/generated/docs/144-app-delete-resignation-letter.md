# 144. app_delete_resignation_letter

- Bruno: `Resignation Letter/app_delete_resignation_letter.bru`
- Flow: `resignation`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/app_delete_resignation_letter`
- Backend model: `resignation.letter`
- Backend method: `app_delete_resignation_letter`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:646`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
