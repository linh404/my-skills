# 079. app_get_address_from_coords

- Bruno: `HR Attendance/app_get_address_from_coords.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/driver.attendance.log/app_get_address_from_coords`
- Backend model: `driver.attendance.log`
- Backend method: `app_get_address_from_coords`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/driver_attendance_log.py:85`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`latitude`, `longitude`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
