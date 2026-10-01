# 002. app_change_password

- Bruno: `Authentication & System/app_change_password.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/res.users/app_change_password`
- Backend model: `res.users`
- Backend method: `app_change_password`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/res_users.py:13`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- none

## Inputs
`new_passwd`, `old_passwd`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
