# Moon Cathay — IEE / MIXER submod

Legendary Lord: **Huyen Ve, Warden of Long Vi** (official name, 02/11/2026).
Latest recorded private test deployment (03/11/2026):
`build/huyen-ve-v19-moonlit-command/mc_huyen_ve_v19_moonlit_command.pack`.
Includes the approved appearance/native animation fix, campaign name and portraits,
five test-granted items, re-equip hotfix and Moonlit Command. Build and installed
pack SHA256 match; full runtime confirmation is pending. See
[Lord identity and build notes](docs/LEGENDARY-LORD.md).

- [Ngoại hình đã duyệt và animation fix](docs/HUYEN-VE-APPROVED-MODEL.md).
- [Tên, portrait, campaign test grant và re-equip](docs/HUYEN-VE-CAMPAIGN-V17.md).
- [Moonlit Command v19 và Army of Renown native](docs/HUYEN-VE-MOONLIT-COMMAND.md).
- [Thông số trang bị và cách test Custom Battle](docs/HUYEN-VE-EQUIPMENT.md).
- [Thiết kế nhiệm vụ đã duyệt](docs/HUYEN-VE-QUEST-CAMPAIGN-DESIGN.md): năm nhiệm vụ
  campaign nhận item, một quest battle cuối nhận LH mới; chưa triển khai.
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
