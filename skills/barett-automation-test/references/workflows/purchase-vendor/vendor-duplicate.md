---
workflow_id: purchase-vendor-vendor-duplicate
area: purchase-vendor
models: [res.partner]
views: [res.partner.form, res.partner.list]
issue_ids: []
status: verified
last_verified: 2026-11-05
---

# Vendor duplicate opens an unsaved, validated copy

## Purpose

Verify that "Tác vụ > Nhân bản" on a vendor does the following:

- It opens an unsaved form, prefilled from the source vendor, with MST/CCCD empty and required.
- It never saves the copy or consumes a vendor code until the user saves.
- After a successful save, the copy has a vendor code and `supplier_rank > 0`, so it shows in the Nhà cung cấp menu.

## Preconditions and fixtures

- Local Odoo at `http://localhost:8069/odoo`, database `barett-dev-3`, running code that includes `barett_purchase/static/src/js/vendor_duplicate.js`. A restart is enough to load it; no module update is needed.
- A standalone company vendor to use as the source. Prefer a QA vendor such as `[QT05/11] NCC Test`; do not modify it.
- Read-only SQL baseline:
  - `select max(id) from res_partner`.
  - The vendor-code sequence value: find the id with `select id from ir_sequence where code='barett.vendor.code'`, then read `select last_value from ir_sequence_<id padded to 3>`.

## Reusable UI steps

1. Open `/odoo/action-account.res_partner_action_supplier/<source vendor id>`. If `navigate_page` times out, use `wait_for` on the vendor name.
2. Click the cog button in the control panel (a11y `button ""`, expandable), then the menu item `Nhân bản`. The label has a leading icon glyph, so match it loosely.
3. Check the copy form:
   - URL ends with `/vendors/new`, and the name ends with `(sao chép)`.
   - MST is empty with `o_required_modifier`, and vendor code is empty.
   - Email and vendor type are prefilled and required.
4. Rename the copy with a `[QA-<run id>]` marker.
5. Click `Lưu thủ công` with MST empty. Expect the notification `Trường không hợp lệ: Mã số thuế`, and SQL max id and sequence unchanged.
6. Fill an unused MST (check it with SQL first) and click `Lưu thủ công`. Expect URL `/vendors/<new id>` and a new vendor code.
7. Open the vendor list (`?view_type=list`) and search the QA marker. Expect the row to show with the default `Hoá đơn mua hàng` facet active.
8. Optional discard branch: duplicate again and click `Huỷ bỏ mọi thay đổi`. Expect a return to `/odoo/vendors`, with no new partner and the sequence unchanged.
9. Contacts branch: open `/odoo/contacts/<vendor id>` and duplicate. Expect `/contacts/new`. After saving with MST, SQL must show `is_company=t` and `supplier_rank=1`.
10. Customers branch: open `/odoo/action-account.res_partner_action_customer/<vendor id>` and duplicate. `Nhóm khách hàng` becomes required, because the menu sets `customer_rank=1`. After saving, the copy has both a vendor code and a customer code.
11. Individual branch: use a QA `Cá nhân` vendor with a CCCD. Create it via Nhà cung cấp → `Mới` → `Cá nhân` if none exists. The copy has CCCD empty and required, and saving is blocked with `Căn cước công dân (CCCD)`.
12. Non-vendor branch: create a QA contact via `/odoo/contacts/new` and duplicate it. Expect the standard Odoo duplicate: saved at once with a numeric id and no vendor code.

## Expected visible states

- Unsaved copy at `/vendors/new` with MST required and empty.
- Save without MST is blocked on the client.
- After saving, `NCCxxxxxxx` is shown and the copy is listed under the supplier filter.

## Side effects and cleanup

- Step 6 creates one QA vendor and consumes one vendor-code number. Retain it with its QA marker; do not delete it automatically.

## Source/runtime references

- `addons/vdx/barett_purchase/models/res_partner.py`: `barett_vendor_duplicate_values`, `copy_data`, `copy`, and `create` (the `supplier_rank` and `is_company` defaults).
- `addons/vdx/barett_purchase/static/src/js/vendor_duplicate.js`.

## Known pitfalls

- If the copy URL is a numeric id instead of `/new`, the runtime still runs the old code: the server `copy()` saved it at once. Check the PID start time against the source edit time before classifying the run as a failure.
- The cog button's a11y label is a single private-use icon glyph, not an empty string. Match it with a regex such as `button "[\ue000-\uf8ff]" expandable`, then wait for `Nhân bản` before clicking.
- The bridge refuses `take_screenshot` with `filePath` when the client declares no roots. Take the screenshot without `filePath` and decode the base64 image instead.
