"""Odoo-shell payload for ensuring an active language exists."""
import json
import os


def _write_report(payload):
    if not REPORT_PATH:
        return
    directory = os.path.dirname(REPORT_PATH) or "."
    os.makedirs(directory, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)


def configure(env, code, name, apply=False):
    Lang = env["res.lang"].sudo().with_context(active_test=False)
    matches = Lang.search([("code", "=", code)])
    if len(matches) > 1:
        raise RuntimeError(f"multiple res.lang rows found for code {code!r}")

    changes = []
    if not matches:
        changes.append({"action": "create", "model": "res.lang", "code": code, "name": name, "active": True})
        if apply:
            language = Lang._create_lang(code, lang_name=name)
    else:
        language = matches
        if not language.active:
            changes.append({"action": "activate", "model": "res.lang", "id": language.id, "code": code})
        else:
            changes.append({"action": "unchanged", "model": "res.lang", "id": language.id, "code": code})

    if apply:
        # Use Odoo's official language-install wizard rather than only flipping
        # ``active``: it activates the row and loads translations for all
        # installed modules without overwriting custom terms.
        wizard = env["base.language.install"].sudo().create({
            "lang_ids": [(6, 0, language.ids)],
            "overwrite": False,
        })
        wizard.lang_install()
        language = Lang.search([("code", "=", code)], limit=1)
        if not language or not language.active:
            raise RuntimeError(f"language {code!r} was not active after apply")
        env.cr.commit()
    else:
        env.cr.rollback()

    return {
        "database": env.cr.dbname,
        "language": code,
        "name": name,
        "apply": bool(apply),
        "active_after_apply": bool(apply and language and language.active),
        "changes": changes,
    }


try:
    result = configure(env, LANGUAGE_CODE, LANGUAGE_NAME, APPLY)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    _write_report(result)
except Exception as error:
    _write_report({"database": env.cr.dbname, "language": LANGUAGE_CODE, "apply": bool(APPLY), "error": str(error)})
    print(f"CONFIGURE_LANGUAGE_ERROR: {error}")
    raise
