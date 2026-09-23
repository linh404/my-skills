# Gate 1 — drawing overview shown to the user

Before editing a `.mdj`, present a plan in plain language. The purpose is to let the user confirm the intended picture, not to expose raw JSON IDs.

Use this structure:

```markdown
## Gate 1 — Tổng quan sơ đồ sắp vẽ

**Diagram:** <name and whether it is new or being edited>

**Mục đích:** <one sentence describing what the diagram explains>

**Khung hệ thống / subject:**
- <boundary 1 and its scope>

**Actors:**
- <actor> — <what it does>

**Nhóm use case:**
- <group or subject>: <use cases>

**Quan hệ chính:**
- <actor> → <use case>
- <include/extend/generalization only when explicitly required>

**Bố cục dự kiến:**
- <where the boundary, use cases, and actors will be placed>
- <how connectors will be routed>
- **Tiêu đề trên canvas:** Không tạo dòng tiêu đề `UMLTextView` riêng phía trên sơ đồ; chỉ dùng tên diagram và nhãn của subject/boundary, trừ khi user yêu cầu khác.

**Phạm vi thay đổi:**
- <files/diagrams to change>
- <what will remain untouched>

**Điểm cần xác nhận:**
- <ambiguity, if any; otherwise “Không có”.>

Chờ user duyệt Gate 1 trước khi ghi/chỉnh file `.mdj`.
```

Keep the overview short enough to review quickly. If the request is ambiguous, state the assumption explicitly instead of silently inventing actors or relationships. Approval applies only to the described diagram scope; a materially different layout or semantic model requires another Gate 1 confirmation.

The Gate 1 overview is a planning message shown to the user; it is not a request to add a matching title text object to the `.mdj` canvas. The default drawing must omit a redundant top title such as “Use Case tổng quát — ...”.
