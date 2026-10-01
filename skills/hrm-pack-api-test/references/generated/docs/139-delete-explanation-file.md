# 139. delete_explanation_file

- Bruno: `HR Attendance Explanation/delete_explanation_file.bru`
- Flow: `attendance_explanation`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/delete_explanation_file`
- Backend model: `hr.attendance.explanation`
- Backend method: `delete_explanation_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2448`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/attach_files.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`

## Inputs
`attachment_id`, `explanation_id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- state-changing request; explicit execution approval required
