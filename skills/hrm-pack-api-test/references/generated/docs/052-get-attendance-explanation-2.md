# 052. get_attendance_explanation_2

- Bruno: `HR Attendance Explanation/get_attendance_explanation_2.bru`
- Flow: `attendance_explanation`
- Operation: `transient_preview`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation.wizard/get_attendance_explanation`
- Backend model: `hr.attendance.explanation.wizard`
- Backend method: `get_attendance_explanation`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/wizard/attendance_explanation_wizard.py:56`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`explained_check_in`, `explained_check_out`, `explained_resource_calendar_id`, `explanation_date`, `explanation_reason`, `hours_of_break`, `leave_end_time`, `leave_start_time`, `overtime_first_end`, `overtime_first_start`, `overtime_second_end`, `overtime_second_start`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
