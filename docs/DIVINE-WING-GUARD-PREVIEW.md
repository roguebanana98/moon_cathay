# Divine Wing Guard — Jade Warriors và cánh trắng

Ngày: 26/11/2026. **Chỉ preview Blender; chưa tích hợp vào game.**

Người dùng chọn tên Divine Wing Guard (Thánh Dực Quân), giáp Jade Warriors và
cánh trắng để xem trước phương án thay Onyx Crowmen của Agents of the Moon.
Không thay Crowmen, bảng DB, chỉ số, tuyển quân hoặc pack trong lần này.
Zhao vẫn được người dùng yêu cầu để lại sau; đây là phần việc độc lập.

## File làm việc

- Scene chính đã nhúng texture:
  `build/divine-wing-guard-preview/divine-wing-guard-preview-packed.blend`.
- Ảnh trước: `build/divine-wing-guard-preview/divine-wing-guard-front.png`.
- Ảnh sau: `build/divine-wing-guard-preview/divine-wing-guard-back.png`.
- Manifest/report: `asset-manifest.json`, `preview-report.json` cùng thư mục.
- Bản scene trước khi pack texture được giữ nguyên, không ghi đè cửa sổ người dùng.

Mốc preview ban đầu lưu scene/tài nguyên trong build/reference bị ignore. Sau đó
người dùng yêu cầu backup checkpoint animation đã lưu vào Git: bản editable hiện
ở assets/working/divine-wing-guard/divine-wing-guard-working.blend (Git LFS).
Xem checkpoint.json/README cạnh file và tài liệu animation review; các bản trích
xuất native/Workshop vẫn bị ignore.

## Thành phần và thao tác

- Native Jade Warriors body01/head01/sword01/shield01, giữ geometry, UV và weights.
- Nguồn cánh: Angels of Warhammer, Workshop `3045854505/terickz_angels.pack`.
  Model `terickz_angel_body_first_02.rigid_model_v2`, các phần LOD0 số 2–9;
  không dùng thân/chân thiên thần. Donor gốc được giữ trong collection ẩn.
- Tỷ lệ cánh 0.78 so với donor; căn mốc spine_2 vào lưng Jade Warrior.
- Shader riêng làm trắng lông, giữ chi tiết/alpha; không sửa pixel texture nguồn.
- Kiếm/khiên giữ native prop bones và pivot RMV2. Tư thế đứng lấy từ native
  `humanoid01e/sword_shield/stand/hu1e_sword_and_shield_stand_01.anim`.
- Hai góc render đã xem; khung trước được mở rộng để không cắt đầu cánh.

## Giới hạn và trạng thái kiểm tra

**Đây là assembly ngoại hình với hai rig native riêng:** humanoid01e cho Jade
Warrior, humanoid16c cho cánh. Cánh theo lưng bằng constraint trong preview.
Chưa chuyển thân/cánh thành một rig xuất game, chưa kiểm tra bay/hạ cánh/attack/
death hoặc engine clipping. Không coi idle thân và render tĩnh là kiểm chứng bay.

Đã kiểm tra import warnings rỗng, bounds hữu hạn, 3 phần thân/đầu, 2 prop, 8 phần
cánh; texture đã pack vào scene và report không có ảnh mất. Native/Workshop
được đọc vào `reference/local/divine-wing-guard`, không sửa pack gốc.
Không export RMV2/pack, deploy, sửa launcher/save hoặc mở game.

## Dựng lại và tiếp tục

1. `tools/Prepare-Divine-Wing-Guard-Preview.py --game <verified game folder> --angels <verified source pack>`
   trích dependency vào reference riêng; công cụ lấy từ config/local.json.
2. Chạy `tools/Build-Divine-Wing-Guard-Preview.py` trong Blender background mới,
   `--factory-startup`. Script mặc định bảo vệ output có sẵn.
3. Script hiện đã pack ảnh trước khi save; bản scene `-packed.blend` hiện tại
   được tạo từ preview đầu bằng bước pack riêng, giữ nguyên bản trước đó.
4. Tiếp theo chờ người dùng xem/chỉnh ngoại hình. Mọi retarget, animation hoặc
   game integration là bước sau, không nằm trong kết quả preview này.

Không chạy builder đè scene người dùng đã chỉnh hoặc đã duyệt.
