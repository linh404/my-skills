# 113. create_or_update_resignation_letter

- Bruno: `Resignation Letter/create_or_update_resignation_letter.bru`
- Flow: `resignation`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/resignation.letter/create_or_update_resignation_letter`
- Backend model: `resignation.letter`
- Backend method: `create_or_update_resignation_letter`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/resignation_letter.py:369`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/update_employee_onboard_time.bru`
- `Resignation Letter/get_infor_departure_reason.bru`

## Inputs
`content`, `day_off`, `departure_reason_id`, `information`, `note`, `receiver`, `resignation_date`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
