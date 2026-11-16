---
workflow_id: product-category-issue-60-category-type-options
area: product-category
models: [product.category]
views: [product.category.list, product.category.form]
issue_ids: [60]
status: verified
last_verified: 2026-11-06
---

# Product-category type options

## Purpose

Verify every visible value of the product-category type selection against the
Issue 60 FS, including the `Bao bì đóng gói` option and exact Vietnamese text.

## Preconditions and fixtures

- Vietnamese UI on local database `barett-dev-3`.
- The check uses a new unsaved form and must end with `Huỷ bỏ mọi thay đổi`.
- No fixture should be retained.

## Reusable UI steps

1. Log in through `/web/login?db=barett-dev-3` with the approved local test
   account.
2. Open `/odoo/action-196` and verify the `Danh mục sản phẩm` list.
3. Click `Mới` to open `/odoo/action-196/new`.
4. Read every option rendered by the category-type combobox, currently labeled
   `Phân loại sản phẩm` in the Vietnamese runtime.
5. Compare every label exactly with the FS list; punctuation and conjunctions
   are part of the expected value.
6. Click `Huỷ bỏ mọi thay đổi` and verify return to `/odoo/action-196`.

## Expected visible states

- The option list is: `NVL`, `Bán thành phẩm`, `Thành phẩm`, `CCDC`,
  `Thiết bị thị trường`, `Vỏ keg`, `Bao bì đóng gói`,
  `Phế liệu/Sản phẩm phụ/Phục hồi`, `Khác`.
- The new form is discarded without saving a product category.

## Side effects and cleanup

The form is cancelled without saving. No fixture or database change is
expected.

## Source/runtime references

- `addons/vdx/barett_product/models/product_category.py`
  (`product.category.category_type`).
- `addons/vdx/barett_product/views/product_category_views.xml` (form field).
- `addons/vdx/barett_product/i18n/vi.po` (Vietnamese selection labels).

## Known pitfalls

- Source changes do not prove the running registry or translated selection
  metadata is current; read the rendered combobox.
- `Phế liệu & Sản phẩm phụ Phục hồi` is not an exact match for the FS value
  `Phế liệu/Sản phẩm phụ/Phục hồi`.
