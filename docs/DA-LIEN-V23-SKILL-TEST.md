# Da Lien v23 — Moon Arts skill test

Ngày 03/11/2026: người dùng duyệt hướng sửa Yin/Heavens và yêu cầu đưa vào mod
để test, đồng thời cập nhật goal. Đã build và deploy private v23 thay v22.

Pack: `build/huyen-ve-v23-da-lien-skills/mc_huyen_ve_v23_da_lien_skills.pack`.
SHA256: `4accd5177824df1946f3d81f298898665202a9d8bcb13ef6c264dba97c7d4c5e`.
Source và bản trong game có hash bằng nhau. Launcher v23 bật/v22 tắt; có backup.
Đây là bản test: chưa xác nhận skill UI, animation niệm phép, migration hoặc cân
bằng trong engine. Quest nhận Hero chưa triển khai.

## Bộ phép và đường mở khóa

| Kỹ năng | Điểm tối đa | Mở khóa |
|---|---:|---|
| Blossom Wind | 2 | Bản cơ bản miễn phí từ đầu; mua 2 mức nâng cấp |
| Power of Yin | 1 | Cấp 1 |
| Earth Blood | 3 | Cấp 1 |
| Flesh to Stone | 3 | Cấp 1 |
| Storm of Shadows | 3 | Cấp 1 |
| Evasion | 1 | Cấp 7 và 4 điểm trong 5 ô phía trước |
| Talons of Night | 3 | Cấp 8 và Evasion |
| Comet of Casandora | 3 | Cấp 8 và Evasion |
| Earthing | 1 | Cấp 8 và Evasion |
| Magical Reserves | 1 | Cấp 8 và Evasion |
| Arcane Conduit | 1 | Cấp 12 và 4 điểm trong 4 ô nâng cao |

Giữ effect nâng cấp phép native, trừ Blossom Wind chuyển mức native 2/3 thành
hai mức mua điểm 1/2 vì bản cơ bản đã được cấp qua hidden foundation. Các phép
còn lại: mức 1 mở phép; mức 2 overcast/cooldown; mức 3 tối ưu cost/miscast.
Composite lore chỉ có sáu base spell và Power of Yin; overcast dùng native links.
Không có Life Bloom, Regrowth, Metal spell hoặc Enchanted Metallurgy.

## Các nhánh còn lại

Sáu skill riêng, mỗi ô một điểm và không bắt mua ô trước:

| Skill | Cấp | Effect |
|---|---:|---|
| Moon Scholar | 8 | Cooldown Yin/Heavens −10%; không áp dụng cho Life |
| Silver Ward | 12 | +20 giáp bản thân |
| Deep Wells | 16 | +5 sức chứa dự trữ Winds của quân đoàn |
| Moonlit Grace | 20 | +10% tốc độ, +8 melee defence bản thân |
| Veil of the Moon | 24 | −2 lượt hồi phục khi bị thương |
| Lunar Mastery | 28 | +10% spell mastery; attribute group living Alchemist đã có spell_mastery |

Wind Harmony và Ranged Discipline mở ở cấp 7. Mentor có ba mức cấp 30/40/50.
Campaign giữ sáu skill native tương ứng khung engineer của Cathay Alchemist:
Increase Mobility, Boost Income, Damage Building, Assassinate, Hinder Replenishment,
Specialist. Giữ rank gates native của từng mức, hidden action enables, action
scaling và nền background trait. Không có mount, nhánh đỏ Lord hay Undead.
Immortality được cấp miễn phí qua script, không phải ô phải mua.

Đã tính lại V2: 26 ô nhìn thấy, 51 điểm để max. Nhánh magic 22, unique 6,
resistance 2, campaign 18 và Mentor 3. Hidden foundation không tính vào chi phí.
Ngân sách tăng cấp 1→50 thông thường là 49 điểm nếu không có điểm thưởng.

## Test trong game

Khởi động lại game để đọc pack mới. Custom Battle → Grand Cathay → Heroes →
Da Lien có preset cấp 40 với cả sáu phép và các battle passive/unique để test ngay.
Kiểm tra sáu icon phép, cast/overcast, hướng wind/vortex, friendly fire, Comet báo
trước, Earth Blood hồi máu đúng healing cap và Flesh to Stone tăng giáp đúng mục tiêu.
Power of Yin và Arcane Conduit vẫn cần kiểm tra trigger/hiệu quả trong battle.

Campaign vẫn giữ spawn một lần gần Long Vi đang sở hữu. Với Da Lien đã có từ
bản Metal, script v23 dùng native reset một lần theo CQI, dọn skill cũ và cấp lại
hai foundation mới. Không tăng XP, không tự mua phép/unique, không tạo Hero khác.
Nhân vật, background, trang bị và model giữ nguyên. Cần kiểm tra điểm hoàn lại,
không còn effect Metal, menu campaign action, wounded-return và save/load lần hai.
Marker reset và marker hoàn tất tách riêng để không reset lại các điểm vừa mua
nếu một bước dọn/grant cần thử lại.

Tham chiếu API migration:
[WH3 episodic scripting](https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html#function:episodic_scripting:force_reset_skills).
Đây là API có tài liệu; chưa chạy migration trong engine ở mốc bàn giao này.

## Kiểm tra đã thực hiện

- Roundtrip toàn bộ DB/loc mới/thay đổi qua RPFM đạt; không có diagnostic mới,
  không duplicate loc keys hoặc reference chặn mới.
- Kiểm tra độc lập sáu đường base/overcast/cost, chỉ Blossom Wind có sẵn cấp 1,
  đường mua hợp lệ cấp 2→12, Mentor 30/40/50 và preset Custom Battle đạt.
- So payload v22: thay đúng 5 payload của Da Lien, thêm 9 payload; các phần khác
  byte-identical, bao gồm graphics/portrait/Huyen Ve/province/startpos/spawn v20.
- Deploy có backup launcher, đọc lại cấu hình và đối chiếu hash. File pack v22
  giữ lại để rollback; các launcher entry khác không đổi.

Báo cáo tại `build/huyen-ve-v23-da-lien-skills/`: `pack-validation.json`,
`skill-regression.json`, `skill-manifest.json`, `diagnostics-review.json` và
`deployment-report.json`. Không sửa trực tiếp save hoặc Workshop.

Build lại bằng `tools/Build-Da-Lien-Skill-Test.py` vào thư mục candidate mới;
script chủ động không ghi đè pack đã tồn tại. Validator:
`tools/Validate-Da-Lien-Skill-Test.py`; deploy:
`tools/Deploy-Da-Lien-Skill-Test.py`.
