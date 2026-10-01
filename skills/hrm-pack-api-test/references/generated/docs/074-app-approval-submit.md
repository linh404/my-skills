# 074. app_approval_submit

- Bruno: `HR Attendance Explanation/app_approval_submit.bru`
- Flow: `attendance_explanation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/app_approval_submit`
- Backend model: `hr.attendance.explanation`
- Backend method: `app_approval_submit`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2269`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`
- `HR Attendance Explanation/get_attendance_explanation_details.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- state-changing request; explicit execution approval required
