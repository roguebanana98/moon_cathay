# Divine Wing Guard — xem thử bay, hạ cánh và chiến đấu

Ngày 26/11/2026. **Blender-only; chưa tích hợp vào game.**

## Scene hiện hành

`build/divine-wing-guard-animation/divine-wing-guard-animation-review-v2.blend`

Đã mở bằng Blender 5.2.2 LTS, mở rộng timeline, fit toàn bộ 1–626 và bật playback.
Đã quan sát frame chuyển 98 → 185 cùng cánh thay đổi tư thế. Space dừng/phát;
kéo playhead đến marker để xem từng đoạn. Tên đoạn xuất hiện trong khung camera.
Việc mở lại file không tự khởi động playback; dùng Space/nút Play.

| Frame | Đoạn |
|---|---|
| 1–82 | Take off — cất cánh |
| 83–202 | Flight — bay |
| 203–292 | Hover — lơ lửng |
| 293–378 | Air attack — đánh trên không |
| 379–436 | Landing — hạ cánh |
| 437–496 | Ground stand — đứng đất |
| 497–548 | Sword attack A |
| 549–626 | Sword attack B |

Scene static `build/divine-wing-guard-preview/divine-wing-guard-preview-packed.blend`
và các cửa sổ đang mở được giữ nguyên. V1 animation review không còn là bản xem
hiện hành: độ cao transition/camera chưa đúng. V2 chuẩn hóa độ cao nhân vật và
camera bám pelvis; không dùng V1 để đánh giá kết quả hiện hành.

## Nguồn chuyển động và cách ghép

- Cất cánh, bay, hover, tấn công trên không và landing: clip native humanoid16c
  của Valkia, trích read-only từ `anim2.pack` game trên ổ H.
- Đứng/đánh đất: clip native humanoid01e sword/shield của Jade Warriors.
- Giữ hai rig riêng. Chuyển chuyển động thân bằng retarget rotation có bù rest
  pose; 48 ánh xạ xương thân, đầu/jaw/eyelid. Không thay geometry hoặc skin weights.
- Cánh/feather giữ kênh chuyển động nguồn trên rig cánh; theo lưng bằng constraint.
- Kiếm/khiên dùng relative hand grip lấy từ pose native trong scene static; kiểm
  tra matrix attachment không đồng nghĩa đã chứng minh mọi tiếp xúc tay hoàn hảo.
- Timeline bake đầy đủ location/rotation/scale để tránh dư pose giữa các đoạn.
- Xóa root XY cho review tại chỗ. Offset độ cao trình bày chuẩn hóa cất cánh/landing
  theo độ cao pelvis về cùng mức bay khoảng 3m, thay cho độ cao do engine quản lý.
  Offset, retarget và montage này không được xuất làm animation game.

## Đã kiểm tra và giới hạn còn lại

- 8 clip đã đọc; không có importer warnings. Kiểm tra matrix hữu hạn mọi frame
  nguồn, 5 pose/đoạn cho mesh bounds và prop attachment (40 pose tổng).
- Geometry/weights của các mesh hiện lên giữ nguyên; source static hash giữ nguyên.
- 32 image packed. Đã render và xem các pose giữa flight/landing/combat.
- Đã kiểm tra UI thực tế và thấy playback tiến frame; đây không phải engine QA.

**Vấn đề còn lại:** lông cánh gập có thể chồng lên vai/đầu trong một số tư thế
chiến đấu đất. Đòn trên không lấy từ choreography dùng giáo của Valkia nhưng đang
cầm kiếm Jade Warrior, nên chưa coi là đòn kiếm hoàn thiện. Ánh xạ thân/cloth và
điểm nối cánh vẫn cần người dùng xem; kiểm tra tọa độ không chứng minh hết clipping.
Chưa là một rig xuất game hoàn chỉnh, chưa thử runtime bay/đánh/collision.

Không export RMV2/animation/pack, không sửa DB, unit stats, tuyển quân, launcher,
save, native/Workshop pack; không mở game. Không chép model dẫn xuất vào Git.

## Công cụ và báo cáo

- `tools/Prepare-Divine-Wing-Guard-Animation.py`: trích 8 clip và pose cánh đứng.
- `tools/Build-Divine-Wing-Guard-Animation.py`: dựng scene từ static checkpoint,
  bake review, kiểm tra và render; mặc định bảo vệ output có sẵn.
- `build/divine-wing-guard-animation/clips.json`: đường dẫn nguồn/nhãn.
- `animation-review-report.json` cùng thư mục: checks và trạng thái hiện hành.
- `review-flight.png`, `review-landing.png`, `review-combat.png`: ảnh đã xem.

Builder chạy trong process Blender background mới; không chạy đè scene có chỉnh
sửa chưa lưu của người dùng. V2 đã lưu bố cục UI trong Blender 5.2.2; không suy từ
việc xem preview thành phê duyệt export hoặc tích hợp game.

## Checkpoint đã lưu theo yêu cầu — 26/11/2026

Đã Save trực tiếp cửa sổ v2 đang xem, giữ frame 496 và trạng thái pause/bố cục/
visibility/material/animation hiện tại. Không append lại đối tượng hoặc chạy
builder để thay thế chỉnh sửa trong scene. Các cửa sổ khác và static scene giữ nguyên.

- File tiếp tục: `build/divine-wing-guard-animation/divine-wing-guard-animation-review-v2.blend`.
- Snapshot riêng: `build/divine-wing-guard-checkpoints/20261126T053543Z/divine-wing-guard-saved.blend`.
- SHA256: `3a649c18551828fd16510a4e7f0ee8ceb76bedc606f25e4d5bc257eca98b0711`.
- Resume pointer: `build/divine-wing-guard-checkpoints/resume-latest.json`.
- Metadata/audit nằm cạnh snapshot và trong resume pointer.

Đã mở lại snapshot bằng Blender 5.2.2 để kiểm tra 32 image packed, không image ngoài,
không linked library; đủ 8 marker, range1–626 và hai action body/wing. Hash snapshot
trùng bản live vừa lưu. Snapshot là bản đầy đủ scene, giữ cờ ẩn của donor/studio/rig.

Người dùng yêu cầu lưu model, không yêu cầu tích hợp game hoặc upload model lên Git.
Checkpoint hiện ở build bị ignore. Không suy mốc lưu thành mọi chuyển động/clipping
đã hoàn thiện. Tiếp tục từ file đã lưu/snapshot; không chạy generator đè lên nó.

## Backup editable model vào Git theo yêu cầu — 26/11/2026

Người dùng yêu cầu đẩy model vừa lưu lên Git. Bản đầy đủ scene đã được sao chép
byte-identical từ checkpoint vào:

`assets/working/divine-wing-guard/divine-wing-guard-working.blend` (Git LFS).

SHA256 `3a649c18551828fd16510a4e7f0ee8ceb76bedc606f25e4d5bc257eca98b0711`,
36.903.322 byte; 32 image packed, không linked library hoặc image ngoài.
Metadata portable và hướng dẫn nằm tại `checkpoint.json`/`README.md` cạnh file.
Sau clone dùng file tracked này; nếu còn là pointer nhỏ, chạy `git lfs pull`.

Mốc này thay thế ghi chú chỉ lưu local ở trên đối với đúng checkpoint này.
Full scene giữ visibility của donor/rig/studio và toàn bộ animation/material.
Không đưa native/Workshop pack hoặc thư mục trích xuất vào Git. Chưa tích hợp game;
những giới hạn chuyển động đã ghi vẫn còn. Không chạy builder đè bản người dùng.
