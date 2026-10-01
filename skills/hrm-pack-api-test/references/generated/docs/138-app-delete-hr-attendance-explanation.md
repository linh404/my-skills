# 138. app_delete_hr_attendance_explanation

- Bruno: `HR Attendance Explanation/app_delete_hr_attendance_explanation.bru`
- Flow: `attendance_explanation`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/app_delete_hr_attendance_explanation`
- Backend model: `hr.attendance.explanation`
- Backend method: `app_delete_hr_attendance_explanation`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2252`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- state-changing request; explicit execution approval required
