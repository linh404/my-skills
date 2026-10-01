# 050. upload_staff_confirmation_letter

- Bruno: `HR Employee/upload_staff_confirmation_letter.bru`
- Flow: `employee_context`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-employee/upload_files/upload_staff_confirmation_letter`
- Backend model: `hr.employee`
- Backend method: `upload_staff_confirmation_letter`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1821`
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
