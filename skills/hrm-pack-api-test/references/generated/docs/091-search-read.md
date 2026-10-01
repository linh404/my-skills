# 091. search_read

- Bruno: `HR Attendance/search_read.bru`
- Flow: `gps_attendance`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.attendance/search_read`
- Backend model: `hr.attendance`
- Backend method: `search_read`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_attendance.py:15`
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`domain`, `fields`, `limit`, `offset`, `order`

## Captures
none declared

## Constraints and risks
- job.allow_gps_attendance must be true
- second create can toggle check-in/check-out
