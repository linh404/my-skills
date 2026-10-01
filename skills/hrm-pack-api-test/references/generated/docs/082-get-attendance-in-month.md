# 082. get_attendance_in_month

- Bruno: `HR Attendance/get_attendance_in_month.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_attendance_in_month`
- Backend model: `hr.attendance`
- Backend method: `get_attendance_in_month`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:1963`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/get_attendance_today.bru`

## Inputs
`month`, `year`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
