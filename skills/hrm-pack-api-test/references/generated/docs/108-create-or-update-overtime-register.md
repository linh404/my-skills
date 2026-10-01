# 108. create_or_update_overtime_register

- Bruno: `HR Leave & Overtime/create_or_update_overtime_register.bru`
- Flow: `overtime`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/create_or_update_overtime_register`
- Backend model: `hr.leave`
- Backend method: `create_or_update_overtime_register`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1364`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/get_overtime_holiday_status_id.bru`

## Inputs
`coefficient`, `employee_id`, `holiday_status_id`, `name`, `overtime_type`, `request_date_from`, `request_date_to`, `type`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- overtime dates must satisfy same-day source constraint
- state-changing request; explicit execution approval required
