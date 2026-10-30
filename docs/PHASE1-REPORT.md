# Báo cáo thực tế Phase 1

Ngày 30/10/2026, Asia/Saigon. Chỉ setup và phân tích.

## Máy và dependency

Steam registry: `C:\Program Files (x86)\Steam`. `libraryfolders.vdf` trỏ game tới
`F:\SteamLibrary`. Manifest `appmanifest_1142710.acf` xác nhận build ID `25961564`.
Game: `F:\SteamLibrary\steamapps\common\Total War WARHAMMER III`.
Workshop: `F:\SteamLibrary\steamapps\workshop\content\1142710`.

| Mod | Workshop ID | Pack đã xác minh | Bytes |
|---|---|---|---:|
| IEE | 3007996493 | `F:\SteamLibrary\steamapps\workshop\content\1142710\3007996493\!cr_immortal_empires_expanded.pack` | 3,223,934,769 |
| MIXER | 2859968660 | `F:\SteamLibrary\steamapps\workshop\content\1142710\2859968660\!b_mixer.pack` | 27,452,617 |

SHA256 đầy đủ và thời gian file nằm trong `reports/dependency-fingerprints.json`.
Đã thấy MCT `2927955021/groovy_mct.pack` và Custom Lord Creation
`3660806424/fuwuvi_custom_lord_creation.pack`. Các mod khác gồm DeepWar AI,
AI Coordinated Assault và pack AI của Zach. Đây là inventory trên đĩa, không khẳng định
mọi pack đều bật hoặc tương thích. Chưa phân tích API của Custom Lord Creation.

## Công cụ

| Công cụ | Kết quả thực tế |
|---|---|
| RPFM CLI/UI | Có tại `D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc`. **CLI thực tế là 4.6.3**, xác minh `--version`; tên thư mục cũ không phải version binary. CLI đã chạy thành công. GUI chưa mở. |
| RPFM cũ | Có thư mục 4.3.8 và 1.6.1; không dùng |
| WH3 schema | Có ở `C:\Users\ADMIN\AppData\Roaming\FrodoWazEre\rpfm\config\schemas\schema_wh3.ron`, mtime 04/10/2025; chưa cập nhật |
| EditSF | `D:\Mod TW3k\EditSF 1.1.1\EditSF.exe`; thư viện cũ không đọc được ABCB của startpos này |
| SaveParser | `D:\Mod TW3k\SaveParser\SaveParser.exe`, file version 1.43.2.1; chưa xác nhận khả năng đọc WH3 hiện tại |
| Git | Đã chạy, version 2.56.0.windows.2 |
| Python | Runtime có sẵn tại đường dẫn trong `config/local.json`; dùng standard library, không pip install |
| Assembly Kit WH3 | Chưa tìm thấy trong manifest Steam đã kiểm tra / thư mục game; installer Three Kingdoms không phải WH3 kit |
| Blender / AssetEditor / RME | Chưa xác minh executable phù hợp qua các đường dẫn đã tìm; thư mục `D:\Blender` không đủ chứng minh đã có tool dùng được |

## Kết quả theo nhiệm vụ

1. Tìm được game, Steam library và Workshop qua registry + manifest.
2. Xác định đúng hai pack và hash để phát hiện cập nhật.
3. Kiểm tra tool thực có; ghi rõ version và giới hạn schema/ESF.
4. Tạo cấu trúc source, authored assets, tools, docs, tests, private references, build, dist.
5. Tạo Git `main`, `.gitignore`, `.gitattributes`, quy tắc `AGENTS.md`; không cấu hình remote/push.
6. Lập inventory IEE: 13,970 đường dẫn nội dung (RPFM list), 272 DB fragments thuộc 181 loại bảng,
   42 script, 26 loc. Các nhánh lớn là terrain, rigidmodels, ui; không sao chép chúng vào source.
7. Xác định faction, culture/subculture, bốn region và Lord; đối chiếu save hiện có. Xem báo cáo faction.
8. Thiết kế submod nhỏ, dependency rõ ràng, không mang startpos/map của IEE theo.
9. Viết hướng dẫn build, test, mở rộng và script tái lập phân tích.
10. Tạo skeleton pack riêng, mở lại bằng RPFM và kiểm tra binary; chỉ metadata, không gameplay.

## Giới hạn và phần chưa làm

- RPFM xuất một số DB thành binary vì schema không phù hợp; danh sách chính xác nằm trong
  `reports/iee-extraction.log` và `reports/mixer-extraction.log`. Không coi file binary đó là TSV hợp lệ.
- Bộ đọc ESF tự viết là read-only cho cấu trúc đã gặp. Nó kiểm tra kích thước node/string table/LZMA;
  bỏ qua nhánh diplomacy/CAI không liên quan. Không dùng làm writer hoặc coi là editor tổng quát.
- Chưa kiểm thử game, màn hình chọn faction, Lua, save/load sau thay đổi hoặc campaign multiplayer.
- Chưa tạo Legendary Lord, roster, cờ, model, province, family tree hay skill tree.
- Không sửa game/Workshop/save; không cài hoặc cập nhật công cụ; không phát hành asset bên thứ ba.
- Hash baseline được lập trong phiên phân tích, không phải checksum lịch sử trước phiên.

## Bước tiếp theo sau khi mở Phase 2

Ưu tiên một thay đổi nhỏ về tên/cờ/màu của faction hiện hữu, rồi kiểm thử baseline IEE + MIXER + MCT
và submod trên campaign mới. Trước khi dùng bảng chưa giải mã được, cần được phép cập nhật schema/tool.
Sau đó mới làm roster và Lord; thay topology/province và family simulation là các dự án riêng có rủi ro cao hơn.
