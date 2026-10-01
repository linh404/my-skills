# KG Odoo HRM verified flow notes

These notes were derived from the current collection/source snapshot. Treat them as a fast starting point, then re-check the files when the collection or backend changes.

Use lifecycle mode for fresh-resource collection lifecycles. Execute it only
against a disposable local/test database; never use shared, staging, or
production data.

## Global prerequisites

1. Use `Authentication & System/login.bru` first. It calls `/api/login`, stores `access_token` in the secret Bruno variable `token`, and lets Bruno's default cookie jar retain the Odoo `session_id` for later generic/upload routes.
2. Most endpoints require bearer auth. The authenticated user must usually be linked to an employee; leave, resignation, transfer, helpdesk, attendance, and employee-profile flows may fail otherwise.
3. Canonical create/upload branches capture flow-scoped IDs (`leave_id`, `overtime_id`, `explanation_id`, `resignation_id`, `staff_transfer_id`, `ticket_id`, `attendance_log_id`) with Bruno response scripts. Standalone requests may still contain operator-managed fixture IDs (`id`, `employee_id`, `res_id`); verify those against the selected database.
4. Verify the selected database before any mutation. The checked-in local environment names `kg-dev-4`; do not assume it is the intended blank/test database.
5. `Staff Transfer/create_or_update_staff_transfer_2.bru` is a non-default alias. Literal bearer/Cookie headers were removed; prefer the canonical JSON-2 request and keep the alias excluded unless explicitly needed.
6. Approval APIs also require a matching approval template, originator permission, configured approval stage, and an approver assigned to the current stage (`approval/models/approval.py`); a valid record state alone is not enough.

## Recommended dependency order

The following is a source-backed starting order, not permission to execute all requests:

```text
auth.login
  -> read-only reference helpers
  -> employee/current-user context
  -> one isolated transaction flow at a time
  -> submit/approve/reject/cancel workflow
  -> detail/list/progress verification
  -> optional attachment operations
```

Reference helpers include division, department, employee group, job/job title, calendar, contract info, area category, departure reason, leave type/days, explanation reason/day type/allocation, and overtime leave type.

## Transaction flows

### Leave

```text
get_holiday_status_id_and_days
  -> create_or_update_hr_leave
  -> get_hr_leave_details / get_list_leaves
  -> optional attach_files
  -> app_approval_submit
  -> app_approval_accept OR app_approval_reject
  -> get_hr_leave_approval_progress / details
```

Constraints to inspect before execution:

- authenticated user must resolve to an employee;
- `holiday_status_id` must exist;
- quota/validity/date constraints apply;
- birthday leave requires employee birthday and matching month;
- workflow state is confirmed/first approval then approved/validated depending on the configured flow.

### Overtime

```text
get_overtime_holiday_status_id
  -> create_or_update_overtime_register
  -> app_approval_submit_2 (or the matching collection request)
  -> accept/reject
  -> get_overtime_register_details / get_list_overtime_register
```

The source enforces same-day overtime dates (`vdx_hr_holidays/models/hr_leave.py:519`). Verify the exact submit/accept request variant before running.

### Attendance explanation

```text
get_infor_explanation_reason + get_infor_day_type + get_infor_allocation
  -> optional get_attendance_explanation_2 preview/helper
  -> create_or_update_explanation
  -> attach_files (optional)
  -> get_attendance_explanation_details / approval_progress
  -> app_approval_submit
  -> app_approval_accept OR reject
  -> cancel / draft / delete only when explicitly requested
```

The source requires employee, explanation date, reason, and calendar; it has a unique employee/date constraint and validates time intervals (`vdx_hr_attendance/models/hr_attendance_explain.py:29,315,1218`).

### Resignation

```text
get_employee_infor
  -> update_employee_onboard_time
  -> get_infor_departure_reason
  -> create_or_update_resignation_letter
  -> get_resignation_letter_details / list / approval_progress
  -> app_approval_submit
  -> app_approval_accept OR reject
  -> cancel / draft only when explicitly requested
```

Required employee, resignation date, day-off, and employee onboard date; departure reason is an ID. The test helper updates the current employee's onboard date before creation. Duplicate active/draft/waiting letters and invalid dates are rejected. Workflow is draft -> waiting -> approved/refused (`vdx_hr_custom/models/resignation_letter.py:16,121,391,685`).

### Staff transfer

```text
get_infor_area_category + get_infor_job_title
  -> create_or_update_staff_transfer
  -> get_staff_transfer_details / list / approval_progress
  -> app_approval_submit
  -> app_approval_accept OR reject
  -> cancel / draft only when explicitly requested
```

Required type, employee, and effective date. Type must be one of `appoint`, `concurrent`, `adjust_salary`, `assignment`, `adjust`, or `released`. Duplicate employee/type/effective-date rows are rejected unless cancelled (`vdx_hr_custom/models/staff_transfer.py:14,438,2053,2099`).

### Helpdesk

```text
create_or_update_helpdesk_ticket
  -> get_helpdesk_ticket_details / get_list_helpdesk_ticket
  -> attach_files (multipart with created ticket res_id)
  -> delete_att_file only when explicitly requested
```

Create requires an authenticated user linked to an employee; `type` is `feedback` or `propose`. Upload requires the new ticket ID (`vdx_hr_custom/models/helpdesk_ticket.py:68,186`).

### GPS attendance

```text
app_get_address_from_coords (optional)
  -> create_attendance_gps
  -> get_attendance_today / month / employee / violation / totals
  -> upload_attendance_image (optional)
```

The authenticated employee must have a job with `allow_gps_attendance=True`. Driver employees (`position_code == NV14`) use `driver.attendance`; other employees use `hr.attendance`. There is one record per employee/day, and calling create twice toggles check-in to check-out; never treat it as a harmless read-only probe (`vdx_hr_attendance/models/driver_attendance.py:202`, `hr_attendance.py:1493`).

## Read-only precondition flows

Reward/discipline requests expose existing approved records; the collection has no corresponding create API. Blog posts, banners, org chart, and attendance reports are read-only queries. Mark these as `READ_ONLY_REQUIRES_EXISTING_DATA`, not as setup steps.

## Additional safety findings

- `get_attendance_explanation_2`, `get_hr_leave_details_2`, and
  `get_overtime_register_details_2` are wizard/transient computations despite
  their `get_` names; classify them as preview/stateful helper calls.
- `get_list_driver_attendance_log` can expose public attachment state while
  assembling its response; do not treat it as a privacy-neutral list call.
- `/recheck/image/<attachment_id>` is publicly accessible in the current
  controller; require an explicit attachment fixture and never use personal
  data in a smoke run.
- Employee-ID report calls (`get_attendance_for_one_employee`,
  `get_employee_total_work_in_month`, and `get_attendance_violation_details`)
  require a privacy/access review before using arbitrary employee IDs.

## Endpoint mechanics

- `/json/2/<model>/<method>` is an Odoo JSON-2 model method route.
- `/api/models/<model>/execute/<method>` is the custom generic executor (`vdx_hr/controllers/main.py:87`).
- `/api/models/<model>/upload_files/<method>` is multipart and requires `res_id` plus `files` (`vdx_hr/controllers/main.py:141`).
- Generic route model names convert `-` to `.`.
- Bruno's cookie jar is the session/DB binding mechanism after login; do not combine a persisted session cookie with a forced `X-Odoo-Database` header for the same request.
- `get_*_2` wizard requests are preview/helper flows; do not assume they are equivalent to direct detail endpoints.

## Evidence labels for this project

Use one of these labels for every edge/node:

- `SOURCE_VERIFIED`
- `INFERRED_FROM_FIELD_REFERENCE`
- `READ_ONLY_REQUIRES_EXISTING_DATA`
- `DESTRUCTIVE_OR_STATEFUL`
- `UNKNOWN_NEEDS_MANUAL_CONFIRMATION`
