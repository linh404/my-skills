# 073. get_attendance_explanation_details

- Bruno: `HR Attendance Explanation/get_attendance_explanation_details.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_attendance_explanation_details`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_attendance_explanation_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:1883`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`

## Inputs
`explanation_id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
