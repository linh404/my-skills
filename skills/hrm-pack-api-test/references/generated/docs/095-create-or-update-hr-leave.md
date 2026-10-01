# 095. create_or_update_hr_leave

- Bruno: `HR Leave & Overtime/create_or_update_hr_leave.bru`
- Flow: `leave`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/create_or_update_hr_leave`
- Backend model: `hr.leave`
- Backend method: `create_or_update_hr_leave`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1041`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `HR Leave & Overtime/get_holiday_status_id_and_days.bru`

## Inputs
`holiday_status_id`, `name`, `request_date_from`, `request_date_from_period`, `request_date_to`, `request_unit_half`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- state-changing request; explicit execution approval required
