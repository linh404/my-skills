# 030. delete_curriculum_vitae_file

- Bruno: `HR Employee/delete_curriculum_vitae_file.bru`
- Flow: `employee_context`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.employee/delete_curriculum_vitae_file`
- Backend model: `hr.employee`
- Backend method: `delete_curriculum_vitae_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:1488`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`
- `HR Employee/upload_curriculum_vitae.bru`

## Inputs
`attachment_id`

## Captures
none declared

## Constraints and risks
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
- state-changing request; explicit execution approval required
