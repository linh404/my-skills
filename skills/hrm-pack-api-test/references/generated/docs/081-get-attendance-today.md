# 081. get_attendance_today

- Bruno: `HR Attendance/get_attendance_today.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_attendance_today`
- Backend model: `hr.attendance`
- Backend method: `get_attendance_today`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:2541`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/create_attendance_gps.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
