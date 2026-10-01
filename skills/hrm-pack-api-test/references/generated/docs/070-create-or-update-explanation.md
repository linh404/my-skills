# 070. create_or_update_explanation

- Bruno: `HR Attendance Explanation/create_or_update_explanation.bru`
- Flow: `attendance_explanation`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/create_or_update_explanation`
- Backend model: `hr.attendance.explanation`
- Backend method: `create_or_update_explanation`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2204`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance Explanation/get_infor_allocation.bru`
- `HR Attendance Explanation/get_infor_day_type.bru`
- `HR Attendance Explanation/get_infor_explanation_reason.bru`

## Inputs
`explained_resource_calendar_id`, `explanation_date`, `explanation_reason`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- state-changing request; explicit execution approval required
