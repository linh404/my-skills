# 110. get_helpdesk_ticket_details

- Bruno: `Helpdesk Ticket/get_helpdesk_ticket_details.bru`
- Flow: `helpdesk`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/helpdesk.ticket/get_helpdesk_ticket_details`
- Backend model: `helpdesk.ticket`
- Backend method: `get_helpdesk_ticket_details`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/helpdesk_ticket.py:121`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Helpdesk Ticket/create_or_update_helpdesk_ticket.bru`

## Inputs
`id`

## Captures
none declared

## Constraints and risks
- authenticated user must link to employee
- type is feedback or propose
- upload requires ticket res_id
