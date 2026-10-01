# 118. app_approval_submit

- Bruno: `Resignation Letter/app_approval_submit.bru`
- Flow: `resignation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/app_approval_submit`
- Backend model: `resignation.letter`
- Backend method: `app_approval_submit`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:663`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`
- `Resignation Letter/get_resignation_letter_approval_progress.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
