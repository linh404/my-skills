# 142. delete_att_file

- Bruno: `HR Leave & Overtime/delete_att_file.bru`
- Flow: `leave`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/delete_att_file`
- Backend model: `hr.leave`
- Backend method: `delete_att_file`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1704`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/app_approval_submit.bru`
- `HR Leave & Overtime/attach_files.bru`
- `HR Leave & Overtime/create_or_update_hr_leave.bru`

## Inputs
`attachment_id`, `id`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- state-changing request; explicit execution approval required
