# 111. get_list_helpdesk_ticket

- Bruno: `Helpdesk Ticket/get_list_helpdesk_ticket.bru`
- Flow: `helpdesk`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/helpdesk.ticket/get_list_helpdesk_ticket`
- Backend model: `helpdesk.ticket`
- Backend method: `get_list_helpdesk_ticket`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/helpdesk_ticket.py:68`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Helpdesk Ticket/create_or_update_helpdesk_ticket.bru`
- `Helpdesk Ticket/get_helpdesk_ticket_details.bru`

## Inputs
`limit`, `offset`

## Captures
none declared

## Constraints and risks
- authenticated user must link to employee
- type is feedback or propose
- upload requires ticket res_id
