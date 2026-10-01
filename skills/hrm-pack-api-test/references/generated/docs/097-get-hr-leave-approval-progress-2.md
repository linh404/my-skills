# 097. get_hr_leave_approval_progress_2

- Bruno: `HR Leave & Overtime/get_hr_leave_approval_progress_2.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_hr_leave_approval_progress`
- Backend model: `hr.leave`
- Backend method: `get_hr_leave_approval_progress`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:907`
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
