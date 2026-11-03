# Concept 03 — model đầu

Trạng thái 03/11/2026: concept03/Tripo là lịch sử thử nghiệm. Ngoại hình đã chọn
hiện là [model được duyệt](HUYEN-VE-APPROVED-MODEL.md), tích hợp từ v16 và kế thừa
trong private test v19. Các ghi chú v14/v15 và việc tiếp tục sửa thân concept03
bên dưới mô tả các mốc cũ, không phải công việc bắt buộc của Lord hiện hành.

## Rig thử local — 2026-11-02

Đã tạo working mesh 24k/14k/8k/4k tam giác, căn bind pose và rig 96 xương
humanoid01e của Yuan Bo; chuyển PBR sang DDS/material WH3, xuất RMV2 và lắp
kiếm riêng vào weapon_2. Scene, preview và pack đồ họa nằm trong
`build/huyen-ve-model-v1/`. Chi tiết và giới hạn:
[HUYEN-VE-MODEL-RIG.md](HUYEN-VE-MODEL-RIG.md).
Tà áo vẫn cần làm sạch và sửa weight ở tư thế chạy/đánh sâu; chưa đạt chất
lượng phát hành, chưa kiểm thử game. Bản gameplay v14 giữ nguyên.

## Đã nhận file local từ người dùng — 2026-11-02

Người dùng cung cấp thư mục `assets/authored/ancient warrior armor 3d model`.
Đã nhập FBX `tripo_convert_54bb716b-006f-47b3-8c1a-26c175497887.fbx` vào Blender
4.5.15 và render kiểm tra trước/ngang. Không ghi đè bản gốc.

- Một mesh object, 237,377 vertex, 474,836 triangle, 1 UV layer, 1 material.
- Không có armature, vertex group, vertex weight hoặc animation action.
- Các map base color, metallic, normal và roughness được material gọi đến đã
  tìm được và tải đủ ở 4096×4096. Thư mục còn có map `rm` chưa xác định cách
  đóng kênh; không giả định có thể dùng thẳng làm material map của WH3.
- Kích thước scene sau import khoảng 0.407 × 0.234 × 0.980 đơn vị Blender;
  chưa căn scale/pose về skeleton humanoid01e của Yuan Bo.
- Kiểm tra hình ảnh: đúng bạch bào/giáp bạc/đai xanh, thân không cầm kiếm,
  các tà áo và trang trí cần kiểm tra biến dạng sau khi skinning.
- Scene kiểm tra: `build/model-intake/huyen-ve-tripo-20261102/huyen-ve-tripo-inspection.blend`.
  Preview `front.png`, `side.png` trong cùng thư mục.
- Báo cáo và SHA-256 nguồn: `reports/huyen-ve-tripo-intake.json`.
  Script: `tools/Inspect-Tripo-Lord.py`.

Đây là thông số bản nguồn lúc tiếp nhận. Các bước tối ưu, căn rig, vật liệu và
lắp kiếm đã có bản thử như mốc ở trên; chưa tích hợp vào Lord trong game.

## Lịch sử bản Public xem thử

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

Ở thời điểm bản Public xem thử chưa có file thân local. Sau đó người dùng đã
cung cấp FBX; tiến độ local hiện tại được ghi ở đầu tài liệu.
