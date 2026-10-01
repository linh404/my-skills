"""Odoo-shell payload for configuring the dynamic approval framework.

This file is executed by ``configure_approval.py`` inside an Odoo shell where
the standard ``env`` object is available. It intentionally uses only ORM
operations; no SQL or service restart is required.
"""
import json


MODEL_CONFIGS = {
    "hr.leave": {
        # Odoo's hr.leave uses ``confirm`` as its initial/requested state;
        # there is no ``draft`` selection value in this deployment.
        "draft": "confirm",
        "approval": "validate1",
        "approved": "validate",
        "rejected": "refuse",
        "cancel": "cancel",
    },
    "hr.attendance.explanation": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "challenge.employee": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "challenge.management": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "contract.extension": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "probationary.assessment": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "probationary.management": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "resignation.letter": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "reward.discipline": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "staff.transfer": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "staffing.plan": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
    "welfare.management": {
        "draft": "draft",
        "approval": "waiting",
        "approved": "approved",
        "rejected": "refused",
        "cancel": "cancel",
    },
}

AUTO_PREFIX = "[hrm-pack-api-test:approval-config:v1]"
STAGE_NAME = f"{AUTO_PREFIX} Default HR approval stage"


def _state_values(model):
    field = model._fields.get("state")
    if field is None:
        return set()
    if hasattr(field, "get_values"):
        # Odoo 19 returns a list of selection keys from get_values().
        return {str(value) for value in (field.get_values(model.env) or [])}
    selection = field.selection
    if callable(selection):
        selection = selection(model.env)
    return {str(item[0]) for item in (selection or []) if item}


def _user_domain(selector):
    selector = str(selector).strip()
    if selector.isdigit():
        return [("id", "=", int(selector))]
    return ["|", "|", ("login", "=", selector), ("email", "=", selector), ("name", "=", selector)]


def _get_unique_user(env, selector):
    users = env["res.users"].sudo().search(_user_domain(selector))
    if len(users) != 1:
        raise RuntimeError(f"user selector {selector!r} matched {len(users)} users; use an exact login/email/id")
    return users


def _ensure_stage(env, approver, apply, changes):
    Stage = env["approval.stage"].sudo()
    matches = Stage.search([("name", "=", STAGE_NAME), ("company_id", "=", env.company.id)])
    if len(matches) > 1:
        raise RuntimeError(f"multiple owned approval stages found for {STAGE_NAME!r}; clean duplicates manually")
    stage = matches[:1]
    vals = {"name": STAGE_NAME, "no_of_approve": 1, "no_of_reject": 1}
    if not stage:
        changes.append({"action": "create", "model": "approval.stage", "values": {**vals, "approver_id": approver.id}})
        if not apply:
            return None
        stage = Stage.create({**vals, "lines": [(0, 0, {"user_id": approver.id})]})
    else:
        line = stage.lines.filtered(lambda item: item.user_id == approver)[:1]
        if not line:
            changes.append({"action": "add", "model": "approval.stage.line", "stage_id": stage.id, "user_id": approver.id})
            if apply:
                stage.write({"lines": [(0, 0, {"user_id": approver.id})]})
        if stage.no_of_approve != 1 or stage.no_of_reject != 1:
            changes.append({"action": "update", "model": "approval.stage", "id": stage.id, "values": vals})
            if apply:
                stage.write(vals)
    return stage


def _ensure_template(env, model_name, model_record, stage, approver, originator, apply, changes):
    Template = env["approval.template"].sudo()
    template_name = f"{AUTO_PREFIX} {model_name}"
    matches = Template.search([("name", "=", template_name), ("company_id", "=", env.company.id)])
    if len(matches) > 1:
        raise RuntimeError(f"multiple owned approval templates found for {template_name!r}; clean duplicates manually")
    template = matches[:1]
    if template and template.model_id != model_record:
        raise RuntimeError(
            f"owned template {template_name!r} points to {template.model_name!r}, expected {model_name!r}"
        )
    vals = {
        "name": template_name,
        "model_id": model_record.id,
        "active": True,
        "create_check": True,
        "create_condition": False,
        "edit_check": False,
    }
    if not template:
        changes.append({"action": "create", "model": "approval.template", "values": {**vals, "originator_id": originator.id, "stage_id": stage.id if stage else None}})
        if not apply:
            return None
        template = Template.create({
            **vals,
            "originators": [(0, 0, {"user_id": originator.id})],
            "stages": [(0, 0, {"stage_id": stage.id})],
        })
    else:
        changes.append({"action": "ensure", "model": "approval.template", "id": template.id, "values": vals})
        if apply:
            template.write(vals)
        if not template.originators.filtered(lambda item: item.user_id == originator):
            changes.append({"action": "add", "model": "approval.template.originator", "template_id": template.id, "user_id": originator.id})
            if apply:
                template.write({"originators": [(0, 0, {"user_id": originator.id})]})
        if stage and not template.stages.filtered(lambda item: item.stage_id == stage):
            changes.append({"action": "add", "model": "approval.template.stage", "template_id": template.id, "stage_id": stage.id})
            if apply:
                template.write({"stages": [(0, 0, {"stage_id": stage.id})]})
    return template


def configure(env, approver_selector, originator_selector, apply=False, force=False):
    """Validate and optionally configure all dynamic-approval model records."""
    modules = env["ir.module.module"].sudo().search([("name", "=", "approval"), ("state", "=", "installed")])
    if not modules:
        raise RuntimeError("approval module is not installed in this database")

    approver = _get_unique_user(env, approver_selector)
    originator = _get_unique_user(env, originator_selector)
    IrModel = env["ir.model"].sudo()
    changes = []
    missing_models = []
    invalid_states = []
    conflicts = []
    prepared = []

    for model_name, mapping in MODEL_CONFIGS.items():
        model_record = IrModel.search([("model", "=", model_name)], limit=1)
        if not model_record:
            missing_models.append(model_name)
            continue
        Model = env[model_name].sudo()
        values = _state_values(Model)
        expected = {mapping[key] for key in ("draft", "approval", "approved", "rejected", "cancel")}
        missing_states = sorted(expected - values)
        if missing_states:
            invalid_states.append({"model": model_name, "missing_states": missing_states, "available_states": sorted(values)})
            continue
        state_vals = {
            "state_field": "state",
            "state_draft": mapping["draft"],
            "state_approval": mapping["approval"],
            "state_approved": mapping["approved"],
            "state_rejected": mapping["rejected"],
            "state_cancel": mapping["cancel"],
        }
        current = {key: getattr(model_record, key) for key in state_vals}
        non_empty = {key: value for key, value in current.items() if value}
        mismatch = {key: (current[key], state_vals[key]) for key in state_vals if current[key] and current[key] != state_vals[key]}
        if mismatch and not force:
            conflicts.append({"model": model_name, "mapping": mismatch})
            continue
        if current != state_vals:
            changes.append({"action": "update", "model": "ir.model", "id": model_record.id, "name": model_name, "values": state_vals})
        prepared.append((model_name, model_record, state_vals))

    if missing_models or invalid_states or conflicts:
        report = {
            "database": env.cr.dbname,
            "approver": {"id": approver.id, "login": approver.login, "name": approver.name},
            "originator": {"id": originator.id, "login": originator.login, "name": originator.name},
            "apply": bool(apply), "force": bool(force), "models": list(MODEL_CONFIGS),
            "changes": changes, "missing_models": missing_models,
            "invalid_states": invalid_states, "conflicts": conflicts,
        }
        env.cr.rollback()
        raise RuntimeError(json.dumps(report, ensure_ascii=False))

    stage = _ensure_stage(env, approver, apply, changes)
    try:
        for model_name, model_record, state_vals in prepared:
            if apply:
                model_record.write(state_vals)
            _ensure_template(env, model_name, model_record, stage, approver, originator, apply, changes)
        if apply:
            env["approval.template"].sudo()._update_registry()
            missing_runtime = []
            for model_name, _model_record, _state_vals in prepared:
                Model = env[model_name].sudo()
                for attr in ("x_approval_btn", "x_current_approver_ids", "approval_submit", "approval_accept"):
                    if not hasattr(Model, attr):
                        missing_runtime.append(f"{model_name}.{attr}")
            if missing_runtime:
                raise RuntimeError("registry verification failed: " + ", ".join(missing_runtime))
            env.cr.commit()
        else:
            env.cr.rollback()
    except Exception:
        env.cr.rollback()
        raise
    return {
        "database": env.cr.dbname,
        "approver": {"id": approver.id, "login": approver.login, "name": approver.name},
        "originator": {"id": originator.id, "login": originator.login, "name": originator.name},
        "apply": bool(apply),
        "force": bool(force),
        "models": list(MODEL_CONFIGS),
        "changes": changes,
    }


def _write_report(payload):
    if not REPORT_PATH:
        return
    import os
    directory = os.path.dirname(REPORT_PATH) or "."
    os.makedirs(directory, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)


try:
    result = configure(env, APPROVER_SELECTOR, ORIGINATOR_SELECTOR, APPLY, FORCE)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    _write_report(result)
except Exception as error:
    print(f"CONFIGURE_APPROVAL_ERROR: {error}")
    _write_report({
        "database": env.cr.dbname,
        "apply": bool(APPLY),
        "force": bool(FORCE),
        "error": str(error),
    })
    raise
