# Guide outline (Vietnamese user guide, modeled on "Hướng dẫn thao tác: Tạm ứng – Hoàn ứng")

Write the Markdown in the users' UI language (Vietnamese for VDX projects). Keep sentences short,
name every button/field/menu exactly as the UI shows it, in bold when it is something to click.

```markdown
---
title: "Hướng dẫn thao tác: <Chức năng> (<mã FS nếu có>)"
lang: vi-VN
---

<1 đoạn: phạm vi (module), tên nút/menu theo giao diện tiếng Việt, ảnh chụp trên DB <db> ngày <dd/mm/yyyy>;
khung đỏ đánh số là chỗ cần thao tác hoặc cần xem. Nguồn: <FS + phiên bản> nếu có.>

# 1. Vai trò và menu
| Vai trò | Nhóm Odoo | Làm gì |        <- from security groups / tier definitions actually in the DB
| Menu | Dành cho |                     <- full path App > Menu > Submenu
# 2. Cấu hình / điều kiện trước khi dùng  <- only what the flow really needs; numbered, in order
# 3. Luồng tổng quát                      <- fenced text diagram: states and buttons with arrows
# 4..N. One section per document/step of the chosen flow
## N.1 Mở chức năng                       <- menu path + screenshot with "Mới" marked
## N.2 Lập ...                            <- field table | Trường | Ghi chú | then screenshot
## N.x <each button>                      <- what it checks, what it changes, screenshot
# Hủy, xóa, nhân bản                      <- matrix by document and state
# Thông báo chặn thường gặp               <- | Thông báo | Cách xử lý |, text copied from vi.po / UI
# Giới hạn hiện tại                        <- bugs and gaps seen while running the flow
```

Image syntax: `![](img/03-year-form.png){width=100%}` (one screenshot per step, 1440x900).

Rules:
- Every statement must come from what was observed in the UI run or read in the code/FS. No guesses.
- Number the red marks in click order and refer to them in the text when helpful.
- Error messages: use the exact translated text; if the UI shows English, quote it and add "(chưa dịch)".
- Put anything odd you saw (untranslated labels, dead-end states, wrong sorting) in "Giới hạn hiện tại".
