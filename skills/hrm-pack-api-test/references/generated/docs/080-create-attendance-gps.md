# 080. create_attendance_gps

- Bruno: `HR Attendance/create_attendance_gps.bru`
- Flow: `gps_attendance`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/driver.attendance/create_attendance_gps`
- Backend model: `driver.attendance`
- Backend method: `create_attendance_gps`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/driver_attendance.py:187`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/app_get_address_from_coords.bru`

## Inputs
`address`, `latitude`, `longitude`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
- state-changing request; explicit execution approval required
