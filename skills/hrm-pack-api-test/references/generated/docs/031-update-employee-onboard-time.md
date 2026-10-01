# 031. update_employee_onboard_time

- Bruno: `HR Employee/update_employee_onboard_time.bru`
- Flow: `employee_context`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/hr.employee/write`
- Backend model: `hr.employee`
- Backend method: `write`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/hr_employee.py:411`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`

## Inputs
`ids`, `onboard_time`, `vals`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
