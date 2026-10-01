# 116. get_resignation_letter_details

- Bruno: `Resignation Letter/get_resignation_letter_details.bru`
- Flow: `resignation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/get_resignation_letter_details`
- Backend model: `resignation.letter`
- Backend method: `get_resignation_letter_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:553`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`
- `Resignation Letter/get_resignation_letter.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
