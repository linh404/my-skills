# 143. delete_att_file

- Bruno: `Helpdesk Ticket/delete_att_file.bru`
- Flow: `helpdesk`
- Operation: `delete`
- Endpoint: `POST {{base_url}}/json/2/api/models/helpdesk-ticket/execute/delete_att_file`
- Backend model: `api`
- Backend method: `models`
- Source: unknown
- Evidence: **COLLECTION_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Helpdesk Ticket/attach_files.bru`
- `Helpdesk Ticket/create_or_update_helpdesk_ticket.bru`

## Inputs
`attachment_id`, `id`

## Captures
none declared

## Constraints and risks
- authenticated user must link to employee
- type is feedback or propose
- upload requires ticket res_id
- state-changing request; explicit execution approval required
