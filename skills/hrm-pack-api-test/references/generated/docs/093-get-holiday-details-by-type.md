# 093. get_holiday_details_by_type

- Bruno: `HR Leave & Overtime/get_holiday_details_by_type.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_holiday_details_by_type`
- Backend model: `hr.leave`
- Backend method: `get_holiday_details_by_type`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1145`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
