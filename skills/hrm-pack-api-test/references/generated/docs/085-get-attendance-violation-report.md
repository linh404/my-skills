# 085. get_attendance_violation_report

- Bruno: `HR Attendance/get_attendance_violation_report.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_attendance_violation_report`
- Backend model: `hr.attendance`
- Backend method: `get_attendance_violation_report`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:2832`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Attendance/get_attendance_violation_details.bru`

## Inputs
`group_ids`, `limit`, `month`, `offset`, `year`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
