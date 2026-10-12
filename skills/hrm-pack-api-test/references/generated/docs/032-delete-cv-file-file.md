# 032. delete_cv_file_file

- Bruno: `HR Employee/delete_cv_file_file.bru`
- Flow: `employee_context`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.employee/delete_cv_file_file`
- Backend model: `hr.employee`
- Backend method: `delete_cv_file_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1326`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`
- `HR Employee/upload_cv_file.bru`

## Inputs
`attachment_id`

## Captures
none declared

## Constraints and risks
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
- state-changing request; explicit execution approval required
