---
workflow_id: purchase-order-rfq-requesting-department-label
area: purchase-order
models: [purchase.order, purchase.request]
views: [purchase.order.form]
issue_ids: [43]
status: verified
last_verified: 2026-11-06
---

# RFQ requesting-department label

## Purpose

Verify that the department field on an RFQ/PO form uses the requested visible
label `Phòng ban yêu cầu mua`, consistent with its requesting-department
meaning on purchase requests.

## Preconditions and fixtures

- Vietnamese UI on local database `barett-dev-3`.
- An existing RFQ/PO linked to a purchase request and carrying a non-empty
  `department_id`.
- The check is read-only; no disposable fixture is normally needed.

## Reusable UI steps

1. Log in through `/odoo` with the approved local test account.
2. Open `/odoo/purchase` and locate the target RFQ/PO by its visible reference.
3. Open the target record and verify its page title/reference.
4. In the supplier/header group, read the visible label immediately before the
   linked department value.
5. Compare the label exactly with `Phòng ban yêu cầu mua`; do not infer a pass
   from the department value or the linked purchase request.

## Expected visible states

- The field label is exactly `Phòng ban yêu cầu mua`.
- The existing department value remains visible beside/below that label.

## Side effects and cleanup

Read-only navigation only. No cleanup is required.

## Source/runtime references

- `addons/vdx/barett_purchase_request/models/purchase_order.py`
  (`purchase.order.department_id`).
- `addons/vdx/barett_purchase_request/views/purchase_order_views.xml`
  (purchase-order form insertion).
- `addons/vdx/barett_purchase_request/models/purchase_request.py`
  (`purchase.request.department_id`, the requesting-department counterpart).

## Known pitfalls

- `Phòng ban` is not equivalent to `Phòng ban yêu cầu mua` for this criterion.
- A correct supplier display or hidden standalone vendor-code field does not
  provide evidence for this separate label criterion.
- When source says `Department` and runtime renders `Phòng ban`, the runtime is
  consistent with that source; investigate the field string before diagnosing
  stale registry or translation cache.
