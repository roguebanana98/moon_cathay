# Huyen Ve — Mật Lệnh Phương Nam

Ngày thiết kế: 03/11/2026. Phạm vi: thiết kế campaign `cr_combi_expanded`, faction
`cr_cth_agents_of_the_moon`, Legendary Lord subtype `mc_moon_warden`.
Đây là đặc tả để triển khai; chưa thêm mission, hero, sửa pack hoặc chạy game.

## 1. Quyết định thiết kế và mức khả thi

Giữ nhiệm vụ nền hiện có, thêm một tuyến truyện gồm **5 chương nhận 5 món của
Relics of the Warden of Long Vi**, sau đó **1 chương cuối nhận Legendary Hero mới**.
Không yêu cầu hoàn thành Long Victory mới được nhận hero. Không đặt thời hạn.
Các cấp là cấp hiển thị mục tiêu thiết kế, chưa phải rank nội bộ dùng trong DB.

Điều chỉnh theo phản hồi mới nhất: **chỉ còn một quest battle ở chương 6** để
nhận Legendary Hero. Năm món trang bị được nhận qua nhiệm vụ campaign. Chương
3 đổi thành điều tra rồi mang chứng cứ về Long Vi; chương 5 đổi thành hồi phục
thanh kiếm tại Long Vi. Thay đổi này supersede phương án Hero điều tra → quest
battle trước đó, không giữ ba battle chỉ vì bản cũ đã viết như vậy.

**Hạ tầng native hỗ trợ các cơ chế đề xuất, nhưng chưa chứng minh triển khai được
trận cuối Huyen Ve cụ thể. Trận này chưa đạt mức sẵn sàng triển khai:** chưa
chốt tọa độ campaign, map/deployment/entry, roster và trigger đầy đủ. Không thể
cam kết chất lượng bản chơi từ bản thiết kế này. Xem đánh giá bổ sung tại
`HUYEN-VE-QUEST-BATTLE-READINESS.md`. Hai cổng phải chứng minh sớm là bộ đếm kill
đúng quân đoàn và vòng đời Legendary Hero mới. Quest battle dùng map có sẵn;
không đặt yêu cầu map mới, lồng tiếng mới hoặc model hero tự làm trong bản đầu.

## 2. Nhiệm vụ hiện có và cách cùng tồn tại

Nguồn: `docs/FACTION-MISSIONS.md`, audit ngày 02/11/2026. Bốn nhiệm vụ ACTIVE
dưới đây được xác nhận trong snapshot save 30/10, trước bản Huyen Ve; không phải
khẳng định cả bốn hiện đang ACTIVE trong save người chơi hôm nay.

| Nhiệm vụ | Điều kiện đã xác nhận | Phần thưởng/ghi chú |
|---|---|---|
| Short Victory | Occupy/loot/raze/sack 30 settlements | +3 hero capacity theo bundle Order |
| Long Victory | Short Victory và mốc 60 settlements | +10 hero recruit rank theo bundle Order |
| Domination | Mốc 272 settlements | Payload dummy Forge of Souls; chưa thấy bundle chỉ số trong mission |
| Capture Settlement | Chiếm settlement; target list trong snapshot rỗng | 750 gold + Potion of Strength |

Các mốc victory là điều kiện settlement của engine, không phải số thành phải
giữ đồng thời. Giữ các nhiệm vụ này; chưa thay điều kiện thắng bằng thiết kế mới.
Chiếm Avauka có thể đồng thời giúp tiến độ nhiệm vụ nền nếu engine xác nhận;
không can thiệp hoặc tự hoàn thành mission vanilla từ script của mod.

Các nhánh tutorial dùng chung có tuyển quân, nghiên cứu, xây dựng, province,
commandment, tài chính, Hero và ngoại giao; xuất hiện tùy điều kiện campaign.
Các mission Cathay về Harmony, Compass và caravan tồn tại trong script nhưng
chưa xác nhận tất cả chạy đúng với faction/version hiện tại. Không dùng chúng
làm điều kiện bắt buộc của tuyến mới.

Saytang và Gotrek & Felix có đường hỗ trợ qua MIXER, còn phụ thuộc DLC, trạng thái
nhân vật và runtime. Taoyan thiếu mapping faction trong audit hiện tại. **Hero
mới của tuyến này là nhân vật riêng của mod**, không đổi tên một LH dùng chung,
không thay phần thưởng bằng Saytang/Taoyan và không phụ thuộc tuyển được họ.

## 3. Cốt truyện xuyên suốt

Đoàn vận chuyển bảo khí tới Long Vi mất tích. Những mệnh lệnh đóng ấn hợp lệ lại
đưa các đội tuần phòng vào phục kích. Huyen Ve phải khôi phục tuyến tiếp tế,
tìm kẻ dùng ấn giả và thu hồi các bảo vật trước khi chúng bị dùng để mở đường
cho Chaos. Những dấu hiệu để lại cho thấy một người bảo vệ đoàn hàng vẫn sống.

Người đó là **Lam Anh, the Last Moonwatcher** — tên và nhân vật đề xuất cho mod.
Lam Anh giữ sổ lộ trình gốc, lần theo kẻ chủ mưu rồi bị vây khi đang khóa đường
dẫn quân Chaos. Thu đủ năm bảo khí giúp Huyen Ve tìm ra và giải cứu cô ở hồi cuối.
Mỗi chương giải quyết một vấn đề và để lại một manh mối, không chỉ trả một món đồ.

Toàn bộ truyện mới là sáng tác cho mod; không coi là canon Warhammer.
Văn bản thiết kế dùng tiếng Việt; UI mới dùng English ASCII theo quy ước dự án.

## 4. Chuỗi chính

Mỗi chương yêu cầu chương trước hoàn tất và đạt cấp gợi ý. Chỉ một chương chính
hoạt động cùng lúc. Mốc cấp dùng để điều tiết nhịp, sẽ điều chỉnh sau playtest.

| Chương / cấp gợi ý | Mission UI | Mục tiêu bắt buộc | Phần thưởng duy nhất |
|---|---|---|---|
| 1 / 6 | A Seal in the Moonlight | Sở hữu Long Vi; Huyen Ve thắng 2 trận campaign sau khi nhận nhiệm vụ | Moonshadow Jade Pendant — talisman |
| 2 / 10 | Reopen the Southern Road | Đưa Avauka về quyền sở hữu trực tiếp của faction | Long Vi Mountain-Pattern Armour — armour |
| 3 / 14 | The Counterfeit Seal | Hero độc lập điều tra marker rồi đưa chứng cứ về Long Vi | Warden's Seal — enchanted item |
| 4 / 18 | Feed the Moon Lantern | Quân đoàn do Huyen Ve chỉ huy đạt mốc kill từ khi chương mở | Moon Lantern — arcane item |
| 5 / 22 | Restore the Nightwarden | Huyen Ve tới Long Vi, trả 3.000 gold để phục hồi kiếm; bảo vệ quyền sở hữu thành trong 2 lượt xử lý | Nightwarden's Blade — weapon |
| 6 / 25 | The Last Moonwatcher | Đã nhận đủ 5 món; Huyen Ve thắng quest battle giải cứu Lam Anh | Legendary Hero mới: Lam Anh |

### Chương 1 — Dấu ngọc trong đêm

Mật sứ chỉ trao ngọc nhận diện cho người thực sự giữ được Long Vi. Hai chiến
thắng xác lập uy tín của Huyen Ve và hé lộ các mệnh lệnh phục kích bất thường.

- Long Vi: `cr_combi_region_long_vi`. Nếu đã sở hữu thì đánh dấu mục tiêu lãnh thổ
  đạt ngay. Phải còn sở hữu khi kết thúc chương; mất thành không xóa chiến công.
- Chỉ tính trận có Huyen Ve chỉ huy quân đoàn tham chiến và thắng; cho phép
  autoresolve. Không tính trận chỉ quân đồng minh đánh khi Huyen Ve không tham dự.
- Quest battle và trận thử không tính vào hai chiến thắng campaign này.
- Nhận ngọc dẫn tới tin thợ rèn mang giáp bị cắt đường về từ Avauka.

### Chương 2 — Mở lại đường phương Nam

Thu hồi Avauka để đưa thợ rèn và giáp về Long Vi. Dùng một thành cụ thể để người
chơi có mục tiêu chiến dịch rõ ràng, không sinh quân cướp dùng chung faction QB.

- Avauka: `cr_combi_region_avauka`, đã đối chiếu key trong dữ liệu IEE.
- Nếu thành thuộc phe địch: chiếm và occupy; sack/raze riêng lẻ không đủ.
- Bất kỳ quân đoàn nào của faction cũng được chiếm thành. Không bắt Huyen Ve
  phải thực hiện last hit nếu một quân đoàn khác đã kiểm soát con đường.
- Nếu đã sở hữu khi mở chương: công nhận ngay, không bắt bỏ thành rồi chiếm lại.
- Nếu do đồng minh/trung lập giữ: không ép phá liên minh. Dilemma cho phép trả
  2.000 gold để mở đường và chuộc giáp; thiếu tiền giữ lựa chọn chờ, không trừ âm.
  Đây là đường hoàn thành thay thế được ghi rõ trong UI khi đủ điều kiện.
- Chỉ cần đạt một trong hai đường, trao đúng một giáp. Mất Avauka sau hoàn thành
  không thu hồi giáp hoặc khóa chương tiếp theo.

### Chương 3 — Kẻ mang ấn giả

Giáp trở về cùng một lệnh áp tải sai dấu. Một Hero tới kho lưu trữ được đánh dấu
để tìm ấn thật và chứng cứ sửa lệnh; đưa hồ sơ về Long Vi để xác nhận quyền trấn thủ.

- Hero phải thuộc faction, đứng độc lập; Lord và Hero đang embed không hoàn
  thành bước điều tra. Marker không đòi hero action có xác suất thành công.
- Tọa độ marker chưa được chốt: phải chọn điểm đất đi tới được trên IEE, ngoài
  vùng thành bị vây, có đường thay vị trí nếu kiểm tra ban đầu thất bại.
- Sau điều tra, một Hero độc lập của faction tới region Long Vi đang sở hữu
  để giao hồ sơ. Có thể là Hero khác nếu người điều tra chết; lưu discovery ở
  faction, không làm mất tiến độ vì thay nhân vật. Không bắt hero action có RNG.
- Chỉ hoàn tất khi giao hồ sơ sau bước điều tra; Hero đã ở Long Vi từ trước
  không tự hoàn thành bước giao ngay tại thời điểm discovery.
- Trao ấn sau khi xác minh hồ sơ. Sổ giả hé lộ Lam Anh còn sống và chiếc đèn đang
  bị ô uế. Không spawn quân nhiệm vụ, không quest battle, không phải giết nhân vật.

### Chương 4 — Thắp lại Nguyệt Đăng

Chiếc đèn cần chiến công thực tế của đoàn quân trấn thủ để phá dấu ô uế.
Đây là nhiệm vụ tích lũy qua các trận campaign thường, không thêm quest battle.

- Mục tiêu ban đầu: **2.000 enemy entities tại unit size Ultra**. Đề xuất mốc
  Small/Medium/Large/Ultra: 500/1.000/1.500/2.000, cần hiệu chỉnh bằng playtest.
  Chưa xác minh API đọc unit size; nếu không đọc được đáng tin cậy, dùng cấu hình
  rõ ràng chọn lúc khởi tạo và lưu mốc, không tự đoán hoặc đổi giữa chừng.
- Đếm cá thể địch, không đếm 2.000 unit card. Cộng kill do các đơn vị thuộc quân
  đoàn Huyen Ve gây ra; không phải 2.000 kill cá nhân của Lord.
- Tính từ khi phát chương, giữ tiến độ khi thua/rút lui hoặc Huyen Ve bị thương.
  Chỉ cộng kết quả hợp lệ của trận campaign; không cộng kill cũ hoặc quest battle.
- Định danh lực lượng tại lúc giao chiến, không suy ra từ quyền sở hữu các unit
  sau trận. Quân khác cùng faction và viện quân đồng minh không được cộng nhầm.
- Mục tiêu chất lượng là hỗ trợ cả manual và autoresolve, phép/AOE và viện quân.
  Đây là điều phải chứng minh bằng thử nghiệm, chưa phải tính năng đã xác nhận.
- UI hiển thị `Army kills: X / Y` và số được cộng sau trận; không dùng dữ liệu
  phần trăm casualties nhân quân số ban đầu để giả làm kill chính xác.

### Chương 5 — Thanh kiếm sau nửa đêm

Ngọn đèn soi ra nơi giấu kiếm trong lô hàng thu hồi. Thanh kiếm bị hỏng phong ấn;
Huyen Ve phải mang nó về Long Vi để thợ rèn phục hồi trước khi tìm Lam Anh.

- Huyen Ve tới region Long Vi đang thuộc faction, mở dilemma trả 3.000 gold.
  Thiếu tiền được chờ và mở lại; không dùng treasury âm hoặc trừ lặp callback.
- Sau thanh toán, tính 2 FactionTurnStart tiếp theo còn sở hữu Long Vi. Nếu mất
  thành thì tạm dừng, lấy lại thì tiếp tục; không thu phí lần hai. Thời lượng là
  giá trị thiết kế để playtest, không phải đếm 2 lượt AI riêng lẻ.
- Huyen Ve có thể rời đi sau khi đặt việc; không buộc ông đứng chờ 2 lượt.
  Không đòi construction chain chưa có hoặc sinh địch ép công thành.
- Trao kiếm; bonus đủ bộ +5% ward save dùng định nghĩa set đã có, không thêm
  vĩnh viễn một buff tương đương bằng script hoàn thành nhiệm vụ.
- Kiếm và ấn xác nhận vị trí Lam Anh đang cố thủ; mở hồi cuối ở cấp phù hợp.

### Chương 6 — Người gác trăng cuối cùng

Lam Anh dùng tín hiệu cuối cùng dẫn Huyen Ve tới chỗ cô đang chặn quân Chaos.
Trận cuối kết thúc câu chuyện bằng việc giải cứu một nhân vật đã được nhắc tới,
đồng thời mở thêm lựa chọn đội hình cho chiến dịch sau đó.

- Gate là đã hoàn thành 5 chương và nhận đủ 5 món; **không buộc đang equip đủ
  bộ**, không bắt quay về thay đồ. Đồ chỉ mang vai trò mạch truyện ở gate này.
- Một quest battle cuối gồm phòng thủ và phản công: giữ Lam Anh sống khoảng
  4 phút, sau đó đẩy lùi quân địch cuối cùng. Timer là chuyển giai đoạn, không tự thắng.
- Lam Anh là đơn vị đồng minh cố định trong battle; nếu chết thì thua và được
  thử lại. Hero campaign thực chỉ sinh sau chiến thắng, không lấy chính battle
  unit làm nhân vật campaign trước khi mission hoàn tất.
- Vị trí Lam Anh có khoảng trống để tiếp cận; đợt đầu không đủ sức giết cô
  trước khi quân người chơi có cơ hội can thiệp. Không yêu cầu người chơi biết
  trước điểm spawn để thắng.
- Sau thắng: spawn Hero tại điểm hợp lệ gần Huyen Ve; nếu Lord đang trên biển,
  trong tình trạng không hợp lệ hoặc vị trí bị chặn, dùng owned region an toàn.
  Nếu chưa có điểm hợp lệ, giữ reward pending và thử lại, không phát bản sao.

## 5. Legendary Hero mới — Lam Anh

Vai trò đề xuất: nữ Moonwatch captain, kiếm một tay, bộ binh, hỗ trợ tuyến trước
và săn Hero địch. Giữ bản đầu human-only, không mount, không thêm lore phép.
Đây là tên/giới tính/vai trò đề xuất thiết kế, chưa phải lựa chọn đã được người
dùng chốt. Có thể đổi danh tính mà không ảnh hưởng cấu trúc sáu chương.

- Một subtype riêng dự kiến `mc_lam_anh`, một instance cho faction trong campaign.
  Không đưa vào pool tuyển ngẫu nhiên; wounded rồi trở lại được, không nhận lần hai.
- Cấp khi nhận đề xuất: 15, sẽ chốt quy ước XP/rank sau prototype. Không tự gán
  chỉ số ngang LL cấp cao hoặc cộng hero capacity toàn faction không cần thiết.
- Bộ kỹ năng đầu dùng melee/defence/duelist native phù hợp, có cây riêng.
  Hai điểm đặc trưng dự kiến: bản thân có Stalk và một kỹ năng chỉ huy phòng thủ
  ngắn hạn. Chỉ chọn effect/ability sau khi đối chiếu DB; chưa hứa aura mới.
- Không thêm hồi máu, không nhân bản Silence của kiếm hay spell kit Huyen Ve.
  Test để kit không cộng dồn vô hạn với aura ấn và Moonlit Command.
- Chất lượng bản đầu: model/animation/portrait native tương thích, tên và UI riêng,
  không T-pose, không portrait trống. Model mới, voice mới và cinematic không nằm
  trong điều kiện hoàn thành tính năng này.
- Chưa chọn donor art/model; phải kiểm tra skeleton, animation, equip, voice và
  quyền nội dung trước khi chốt. Không mặc định dùng model Huyen Ve bên thứ ba.

## 6. Khả thi kỹ thuật và cổng chất lượng

| Hạng mục | Bằng chứng local | Đánh giá và điều kiện thông qua |
|---|---|---|
| Chiếm/giữ thành và thắng trận | Region keys IEE, mission_manager, listener battle trong audit cũ | Khả thi cao; test thành đã sở hữu, mất lại, đồng minh giữ và save/load |
| Hero điều tra → giao hồ sơ | Interactive Marker Manager và kiểm tra vị trí/ownership campaign | Có nền tảng; cần chốt marker đi được, thứ tự hai bước và khôi phục sau load |
| Phục hồi kiếm | Dilemma, treasury transaction và saved-state/turn listener | Có nền tảng; cần kiểm chứng trừ tiền một lần, đếm lượt và mất/lấy lại Long Vi |
| Đếm kill đúng quân đoàn | Glottkin script dùng force CQI + `units_killed_by_attacker_unit_set`/defender tại CharacterCompletedBattle | Khả thi có điều kiện; chưa chứng minh dữ liệu bao phủ mọi đơn vị/phép/autoresolve |
| Một quest battle cuối | Dragon's Fang và các bảng battle_set_piece đã audit | Chưa cấu hình; chất lượng phụ thuộc map, deployment, trigger và playtest |
| Hero campaign mới | Native character_unlocking dùng UniqueAgentSpawned và spawn_unique_agent* | Có đường triển khai; cần DB subtype/unit/skill/agent đúng và thử wounded-return |
| Trao đủ bộ và equip | 5 ancillaries + set đã build; có script cấp đồ test v17 | Định nghĩa đã có; re-equip v18 và bonus đủ/tháo đồ vẫn cần runtime xác nhận |

**Kill prototype:** `KILL_X_ENTITIES` trong Tz'arkan chỉ cho thấy objective đếm
toàn faction với `total`; không đủ chứng minh lọc đúng quân đoàn. Không dùng
objective đó trực tiếp rồi ghi UI rằng chỉ đếm Huyen Ve. Mẫu Glottkin là hướng
phù hợp hơn: force CQI + unit set. Nếu chọn hướng này phải tạo unit set bao phủ
roster hợp lệ, kể cả Lord, Hero, artillery và quân mod; xác minh summoned units
và kill phép thực tế. Không coi một set Cathay missile sẵn có là toàn quân.

Nếu prototype không đạt việc quy kill cho đúng quân đoàn trong cả manual và
autoresolve, dừng triển khai chương 4 để sửa bộ đếm. Phương án thay thế công khai
là đổi sang thắng 4 trận bằng Huyen Ve; đây là thay đổi thiết kế cần ghi rõ,
không âm thầm đếm toàn liên minh hoặc bỏ autoresolve mà vẫn dùng mô tả cũ.

## 7. Trạng thái, save cũ và nhận thưởng

Script riêng trong `script/campaign/mod/`, DB và loc prefix `mc_`; không thay
toàn bộ wh_quests, không sửa startpos chỉ để phát nhiệm vụ. Thiết kế state:
`locked -> active -> objective_complete -> reward_pending -> completed`.
Lưu version, stage, issued, target/mốc, counters, battle deduplication records,
reward state và hero spawn state. Không lưu engine interface vào saved value.

- Tính lại điều kiện sở hữu sau load; khôi phục listener/marker một lần. Lưu
  tiến độ qua wounded và quân đoàn mới; subtype nhận diện nhân vật, CQI nhận
  diện lực lượng tại trận, không cố định mã quân đoàn suốt campaign.
- Hoàn thành battle chỉ chuyển reward_pending. Kiểm tra nhân vật/ancillary thực
  rồi mới chốt completed; callback lặp không tạo thêm item hoặc Hero.
- Mỗi trận cộng một lần; snapshot khóa khử lặp cần đủ dữ liệu để phân biệt hai
  trận cùng lượt/cùng quân. Chưa chốt API battle ID, không giả định CQI là battle ID.
- Save cấp cao chưa chơi tuyến: mở chương 1, công nhận lãnh thổ đang có; không
  tự hoàn thành chiến công, không tính kill hồi tố, không mở tất cả chương cùng lúc.
- Save còn Ju Di subtype generic không đủ điều kiện; tên hiển thị không thay
  thế subtype. Không tự chuyển generic Lord hoặc sửa save trong phạm vi thiết kế.

**Tách bản test cấp đồ và bản progression:** v17 có script tự grant/equip cả bộ;
v18 đổi unique_to_world/unique_to_faction sang false để thử sửa re-equip. Bản
progression phải bỏ đường auto-grant và chỉ phát đồ từ reward handler; không
khôi phục hai flag unique theo phỏng đoán, quản lý phát một lần bằng state.

New campaign là chuẩn kiểm thử tuyến nhận đồ. Với save test đã có cả bộ: cho
chơi lại câu chuyện nhưng không phát thêm món đã được ghi nhận trong inventory
hoặc marker grant test. Marker test không đồng nghĩa đã hoàn thành mission.
Phải đối chiếu đồ đang equip lẫn inventory; nếu không xác minh được inventory
đáng tin cậy thì chưa hỗ trợ migration save test, không xóa đồ để ép chơi lại.
Không tự đánh dấu 5 chương hoàn tất hoặc spawn Hero chỉ vì phát hiện có đủ bộ.

## 8. Trình tự thực hiện và tiêu chí nghiệm thu

1. Làm prototype kill counter và Hero lifecycle trước khi đầu tư battle cuối.
   Mỗi cái cần log đối chiếu trong game, không chỉ kiểm tra tồn tại API.
2. Làm chương 1–2: UI, reward pending, đủ/thiếu tiền, chiếm thành và đường đồng
   minh. Chứng minh một item được nhận/equip/tháo/equip lại và không nhân bản.
3. Làm chương 3: Hero marker → giao hồ sơ tại Long Vi → đúng một ấn.
4. Làm chương 4 sau khi bộ đếm đạt; thử các unit size và điều chỉnh ngưỡng.
5. Làm chương 5: dilemma → thanh toán một lần → 2 lượt xử lý → đúng một kiếm.
6. Làm chương 6 từ quest battle tối giản đã vào/ra campaign được. Chốt map,
   tọa độ, roster, entry và timeline rồi kiểm thử thắng/thua/retry/reward.
   Test end-to-end bằng một campaign progression không có test grant.

| Nhóm kiểm thử | Điều kiện đạt |
|---|---|
| Kill | Đúng army, attacker/defender, reinforcement, manual/auto; infantry/artillery/spell; không cộng quân khác, không đếm hai lần |
| Save/load | Load giữa mục tiêu và sau battle/reward; giữ tiến độ, không lặp marker/reward, không mất mission khi wounded |
| Battle | Map cuối deploy/pathfinding tốt, không thắng sớm, thua thử lại được, teleport và trở về đúng; không spawn đè lên quân người chơi |
| Điều tra/phục hồi | Giao hồ sơ đúng thứ tự, thay Hero không kẹt; thiếu tiền chờ được, trả đúng một lần, mất thành tạm dừng và load không tăng lượt |
| Reward | Đúng 5 món/5 ô, đúng thứ tự, không bản sao; set bật đủ bộ/tắt khi thiếu; tháo lắp lại ổn |
| Hero | Nhận đúng một Lam Anh, chọn/di chuyển/embed/ra trận được; model/skill/portrait đúng; wounded hồi phục; load không spawn lại |
| Nhịp campaign | Tối thiểu một lượt chơi toàn tuyến và kiểm tra mốc cấp; không phải farm lại thành, phá liên minh hay phụ thuộc faction địch sống |
| Regression | Nhiệm vụ/victory nền còn nguyên; dependency/schema/diagnose hợp lệ; không bảng DLC ownership bị cấm |

Thiết kế ưu tiên single-player. Multiplayer chưa nằm trong tiêu chí hoàn thành
bản đầu và phải kiểm thử đồng bộ/người nhận riêng trước khi công bố hỗ trợ.
Chỉ đánh dấu gameplay hoàn thành sau khi có bằng chứng runtime cho các cổng trên.

## 9. Nguồn đối chiếu trong workspace

- `docs/FACTION-MISSIONS.md`: snapshot nhiệm vụ nền, tutorial, LH native.
- `docs/HUYEN-VE-EQUIPMENT-IDEA.md`: tiền đề năm bảo khí và quyết định chương 3.
- `docs/HUYEN-VE-EQUIPMENT-FEASIBILITY.md`: mission, marker, quest battle, set.
- `src/campaign/huyen-ve-equipment.json`: tên/key/ô và hiệu ứng 5 món hiện có.
- `src/campaign/province-layout.json`: region keys Long Vi/Avauka và province.
- `src/script/campaign/mod/mc_huyen_ve_campaign_test_items.lua`: đường grant v17.
- `AGENTS.md`: v18 re-equip, quy ước English ASCII/icon native và phạm vi test.
- `reference/local/lord-scripts/script/campaign/wh2_dlc14_tzarkans_whispers.lua`,
  `tzarkan_generate_kill_mission`: objective KILL_X_ENTITIES.
- `reference/local/lord-scripts/script/campaign/wh3_dlc29_glottkin_marks_of_nurgle.lua`,
  khoảng dòng 120–160: force CQI và units_killed_by_*_unit_set.
- `reference/local/lord-scripts/script/campaign/wh3_main_legendary_characters.lua`,
  `spawn_hero`, `unique_agent_listener`: spawn LH và xử lý callback.
- `reference/local/lord-scripts/script/_lib/lib_campaign_manager.lua`:
  pending battle cache theo attacker/defender và force CQI.

Các file reference là dữ liệu local đã trích xuất, không phải xác nhận API ở
mọi phiên bản game. Khi triển khai cần đối chiếu lại hash dependency hiện hành.
