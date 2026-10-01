# 032. upload_birth_certificate

- Bruno: `HR Employee/upload_birth_certificate.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/upload_birth_certificate`
- Backend model: `hr.employee`
- Backend method: `upload_birth_certificate`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1504`
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
