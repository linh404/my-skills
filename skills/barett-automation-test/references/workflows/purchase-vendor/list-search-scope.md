---
workflow_id: purchase-vendor-list-search-scope
area: purchase-vendor
models: [res.partner]
views: [res.partner.tree, res.partner.search]
issue_ids: []
status: verified
last_verified: 2026-11-06
---

# Purchase vendor list/search scope

## Purpose

Check that supplier list and search UI contains supplier-specific customizations while customer-only customizations remain limited to the customer view.

## Preconditions and fixtures

- Local Barett database with Purchase, Account Follow-up, and vendor menu access.
- Use existing partners and vendor types; no fixture is required.

## Reusable UI steps

1. Open `/odoo/vendors?view_type=list` in the local database.
2. Inspect list headers for customer-only columns such as Customer Code, Customer Type, and Customer Rank.
3. Open the search menu and inspect filters and group shortcuts; verify customer-only shortcuts and `Overdue Customer Invoices` are absent, while vendor type remains available.
4. Select the vendor grouping shortcut and confirm the records group under their vendor type values.
5. Open `Thêm bộ lọc tùy chỉnh`, choose the vendor type field, and enter a prefix such as `NCC`; verify current vendor type values appear. Cancel without applying if only inspecting.
6. Open `/odoo/customers?view_type=list` and confirm customer-specific fields remain available there.

## Expected visible states

- Vendor list has supplier-specific fields and no customer-only columns, filters, or group shortcuts.
- Customer list retains customer-specific fields and shortcuts.
- Vendor type filtering and grouping use `vendor_type_id`; new vendor types are discoverable without adding fixed domestic/foreign filters.

## Side effects and cleanup

Navigation and temporary search/group states only. Cancel an exploratory custom-filter dialog without applying. Do not create or edit records.

## Source/runtime references

- `addons/vdx/barett_sale/views/res_partner_views.xml` scopes customer list/search customizations.
- `addons/vdx/barett_purchase/views/res_partner_views.xml` scopes vendor customizations and defines `vendor_type_id` search/group support.
- The purchase follow-up search extension directly inherits `account_followup.customer_statements_search_view` to hide `filter_with_overdue_invoices` for supplier mode. `barett_purchase` depends on `account_followup`.

## Known pitfalls

- Purchase `Cấu hình` can open vendor type configuration, not the vendor partner list. Use the vendor list route or `Đơn hàng` > `Nhà cung cấp`.
- The filter field picker may show two identical Vietnamese `Nhà cung cấp` labels; confirm the vendor type entry by its autocomplete values.
- Confirm the list URL includes `?view_type=list`; vendor/customer menus may default to kanban.
