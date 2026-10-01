# 053. get_hr_leave_details_2

- Bruno: `HR Leave & Overtime/get_hr_leave_details_2.bru`
- Flow: `leave`
- Operation: `transient_preview`
- Endpoint: `POST {{base_url}}/json/2/hr.leave.wizard/get_hr_leave_details`
- Backend model: `hr.leave.wizard`
- Backend method: `get_hr_leave_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/hr_leave_wizard.py:28`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`holiday_status_id`, `name`, `request_date_from`, `request_date_from_period`, `request_date_to`, `request_unit_half`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
