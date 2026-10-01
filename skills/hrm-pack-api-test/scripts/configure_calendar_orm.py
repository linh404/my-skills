"""Odoo-shell payload for an HRM API resource-calendar fixture.

The wrapper script injects ``APPLY``, ``USER_SELECTOR``, ``CALENDAR_NAME``,
``JOB_NAME`` and ``REPORT_PATH`` before this file is evaluated.  The payload
uses ORM only and rolls back the transaction on dry-run or any error.
"""
import json
import os


AUTO_PREFIX = "[hrm-pack-api-test:calendar-fixture:v1]"
DEFAULT_CALENDAR_NAME = f"{AUTO_PREFIX} API test calendar"
DEFAULT_JOB_NAME = f"{AUTO_PREFIX} API test job"


def _user_domain(selector):
    selector = str(selector).strip()
    if selector.isdigit():
        return [("id", "=", int(selector))]
    return [
        "|",
        "|",
        ("login", "=", selector),
        ("email", "=", selector),
        ("name", "=", selector),
    ]


def _get_user(env, selector):
    users = env["res.users"].sudo().search(_user_domain(selector))
    if len(users) != 1:
        raise RuntimeError(
            f"user selector {selector!r} matched {len(users)} users; "
            "use an exact login/email/id"
        )
    return users


def _fallback_attendance_values():
    values = []
    for day in range(5):
        label = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][day]
        values.extend(
            [
                {
                    "name": f"{label} Morning",
                    "dayofweek": str(day),
                    "hour_from": 9.0,
                    "hour_to": 12.0,
                    "day_period": "morning",
                },
                {
                    "name": f"{label} Lunch",
                    "dayofweek": str(day),
                    "hour_from": 12.0,
                    "hour_to": 13.0,
                    "day_period": "lunch",
                },
                {
                    "name": f"{label} Afternoon",
                    "dayofweek": str(day),
                    "hour_from": 13.0,
                    "hour_to": 17.0,
                    "day_period": "afternoon",
                },
            ]
        )
    return values


def _attendance_values(calendar=None):
    """Copy a real calendar's attendance lines; keep a safe fallback."""
    if calendar and calendar.attendance_ids:
        values = []
        line_fields = {
            "name",
            "dayofweek",
            "hour_from",
            "hour_to",
            "day_period",
            "week_type",
            "date_from",
            "date_to",
        }
        for line in calendar.attendance_ids:
            values.append(
                {
                    field_name: getattr(line, field_name)
                    for field_name in line_fields
                    if field_name in line._fields and getattr(line, field_name, False) not in (False, None)
                }
            )
        if values:
            return values
    return _fallback_attendance_values()


def _calendar_base_values(employee, template, calendar_name):
    company = employee.company_id or env.company
    template_tz = template.tz if template else False
    values = {
        "name": calendar_name,
        "company_id": company.id,
        "tz": (
            template_tz
            or employee.user_id.tz
            or env.user.tz
            or "Asia/Saigon"
        ),
        "number_work": 1.0,
        "dayoff_time": 2,
        "break_minutes": 60.0,
        "is_full_shift": True,
    }
    # Preserve standard calendar options when the target Odoo build exposes
    # them, without assuming a particular Odoo minor version.
    for field_name in ("two_weeks_calendar", "flexible_hours", "full_time_required_hours"):
        if template and field_name in template._fields:
            values[field_name] = getattr(template, field_name)
    return values


def _ensure_calendar(env, employee, calendar_name, apply, changes):
    Calendar = env["resource.calendar"].sudo()
    company = employee.company_id or env.company
    calendars = Calendar.search(
        [("name", "=", calendar_name), ("company_id", "=", company.id)]
    )
    if len(calendars) > 1:
        raise RuntimeError(
            f"multiple owned calendars found for {calendar_name!r}; clean duplicates manually"
        )
    calendar = calendars[:1]
    template = getattr(company, "resource_calendar_id", False) or Calendar.search(
        [("company_id", "=", company.id)], order="id", limit=1
    )
    values = _calendar_base_values(employee, template, calendar_name)
    if not calendar:
        attendance_values = _attendance_values(template)
        changes.append(
            {
                "action": "create",
                "model": "resource.calendar",
                "values": {**values, "attendance_count": len(attendance_values)},
            }
        )
        if not apply:
            return None
        calendar = Calendar.create(
            {
                **values,
                "attendance_ids": [(0, 0, item) for item in attendance_values],
            }
        )
    else:
        missing = []
        existing_keys = {
            (line.dayofweek, float(line.hour_from), float(line.hour_to), line.day_period)
            for line in calendar.attendance_ids
        }
        for item in _attendance_values(calendar):
            key = (
                item["dayofweek"],
                float(item["hour_from"]),
                float(item["hour_to"]),
                item["day_period"],
            )
            if key not in existing_keys:
                missing.append(item)
        if calendar.tz != values["tz"] or calendar.number_work != values["number_work"]:
            changes.append(
                {
                    "action": "ensure",
                    "model": "resource.calendar",
                    "id": calendar.id,
                    "values": values,
                }
            )
            if apply:
                calendar.write(values)
        if missing:
            changes.append(
                {
                    "action": "add_attendance_lines",
                    "model": "resource.calendar.attendance",
                    "calendar_id": calendar.id,
                    "count": len(missing),
                }
            )
            if apply:
                calendar.write({"attendance_ids": [(0, 0, item) for item in missing]})
    return calendar


def _ensure_job(env, employee, calendar, job_name, apply, changes):
    Job = env["hr.job"].sudo()
    job = employee.job_id
    if not job:
        matches = Job.search(
            [("name", "=", job_name), ("company_id", "=", employee.company_id.id)]
        )
        if len(matches) > 1:
            raise RuntimeError(
                f"multiple owned jobs found for {job_name!r}; clean duplicates manually"
            )
        job = matches[:1]
        if not job:
            changes.append(
                {
                    "action": "create",
                    "model": "hr.job",
                    "values": {"name": job_name, "company_id": employee.company_id.id},
                }
            )
            if not apply:
                changes.extend(
                    [
                        {
                            "action": "assign_employee_job",
                            "model": "hr.employee",
                            "id": employee.id,
                            "job_id": None,
                            "planned": True,
                        },
                        {
                            "action": "link_calendar_to_job",
                            "model": "hr.job",
                            "id": None,
                            "calendar_id": None,
                            "planned": True,
                        },
                    ]
                )
                return None
            job = Job.create({"name": job_name, "company_id": employee.company_id.id})
        if employee.job_id != job:
            changes.append(
                {
                    "action": "assign_employee_job",
                    "model": "hr.employee",
                    "id": employee.id,
                    "job_id": job.id,
                }
            )
            if apply:
                employee.write({"job_id": job.id})
    if calendar and calendar not in job.resource_calendar_ids:
        changes.append(
            {
                "action": "link_calendar_to_job",
                "model": "hr.job",
                "id": job.id,
                "calendar_id": calendar.id,
            }
        )
        if apply:
            job.write({"resource_calendar_ids": [(4, calendar.id)]})
    return job


def configure(env, user_selector, calendar_name=None, job_name=None, apply=False):
    user = _get_user(env, user_selector)
    employees = env["hr.employee"].sudo().search([("user_id", "=", user.id)])
    if len(employees) != 1:
        raise RuntimeError(
            f"user {user.login!r} maps to {len(employees)} employees; expected exactly one"
        )
    employee = employees
    if not employee.company_id:
        raise RuntimeError(f"employee {employee.display_name!r} has no company")
    calendar_name = calendar_name or DEFAULT_CALENDAR_NAME
    job_name = job_name or DEFAULT_JOB_NAME
    changes = []
    calendar = _ensure_calendar(env, employee, calendar_name, apply, changes)
    job = _ensure_job(env, employee, calendar, job_name, apply, changes)
    if apply:
        env.cr.commit()
        # Re-read the records after commit so the report contains runtime IDs.
        calendar = env["resource.calendar"].sudo().search(
            [("name", "=", calendar_name), ("company_id", "=", employee.company_id.id)],
            limit=1,
        )
        employee.invalidate_recordset()
        job = employee.job_id
    else:
        env.cr.rollback()
    return {
        "database": env.cr.dbname,
        "user": {"id": user.id, "login": user.login, "name": user.name},
        "employee": {"id": employee.id, "name": employee.name},
        "job": {"id": job.id if job else None, "name": job.name if job else job_name},
        "calendar": {
            "id": calendar.id if calendar else None,
            "name": calendar.name if calendar else calendar_name,
            "attendance_count": len(calendar.attendance_ids) if calendar else len(_fallback_attendance_values()),
        },
        "apply": bool(apply),
        "changes": changes,
    }


def _write_report(payload):
    if not REPORT_PATH:
        return
    directory = os.path.dirname(REPORT_PATH) or "."
    os.makedirs(directory, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)


try:
    result = configure(env, USER_SELECTOR, CALENDAR_NAME, JOB_NAME, APPLY)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    _write_report(result)
except Exception as error:
    env.cr.rollback()
    print(f"CONFIGURE_CALENDAR_FIXTURE_ERROR: {error}")
    _write_report({"database": env.cr.dbname, "apply": bool(APPLY), "error": str(error)})
    raise
