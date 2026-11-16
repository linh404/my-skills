# Barett Odoo testing lessons

## 2026-11-04 — Issue 41 positive-line validation

- Source `addons/vdx/barett_purchase_request/models/purchase_order.py:182-220`
  validates unit price and quantity before Policy Approval and Price Approval,
  while intentionally skipping display and promotion lines.
- UI verification on PO `18` (Policy Approval) and PO `13` (Price Approval)
  with ordinary lines having quantity `1` and unit price `0` showed the
  visible error `Product lines must have a unit price and quantity greater
  than 0.`; both records kept their pre-test approval states.
- At the initial run, the database had no `purchase.order.line` with
  `is_promotion_line = true` and no linked-RFQ fixture with zero quantity;
  those gaps were later covered by the disposable fixtures below.

## 2026-11-04 — Issue 41 disposable fixtures created through UI

- Created PO `PO/26/11/00030` from PR00013 through the PR-to-RFQ flow, changed
  its ordinary line to quantity `0` and unit price `100`, and submitted Policy
  Approval. The UI showed `Product lines must have a unit price and quantity
  greater than 0.`; the order stayed `draft/none/none`, isolating the quantity
  guard from the unit-price guard.
- Created promotion `PROMO-C1-261104-01` / `QA Issue 41 Promotion` through the
  UI with one purchase condition (total order quantity >= 1) and one fixed gift
  benefit, activated it, then created PO `PO/26/11/00032` from PR00012. After
  setting the ordinary line price to `100` and applying `Tính KM`, the order
  had a promotion line with quantity `1`, price `0`, and
  `is_promotion_line=true`.
- PO32 Policy Approval submitted successfully with the zero-price promotion
  line present; Policy was approved from Approval History, then Price Approval
  submitted successfully and became pending. This covers the promotion-line
  skip branch for both submit paths.
- PO31 is a no-origin corroboration fixture created directly through the UI
  with an ordinary positive line plus the same promotion line.

## 2026-11-03 — browser evidence over RPC

- Acceptance actions must be executed and observed in the dedicated Chrome
  profile through Chrome DevTools MCP. Do not replace a click, save, approve,
  reject, or delete test with `/web/dataset/call_kw`.
- Use read-only SQL only to identify fixture state, partner ranks, installed
  modules, or a failed runtime's metadata. If RPC is ever needed for diagnosis,
  state the reason and do not use it as the acceptance result.

## 2026-11-03 — PR tier versus RFQ approval

- `purchase.request` uses the tier-validation flow; RFQs use the Barett policy
  and price approval review flow. Their rejection controls are not equivalent.
- For PR rejection, verify whether the active tier definition has comments
  enabled before interacting. A separate RFQ rejection wizard does not satisfy
  the PR rejection-reason requirement.

## 2026-11-03 — supplier popup domain

- The PR-to-RFQ supplier popup can expose autocomplete suggestions that are not
  suppliers even when the Python field has
  `res_partner_search_mode=supplier`. Compare suggestions with read-only
  `res_partner.supplier_rank` data before marking the domain criterion passed.

## 2026-11-03 — stale registry check

- A previous `purchase.request.rejection_reason` undefined-field symptom was
  not reproduced after the local runtime refreshed. Re-check the active PID,
  database, config, addons path, and installed owning module before carrying a
  stale blocker into a new run.

## 2026-11-03 — isolated Chrome MCP and source/runtime alignment

- The old fixed-profile/port workflow (`/home/linh/.config/google-chrome-codex-odoo`
  plus `9223`) can leave a stale `DevToolsActivePort` browser UUID and cause
  `ECONNREFUSED` or `404` when MCP reconnects. Use the MCP server's `--isolated`
  mode instead; verify its fresh temporary `--user-data-dir` and never patch
  the endpoint file by hand.
- A running Odoo process can still serve a previously loaded branch after the
  checkout changes. Compare the current source with the runtime behavior
  before marking an issue passed; if they disagree, record `BLOCKED` pending a
  runtime refresh. Report the mismatch and recommended refresh to the user;
  do not run the refresh unless explicitly asked.

## 2026-11-03 — replacement method flow

- When a test operation fails, replace the method rather than repeating it:
  for example, move from a failed DB query to source/UI/log/read-only metadata,
  or from a failed source path to module/manifest/model tracing.
- Record the failed method, replacement method, equivalence, and evidence. Do
  not use a replacement method to avoid a real product-behavior failure; if no
  permitted method proves the fact, report `BLOCKED`.

## 2026-11-03 — approval guard UI checks

- For delete or confirm guards on existing QA records, inspect the list
  `Tác vụ` menu and rendered button/field visibility first; do not click a
  destructive action unless the record is disposable or the user explicitly
  authorizes the state change.
- Approval-gated controls may depend on both the Odoo document `state` and a
  custom approval state. Check both. A promotion button gated only by
  `state == 'draft'` can remain visible while Policy Approval is pending or
  already approved.

## 2026-11-03 — fixture coverage before workflow actions

- Query the current document and review states before starting a UI scenario.
  Do not recycle an existing record by changing its workflow state just to
  obtain coverage.
- If the required state or user role is absent, create a clearly marked
  disposable fixture through the Odoo UI when the local test database and
  permissions allow it, then continue the scenario. Report `BLOCKED` only when
  UI fixture creation is unavailable or unsafe; use `NOT TESTED` only when no
  safe UI-creatable path exists.

## 2026-11-03 — manual purchase-request fixture approver

- A manual purchase request derives `assigned_to` from the requester's
  department manager. If the requester is the department manager, the custom
  compute intentionally falls back to the parent department and can leave the
  approver empty.
- For a pending-approval fixture, create/link a requester employee in a test
  department and set a different employee with a user account as that
  department's manager through the UI. Verify `assigned_to` before submitting
  the request for approval.

## 2026-11-03 — Issue 36 permission semantics

- Issue 36 visibility rules are conjunctive: document state, remaining
  quantity, security group, and creator/approver identity must all match; do
  not treat separate BA bullets as alternative `OR` paths.
- The BA clarification is that completing an in-progress request with
  remaining quantity still ends in `Đã hoàn thành` after the required reason
  confirmation. Test both the confirmation gate and the final state.

## 2026-11-03 — refresh before classifying wizard views

- After a wizard/view change, hard-refresh the dedicated browser tab or open a
  fresh tab before classifying the popup. Compare the fresh rendered title,
  field label, placeholders, and buttons; do not carry a stale popup DOM into
  the result.
- For the completion flow, the verified fresh UI is `Complete Purchase
  Request`, `Completion Reason`, and `Complete`/`Cancel`. If an empty-submit
  message still shows an old label, record it separately from the popup-view
  criterion and first confirm the result after a fresh tab.

## 2026-11-05 — PR Done permission and stale record rules

- Removing a `<field>` from an `ir.rule` XML record does not reset it on
  module update: `perm_write=False` stayed in `barett-dev-3` after the XML line
  was deleted, blocking purchasing users from completing PRs. Declare
  `perm_write=True` explicitly. Verified after update: purchasing user
  completed PR00145 through the UI.
- Requester-only users see no `Done` button on an `In progress` PR; the server
  guard in `button_done` is covered by unit test, not by UI.
- Many2one autocomplete: `Enter` can create a record (`Tạo "<text>"`). The
  2026-11-05 run created duplicate department `Administration` (id 15) this way.

## 2026-11-05 — PO vendor code display / tooling

- On PO screens, "Nhà cung cấp" renders `NCCxxxxxxx - <name>` via the
  `show_vendor_code` context on `partner_id`. The label "Mã nhà cung cấp" seen
  on the PO form and in the list optional columns is core `partner_ref`
  (Vendor Reference), not `vendor_code`.
- With several local DBs and empty dbfilter, `/odoo` shows no login form; log in
  via `/web/login?db=barett-dev-3`.
- chrome-devtools-mcp 1.12.0 requires `pageId` on page-level tools
  (`take_snapshot`, `navigate_page`, `click`, ...).

## 2026-11-05 — Vendor duplicate / screenshot tooling

- Vendor `Nhân bản` now opens an unsaved `/vendors/new` copy (JS patch of
  `FormController.duplicateRecord` in `barett_purchase`). If a vendor copy
  URL is a numeric id, the runtime predates that code.
- chrome-devtools-mcp refuses `take_screenshot` `filePath` outside the
  client's declared roots; with an empty `roots/list` answer, take the
  screenshot without `filePath` and decode the base64 image content.
- 2026-11-05 recheck: verified on barett-dev-3 from the Nhà cung cấp,
  Liên hệ and Khách hàng menus, for individual (CCCD) vendors, and for the
  non-vendor fallback (standard immediate copy). Duplicating from Khách hàng
  also makes the copy a customer, so `Nhóm khách hàng` becomes required.
- The form cog button's a11y label is a private-use icon glyph; match it by
  regex rather than `button ""`.
