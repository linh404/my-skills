# 038. upload_cv_file

- Bruno: `HR Employee/upload_cv_file.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/upload_cv_file`
- Backend model: `hr.employee`
- Backend method: `upload_cv_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1264`
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
