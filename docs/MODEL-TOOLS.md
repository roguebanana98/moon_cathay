# Bộ công cụ model WH3

Chuẩn bị ngày 2026-11-01 theo quyền tải và chuẩn bị công cụ của người dùng.
Thư mục chương trình: `D:\Warhammer3_Modding\tooling\model-workbench`.
Lối mở nhanh: thư mục con `Open Tools` gồm shortcut Blender, Asset Editor, Paint.NET và RPFM.

| Công cụ | Phiên bản | Vai trò |
| --- | --- | --- |
| RPFM | 4.5.4, đã có | Đọc/ghi pack, bảng DB, VMD, kiểm tra dependency |
| Asset Editor | 0.78 | Xem/kitbash model, material, rig và animation |
| Blender | 4.5.15 LTS portable x64 | Dựng mesh, UV, rig, skinning, LOD |
| Total War RigidModel add-on | 1.22.3 | Nhập/xuất RMV2 và ANIM trong Blender |
| Paint.NET | 5.1.12 portable x64 | Chỉnh texture, đọc/ghi DDS |
| DirectXTex | may2026 / 2026.5.8.1 | texconv chuyển đổi texture, texdiag kiểm tra codec/mipmap |

## Cấu hình đã chuẩn bị

- Blender dùng thư mục `portable`, cài add-on dưới `portable/scripts/addons/io_scene_rmv2` và bật trong user preferences. Không phụ thuộc hồ sơ Blender khác của người dùng.
- Texture Root Directory của add-on: `D:\Warhammer3_Modding\moon_cathay\reference\local\yuan-bo-model`.
- Asset Editor dùng cấu hình tại `C:\Users\ADMIN\AssetEditor\ApplicationSettings.json`: game Warhammer III, đường dẫn `F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data`, camera BlenderStyle. Có bản sao cấu hình trước thay đổi trong thư mục công cụ. Asset Editor giữ cache/log trong `C:\Users\ADMIN\AssetEditor`, dù chương trình được giải nén riêng.
- Các executable được ghi vào `moon_cathay/config/local.json`: blender, asset_editor, paint_net, texconv, texdiag.
- Tất cả binary và archive mới nằm trong tooling bị Git ignore. Nguồn và SHA-256 gói tải nằm trong `tooling/model-workbench/download-manifest.json`; đã đối chiếu với GitHub release digest hoặc checksum chính thức Blender.

## Kiểm tra đã thực hiện

- Blender chạy headless, add-on bật được và lưu preferences portable.
- Nhập skeleton humanoid01e: 96 bone.
- Nhập cả 4 LOD body Yuan Bo: 7 mesh, tổng 53,407 triangles.
- Nhập cả 4 LOD kiếm: 4 mesh, tổng 1,946 triangles.
- Cả 8 texture được Blender đọc có dữ liệu và kích thước đúng. Chi tiết tại `reports/model-tools-blender-check.json`.
- texconv/texdiag chạy được; texdiag đọc texture kiếm gốc và nhận BC1_UNORM_SRGB, 512×512, 10 mip.
- Paint.NET đã khởi động tới cửa sổ tài liệu trống. Asset Editor đã tạo dữ liệu khởi động và vào giao diện chính với `All Game Packs - Warhammer III [Read Only]`, status `Current Game: Warhammer III`.
- Chưa kiểm tra render model trong Asset Editor, export roundtrip hoặc model mới chạy trong game. Kiểm tra import không thay thế các bước này.

Chạy lại bài kiểm tra Blender bằng executable trên với `--background --python-exit-code 1 --python D:\Warhammer3_Modding\moon_cathay\tools\Verify-Blender-Model-Tools.py`.

## Bắt đầu dựng lord

Mở shortcut Blender; File → Import có RigidModel v2 và Total War Animation. Import skeleton `reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim`, chọn armature rồi import body RMV2. Kiếm là mesh static riêng; khi lắp theo chuyển động phải dùng attachment weapon_2 đã khảo sát. Không coi việc import hai mesh chung vào Blender là đã tự động tái tạo VMD.

Giữ model tham khảo trong reference/local, lưu bản chỉnh dưới build hoặc assets/authored tùy nội dung. Tạo variant và VMD riêng cho lord mới. Chưa có thao tác ghi vào game, Workshop hoặc pack đang chơi trong lần chuẩn bị này.

Nguồn tải chính thức:

- [Asset Editor release](https://github.com/donkeyProgramming/TheAssetEditor/releases/tag/v.078)
- [Blender 4.5 downloads và checksum](https://download.blender.org/release/Blender4.5/)
- [Total War RigidModel add-on](https://github.com/robert-d-schultz/rmv2_anim_blender_import_export/releases/tag/v1.22.3)
- [Paint.NET portable](https://github.com/paintdotnet/release/releases/tag/v5.1.12)
- [Microsoft DirectXTex](https://github.com/microsoft/DirectXTex/releases/tag/may2026)
