# 133. app_approval_submit

- Bruno: `Staff Transfer/app_approval_submit.bru`
- Flow: `staff_transfer`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/staff.transfer/app_approval_submit`
- Backend model: `staff.transfer`
- Backend method: `app_approval_submit`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/staff_transfer.py:1411`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/create_or_update_staff_transfer.bru`
- `Staff Transfer/get_staff_transfer_approval_progress.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
- state-changing request; explicit execution approval required
