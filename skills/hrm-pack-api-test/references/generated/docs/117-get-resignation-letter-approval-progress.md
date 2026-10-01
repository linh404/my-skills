# 117. get_resignation_letter_approval_progress

- Bruno: `Resignation Letter/get_resignation_letter_approval_progress.bru`
- Flow: `resignation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/get_resignation_letter_approval_progress`
- Backend model: `resignation.letter`
- Backend method: `get_resignation_letter_approval_progress`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:530`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`
- `Resignation Letter/get_resignation_letter_details.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
