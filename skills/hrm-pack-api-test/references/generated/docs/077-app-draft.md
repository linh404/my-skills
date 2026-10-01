# 077. app_draft

- Bruno: `HR Attendance Explanation/app_draft.bru`
- Flow: `attendance_explanation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/app_draft`
- Backend model: `hr.attendance.explanation`
- Backend method: `app_draft`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2369`
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
