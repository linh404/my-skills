# 054. get_overtime_register_details_2

- Bruno: `HR Leave & Overtime/get_overtime_register_details_2.bru`
- Flow: `overtime`
- Operation: `transient_preview`
- Endpoint: `POST {{base_url}}/json/2/hr.leave.wizard/get_overtime_register_details`
- Backend model: `hr.leave.wizard`
- Backend method: `get_overtime_register_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/hr_leave_wizard.py:60`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`holiday_status_id`, `name`, `request_date_from`, `request_date_from_period`, `request_date_to`, `request_unit_half`

## Captures
none declared

## Constraints and risks
- overtime dates must satisfy same-day source constraint
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
