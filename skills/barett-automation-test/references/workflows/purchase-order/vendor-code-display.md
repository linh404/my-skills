---
workflow_id: purchase-order-vendor-code-display
area: purchase-order
models: [purchase.order, res.partner]
views: [purchase.order.form, purchase.order.list, purchase.order.kpis.list]
issue_ids: [43]
status: verified
last_verified: 2026-11-05
---

# PO vendor displayed as "Mã NCC - Tên NCC"

## Purpose

Verify that on purchase orders, "Nhà cung cấp" renders as `<vendor_code> - <name>` on the form, the RFQ list and the PO list, and that the autocomplete finds vendors by code. Also verify that the standalone vendor-code field is hidden on the form and absent from the lists, and that other models still show the plain name.

## Preconditions and fixtures

- Runtime must include the `show_vendor_code` override in `barett_purchase/models/res_partner.py`. Compare the Odoo PID start time with the source mtime and the module update time.
- One editable draft RFQ: policy/price approval not `pending` or `approved`. Find it with read-only SQL on `purchase_order`.
- Vendors with `vendor_code` set. List them with read-only SQL on `res_partner.vendor_code`.

## Reusable UI steps

1. Log in at `/web/login?db=barett-dev-3`. Plain `/odoo` shows no login form while several DBs exist.
2. Open `/odoo/purchase` (RFQ list). Check the column headers and the "Nhà cung cấp" cell text.
3. Open `/odoo/action-purchase.purchase_form_action` (PO list). Check the cells, then open the optional-columns toggler and read its labels.
4. Open `/odoo/purchase/<readonly rfq id>`. Check the Nhà cung cấp link text and that no `div[name=vendor_code]` is rendered.
5. Open `/odoo/purchase/<draft rfq id>`. In the "Nhà cung cấp" combobox, select its text and type a vendor code (e.g. `NCC000000x`), a code fragment and a name fragment; read `.o-autocomplete--dropdown-item`. Press Escape, then click Discard.
6. Open `/odoo/res.partner/<vendor id>` and `/odoo/barett.payment.request/<id>`. Confirm the plain name is shown without the code.

## Expected visible states

- PO cells and the combobox read `NCCxxxxxxx - <name>`. Vendor contacts without a code show the name only.
- The optional-columns menu has no vendor-code entry. "Mã nhà cung cấp" there and on the form is the core `partner_ref` (Vendor Reference), not `vendor_code`.
- Non-PO screens show the plain name.

## Side effects and cleanup

Read-only when step 5 ends with Discard. Verify `purchase_order.partner_id`/`write_date` unchanged with read-only SQL.

## Source/runtime references

- `addons/vdx/barett_purchase/models/res_partner.py` (`_compute_display_name`, `_search_display_name`)
- `addons/vdx/barett_purchase/views/purchase_order_views.xml` (`partner_id` context `show_vendor_code`)
- `addons/vdx/barett_purchase_request/views/purchase_order_views.xml` (`vendor_code invisible="1"`)

## Known pitfalls

- The Vietnamese label "Mã nhà cung cấp" is `partner_ref`. Do not mistake it for `vendor_code`.
- The `WINNER` name search also returns global partner_autocomplete suggestions. Those are pre-existing and not part of this check.
- chrome-devtools-mcp 1.12.0 tools require `pageId` on every page-level call.
