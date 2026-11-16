---
workflow_id: purchase-order-issue-41-positive-line-validation
area: purchase-order
models: [purchase.order, purchase.order.line, purchase.request]
views: [purchase.order.form, purchase.request.form]
issue_ids: [41]
status: verified
last_verified: 2026-11-04
---

# Positive-line validation before approval

## Purpose

Verify that ordinary purchase lines require quantity and unit price greater
than zero before Policy Approval and Price Approval, while promotion lines
with a zero unit price are excluded from the guard.

## Preconditions and fixtures

- Use the local `barett-dev-3` database and a fresh isolated Chrome DevTools
  MCP profile.
- Read the requested IssueList row by matching the issue number in column A.
- Reuse an existing ordinary zero-price line when available. If a promotion
  line or zero-quantity linked RFQ is missing, create a disposable QA fixture
  through the Odoo UI; never write fixtures with RPC or SQL.
- For the promotion branch, create and activate a promotion with a purchase
  condition and a fixed gift benefit, create an RFQ with a valid ordinary line,
  then apply `Tính KM`.

## Reusable UI steps

1. Open the purchase order form and verify the visible approval status fields.
2. For an ordinary line with unit price `0`, click `Gửi Phê duyệt Chính sách`
   or, after Policy Approval is approved, click `Gửi Phê duyệt Giá`.
3. Verify the modal text `Product lines must have a unit price and quantity
   greater than 0.` and confirm the approval state is unchanged.
4. For the quantity branch, edit the ordinary line to quantity `0` and unit
   price `100`, save, submit Policy Approval, and verify the same error.
5. For the promotion branch, keep the ordinary line positive, apply `Tính KM`,
   verify the generated promotion line has price `0` and is marked as a
   promotion line, submit Policy Approval, approve it from Approval History,
   and submit Price Approval.

## Expected visible states

- Invalid ordinary lines stay in their pre-test approval state.
- A valid ordinary line plus a zero-price promotion line can submit both
  approval actions.
- Policy Approval and Price Approval show `Chờ xử lý` after successful
  submission; Policy Approval can be approved from Approval History.

## Side effects and cleanup

Record every created QA promotion and purchase order, including URLs and
before/after states. Leave fixtures in the local database when cleanup could
remove related approval or promotion data; report the exact remaining states.

## Source/runtime references

- `addons/vdx/barett_purchase_request/models/purchase_order.py:182-220`
- `http://localhost:8069/odoo`
- `/home/linh/odoo-versions/config/barret.conf`

## Known pitfalls

- The first zero-quantity fixture may also have unit price zero, which does
  not isolate the quantity branch. Change its price to a positive value and
  rerun the approval action.
- Closing an activity card does not approve an approval review; use the
  `Approval History` tab and its visible `Phê duyệt` action.
