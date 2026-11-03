# Da Lien — Thiết kế skill tree (chưa triển khai)

> V1 lịch sử: người dùng nhận xét bộ Metal không hợp nhân vật. Hướng phép hiện tại chuyển sang Yin/Heavens và hai phép hỗ trợ Life; xem DA-LIEN-SKILL-DIRECTION-V2.md. Các con số/gate/bộ phép dưới đây chưa được duyệt và cần tính lại cho V2.

Da Lien là Legendary Hero pháp sư con người của Agents of the Moon: đánh cụm lính, hồi máu nhẹ, tăng giáp. Bộ phép Metal/Life hỗn hợp; giữ tên và hình phép native để dễ nhận biết.

Ngày: 03/11/2026. Nguồn kiểm tra: DB native local; audit đầy đủ và icon provenance tại build/da-lien-skill-design/.

## Phép thuật

| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |
|---|---:|---|---|
| Searing Doom | 2 | Cấp 1 | Phép bombardment chống đội hình lính. Có sẵn bản cơ bản khi xuất hiện; 2 điểm nâng cấp theo native. |
| Earth Blood | 3 | Cấp 1 | Hồi máu nhẹ theo vùng; không hồi sinh lính chết. 6 Winds ở bản cơ bản; giữ healing cap native. |
| Glittering Robe | 3 | Cấp 1 | Tăng 60 giáp trong 44 giây; bản cơ bản cho một mục tiêu, overcast hỗ trợ theo vùng. |
| Gehenna’s Golden Hounds | 3 | Cấp 1 | Vortex di chuyển gây sát thương lên đội hình lính; cần cẩn thận vị trí đồng minh. |
| Metalshifting | 1 | Cấp 1 | Giữ một lore passive native. Không cộng thêm Life Bloom để tránh hồi máu tự động mỗi lần niệm phép. |
| Evasion | 1 | Cấp 7 + 4 điểm phép đầu | Giữ passive sinh tồn dành cho caster; nút nối sang nhóm phép nâng cao. |
| Transmutation of Lead | 3 | Cấp 8 + Evasion | Hex giảm sức chiến đấu của đối phương; hỗ trợ bộ binh giữ tuyến. |
| The Dwellers Below | 3 | Cấp 8 + Evasion | Phép sát thương vùng cao cấp cho cụm lính. 17 Winds ở bản cơ bản; không đổi thành sát thương miễn phí. |
| Earthing | 1 | Cấp 8 + Evasion | Giảm 15 điểm phần trăm nguy cơ miscast theo effect native. |
| Magical Reserves | 1 | Cấp 8 + Evasion | Tăng 5 sức chứa dự trữ Winds của quân đoàn; không phải tự tạo Winds vô hạn. |
| Arcane Conduit | 1 | Cấp 12 + 4 điểm nhóm nâng cao | Giữ cơ chế Arcane Conduit native hiện tại: passive, không thiết kế thành nút bấm cũ. |

## Kỹ năng riêng

| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |
|---|---:|---|---|
| Moon Scholar | 1 | Cấp 8 | Đề xuất: −10% cooldown phép Metal và Life của Da Lien. |
| Silver Ward | 1 | Cấp 12 | Đề xuất: +20 giáp cho bản thân. Không cấp elixir hay cơ chế Alchemist đi kèm. |
| Deep Wells | 1 | Cấp 16 | Đề xuất: +5 dự trữ Winds; cộng với Magical Reserves thành +10. |
| Moonlit Grace | 1 | Cấp 20 | Đề xuất: +10% tốc độ và +8 melee defence cho bản thân; giúp thoát cận chiến. |
| Veil of the Moon | 1 | Cấp 24 | Đề xuất: −2 lượt hồi phục khi bị thương. Đây không phải ô mua Immortality. |
| Lunar Mastery | 1 | Cấp 28 | Đề xuất: +10% spell mastery cho bản thân; phải nối cả effect và attribute cho phép mastery. |

## Sinh tồn

| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |
|---|---:|---|---|
| Wind Harmony | 1 | Cấp 7 | Native: +10% spell resistance cho bản thân. |
| Ranged Discipline | 1 | Cấp 7 | Native: +10% missile resistance cho bản thân. |

## Campaign

| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |
|---|---:|---|---|
| Increase Mobility | 3 | Cấp 1 / 5 / 10 | Native: nâng hiệu quả hỗ trợ di chuyển quân đoàn +5 / +10 / +15; phải gắn đúng action khi nhúng quân. |
| Boost Income | 3 | Cấp 1 / 5 / 10 | Native: nâng hiệu quả tác động thu nhập +2 / +4 / +6; áp dụng theo cơ chế vùng và action native. |
| Damage Building | 3 | Cấp 1 / 5 / 10 | Native: +5 / +15 / +30 vào hiệu quả hành động phá công trình; không phải +% sát thương battle. |
| Assassinate | 3 | Cấp 1 / 5 / 10 | Native của Cathay Alchemist: nâng hiệu quả hành động ám sát Hero +3 / +8 / +15. Không tăng sức đấu tay đôi trong battle. |
| Hinder Replenishment | 3 | Cấp 1 / 5 / 10 | Native: −10 / −20 / −40 vào hiệu quả cản bổ sung quân địch; cần giữ enable/action scaling nền. |
| Specialist | 3 | Cấp 1 | Native: chi phí hành động −10 / −20 / −40%; cơ hội thành công +1 / +3 / +6 điểm phần trăm. |

## Mentor

| Kỹ năng | Điểm tối đa | Mở khóa | Thiết kế |
|---|---:|---|---|
| Mentor | 3 | Cấp 30 / 40 / 50 | Native Hero Mentor: chia sẻ kinh nghiệm theo mức 15 / 30 / 50. Không dùng mốc cấp 29 / 39 / 49 hiển thị: đó là rank nội bộ. |

- ĐÂY LÀ BẢN THIẾT KẾ ĐỂ DUYỆT. Chưa sửa DB, script, pack hay bản game v22. Tên skill riêng bằng ASCII khi đưa vào game; icon của chúng chỉ là artwork native minh họa, không kế thừa hiệu ứng của skill cho icon.

- Sáu phép chủ động: Searing Doom, Earth Blood, Glittering Robe, Golden Hounds, Transmutation of Lead và Dwellers Below. Ba phép gây sát thương vùng, một heal, một buff giáp và một hex. Không chọn Final Transmutation vì ưu tiên cụm lính; không chọn Regrowth/Life Bloom để giữ vai trò hồi máu phụ.

- Khởi đầu: Searing Doom cơ bản miễn phí qua hidden enable node; không tự cấp Earth Blood/Glittering Robe. 2 điểm Searing Doom chỉ nâng phép đã có. Những phép còn lại dùng 3 mức native: mở phép → overcast/cooldown → tối ưu chi phí/miscast. Lore passive Metalshifting phải được mua riêng.

- Gating đề xuất: 4 điểm đầu phải được tiêu trong nhóm Searing Doom, Earth Blood, Glittering Robe, Golden Hounds hoặc Metalshifting để mở Evasion ở cấp 7. Nhóm nâng cao gồm Lead, Dwellers, Earthing, Reserves mở sau Evasion ở cấp 8. Tiêu 4 điểm trong nhóm nâng cao mới mở Conduit từ cấp 12. Đây là mốc thiết kế riêng; native thường dùng điều kiện điểm/link, không áp nguyên mốc cấp này.

- Nhánh riêng gồm 6 ô độc lập, mở theo cấp và mỗi ô tốn 1 điểm. Không ép mua cả chuỗi để lấy Lunar Mastery. Các số cộng là đề xuất cân bằng, chưa đo hiệu quả trong game.

- Tổng mua tối đa: phép thuật 22 + riêng 6 + sinh tồn 2 + campaign 18 + Mentor 3 = 51 điểm. Ngân sách chuẩn 49 điểm từ tăng cấp 1→50, nếu không có điểm thưởng. Không thể max tất cả: nhánh battle/caster có thể giảm đầu tư hành động campaign. Không tính phép khởi đầu, immortality hoặc action nền vào chi phí.

- Ví dụ build cấp 50 dùng đủ 49 điểm: phép 22 + riêng 6 + sinh tồn 2 + Mobility 3 + Specialist 3 + Income 3 + Assassinate 3 + Hinder Replenishment 3 + Damage Building 1 + Mentor 3. Hai điểm Damage Building còn lại là lựa chọn đánh đổi. Đây là tổng cuối cây, không phải thứ tự auto-spend.

- Nền miễn phí/ẩn bắt buộc: immortality ngay khi nhận Legendary Hero; agent action enables và scaling; enable phép khởi đầu; lore/composite group chỉ liệt kê base spells và giữ đúng liên kết overcast. Giữ trait/equipment slots của living Hero; không đem regeneration, undead healing, crumbling, raising dead hay cơ chế Lord của Neferata vào.

- Không có ô mua mount ở phiên bản đầu vì chưa có model/animation cưỡi tương ứng. Không có nhánh đỏ Lord, Route Marcher Lord, Army of Renown hay Lightning Strike. Mobility là skill Hero hỗ trợ quân đoàn. Tạm không đưa hai action buff alchemy mới của Alchemist vào vì kit Da Lien dùng Glittering Robe và không giữ toàn bộ hệ alchemy.

- Campaign giữ bộ hành động thực của khung Cathay Alchemist hiện tại (engineer): Mobility, Income, Damage Building, Assassinate, Hinder Replenishment. Không tự thêm Wound, Block Army hay Steal Technology khi chưa đổi action framework. Các phần trăm hiệu quả action không đồng nghĩa tỷ lệ thành công cuối cùng: engine còn tính cấp, mục tiêu và bổ trợ khác.

- Khả thi: phép/overcast, caster basics, Mentor, resistance và campaign skills có donor native kiểm chứng trong DB. Nhánh riêng chủ yếu ghép effect native; Lunar Mastery cần attribute enable tương ứng. Phải kiểm thử cây hỗn hợp, passive trigger khi cast cả hai lore, tooltip/mana thực tế, friendly fire, heal cap, action menus và điểm/link mở khóa. Chưa khẳng định runtime hoặc chất lượng cân bằng trước các bài kiểm tra này.

- Cấp khi nhận qua quest chưa chốt. Bản thiết kế hoạt động từ cấp 1; nếu sau này nhận ở cấp 15, phải cấp đúng XP/điểm chưa dùng hoặc chọn preset rõ ràng, không tự lén mua skill. Prototype Long Vi vẫn dùng cây thử nghiệm Metal hiện có.
