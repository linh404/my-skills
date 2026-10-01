# 055. create_or_update_helpdesk_ticket

- Bruno: `Helpdesk Ticket/create_or_update_helpdesk_ticket.bru`
- Flow: `helpdesk`
- Operation: `mutate`
- Endpoint: `POST {{base_url}}/json/2/helpdesk.ticket/create_or_update_helpdesk_ticket`
- Backend model: `helpdesk.ticket`
- Backend method: `create_or_update_helpdesk_ticket`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/helpdesk_ticket.py:186`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
`description`, `name`, `type`

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- authenticated user must link to employee
- type is feedback or propose
- upload requires ticket res_id
- state-changing request; explicit execution approval required
