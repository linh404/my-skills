# 006. update_device_token

- Bruno: `Authentication & System/update_device_token.bru`
- Flow: `authentication`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/api/update-device-token`
- Backend model: `api`
- Backend method: `update-device-token`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- none

## Inputs
`employee_id`, `fcm_token`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- request contains hardcoded numeric ID; replace with isolated fixture ID before execution
- state-changing request; explicit execution approval required
