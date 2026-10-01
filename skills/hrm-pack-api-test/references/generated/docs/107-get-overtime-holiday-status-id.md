# 107. get_overtime_holiday_status_id

- Bruno: `HR Leave & Overtime/get_overtime_holiday_status_id.bru`
- Flow: `overtime`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_overtime_holiday_status_id`
- Backend model: `hr.leave`
- Backend method: `get_overtime_holiday_status_id`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1403`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- overtime dates must satisfy same-day source constraint
