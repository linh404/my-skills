# 036. upload_curriculum_vitae

- Bruno: `HR Employee/upload_curriculum_vitae.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/upload_curriculum_vitae`
- Backend model: `hr.employee`
- Backend method: `upload_curriculum_vitae`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1423`
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
