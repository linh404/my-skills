# 005. sign_up

- Bruno: `Authentication & System/sign_up.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/app/signup/user`
- Backend model: `unresolved`
- Backend method: `app_signup_user`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/controllers/main.py:299`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- none

## Inputs
`email`, `login`, `name`, `pass_wd`, `phone`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
