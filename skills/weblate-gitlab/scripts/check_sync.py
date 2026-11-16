"""Read-only: compare local Odoo POT/PO with a Weblate project.

Usage: check_sync.py <weblate_project> <out_dir> [repo_root] [lang]
"""
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
_here = os.path.dirname(os.path.abspath(__file__))
for _d in (os.path.join(_here, "..", "..", "odoo-wlc", "scripts"), os.path.expanduser("~/.codex/skills/odoo-wlc/scripts")):
    if os.path.exists(os.path.join(_d, "weblate_api.py")):
        sys.path.insert(0, _d)
        break
import weblate_api as w
import polib

P = sys.argv[1]
ROOT = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
LANG = sys.argv[4] if len(sys.argv) > 4 else "vi"
OUT = sys.argv[2]
cfg = w.load_config()
os.makedirs(OUT, exist_ok=True)


def raw(path):
    req = urllib.request.Request(cfg["url"] + path, headers={"Authorization": "Token " + cfg["key"], "User-Agent": w.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return "HTTP%s" % e.code


def key(e):
    return (e.msgctxt or "", e.msgid)


def entries(po):
    return {key(e): e for e in po if not e.obsolete}


def one(slug):
    comp = w.api_get(cfg, f"components/{P}/{slug}/")
    res = {"slug": slug, "new_base": comp["new_base"]}
    repo = w.api_get(cfg, f"components/{P}/{slug}/repository/")
    res["remote"] = repo["remote_commit"]["shortrevision"] if repo.get("remote_commit") else None
    res["needs"] = [k for k in ("needs_commit", "needs_merge", "needs_push") if repo.get(k)]
    res["merge_failure"] = repo.get("merge_failure")
    txt = raw(f"translations/{P}/{slug}/{LANG}/file/")
    if txt.startswith("HTTP"):
        res["weblate_lang"] = txt
        return res
    open(f"{OUT}/{slug}.{LANG}.po", "w").write(txt)
    wpo = entries(polib.pofile(txt))
    pot_path = os.path.join(ROOT, comp["new_base"])
    vi_path = os.path.join(os.path.dirname(pot_path), f"{LANG}.po")
    if os.path.exists(pot_path):
        pot = entries(polib.pofile(pot_path))
        res["pot_missing_on_weblate"] = len(pot.keys() - wpo.keys())
        res["weblate_extra_vs_pot"] = len(wpo.keys() - pot.keys())
        res["pot_total"] = len(pot)
    else:
        res["pot_local"] = "MISSING"
    res["weblate_total"] = len(wpo)
    res["weblate_translated"] = sum(1 for e in wpo.values() if e.translated())
    if os.path.exists(vi_path):
        lpo = entries(polib.pofile(vi_path))
        res["po_only_local"] = len(lpo.keys() - wpo.keys())
        res["po_only_weblate"] = len(wpo.keys() - lpo.keys())
        diff = []
        for k in lpo.keys() & wpo.keys():
            a, b = lpo[k], wpo[k]
            if (a.msgstr, a.msgstr_plural, a.fuzzy) != (b.msgstr, b.msgstr_plural, b.fuzzy):
                diff.append({"msgid": k[1][:80], "local": a.msgstr[:80], "weblate": b.msgstr[:80], "lf": a.fuzzy, "wf": b.fuzzy})
        res["msgstr_diff"] = len(diff)
        res["diff_samples"] = diff[:5]
        res["local_translated"] = sum(1 for e in lpo.values() if e.translated())
        res["local_po_git"] = "untracked" if os.system(f"git -C {ROOT} ls-files --error-unmatch {vi_path} >/dev/null 2>&1") else "tracked"
    else:
        res["po_local"] = "MISSING"
    return res


slugs = [c["slug"] for c in w.api_get_paged(cfg, f"projects/{P}/components/") if c["slug"] != "glossary"]
with ThreadPoolExecutor(6) as ex:
    results = list(ex.map(one, slugs))
json.dump(results, open(f"{OUT}/result.json", "w"), ensure_ascii=False, indent=1)
print("remote_commit", {x.get("remote") for x in results}, "needs", {tuple(x.get("needs", [])) for x in results},
      "merge_failure", {x.get("merge_failure") for x in results})
for x in results:
    flags = []
    if x.get("weblate_lang"):
        flags.append(f"weblate {LANG} " + x["weblate_lang"])
    if x.get("pot_local"):
        flags.append("pot local missing")
    if x.get("po_local"):
        flags.append(f"{LANG}.po local missing")
    for k in ("pot_missing_on_weblate", "weblate_extra_vs_pot", "po_only_local", "po_only_weblate", "msgstr_diff"):
        if x.get(k):
            flags.append(f"{k}={x[k]}")
    print(x["slug"], x.get("pot_total"), x.get("weblate_total"), x.get("weblate_translated"),
          x.get("local_translated"), x.get("local_po_git", ""), flags or "OK")
