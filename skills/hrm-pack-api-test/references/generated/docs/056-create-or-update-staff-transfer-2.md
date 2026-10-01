# 056. create_or_update_staff_transfer_2

- Bruno: `Staff Transfer/create_or_update_staff_transfer_2.bru`
- Flow: `staff_transfer`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/api/models/staff-transfer/execute/create_or_update_staff_transfer`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`area_category_id`, `concurrent_allowance`, `content`, `department_id`, `division`, `employee_id`, `group_id`, `is_challenge`, `job_id`, `job_title_id`, `salary`, `suggested_allowance`, `type`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
- state-changing request; explicit execution approval required
