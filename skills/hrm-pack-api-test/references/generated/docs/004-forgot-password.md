# 004. forgot_password

- Bruno: `Authentication & System/forgot_password.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/app/forgot-password`
- Backend model: `unresolved`
- Backend method: `app_forgot_password`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/controllers/main.py:384`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- none

## Inputs
`login`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
