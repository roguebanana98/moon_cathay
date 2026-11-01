# Agents of the Moon — kiểm tra nhiệm vụ

Ngày kiểm tra: 02/11/2026. Faction: `cr_cth_agents_of_the_moon`.
Đây là kiểm tra đọc dữ liệu local và script IEE/MIXER/vanilla, không sửa gameplay.
Save có sẵn được lưu ngày 30/10/2026, trước bản Huyen Ve. SHA256 của save khớp
nguồn đã dùng để tạo bản trích xuất; không coi đây là tình trạng UI đang chạy
hoặc bằng chứng runtime của v12. JSON kết quả: `reports/faction-missions-audit.json`.

## 1. Nhiệm vụ đã xác nhận trong save

| Nhiệm vụ | Mục tiêu đã lưu | Phần thưởng đã lưu/đối chiếu DB |
|---|---|---|
| Short Victory | Occupy/loot/raze/sack 30 settlements | Bundle Order short: +3 hero capacity |
| Long Victory | Hoàn thành Short Victory và occupy/loot/raze/sack 60 settlements | Bundle Order long: +10 hero recruit rank |
| Domination | Occupy/loot/raze/sack 272 settlements | Payload text `dummy_wh3_main_survival_forge_of_souls`; không thấy bundle chỉ số trong mission này |
| Capture Settlement | Chiếm khu định cư; danh sách region mục tiêu trong save để trống | 750 treasury và Potion of Strength |

Cả bốn có trạng thái `ACTIVE`. Không có thời hạn dạng nhiệm vụ có đếm lượt
được xác định trong bảng này. Mốc 30/60/272 là điều kiện settlement của engine,
không nên diễn giải thành phải đồng thời giữ từng ấy thành.

Startpos IEE gốc không chứa các CAMPAIGN_MISSION trong subtree faction được
trích xuất. Nhiệm vụ ở save được khởi tạo bởi hệ thống script trong campaign.

## 2. Vì sao không có chuỗi thắng riêng

Không tìm thấy khai báo faction trong các script nhiệm vụ/victory vanilla,
IEE và MIXER đã kiểm tra, hoặc trong source submod hiện tại.
Trong `script/campaign/main_warhammer/victory_objectives.lua`:

- `initialise_victory_missions()` chọn alignment Order theo subculture Cathay.
- Short/Long dùng các ngưỡng Order 30/60, cộng điều kiện hoàn thành Short.
- `create_long_objective()` chỉ thêm mục tiêu subculture bên trong nhánh có
  `self.factions[faction_key]`. Agents of the Moon không có entry riêng đó.
- Vì vậy không được áp các mục tiêu Great Bastion/diệt sáu phe thù của Cathay
  cho faction này chỉ vì chúng có trong bảng subculture. Save xác nhận chúng
  không nằm trong Long Victory của Agents of the Moon.
- Domination fallback là 272 theo script đang kiểm tra.

Hiện chưa có mục tiêu bảo vệ Long Vi, thống nhất Khuresh hoặc chuỗi mật lệnh
Moon Empress cho Huyen Ve. Quest item/battle của Yuan Bo cũng không tự đi theo
việc dùng model của ông; không thấy quest riêng gắn `mc_moon_warden` trong submod.

## 3. Chuỗi nhiệm vụ hướng dẫn dùng chung

MIXER `script/campaign/_narrative/wh3_narrative_shared_faction_data.lua` thêm
faction người chơi theo culture và chọn đối thủ ban đầu qua thành địch gần
quân của faction leader nhất, trong số các faction đang chiến tranh có home region.
Nếu không có đối thủ hợp lệ, dữ liệu đối thủ ban đầu có thể không được đặt.
Save cũ thiếu dữ liệu narrative không tự được khởi tạo lại từ đầu.

`wh3_narrative_shared_chains.lua` cung cấp các nhánh: đánh đối thủ đầu tiên,
chiếm thành/hoàn chỉnh province/ban commandment, tuyển quân, nâng cấp thành,
nghiên cứu, hero, tài chính, tạo quân đội và ngoại giao. Chúng là chuỗi có điều
kiện, chịu ảnh hưởng advice history và trạng thái save, không phải toàn bộ cùng
xuất hiện ở lượt 1. Capture Settlement trong save thuộc hệ thống này.

## 4. Các nhiệm vụ cơ chế Cathay trong script

Culture loader đăng ký `wh3_narrative_cathay.lua` cho faction người chơi Cathay.
Các cấu hình dưới đây tồn tại trong script; chưa xác nhận chúng đều phát và
hoàn thành được trên campaign hiện tại. Đặc biệt nhánh Harmony còn dùng pooled
resource/effect cũ, cần thử runtime theo phiên bản game.

| Mission key suffix (prefix `wh3_main_camp_narrative_cathay_`) | Điều kiện chính | Reward mặc định trong script |
|---|---|---|
| `restore_harmony_01` | Sau khi Harmony lệch tới ngưỡng ±4, đưa về 0 | 1.000 gold |
| `construct_harmony_buildings_01` | Xây 3 công trình có effect Yin/Yang theo bộ lọc script | 3.000 gold + uncommon arcane item |
| `compass_01` | Đổi hướng Compass | 750 gold |
| `compass_02` | Bộ đếm đổi hướng đạt 4 | 750 gold + uncommon armour |
| `ivory_road_01` | Dispatch caravan | 750 gold |
| `ivory_road_02` | Hoàn thành 5 chuyến caravan | 750 gold + uncommon banner |

Tên hàm của mission công trình có chữ 'five', nhưng số truyền vào thực tế là
3; phải đọc giá trị cấu hình thay vì dựa vào tên/comment. Reward một số mission
có cơ chế kế thừa từ mission trước, bảng trên ghi payload khai báo tại node đó.

## 5. Legendary Hero và quest battle

- **Saytang:** vanilla đặt `unlock_rank = 13`, có điều kiện sở hữu Shadows of
  Change hoặc gói Cathay tương ứng. MIXER hiện tại thêm `starting_mission_keys`
  cho faction Cathay phụ trong pre-first-tick callback của `mixer_unlocker.lua`.
  Có đường cấu hình cho Agents of the Moon; chưa xác nhận kích hoạt trong v12.
- **Gotrek & Felix:** vanilla `unlock_rank = 15`; MIXER thêm mission quest battle
  Cathay và bổ sung allowed-faction list cho faction phụ. Còn phụ thuộc họ đã
  được faction khác nhận hay chưa, quyền DLC và trạng thái campaign.
- **Taoyan:** vanilla hiện tại có `unlock_rank = 8` (comment còn ghi 13).
  `starting_mission_keys` chỉ liệt kê các faction Cathay chính, không có Agents
  of the Moon; MIXER đã kiểm tra không có patch Taoyan tương ứng như Saytang.
  `get_mission_key()` có thể rơi về `mission_keys[1]`, nhưng bảng này dùng key
  faction nên trả nil. Đây là thiếu sót cấu hình đáng kiểm tra/sửa, chưa phải
  bằng chứng đã quan sát lỗi runtime.

Mốc rank trên là giá trị code, không suy diễn từ comment hay tự đổi thành
level hiển thị. Các LH là nhân vật dùng chung; không khẳng định phe người chơi
luôn có thể nhận nếu nhân vật đã được cấp cho phe khác.

## 6. Nguồn local và bước tiếp theo

- `reference/local/save-compact.json`, `startpos-compact.json`: dữ liệu snapshot.
- `reference/local/mixer-20261101/script/campaign/mod/mixer_unlocker.lua`:
  patch mở nhiệm vụ hero cho faction phụ, đặc biệt đoạn Cathay khoảng dòng 467.
- `reference/local/mixer/script/campaign/_narrative/wh3_narrative_shared_faction_data.lua`:
  ánh xạ culture và chọn đối thủ đầu tiên.
- `reference/local/lord-scripts/script/campaign/_narrative/wh3_narrative_shared_chains.lua`:
  chuỗi hướng dẫn chung.
- `reference/local/lord-scripts/script/campaign/_narrative/races/wh3_narrative_cathay.lua`:
  sáu mission cơ chế Cathay.
- `reference/local/lord-scripts/script/campaign/main_warhammer/victory_objectives.lua`:
  điều kiện thắng và fallback.
- `reference/local/lord-scripts/script/campaign/wh3_main_legendary_characters.lua`:
  điều kiện hero và hàm chọn mission.
- `reference/local/lord-vanilla/db/effect_bundles_to_effects_junctions_tables/data__.tsv`:
  bonus thắng Order.

Hướng triển khai phù hợp nếu mở rộng: thêm Short/Long Victory theo Long Vi và
Khuresh; xây chuỗi Moon Empress riêng; bổ sung mapping Taoyan; sau đó kiểm thử
new campaign và load save riêng. Chưa triển khai các thay đổi này trong lần audit.
