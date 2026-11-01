# Moon Cathay — IEE / MIXER submod

Legendary Lord: **Huyen Ve, Warden of Long Vi** (official name, 02/11/2026).
Current integrated build: `build/huyen-ve-equipment/mc_huyen_ve_v14_native_icons.pack`.
Five items and Custom Battle item links statically validated; runtime confirmation pending. See
[Lord identity and build notes](docs/LEGENDARY-LORD.md).

[Trang bị v14 và cách test Custom Battle](docs/HUYEN-VE-EQUIPMENT.md).

[Kiểm tra hệ thống nhiệm vụ Agents of the Moon](docs/FACTION-MISSIONS.md)
(02/11/2026): đối chiếu script và save 30/10; chưa thay đổi nhiệm vụ.

Project: `D:\Warhammer3_Modding\moon_cathay` · Phase 1 · 30/10/2026 (Asia/Saigon).

Đã thiết lập repository, kiểm kê dependency, phân tích DB/startpos và đối chiếu save
Agents of the Moon hiện có. Chưa thay gameplay/campaign, chưa deploy, chưa publish.
Tên project và prefix `mc_` là tên kỹ thuật tạm thời, có thể đổi ở phase sau.

- [Báo cáo Phase 1](docs/PHASE1-REPORT.md)
- [Faction và Khuresh](docs/FACTION-ANALYSIS.md)
- [Build, tái lập phân tích và test](docs/BUILD-TEST.md)
- [Kiến trúc và lộ trình](docs/ARCHITECTURE.md)
- [Nguồn và giới hạn bằng chứng](docs/SOURCES.md)

## Cấu trúc

| Thư mục | Vai trò |
|---|---|
| `src/db`, `src/text`, `src/script` | Source tự viết; đang trống |
| `assets/authored` | Asset tự tạo/có quyền sử dụng |
| `config` | Mẫu cấu hình; `local.json` chứa đường dẫn máy, được ignore |
| `tools` | Trích xuất chỉ đọc, phân tích, tạo skeleton, kiểm tra hash |
| `tests` | Phạm vi kiểm chứng |
| `reports` | Dữ kiện, inventory, fingerprints, log lỗi schema |
| `reference/local` | Trích xuất bên thứ ba để nghiên cứu riêng; không vào Git/release |
| `build`, `dist` | Build tạm / bản phát hành; không vào Git |

Pack Phase 1 trong `build/` là pack loại **mod**, chỉ chứa dependency và metadata RPFM.
Nó không có nội dung chơi được. Không đưa pack này vào game để thay faction.

Chạy lại kiểm tra bằng PowerShell từ project:

```powershell
./tools/Verify-Dependencies.ps1
./tools/Build-Skeleton.ps1
$cfg = Get-Content config/local.json -Raw | ConvertFrom-Json
& $cfg.python tools/Validate-Phase1.py
```

Không kèm dependency binary/asset, không tự động tải công cụ, không có bước deploy.
