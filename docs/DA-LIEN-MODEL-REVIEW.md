# Da Lien — Beautiful Neferata model review

Trạng thái game hiện tại: [v22 đã tích hợp/deploy](DA-LIEN-V22-APPEARANCE.md)
bỏ cổ áo, da hồng ấm và trượng mặt trăng; chưa xác nhận runtime. Ghi chú
scene-only trong các mốc bên dưới không thay thế trạng thái v22.

Scene mới nhất: [đầu trượng trăng lưỡi liềm](DA-LIEN-MOON-STAFF.md), kế thừa da
hồng nhẹ và bỏ cổ áo. Các chỉnh sửa này chưa được export/deploy vào game v21.

Scene mới nhất: [da đã được làm hồng ấm nhẹ](DA-LIEN-SKIN-WARM.md), kế thừa bản
bỏ cổ áo. Hiện là material tint trong Blender, chưa bake texture/deploy vào game.

Chỉnh sửa mới nhất: [đã bỏ riêng mảnh cổ áo dựng phía sau](DA-LIEN-COLLAR-EDIT.md)
trong một scene Blender riêng; tay áo và các mesh khác giữ nguyên. Pack game
v21 chưa thay model theo chỉnh sửa này.

Tiếp nối: đã tích hợp/deploy [v20 appearance test](DA-LIEN-V20-VISUAL-TEST.md)
với script tạo Hero một lần gần Long Vi; chưa xác nhận runtime. Scene Blender
bên dưới vẫn là bản xem riêng, không được dùng để export lại mesh của pack test.

03/11/2026. Người dùng đã chọn tên **Da Lien**, pháp sư con người của Agents of
the Moon: sát thương diện rộng lên lính, hồi máu nhẹ, buff giáp. Nguồn model được
chọn là Beautiful Neferata, Workshop **3809988722**.

## Scene xem thử

- Scene: `build/da-lien-model-review/da-lien-beautiful-neferata-review.blend`.
- Blender 5.2.3, đã mở UI và xem trước/bên hông/phía sau, material preview.
- Mesh/texture Beautiful Neferata giữ nguyên; native humanoid01ba, 86 bones.
- Vũ khí theo native VMD: dagger gắn `be_prop_0`, staff gắn `be_prop_5`.
- Native stand clip 61 frame, 30fps. Đây là preview Blender, chưa test trong game.
- Texture được chuyển thành PNG và pack vào blend để xem màu, không sửa DDS nguồn.
- Nguồn body: một LOD, 238.865 tam giác. Blender import giữ 237.885 tam giác;
  chênh 980 cần kiểm tra importer/degenerate faces trước export, không coi là
  roundtrip bảo toàn geometry. Dagger 12.000 và staff 31.522 tam giác trong preview.
- Báo cáo: `model-review.json`, `reference-manifest.json` cùng thư mục build.

## Nhận xét khi xem

Ở tư thế đứng đã xem trước/hông/sau, model có đủ texture, tóc, váy, staff và dagger;
chưa thấy lỗi biến dạng lớn ở các góc đó. Chưa thử run/attack/cast hoặc kiểm tra
clipping toàn bộ animation, không kết luận mesh đã đạt chất lượng runtime.

Các điểm đề xuất để người dùng duyệt, **chưa chỉnh sửa**:

1. Da mặt/thân khá nhợt; cân nhắc ấm hơn để đọc thành nhân vật người sống.
2. Cổ áo cao nhọn và màu đỏ sẫm/vàng mang cảm giác Vampire; cân nhắc bảng màu
   đêm/trăng và chỉnh cổ áo nếu muốn gần Agents of the Moon hơn.
3. Đầu staff có hình dạng ly/cốc; có thể giữ hoặc thay bằng đầu trượng trăng/sen.
4. Cần giải quyết mật độ mesh và chỉ có một LOD trước khi tích hợp gameplay.
   Không tự giảm polygon hoặc sửa tay/head/rig chỉ để tạo preview.

## Việc tiếp theo

- Duyệt ngoại hình và phần muốn giữ/đổi trực tiếp trên scene.
- Chọn lore/spell keys/cây skill riêng theo vai trò đã chốt; loại cơ chế Undead.
- Tạo subtype Hero riêng, không đổi trực tiếp Neferata native hoặc clone class Lord.
- Kiểm thử animation lookup, equip, spell targets người sống, UI, embed và wounded.

Đã trích xuất chỉ đọc vào `reference/local/beautiful-neferata`; không sửa mod
Workshop, game pack, launcher hoặc save. Chưa tạo gameplay pack/hero. Model
dẫn xuất giữ private; chưa có phê duyệt phân phối công khai asset của tác giả.
