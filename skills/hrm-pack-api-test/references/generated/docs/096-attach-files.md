# 096. attach_files

- Bruno: `HR Leave & Overtime/attach_files.bru`
- Flow: `leave`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/hr-leave/upload_files/attach_files`
- Backend model: `hr.leave`
- Backend method: `attach_files`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1660`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/create_or_update_hr_leave.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- state-changing request; explicit execution approval required
