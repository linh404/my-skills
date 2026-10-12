# 006. update_device_token

- Bruno: `Authentication & System/update_device_token.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/hr.employee/update_device_token`
- Backend model: `hr.employee`
- Backend method: `update_device_token`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_employee.py:891`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- none

## Inputs
`fcm_token`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
