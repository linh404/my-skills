---
workflow_id: purchase-vendor-issue-17-required-label
area: purchase-vendor
models: [res.partner]
views: [res.partner.form, res.partner.list]
issue_ids: [17]
status: verified-with-failure
last_verified: 2026-11-05
---

# Vendor group required and label check

## Purpose

Verify issue #17 for the vendor form: vendor group is required only for vendors, and the visible label uses the requested Vietnamese wording.

## Preconditions and fixtures

- Local Odoo is running at `http://localhost:8069/odoo` on database `barett-dev-3`.
- Use the Purchase app and a fresh isolated Chrome DevTools profile.
- If a create flow is needed, use a disposable `[QA-ISSUE-17]` marker and record cleanup.

## Reusable UI steps

1. Open `Mua hàng → Đơn hàng → Nhà cung cấp`.
2. Click `Mới` and inspect the vendor group widget on the form.
3. Verify the widget has required styling while the partner is a vendor; save only with disposable data.
4. Open a known non-vendor contact and verify the vendor group field is not required or visible.
5. Verify the vendor code and vendor group labels use `Nhóm nhà cung cấp`.

## Expected visible states

- Vendor form: `vendor_type_id` is required.
- Non-vendor contact: `vendor_type_id` is not required.
- Vendor labels: `Nhóm nhà cung cấp`.

## Side effects and cleanup

Use only disposable vendor fixtures. Delete them through the UI when safe; do not modify existing vendors.

## Source/runtime references

- `addons/vdx/barett_purchase/models/res_partner.py:56`
- `addons/vdx/barett_purchase/views/res_partner_views.xml:11`

## Known pitfalls

- The current defaulting path automatically assigns `NCC trong nước` when a vendor is created, so clearing the form value alone does not exercise a missing-default backend error.
- The current runtime labels still show `Nhà cung cấp`; the translation criterion is currently failing.
