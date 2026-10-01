# 094. get_holiday_status_id_and_days

- Bruno: `HR Leave & Overtime/get_holiday_status_id_and_days.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_holiday_status_id_and_days`
- Backend model: `hr.leave`
- Backend method: `get_holiday_status_id_and_days`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1078`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`request_date_from`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
