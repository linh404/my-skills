# 090. get_total_work_in_month

- Bruno: `HR Attendance/get_total_work_in_month.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/get_total_work_in_month`
- Backend model: `hr.attendance`
- Backend method: `get_total_work_in_month`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:2363`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`month`, `year`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
