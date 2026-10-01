# 060. app_approval_set_to_cancel_2

- Bruno: `HR Leave & Overtime/app_approval_set_to_cancel_2.bru`
- Flow: `leave`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/app_approval_set_to_cancel`
- Backend model: `hr.leave`
- Backend method: `app_approval_set_to_cancel`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1327`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- state-changing request; explicit execution approval required
