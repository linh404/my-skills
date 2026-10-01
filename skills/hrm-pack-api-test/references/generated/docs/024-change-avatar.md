# 024. change_avatar

- Bruno: `HR Employee/change_avatar.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/change_avatar`
- Backend model: `hr.employee`
- Backend method: `change_avatar`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:920`
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
