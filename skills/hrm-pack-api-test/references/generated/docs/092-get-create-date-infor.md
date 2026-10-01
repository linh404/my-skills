# 092. get_create_date_infor

- Bruno: `HR Leave & Overtime/get_create_date_infor.bru`
- Flow: `leave`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.leave/get_create_date_infor`
- Backend model: `hr.leave`
- Backend method: `get_create_date_infor`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_attendance/models/hr_leave.py:1020`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`rec_id`

## Captures
none declared

## Constraints and risks
- employee context required
- holiday_status_id must exist
- quota/date validity enforced
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
