# 121. app_btn_cancel

- Bruno: `Resignation Letter/app_btn_cancel.bru`
- Flow: `resignation`
- Operation: `workflow_transition`
- Endpoint: `POST {{base_url}}/json/2/api/models/resignation-letter/execute/app_btn_cancel`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Resignation Letter/app_approval_submit.bru`
- `Resignation Letter/create_or_update_resignation_letter.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- employee/resignation date/day-off/departure reason required
- employee.onboard_time must be configured before create
- duplicate active records rejected
- state-changing request; explicit execution approval required
