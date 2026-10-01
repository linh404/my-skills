# 141. app_delete_overtime_register

- Bruno: `HR Leave & Overtime/app_delete_overtime_register.bru`
- Flow: `overtime`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/app_delete_overtime_register`
- Backend model: `hr.leave`
- Backend method: `app_delete_overtime_register`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1429`
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
- state-changing request; explicit execution approval required
