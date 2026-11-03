# Da Lien — ảnh thẻ người dùng

03/11/2026: người dùng cung cấp PNG 593×1280 và yêu cầu căn kích thước, tích hợp vào mod.
Bản gốc được giữ tại `assets/authored/da-lien/portraits/Da_Lien_user_portrait.png`.

- Unit portrait và Custom Battle card: RGBA 60×130, giữ toàn bộ bố cục dọc.
- Faction leader portrait: RGBA 85×115, crop đầu/cổ từ ảnh gốc.
- Porthole và minspec fallback: RGBA 300×164 theo canvas native, ảnh đầu căn giữa;
  khoảng trống hai bên lấy màu nền của ảnh gốc. Không kéo ảnh dọc thành mặt ngang.

Resize bằng Lanczos, không chỉnh khuôn mặt hoặc tạo thêm nội dung. Năm PNG thay đúng
đường dẫn cũ; portrait settings/DB không đổi. Mọi payload khác byte-identical so với r4.
Kiểm tra kích thước/mode/giải mã PNG và dữ liệu sau đóng gói đạt.

Candidate: `build/huyen-ve-v25-quest-chain/mc_huyen_ve_v25_quest_chain_test_r5.pack`.
Đã cài và bật r5 sau khi người dùng tự lưu/thoát game; r4 tắt. Có backup launcher và đối chiếu SHA256 pack cài đặt. Chưa kiểm tra chân dung mới trong game.

Build/import: `tools/Import-Da-Lien-User-Portrait.py`.
Full-chain builder cũng đọc manifest portrait để giữ ảnh mới trong lần build sau.
Manifest và các PNG đã căn nằm cạnh ảnh gốc; preview/báo cáo tại thư mục build.
