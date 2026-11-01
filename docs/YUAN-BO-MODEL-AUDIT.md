# Khảo sát model Yuan Bo cho lord mới

Ngày: 2026-11-01. Đọc trực tiếp pack vanilla đang cài, không chỉnh game hoặc pack thử nghiệm.

## Kết luận về thân và kiếm

Hai model riêng, được lắp bằng variant mesh definition (VMD):

- VMD: `variantmeshes/variantmeshdefinitions/cth_jade_dragon_human.variantmeshdefinition` trong `variants.pack`.
- Slot `body`: `variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.wsmodel`.
- Slot `weapon_2`, `attach_point="weapon_2"`: `variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.wsmodel`.
- Hai WSMODEL trỏ đến hai file cùng tên đuôi `.rigid_model_v2` trong `variants3.pack`.
- Slot weapon_1 và weapon_3–6 trống. Slot head trống; hình học đầu nằm trong body asset, không có head model được VMD này gọi riêng.

Body RMV2 khai báo skeleton `humanoid01e`. Kiếm RMV2 có tên skeleton rỗng, vertex format static (0). Vì vậy không cần skin toàn bộ kiếm theo các ngón tay: game đặt mesh kiếm vào attachment của nhân vật. Skeleton có bone `weapon_2`, index 3, parent index 0. Không nên diễn giải thành parent trực tiếp vào hand bone: đây là bone vũ khí riêng; chuyển động của animation và attachment quyết định tư thế kiếm. Cuộc khảo sát này chưa giải mã track từng animation hoặc xem chuyển động trong renderer.

## Thông số đo trực tiếp

RMV2 version 8. Vertex là vertex đã tách theo UV/normal trong file game, không phải số điểm độc nhất trong Blender. Tam giác = index count / 3; đã kiểm tra index nằm trong giới hạn vertex, kích thước buffer và offset khớp toàn bộ file.

| LOD | Body vertices | Body triangles | Sword vertices | Sword triangles | Tổng triangles |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 15,146 | 19,812 | 822 | 814 | 20,626 |
| 1 | 12,845 | 15,879 | 634 | 570 | 16,449 |
| 2 | 8,783 | 9,955 | 409 | 316 | 10,271 |
| 3 | 7,188 | 7,761 | 344 | 246 | 8,007 |

- Body có 2 mesh part ở LOD0–2 và 1 part ở LOD3. WSMODEL phân part opaque và alpha; không coi hai part này là hai nhân vật.
- Body LOD0–1 dùng weighted4 (format 4, stride 36 byte); LOD2–3 weighted2 (format 3, stride 32 byte). Đây là layout skinning, không phải số bone của toàn rig.
- Sword: 1 part ở mọi LOD, static, stride 32 byte.
- Các giá trị `LodCameraDistance` lưu trong cả hai file: 10 / 20 / 30 / 10000. Không khẳng định đây là khoảng cách thực nhìn thấy bằng mét hoặc quy tắc engine chuyển LOD.
- Body file 1,911,626 byte; sword file 91,608 byte, chưa tính texture và animation.
- Skeleton `animations/skeletons/humanoid01e.anim` trong `anim2.pack`: 96 bone, gồm cả weapon_1–6 và các bone phụ. Đây không phải 96 bone đều cần có weight trên mesh.
- `variants_tables`: variant `wh3_dlc24_cth_cha_yuan_bo_human`, filename `cth_jade_dragon_human`, scale 1.15, scale_variation 0, mount_scale 1.
- Body part opaque LOD0 có AABB x≈1.450, y≈2.142, z≈0.675 đơn vị model. Đây là bounding box của part trong pose lưu, không phải chiều cao người đo ngoài đời.
- `battle_entities` dùng height 2.2, radius 0.7, mass 1000. Các giá trị gameplay/collision này tách biệt với kích thước mesh; không dùng mass làm trọng lượng vật lý của bản thiết kế.

## Texture và material

Các texture riêng của bộ đang dùng nằm trong `variants_dds3.pack`:

| Asset | Kích thước | Map riêng |
| --- | --- | --- |
| Body | 2048 × 2048 | base_colour, material_map, normal, mask |
| Sword 2h | 512 × 512 | base_colour, material_map, normal, mask |

Base colour/material map dùng DDS DX10 header; normal/mask dùng DXT5 trong file đã kiểm tra. Các mip count và file size được ghi trong JSON. Không tự suy DX10 là một codec cụ thể nếu chưa đọc DXGI format. Có texture mang tên sword_1h trong pack nhưng VMD hiện tại không sử dụng chúng.

Body WSMODEL phân material weighted4/weighted2 và alpha_on/alpha_off theo LOD. Sword dùng `shaders/rigid_character_emissive.xml.shader`; material có emissive_tint xanh (0,1,0) và emissive_strength 1.7. Body opaque weighted4 có strength 1.2. Muốn đổi sang chủ đề ánh trăng cần khảo sát cả base colour, mask và tham số emissive; chỉ đổi màu diffuse có thể vẫn còn phát sáng xanh. Một số noise/blood/dither map được dùng chung từ commontextures.

## Animation và liên kết dữ liệu

`land_units` của bản người dùng animation `hu1e_dlc24_yuan_bo_dragon_jade`.
Animation table tương ứng khai báo `SkeletonName=humanoid01e` và hai fragment `hu1e_cathey_base`, `hu1e_dlc24_yuan_bo_dragon_jade`.
Fragment `hu1e_dlc24_yuan_bo_sword` cũng khai báo humanoid01e; có slot đứng, di chuyển, đánh, v.v. Một số slot tham chiếu animation Zhao Ming. Vì vậy không nên chỉ sao chép những file có chữ yuan_bo rồi coi là đủ toàn bộ dependency.

Đường dẫn hiển thị battle cơ bản:

`main_units → land_units + unit_variants → variants → VMD → WSMODEL → RMV2 + material → DDS`

Animation được chọn qua land_units và các animation table/fragment; campaign art có liên kết riêng qua campaign_character_art_sets/arts. Bản Huyen Ve hiện tại clone unit từ Yuan Bo người, giữ variant donor; đây là lý do còn dùng ngoại hình Yuan Bo. Đổi ngoại hình riêng cần tạo variant/VMD riêng và cập nhật liên kết của lord mới, gồm campaign art liên quan, tránh sửa VMD vanilla dùng chung.

## Bộ thông số đề xuất để làm lord mới

Đây là ngân sách tham chiếu theo donor, không phải giới hạn cứng của engine:

1. Body và kiếm tách riêng. Dựng body khoảng 20 nghìn triangles LOD0; kiếm khoảng 800–1,000 triangles nếu mức chi tiết tương đương. Tạo đủ 4 LOD, tham khảo các mức tổng trong bảng.
2. Giữ rig humanoid01e, tên/thứ tự bone và bind pose từ donor nếu muốn dùng lại animation Yuan Bo. Skin body theo rig đó; kiểm tra vai, khuỷu tay, cổ tay, áo dài, tóc/râu và những bộ phận mềm khi chạy/đánh/cast/chết. Mesh từ generator vẫn cần retopology, UV và rigging trước khi đưa vào game.
3. Dùng kiếm donor làm mẫu căn grip/pivot/hướng và chiều dài trong local space; attachment vẫn là weapon_2. Không tự dựng kiếm tại world origin rồi giả định game căn lại điểm cầm. Hình dáng vũ khí quá khác có thể cần animation mới, không chỉ thay mesh.
4. UV/map body 2K và sword 512 là mốc khởi đầu phù hợp. Giữ vật liệu alpha cho phần cần xuyên và kiểm tra giảm LOD. Tạo đường dẫn texture/material riêng để không đổi Yuan Bo gốc.
5. Làm bản đổi model tối thiểu trước: clone variant/VMD, thay body hoặc sword, giữ animation và scale donor. Sau khi kiểm tra tư thế/điểm cầm mới chỉnh scale hoặc collision nếu thiết kế yêu cầu.
6. Kiểm tra cả battle, campaign và portrait 3D: đứng, chạy, xoay, charge, chuỗi đánh, cast, knockback và death; zoom qua LOD. Khảo sát tĩnh này chưa xác nhận runtime, clipping, shader hay silhouette.

## Bằng chứng và tái lập

- Tài sản trích nằm trong `reference/local/yuan-bo-model/` (ignored, không đưa vào src hoặc Git).
- `reports/yuan-bo-model-audit.json`: số đo từng part/LOD, SHA256 hai model, bone list và DDS headers.
- `tools/Audit-Yuan-Bo-Model.py`: đọc lại dữ liệu đã trích và kiểm tra cấu trúc.
- File gốc được giữ nguyên. Không build/deploy bản model mới trong lần khảo sát này.

Nguồn định dạng và công cụ: [TheAssetEditor](https://github.com/donkeyProgramming/TheAssetEditor), đặc biệt `Shared/GameFiles/RigidModel/RmvFileHeader.cs`, `RmvCommonHeader.cs`, `RmvFile.cs`, `LodHeader/Rmv2LodHeader_V7_V8.cs` và `Shared/GameFiles/Animation/AnimationFile.cs`. Asset Editor hỗ trợ kitbash, rig/animation và chuyển đổi model; chưa cài thêm trong workspace. Các số liệu Yuan Bo phía trên lấy từ game local, không suy từ mô tả công cụ trên web.
