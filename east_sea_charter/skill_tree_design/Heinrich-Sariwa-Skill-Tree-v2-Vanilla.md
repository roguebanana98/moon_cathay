# Heinrich & Sariwa — thiết kế skill tree v2: skill có sẵn trong game

Bản này thay thế thiết kế 48 skill tự tạo trước đó. Chỉ thiết kế, chưa sửa hoặc xuất pack game. Nguồn đối chiếu trực tiếp: db.pack và ui.pack trong bản game đang cài.

## Nguyên tắc

- Chỉ dùng skill, hiệu ứng và icon vanilla. Tên mới chỉ là đề xuất localization; không sửa chỉ số, mana, hồi chiêu, loại sát thương, VFX hay animation.
- Heinrich lấy General of the Empire làm nền. Sariwa lấy Damsel (Heavens) làm nền để có Thunderbolt, Comet và Chain Lightning phù hợp vai trò sát thương tầm xa.
- Giữ cửa điểm, cấp mở, bậc nâng và các lựa chọn loại trừ của cây gốc. Thêm Guardian cho Heinrich; Sariwa thay Arcane Conduit bằng Greater Arcane Conduit từ Archmage. Không cộng hai conduit.
- Heinrich giữ Barded Warhorse và Imperial Griffon; bỏ Pegasus khỏi thiết kế. Sariwa đi bộ theo mô tả, bỏ Warhorse và Unicorn khỏi thiết kế này.
- Không đưa trait bẩm sinh, skill ẩn hoặc Mark of Hysh phụ thuộc cơ chế khác vào cây phân điểm.
- Không tạo bonus cặp đôi, phép Naga mới, skill kiếm mới, nhánh chính trị hoặc hiệu ứng thuế/cảng tự chế. Kiếm Sariwa vẫn là vũ khí model; không cần thêm nhánh cận chiến.

## Hai bổ sung quan trọng

- **Guardian → Đại Bàng Che Chở**, nguồn Handmaiden: giúp Heinrich che chở nhân vật đồng minh gần mình bằng đúng ability Guardian. Không viết lại thành aura chỉ dành cho Sariwa.
- **Greater Arcane Conduit → Mạch Phép Đền Cổ**, nguồn Archmage (Heavens): tăng năng lực pháp sư của Sariwa bằng ability có sẵn, thay cho Arcane Conduit thường.

Các hiệu ứng số cụ thể và liên kết DB nguyên bản được lưu trong skills-vanilla-v2.json; không suy diễn số từ tên skill. Tên gốc luôn ghi cạnh tên đề xuất để dễ đối chiếu.

## Heinrich von Adlerhorst

### Kỹ năng chung & thú cưỡi

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/mount_barded_warhorse.png) | Barded Warhorse | Barded Warhorse | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/mount_imperial_griffon.png) | Imperial Griffon | Imperial Griffon | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_general_ability.png) | Brass-Lunged | Brass-Lunged | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_lord_abilities_hold_the_line.png) | Hold the Line! | Giữ Vững Đầu Cầu | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_ward_save.png) | Sigmar’s Ward | Sigmar’s Ward | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_unit_capacity.png) | Soldiers of Renown | Soldiers of Renown | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_wound_time.png) | Immortality | Immortality | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_experience.png) | Mentor | Mentor | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh_main_skill_emp_lord_unique_general_barded_warhorse`
- `wh_main_skill_emp_lord_unique_general_imperial_griffon`
- `wh_main_skill_all_lord_battle_brass-lunged`
- `wh_main_skill_emp_lord_battle_hold_the_line`
- `wh_main_skill_emp_all_unique_sigmars_ward`
- `wh3_main_skill_all_army_of_renown_lord`
- `wh2_main_skill_all_immortality_lord`
- `wh3_main_skill_all_mentor_lord`

### Chuyên môn General · giữ lựa chọn loại trừ gốc

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_bonus_vs_infantry.png) | Imperial Training | Imperial Training | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_defence.png) | Survival Instincts | Dạn Dày Viễn Chinh | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/immune_to_psychology.png) | War Hero | War Hero | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_character_abilities_heroic_killing_blow.png) | Heroic Killing Blow | Heroic Killing Blow | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh3_dlc25_skill_emp_lord_general_special_1`
- `wh3_dlc25_skill_emp_lord_general_special_2`
- `wh3_dlc25_skill_emp_lord_general_special_3`
- `wh3_dlc25_skill_emp_lord_general_special_4`

### Chỉ huy General · giữ lựa chọn loại trừ gốc

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_experience.png) | Drill Instructor | Drill Instructor | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_charge.png) | Leading the Charge | Leading the Charge | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_army.png) | Statesman | Người Mang Hiến Chương | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_military_spending.png) | Leader of Men | Uy Danh Phó Vương | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh3_dlc25_skill_emp_lord_general_special_5`
- `wh3_dlc25_skill_emp_lord_general_special_6`
- `wh3_dlc25_skill_emp_lord_general_special_7`
- `wh3_dlc25_skill_emp_lord_general_special_8`

### Cận chiến · ưu tiên chống chịu

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_defence.png) | Hard to Hit | Hard to Hit | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_charge.png) | Devastating Charge | Devastating Charge | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_armour.png) | Full Plate Armour | Thép Nhà Adlerhorst | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_health.png) | Scarred Veteran | Scarred Veteran | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_attack.png) | Deadly Blade | Deadly Blade | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_character_abilities_foe_seeker.png) | Foe-Seeker | Foe-Seeker | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_damage.png) | Wound-Maker | Wound-Maker | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_attack.png) | Blade Master | Blade Master | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_morale.png) | Indomitable | Indomitable | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_defence.png) | Blade Shield | Blade Shield | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_character_abilities_deadly_onslaught.png) | Deadly Onslaught | Deadly Onslaught | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh_main_skill_all_all_self_hard_to_hit_starter`
- `wh2_dlc11_skill_all_lord_self_devastating_charge`
- `wh2_dlc11_skill_all_lord_self_full_plate_armour`
- `wh2_dlc11_skill_all_lord_self_scarred_veteran`
- `wh2_dlc11_skill_all_lord_self_deadly_blade`
- `wh_main_skill_all_all_self_foe-seeker`
- `wh2_dlc11_skill_all_lord_self_wound-maker`
- `wh2_dlc11_skill_all_lord_self_blade_master`
- `wh2_dlc11_skill_all_lord_self_self_indomitable`
- `wh2_dlc11_skill_all_lord_self_blade_shield`
- `wh_main_skill_all_all_self_deadly_onslaught`

### Quân đội Empire

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_morale.png) | Inspiring Presence | Inspiring Presence | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_defence.png) | Emperor's Finest | Emperor's Finest | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_charge.png) | Speed of Horse | Speed of Horse | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_ranged_damage.png) | Pistolkorps | Pistolkorps | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_attack.png) | Noble Beasts | Noble Beasts | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_ward_save.png) | Mighty Forge | Mighty Forge | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_ranged_damage.png) | Imperial Gunnery | Imperial Gunnery | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_character_abilities_rally.png) | Rally! | Rally! | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_defence.png) | Strength of Hardship | Strength of Hardship | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_ranged_damage.png) | Sharpshooter | Sharpshooter | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_attack.png) | Taste for Battle | Taste for Battle | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/battle_ammo.png) | Artillery Master | Artillery Master | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_character_abilities_stand_your_ground.png) | Stand Your Ground! | Đứng Sau Ta | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh_main_skill_all_lord_battle_inspiring_presence`
- `wh2_dlc11_skill_emp_army_buff_emperors_finest`
- `wh2_dlc11_skill_emp_army_buff_speed_of_horse`
- `wh2_dlc11_skill_emp_army_buff_pistolkorps`
- `wh3_dlc29_skill_emp_army_buff_noble_beasts`
- `wh2_dlc11_skill_emp_army_buff_mighty_forge`
- `wh2_dlc11_skill_emp_army_buff_imperial_gunnery`
- `wh_main_skill_all_lord_battle_rally`
- `wh2_dlc11_skill_emp_army_buff_strength_of_hardship`
- `wh2_dlc11_skill_emp_army_buff_sharpshooter`
- `wh2_dlc11_skill_emp_army_buff_taste_for_battle`
- `wh2_dlc11_skill_emp_army_buff_artillery_master`
- `wh_main_skill_all_lord_battle_stand_your_ground`

### Chiến dịch · đoàn viễn chinh

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_movement.png) | Route Marcher | Route Marcher | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_public_order.png) | Iron Disciplinarian | Iron Disciplinarian | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_military_spending.png) | Leader of Renown | Leader of Renown | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_disaster.png) | Reassuring Presence | Reassuring Presence | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_untainted.png) | Fervent | Fervent | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_wound_time.png) | Irrepressible | Irrepressible | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_subterfuge.png) | Lightning Strike | Lightning Strike | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_military_spending.png) | Quartermaster | Quartermaster | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_replenishment.png) | Logistician | Logistician | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_ambush.png) | Alert | Alert | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_army.png) | Headhunter | Headhunter | General of the Empire. Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh_main_skill_all_lord_campaign_route_marcher`
- `wh_main_skill_emp_lord_campaign_iron_disciplinarian`
- `wh_main_skill_emp_lord_campaign_leader_of_renown`
- `wh_main_skill_lord_all_campaign_reassuring_presence`
- `wh_main_skill_emp_lord_campaign_fervent`
- `wh_main_skill_all_lord_campaign_irrepressible`
- `wh_main_skill_all_lord_campaign_lightning_strike`
- `wh_main_skill_emp_lord_campaign_quartermaster`
- `wh_main_skill_emp_lord_campaign_logistician`
- `wh_main_skill_all_lord_campaign_alert`
- `wh_main_skill_emp_lord_campaign_headhunter`

### Bổ sung từ class khác

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh2_dlc10_guardian.png) | Guardian | Đại Bàng Che Chở | High Elf Handmaiden. Skill bổ sung. Đề xuất mở cấp 11 theo skill nguồn; 1 bậc. Dùng nguyên Guardian, áp dụng theo đối tượng gốc, không giới hạn riêng Sariwa. |

Khóa skill để đối chiếu:
- `wh2_dlc10_skill_hef_handmaiden_protector_2`

## Sariwa

### Bảo hộ & kỹ năng chung

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_hero_passive_aura_of_the_lady.png) | Aura of the Lady | Hào Quang Người Giữ Đền | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_ward_save.png) | Lady’s Mantle | Áo Choàng Lời Thề | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_wound_time.png) | Immortality | Immortality | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_experience.png) | Mentor | Mentor | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh_main_skill_brt_wizard_unique_damsel_aura_of_the_lady`
- `wh_main_skill_brt_all_unique_ladys_mantle`
- `wh2_main_skill_all_immortality_hero`
- `wh3_main_skill_all_mentor_hero`

### Phép thuật · Heavens

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_spell_heavens_harmonic_convergence.png) | Harmonic Convergence | Điềm Lành Đền Cổ | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_lore_passive_roiling_skies.png) | Roiling Skies | Bầu Trời Của Ngọc Xà | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_spell_heavens_wind_blast.png) | Wind Blast | Hơi Thở Naga | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_spell_heavens_curse_of_the_midnight_wind.png) | Curse of the Midnight Wind | Lời Nguyền Đền Rắn | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_spell_heavens_urannons_thunderbolt.png) | Urannon's Thunderbolt | Lôi Kích Ngọc Xà | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_character_passive_evasion.png) | Evasion | Evasion | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_spell_heavens_comet_of_casandora.png) | Comet of Casandora | Thiên Thạch Đền Cổ | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/battle%20ui/ability_icons/wh_main_spell_heavens_chain_lightning.png) | Chain Lightning | Ngũ Xà Lôi Quang | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_magic.png) | Earthing | Earthing | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/character_magic.png) | Magical Reserves | Magical Reserves | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/wh_main_character_abilities_arcane_conduit.png) | Greater Arcane Conduit | Mạch Phép Đền Cổ | High Elf Archmage (Heavens). Thay Arcane Conduit bằng Greater Arcane Conduit; giữ cửa mở cuối nhánh phép của Damsel. Không nhận cả hai. |

Khóa skill để đối chiếu:
- `wh_main_skill_all_magic_heavens_01_harmonic_convergence`
- `wh_main_skill_all_magic_heavens_03_rolling_skies`
- `wh_main_skill_all_magic_heavens_02_wind_blast`
- `wh_main_skill_all_magic_heavens_04_curse_of_the_midnight_wind`
- `wh_main_skill_all_magic_heavens_05_urannons_thunderbolt`
- `wh_main_skill_all_magic_all_06_evasion`
- `wh_main_skill_all_magic_heavens_09_comet_of_casandora`
- `wh_main_skill_all_magic_heavens_10_chain_lightning`
- `wh_main_skill_all_magic_all_07_earthing`
- `wh_main_skill_all_magic_all_08_power_drain`
- `wh2_dlc14_skilll_all_magic_all_greater_arcane_conduit`

### Chiến dịch · học giả Khuresh

| Icon gốc | Skill gốc | Tên đề xuất | Nguồn / ghi chú |
|---|---|---|---|
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_replenishment.png) | Replenish Troops | Replenish Troops | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_untainted.png) | Cleanse Corruption | Cleanse Corruption | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_technology.png) | Steal Technology | Steal Technology | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_wound_time.png) | Wound | Wound | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_movement.png) | Block Army | Block Army | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |
| ![icon](D:/Warhammer3_Modding/east_sea_charter/skill_tree_design/vanilla_reference/ui/campaign%20ui/skills/campaign_military_spending.png) | Specialist | Specialist | Damsel (Heavens). Giữ cấp mở, số bậc và điều kiện nối của cây gốc. |

Khóa skill để đối chiếu:
- `wh2_main_skill_all_hero_assist_army_replenish_troops`
- `wh2_main_skill_all_hero_passive_spread_corruption`
- `wh2_main_skill_all_hero_hinder_settlement_steal_technology`
- `wh2_main_skill_all_hero_hinder_agent_wound`
- `wh2_main_skill_all_hero_hinder_army_block_army`
- `wh2_main_skill_all_hero_reduce_action_cost`
