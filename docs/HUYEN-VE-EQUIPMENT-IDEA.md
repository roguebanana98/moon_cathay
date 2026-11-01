# Huyen Ve — đề xuất bộ trang bị và nhiệm vụ

Ngày: 02/11/2026. Trang bị đã được người dùng yêu cầu triển khai vào v13 để test;
chuỗi nhiệm vụ dưới đây chưa triển khai. Xem [trạng thái trang bị](HUYEN-VE-EQUIPMENT.md).

Đã kiểm tra khả thi ở mức dữ liệu/script: xem
[báo cáo kỹ thuật](HUYEN-VE-EQUIPMENT-FEASIBILITY.md). Chưa kiểm thử runtime.

## Cơ sở tham khảo

Đã đọc `reference/local/lord-scripts/script/campaign/main_warhammer/wh_quests.lua`,
localization nhiệm vụ trong `reference/local/vanilla/text/db/missions__.loc.tsv`,
script trận Dragon's Fang tại
`reference/local/lord-scripts/script/battle/quest_battles/yuan_bo/battle_script.lua`,
DB ancillary và ancillary set. Các mẫu được chọn:

- Dragon's Fang: điều tra dịch bệnh và dấu vết Chaos; trận đánh có phản đồ Cathay,
  alchemist và nhiều đợt quân Nurgle. Lấy cảm hứng từ điều tra → phát hiện phản đồ
  → trận đánh có diễn biến, không sao chép nội dung hay coi đây là quest Huyen Ve.
- Storm Wind Coronal: câu chuyện thu hồi bảo vật gắn với Snake Gate.
- Armour of the Dragon's Gaze: thu hồi ngọc có năng lượng huyền bí để làm giáp.
  Flavor text của giáp liên hệ trực tiếp với ánh nhìn của Moon Empress.
- Grombrindal: bốn trang bị quest khác nhau được khai báo cho một Lord.
- Silver Seal/Ghal Maraz: cấu trúc điều tra, chuẩn bị, vượt thử thách rồi nhận
  bảo vật. Nguồn chính thức mô tả chuỗi lịch sử của Warhammer I:
  https://wiki.totalwar.com/w/Karl_Franz_Quests
  Không coi các bước lịch sử đó là điều kiện chính xác của WH3 hiện tại.

## Chủ đề đề xuất

Tên bộ: **Bảo Khí Trấn Thủ Long Vi**.
Tên chuỗi: **Mật Lệnh Phương Nam**.

Một đoàn vận chuyển bảo khí bị đánh cướp trên đường tới Long Vi. Từng dấu vết
cho thấy có người bên trong tiết lộ lộ trình. Huyen Ve vừa khôi phục quyền lực
trấn thủ, vừa phát hiện kẻ phản bội định dùng tuyến tiếp tế để đưa quân Chaos
vào vùng đất này. Mỗi món đến từ một bước câu chuyện khác nhau: vật được trao,
giáp được phục hồi, ấn được tìm lại, pháp khí được thanh tẩy và kiếm được thu hồi.

Nhân vật, bảo khí, sắc lệnh và sự kiện này đều là sáng tác cho mod. Không gán
cho Huyen Ve địa vị thành viên hoàng tộc rồng. Không đưa quốc gia Việt Nam có
thật vào canon. Thẩm mỹ Việt nằm ở ngọc bội, ấn trấn thủ, họa tiết đồng, sóng
nước và bông lúa; giáp Sơn Văn vẫn hòa với ngôn ngữ thiết kế Cathay.

## Năm món, năm ô độc lập

Các cấp dưới đây là cấp hiển thị dự kiến; chưa chuyển sang rank nội bộ.
Chỉ mở chương tiếp theo khi đã nhận món trước và đạt cấp yêu cầu.

| Thứ tự/cấp | Món và ô | Vai trò dự kiến |
|---|---|---|
| 1 / cấp 6 | Ngọc Bội Nguyệt Ảnh — Talisman | +5% ward save, +10% spell resistance; bảo vệ cá nhân |
| 2 / cấp 10 | Giáp Sơn Văn Long Vi — Armour | +25 armour, +5 melee defence; giữ tuyến trước |
| 3 / cấp 14 | Ấn Trấn Thủ — Enchanted Item | Aura +6 leadership trong 35m; +2 control tại province sở hữu nơi Lord hiện diện |
| 4 / cấp 18 | Nguyệt Đăng — Arcane Item | +15% power recharge, -10% spell cooldown; hỗ trợ bộ phép sẵn có |
| 5 / cấp 22 | Kiếm Trấn Dạ — Weapon | +8 melee attack, +20% weapon strength, magical attacks; active Phá Tà gây Silence một caster địch trong 15s, dự kiến 2 lần/trận |

Các số là điểm khởi đầu để cân bằng. Hiệu ứng Silence, aura, giới hạn sử dụng,
giảm cooldown và set bonus cần đối chiếu effect/ability hợp lệ trước khi triển
khai. Không hứa đã có API/effect phù hợp chỉ từ bản idea này.

Không thêm phép hồi máu miễn phí vì Lord đã có Earth Blood; không nhân đôi
Spirit Leech hoặc The Enfeebling Foe, không sao chép execution của Yuan Bo.
Bonus đủ bộ đề xuất: +5% ward save cá nhân, chỉ hoạt động khi trang bị cả năm.
Chưa quyết định khóa vĩnh viễn trang bị, không cho chuyển hay cách xử lý mất đồ.

## Năm chương nhiệm vụ

### 1. Dấu Ngọc Trong Đêm → Ngọc Bội Nguyệt Ảnh

Một mật sứ mang tin về đoàn vận chuyển mất tích tới Long Vi. Huyen Ve phải ổn
định địa bàn trước khi được giao vật nhận diện của người giữ mật lệnh.
Mục tiêu: sở hữu Long Vi, để Huyen Ve thắng hai trận sau khi nhiệm vụ bắt đầu.
Trao ngọc bội sau chiến công thứ hai. Không cần quest battle riêng ở chương mở đầu.

### 2. Lửa Tắt Bên Lò Rèn → Giáp Sơn Văn Long Vi

Thợ rèn và bản giáp dành cho trấn thủ bị thất lạc trong vụ cướp. Giải cứu họ
đồng thời giành lại nguyên liệu để hoàn thiện giáp.
Mục tiêu: Huyen Ve thắng một trận đánh quân cướp do nhiệm vụ tạo gần vùng Long Vi;
sau đó trả 2.000 vàng để phục hồi giáp. Đánh trận campaign thông thường, không
buộc chờ AI công thành, không cần xây một công trình riêng chỉ để làm quest.

### 3. Kẻ Mang Ấn Giả → Ấn Trấn Thủ

Lệnh điều quân giả đang làm rỗng các trạm phòng thủ. Một viên quan thuộc đoàn
vận chuyển đã thay ấn thật và bán lộ trình cho kẻ thù.
Mục tiêu cập nhật theo người dùng: đưa một Hero tới địa điểm điều tra được đánh
dấu để mở quest battle riêng. Huyen Ve thắng trận phản đồ và viện quân bảo vệ
viên quan mang ấn để nhận Ấn Trấn Thủ. Không tạo đội quân mục tiêu trên campaign,
tránh bị faction khác tiêu diệt. Hero chỉ cần tới vị trí, không phải làm action
có xác suất; quest battle có thể teleport và thử lại nếu thua.

### 4. Đèn Tắt Dưới Trăng → Nguyệt Đăng

Pháp khí dẫn đường và trấn an người hành quân đã bị kẻ phản bội làm ô uế.
Mục tiêu: thắng quest battle bảo vệ người thực hiện nghi thức; chống hai đợt
tấn công rồi diệt pháp sư duy trì sự ô uế. Nghi thức khoảng 5 phút, sau đó vẫn
phải kết thúc trận thắng. Dùng đơn vị và map hợp lệ của game; chưa chọn cụ thể.

### 5. Mật Lệnh Cuối Cùng → Kiếm Trấn Dạ

Huyen Ve tìm được nơi giấu món cuối cùng: thanh kiếm dành cho người trấn thủ.
Quân phản đồ dùng nó làm mồi nhử và chuẩn bị mở đường cho chủ nhân Chaos.
Mục tiêu: thắng quest battle hai giai đoạn. Đầu tiên đánh tan quân phản đồ Cathay,
sau đó chặn viện quân Chaos và hạ pháp sư chủ mưu. Có thể vô hiệu hóa hai nguồn
tiếp sức để làm yếu đợt cuối; đây là mục tiêu phụ giúp trận dễ hơn, không làm
người chơi bị kẹt vì bỏ lỡ. Nhận kiếm khi toàn bộ trận đánh kết thúc thắng.

## Nguyên tắc chơi và triển khai

- Năm phần thưởng riêng, chỉ nhận từng món sau khi hoàn thành chương tương ứng.
- Ba quest battle có kịch bản ở chương 3–5; chương 3 mở sau bước Hero điều tra.
- Đội quân nhiệm vụ sinh theo script để không phụ thuộc một faction mục tiêu
  phải sống đến cuối game. Không dựa vào roster Naga chưa có trong mod.
- Không ép chiến tranh với một faction Cathay chính có thể đang là đồng minh.
- Quest battle có teleport, thua có thể đánh lại, không hết hạn. Chiến lợi phẩm
  trao đúng một lần và giới hạn đúng subtype Huyen Ve.
- Lưu trạng thái từng chương; kiểm tra lại khi load save hoặc Lord hồi phục.
  Nếu load save đã vượt mốc cấp, mở chương hợp lệ tiếp theo, không tự trao đồ.
- Đổi Long Vi ownership do MCT hoặc chiến tranh cần được xét rõ khi triển khai;
  thiết kế hiện tại cố ý yêu cầu người trấn thủ lấy lại Long Vi ở chương đầu.

Bước tiếp theo sau khi người dùng duyệt: chốt số món, tên, mốc cấp và mức sức
mạnh; sau đó làm từng mission và kiểm thử nhận đồ, equip, thua/đánh lại, save/load.
