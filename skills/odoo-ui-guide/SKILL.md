---
name: odoo-ui-guide
description: Run a business flow through the Odoo web UI with Playwright, take annotated screenshots (numbered red boxes) at each step, and produce a user guide (Markdown -> DOCX with table of contents -> PDF). Works for any Odoo project/instance. Use when the user asks for a "hướng dẫn thao tác", user guide, step-by-step manual with screenshots, or to "vừa test vừa chụp màn hình hướng dẫn" a feature.
---

# Odoo UI guide (test + screenshots + DOCX/PDF)

Produces a guide in the style of `huong-dan-tam-ung-hoan-ung.pdf`: title, auto table of contents,
role/menu tables, numbered steps, 1440x900 screenshots with red numbered boxes, field tables,
error-message table and a "current limitations" section. The flow is executed for real, so the
guide doubles as a UI test: anything that fails or looks wrong goes into the guide's limitations
section and the final report.

## 1. Ask first (mandatory, before touching any browser or DB)

Use AskUserQuestion. Never assume a project, instance or flow from earlier conversations.
Ask for, in one round when possible:

1. **Instance and database**: base URL (e.g. `http://localhost:8069`, a dev site) and DB name.
   Offer the instances/DBs you can see in the current project (config files, CLAUDE.md), plus "Other".
   If the instance is shared (dev/staging/prod), confirm the user accepts that test records will be created there.
2. **Flow to document**: the starting point and the end point (e.g. "from annual plan to approved
   monthly plan"), and which branches to cover (approve and/or reject, cancel, etc.).
   Offer the flows you can infer from the module (menus, states, buttons), plus "Other".
3. **Logins per role** (only if not already documented in the project): which user acts as
   requester / approver / etc. Don't document the login itself in the guide unless asked.
4. **Output**: file name/location for the DOCX and PDF (default: the user's home dir,
   `huong-dan-<slug>.docx/.pdf`) and the source FS to cite, if any.

## 2. Understand the flow before clicking

- Read the module code for the chosen flow: models (states, `action_*` methods and their
  `UserError`s), views (buttons and `invisible` conditions), security groups, tier definitions, menus.
- Read the FS if the user gave one. Note preconditions (master data, config) the flow needs.
- Check the target DB for the data the flow needs (read-only queries are fine for this).
  Prefer creating fresh, clearly named demo records through the UI over reusing QA data.
- Get exact UI labels from `i18n/vi.po` (or the UI itself) — never translate on your own.

## 3. Browser setup

- Playwright MCP may only read files under its output root (e.g. `~/.cache/playwright-mcp-output`).
  Copy the helper there, then load it once per browser session:
  ```bash
  cp <skill>/scripts/shot.js ~/.cache/playwright-mcp-output/guide-shot.js
  ```
  `browser_run_code_unsafe({ filename: "~/.cache/playwright-mcp-output/guide-shot.js" })` (absolute path).
  Re-load it if the browser restarts (`page.context().__guideShot` becomes undefined).
- `browser_resize` to **1440 x 900**.
- Log in: `await page.context().__guideLogin(page, baseUrl, db, login, password)` (handles the
  "Choose a user" screen). Keep it out of the guide.
- Work directory: `~/.cache/playwright-mcp-output/guides/<slug>/` with `img/` for screenshots and
  the Markdown file. Never write screenshots or scratch files into a repository.

## 4. Run the flow and capture

For each step: act through the UI (click, fill, select) like a user, then capture:

```js
async (page) => {
  const G = '/home/<user>/.cache/playwright-mcp-output/guides/<slug>/img';
  return await page.context().__guideShot(page, `${G}/05-confirm.png`, [
    { target: 'button[name="action_confirm"]', label: '1 Xác nhận', tag: 'right' },
    { target: 'div[name="partner_ids"]', label: '2 Khách hàng' },
  ]);
}
```

- `target`: CSS/Playwright selector; prefer stable Odoo hooks: `button[name="action_x"]`,
  `div[name="field"]`, `td[name="field"]` in one2many rows, `a.nav-link:has-text("Tab")`,
  `.o_statusbar_status button[data-value="state"]`, or a function returning a Locator.
- `tag`: `above` (default), `below`, `right`, `inside`. Use `below` for statusbar/top-edge items.
- The result lists `found: false` for missing targets — fix the selector and recapture.
- Name files `NN-step.png` in flow order. Look at each screenshot (Read) before moving on:
  check that labels don't hide the content they point at and nothing is clipped.

UI tips (Odoo 17/18):
- Do not wait for `networkidle` (long-polling never idles); wait for a concrete element instead.
- many2one / many2many inputs: `pressSequentially(text, {delay: 30})`, then click the
  `.o-autocomplete--dropdown-menu .dropdown-item` that matches.
- one2many editable rows: click the cell, fill `tr.o_selected_row td[name=...] input`, click
  outside the list (or press Tab) before saving; verify the saved value — fast typing can drop it.
- Confirmation dialogs: `.modal-footer button.btn-primary`.
- Statusbar buttons and state labels can share text — select buttons by `name=`.

Record while running: every blocking message seen, every untranslated label, dead-end states,
anything that differs from the FS. These feed the guide's last sections and your final report.

## 5. Write the guide

Follow `references/guide-outline.md`. Write `<slug>.md` next to `img/`, images as
`![](img/NN-step.png){width=100%}`.

## 6. Build DOCX + PDF

```bash
<skill>/scripts/build_guide.sh ~/.cache/playwright-mcp-output/guides/<slug>/<slug>.md /home/<user>/huong-dan-<slug>
```

pandoc (styles from `assets/reference.docx`, TOC depth 2, title "Mục lục") → LibreOffice via
Python-UNO refreshes the TOC and exports the PDF. Needs `pandoc`, `soffice`, and `/usr/bin/python3`
with `uno` (`python3-uno`). Override the TOC title with `TOC_TITLE=...` for other languages.
Render 2–3 pages with `pdftoppm -r 40` and look at them before reporting.

## 7. Report

Tell the user: output paths (DOCX + PDF), the DB/instance and the records created (codes/IDs),
and the issues found during the run (also listed in the guide's limitations section).
Do not delete the created records unless asked.
