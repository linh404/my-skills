---
name: facebook-room-finder
description: Tìm, lọc và so sánh tin cho thuê phòng trọ trên Facebook bằng MCP Chrome DevTools; áp dụng khi người dùng muốn tìm tin mới hoặc tiếp tục cải thiện cách tìm.
---

# Tìm phòng trọ trên Facebook

Hỗ trợ người dùng tìm các tin phòng trọ phù hợp trên Facebook, thu thập thông tin có thể kiểm chứng từ bài đăng, rồi trình bày danh sách ngắn kèm đường dẫn nguồn. Cách tìm phải thích ứng với yêu cầu từng lần và những gì đã học được; không mặc định một bộ từ khóa, nhóm, thứ tự lọc hay cách chấm điểm cố định.

## Cách làm

- Dùng MCP Chrome DevTools để thao tác trên Facebook trong phiên trình duyệt hiện có. Bắt đầu bằng `mcp__chrome_devtools__list_pages`, chọn đúng tab bằng `select_page`, rồi dùng `take_snapshot` để đọc giao diện. Điều hướng, nhập từ khóa và mở bài qua các điều khiển nhìn thấy được; lấy snapshot mới sau khi giao diện chuyển trạng thái.
- Chọn cách khám phá phù hợp với tiêu chí người dùng và giao diện hiện tại: tìm bài đăng, tìm trong nhóm, Marketplace hoặc kết hợp. Điều chỉnh truy vấn khi kết quả quá rộng, cũ hoặc lệch khu vực. Không coi một cách tìm đã hiệu quả một lần là quy tắc bắt buộc.
- Nếu thiếu thông tin làm thay đổi đáng kể kết quả, hỏi ngắn gọn về các tiêu chí quan trọng nhất (chẳng hạn khu vực, ngân sách, thời điểm dọn vào). Nếu người dùng đã đưa đủ tiêu chí hoặc muốn tìm rộng, bắt đầu luôn và nêu rõ phạm vi đã dùng.
- Với mỗi tin hữu ích, ghi nhận những gì bài đăng thực sự nêu: giá thuê, khu vực/địa chỉ được công khai, diện tích, tiện ích, tiền cọc, ngày đăng và điều kiện liên quan. Đính kèm liên kết bài đăng hoặc nguồn truy cập được. Ghi “chưa thấy thông tin” khi thiếu; không tự suy đoán.
- Gộp tin trùng khi có đủ dấu hiệu, phân biệt thông tin người đăng khẳng định với nhận xét của mình, và gọi các điểm đáng ngờ là “cần xác minh” thay vì kết luận lừa đảo. Sắp xếp kết quả theo tiêu chí hiện tại của người dùng, kèm lý do ngắn và hạn chế của dữ liệu.
- Nếu Facebook yêu cầu đăng nhập, CAPTCHA, xác minh danh tính hoặc chặn truy cập, dừng thao tác bị chặn và báo người dùng; không tìm cách vượt qua. Chỉ dùng nội dung hiển thị mà người dùng có quyền xem; ưu tiên snapshot giao diện. Không truy cập endpoint/API riêng hay cố lấy dữ liệu ẩn.
- Mặc định chỉ tìm và báo cáo. Không bình luận, nhắn tin, gọi điện, gửi biểu mẫu, đặt cọc hay chia sẻ thông tin cá nhân của người dùng nếu họ chưa yêu cầu rõ. Nếu người dùng yêu cầu liên hệ, làm theo đúng nội dung và phạm vi họ chỉ định; hỏi lại khi người nhận hoặc nội dung gửi chưa rõ.

## Cập nhật từ những lần tìm

Sau mỗi phiên tìm đã hoàn tất, cập nhật mục này trong skill khi có bài học có ích cho lần sau. Đây là ghi chú sống, được sửa hoặc xóa khi có dữ liệu mới; không phải bộ quy tắc bất biến.

- Chỉ giữ kinh nghiệm có thể tái sử dụng, ví dụ một cách tìm đã cho kết quả tốt trong một khu vực hoặc một thay đổi giao diện đã quan sát.
- Phân biệt điều người dùng xác nhận là sở thích lâu dài với quan sát tạm thời về Facebook. Không biến tiêu chí của riêng lần tìm hiện tại thành sở thích mặc định.
- Ghi rõ ngữ cảnh và mức độ chắc chắn cho quan sát còn tạm thời; kiểm tra lại vì giao diện, nhóm và chất lượng kết quả có thể đổi.
- Không lưu thông tin liên hệ cá nhân, chi tiết riêng tư, hay nội dung từng tin đăng vào ghi chú học tập. Không thêm một ngoại lệ đơn lẻ thành quy tắc chung.
- Giữ ghi chú ngắn. Khi mục này còn trống, chỉ thêm bài học sau lần dùng thực tế đầu tiên; người dùng có thể yêu cầu sửa hoặc bỏ bất kỳ ghi chú nào.

### Kinh nghiệm đã rút ra

Chưa có. Sẽ bổ sung sau các lần tìm thực tế.
