# Huyen Ve v25 — tích hợp đủ sáu nhiệm vụ

Cập nhật 03/11/2026. Bản private test hiện bật: `mc_huyen_ve_v25_quest_chain_test_r7.pack`.
SHA256: `7688bf9369353f10f253d43c7c3f4ba7085a27db2dbddd8628812456b2704a66`.
R6 giữ nguyên, tắt làm fallback trong game; v24 còn bản build local, không còn cài ở data. Không bật đồng thời hai bản.

R4 chỉ đổi dữ liệu icon Crimson Moonstone sang artwork Gem of Blood native; các dòng DB khác giữ nguyên, script và tài nguyên khác byte-identical. Smoke campaign dưới đây thuộc r3; không có lượt runtime mới cho r4.

R5 tích hợp ảnh thẻ Da Lien người dùng cung cấp: 5 PNG đúng kích thước native, giữ nguyên mọi payload khác của r4. Đã cài/bật sau khi người dùng tự đóng game. Chưa kiểm tra chân dung mới trong game. Xem DA-LIEN-USER-PORTRAIT.md.

R6 thay kiếm Huyen Ve bằng fantasy longsword đã duyệt. 4 LOD, DDS 2K/mip; mọi payload ngoài kiếm byte-identical với r5. Đã cài/bật r6, r5 tắt. Chưa kiểm chứng kiếm mới trong game.

R7 thêm vị trí đầu game Long Vi cho nguyên quân đoàn Huyen Ve qua native startup callback; chỉ áp dụng campaign mới, không dịch chuyển save đang chơi. Đã cài/bật, còn kiểm chứng trực tiếp trong game.

## Tiến trình đã triển khai

| Chương | Cấp Huyen Ve | Điều kiện | Thưởng |
|---|---:|---|---|
| 1 | 6 | Sở hữu Long Vi, Huyen Ve chỉ huy thắng 2 trận campaign thường | Ngọc Bội |
| 2 | 8 | Thắng rescue Quest Battle bằng Huyen Ve, Da Lien sống | Da Lien cấp 5 + Crimson Moonstone |
| 3 | 10 | Sở hữu Avauka hoặc trả 2.000 vàng khi chủ thành không có chiến tranh với mình | Giáp |
| 4 | 14 | Hero độc lập điều tra marker gần Leilou; sau đó Hero độc lập di chuyển vào Long Vi đang sở hữu | Ấn |
| 5 | 18 | Quân đoàn Huyen Ve tích lũy kill, mốc 2.000 tại Ultra, chỉnh theo unit size | Nguyệt Đăng |
| 6 | 22 | Huyen Ve tới Long Vi đang sở hữu, trả 3.000 vàng một lần; đợi 2 lượt faction sau đó | Kiếm Trấn Dạ |

Chỉ mở chương sau khi thưởng chương trước được xác nhận. Chương 6 mất Long Vi thì tạm dừng,
lấy lại tiếp tục, không thu phí lần hai. Chương 4 cho Hero khác giao hồ sơ; Lord/Hero embed
không tính, đứng sẵn tại Long Vi không tự hoàn thành. Chương 5 chụp force CQI trước trận,
chỉ cộng kill của chính quân đoàn (gồm Lord/Hero/phép), loại Quest Battle và callback trùng.
Custom unit set bao phủ đủ 13 lớp quân đất native, gồm inf_spr/spcl mà all_land_units bỏ sót.
Độ chính xác manual/autoresolve còn phải thử engine.

Save state version 2 giữ chapter/scalars; nâng state chương 1 cũ không xóa tiến độ.
Không xóa đồ/Hero đã có, không tạo Hero trùng hoặc hạ cấp/reset Hero cũ. Hero bị thương
được nhận diện qua saved marker/CQI để chờ trở lại. Các đường tự spawn/cấp đồ visual test
được chặn trong v25 bằng saved flag. V24 fallback giữ hành vi test cũ.

## Quest Battle duy nhất

Map native Amber Bow: qb_wh2_dlc13_wulfhart_amber_bow, catchment_01.
Giữ deployment donor player/defender_1/attacker_3, không viện quân.
Chaos Lord cấp 2, 5 Marauders, 2 Warhounds, 1 Marauder Horsemen; proxy Da Lien cấp 5,
ba phép đầu game và Crimson Moonstone, hộ vệ Cathay. Chi tiết key/unit/deployment trong
src/campaign/huyen-ve-rescue-battle.json và DB graph được build/roundtrip.
Địch tấn công đội hộ vệ sau 1 giây; Da Lien chết dẫn tới thua. Không timer thắng.

Điểm campaign tìm bằng native valid-spawn quanh Long Vi, fallback vị trí đất hợp lệ;
không tìm được thì chờ thử lại. Dùng native set_mission_location_override sau phát mission
và khi khôi phục. mission_manager:set_position không đủ cho FIGHT_SET_PIECE_BATTLE.
Thưởng đòi cả thắng đúng trận/commander và MissionSucceeded.

## Bằng chứng và giới hạn

- 13 hồi quy state chương 1, 58 kiểm tra adapter/toàn tuyến, 10 tình huống thưởng Hero;
  battle mock và native generated_battle library contract đạt tại biên engine giả lập.
- DB roundtrip, mission/dilemma/marker/unit-set links và source/pack hash đạt;
  không diagnostic chặn mới/metadata warning mới; payload ngoài phạm vi byte-identical.
- Rescue prototype v4 đạt Decisive Victory thật, Da Lien sống và hai mục tiêu xanh.
  V4 quá dễ (không ra lệnh vẫn thắng); v25 đổi địch sang đánh hộ vệ, chưa duyệt cân bằng mới.
  V4 Continue về Trials of Fate; routing frontend và campaign return cần thử tiếp.
- Campaign r2 không khởi tạo controller: map IEE là cr_combi_expanded nhưng script campaign
  name là main_warhammer. R3 nhận cả hai tên và kiểm tra Long Vi tồn tại; thêm hồi quy
  nhận alias và loại Realm of Chaos. Smoke r3 đã đạt: controller khởi tạo state 2/chương 1; không thấy auto-spawn Hero visual test. Đã thoát game và khôi phục đủ 69 save/hash cùng intro preference. Báo cáo: runtime-campaign-smoke-r3.json.
- Chưa xác nhận playthrough sáu chương trong game, teleport/return, nhánh Da Lien chết,
  save/load từng chương, auto/manual kill và cân bằng. Không coi test Lua là bằng chứng engine.

Game lượt smoke: 9.0.5; rescue v4 cũ dùng 9.0.4. Backup đủ 69 save trước campaign QA.
Trạng thái khôi phục save/preference: build/huyen-ve-v25-quest-chain/campaign-smoke-session.json.
Báo cáo cùng thư mục: pack-validation.json, deployment.json, lua-regression.json.
QA battle cũ: build/huyen-ve-v25-rescue-prototype/runtime-qa-v4.json.
