---
name: barett-retest-dev
description: Retest Barett ERP issues from the Google Sheet issue list on the dev site (https://dev-barett.vdx.vn) by clicking through the web UI with Playwright, per role. Use when the user asks to test/retest issues (e.g. "test lại các issue mua hàng khẩn cấp/cao đã hoàn thành trên site dev").
---

# Retest issue trên site dev Barett

Retest the issues bằng **thao tác trên giao diện web** như tester thật. Không gọi RPC/`/web/dataset/call_kw`, kể cả để đọc dữ liệu; mọi setup dữ liệu cũng làm qua UI.

## 1. Lấy danh sách issue

Sheet ID và tab lấy từ biến môi trường `BARETT_ISSUE_SHEET_ID` và `BARETT_ISSUE_SHEET_GID` (hỏi user nếu chưa đặt). Tải CSV (sheet public) vào scratchpad:

```bash
curl -sL -o <scratchpad>/sheet/issues.csv \
  "https://docs.google.com/spreadsheets/d/${BARETT_ISSUE_SHEET_ID}/export?format=csv&gid=${BARETT_ISSUE_SHEET_GID}"
```

Cột (index 0-based): 0 STT · 2 Module · 3 Model · 4 Màn hình · 5 Nội dung lỗi · 8 PIC Test · 9 Ngày ghi nhận · 10 Mức độ ưu tiên (`Khẩn cấp!`, `Cao`, `Trung bình`, `Thấp`) · 11 PIC Dev · 13 Trạng thái task (`Hoàn thành`, `Đã fix`, `Đang thực hiện`, rỗng) · 14 Ngày test · 15 Ghi chú (kết quả retest trước). Lọc bằng `python3 -I` + `csv`; module có thể có khoảng trắng thừa (`strip()`). Một số dòng không có STT — gọi theo số dòng sheet.

Đọc cột Ghi chú: nó chứa kết quả retest trước và các lưu ý còn mở — retest đúng các điểm đó. Đọc code liên quan trong `addons/vdx/` để biết hành vi mong đợi (tên nút, điều kiện khóa, thông báo).

## 2. Kết nối trình duyệt

- **Admin**: dùng Chrome hằng ngày của user (đã đăng nhập dev site; mật khẩu admin trong test.md từng bị từ chối). Remote debugging bật qua `chrome://inspect/#remote-debugging`; endpoint nằm ở `~/.config/google-chrome/DevToolsActivePort` (đổi mỗi lần mở lại Chrome). **Không** tự mở Chrome mới bằng `--remote-debugging-port` — user muốn dùng đúng profile đang dùng.
- Chạy `~/.claude/skills/barett-retest-dev/setup.sh` (cần `BARETT_CC_PASSWORD` để đăng nhập các tài khoản `cc_*`) → sinh `~/.cache/playwright-mcp-output/cc/prelude.js` với endpoint hiện tại. File chạy bằng `mcp__playwright__browser_run_code_unsafe` phải nằm trong `~/.cache/playwright-mcp-output` hoặc repo (không dùng scratchpad `/tmp`, không ghi vào repo).
- Nạp helper: `browser_run_code_unsafe` với `filename: /home/linh/.cache/playwright-mcp-output/cc/prelude.js` → trả `"prelude ok"`.
- **Giữ kết nối**: prelude lưu kết nối CDP ở `page.context().__cdp`, tab test ở `__tab`, helper ở `__h`, phiên vai trò ở `__roles`. `globalThis` và `require` KHÔNG dùng được. Mọi bước sau viết code inline ngắn, mở đầu:
  ```js
  async (page) => { const h = page.context().__h; if (!h) return 'NEED_PRELUDE'; ... }
  ```
  Gặp `NEED_PRELUDE` (context MCP bị reset) → chạy lại prelude. Không bao giờ `browser.close()` kết nối CDP.
- Admin thao tác trong **tab riêng** (`h.t`), không điều hướng các tab đang mở của user.
- **Phiên theo vai trò** (`h.as(login)`) chạy trong Chromium riêng của Playwright MCP (context riêng mỗi user), không mở cửa sổ ẩn danh trên Chrome của user (user sẽ đóng chúng). Trang có thể bị đóng giữa chừng → `h.as` tự mở lại trang trong context cũ.

Helper chính trong prelude: `go(p, path)` (tự retry màn "Bạn đang offline"), `status`, `headerButtons`, `alertBtns` (nút duyệt trên banner tier validation), `cpButtons`, `gearItems` (menu Tác vụ), `val`, `readonly`, `invalid`, `pick(p, field, text, scope)` (chọn many2one/many2many), `save`, `discard`, `click(p, text)`, `errors` (notification + modal), `errDetail`, `closeDialogs`, `prNew(p, productText, qty)`, `prView(login, id)`.

## 3. Dữ liệu test

Tạo dữ liệu riêng tiền tố `[CC]`, không sửa tài khoản/dữ liệu QA khác (`qa_*`, `quynhntd`...). Dùng lại nếu đã có (dev site được thêm/sửa/xóa tự do).

| Vai trò | Login (mật khẩu chung: biến môi trường `BARETT_CC_PASSWORD`) | Nhân viên / phòng ban | Nhân bản quyền từ |
|---|---|---|---|
| NV lập phiếu | `cc_nv` | [CC] Phòng SX | `qa_nvsx` |
| TBP | `cc_tbp` | trưởng [CC] Phòng SX | `qa_tbpsx` |
| GĐ khối (phòng cha) | `cc_gd` | trưởng [CC] Khối SX | `qa_tbpsx` |
| NV tổ không có TBP | `cc_nv2` | [CC] Tổ SX1 (con của Phòng SX) | `qa_nvsx` |
| NV Mua hàng | `cc_nvmh` | — | `qa_nvmh` |
| Duyệt cấp 1 / 2 | `cc_duyet1` / `cc_duyet2` | — | `qa_duyet1/2` |

Cấu hình duyệt: `[CC] Duyệt chủ trương SX` và `[CC] Duyệt giá SX` cho [CC] Khối SX + [CC] Phòng SX, cấp 1 `cc_duyet1`, cấp 2 `cc_duyet2`, ngưỡng 0, `≥`, OR.

Cách tạo qua UI và bẫy đã gặp:
- User: Cài đặt › Người dùng › mở user mẫu › Tác vụ › **Nhân bản** › sửa login › Lưu. Tên khi nhân bản KHÔNG lưu — mở lại user, sửa tên, lưu riêng. Mật khẩu: Tác vụ › Thay đổi Mật khẩu › **bấm vào ô** "Mật khẩu mới" rồi mới gõ.
- Nhân bản user không tạo nhân viên → tạo nhân viên ở Nhân viên › Mới, chọn phòng ban, tab **Cài đặt** › Người dùng liên quan.
- Thứ tự: phòng ban (chưa có trưởng) → nhân viên → gán trưởng phòng.
- Many2one: **không bao giờ bấm "Tạo …"/"Tạo và chỉnh sửa…"** (mở dialog mời user mới / tạo bản ghi rác); `h.pick` đã loại các mục này.
- Lỗi validate khi rời form hiện dialog footer "Ở đây / Huỷ bỏ thay đổi" → `closeDialogs` bấm "Ở đây" rồi `discard`.
- Đường dẫn hay dùng: PR `/odoo/action-529/<id>` (`/new`), cấu hình duyệt `/odoo/action-835`, phòng ban `/odoo/action-hr.hr_department_tree_action`, user `/odoo/action-base.action_res_users`, nhân viên `/odoo/employees`. Action id có thể đổi sau upgrade — nếu 404 thì đi qua menu.

## 4. Thực hiện test

- Mỗi issue: xác định vai trò cần (người lập, TBP, NV Mua hàng, người duyệt đúng/sai cấp, admin) và kiểm tra từng ý trong Nội dung lỗi + lưu ý ở Ghi chú. Kiểm tra cả "phải có" lẫn "không được có" (nút ẩn, form khóa, chặn lưu/xóa, menu Tác vụ không còn Xóa/Nhân bản).
- Ghi bằng chứng: mã phiếu (PR/…, PO/…), vai trò, thao tác, thông báo hiển thị nguyên văn.
- Ghi chú bản dịch: thông báo/nhãn còn tiếng Anh thì nêu ra (không tính là fail nghiệp vụ nếu BA không yêu cầu).
- Dữ liệu cũ vi phạm ràng buộc mới (ràng buộc chỉ chạy khi ghi) → báo riêng.
- Không sửa sheet trừ khi user yêu cầu. Chỉ báo kết quả.
- Báo tiến độ ngắn gọn khi user hỏi; mạng dev chập chờn ("Bạn đang offline") là bình thường — retry, không kết luận lỗi khi chưa tái hiện được.

## 5. Báo cáo

Bảng: `STT | Mức | Kết quả (✅ Đạt / ❌ Không đạt / ⚠️ Đạt một phần / ⏳ Chưa test) | Ghi chú (vai trò, mã phiếu, thông báo)`. Sau bảng: các điểm còn mở, dữ liệu test đã tạo, phần chưa test được và lý do.
