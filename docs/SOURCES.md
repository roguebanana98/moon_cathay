# Nguồn và độ tin cậy

Ưu tiên binary/manifest trên máy ngày 30/10/2026. Snapshot phân tích không bảo đảm tương thích
với một bản game/Workshop tương lai hoặc cấu hình mod runtime khác.

## Nguồn local

- Steam registry và `C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf`.
- `F:\SteamLibrary\steamapps\appmanifest_1142710.acf` (build ID; không đưa Steam user ID vào report).
- Hai Workshop pack theo `reports/dependency-fingerprints.json`.
- RPFM CLI `--version`, `pack list/extract/create/add/add-dependency-pack --help`.
- IEE export DB/loc/script, startpos `cr_combi_expanded`; MIXER export scripts.
- Vanilla `data/db.pack` culture mapping và `data/local_en.pack` name localization.
- Existing save `Agents of the Moon.11158371198.save`, chỉ đọc để đối chiếu leader/ownership.

DB và loc sử dụng RPFM TSV, quoting disabled. Các file không giải mã được được giữ ở private references,
không coi là dữ liệu đã phân tích. Bảng màu và ID lưu trong factual JSON; không lưu asset texture/model vào Git.

## Nguồn upstream đã tra cứu

- [IEE — trang tác giả trên Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3007996493)
- [MIXER — trang tác giả trên Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=2859968660)
- [RPFM repository](https://github.com/Frodo45127/rpfm)
- [RPFM ESF format overview](https://raw.githubusercontent.com/Frodo45127/rpfm/master/rpfm_lib/src/files/esf/mod.rs)
- [RPFM CBAB reader](https://raw.githubusercontent.com/Frodo45127/rpfm/master/rpfm_lib/src/files/esf/cbab.rs)
- [RPFM node format](https://raw.githubusercontent.com/Frodo45127/rpfm/master/rpfm_lib/src/files/esf/utils.rs)
- [RPFM PFH5 format](https://raw.githubusercontent.com/Frodo45127/rpfm/master/rpfm_lib/src/files/pack/pack_versions/pfh5.rs)
- [EditSF fork mô tả ABCB support](https://github.com/xADDBx/EditSF) — chỉ đọc thông tin, không tải/cài binary.

Đã gặp GitHub API rate limit khi thử lấy file tree, sau đó đọc các source URL công khai đã xác minh.
Source upstream dùng để hiểu format, không thay công cụ đang cài hoặc cập nhật schema.
Thông tin parser tự viết không phải chứng nhận của RPFM. Header/string table/node boundaries và
các liên kết faction-region-character đã được kiểm tra trên hai snapshot thực.

Trang Steam qua web có phần boilerplate incompatibility/removal; không sử dụng phần đó làm kết luận
rằng mod local bị gỡ/hỏng. Kết quả report dựa trên file local và chưa có smoke test trong game.

## Quyền và phát hành

Không có giấy phép tái phân phối asset/code IEE/MIXER được cấp trong tác vụ này.
Chỉ dùng private extraction để nghiên cứu. Không kèm chúng vào Git, build gameplay hoặc release.
Asset mới cần provenance riêng. Chưa chọn license cho source project của người dùng.
