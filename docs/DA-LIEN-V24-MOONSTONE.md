# Da Lien v24 — Crimson Moonstone

03/11/2026: người dùng yêu cầu tích hợp magic item đã đề xuất. Đã build/deploy
private v24 thay v23; launcher v24 bật/v23 tắt, có backup và hash khớp.

Pack: `build/huyen-ve-v24-da-lien-moonstone/mc_huyen_ve_v24_da_lien_moonstone.pack`.
SHA256: `ed8618f50384160c873dc1dedace334d63a579590fa2a7ee1eeb443c06d21f74`.

## Item

**Crimson Moonstone**, Arcane Item, chỉ subtype `mc_da_lien` sử dụng. Viên ngọc
đỏ trước ngực là ý tưởng ngoại hình; model/texture hiện tại giữ nguyên. UI dùng
icon Gem of Blood native (đổi tại v25 r4 theo yêu cầu người dùng) đã kiểm tra tồn tại; chỉ tham chiếu artwork, không lấy
hiệu ứng hoặc cơ chế Undead của item gốc.

- +5 sức chứa dự trữ Winds of Magic cho quân đoàn chứa Da Lien.
- +5% ward save cho Da Lien.
- **Moonlit Renewal**: bound heal, 1 lần/trận, không tốn Winds, không overcast.
  Giữ phạm vi cast 200m, vùng 35m, tối đa 4 đơn vị bạn, thời lượng 7 giây và heal
  phase native Earth Blood; không hồi sinh lính và không tăng healing cap.

Ability riêng chỉ đổi key, unique ID và số lần dùng từ native bound Earth Blood.
Phép Earth Blood trong cây skill vẫn độc lập. Item enable effect là đường duy nhất
bật Moonlit Renewal: không tự cấp qua skill hoặc để ability luôn bật trên unit.
Các ô unique, spell mastery, resistance và spell kit v23 không thay đổi.

## Nhận đồ và Custom Battle

Campaign load/faction turn: sau callback spawn v20 và skill migration v23, script
đợi Da Lien đang hoạt động rồi cấp và equip một lần. Áp dụng cả Hero đã có trên
save test; Da Lien bị thương thì chờ hồi phục. Script kiểm tra cả ancillary pool,
xác nhận item tồn tại sau grant rồi mới lưu marker. Nếu ngọc đã nằm trong kho,
script không tạo thêm hoặc ép equip. Không tự tạo Hero hay sửa trực tiếp save.

Sau khi người chơi tháo ngọc, các lần load/turn sau không tự equip lại. Các cờ
unique_to_world/unique_to_faction đều false theo native donor và hotfix re-equip
của Huyen Ve; whitelist subtype kiểm soát người dùng item. Không random drop,
không chuyển sang Hero khác, không bị trộm/phá; swap delay bằng 0.

Custom Battle → Grand Cathay → Heroes → Da Lien → chọn **Crimson Moonstone** ở
trang bị Arcane Item. Item có native character-item link riêng; không thay preset
spell hoặc chiếm slot item của Huyen Ve.

## Kiểm tra

- 14 payload thêm mới; mọi payload v23 byte-identical. Model/portrait/skill tree,
  tỉnh/startpos, Huyen Ve và các script cũ giữ nguyên.
- Roundtrip DB/loc qua RPFM đạt. Không có lỗi chặn mới; 6 cảnh báo enum/reference
  metadata của schema được ghi riêng, không bị coi là reference gameplay đã mất.
- Validator độc lập kiểm tra ba effect, chỉ Da Lien được equip, cờ re-equip,
  item-only ability gate, một lần dùng/zero Winds, native heal không hồi sinh,
  Custom Battle link và sự tách biệt với spell Earth Blood học được.
- Deploy đọc/ghi/đọc lại launcher, giữ nguyên entry khác và pack v23; backup:
  `build/huyen-ve-deployment/v24-20261103-063211/20190104-moddata.dat`.

**Runtime chưa xác nhận:** cần kiểm tra ngọc được cấp đúng một lần trên save cũ,
tên/icon/tooltip, +5 reserve/+5 ward, chọn item trong Custom Battle, cast heal đúng
1 lần, tháo ngọc mất ability và equip lại nhận đủ effect; save/load sau khi tháo
không tự equip/cấp lại. Cần kiểm tra heal/mastery/cap thực tế trong battle.

API grant được đối chiếu với script native và
[tài liệu WH3 episodic scripting](https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html#function:episodic_scripting:force_add_ancillary).
`faction:ancillary_exists` được tham chiếu từ script native Sword of Khaine.

Source: `src/campaign/da-lien-equipment.json`,
`src/script/campaign/mod/mc_da_lien_crimson_moonstone.lua`.
Build/validate/deploy helpers: `tools/Build-Da-Lien-Moonstone-Test.py`,
`tools/Validate-Da-Lien-Moonstone-Test.py`, `tools/Deploy-Da-Lien-Moonstone-Test.py`.
Báo cáo: `pack-validation.json`, `item-regression.json`, `diagnostics-review.json`,
`deployment-report.json` trong `build/huyen-ve-v24-da-lien-moonstone/`.
