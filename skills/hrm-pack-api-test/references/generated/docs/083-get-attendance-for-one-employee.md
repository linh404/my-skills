# 083. get_attendance_for_one_employee

- Bruno: `HR Attendance/get_attendance_for_one_employee.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_attendance_for_one_employee`
- Backend model: `hr.attendance`
- Backend method: `get_attendance_for_one_employee`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:2173`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/get_attendance_in_month.bru`

## Inputs
`id`, `month`, `year`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
