# 075. app_approval_accept

- Bruno: `HR Attendance Explanation/app_approval_accept.bru`
- Flow: `attendance_explanation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/app_approval_accept`
- Backend model: `hr.attendance.explanation`
- Backend method: `app_approval_accept`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2293`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/app_approval_submit.bru`
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
