# 146. app_delete_staff_transfer

- Bruno: `Staff Transfer/app_delete_staff_transfer.bru`
- Flow: `staff_transfer`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/staff.transfer/app_delete_staff_transfer`
- Backend model: `staff.transfer`
- Backend method: `app_delete_staff_transfer`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/staff_transfer.py:1350`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/create_or_update_staff_transfer.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
- state-changing request; explicit execution approval required
