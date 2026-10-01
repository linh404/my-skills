# 088. get_list_driver_attendance_log

- Bruno: `HR Attendance/get_list_driver_attendance_log.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/driver.attendance.log/get_list_driver_attendance_log`
- Backend model: `driver.attendance.log`
- Backend method: `get_list_driver_attendance_log`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/driver_attendance_log.py:127`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`date_from`, `date_to`, `limit`, `offset`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
