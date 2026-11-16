---
name: weblate-gitlab
description: Vận hành, kiểm tra và xử lý lỗi luồng dịch Odoo giữa GitLab CI (POT), Weblate tự host (PO) và translation MR. Dùng khi job i18n CI fail, kiểm tra Weblate có đồng bộ POT/PO với code không, component thiếu ngôn ngữ/bị lock, Weblate không tạo MR, hoặc cấu hình component/webhook/credential Weblate–GitLab.
---

# Weblate ↔ GitLab cho Odoo

Bản cô đọng của skill `configure-weblate-gitlab-v2` (đọc reference ở đó khi cần chi tiết, xem bảng cuối).

`$SKILL_DIR` = thư mục chứa file SKILL.md này. Skill anh em (`odoo-wlc`, `configure-weblate-gitlab-v2`) nằm cạnh nó trong cùng repo skill hoặc ở `~/.codex/skills/`.

## Xác định thông số dự án trước

| Thông số | Lấy từ |
| --- | --- |
| Weblate project slug | `config/project.json` key `weblate_project`, hoặc user cung cấp; liệt kê bằng `odoo-wlc/scripts/weblate_api.py components <slug>` |
| Repo Weblate đọc | `GET components/<slug>/<component>/` → `repo`, `branch`, `push_branch`. Đối chiếu với remote git local: repo chung có thể là `upstream`, không phải fork `origin` |
| Component | Thường 1 component/module: `filemask=<addons_root>/<module>/i18n/*.po`, `new_base=.../<module>.pot`, `template` rỗng, format `po` |
| CI i18n | Đọc định nghĩa pipeline (`.gitlab-ci.yml` hoặc template CI được include). Chuỗi điển hình: export POT → commit `[skip ci]` lên `dev` → job sync tạo component/thêm ngôn ngữ trên Weblate → (tùy chọn) job dịch tự động + mở translation MR. Ghi lại tên job và biến kích hoạt chạy tay |
| Auth API | `~/.weblate` hoặc `WLC_URL`+`WLC_KEY` (dùng chung với skill `odoo-wlc`) |

## Quy tắc bất biến

1. Dev sửa source string → MR code. POT do CI sinh, PO `msgstr` do Weblate/BA. Không sửa tay `.pot`/`.po` trong repo.
2. Weblate không bao giờ push thẳng branch nguồn: backend `GitLab merge request`, push branch riêng (vd `weblate-translations`); Maintainer duyệt MR trên GitLab.
3. Chiều đi: GitLab push → webhook `https://<weblate>/hooks/gitlab/` → Weblate fetch → add-on `Update PO files to match POT (msgmerge)` (cài cấp project) cập nhật PO.
4. `Edit base file` tắt; không bật review gate trên Weblate nếu BA đã là gate nội dung.
5. Không tự `wlc commit`/`wlc push`/unlock/sửa setting live khi user chỉ yêu cầu kiểm tra; Commit/Push làm trên UI Weblate.
6. Không lộ token (mask phần `user:token@` trong repo URL khi in kết quả API).

## Kiểm tra đồng bộ (chỉ đọc)

```bash
git fetch -q <remote_repo_chung>   # so với branch mà Weblate đọc
python3 $SKILL_DIR/scripts/check_sync.py <weblate_project> <out_dir> [repo_root] [lang]
```

Script in mỗi component: POT local vs msgid trên Weblate, `<lang>.po` local vs Weblate (thiếu/thừa entry, msgstr khác), HTTP404 = component chưa có ngôn ngữ; dòng đầu là trạng thái repo Weblate (`remote_commit`, `needs_*`, `merge_failure`). Đọc kết quả:

| Dấu hiệu | Ý nghĩa |
| --- | --- |
| `remote_commit` ≠ HEAD của branch nguồn | Weblate chưa fetch commit mới (webhook/lock/lỗi fetch) |
| `pot_missing_on_weblate` / `weblate_extra_vs_pot` > 0 | Source trên Weblate lệch POT local |
| `po_only_weblate` > 0, msgstr không khác | Weblate đã msgmerge, local chưa nhận — chờ push MR |
| `msgstr_diff` > 0 | Bản dịch trên Weblate chưa về repo (hoặc ngược lại: file local chưa lên Weblate) |
| `needs_push` | Weblate còn commit chưa push → cần Push trên UI + merge translation MR |
| `weblate <lang> HTTP404` | Component chưa có ngôn ngữ đó |

Lịch sử thay đổi: `GET projects/<slug>/changes/?timestamp_after=<ISO>` (bỏ qua "String added in the repository" là nhiễu của bản ngôn ngữ nguồn).

## Triage theo ranh giới đầu tiên fail

| Ranh giới | Xem trước |
| --- | --- |
| Job CI sync `TimeoutError` khi gọi `POST components/.../translations/` (thêm ngôn ngữ) | Weblate chậm khi thêm ngôn ngữ cho component mới (commit repo bên Weblate). Các component sau điểm chết thiếu ngôn ngữ và job dịch/MR phía sau không chạy. Retry job hoặc chạy lại riêng bước sync |
| CI không push được POT (`403`) | Job token permission "Allow Git push requests", protected branch, diff chỉ `*/i18n/*.pot`, marker `[skip ci]` |
| POT thiếu string mới | Module có cài trong DB export, markup `_()`/`_lt`, addons path, đối số exporter |
| POT đổi mỗi lần chạy | Header/DB/Odoo version không deterministic |
| Webhook OK nhưng Weblate không có unit mới | Commit có trên branch nguồn chưa, component branch/`new_base`, component lock, maintenance log, add-on msgmerge |
| PO không có unit mới | Thiếu add-on msgmerge (template không tự chạy msgmerge) |
| Weblate push branch nhưng không có MR | Backend không phải `GitLab merge request`, API token thiếu scope `api` (`insufficient_scope`), push branch rỗng |
| Weblate push `403`/`terminal prompts disabled`/`miss credentials` | Credential `write_repository`, push URL, biến env sai cú pháp (`KEY=value`) |
| Translation MR conflict | Weblate còn commit pending hoặc PO bị sửa song song trên GitLab |
| Component locked | Đọc lỗi repo/add-on, sửa nguyên nhân, maintenance, rồi mới unlock |
| String cũ fuzzy / entry `#~` | msgid đổi; BA rà lại. Obsolete giữ nguyên trừ khi có cấu hình xóa |
| GitLab API `403 insufficient_scope` khi đọc pipeline | Token chỉ có scope hẹp; cần `read_api`, hoặc đọc thẳng file định nghĩa CI |

Không đồng nhất: webhook success ≠ đã fetch; branch đã push ≠ có MR; chọn POT template ≠ PO đã sync; job-token permission ≠ protected branch cho push.

## Reference chi tiết

Thư mục `configure-weblate-gitlab-v2/references/`:

| Cần | File |
| --- | --- |
| Docker Compose, volume, HTTPS, tunnel | `weblate-self-hosted-deployment.md` |
| Credential, protected branch, webhook, lỗi Git/MR | `weblate-gitlab-integration.md` |
| Project/Component/Files/add-on/language, lỗi UI | `weblate-settings-configuration.md` |
| Hợp đồng exporter POT, acceptance test | `odoo-ci-pot-workflow.md` |
| Full Export vs Changed Module Export, Manifestoo | `odoo-ci-job-solutions.md` |
| LibreTranslate/Ollama | `weblate-machine-translation.md` |

Dịch/upload bản dịch qua wlc: dùng skill `odoo-wlc`.
