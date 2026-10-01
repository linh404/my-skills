# 044. upload_health_check

- Bruno: `HR Employee/upload_health_check.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/upload_health_check`
- Backend model: `hr.employee`
- Backend method: `upload_health_check`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1584`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
