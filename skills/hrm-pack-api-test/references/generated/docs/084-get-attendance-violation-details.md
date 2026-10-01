# 084. get_attendance_violation_details

- Bruno: `HR Attendance/get_attendance_violation_details.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_attendance_violation_details`
- Backend model: `hr.attendance`
- Backend method: `get_attendance_violation_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:2913`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/get_attendance_for_one_employee.bru`

## Inputs
`employee_id`, `month`, `year`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
