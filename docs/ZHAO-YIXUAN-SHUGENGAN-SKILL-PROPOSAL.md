# Zhao Yixuan — đề xuất pháp sư cơ động theo nền Shugengan

Ngày: 26/11/2026.

**Trạng thái hiện tại 27/11/2026: v37 ĐÃ CÀI/BẬT, ĐANG CHỜ NGƯỜI DÙNG TEST.**

V37 kế thừa thiết kế v36 và sửa mục Zhao/phép trùng trong Custom Battle; xem
`docs/ZHAO-CUSTOM-BATTLE-DUPLICATES-V37.md`. Model campaign đã kiểm tra chuỗi
tham chiếu trong pack cài đặt và các mod đang bật, chưa xác nhận hình trong game.
Bản vá ẩn Onyx riêng Moon chạy cùng v37. Các ghi chú v36 dưới đây là lịch sử triển khai.

Cập nhật triển khai 26/11/2026: người dùng cung cấp v35 và yêu cầu dùng làm nền,
áp dụng bản thiết kế này cùng reskin năm loại Jade đã duyệt. Đã build/cài
`mc_moonshadow_heroes_v36_zhao_jade.pack`, SHA256
`2584f38b44cf2e9d8f9f4feba87a809cfbfc187dd17f71d638292c2d905087e3`.
V35 gốc giữ nguyên. Bản mới có 54 node hiển thị/68 node gồm ẩn, 17 điểm nhánh
phép, sáu phép đúng bảng dưới, một Power of Yin và bound chọn một trong bốn.
Chỉ số đi bộ đúng thiết kế. Mounted dùng chênh lệch Shugengan: horse bonusHP4764,
Longma5364; giáp60, MA45/MD35; charge40/60; sát thương210+90AP và240+100AP,
giữ movement native, mở ở cấp hiển thị5/15. Không cộng run4.2 lên mount.
Foot body/sword/Yuan Bo profiles giữ nguyên. Kiếm mounted hand_right riêng đã
xuất/đọc lại bốn LOD; kiểm tra15clip/45mẫu và render riêng, không xuất montage.
Độ khớp rider Longma khi bay/clipping/transition vẫn cần kiểm chứng trong game.

Có script migration phạm vi Zhao/Moon: native one-time skill reset, cleanup grant
cũ/Command Seal, giữ XP và traits, foundation hai phép/mount đạt cấp, bất tử theo
skill Immortality đã mua. Boundary tests passed; engine refunds và save migration
chưa được xác nhận runtime. RPFM DB/loc roundtrip, donor/graph/gate/hash checks
passed;168cảnhbáo thiếu định nghĩa tham chiếu schema/cache còn lại, không có loại
diagnostic khác. Launcher chưa sửa. Hướng dẫn/báo cáo: `dist/moon-v36-zhao-jade`
và `build/moon-v36-zhao-jade`. Không push Git hoặc thêm LFS trong đợt triển khai.
Những ghi chú chờ pack, mount chưa triển khai và trạng thái save-only bên dưới là
lịch sử thiết kế, được cập nhật triển khai này thay thế.

Cập nhật 26/11/2026 sau khi lưu: người dùng đã yêu cầu triển khai bản này vào mod.
Đã kiểm tra thư viện Steam ổ H, project/build, launcher và thư mục backup được
kiểm tra nhưng chưa tìm thấy pack nền v34 hoặc bản mới hơn. Đang chờ vị trí/bản
copy pack nền để giữ nguyên các nhân vật và ngoại hình đã duyệt. Chưa build/deploy.
Phạm vi triển khai đã được yêu cầu; không cần hỏi lại phê duyệt thiết kế chỉ vì
đang thiếu file nền. Các câu "chưa yêu cầu triển khai" bên dưới mô tả mốc lưu ban đầu.

Người dùng yêu cầu lưu bản xem trước, không yêu cầu triển khai. Tài liệu này
không xác nhận đã build, deploy, thay chỉ số/cây kỹ năng, thêm mount hoặc kiểm thử
trong game. V34 đã ghi nhận trước đó vẫn giữ chỉ số và cây WWD; việc lưu tài liệu
không thay đổi trạng thái đó. Xem `ZHAO-YUAN-BO-INTEGRATION-V34.md`.

## 1. Vai trò và phạm vi

- Lord thường, tuyển lặp lại; vai trò pháp sư kiêm chỉ huy tương đương Shugengan.
- Cận chiến yếu hơn Shugengan, chạy nhanh hơn để chọn vị trí niệm phép.
- Giữ ngoại hình, kiếm và animation Yuan Bo đã duyệt; không lấy chỉ số Yuan Bo.
- Dùng nền Shugengan Yin cho nhánh đỏ, xanh, kỹ năng chung và kỹ năng riêng.
- Thay cây WWD bằng cây mới nếu sau này được yêu cầu triển khai, không cộng hai cây.
- Tên hiển thị dự kiến English ASCII, dùng icon/VFX và cơ chế phép native.
- Đây là mục tiêu cân bằng; chưa có bằng chứng playtest về sức mạnh tương đương.

## 2. Nguồn đối chiếu và giới hạn

Đã đọc game 9.0.5.0, Steam build 26810549 tại
`H:\SteamLibrary\steamapps\common\Total War WARHAMMER III` và WWD tại
`H:\SteamLibrary\steamapps\workshop\content\1142710\2789903784\DEER24Cathay.pack`.

- SHA256 WWD đang có: `68db9e4881bac0e41b7bd3ece71aaaf39be90053d9242abe15cd59dec287f528`.
- SHA256 nguồn WWD ghi khi làm v34: `c5f411df984a0241d0dc507255a28e596a66ea5df585710ef5d61794fb60d304`.
- SHA256 native `db.pack`: `73fe248f0983720d20638d5dfe6ba20e5207229a1a4d67c9b86a3bfe1b7d7626`.
- WWD hiện tại khác nguồn v34; chưa có pack v34 để đối chiếu trực tiếp trên máy này.
- Bản trích xuất/báo cáo local, không đưa vào Git:
  `reference/local/zhao-shugengan-comparison-20261126/comparison.json`.

WWD hiện có: bonus HP 5500, giáp 70, leadership 80, melee attack 50,
melee defence 65, charge 40, weapon damage 280 thường +120 AP, kháng đạn 0%,
Harmony profile 200%, giá tuyển 1500/upkeep 375/CB base 1500.
Các số này mô tả nguồn WWD hiện tại, không phải kết quả kiểm chứng pack v34 cũ.

## 3. Chỉ số đề xuất — đi bộ, chưa có skill/trang bị/buff

| Chỉ số | Shugengan native | Zhao đề xuất |
|---|---:|---:|
| Bonus HP trong DB | 4360 | 4160 |
| Giáp | 30 | 20 |
| Leadership | 70 | 70 |
| Melee attack | 55 | 45 |
| Melee defence | 40 | 35 |
| Charge bonus | 30 | 20 |
| Sát thương thường | 280 | 210 |
| Sát thương AP | 120 | 90 |
| Tổng weapon strength | 400 | 300 |
| Tốc độ chạy trong DB | 3.8 | 4.2 |
| Khối lượng | 800 | 800 |
| Kháng đạn | 15% | 15% |
| Kháng vật lý / ward save nền | 0% / 0% | 0% / 0% |
| Spell mastery nền | 100% | 100% |
| Harmony amplification profile | 150% | 150% |
| Giá tuyển campaign | 1000 | 1000 |
| Upkeep | 300 | 300 |
| Giá cơ bản Custom Battle | 700 | 700 |

`bonus_hit_points` không phải HP thẻ cuối cùng ở mọi unit size. Hai entity đi bộ
đối chiếu có thêm 8 HP nền. Giá CB chưa tính lựa chọn phép/mount. Giữ tầm đánh,
khối lượng và khả năng va chạm theo nền Shugengan; không thêm né đòn ẩn hoặc
xuyên đội hình. Zhao nhanh hơn khoảng 10.5%, weapon strength thấp hơn 25%.
Animation có thể ảnh hưởng hiệu quả cận chiến, nên bảng chỉ số không chứng minh
hiệu quả chiến đấu thực tế. Không tăng hành quân campaign theo tốc độ battle.

## 4. Cấu trúc cây

| Nhánh | Số ô hiển thị |
|---|---:|
| Phép chính và hỗ trợ phép | 11 |
| Kỹ năng riêng Mooncourt | 6 |
| Đỏ — quân đội | 13 |
| Xanh — campaign | 11 |
| Chung và mount | 9 |
| Phép bound phụ, chọn một | 4 |
| Tổng dự kiến | 54 |

Không có nhánh đánh kiếm riêng. Số ô là bố cục thiết kế, chưa phải đồ thị DB
đã build. Cấp dưới đây là cấp Lord hiển thị trong game. Không khóa cấp nghĩa là
vẫn phải mua bằng điểm và đáp ứng tiền đề, không tự nhận miễn phí.

## 5. Phép Moon / nước / lửa

| Chủ đề | Tên đề xuất | Phép native | Vai trò |
|---|---|---|---|
| Moon | Lunar Snare | Storm of Shadows | Làm chậm, giữ khoảng cách |
| Moon | Grasp of the Eclipse | Talons of Night | Sát thương diện rộng cao cấp |
| Nước | Crashing Tide | Tidecall | Sát thương theo hướng |
| Nước | Sea Mist | Fog of the Damned | Debuff hỗ trợ giao chiến |
| Lửa | Ember Bolt | Fireball | Công kích từ xa |
| Lửa | Flameforged Blade | Flaming Sword of Rhuin | Buff công kích |

Giữ thông số, icon, VFX, Winds, cooldown và overcast của nguồn native.
Không có Earth Blood, hồi máu hoặc triệu hồi trong sáu phép chính.
Chỉ một nội tại lore: **Lunar Ascendancy = Power of Yin**; không cộng thêm
Kindleflame/Life Bloom. Không khóa độc quyền nước/lửa.

| Nhóm | Kỹ năng | Điểm tối đa | Tiền đề |
|---|---|---:|---|
| Mở đầu | Ember Bolt | 2 | Không khóa cấp |
| Đầu | Lunar Snare | 2 | Ember Bolt cấp kỹ năng 1 |
| Đầu | Crashing Tide | 2 | Ember Bolt cấp kỹ năng 1 |
| Đầu | Lunar Ascendancy | 1 | Ember Bolt cấp kỹ năng 1 |
| Cầu nối | Evasion | 1 | Tổng 4 điểm trong ba ô nhóm đầu sau Ember Bolt |
| Sau | Grasp of the Eclipse | 2 | Evasion |
| Sau | Sea Mist | 2 | Evasion |
| Sau | Flameforged Blade | 2 | Evasion |
| Sau | Earthing | 1 | Evasion |
| Sau | Magical Reserves | 1 | Evasion |
| Cuối | Arcane Conduit | 1 | Tổng 4 điểm trong năm ô sau Evasion |

Tổng hoàn thiện nhánh phép: **17 điểm**. Khi tuyển, kỹ năng ẩn mở Ember Bolt và
Lunar Snare cơ bản, nhưng các ô nâng cấp vẫn có 0 điểm. Không gán cấp Lord cố
định cho phép cao cấp. Cấu trúc năm ô sau Evasion là điều chỉnh thiết kế, cần
kiểm tra lại liên kết và khả năng đạt gate khi triển khai.

## 6. Sáu kỹ năng riêng Mooncourt

Mỗi ô 1 điểm. Lấy ngân sách hiệu ứng của Shugengan Yin, không thêm melee attack,
weapon strength hoặc hồi máu riêng.

| Kỹ năng | Điều kiện | Hiệu ứng đề xuất |
|---|---|---|
| Mooncourt Defence | Cấp Lord 13 | +20 giáp, +6 melee defence, +15% tốc độ cho bản thân, như donor |
| Threefold Attunement | Mooncourt Defence | +10% spell mastery; -20% cooldown chỉ Lunar Snare và Grasp of the Eclipse |
| Protection of the Mooncourt | Mooncourt Defence | Giữ hiệu ứng bảo hộ và đúng nhóm quân donor Yin |
| Master of the Mooncourt | Mooncourt Defence | Giữ giảm upkeep/thời gian tuyển và đúng nhóm quân donor Yin |
| Resonant Presence | Mooncourt Defence | +50% khuếch đại Harmony theo donor |
| Empowered Mooncaster | Ít nhất 3 trong 4 ô trung gian trên | Giữ gói barrier và năng lực Winds của donor |

Threefold Attunement không giảm cooldown phép nước/lửa, bound hoặc vật phẩm.
Không mở rộng các unit set donor sang toàn roster. Có thể học đủ sáu ô.

Sau khi cả hai mua kỹ năng phòng thủ donor: Shugengan giáp 50/MD 46/MA 55/WS 400;
Zhao giáp 40/MD 41/MA 45/WS 300. Zhao vẫn yếu hơn về cận chiến, giữ ưu thế tốc độ.

## 7. Nhánh đỏ — nền Shugengan

| Nhóm | Kỹ năng | Điểm tối đa | Công dụng |
|---|---|---:|---|
| Mở đầu | Inspiring Presence | 1 | Mở nhóm đầu |
| Đầu | Unyielding | 3 | MA/MD bộ binh |
| Đầu | Sure Aim | 3 | Sát thương/tầm bắn cung nỏ |
| Đầu | Eastern Fires | 3 | Đạn/sát thương súng pháo |
| Đầu | Mighty Charge | 3 | Charge/sức đánh kỵ binh |
| Đầu | Stone Gaze | 3 | Nhóm Compass/Terracotta Sentinel |
| Đầu | Sky Fire | 3 | Các nhóm quân bay native |
| Cầu nối | Rally! | 1 | Tổng 6 điểm trong sáu ô nhóm đầu |
| Sau | Blades of the Bastion | 1 | Bộ binh kỳ cựu |
| Sau | Fast Hands | 1 | Quân tầm xa kỳ cựu |
| Sau | Unified Charge | 1 | Kỵ binh kỳ cựu |
| Sau | Looming Lanterns | 1 | Quân bay kỳ cựu |
| Cuối | Stand Your Ground! | 1 | Rally! và ít nhất một ô kỳ cựu |

Không thêm khóa cấp Lord. Inspiring Presence mở nhóm đầu, Rally! mở nhóm sau.
Giữ giá trị, phạm vi và unit set native; ô kỳ cựu giữ điều kiện kinh nghiệm đơn vị
native. Không dùng nhánh đỏ để tăng riêng chỉ số cận chiến Zhao.

## 8. Nhánh xanh — nền Shugengan

| Nhóm | Kỹ năng | Điểm tối đa | Công dụng |
|---|---|---:|---|
| Mở đầu | Route Marcher | 1 | Hành quân |
| Đầu | Iron Disciplinarian | 3 | Control |
| Đầu | Inspiring Recruitment | 3 | Giảm chi phí tuyển |
| Đầu | Reassuring Presence | 3 | Giảm tổn thất attrition |
| Đầu | Fervent | 3 | Giảm corruption |
| Cầu nối | Irrepressible | 1 | Hồi phục Lord, kinh nghiệm, thời gian bị thương |
| Sau | Lightning Strike | 3 | Viện quân; cấp kỹ năng 3 mở Lightning Strike |
| Sau | Quartermaster | 3 | Giảm upkeep |
| Sau | Logistician | 3 | Replenishment |
| Sau | Alert | 3 | Chống phục kích |
| Cuối | The Great Bastion | 1 | Kinh nghiệm quân đội, upkeep, tuyển quân theo native |

Không thêm khóa cấp Lord. Route Marcher mở nhóm đầu; tổng 4 điểm nhóm đầu mở
Irrepressible; Irrepressible mở nhóm sau; tổng 4 điểm nhóm sau mở The Great Bastion.
Giữ hiệu ứng native. Tốc độ battle mới không tăng tầm hành quân campaign.

## 9. Kỹ năng chung và mount

| Kỹ năng | Điểm | Cấp Lord hiển thị |
|---|---:|---|
| Will of the Dragons | 1 | Không khóa cấp |
| Wind Harmony (+10% spell resistance) | 1 | 7 |
| Ranged Discipline (+10% missile resistance) | 1 | 7 |
| Harmonious Presence — Yin | 1 | Không khóa cấp |
| Soldiers of Renown | 3 | 10 / 20 / 30 |
| Immortality | 1 | 20 |
| Mentor | 3 | 30 / 40 / 50 |
| Warhorse | Tự mở | 5 |
| Jade Longma | Tự mở | 15 |

Dùng Soldiers of Renown của Lord thường, không lấy bản Legendary Lord Huyen Ve.
Đây là cấp hiển thị đề xuất; khi triển khai phải kiểm tra cách mã hóa rank/criteria,
không chép số thẳng vào DB rồi mặc định tương đương.

**Mount chưa có model rider hoàn thiện.** Hai ô là mục tiêu thiết kế, không phải
tài nguyên đã sẵn sàng. Phải làm/duyệt rider riêng. Mỗi dạng lấy nền mount Shugengan
tương ứng rồi giảm cận chiến theo định hướng Zhao; chưa chốt con số mounted.
Không cộng tốc độ đi bộ 4.2 hoặc nhân ưu thế tốc độ lên ngựa/Longma.

## 10. Phép bound phụ — chọn một

Mở từ cấp Lord **10**. Mỗi ô 1 điểm; mua một sẽ khóa ba ô còn lại.

| Kỹ năng | Phép bound |
|---|---|
| Metal Affinity | Plague of Rust |
| Death Affinity | Spirit Leech |
| Beast Affinity | Flock of Doom |
| Shadow Affinity | The Enfeebling Foe |

Giữ giới hạn sử dụng, cooldown và thông số native; không cho học cả bốn.

## 11. Các nguồn WWD dự kiến thay thế

Nếu được yêu cầu triển khai cây mới, bỏ khỏi cấu hình mới:

- Ability tăng sức mạnh theo tử trận gần đó và kỹ năng mở sẵn tương ứng.
- Ability WWD gây sát thương diện rộng, bảo hộ/hồi phục/triệu hồi.
- Các kỹ năng tăng trưởng, tiến trình và bonus Command Seal cũ.
- Bất tử cấp sẵn; thay bằng ô Immortality cấp Lord 20.

Command Seal WWD hiện có +8 leadership quân đội, -8% upkeep, +25% chống phục kích,
+3% replenishment; không cộng các bonus đó vào cây Shugengan mới.
Đây là kế hoạch thay thế, không phải thông báo đã xóa dữ liệu hoặc vật phẩm.
Nếu triển khai cho save cũ, phải thiết kế migration riêng để xử lý skill, điểm,
ability, bất tử và item đã có; không tự sửa save hoặc mặc định chúng tự biến mất.

## 12. Mốc tiến triển và việc còn lại

| Cấp Lord | Mốc |
|---|---|
| 1 | Hai phép cơ bản; chỉ số đi bộ mới theo thiết kế |
| 2–6 | Đầu tư phép/đỏ/xanh; mục tiêu Warhorse cấp 5 |
| 7 | Hai ô kháng phép/đạn |
| 10 | Phép bound chọn một; Soldiers of Renown cấp kỹ năng 1 |
| 13 | Bắt đầu Mooncourt |
| 15 | Mục tiêu Jade Longma sau khi hoàn thiện rider |
| 20 | Immortality; Soldiers of Renown cấp kỹ năng 2 |
| 30 / 40 / 50 | Mentor và hoàn thiện hướng đã chọn |

Phép cao cấp/capstone đỏ/xanh mở theo điểm, không có một cấp cố định cho mọi build.
Không tăng điểm mỗi cấp; nếu dùng 1 điểm/lần lên cấp thì phải chọn hướng đầu tư,
không mua hết cây ở cấp 50.

- [X] Lưu đề xuất theo yêu cầu người dùng.
- [X] Người dùng đã yêu cầu triển khai sau khi lưu; đang chờ pack nền v34 hoặc bản mới hơn.
- [ ] Đối chiếu pack v34 thực tế và dependency mới trước khi build.
- [ ] Chốt chi tiết chỉ số mounted, làm/duyệt rider.
- [ ] Chốt migration save cũ nếu nằm trong phạm vi triển khai.
- [ ] Build/kiểm tra DB, graph, spell modifiers và criteria/rank hiển thị.
- [ ] Kiểm thử game: khả năng chạy thoát, attack/cast, Winds/cooldown,
      kỹ năng/quân đội, mount, level-up và save/load.

Không có build, deploy hoặc game launch trong lần lưu đề xuất này.

## 13. Audit khả năng phục hồi build và bàn giao Git — 26/11/2026

Sau khi yêu cầu triển khai, người dùng yêu cầu ưu tiên cập nhật Project Goals và
đẩy các thay đổi dự án lên Git trước. Chưa có triển khai gameplay trong đợt này.

- Script v34 cần pack v33 và scene Zhao đã sửa grip; v33 cần pack v32.
- Các bước trước tiếp tục phụ thuộc pack, scene đã chỉnh, render và report trong
  `build/` hoặc `reference/local/`; các thư mục này không nằm trong Git.
- Repo có source và một số checkpoint Blender đã được chủ động backup, nhưng
  chưa có đủ đầu vào để chứng minh build sạch ra đúng bản v34 nguyên trạng.
- Nguồn Workshop hiện tại khác hash nguồn cũ; cần audit dependency trước rebuild.
- Có thể nghiên cứu tái dựng chức năng từ source và tài nguyên hiện có, nhưng phải
  gọi đúng là bản tái dựng và duyệt lại những ngoại hình thiếu checkpoint.
- Ưu tiên khôi phục bất kỳ pack v32/v33/v34 hoặc backup build để giảm phần phục hồi.
- `tools/Build-Mooncourt-Moon-Arts.py` là script v35 cũ, có bộ phép và lựa chọn
  khác tài liệu này. Không chạy trực tiếp hoặc bỏ hash guard để ép nó làm bản mới.
- Không tái tạo đè checkpoint đã duyệt. Mount và migration save cũ vẫn chưa chốt.

Bản trích xuất game/Workshop và file tạm tiếp tục nằm ngoài Git. Đợt backup này
lưu tài liệu thiết kế, kết quả audit và trạng thái công việc; không bổ sung pack
hoặc game asset vào repo. Chưa build, deploy hoặc xác nhận runtime cho thiết kế mới.
