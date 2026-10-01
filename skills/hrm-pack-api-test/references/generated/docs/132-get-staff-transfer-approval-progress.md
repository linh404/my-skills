# 132. get_staff_transfer_approval_progress

- Bruno: `Staff Transfer/get_staff_transfer_approval_progress.bru`
- Flow: `staff_transfer`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/staff.transfer/get_staff_transfer_approval_progress`
- Backend model: `staff.transfer`
- Backend method: `get_staff_transfer_approval_progress`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/staff_transfer.py:1092`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/create_or_update_staff_transfer.bru`
- `Staff Transfer/get_staff_transfer_details.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
