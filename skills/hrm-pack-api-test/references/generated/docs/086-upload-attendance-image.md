# 086. upload_attendance_image

- Bruno: `HR Attendance/upload_attendance_image.bru`
- Flow: `gps_attendance`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/driver-attendance-log/upload_files/upload_attendance_image`
- Backend model: `driver.attendance.log`
- Backend method: `upload_attendance_image`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/driver_attendance_log.py:224`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/get_attendance_violation_report.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
- state-changing request; explicit execution approval required
