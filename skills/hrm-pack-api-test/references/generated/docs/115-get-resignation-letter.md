# 115. get_resignation_letter

- Bruno: `Resignation Letter/get_resignation_letter.bru`
- Flow: `resignation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/get_resignation_letter`
- Backend model: `resignation.letter`
- Backend method: `get_resignation_letter`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:414`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`

## Inputs
`approve_resignation_letter`, `date_from`, `date_to`, `employee_id`, `limit`, `offset`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
