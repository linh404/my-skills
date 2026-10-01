# 071. attach_files

- Bruno: `HR Attendance Explanation/attach_files.bru`
- Flow: `attendance_explanation`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-attendance-explanation/upload_files/attach_files`
- Backend model: `hr.attendance.explanation`
- Backend method: `attach_files`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2391`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/create_or_update_explanation.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- state-changing request; explicit execution approval required
