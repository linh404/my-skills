# 112. get_infor_departure_reason

- Bruno: `Resignation Letter/get_infor_departure_reason.bru`
- Flow: `resignation`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.departure.reason/get_infor_departure_reason`
- Backend model: `hr.departure.reason`
- Backend method: `get_infor_departure_reason`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/hr_departure_reason.py:10`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
