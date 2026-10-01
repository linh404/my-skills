"""Odoo-shell payload for an HR leave-allocation API fixture.

The wrapper injects ``APPLY``, ``USER_SELECTOR``, ``LEAVE_TYPE_SELECTOR``,
``MIN_DAYS``, ``ALLOCATION_NAME`` and ``REPORT_PATH`` before evaluation. Only
records carrying the fixture marker are created or updated.
"""
import datetime as dt
import json
from pathlib import Path

AUTO_PREFIX = "[hrm-pack-api-test:leave-allocation-fixture:v1]"
DEFAULT_ALLOCATION_NAME = f"{AUTO_PREFIX} API test allocation"


def _selector_domain(selector, fields):
    selector = str(selector).strip()
    if selector.isdigit():
        return [("id", "=", int(selector))]
    domain = []
    for field_name in fields:
        if domain:
            domain.insert(0, "|")
        domain.append((field_name, "=", selector))
    return domain


def _one(recordset, label):
    if len(recordset) != 1:
        raise RuntimeError(f"{label} matched {len(recordset)} records; use an exact selector")
    return recordset


def _get_user(env, selector):
    users = env["res.users"].sudo().search(
        _selector_domain(selector, ("login", "email", "name"))
    )
    return _one(users, f"user selector {selector!r}")


def _get_employee(env, user):
    employees = env["hr.employee"].sudo().search([("user_id", "=", user.id)])
    return _one(employees, f"user {user.login!r} employee mapping")


def _get_leave_type(env, selector):
    LeaveType = env["hr.leave.type"].sudo()
    if selector:
        leave_types = LeaveType.search(
            _selector_domain(selector, ("name", "x_leave_type_code"))
        )
        leave_type = _one(leave_types, f"leave-type selector {selector!r}")
    else:
        leave_type = LeaveType.search(
            [
                ("active", "=", True),
                ("requires_allocation", "=", True),
                ("type", "!=", "overtime"),
            ],
            order="id",
            limit=1,
        )
        if not leave_type:
            raise RuntimeError("no active non-overtime leave type requires allocation")
    if not leave_type.active:
        raise RuntimeError(f"leave type {leave_type.display_name!r} is inactive")
    if not leave_type.requires_allocation:
        raise RuntimeError(
            f"leave type {leave_type.display_name!r} does not require allocation; "
            "choose a quota-based leave type"
        )
    if leave_type.type == "overtime":
        raise RuntimeError("overtime leave types are not valid for the HR leave fixture")
    return leave_type


def _allocation_values(employee, leave_type, allocation_name, days):
    return {
        "name": allocation_name,
        "employee_id": employee.id,
        "holiday_status_id": leave_type.id,
        "allocation_type": "regular",
        "number_of_days": days,
        "date_from": dt.date.today(),
        "date_to": False,
        "state": "confirm",
    }


def configure(
    env,
    user_selector,
    leave_type_selector=None,
    min_days=30.0,
    allocation_name=None,
    apply=False,
):
    user = _get_user(env, user_selector)
    employee = _get_employee(env, user)
    leave_type = _get_leave_type(env, leave_type_selector)
    allocation_name = allocation_name or DEFAULT_ALLOCATION_NAME
    Allocation = env["hr.leave.allocation"].sudo()
    owned = Allocation.search(
        [
            ("name", "=", allocation_name),
            ("employee_id", "=", employee.id),
        ],
        order="id",
    )
    if len(owned) > 1:
        raise RuntimeError(
            f"multiple owned allocations found for {allocation_name!r}; clean duplicates manually"
        )

    changes = []
    allocation = owned[:1]
    values = _allocation_values(employee, leave_type, allocation_name, min_days)
    if not allocation:
        changes.append(
            {
                "action": "create_and_validate",
                "model": "hr.leave.allocation",
                "values": {
                    **values,
                    "date_from": str(values["date_from"]),
                },
            }
        )
        if apply:
            allocation = Allocation.create(values)
            allocation._action_validate()
    else:
        if allocation.holiday_status_id != leave_type:
            raise RuntimeError(
                f"owned allocation {allocation.id} belongs to leave type "
                f"{allocation.holiday_status_id.display_name!r}, not {leave_type.display_name!r}; "
                "choose that type or clean the owned fixture manually"
            )
        if allocation.number_of_days < min_days:
            changes.append(
                {
                    "action": "increase_days",
                    "model": "hr.leave.allocation",
                    "id": allocation.id,
                    "from": allocation.number_of_days,
                    "to": min_days,
                }
            )
            if apply:
                allocation.write({"number_of_days": min_days})
        if allocation.date_to:
            changes.append(
                {
                    "action": "remove_end_date",
                    "model": "hr.leave.allocation",
                    "id": allocation.id,
                    "from": str(allocation.date_to),
                }
            )
            if apply:
                allocation.write({"date_to": False})
        if allocation.state != "validate":
            changes.append(
                {
                    "action": "validate",
                    "model": "hr.leave.allocation",
                    "id": allocation.id,
                    "from": allocation.state,
                }
            )
            if apply:
                if allocation.state == "refuse":
                    allocation.write({"state": "confirm"})
                allocation._action_validate()

    if apply:
        env.cr.commit()
        allocation = Allocation.search(
            [
                ("name", "=", allocation_name),
                ("employee_id", "=", employee.id),
                ("holiday_status_id", "=", leave_type.id),
            ],
            limit=1,
        )
    else:
        env.cr.rollback()

    report = {
        "database": env.cr.dbname,
        "user": {"id": user.id, "login": user.login, "name": user.name},
        "employee": {"id": employee.id, "name": employee.name},
        "leave_type": {
            "id": leave_type.id,
            "name": leave_type.name,
            "code": getattr(leave_type, "x_leave_type_code", False),
            "requires_allocation": bool(leave_type.requires_allocation),
        },
        "allocation": {
            "id": allocation.id if allocation else None,
            "name": allocation.name if allocation else allocation_name,
            "state": allocation.state if allocation else "confirm",
            "number_of_days": allocation.number_of_days if allocation else min_days,
            "date_from": str(allocation.date_from) if allocation else str(values["date_from"]),
            "date_to": str(allocation.date_to) if allocation and allocation.date_to else None,
        },
        "apply": bool(apply),
        "changes": changes,
    }
    Path(REPORT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(REPORT_PATH).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    return report


configure(
    env,
    USER_SELECTOR,
    LEAVE_TYPE_SELECTOR,
    MIN_DAYS,
    ALLOCATION_NAME,
    APPLY,
)
