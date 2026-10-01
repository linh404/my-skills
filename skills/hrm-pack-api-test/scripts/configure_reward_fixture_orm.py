"""Odoo-shell payload for the owned Reward & Discipline API fixture."""

import datetime as dt
import json
from pathlib import Path


MARKER = "[hrm-pack-api-test:reward-fixture:v1]"
DESCRIPTION = f"{MARKER} API read-only report fixture"


def _one(records, label):
    if len(records) != 1:
        raise RuntimeError(f"{label} matched {len(records)} records; use an exact selector")
    return records


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


def _user(selector):
    users = env["res.users"].sudo().search(
        _selector_domain(selector, ("login", "email", "name"))
    )
    return _one(users, f"user selector {selector!r}")


def _employee(user):
    employees = env["hr.employee"].sudo().search([("user_id", "=", user.id)])
    return _one(employees, f"user {user.login!r} employee mapping")


def _reward_type(selector):
    Type = env["type.reward.discipline"].sudo()
    if selector:
        types = Type.search(_selector_domain(selector, ("name", "code")))
        reward_type = _one(types, f"reward type selector {selector!r}")
        if reward_type.area not in ("reward", "both"):
            raise RuntimeError(
                f"reward type {reward_type.display_name!r} is not usable for a reward"
            )
        return reward_type
    reward_type = Type.search([("area", "in", ("reward", "both"))], order="id", limit=1)
    if not reward_type:
        raise RuntimeError("no reward-capable type.reward.discipline exists")
    return reward_type


user = _user(USER_SELECTOR)
employee = _employee(user)
reward_type = _reward_type(REWARD_TYPE_SELECTOR)
Reward = env["reward.discipline"].sudo()
owned = Reward.search([("content", "=", DESCRIPTION)], order="id")
if len(owned) > 1:
    raise RuntimeError(
        f"multiple owned reward fixtures found for {DESCRIPTION!r}; clean duplicates manually"
    )

values = {
    "type": "reward",
    "type_reward_id": reward_type.id,
    "object": "personal",
    "employee_id": employee.id,
    "effective_date": dt.date.today(),
    "is_in_salary": False,
    "value": 0.0,
    "content": DESCRIPTION,
    "note": "Owned by hrm-pack-api-test; safe test data.",
    "state": "approved",
}
changes = []
fixture = owned[:1]
if not fixture:
    changes.append(
        {
            "action": "create",
            "model": "reward.discipline",
            "values": {**values, "effective_date": str(values["effective_date"])},
        }
    )
    if APPLY:
        fixture = Reward.create(values)
else:
    if fixture.employee_id != employee:
        raise RuntimeError(
            f"owned fixture {fixture.id} belongs to employee {fixture.employee_id.display_name!r}, "
            f"not {employee.display_name!r}"
        )
    if fixture.type != "reward":
        raise RuntimeError(f"owned fixture {fixture.id} is not a reward record")
    mismatches = {}
    if fixture.type_reward_id != reward_type:
        mismatches["type_reward_id"] = (fixture.type_reward_id.id, reward_type.id)
    if fixture.object != values["object"]:
        mismatches["object"] = (fixture.object, values["object"])
    if fixture.is_in_salary != values["is_in_salary"]:
        mismatches["is_in_salary"] = (fixture.is_in_salary, values["is_in_salary"])
    if fixture.value != values["value"]:
        mismatches["value"] = (fixture.value, values["value"])
    if fixture.effective_date != values["effective_date"]:
        mismatches["effective_date"] = (str(fixture.effective_date), str(values["effective_date"]))
    if fixture.state != "approved":
        mismatches["state"] = (fixture.state, "approved")
    if mismatches:
        changes.append({"action": "update_owned", "model": "reward.discipline", "id": fixture.id, "values": values})
        if APPLY:
            fixture.with_context(approval_ignore_write_check=True).write(values)

if APPLY:
    env.cr.commit()
    fixture = Reward.search([("content", "=", DESCRIPTION)], limit=1)
else:
    env.cr.rollback()

report = {
    "database": env.cr.dbname,
    "marker": MARKER,
    "user": {"id": user.id, "login": user.login},
    "employee": {"id": employee.id, "name": employee.name},
    "reward_type": {"id": reward_type.id, "name": reward_type.name, "area": reward_type.area},
    "fixture": {
        "id": fixture.id if fixture else None,
        "state": fixture.state if fixture else "approved",
        "content": DESCRIPTION,
    },
    "apply": bool(APPLY),
    "changes": changes,
}
Path(REPORT_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(REPORT_PATH).write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
