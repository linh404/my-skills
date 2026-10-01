# 106. get_list_overtime_register

- Bruno: `HR Leave & Overtime/get_list_overtime_register.bru`
- Flow: `overtime`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_list_overtime_register`
- Backend model: `hr.leave`
- Backend method: `get_list_overtime_register`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1451`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`date_from`, `limit`, `offset`

## Captures
none declared

## Constraints and risks
- overtime dates must satisfy same-day source constraint
