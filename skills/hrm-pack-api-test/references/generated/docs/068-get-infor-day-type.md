# 068. get_infor_day_type

- Bruno: `HR Attendance Explanation/get_infor_day_type.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_infor_day_type`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_infor_day_type`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2176`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/get_infor_explanation_reason.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
