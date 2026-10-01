# 129. create_or_update_staff_transfer

- Bruno: `Staff Transfer/create_or_update_staff_transfer.bru`
- Flow: `staff_transfer`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/staff.transfer/create_or_update_staff_transfer`
- Backend model: `staff.transfer`
- Backend method: `create_or_update_staff_transfer`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/staff_transfer.py:1365`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/get_infor_job_title.bru`

## Inputs
`area_category_id`, `content`, `effective_date`, `type`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
- state-changing request; explicit execution approval required
