# Kiến trúc submod và mở rộng

## Quyết định Phase 1

Giữ IEE làm chủ campaign map/startpos, MIXER cung cấp unlocker/helpers. Submod độc lập chỉ chứa
những DB row, localization, script và asset do project tạo. Workshop Required Items tương lai phải
khai báo IEE và MIXER; metadata pack dùng đúng `!cr_immortal_empires_expanded.pack`, `!b_mixer.pack`.
MCT hiện đã cài, có liên quan cấu hình IEE/MIXER; xác nhận yêu cầu theo phiên bản khi phát hành.

IEE có hai startpos path: `campaigns/cr_combi_expanded/startpos.esf` và
`campaigns/wh3_main_combi/startpos.esf`. Báo cáo faction này đọc **cr_combi_expanded**.
Không đặt startpos vào submod để "gộp" campaign: file cùng path sẽ cạnh tranh thay thế, không tự merge.
Không copy toàn bộ bảng hoặc script của IEE để thay một faction; giữ phạm vi override nhỏ và ghi lý do từng row.

Namespace đề xuất `mc_` cho key/path/listener/state mới. Với override có chủ đích phải giữ key gốc;
với entity mới phải dùng key mới. Dùng asset paths tham chiếu dependency, không đóng gói lại binary của tác giả.

## Các lớp công việc

| Tính năng | Hướng triển khai | Điều kiện / giới hạn |
|---|---|---|
| Tên | Loc key `factions_screen_name_cr_cth_agents_of_the_moon` và các biến thể adjective/rebels | Kiểm tra ưu tiên loc và nhiều ngôn ngữ |
| Cờ/màu | `factions_tables` flags_path và các uniform/banner colour; asset cờ mới tự tạo | Kiểm tra alpha/mipmap/size và battle material |
| Roster | Truy ngược military group, recruitment/buildings, mercenary/RoR và subtype permissions | `faction_rebellion_units_junctions` không phải toàn bộ roster tuyển quân |
| Lord/Skill Tree | Agent subtype, main/land unit, art set, frontend data, skill node sets/links/effects tương ứng | Chưa xác nhận đủ schema/API để build; không chỉ đổi portrait |
| Model 3D riêng | Model authored, rig/skin theo skeleton phù hợp, reuse animation bằng tham chiếu | Phải thử skeleton, bone names, proportions, mounts, LOD, materials, weapon sockets và animation trong battle |
| Tạo/chia faction | Phân biệt kích hoạt faction có sẵn với faction mới trong startpos; phối hợp workflow IEE/MIXER | Không giả định Lua tạo được faction tùy ý; cần kiểm tra startpos/tool và ID allocation |
| Chia province/map | Có DB junction nhưng topology, slots, pathfinding và startpos phải đồng bộ | Đổi DB junction đơn lẻ không đủ; là nhánh nghiên cứu campaign map riêng |
| Family Tree/hôn nhân/sinh con | Mô hình quan hệ riêng do script lưu bền vững và UI riêng; dùng character keys/IDs ổn định có migration | Chưa chứng minh có hệ thống family tree native kiểu Three Kingdoms trong WH3 |
| Di truyền skill/class | Rule engine explicit, whitelist skill/effect, RNG có kiểm soát, tạo Lord lúc trưởng thành | Không hứa di truyền model/genetics hay class native; cần test save/load, chết/hồi sinh và multiplayer |
| Custom Lord Creation | Adapter riêng nếu mod cung cấp API thật; kiểm tra pack/script và quyền trước tích hợp | Đã thấy pack trên máy nhưng chưa phân tích API; không tự copy code |

## API đã thấy trong dữ liệu cài đặt

- `mixer_enable_custom_faction(startpos_id)` ở `script/_lib/mod/mixer_lib_frontend.lua:83`.
- `mixer_add_starting_unit_list_for_faction(faction_key, unit_list)` ở cùng file, dòng 20.
- `mixer_add_faction_to_major_faction_list(faction_key)` ở cùng file, dòng 117.
- IEE gọi `core:add_ui_created_callback` cho frontend enable.
- IEE MCT gọi `cm:is_region_owned_by_faction`, `custom_starts:region_change`,
  `custom_starts:teleport_character_faction_leader`, `custom_starts:force_diplomacy_change`.

Đây là bằng chứng tồn tại ở phiên bản đang cài, không phải cam kết API ổn định.
Không gọi API nào trong phase này. Các API family tree/spawn/UI/save-state cần nghiên cứu nguồn game
và kiểm thử riêng trước khi viết implementation.

## Lộ trình đề xuất

1. Phase 2: tên/cờ/màu trên Agents of the Moon, test campaign mới và MCT, chốt load precedence.
2. Phase 3: roster và Lord cơ bản dựa trên skeleton/animation Cathay, skill tree có phạm vi nhỏ.
3. Phase 4: model authored và pipeline asset; kiểm chứng rig/material/LOD/battle.
4. Phase 5: family simulation tối thiểu: quan hệ + save/load + sinh con giả lập; sau đó mới mở inheritance/class.
5. Nhánh độc lập: faction/province/map, cần đánh giá tooling và cách duy trì tương thích với mỗi bản IEE.

Không thực hiện các phase này cho tới khi người dùng mở rộng phạm vi.
