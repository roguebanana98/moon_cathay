# Quest battle Huyen Ve — mức sẵn sàng thực tế

Đối chiếu local ngày 03/11/2026, sau yêu cầu làm rõ tính khả thi.
Lần audit ban đầu chỉ đọc dữ liệu. Trạng thái triển khai mới nhất ở đoạn dưới.

**Hiện hành v25 r3:** đủ sáu chương đã tích hợp/cài/bật private test; campaign
rescue/reward đã nối. Điểm battle tìm đất hợp lệ quanh Long Vi; marker điều tra
quanh Leilou. Địch mới nhắm hộ vệ để tăng sức ép. Chưa full campaign playthrough.
IEE script dùng main_warhammer; r3 đã sửa guard nhận alias và kiểm tra Long Vi.
Xem `HUYEN-VE-V25-QUEST-INTEGRATION.md` và báo cáo mới trong quest-chain build.
Các đoạn audit/prototype bên dưới được giữ làm lịch sử, không mô tả launcher hiện tại.

**Lịch sử prototype 03/11:** rescue prototype v4 đã chạy thật từ Quest Battles
tới Decisive Victory trên Amber Bow, Da Lien sống và hai mục tiêu hiện/hoàn thành.
Log native xác nhận script và nhóm quân. Moon Bow rừng tuyết đã bị loại; lỗi
thiếu scripted_objectives DB và sai localisation đã sửa. Chưa duyệt cân bằng
(đứng yên vẫn thắng), chưa thử nhánh Hero chết/thua, chưa nối campaign/reward.
Đã thoát game, khôi phục v24 và intro preference; không mở campaign save.
Xem `HUYEN-VE-V25-QUEST-INTEGRATION.md`. Full campaign end-to-end vẫn **0/1**.

**Cập nhật sau yêu cầu nhận Da Lien sớm:** thiết kế hiện hành giữ **một quest
battle ở chương 2/cấp Huyen Ve 8**, ngay sau chương 1; thưởng Da Lien và Crimson
Moonstone. Không còn chờ chương 6/cấp 25/thu đủ bộ. Các bảng 0/3 và đánh giá ba
trận bên dưới là lịch sử audit bản cũ. Battle hiện hành đã có prototype như
cập nhật trên. Prototype phải làm trận giải cứu đầu game, không triển khai
battle Ấn/Kiếm hoặc thêm một trận cuối khác.

Mục tiêu cân bằng mới: quân tier 1–2, battle proxy Da Lien với bộ phép đầu game
giới hạn, không dùng preset Custom Battle cấp 40/full spell kit. Bỏ yêu cầu cũ
giữ 4 phút; ưu tiên mục tiêu thắng quân vây và giữ Hero sống. Map/điểm campaign,
deployment/entry, enemy faction/roster/count và timeline phải chốt qua prototype.
Chưa có số unit/key hoặc tọa độ nào được duyệt chỉ từ thay đổi thứ tự quest.

## Kết luận audit ba battle cũ — chỉ dùng làm bằng chứng lịch sử

**Chưa thể chắc ba quest battle Huyen Ve sẽ hoạt động hoặc đạt chất lượng.**
Thiết kế tại thời điểm audit là ý tưởng campaign có bằng chứng hạ tầng, chưa phải battle
spec đầy đủ. Số battle Huyen Ve đã cấu hình và kiểm chứng end-to-end: **0/3**.
Không được dùng sự tồn tại của battle native làm bằng chứng mod mới chạy được.

## Hai loại vị trí cần tách rõ

1. Điểm quest trên campaign: `missions.location_x/location_y`, radius và quan
   hệ với campaign Expanded; cần đứng trên đất đi được, không ở biển/núi hoặc
   phần map ngoài phạm vi. Marker điều tra là một điểm riêng, chưa chắc trùng
   điểm mở battle. Teleport và lọc đúng Huyen Ve cũng cần kiểm chứng.
2. Battlefield: `battle_set_pieces.battlefield_folder`, `catchment_area`, BMD
   layer nếu có; quân khởi đầu cần deployment zone, viện quân cần entry hợp lệ.
   Tọa độ campaign gần Long Vi không tự tạo battlefield giống Long Vi.

Native Dragon's Fang có mission IE ở (745, 462), nhưng đó là tọa độ native,
**không phải tọa độ được duyệt cho IEE**. Không sao chép sang Huyen Ve theo suy đoán.
Hiện chưa chốt bất kỳ tọa độ số nào cho ba trận mới.

## Bằng chứng cụ thể: Dragon's Fang native

Set piece: `wh3_dlc24_cth_yuan_bo_dragons_fang`.

- Map: `wh3_main_macro_nur_realm_01`, catchment `catchment_35`.
- Weather: `weather/battle/wh_nurgle_realm_03.environment_group`.
- Kiểu classic, player attacker, teleport cost 500, autoresolve campaign false.
- Script: `script/battle/quest_battles/yuan_bo/battle_script.lua`.
- Đây là Nurgle Realm; chưa phù hợp để khẳng định là đường tiếp tế/rừng Long Vi.

| Nhóm script | Faction trong DB battle | Unit thường trong junction DB | Lệnh viện quân |
|---|---|---|---|
| cathay_traitors | wh3_main_cth_cathay_qb1 | 4 Jade Warriors; 2 Crane Gunners; 2 Grand Cannons; 2 Fire Rain Rocket Batteries | Có sẵn, lệnh tấn công tại message start |
| plaguebearer_horde | wh3_main_nur_nurgle_qb1 | 1 Nurglings; 5 Plaguebearers `_0`; 2 Plaguebearers `_1` | Signal 80.000ms, đợi thêm 1.000ms rồi cho phép vào |
| rot_flies | wh3_main_nur_nurgle_qb1 | 3 Chaos Furies; 2 Rot Flies | Signal 120.000ms, đợi thêm 1.000ms |
| unclean_ones | wh3_main_nur_nurgle_qb1 | 3 Nurglings; 2 Great Unclean Ones | Signal 160.000ms, đợi thêm 1.000ms |
| daemon_prince | wh3_main_nur_nurgle_qb1 | 1 Rot Flies | Signal 200.000ms, đợi thêm 1.000ms |

Các số trên là số unit card trong bảng junction, không phải số cá thể lính và
chưa gồm character records. Junction character gắn hai Alchemist vào defender_1,
một character record tên `wh3_dlc24_qb_cth_alchemist_2` vào defender_3 với script
name `unclean_ones`, và Daemon Prince vào defender_5. Cần resolve character/unit
type trước khi diễn giải hình dạng nhân vật từ tên record.

Các mốc timer là offset script, không bảo đảm toàn đợt đã xuất hiện trên màn hình
đúng giây đó: còn delay, điểm entry và thời gian di chuyển. Native script dùng
`message_on_any_deployed` để ra lệnh rush sau khi có unit thực sự triển khai.
Defender_3 có approach_angle 90, các nhóm còn lại 0; không thể từ đó kết luận
trái/phải/bắc/nam trên map mới khi chưa kiểm tra orientation và entry.

Faction QB ở đây là cấu hình phe của quân trong set piece. Không cần suy ra
người chơi phải khai chiến với faction Cathay/Nurgle đang tồn tại trên campaign.
Nếu dùng lại key faction cho battle riêng thì tạo army records mới của mod;
không sửa/kill quân campaign hoặc khóa ngoại giao của faction QB dùng chung.

## Cơ chế đã đọc được trong thư viện

`generated_army:reinforce_on_message` trong `lib_generated_battle.lua` gọi
`deploy_reinforcement(false)` trước, chờ message và wait_offset, rồi gọi
`deploy_reinforcement(true)`. Đây là bằng chứng trực tiếp có thể giữ và thả
viện quân theo trigger, không phải chỉ đoán từ tên hàm.

Thư viện cũng có `generated_battle:set_victory_countdown_on_message` để điều
chỉnh countdown kết thúc trận. Việc tránh thắng sớm khi chưa vào đợt tiếp theo
vẫn phải được thiết kế và thử trong prototype cụ thể.

## Các map khác tìm được, chưa chọn cho Huyen Ve

| Set piece native | Battlefield | Catchment | Trạng thái |
|---|---|---|---|
| wh3_cp1_qb_cth_bhashiva_heavens_gate | wh3_cp1_bhashiva_qb1 | catchment_01 | Có record DB; chưa kiểm tra địa hình/entry/BMD cho kịch bản mới |
| wh3_cp1_qb_cth_bhashiva_final_battle | wh3_cp1_bhashiva_final_battle | catchment_01 | Có record DB; chưa kiểm tra dependencies/script đặc thù |
| wh3_dlc24_cth_yuan_bo_compass | major_n_cth_weijin | trống | Native siege; không mặc định phù hợp trận ngoài đồng |

Không chọn map chỉ vì tên có Cathay. Phải xem đúng battlefield, vùng deploy,
đường đi và entry. Tồn tại record trong TSV chưa chứng minh toàn bộ tài nguyên
và quyền nội dung đã hợp lệ cho custom set piece.

## Những gì còn thiếu ở từng battle

| Trận Huyen Ve | Điểm campaign | Map/deploy/entry | Địch và viện quân | Thời điểm/điều kiện | Kết luận |
|---|---|---|---|---|---|
| Chương 3 — Ấn | Chưa chốt tọa độ marker và quest | Chưa chọn map | Chủ đề Cathay phản đồ; chưa chốt faction key/roster/count/character | Chưa chốt mốc đánh sườn và cửa vào | Chưa sẵn sàng triển khai |
| Chương 5 — Kiếm | Chưa chốt tọa độ | Chưa chọn map | Cathay rồi Chaos; chưa chọn god/faction và roster | Chưa chốt trigger chuyển giai đoạn, timeout dự phòng và mục tiêu phụ | Chưa sẵn sàng triển khai |
| Chương 6 — Hero | Chưa chốt tọa độ | Chưa chọn vị trí bảo vệ/entry | Chưa chốt roster địch, hộ vệ và battle proxy Lam Anh | 4 phút mới là ý tưởng; death/fail và đợt cuối chưa làm | Chưa sẵn sàng triển khai |

Không chuyển đội hình native trong bảng trên thành roster Huyen Ve mà không
ghi nhận đó là quyết định thiết kế mới và kiểm tra lại cân bằng.

## Trình tự prototype trong audit cũ — đã thay bằng chương 2 ở phần cập nhật trên

Làm **một vertical slice chương 3** trước khi cam kết cả ba trận:

1. Chọn một map native có đủ deploy/entry đã kiểm tra trực quan. Ghi rõ battlefield,
   catchment/layer và các vùng dùng được; không hứa đặt vật thể nghi lễ mới.
2. Chọn tọa độ marker và quest thực trên `cr_combi_expanded`, xác minh đường đi.
3. Chốt army manifest: faction, alliance, unit keys, số lượng, rank, character,
   script labels và entry cho từng nhóm. Đối chiếu từng key với DB.
4. Chốt event timeline: battle start, cảnh báo, trigger/time viện quân, order sau
   deploy, chống lặp, khóa thắng sớm và điều kiện giải phóng khóa.
5. Build/diagnose/roundtrip pack thử riêng, rồi vào battle bằng quân campaign
   Huyen Ve trên Expanded; chứng minh đúng quân, đúng map và viện quân vào được.
6. Thử thắng, thua, retry, teleport trở về, nhận đúng một item và save/load.

Chỉ sau vòng này mới được nói đã chứng minh setup được quest battle Huyen Ve.
Đạt chất lượng còn cần playtest với quân người chơi yếu/mạnh, pháo, bay và
pathfinding; một trận load được chưa đủ.

## Nguồn kiểm tra

- `reference/local/lord-vanilla/db/battle_set_pieces_tables/data__.tsv`
- `reference/local/lord-vanilla/db/battle_set_piece_armies_tables/data__.tsv`
- `reference/local/lord-vanilla/db/battle_set_piece_armies_junctions_tables/data__.tsv`
- `reference/local/lord-vanilla/db/battle_set_piece_armies_units_junctions_tables/data__.tsv`
- `reference/local/lord-vanilla/db/battle_set_piece_armies_characters_junctions_tables/data__.tsv`
- `reference/local/lord-vanilla/db/missions_tables/data__.tsv`
- `reference/local/lord-scripts/script/battle/quest_battles/yuan_bo/battle_script.lua`
- `reference/local/lord-scripts/script/_lib/lib_generated_battle.lua`

Đây là đối chiếu nguồn local, chưa chạy RPFM build hoặc test game trong lần này.
