# Huyen Ve — thử fantasy longsword trong Blender

Cập nhật sau khi duyệt preview: người dùng yêu cầu đưa kiếm vào mod để test game.
Đã xuất 4 LOD 12.000/6.000/3.000/1.200 tam giác, giữ UV và cách căn trong preview.
Các map basecolour/material/normal ở 2048², mask trung tính 128², DDS/mipmap đúng
pipeline WH3. Kiếm là static prop, không skeleton/binding thứ hai; VMD hiện có
gắn vào weapon_2. Model cơ thể, tay, runtime animation và gameplay giữ nguyên.

Model RMV2 thực tế đã nhập lại với DDS: kiểm tra 12 tư thế đứng/chạy/chém/cast
trên đủ 4 LOD đạt. Render `exported-sword-review.png` đã kiểm tra trực quan.
Đây là kiểm chứng file/Blender; chưa xác nhận trong game hoặc mọi frame không clipping.
Scene nhập lại: `huyen-ve-fantasy-sword-exported-review.blend` cạnh scene preview.
Pack đã cài và bật, r5 tắt/giữ rollback; có backup launcher và hash cài đặt trùng.
Pack: `build/huyen-ve-v25-quest-chain/mc_huyen_ve_v25_quest_chain_test_r6.pack`.
Trạng thái cài/bật đối chiếu `deployment.json` cùng thư mục pack.

Nguồn chọn kiếm cho các lần build sau: `src/campaign/huyen-ve-sword.json`.
Rebuild: Convert-Fantasy-Sword-Textures.py → Export-Huyen-Ve-Fantasy-Sword.py
(Blender) → Validate-Fantasy-Sword-Graphics.py → Review-Exported-Fantasy-Sword.py
(Blender) → Build-Fantasy-Sword-Test-Pack.py. Builder bản test r6 bảo vệ không
ghi đè pack đã có; full quest builder đọc manifest kiếm để giữ lựa chọn này.

## Lịch sử bước xem Blender

03/11/2026: người dùng thêm FBX trong `assets/authored/fantasy longsword 3d model`,
yêu cầu thử thay kiếm Huyen Ve, sau đó xác định xem trong Blender trước.

Scene riêng: `build/huyen-ve-fantasy-longsword/huyen-ve-fantasy-sword-preview.blend`.
Dựa trên body/rig native đã duyệt ở `huyen-ve-v16-animation-review.blend`.
Kiếm cũ giữ trong scene và ẩn; body, tay và animation không sửa. Source FBX và
scene đã duyệt giữ nguyên. Không export RMV2, đóng pack hoặc deploy trong bước này.

FBX: 233.486 vertex, 466.979 tam giác, một UV, bộ basecolor/metallic/roughness/normal
4K. Preview giữ toàn bộ hình học và nối texture PBR. Đây chưa phải mesh tối ưu cho game.

Căn đồng tỷ lệ 1,57458, tâm chuôi tại Z=0,815 trong FBX; đổi trục để lưỡi theo
kiếm cũ và gắn `COPY_TRANSFORMS` vào `weapon_2`. Chín mẫu pose thuộc đứng/chạy/chém
đạt sai số transform 0. Điều này kiểm tra attachment, không chứng minh không xuyên
tay/giáp trong mọi frame. Phần chắn tay trang trí lớn cần người dùng xem tỷ lệ.

Scene mở ở animation đứng, giữ đủ các clip native để thử chém/chạy. Có ảnh render
`huyen-ve-fantasy-sword-preview.png`, intake và `preview-validation.json` cạnh scene.
Tool: `tools/Prepare-Huyen-Ve-Fantasy-Sword-Preview.py`.
