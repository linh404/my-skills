# 140. app_delete_hr_leave

- Bruno: `HR Leave & Overtime/app_delete_hr_leave.bru`
- Flow: `leave`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/app_delete_hr_leave`
- Backend model: `hr.leave`
- Backend method: `app_delete_hr_leave`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1348`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
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
