# 003. app_delete_account

- Bruno: `Authentication & System/app_delete_account.bru`
- Flow: `authentication`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/res.users/app_delete_account`
- Backend model: `res.users`
- Backend method: `app_delete_account`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/res_users.py:52`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- none

## Inputs
`pass_wd`

## Captures
none declared

## Constraints and risks
- state-changing request; explicit execution approval required
