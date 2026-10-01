# 005. sign_up

- Bruno: `Authentication & System/sign_up.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/app/signup/user`
- Backend model: `app`
- Backend method: `signup`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- none

## Inputs
`email`, `login`, `name`, `pass_wd`, `phone`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
