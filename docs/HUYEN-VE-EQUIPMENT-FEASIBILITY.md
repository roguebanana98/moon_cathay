# Khả thi: Bảo Khí Trấn Thủ Long Vi

Ngày kiểm tra: 02/11/2026. Kết luận: **cả năm chương và năm món đều có đường
triển khai bằng hệ thống game hiện có; chưa chứng minh hoạt động bằng runtime**.
Hai quest battle là phần tốn công nhất. Chưa tạo trang bị, mission hay pack mới.

Đã chạy `tools/Audit-Equipment-Quest-Feasibility.py`: 16 kiểm tra bằng chứng tĩnh
đạt. Chi tiết và hash từng nguồn nằm trong `reports/equipment-quest-feasibility.json`.
Đây là bằng chứng về khả năng của hệ thống, không phải test chức năng của mod.

## Đánh giá từng chương

| Chương | Khả thi | Cách làm có cơ sở trong game | Điều kiện phải xử lý |
|---|---|---|---|
| 1: Long Vi + thắng 2 trận | Cao | Mission có objective SCRIPTED, listener CharacterCompletedBattle, kiểm tra subtype/faction và chiến thắng, bộ đếm saved value | Chỉ tính sau khi phát nhiệm vụ; khử đếm lặp cùng battle; kiểm tra vẫn sở hữu Long Vi khi hoàn thành |
| 2: diệt quân cướp + trả 2.000 vàng | Cao, có quản lý quân mục tiêu | create_force/create_force_with_general hoặc invasion_manager; ghi CQI quân mục tiêu; sau chiến thắng phát dilemma sửa giáp | Vị trí spawn hợp lệ trên IEE; trả tiền đúng một lần; thiếu tiền được quay lại; không dùng gold reward âm rồi vô tình cho treasury âm |
| 3: Hero điều tra + hạ phản đồ | Cao | Interactive Marker Manager có AreaEntered và trả character; lọc Hero của faction, hoàn thành bước điều tra rồi tạo quân | Đánh dấu phải đi tới được; Hero đang embed có thể không kích hoạt như Hero độc lập, cần hướng dẫn tách Hero; không cho Lord thường hoàn thành thay |
| 4: bảo vệ nghi lễ | Khả thi, cần quest battle riêng | Battle set-piece DB, script điều khiển quân đồng minh/địch, timer, viện quân và điều kiện thắng/thua | Chọn map/deployment phù hợp; người làm lễ chết phải thua; hết 5 phút chưa tự thắng nếu chưa diệt địch; ngăn game kết thúc sớm trước viện quân |
| 5: phản đồ rồi Chaos | Khả thi, cần quest battle riêng | Dragon's Fang có mẫu quân Cathay phản đồ và các đợt viện quân Nurgle; bộ quản lý battle có message/timer/trigger thương vong | Trigger đợt sau chỉ chạy một lần; mục tiêu phụ không khóa thắng; chỉ phát kiếm khi campaign nhận thắng mission |

### Đội quân mục tiêu ở chương 2–3

Drycha/Coeddil là ví dụ vanilla tạo đội quân nhiệm vụ trên campaign, điều chỉnh
ngoại giao và xử lý MissionGenerationFailed. IEE startpos có candidate faction
`wh3_main_cth_cathay_qb1`; không bắt buộc thêm một faction mới vào startpos để
nghiên cứu prototype. Tuy nhiên faction QB đó được game dùng chung, **không
được coi là faction riêng độc quyền của mod**.

Phải theo dõi đúng force/leader do nhiệm vụ tạo và chỉ dọn quân đó. Không sao
chép các thao tác kill_all_armies hoặc khóa toàn bộ ngoại giao của faction dùng
chung. Cần kiểm tra script game khác có quản lý/dọn faction đó hay không trước
khi chọn donor cuối cùng. Nếu không cô lập được, có thể thay bước này bằng
scripted encounter/quest battle hoặc thiết kế một faction riêng sau.

Nếu phe thứ ba hạ quân nhiệm vụ: không trao thưởng nhầm cho Huyen Ve; phải có
cách tạo lại mục tiêu hoặc cho người chơi thử lại. Đây là hạng mục triển khai,
không phải giới hạn khiến thiết kế bất khả thi.

## Đánh giá năm món và hiệu ứng

| Món | Kết luận |
|---|---|
| Ngọc Bội | Ward save và spell resistance đã có effect ancillary gốc; có thể đặt +5/+10 với scope cá nhân |
| Giáp Sơn Văn | Armour và melee defence dùng effect stat có sẵn; không cần thêm model để chỉ hoạt động về chỉ số |
| Ấn Trấn Thủ | +2 control dùng scope character_to_province_own giống nhánh skill hiện tại; aura 35m/+6 leadership cần ability passive riêng được trang bị bật/tắt, không dùng buff toàn quân thay cho aura |
| Nguyệt Đăng | -10% cooldown có effect gốc và cả 5 phép hiện tại đều được liên kết; +15% battle power recharge có thể làm qua passive/phase mana_regen_mod, cần kiểm chứng giá trị và cộng dồn |
| Kiếm Trấn Dạ | MA, weapon strength và magical attacks có nền tảng ancillary. Silence có attribute thật và donor single-target active; 15 giây/2 lần là cấu hình riêng cần tạo |

### Những điểm phải diễn đạt chính xác

- Recharge trong battle ảnh hưởng nguồn Winds of Magic dùng chung của phe/quân
  liên quan, không tạo một thanh mana riêng cho Huyen Ve. Không nhầm nó với
  tốc độ tăng magic reserve trên campaign. Lord đã có Arcane Conduit nên phải
  thử cộng dồn, không nhân đôi cùng một key ability.
- `wh2_main_effect_ability_cooldown_spells` liên kết đủ Dragon's Breath,
  Earth Blood, Flame Storm, The Enfeebling Foe và Spirit Leech. Không cần đoán
  hiệu ứng sẽ tự nhận diện composite lore.
- `wh3_main_character_abilities_silence_the_prey` có tên dễ gây hiểu nhầm:
  phase đang đọc thay đổi recharge, không phải donor để khẳng định Silence.
  Donor đúng có `special_ability_phase_attribute_effects -> silenced`, ví dụ
  `wh3_dlc27_character_abilities_the_black_tongue`. Nó có active single-target,
  hai lần dùng; phải tách key, sửa duration và loại các hiệu ứng phụ không muốn.
- Bộ 5 ô weapon/armour/talisman/enchanted_item/arcane_item không tranh ô nhau.
  Huyen Ve hiện kế thừa caster subtype donor. Cần kiểm tra equip cả năm trên UI
  thực tế, không chỉ sự tồn tại của category trong DB.
- Set bonus có bảng gốc ancillary_sets, ancillary_set_ancillary_junctions,
  ancillary_set_effect_junctions. Có thể định nghĩa một bộ gồm năm món và ward
  save, nhưng cần kiểm tra đủ/thiếu/tháo đồ để xác nhận điều kiện kích hoạt.
- Equipping item **không tự đổi kiếm hay giáp trên model 3D**. Icon item và
  ngoại hình model là phần asset riêng; không bắt buộc để quest/chỉ số hoạt động.

## Nối vào UI và campaign

Không cần sửa startpos chỉ để thêm chuỗi nhiệm vụ, cũng không cần thay toàn bộ
`wh_quests.lua` vanilla. Hướng ít xung đột là script riêng dưới
`script/campaign/mod/` + DB có prefix riêng + localization/icon + battle script.

Các bảng chính cần có:

- Item: ancillaries, ancillary_info, ancillary_types nếu cần icon mới,
  ancillaries_included_agent_subtypes, ancillary_to_effects, các bảng set.
- UI quest: character_ancillary_quest_ui_details có subtype, ancillary, rank,
  instant và is_quest_battle. Script native đọc rank từ bảng này.
- Mission: missions, scripted_objectives/loc khi dùng objective tùy chỉnh;
  có thể tạo mục tiêu và phần thưởng qua mission_manager, không nhất thiết
  phải dùng toàn bộ campaign-director chain DB.
- Battle: battle_set_pieces, battle_set_piece_armies, army/battle junctions,
  unit/character junctions và battle script riêng. Chỉ thêm bảng thật sự cần,
  không clone toàn bộ donor theo quán tính.
- Ability: unit_abilities, unit_special_abilities, special_ability_phases,
  các bảng junction/stat/attribute và effect grant tương ứng cho aura/Silence.

Native rank listener mở từng quest độc lập. Chỉ thêm năm dòng rank không đủ
để đảm bảo nhận lần lượt: cần bộ quản lý tiến độ riêng chặn chương sau cho tới
khi chương trước đã hoàn thành. UI quest và cấp hiển thị phải khớp điều kiện
thực; dùng quy ước rank nội bộ đã kiểm chứng của project khi triển khai.

## Quest battle, bản đồ và teleport

Game đã có set-piece chứa battlefield_folder, deployment/catchment, script,
teleport_cost và cờ autoresolve. Dragon's Fang dùng map
`wh3_main_macro_nur_realm_01`/`catchment_35` và có nhiều enemy armies. Điều này
chứng minh hạ tầng phù hợp cho trận nhiều giai đoạn; **chưa chốt map đó cho
Long Vi**, vì thẩm mỹ và deployment có thể không phù hợp.

Có thể tái dùng map game bằng tham chiếu, viết DB/script riêng mà không xây
terrain từ đầu. Cần kiểm tra thật vùng deploy/entry/đường đi trước khi chốt.
Nếu cần địa hình/công trình/nghi lễ mới đặt cố định trên map, có thể phải làm
BMD/map layer bằng công cụ Assembly Kit. Máy có binaries Assembly Kit, nhưng
chưa chạy xác minh quy trình export map trong lần audit này. Cinematic lồng
tiếng và map mới không phải điều kiện bắt buộc cho bản chơi được đầu tiên.

Teleport, khóa đúng Huyen Ve tham gia, thua rồi đánh lại và trở về campaign
đều cần kiểm thử với quest battle mới trên `cr_combi_expanded`. Không coi việc
donor hỗ trợ teleport là bằng chứng bản mod mới đã làm được tất cả.

## Save/load, tính duy nhất và trường hợp kẹt

Lưu stage, mission_issued, battle count, force CQI và reward_granted bằng saved
values. Không lưu character/military-force interface trực tiếp. Khi load:

1. Đọc và khôi phục listener/marker cho chương đang chạy.
2. Xác nhận Huyen Ve subtype còn hợp lệ, đang bị thương thì chờ trở lại.
3. Xác nhận force mục tiêu còn tồn tại; xử lý tạo lại nếu mất.
4. Nếu chưa có tiến độ mà Lord đã cấp cao, chỉ mở chương đầu đủ điều kiện.
5. Trao ancillary đúng một lần, đúng Huyen Ve; tách bước trao thưởng khỏi
   callback có thể chạy lặp và xử lý trường hợp Lord chưa có interface hợp lệ.

Có cờ item gốc randomly_dropped/can_be_stolen/can_be_destroyed/transferrable để
tham khảo chính sách đồ quest; Dragon's Fang không drop/trộm/hủy. Cờ này không
thay thế reward_granted trong script. Chưa chọn cách khóa trang bị vĩnh viễn.

Nếu sử dụng save rất cũ còn Lord Ju Di subtype generic, đổi tên ở v12 không
chuyển subtype thành Huyen Ve; không tự cấp bộ quest cho generic Lord đó.
Multiplayer cần lượt kiểm chứng riêng về người nhận, event và đồng bộ trạng thái.

## Thứ tự triển khai và tiêu chí đạt

1. Làm chương 1 + ngọc bội để kiểm chứng UI mission → thắng đúng 2 trận → nhận
   đúng một món → equip. Thử save/load giữa hai trận và sau nhận thưởng.
2. Làm chương 2–3 để kiểm chứng spawn/marker/thanh toán/tạo lại mục tiêu.
3. Làm một quest battle tối giản trên map có sẵn: Huyen Ve vào bằng quân campaign,
   thắng/thua, quay về, nhận thưởng đúng một lần; sau đó mở rộng nghi lễ chương 4.
4. Làm trận nhiều giai đoạn chương 5, ability kiếm, aura ấn và bonus đủ bộ.
5. Kiểm tra load save cấp cao, wounded/respawn, mất Long Vi, thiếu tiền, quân địch
   bị phe khác hạ, tháo item, thiếu từng món, hai lần dùng Silence và overcast.

Chưa có bước nào ở trên được đánh dấu đã chạy trong game. Kết quả lần này là
đường triển khai có bằng chứng cụ thể và danh sách điều kiện cần kiểm chứng.
