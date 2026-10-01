# 109. get_overtime_register_details

- Bruno: `HR Leave & Overtime/get_overtime_register_details.bru`
- Flow: `overtime`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_overtime_register_details`
- Backend model: `hr.leave`
- Backend method: `get_overtime_register_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/hr_leave_wizard.py:60`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/create_or_update_overtime_register.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- overtime dates must satisfy same-day source constraint
