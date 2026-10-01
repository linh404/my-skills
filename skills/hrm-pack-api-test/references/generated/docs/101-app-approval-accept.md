# 101. app_approval_accept

- Bruno: `HR Leave & Overtime/app_approval_accept.bru`
- Flow: `leave`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/api/models/hr-leave/execute/app_approval_accept`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/app_approval_submit.bru`
- `HR Leave & Overtime/create_or_update_hr_leave.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- state-changing request; explicit execution approval required
