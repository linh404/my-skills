# 035. delete_citizen_id_card_file

- Bruno: `HR Employee/delete_citizen_id_card_file.bru`
- Flow: `employee_context`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/api/models/hr-employee/execute/delete_citizen_id_card_file`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Employee/get_employee_infor.bru`
- `HR Employee/upload_citizen_id.bru`

## Inputs
`attachment_id`

## Captures
none declared

## Constraints and risks
- state-changing request; explicit execution approval required
