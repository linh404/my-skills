# 098. get_hr_leave_details

- Bruno: `HR Leave & Overtime/get_hr_leave_details.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_hr_leave_details`
- Backend model: `hr.leave`
- Backend method: `get_hr_leave_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/hr_leave_wizard.py:28`
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
