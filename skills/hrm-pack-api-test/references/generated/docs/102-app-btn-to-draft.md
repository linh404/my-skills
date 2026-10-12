# 102. app_btn_to_draft

- Bruno: `Resignation Letter/app_btn_to_draft.bru`
- Flow: `resignation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/app_btn_to_draft`
- Backend model: `resignation.letter`
- Backend method: `app_btn_to_draft`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:667`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/app_approval_submit.bru`
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
