# 105. get_hr_leave_approval_progress

- Bruno: `HR Leave & Overtime/get_hr_leave_approval_progress.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/api/models/hr-leave/execute/get_hr_leave_approval_progress`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/app_approval_reject.bru`
- `HR Leave & Overtime/create_or_update_hr_leave.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
