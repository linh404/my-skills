# 065. get_attendance_explanation

- Bruno: `HR Attendance Explanation/get_attendance_explanation.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_attendance_explanation`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_attendance_explanation`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/attendance_explanation_wizard.py:56`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`approve_hr_attendance_explanation`, `limit`, `offset`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
