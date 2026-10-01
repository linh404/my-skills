# 099. get_list_leaves

- Bruno: `HR Leave & Overtime/get_list_leaves.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_list_leaves`
- Backend model: `hr.leave`
- Backend method: `get_list_leaves`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:813`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/create_or_update_hr_leave.bru`
- `HR Leave & Overtime/get_hr_leave_details.bru`

## Inputs
`date_from`, `limit`, `offset`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
