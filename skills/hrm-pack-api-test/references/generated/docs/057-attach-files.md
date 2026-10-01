# 057. attach_files

- Bruno: `Helpdesk Ticket/attach_files.bru`
- Flow: `helpdesk`
- Operation: `upload`
- Endpoint: `POST {{base_url}}/api/models/helpdesk-ticket/upload_files/attach_files`
- Backend model: `helpdesk.ticket`
- Backend method: `attach_files`
- Source: `/home/linh/vdx/hrm-package/vdx_hr_custom/models/helpdesk_ticket.py:220`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Helpdesk Ticket/create_or_update_helpdesk_ticket.bru`

## Inputs
Inspect request body

## Captures
`id`, `res_id`, `state`

## Constraints and risks
- authenticated user must link to employee
- type is feedback or propose
- upload requires ticket res_id
- state-changing request; explicit execution approval required
