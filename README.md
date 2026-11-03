# Moon Cathay — IEE / MIXER submod

Legendary Lord: **Huyen Ve, Warden of Long Vi** (official name, 02/11/2026).
Latest recorded private test deployment (03/11/2026):
`build/huyen-ve-v25-quest-chain/mc_huyen_ve_v25_quest_chain_test_r7.pack`.
R7 places Huyen Ve and his existing army beside Long Vi at new-campaign creation through a native startup callback. Loaded campaigns are unaffected. File/Lua checks pass; live new-game placement is pending.

R6 replaces Huyen Ve's sword with the approved user fantasy longsword, four LODs and native DDS materials. Exported-model checks pass; in-game appearance remains for testing.

All six [quest chapters](docs/HUYEN-VE-V25-QUEST-INTEGRATION.md) are implemented:
pendant at 6, Da Lien + Moonstone rescue at 8, armour at 10, Hero investigation/
seal at 14, army kills/lantern at 18 and paid sword restoration at 22.
v25 r7 is enabled; r6 is retained inactive for rollback. Old visual-test grants/spawn are
suppressed in progression. 58 chain tests, 13 chapter-one regressions, 10 Hero
reward scenarios and battle/native-library tests pass with fake engine boundaries;
DB roundtrip and diagnostics pass. Native IEE new-campaign smoke confirms the
controller starts and old visual Hero spawn is suppressed. Full live campaign
playthrough remains pending; see the integration report for engine QA limits.

The inherited features and historical deployment notes follow.
Adds [Crimson Moonstone](docs/DA-LIEN-V24-MOONSTONE.md), Da Lien's signature
Arcane Item: +5 Winds reserve capacity, +5% ward save and one-use bound heal.
Includes one-time campaign grant/equip and Custom Battle equipment access.
Adds [Da Lien's Moon Arts skill tree](docs/DA-LIEN-V23-SKILL-TEST.md): six
Yin/Heavens/Life spells, caster/Hero basics, six uniques, Mentor and scoped
one-time migration from the old Metal test tree. Runtime testing is pending.
Includes [Da Lien's approved appearance](docs/DA-LIEN-V22-APPEARANCE.md): removed
rear collar, warmer human skin DDS and silver/gold moon-staff head.
Adds [Custom Battle access for Da Lien](docs/DA-LIEN-V21-CUSTOM-BATTLE.md) under
Grand Cathay → Heroes, now with the six-spell Moon Arts test preset.
Adds [Da Lien's Hero appearance test](docs/DA-LIEN-V20-VISUAL-TEST.md), spawning
once near owned Long Vi in v20–v24. v25 uses the chapter-2 quest reward instead.
Includes the approved appearance/native animation fix, campaign name and portraits,
five test-granted items, re-equip hotfix and Moonlit Command. Build and installed
pack SHA256 match; v25 enabled and v24 disabled with launcher backup. Full runtime
confirmation is pending. See
[Lord identity and build notes](docs/LEGENDARY-LORD.md).

- [Ngoại hình đã duyệt và animation fix](docs/HUYEN-VE-APPROVED-MODEL.md).
- [Tên, portrait, campaign test grant và re-equip](docs/HUYEN-VE-CAMPAIGN-V17.md).
- [Moonlit Command v19 và Army of Renown native](docs/HUYEN-VE-MOONLIT-COMMAND.md).
- [Thông số trang bị và cách test Custom Battle](docs/HUYEN-VE-EQUIPMENT.md).
- [Thiết kế nhiệm vụ đã duyệt](docs/HUYEN-VE-QUEST-CAMPAIGN-DESIGN.md): năm nhiệm vụ
  campaign nhận item, một quest battle sớm chương 2/cấp 8 nhận Da Lien + ngọc;
  đã tích hợp progression trong v25; cần playthrough campaign thật để xác nhận.
- [Goal và checklist hiện hành](PROJECT_GOALS.txt).

[Kiểm tra hệ thống nhiệm vụ Agents of the Moon](docs/FACTION-MISSIONS.md)
(02/11/2026): đối chiếu script và save 30/10; chưa thay đổi nhiệm vụ.

Project: `D:\Warhammer3_Modding\moon_cathay` · cập nhật 03/11/2026 (Asia/Saigon).

Đã thiết lập repository, kiểm kê dependency, phân tích DB/startpos và đối chiếu save
Agents of the Moon hiện có. Đã mở rộng sang private gameplay prototype và deploy
test theo phạm vi người dùng cho phép; chưa publish. Báo cáo Phase 1 là lịch sử.
Tên project và prefix `mc_` là tên kỹ thuật tạm thời, có thể đổi ở phase sau.

- [Báo cáo Phase 1](docs/PHASE1-REPORT.md)
- [Faction và Khuresh](docs/FACTION-ANALYSIS.md)
- [Build, tái lập phân tích và test](docs/BUILD-TEST.md)
- [Kiến trúc và lộ trình](docs/ARCHITECTURE.md)
- [Nguồn và giới hạn bằng chứng](docs/SOURCES.md)

## Cấu trúc

| Thư mục | Vai trò |
|---|---|
| `src/db`, `src/text`, `src/script` | Source DB, localization và Lua của submod |
| `assets/authored` | Asset tự tạo/có quyền sử dụng |
| `config` | Mẫu cấu hình; `local.json` chứa đường dẫn máy, được ignore |
| `tools` | Trích xuất/phân tích, build, validate, công cụ model và scoped test deployment |
| `tests` | Phạm vi kiểm chứng |
| `reports` | Dữ kiện, inventory, fingerprints, log lỗi schema |
| `reference/local` | Trích xuất bên thứ ba để nghiên cứu riêng; không vào Git/release |
| `build`, `dist` | Build tạm / bản phát hành; không vào Git |

Pack skeleton Phase 1 trong `build/` là pack loại **mod**, chỉ chứa dependency và metadata RPFM.
Nó không có nội dung chơi được. Không đưa pack này vào game để thay faction.

Chạy lại kiểm tra bằng PowerShell từ project:

```powershell
./tools/Verify-Dependencies.ps1
./tools/Build-Skeleton.ps1
$cfg = Get-Content config/local.json -Raw | ConvertFrom-Json
& $cfg.python tools/Validate-Phase1.py
```

Các lệnh skeleton trên không deploy. Private gameplay pack dùng quy trình build/test
riêng ghi trong tài liệu từng phiên bản. Không công bố pack chứa asset bên thứ ba;
model đã duyệt hiện chỉ dùng cho private local test.
