---
workflow_id: purchase-request-pr-done-permission
area: purchase-request
models: [purchase.request, purchase.request.cancel.wizard, res.users, hr.employee]
views: [purchase.request.form, purchase.request.done.wizard.form]
issue_ids: [PR00143, PR00144]
status: verified
last_verified: 2026-11-05
---

# PR completion (Done) by role

## Purpose

Verify who can complete an `In progress` purchase request: a purchasing user
(`Mua hàng / Người dùng`) can; a requester outside purchasing cannot.

## Preconditions and fixtures

- Two disposable users created by admin with a run-ID marker:
  - `<RUN> Buyer`: all access-right selects empty except `Mua hàng? = Người dùng`.
  - `<RUN> Requester`: all access-right selects empty (Internal User only).
- The requester needs an employee in a department whose manager user can
  approve in the UI (e.g. `Issue34 QA`, manager admin).
- A PR requested by the requester, approved, with an RFQ for part of the
  quantity so it is `In progress` and still has quantity to buy.

## Steps

1. Admin: `/odoo/users/new`; fill `Tên`, `Địa chỉ Email?` (login); for each
   access-right select, focus it and press `ArrowUp` until the empty option;
   set the needed role; `Lưu thủ công`.
2. Admin: gear menu → `Thay đổi Mật khẩu` → click the empty password cell,
   type the QA password, `Thay đổi Mật khẩu`.
3. Admin (requester only): user form → `Tạo nhân viên`; on the employee form
   type the department name in `Phòng ban` and **click** the existing
   suggestion (do not press Enter); `Lưu thủ công`.
4. Admin: `/odoo/action-529/new`; set `Yêu cầu bởi`, `Mô tả` with the marker;
   `Thêm một dòng` → click the product field, type, click the suggestion; set
   quantity; `Lưu thủ công`.
5. Admin: `Gửi duyệt` → banner `Bản ghi này cần được xác thực.` → `Xác thực`
   → statusbar `Đã duyệt`.
6. Admin: `Create Quotation` → vendor, reduce `Số lượng cần mua` below the
   request quantity → `Create Quotation`. PR becomes `In progress`.
7. Logout (`/web/session/logout`) → `Use another user` → log in as the
   requester; open the PR. Expected: header has no `Done` button.
8. Logout → `Use another user` → log in as the buyer; open the PR. Expected
   header buttons `Create Quotation`, `Done`.
9. Click `Done` → dialog `Complete Purchase Request`; fill `Completion Reason`;
   `Complete`. Expected: no error, statusbar `Done`, reason shown on the form.

## Retention and side effects

Fixtures are retained. The completed PR keeps its draft RFQ.

## References

- `button_done` guard: `addons/vdx/barett_purchase_request/models/purchase_request.py`.
- Purchasing rules: `addons/vdx/barett_purchase_request/security/security.xml`.
- Unit test for the direct-call guard: `test_08_only_purchasing_completes`.

## Pitfalls

- New users get the English UI: the button is `Done`, the wizard button `Complete`.
- Pressing `Enter` in a many2one autocomplete can pick `Tạo "<text>"` and
  create a record; click the suggestion instead.
- The server-side direct-call guard has no UI path; do not use RPC as
  acceptance evidence.
