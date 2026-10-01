# 069. get_infor_allocation

- Bruno: `HR Attendance Explanation/get_infor_allocation.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_infor_allocation`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_infor_allocation`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2190`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/get_infor_day_type.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
