# Cấu hình Weblate Settings

## Mục lục

1. Phạm vi
2. Nguyên tắc cấu hình
3. Mapping Workspace, Project và Component
4. Tạo Project
5. Tạo Component cho module Odoo
6. Settings → Version control
7. Settings → Files
8. Bật Add-on đồng bộ POT/PO
9. Language và translation workflow
10. Translation Memory
11. Machine Translation tùy chọn
12. Kiểm tra setting sau khi cấu hình
13. Lỗi thường gặp
14. Tài liệu tham chiếu

## 1. Phạm vi

Tài liệu này mô tả các setting cần cấu hình trong giao diện Weblate sau khi instance Weblate và kết nối GitLab đã sẵn sàng.

Phạm vi gồm:

- Workspace, Project và Component.
- Version control của component.
- POT template và PO file mask.
- Add-on đồng bộ POT/PO ở cấp project và component.
- Ngôn ngữ và quyền chỉnh sửa source string.
- Translation Memory và machine-translation suggestion tùy chọn.
- Kiểm tra riêng các setting trên giao diện Weblate.

Không mô tả:

- Docker, database, tunnel và secret runtime: `weblate-self-hosted-deployment.md`.
- GitLab token, protected branch, CI Job Token và webhook: `weblate-gitlab-integration.md`.
- Cách export POT bằng Odoo CI: tài liệu CI job hiện có.

## 2. Nguyên tắc cấu hình

Weblate chỉ quản lý bản dịch PO. POT do CI sinh và là template đầu vào của component.

| Đối tượng | Owner |
|---|---|
| Source code và source string | Developer |
| POT | Odoo CI |
| PO `msgstr` | Weblate và BA/Translator |
| Translation approval và merge | GitLab Maintainer/CTO |

Vì POT thuộc quyền CI:

- Không bật chỉnh sửa source string trực tiếp trên Weblate.
- Không để Weblate push translation trực tiếp vào `dev`.
- Không bật một job khác ghi đè `msgstr` trong PO.
- Không thêm Weblate review gate riêng.

Với project có nhiều component Odoo, nên cài add-on đồng bộ ở cấp project để component tương thích được kế thừa cùng một workflow. `File mask` và `Template for new translations` không phải setting mặc định cấp project; chúng vẫn phải khai báo riêng cho từng component vì mỗi module có đường dẫn POT/PO khác nhau.

## 3. Mapping Workspace, Project và Component

| Scope Weblate | Mapping trong QMS |
|---|---|
| Workspace | Không gian quản lý các project dịch liên quan tới Odoo/QMS |
| Project | `Odoo QMS`, đại diện cho hệ thống/repository Odoo QMS |
| Component | Một module Odoo, ví dụ `g10_access_management` |

Mỗi module có thể được tạo thành một component riêng để có:

- POT template riêng.
- File mask PO riêng.
- Ngôn ngữ và trạng thái dịch riêng.
- Lịch sử đồng bộ riêng.

Nếu nhiều component dùng chung một repository, phải xác định rõ component root và tránh để các component ghi đè cùng một file hoặc cùng một branch tạm.

## 4. Tạo Project

Tạo project:

| Trường | Giá trị dự kiến |
|---|---|
| Name | `Odoo QMS` |
| Slug | Theo slug Weblate sinh tự động |
| Source language | `English` hoặc ngôn ngữ nguồn thực tế của repository |
| Target language | `Vietnamese` (`vi`) |

Các policy access, visibility và user assignment cấu hình theo quyền nội bộ của project. Không mở project công khai nếu repository hoặc nội dung dịch là riêng tư.

## 5. Tạo Component cho module Odoo

Ví dụ component đầu tiên:

| Trường | Giá trị |
|---|---|
| Name | `g10_access_management` |
| Project | `Odoo QMS` |
| Source language | Ngôn ngữ source của module |
| Target language | `Vietnamese` |
| Repository branch | `dev` |

Trước khi lưu, kiểm tra layout thật của repository. Không tự động thêm tiền tố module vào path nếu component root đã là thư mục module.

## 6. Settings → Version control

Trong `Project → Component → Settings → Version control`, cấu hình:

| Field | Giá trị bắt buộc |
|---|---|
| Version control system | `GitLab merge request` |
| Source code repository | URL repository có quyền đọc |
| Repository branch | `dev` |
| Repository push URL | URL cùng repository có quyền ghi branch dịch |
| Push branch | `weblate-translations` |
| Push on commit | Tắt khi kiểm thử có kiểm soát; bật khi vận hành tự động |
| Lock on error | Bật |

Điều kiện:

- `Push branch` phải khác `Repository branch`.
- Không để trống `Push branch`; để trống có thể chuyển sang behavior fork-based.
- Backend phải là `GitLab merge request`, không chỉ là Git push thông thường.
- API credential và Git credential đã được cấu hình theo `weblate-gitlab-integration.md`.

`Push on commit` quyết định thời điểm Weblate đẩy commit. Nó không thay đổi branch policy: mọi PO vẫn phải đi qua `weblate-translations` và MR vào `dev`.

## 7. Settings → Files

### 7.1. Template for new translations

Chọn file POT do CI sinh cho chính module/component đó.

Nếu component root là thư mục module:

```text
i18n/g10_access_management.pot
```

Nếu component root là repository root:

```text
g10_access_management/i18n/g10_access_management.pot
```

Không chọn PO làm template khi workflow đã thống nhất CI sở hữu POT.

### 7.2. File mask

File mask phải khớp các PO của component. Ví dụ khi component root là module:

```text
i18n/*.po
```

Nếu component root là repository root:

```text
g10_access_management/i18n/*.po
```

Chọn language code style khớp filename đang tồn tại, ví dụ `vi.po`, `vi_VN.po` hoặc pattern thực tế của repository.

### 7.3. Quyền chỉnh sửa source

- Tắt `Edit base file` hoặc setting tương đương.
- Không cho người dịch sửa `msgid` từ Weblate.
- Không cấu hình Weblate tạo lại POT.

### 7.4. Phạm vi project và component

Trong `Project → Operations → Add-ons`, cài:

```text
Update PO files to match POT (msgmerge)
```

Đây là project-wide add-on. Component tương thích hiện có và component tương thích được tạo thêm trong project sẽ kế thừa add-on; trên trang add-on của component phải hiển thị trạng thái `Inherited from <project>`. Add-on chạy sau `Repository post-update`, đọc POT theo `Template for new translations` và cập nhật các PO khớp `File mask`.

Không đặt một đường dẫn `File mask` hoặc `Template for new translations` dùng chung cho toàn project. Mỗi component vẫn cấu hình theo module, ví dụ:

```text
File mask: g10_direct_print/i18n/*.po
Template: g10_direct_print/i18n/g10_direct_print.pot
```

Glossary và component không dùng gettext PO có thể được Weblate đánh dấu không tương thích với add-on này.

## 8. Bật Add-on đồng bộ POT/PO

### 8.1. Cấu hình khuyến nghị ở cấp project

Trong `Project → Operations → Add-ons`, bật:

`Update PO files to match POT (msgmerge)`

Không cài thêm cùng add-on ở cấp component nếu component đã kế thừa project-wide add-on; tránh chạy trùng. Chỉ dùng component-level khi cần một ngoại lệ riêng.

### 8.2. Cơ chế xử lý

Add-on này có nhiệm vụ:

1. Đọc POT mới sau khi repository được cập nhật.
2. Thêm source unit mới vào PO.
3. Giữ lại bản dịch của source unit còn tương ứng.
4. Đánh dấu hoặc xử lý source unit đã thay đổi theo quy tắc msgmerge.
5. Loại bỏ hoặc đánh dấu entry không còn trong POT theo cấu hình Weblate.

Việc chọn POT trong `Template for new translations` chỉ xác định template. Nó không tự động chạy machine translation và không tự tạo GitLab MR.

## 9. Language và translation workflow

Trong component:

1. Thêm target language `Vietnamese` (`vi`) nếu chưa có.
2. Kiểm tra PO được tạo đúng filename và header.
3. Giữ trạng thái source language theo ngôn ngữ thực tế của POT.
4. Không bật bắt buộc review riêng trên Weblate.
5. Để BA/Translator xử lý bản dịch và các cảnh báo định dạng.

Các nội dung cần kiểm tra trong Weblate:

- Placeholder Odoo.
- HTML/XML tag.
- Plural form.
- Dấu câu và khoảng trắng.
- Fuzzy hoặc `Needs editing` unit.
- Thuật ngữ nghiệp vụ QMS.

## 10. Translation Memory

Translation Memory là nguồn suggestion hỗ trợ người dịch, không thay thế quyết định của BA/Translator.

Cấu hình khuyến nghị:

- Bật exact-match/built-in suggestion nếu Weblate cung cấp.
- Cho phép sử dụng Translation Memory dùng chung ở phạm vi phù hợp.
- Ưu tiên suggestion có độ tương đồng cao.
- Không tự động ghi đè bản dịch đã được xác nhận chỉ vì có suggestion mới.

Weblate review không phải là gate riêng. Chất lượng nội dung được kiểm tra bởi BA/Translator và sau đó được review/merge trong GitLab MR.

## 11. Machine Translation tùy chọn

Machine translation chỉ tạo suggestion hoặc bản dịch nháp. Có thể vận hành Weblate hoàn chỉnh mà không bật provider bên ngoài.

Nếu dùng LibreTranslate self-host đã triển khai cùng Docker network:

`Administration → Automatic suggestions → LibreTranslate → Install`

Cấu hình:

| Field | Giá trị |
|---|---|
| Source language selection | Source language của component |
| API URL | `http://libretranslate:5000/` |
| API key | Để trống nếu service nội bộ không yêu cầu |

Sau khi cài provider:

1. Test một source unit nhỏ.
2. Kiểm tra placeholder, tag, plural và thuật ngữ.
3. Chỉ chạy `Operations → Batch automatic translation` sau khi test thành công.
4. Review kết quả trước khi commit PO.

Không coi machine translation là điều kiện của đồng bộ Git, webhook hoặc MR.

Baseline hiện tại có thêm service `ollama`, nhưng service này chưa tự động trở thành provider của Weblate. Chỉ ghi nhận Ollama là provider đang hoạt động sau khi đã cấu hình endpoint trong Weblate, test một source unit và kiểm tra đầu ra.

## 12. Kiểm tra setting sau khi cấu hình

### 12.1. Kiểm tra component

- Component không bị lock.
- Repository branch hiển thị là `dev`.
- Push branch hiển thị là `weblate-translations`.
- Backend hiển thị `GitLab merge request`.
- Template trỏ đúng POT.
- File mask bắt đúng PO hiện có.
- Add-on `Update PO files to match POT (msgmerge)` hiển thị là project-wide hoặc `Inherited from <project>` trên component.
- `Edit base file` đã tắt.

### 12.2. Kiểm tra đồng bộ POT/PO

Sau khi một POT mới được commit vào `dev` và Weblate fetch repository:

1. Component nhận được source unit mới.
2. PO tương ứng được cập nhật bởi msgmerge add-on.
3. PO cũ vẫn giữ các bản dịch còn hợp lệ.
4. Người dịch nhìn thấy unit mới trong giao diện.
5. Thay đổi PO được giữ ở Weblate cho tới khi commit/push.

Kiểm thử tạo MR và kiểm tra webhook thuộc tài liệu `weblate-gitlab-integration.md`, không lặp lại ở đây.

## 13. Lỗi thường gặp

### 13.1. Tạo component và chọn POT/PO

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Màn hình tạo component chỉ hiển thị PO, không thấy POT | Weblate đang discovery file dịch hoặc POT chưa có trên branch/repository đang quét | Tạo component từ repository/branch đúng; kiểm tra POT đã tồn tại trên `dev`; sau khi tạo component đặt POT tại `Settings → Files → Template for new translations` |
| Weblate không cho chọn file POT làm template | Component chưa dùng GNU gettext PO hoặc đường dẫn POT không nằm trong repository branch | Chọn đúng file format Gettext; kiểm tra path tương đối theo component root; không chọn file POT của module khác |
| Không thấy module `g10_access_management` | Repository URL, branch hoặc quyền đọc Git không đúng | Kiểm tra component đang đọc đúng repository QMS và branch `dev`; lỗi Git xử lý theo tài liệu GitLab integration |
| Component bắt sai file PO | File mask quá rộng hoặc component root sai | Nếu root là module dùng `i18n/*.po`; nếu root là repository dùng `g10_access_management/i18n/*.po` |

### 13.2. POT/PO synchronization

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| POT đã cập nhật nhưng PO không có source unit mới | Chưa bật `Update PO files to match POT (msgmerge)` hoặc add-on chưa chạy sau repository update | Bật add-on, chạy repository update/maintenance và xem log add-on |
| Component mới không có add-on msgmerge | Add-on được cài ở component khác hoặc project-wide add-on không tương thích với component mới | Kiểm tra `Project → Operations → Add-ons`; trên trang component phải thấy `Inherited from <project>`. Với gettext PO, đặt đúng File mask và POT template trước khi kiểm tra compatibility |
| Chọn đúng POT nhưng PO vẫn không đổi | Template chỉ xác định base file; nó không tự chạy msgmerge | Giữ đồng thời `Template for new translations` và `msgmerge` add-on |
| Weblate không thấy `_()` string mới | Source string chưa được CI export vào POT, component đọc nhầm branch/template hoặc repository chưa fetch commit | Kiểm tra POT commit và webhook trước; sau đó kiểm tra component settings. Exporter thuộc tài liệu CI job |
| String cũ bị đánh dấu fuzzy/Needs editing | `msgid` đã thay đổi và msgmerge không thể giữ bản dịch chắc chắn | BA/Translator kiểm tra lại bản dịch; không tự xóa cờ để che giấu thay đổi source |
| Entry cũ vẫn còn trong PO | msgmerge đánh dấu obsolete thay vì xóa ngay theo cấu hình | Kiểm tra `#~`/obsolete và file format parameters; chỉ bật remove obsolete theo policy dự án |
| PO không được tạo cho `vi` | Target language chưa được thêm hoặc language code style không khớp filename | Thêm `Vietnamese (vi)`, kiểm tra pattern `vi.po`/`vi_VN.po` theo repository |

### 13.3. Quyền chỉnh sửa và component state

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Người dịch sửa được source string | `Edit base file` đang bật hoặc component cho phép manage source strings | Tắt `Edit base file`; source string phải đến từ POT do CI quản lý |
| Weblate cho push trực tiếp vào `dev` | `Push branch` để trống hoặc cấu hình nhầm backend/branch | Đặt `Repository branch=dev`, `Push branch=weblate-translations`, backend `GitLab merge request` |
| Component bị khóa | `Lock on error` khóa component sau lỗi Git/repository update | Đọc log, sửa nguyên nhân, chạy maintenance lại rồi unlock |
| Weblate review trở thành gate thứ hai | Bật review workflow không nằm trong kiến trúc đã chốt | Tắt review gate trên Weblate; BA/Translator là gate nội dung, GitLab MR là nơi review/merge |

### 13.4. Translation Memory và machine translation

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Không có suggestion từ LibreTranslate | Dùng `localhost` thay vì hostname Docker hoặc service chưa load model | Dùng URL nội bộ `http://libretranslate:5000/`, kiểm tra container/network/model |
| Ollama container đang chạy nhưng không có suggestion | Ollama chưa được cài/configure như provider trong Weblate | Cấu hình provider trong `Administration → Automatic suggestions`, dùng endpoint nội bộ phù hợp và test một unit |
| Batch automatic translation không xuất hiện | Provider chưa được cài hoặc chưa thêm target language | Cài provider, thêm `vi`, kiểm tra validation trước khi chạy batch |
| Bản dịch tự động sai placeholder/tag | Dịch máy được commit mà chưa review | Dừng batch, kiểm tra placeholder/plural/HTML/XML và chỉ commit sau khi BA/Translator xác nhận |

### 13.5. Lỗi liên quan đến GitLab

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Không tạo được MR hoặc báo credential | Đây là lỗi Git transport/API, không phải file setting | Chuyển sang `weblate-gitlab-integration.md` để kiểm tra token, URL, branch và backend |
| Webhook đã báo thành công nhưng component không cập nhật | Component bị lock, fetch lỗi hoặc POT/template path sai | Kiểm tra repository maintenance và các mục POT/PO ở trên; chi tiết webhook thuộc tài liệu GitLab |

## 14. Tài liệu tham chiếu

- [Weblate projects and components](https://docs.weblate.org/en/latest/admin/projects.html)
- [Weblate add-ons](https://docs.weblate.org/en/latest/admin/addons.html)
- [Update PO files to match POT](https://docs.weblate.org/en/latest/admin/addons.html#update-po-files-to-match-pot-msgmerge)
