# 004. forgot_password

- Bruno: `Authentication & System/forgot_password.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/app/forgot-password`
- Backend model: `app`
- Backend method: `forgot-password`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- none

## Inputs
`login`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- state-changing request; explicit execution approval required
