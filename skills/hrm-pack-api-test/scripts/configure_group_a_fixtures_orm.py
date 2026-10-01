"""Idempotent Odoo-shell setup for Group-A overtime/staff-transfer fixtures."""
from datetime import date

AREA_MARKER = "[hrm-pack-api-test:area-category-fixture:v1] API test area"
OVERTIME_TYPE_MARKER = "[hrm-pack-api-test:overtime-type-fixture:v1] API test overtime"
OVERTIME_ALLOC_MARKER = "[hrm-pack-api-test:overtime-allocation-fixture:v1] API test overtime allocation"

user = env["res.users"].sudo().search([("login", "=", USER_SELECTOR)], limit=1)
if not user:
    raise RuntimeError(f"user not found: {USER_SELECTOR}")
employee = env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
if not employee:
    raise RuntimeError(f"employee mapping not found for user: {USER_SELECTOR}")

Area = env["area.category"].sudo()
area = Area.search([("name", "=", AREA_MARKER)], limit=1)
if not area:
    print({"action": "create", "model": "area.category", "name": AREA_MARKER})
    if APPLY:
        area = Area.create({"name": AREA_MARKER, "code": "HRM_API_TEST", "type": "office", "active": True})

LeaveType = env["hr.leave.type"].sudo()
overtime_type = LeaveType.search([("name", "=", OVERTIME_TYPE_MARKER)], limit=1)
if not overtime_type:
    print({"action": "create", "model": "hr.leave.type", "name": OVERTIME_TYPE_MARKER})
    if APPLY:
        overtime_type = LeaveType.create({
            "name": OVERTIME_TYPE_MARKER,
            "time_type": "leave",
            "type": "overtime",
            "requires_allocation": True,
            "employee_requests": False,
            "allocation_validation_type": "no_validation",
            "leave_validation_type": "no_validation",
            "request_unit": "day",
            "active": True,
            "company_id": env.company.id,
        })

if overtime_type:
    Allocation = env["hr.leave.allocation"].sudo()
    allocation = Allocation.search([
        ("name", "=", OVERTIME_ALLOC_MARKER),
        ("employee_id", "=", employee.id),
        ("holiday_status_id", "=", overtime_type.id),
    ], limit=1)
    if not allocation:
        print({"action": "create_and_validate", "model": "hr.leave.allocation", "name": OVERTIME_ALLOC_MARKER})
        if APPLY:
            allocation = Allocation.create({
                "name": OVERTIME_ALLOC_MARKER,
                "employee_id": employee.id,
                "holiday_status_id": overtime_type.id,
                "allocation_type": "regular",
                "number_of_days": 30.0,
                "date_from": date.today(),
                "date_to": False,
                "state": "confirm",
            })
    if APPLY and allocation and allocation.state != "validate":
        allocation._action_validate()

if APPLY:
    env.cr.commit()
print({"apply": bool(APPLY), "employee_id": employee.id, "area_id": area.id if area else None, "overtime_type_id": overtime_type.id if overtime_type else None})
