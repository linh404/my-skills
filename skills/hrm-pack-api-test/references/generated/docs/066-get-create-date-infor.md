# 066. get_create_date_infor

- Bruno: `HR Attendance Explanation/get_create_date_infor.bru`
- Flow: `attendance_explanation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance.explanation/get_create_date_infor`
- Backend model: `hr.attendance.explanation`
- Backend method: `get_create_date_infor`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance_explain.py:2049`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`rec_id`

## Captures
none declared

## Constraints and risks
- employee/date/reason/calendar required
- unique employee/date
- time interval validation
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
