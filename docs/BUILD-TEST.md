# Build, phân tích và kiểm thử

## Phase 1 đã chạy

1. RPFM `pack list` đọc trực tiếp dependency, không lưu lại pack nguồn.
2. `tools/Extract-References.ps1` xuất DB/loc/scripts vào ignored `reference/local/` và startpos IEE.
   RPFM 4.6.3 có thể báo warning rồi xuất binary: luôn đọc log, không chỉ dựa vào exit code 0.
3. Python standard library đọc ABCB/CAAB, giải nén LZMA, kiểm tra giới hạn node và string tables.
4. DB/loc nối với ownership và character references để tạo báo cáo.
5. `Build-Skeleton.ps1` tạo pack mới tên GUID, thêm đúng hai dependency bằng RPFM,
   rồi đọc lại. Mỗi lần chạy tạo file mới, không ghi đè build cũ.
6. `Validate-Phase1.py` kiểm tra PFH5, loại mod, đúng dependency, chỉ metadata RPFM,
   bốn settlement, subtype Lord và 42 region/17 province/14 owner.
7. `Verify-Dependencies.ps1` đối chiếu SHA256 hai pack với baseline trong phiên.

## Tái lập dữ liệu

Mở PowerShell tại `D:\Warhammer3_Modding\moon_cathay`. `config/local.json` đã được tạo cho máy này.
Máy khác phải tự xác minh đường dẫn rồi dùng `local.example.json`; script không tải/cài gì.

```powershell
$cfg = Get-Content config/local.json -Raw | ConvertFrom-Json
./tools/Extract-References.ps1
& $cfg.rpfm -g warhammer_3 pack list -p $cfg.iee > reports/iee-pack-index.txt
& $cfg.rpfm -g warhammer_3 pack extract -p (Join-Path $cfg.game 'data/db.pack') -t $cfg.schema -F "db/cultures_subcultures_tables;$PWD/reference/local/vanilla"
& $cfg.rpfm -g warhammer_3 pack extract -p (Join-Path $cfg.game 'data/local_en.pack') -t $cfg.schema -F "text;$PWD/reference/local/vanilla"
& $cfg.python tools/inspect_esf.py reference/local/iee/campaigns/cr_combi_expanded/startpos.esf reference/local/startpos-compact.json > reports/esf-node-counts.json
& $cfg.python tools/inspect_esf.py 'C:\Users\ADMIN\AppData\Roaming\The Creative Assembly\Warhammer3\save_games\Agents of the Moon.11158371198.save' reference/local/save-compact.json > reports/save-node-counts.json
& $cfg.python tools/Summarize-Analysis.py
./tools/Build-Skeleton.ps1
& $cfg.python tools/Validate-Phase1.py
./tools/Verify-Dependencies.ps1
```

Save path ở trên là file đã xác minh trong phiên này; nếu file không còn tồn tại, không tự suy đoán tên mới.
Bộ đọc có thể dùng vài GB RAM trong bước giải mã và mất khoảng một phút hoặc hơn cho từng snapshot.
Nó bỏ qua nội dung diplomacy/CAI theo kích thước đã khai báo, không kiểm chứng logic những nhánh đó.
Các version assertion trong summarizer cố ý dừng khi layout khác; không bỏ assertion để ép đọc bản mới.

## Build nội dung ở phase sau

Hiện script build **chỉ tạo skeleton**. Nó không tự đóng gói `src/`, và chưa có pipeline release gameplay.
Sau khi được yêu cầu mở Phase 2:

- Tạo pack `mod` mới trong build; dependency manager tham chiếu tên pack IEE/MIXER, không merge chúng.
- Dùng schema tương thích cho từng table version. Giữ header TSV theo RPFM.
- Chỉ import source tự viết; DB/loc TSV cần `pack add --tsv-to-binary` theo help đã xác minh.
- DB row override phải được thử với thứ tự ưu tiên thực trong launcher. Không giả định tên file hoặc
  dependency header bảo đảm mọi kiểu xung đột; không hardcode thứ tự load chưa test.
- Chạy diagnostics bằng tool/schema tương thích trước release; kiểm tra thiếu foreign key và trùng key.
- Inventory pack đầu ra phải không chứa startpos, campaign_maps, terrain hay asset IEE/MIXER sao chép.
- Ghi hash dependency, game build ID, phiên bản submod và nguồn/quyền của asset vào release notes.

## Ma trận test trong game — CHƯA CHẠY

| Test | Điều kiện đạt |
|---|---|
| Baseline | Game + IEE + MIXER + MCT, campaign Expanded mới khởi động được |
| Frontend | Agents of the Moon hiển thị đúng, không duplicate leader/faction |
| Submod cosmetic | Tên/cờ/màu đúng ở frontend, campaign, battle; không đổi owner/roster ngoài mục tiêu |
| MCT | Mặc định và bật chuyển Epidemius: không crash, ownership/teleport đúng |
| Save/load | Save mới, load lại, end turn; không nhân đôi listener hoặc state |
| Dependency absent | Không quảng bá hỗ trợ thiếu IEE/MIXER; thông báo/khóa lựa chọn phù hợp nếu triển khai |
| Compatibility | Bật thêm từng mod AI và Custom Lord Creation riêng, ghi mod list và lỗi |
| Upgrade | So sánh checksum/table version sau game/IEE/MIXER update; chạy lại baseline |
| Multiplayer | Chỉ công bố hỗ trợ sau khi kiểm tra sync/RNG/UI trên hai client |

Game logs hiện có tại `%APPDATA%\The Creative Assembly\Warhammer3\logs` và `crash_report`.
Không tự bật logging bằng API hay tên file chưa xác minh. Không dùng save đang chơi để test migration phá hủy.

## Git

`main` chứa source công cụ, docs và factual reports. Không remote/push. `reference/local`, `build`, `dist`,
local config, pack, save và ESF bị ignore. Trước commit/release, dùng `git status`, `git diff --cached`
và `git ls-files` kiểm tra không lọt asset bên thứ ba. Không dùng `git add -f` để đưa reference vào repo.
