# 134. app_approval_accept

- Bruno: `Staff Transfer/app_approval_accept.bru`
- Flow: `staff_transfer`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/staff.transfer/app_approval_accept`
- Backend model: `staff.transfer`
- Backend method: `app_approval_accept`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/staff_transfer.py:1435`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/app_approval_submit.bru`
- `Staff Transfer/create_or_update_staff_transfer.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
- state-changing request; explicit execution approval required
