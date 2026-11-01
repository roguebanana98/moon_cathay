# Huyen Ve — bộ trang bị v14

Ngày 02/11/2026. Đã tạo định nghĩa 5 món, 3 ability riêng, bonus đủ bộ và nối
trang bị vào nhân vật Huyen Ve trong Custom Battle theo cơ chế native.
Build/kiểm tra tĩnh đạt; chưa kiểm thử hiển thị hoặc combat trong game.

Pack tích hợp: `build/huyen-ve-equipment/mc_huyen_ve_v14_native_icons.pack`.
Thay v12 hoặc các bản tích hợp cũ bằng bản này; không bật đồng thời.
Không có bước tự động cài vào game hoặc Workshop.

## Trang bị

| Món | Ô | Hiệu ứng |
|---|---|---|
| Ngọc Bội Nguyệt Ảnh | Talisman | +5% ward save; +10% spell resistance |
| Giáp Sơn Văn Long Vi | Armour | +25 armour; +5 melee defence |
| Ấn Trấn Thủ | Enchanted Item | +2 control tại owned province nơi Lord hiện diện; passive +6 leadership cho quân sở hữu trong 35m |
| Nguyệt Đăng | Arcane Item | -10% spell cooldown; passive +15% Winds of Magic power recharge trong battle |
| Kiếm Trấn Dạ | Weapon | +8 melee attack; +20% weapon strength; magical attacks; Phá Tà |

**Phá Tà:** active nhắm một đơn vị địch trong 60m, áp attribute silenced 15 giây,
2 lần/trận, cooldown 120 giây, không tốn Winds. Mục tiêu hữu ích là caster.
Không có hard filter chỉ cho caster: có thể lãng phí lên đơn vị không có phép.
Ability không gây damage, trói chân hoặc áp stat debuff khác của donor.

**Bonus đủ bộ:** +5% ward save cá nhân khi trang bị đủ năm món qua ancillary set
gốc của game. Cần kiểm tra cả campaign sau khi có quest và Custom Battle; chưa
khẳng định native set bonus được áp dụng ở Custom Battle trước khi thử runtime.

Aura, recharge và Phá Tà được gắn với land unit nhưng đều
requires_effect_enabling=true; chỉ effect từ món tương ứng mới bật ability.
Không cấp chúng bằng skill preset và không chỉnh stat nền của unit.
Aura không mang điều kiện tự tắt khi morale thấp của mẫu Ring of Grimnir.
Nguyệt Đăng dùng một passive key riêng, không thay hoặc cấp lại Arcane Conduit.
Power recharge tác động nguồn Winds chung trong battle; cần kiểm tra cộng dồn
với Arcane Conduit hiện có và quân đồng minh.

## Cách kiểm tra Custom Battle

1. Thay bản submod cũ bằng v14 rồi restart game.
2. Tạo army setup mới, chọn Grand Cathay và thêm
   **Huyen Ve, Warden of Long Vi**. Nếu dùng preset cũ, xóa Lord rồi thêm lại.
3. Chọn Lord và mở phần trang bị/item upgrades. Định nghĩa có đủ năm link
   native battle_set_piece_armies_characters_items, giống cách Yuan Bo có
   Dragon's Fang/Armour of the Dragon's Gaze.
4. Kiểm tra năm món xuất hiện; bật/tắt từng món để xem thay đổi. Nếu UI không
   cho chọn hoặc không áp dụng, ghi lại màn hình và không coi cấu hình tĩnh là
   xác nhận đã mặc được đồ. Chưa thêm phương án mô phỏng bằng hidden skill.

Đề nghị test không có item trước, rồi từng item, cuối cùng đủ bộ:

- Giáp/ngọc/kiếm: so chênh lệch stat và resistance với cùng cấu hình skill.
  Skill Moonblade và các buff v11 vẫn cộng dồn như trước.
- Ấn: đưa bộ binh vào/ra 35m khi trạng thái combat khác giữ nguyên, xem +6
  leadership; +2 control chỉ có ý nghĩa trên campaign, không kiểm tra trong battle.
- Đèn: so cooldown cùng một phép giữa hai setup và tốc độ power recharge trong
  cùng điều kiện; kiểm tra cả các phép overcast đã nâng cấp nếu sử dụng.
- Kiếm: thử Phá Tà lên caster địch, quan sát Silence hết sau 15 giây, cooldown
  120 giây và tối đa hai lần dùng. Tháo kiếm phải mất Phá Tà.
- Đủ bộ: so với cùng setup thiếu một món, quan sát bonus +5 ward save; các buff
  conditional chống Chaos phải giữ cùng điều kiện khi so sánh.

## Campaign, nhiệm vụ và ngoại hình

Định nghĩa item đã ở trong pack, giới hạn đúng subtype Huyen Ve, không rơi ngẫu
nhiên, không được trộm/hủy/chuyển cho Lord khác. **Campaign chưa tự nhận đồ**:
không thêm script grant, không thêm quest UI với lời hứa unlock chưa tồn tại.
Năm nhiệm vụ nhận đồ là bước tiếp theo.

Thiết kế chương 3 được cập nhật theo người dùng: Hero điều tra → mở quest battle
riêng → thắng nhận Ấn, không spawn quân phản đồ trên campaign. Chương 2 vẫn chưa
đổi sang quest battle vì chưa có yêu cầu chốt thay đổi đó.

V14 dùng icon có sẵn của game theo yêu cầu người dùng. Năm món tham chiếu trực
tiếp icon loại trang bị native; ba ability dùng icon native tương ứng. Ba icon
trạng thái theo phase ID là bản sao nguyên byte từ game trong build private,
không phải hình mới. Bộ icon tự vẽ cũ không được đưa vào pack và không còn
được tạo trong quy trình build.
Trang bị chưa thay model 3D, kiếm/giáp ngoài trận hoặc portrait của Lord.

## Tái lập và bằng chứng

- Source thông số: `src/campaign/huyen-ve-equipment.json`.
- Icon native tham chiếu từ ui2.pack; icon phase lấy từ ui.pack, trích xuất riêng
  vào `reference/local/huyen-ve-native-icons/`. Artwork cũ trong authored không dùng.
- Build: `tools/Build-Huyen-Ve-Equipment.ps1`; `-Rebuild` chỉ ghi lại artifact
  v14 trong build, không đụng game/Workshop.
- Validator: Python cấu hình với `tools/Validate-Huyen-Ve-Equipment.py`.
- Manifest: `build/huyen-ve-equipment/manifest.json`.

22 payload mới (18 DB + 1 loc + 3 PNG native alias). Toàn bộ payload v12, bao gồm startpos,
province, kỹ năng, spell progression, name fix và model, giữ nguyên từng byte.
RPFM import/extract roundtrip đạt. New-payload diagnostics chỉ còn cảnh báo enum
reference metadata (bonus_value_id, attribute_type, how, effect_type và một số
field animation/voice); không có unresolved record/path mới. Không có bảng
ownership bị cấm hoặc chỉnh record vanilla. Hash dependency đã khớp baseline.

V14 chỉ đổi icon so với v13: đối chiếu tất cả giá trị DB xác nhận chỉ ui_icon
và icon_name thay đổi; gameplay/loc giữ nguyên. Header DB do RPFM sinh có thể
khác khi build lại, không phải thay đổi chỉ số. Chưa kiểm thử runtime v14.
