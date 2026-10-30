# Agents of the Moon và Khuresh

## Định danh đã đối chiếu

| Thuộc tính | Giá trị |
|---|---|
| Tên English | Agents of the Moon |
| Faction key | `cr_cth_agents_of_the_moon` |
| Race theo UI / culture | Grand Cathay / `wh3_main_cth_cathay` |
| Subculture | `wh3_main_sc_cth_cathay` |
| DB faction index | `1213178199` |
| Faction ID trong startpos đọc được | `205` (ID nội bộ của snapshot, không dùng làm key lâu dài) |
| Frontend/startpos leader ID cho MIXER | `1104464346` |
| Military group | `wh3_main_cth` |
| Flags path | `ui\flags\cr_cth_agents_of_the_moon` |
| Uniform / banner primary, secondary, tertiary | `243355`, `6B6B18`, `D0C11D` |

Nguồn tên: `text/db/cr_new_combi_factions.loc`, dòng export 223.
Nguồn faction: `db/factions_tables/!cr_new_factions`, export version 6, dòng 47.
Culture được nối từ subculture qua `db.pack → cultures_subcultures_tables/data__`.
WH3 không có một field "race" riêng trong row faction này; không nhầm culture với faction key.

## Settlement mặc định

Đọc `IEE → campaigns/cr_combi_expanded/startpos.esf`, nối REGION owner faction ID = 205.

| Settlement | Region key | Province | Province capital |
|---|---|---|---|
| Dai Loa | `cr_combi_region_dai_loa` | `cr_combi_province_primal_labyrinth` — Primal Labyrinth | Có |
| Leilou | `cr_combi_region_leilou` | Primal Labyrinth | Không |
| Long Vi | `cr_combi_region_long_vi` | Primal Labyrinth | Không |
| Preenn | `cr_combi_region_preenn` | `cr_combi_province_paradise_spires` — Paradise Spires | Không |

Các slot capital của faction trong record FACTION cùng tham chiếu region ID 254 (Dai Loa);
province-capital flag được xác nhận độc lập trong bảng `region_to_province_junctions_tables`.
Không suy ra faction sở hữu toàn bộ Paradise Spires chỉ vì sở hữu Preenn.

## Lord khởi đầu và save hiện có

- Government `CHARACTER_POST` có loại `faction_leader`, tham chiếu character ID **329**.
- CHARACTER của faction này nối tới CHARACTER_DETAILS ID **339**, subtype
  **`wh3_main_cth_dragon_blooded_shugengan_yin`** — Dragon-Blooded Shugengan (Yin).
- Name components: forename **Ju** (`names_name_1376971991`, vanilla English loc);
  family_name **Di** (`names_name_623106632`, IEE override). Theo forename + surname là **Ju Di**;
  chưa kiểm tra thứ tự trình bày tên trên UI Cathay trong game.
- Art set: `wh3_main_art_set_cth_dragon_blooded_shugengan_yin_010`.
- Đây là subtype Lord Cathay thường; chưa thấy subtype Legendary Lord riêng cho faction này.
  Không suy luận trạng thái immortal chỉ từ tên hoặc frontend row.

Đã đọc thêm save hiện có:
`C:\Users\ADMIN\AppData\Roaming\The Creative Assembly\Warhammer3\save_games\Agents of the Moon.11158371198.save`.
Tại thời điểm đọc, save có cùng bốn region và cùng faction leader 329 / details 339 / subtype / name keys.
Các candidate trong recruitment pool không được tính là Lord đang hiện diện trên map.
Không khẳng định đây là trạng thái một campaign đang chạy chưa save; không sửa save này.

`reports/agents-of-the-moon.json` lưu offset giải nén, các ID liên kết và kết quả hai snapshot.
Các offset thuộc cây ESF **sau giải nén**, không phải offset trong pack nén.

## Frontend và MCT

`script/frontend/mod/cr_iee_mixer_helpers.lua` khai báo ID 1104464346 ở dòng 51 và gọi
`mixer_enable_custom_faction("1104464346")` ở dòng 214 trong UI-created callback.
Tên bảng `mixer_factions_that_require_other_mods` không có nghĩa faction này bị khóa mặc định:
IEE tự enable placeholder này. Không cần tự ý thêm một unlocker thứ ba.

Row `frontend_faction_leaders` dùng `mixer_dummy` và tài nguyên placeholder khác;
nó không xác định Lord thật trong campaign. Row `faction_agent_permitted_subtypes` chỉ mô tả
quyền subtype, không chứng minh Miao Ying/Yuan Bo/etc. đang là leader.

IEE MCT tùy chọn `epidermus_to_khuresh` (giữ nguyên cách viết trong source) có thể chuyển Dai Loa
cho Epidemius khi region vẫn do Agents of the Moon sở hữu, và teleport leader của faction này.
Nguồn: `script/campaign/cr_combi_expanded/mod/cr_iee_mct_options.lua`, dòng 275–283.
Giá trị mặc định trong code là false; cấu hình người chơi và mod khác có thể đổi kết quả runtime.

## Khuresh

Dùng group DB **`cai_region_hint_area_khuresh`** làm ranh giới có thể tái lập: **42 regions,
17 provinces, 14 faction owners** trong startpos. Đây là AI hint group của IEE, không tuyên bố
là mọi định nghĩa địa lý/lore của Khuresh. Danh sách đầy đủ region/province/owner/subculture:
`reports/khuresh-startpos.tsv`.

| Owner | Số region |
|---|---:|
| Agents of the Moon | 4 |
| Clan Rikek | 4 |
| Gate Guards | 1 |
| Guests of the Raja | 1 |
| Harbingers of Pain | 2 |
| Leofric's Fellowship | 2 |
| Loesh's Indulgence | 4 |
| Orobagor Warherd | 1 |
| Rotten Knot | 3 |
| Scions of Xholankha | 4 |
| Servants of the Blood Nagas | 3 |
| Snakebiters | 4 |
| Speaking Trees | 5 |
| Stormraven | 4 |

Các tên liên quan Naga không tự động có nghĩa là race Naga riêng. Ví dụ Servants of the Blood Nagas
dùng `wh3_main_sc_kho_khorne` trong DB đang cài. Mỗi faction cần kiểm tra row thực trước khi chuyển sang Cathay.
