---
workflow_id: product-category-unique-name-per-parent
area: product-category
models: [product.category]
views: [product.category.form]
issue_ids: []
status: verified
last_verified: 2026-11-06
---

# Product category unique name per parent

## Purpose

Verify that a product category cannot share its exact name with another
category under the same parent (root categories compared together), while the
same name under a different parent is allowed.

## Preconditions and fixtures

- Admin user, `barett-dev-3`, `barett_purchase` updated with
  `models/product_category.py`.
- Create fixtures with a run marker `[QA-<run>]`: root `DM Cha A`, root
  `DM Cha B`, child `DM Thành phẩm` under each.

## Reusable UI steps

1. Open `/odoo/action-product.product_category_action_form/new` (menu Mua
   hàng / Tồn kho / Bán hàng / Kế toán → Cấu hình → Danh mục sản phẩm).
2. Fill `Danh mục` (`div[name="name"] input`); optionally set `Danh mục chính`
   (`div[name="parent_id"] input`, type then click the autocomplete item —
   do not press Enter, it can quick-create).
3. Click `Lưu thủ công` (`button.o_form_button_save`).
4. Duplicate case: same name/parent → dialog `Ôi chao!`; click
   `Huỷ bỏ thay đổi`.
5. Move case: open the child under B, set `Danh mục chính` to A, save → error.
6. Copy case: open a child, cog menu → `Nhân bản` → dialog `Lỗi xác nhận`.

## Expected visible states

- Allowed saves land on `/odoo/action-<id>/<record id>`.
- Blocked saves show `Danh mục sản phẩm cùng tên đã tồn tại trong cùng danh
  mục cha.` (vi_VN) / `A product category with this name already exists under
  the same parent category.` (source).

## Side effects and cleanup

QA categories are retained; no cleanup.

## Source/runtime references

- `addons/vdx/barett_purchase/models/product_category.py`
- `addons/vdx/barett_purchase/i18n/vi.po`
- Unit tests: `addons/vdx/barett_purchase/tests/test_product_category.py`

## Known pitfalls

- After a blocked save the form stays dirty; navigating away triggers a
  `beforeunload` dialog that stalls Playwright scripts. Discard first.
- The Vietnamese message requires the runtime to have loaded the updated
  `vi.po` (restart/update after the i18n change).
