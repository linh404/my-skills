---
workflow_id: purchase-request-header-product-line-layout
area: purchase-request
models: [purchase.request, purchase.request.line]
views: [purchase.request.form]
issue_ids: []
status: verified
last_verified: 2026-11-05
---

# Purchase request header and product line layout

## Purpose

Check the requested arrangement of header fields, the full-width Description field, and the Marketing Goods column before Product on a draft purchase request.

## Preconditions and fixtures

- Local Barett database `barett-dev-3` and an authenticated user who can open Purchase Requests.
- No fixture is needed. Use `/odoo/action-529/new` and do not save the blank form.
- Company (`company_id`) is rendered only for `base.group_multi_company`; with other users, verify its XML placement and record that runtime visibility was not tested.

## Reusable UI steps

1. Open `/odoo/action-529/new` and verify the page is the new `Yêu cầu mua hàng` form.
2. Read the left header group. Expected order: `Yêu cầu bởi`, `Phòng Ban`, `Người phê duyệt`, `Công ty`, `Ngày tạo`.
3. Read the right header group. Expected order: `Nhóm mua hàng`, `Loại lấy hàng`, `Nhà cung cấp Tối thiểu/Tối đa`, `Loại nguồn gốc`, `Tài liệu nguồn`.
4. Verify `Mô tả` spans both header columns. If needed, inspect the `description` widget and compare its width with the full header group.
5. Read the product table headers. Expected: `Hàng MKT` immediately before `Sản phẩm`.
6. Leave the empty form without saving by navigating back to `/odoo/action-529`.

## Expected visible states

- Header fields match the two ordered groups above.
- `Mô tả` occupies the full two-column width.
- Product table shows `Hàng MKT` before `Sản phẩm`.
- If Company is absent, check whether the test user belongs to `base.group_multi_company`; do not infer that the field is missing from source.

## Side effects and cleanup

- No fixture or cleanup is required. Never save the empty form during this check.

## Source/runtime references

- `addons/vdx/barett_purchase_request/views/purchase_request_views.xml:50-68` — header groups, Company visibility, Description span.
- `addons/vdx/barett_purchase_request/views/purchase_request_views.xml:88-90` — `is_marketing` with label `Hàng MKT` before `product_id`.
- Last verified in local `barett-dev-3` at `/odoo/action-529/new`; the corresponding run record contains the runtime evidence.

## Known pitfalls

- Company is restricted to `base.group_multi_company` and may not appear for a single-company user.
- `Hàng MKT` may be visually clipped in a narrow table column; use the accessible column header text to verify its full label.
- The cancel button may time out on an untouched blank form. Navigating back to the request list safely abandons the unsaved form.
