# Concept 03 — model đầu

Ngày 2026-11-02. Người dùng chọn concept 03 (bạch bào, giáp bạc, đai xanh)
và yêu cầu dựng 3D. Sau khi kiểm tra Tripo quốc tế, người dùng chọn phương án
2: một bản Public xem thử, dùng tối đa 45 credits hiện có. Không có quyền mua
subscription hoặc nâng cấp gói. Tripo hiện thông báo xuất file 3D/Private
cần nâng cấp; không được né giới hạn xuất bằng cách lấy dữ liệu nội bộ viewer.

## Tài sản đã tạo local

- `assets/concepts/moon-warden/concept03-model-input/moon-warden-concept03-front-apose-v1.png`:
  ảnh mặt trước một nhân vật, tay rời thân, không kiếm, tạo bằng imagegen từ
  concept đã duyệt để tránh sinh hai cơ thể từ tờ hai hình chiếu.
- Prompt và công cụ nằm cạnh ảnh trong `prompt.txt`.
- `assets/authored/moon-warden/concept03-v1/moon-warden-lotus-sword-v1.blend`
  và `.glb`: mesh kiếm prototype dựng bằng script Blender, UV tự động và vật liệu
  riêng, không chứa asset game. Preview PNG và báo cáo đi kèm. Đây là bản hình
  khối đầu; chi tiết guard và hoa văn chưa khớp hoàn toàn concept. 16,458 tam
  giác trước bước tối ưu; chưa phải ngân sách game khoảng 800–1,000 tam giác.
- Script tái tạo: `tools/Build-Concept03-Sword.py`.

## Trạng thái Tripo

Đã tạo xong model H3.1 Geometry & Texture, Public trên bản quốc tế:
https://studio.tripo3d.ai/workspace/generate/aaf0a312-0f6a-4ff7-8915-d72a9505c819

- Chi đúng 45 credits: số dư 140 → 95. Không mua gói, không chạy generation thứ hai.
- Viewer báo Triangle, 1,970,610 faces và 1,023,713 vertices. Đây là số hiển thị
  của Tripo; chưa đối chiếu bằng đọc file local vì chưa xuất được file thân.
- Đã xem góc trước, cạnh và sau bằng xoay viewer. Giữ được áo trắng, giáp vảy
  bạc, đai xanh, tóc búi và dáng tổng thể của concept. Chi tiết lưng do Tripo suy
  đoán từ một ảnh trước, khác bản vẽ hai góc; các bề mặt và họa tiết mềm cần
  duyệt/làm sạch. Chưa kiểm chứng topology/manifold/skin weight hoặc chuyển động.
- Viewer ban đầu báo Unknown server error; bấm Retry của viewer đã tải được
  model, không phải Generate hoặc Free Retry, không chi thêm credits.
- Đã thử Export GLB 2K bằng nút chính thức: bước xuất hiện hộp yêu cầu nâng
  cấp. Không tải model qua dữ liệu nội bộ viewer, không né paywall.
- Ảnh kiểm chứng: `reports/concept03-tripo-front.jpg`, `concept03-tripo-side.jpg`,
  `concept03-tripo-back.jpg`, `concept03-tripo-final.jpg`.
- Báo cáo thông số và chi phí: `reports/concept03-tripo-generation.json`.

Bản `.com` đã mở nhầm ban đầu là bản Trung Quốc; không dùng để tạo model.
Sau khi người dùng bật quyền file URL cho extension Edge, tải ảnh đã thành công.
Tên tự động/category Tripo có chữ "ancient chinese armor"; đây là nhãn tự sinh
của dịch vụ, không phải thay đổi chủ đề Đại Việt đã duyệt.

Đã hoàn tất bản Public xem thử theo lựa chọn người dùng. Chưa có file thân
local, chưa rig, chưa làm LOD thân, chưa xuất RMV2 hoặc sửa pack đang chơi.
