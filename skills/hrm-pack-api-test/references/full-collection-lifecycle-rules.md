# Full-collection lifecycle rules

These rules apply when the goal is to exercise the collection broadly, not
just run the normal non-destructive business smoke paths.

## 1. Fresh-resource rule for state-changing APIs

Never call a destructive or state-reset endpoint against an arbitrary existing
ID. Build an isolated lifecycle with a fresh record created by the same test:

```text
create -> capture runtime ID -> transition/update -> verify -> cleanup
```

The cleanup endpoint must receive the ID captured from that lifecycle. A
hardcoded ID is not an acceptable substitute for a newly created fixture.

This applies to delete, cancel, reset-to-draft, reject, attachment-delete, and
similar state-changing endpoints. The exact legal state transition must be
verified from the source-backed workflow before execution.

## 2. Account lifecycle rule

Account deletion is tested only as:

```text
sign_up (unique test credentials)
-> login/verify the new account
-> delete_account for that same newly created account
```

Never delete the configured `admin`/operator account, never change its
password during a collection sweep, and never run password recovery against a
real address. Unique credentials must be generated per run and kept out of
reports.

## 3. Employee document lifecycle rule

Employee document APIs are tested as paired operations:

```text
upload document for the designated test employee
-> capture returned attachment ID
-> verify attachment/list/detail
-> delete exactly that captured attachment
```

Use a non-sensitive placeholder file and a designated test employee. Do not
delete hardcoded attachment IDs or documents belonging to an arbitrary
employee. If the upload response does not expose an attachment ID, mark the
delete step as a mapping/fixture blocker instead of guessing.

## 4. Runtime-ID rule and required producer order

Every detail, workflow, attachment, and cleanup request that depends on a
record must have a producer step in the same sequence. The producer captures
the ID with `bru.setVar`; consumers use that runtime variable. An unresolved
`{{variable}}`, a literal historical ID, or a manually typed ID is a mapping
defect for full-collection execution.

When a prerequisite record cannot be created, create the prerequisite fixture
first (for example allocation, calendar, leave type, area category, or
approval template). If the fixture is intentionally unavailable, report the
endpoint as `fixture_unavailable`; do not silently treat a missing record as a
backend pass.

The producer API must be called before each consumer API according to this
minimum map:

| Consumer group | Producer that must run first | Runtime values passed forward |
|---|---|---|
| Leave detail, create-date info, submit, approve, reject, cancel, reset-to-draft, delete, approval progress | `HR Leave & Overtime/get_holiday_status_id_and_days.bru` then `create_or_update_hr_leave.bru` | `leave_id` |
| Leave attachment delete | `create_or_update_hr_leave.bru` then `attach_files.bru` | `leave_id`, `leave_attachment_id` |
| Overtime detail, submit, approve, reject, delete | `get_overtime_holiday_status_id.bru` then `create_or_update_overtime_register.bru` | `overtime_id` |
| Attendance explanation detail, submit, approve, reject, cancel, draft, approval progress, delete | `get_infor_explanation_reason.bru`, `get_infor_day_type.bru`, `get_infor_allocation.bru`, then `create_or_update_explanation.bru` | `explanation_id` |
| Attendance explanation attachment delete | `create_or_update_explanation.bru` then `attach_files.bru` | `explanation_id`, `explanation_attachment_id` |
| GPS attendance reads/image upload | `create_attendance_gps.bru` | `attendance_log_id` |
| Helpdesk detail/list/attachment/delete | `create_or_update_helpdesk_ticket.bru` | `ticket_id`; upload must capture `ticket_attachment_id` |
| Resignation detail/list/submit/approve/reject/cancel/draft/delete/progress | `get_infor_departure_reason.bru` then `create_or_update_resignation_letter.bru` | `resignation_id` |
| Resignation attachment delete | `create_or_update_resignation_letter.bru` then `upload_attachment_file.bru` | `resignation_id`, returned attachment ID |
| Staff transfer list/detail/submit/approve/reject/cancel/draft/delete/progress | `get_infor_area_category.bru`, `get_infor_job_title.bru`, then `create_or_update_staff_transfer.bru` | `staff_transfer_id` |
| Reward detail | `get_list_reward_discipline.bru` | selected existing `reward_id` |
| Employee document delete | matching `upload_<document>.bru` | returned `attachment_id` |

The collection must not send a consumer request before its producer has
returned a valid record/attachment ID.

## 4.1 Dependency-first execution (mandatory)

This rule applies to **every** runner mode, including a full-collection sweep.
Do not execute the collection as a flat list of independent `.bru` files.
Before sending any endpoint, resolve its source-backed dependencies and place
the required producer/setup calls in the same business or lifecycle sequence.
Keep the producer, runtime capture, and consumer in one Bruno process.

If an endpoint has no reviewed producer chain, the correct action is to add the
mapping (or create the required fixture/setup step) before testing it. If the
prerequisite cannot be produced, classify the endpoint as
`fixture_unavailable`/`mapping_gap`; do not call it with an old or guessed ID
just to obtain an error response.

Standalone probes of runtime-dependent endpoints are diagnostic only. They must
not be counted as API failures, API passes, or business coverage. The
authoritative result is the result from the dependency-ordered business or
lifecycle chain.

## 5. Alias rule (deferred)

An alias is a second collection file for the same backend capability or route
(for example a JSON-2 route alongside a generic route, or a file ending in
`_2.bru`). It is not a new business capability. **Aliases remain where they
are and are intentionally deferred in this phase.** Do not rename, rewrite,
map, or execute aliases yet. Do not count them as business coverage. The
canonical route is the source of truth until a separate alias-cleanup phase is
approved.

## 6. Manual-fixture rule

`manual`/`fixture_required` means the current collection still contains a
literal or operator-supplied fixture and cannot safely infer the prerequisite.
For a full collection sweep, replace that manual fixture with a reviewed
setup chain (create/list -> capture ID -> request) whenever the API supports
it. If no setup chain exists, record the exact prerequisite and classify the
result as `fixture_unavailable`, not as an unexplained API failure.

## 7. Execution/reporting rule

Run the full sweep in phases so cleanup is guaranteed:

1. setup/reference data and authentication;
2. create/read/workflow branches with runtime IDs;
3. paired upload/delete and cancel/reset branches;
4. account signup/delete in an isolated test account;
5. final verification and issue logging.

Each failure must retain the request path, prerequisite chain, HTTP status,
redacted error body, and whether it is a backend bug, collection mapping gap,
fixture/environment problem, or external-service configuration problem.
