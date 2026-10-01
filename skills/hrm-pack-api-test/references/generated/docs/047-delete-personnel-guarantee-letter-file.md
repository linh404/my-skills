# 047. delete_personnel_guarantee_letter_file

- Bruno: `HR Employee/delete_personnel_guarantee_letter_file.bru`
- Flow: `employee_context`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/api/models/hr-employee/execute/delete_personnel_guarantee_letter_file`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`
- `HR Employee/upload_personnel_guarantee_letter.bru`

## Inputs
`attachment_id`

## Captures
none declared

## Constraints and risks
- state-changing request; explicit execution approval required
