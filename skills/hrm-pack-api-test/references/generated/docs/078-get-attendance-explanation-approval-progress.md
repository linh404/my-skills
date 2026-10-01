# 078. get_attendance_explanation_approval_progress

- Bruno: `HR Attendance Explanation/get_attendance_explanation_approval_progress.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_attendance_explanation_approval_progress`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_attendance_explanation_approval_progress`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:1859`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/app_approval_reject.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
