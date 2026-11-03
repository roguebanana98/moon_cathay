# Da Lien — bỏ mảnh cổ áo dựng phía sau

Tiếp nối: chỉnh sửa đã được xuất từ raw mesh gốc và deploy trong
[v22](DA-LIEN-V22-APPEARANCE.md); ghi chú chưa export/deploy bên dưới là lịch sử.

03/11/2026. Người dùng yêu cầu bỏ phần dựng sau cổ trong
`Neferata_Outfit_Sleeves_Collar`, giữ lại các phần khác.

- Đã lưu snapshot từ Blender đang mở, gồm thay đổi chưa lưu:
  `build/da-lien-collar-edit/da-lien-before-collar-edit-live.blend`.
- Bản chỉnh riêng: `build/da-lien-collar-edit/da-lien-collar-removed.blend`.
- Xóa riêng assembly cổ áo dựng gồm vỏ, lót, viền và trang trí gắn trên đó;
  giữ vòng cổ phía trước, cả hai tay áo, phần vai thuộc tay áo và mọi mesh khác.
- Mesh mục tiêu: 42.547 → 29.387 vertices, 66.320 → 46.992 faces;
  bỏ 13.160 vertices/19.328 faces thuộc 15 geometric islands của cổ áo.
- Đối chiếu chính xác phần giữ lại: tọa độ, weights, UV, thứ tự faces và normals
  không đổi (normal error 0). Sáu mesh khác có fingerprint không đổi;
  rig/bones/pose giữ nguyên. Material/texture nguồn không chỉnh.
- Report và ID các island: `collar-removal-report.json` cùng thư mục build.
- Tool: `tools/Remove-Da-Lien-Raised-Collar.py`; không weld/decimate/retopo phần giữ lại.

Đây là chỉnh sửa scene Blender để xem ngoại hình. Chưa export RMV2, chưa build
hoặc deploy thay pack v21; model trong game vẫn là bản test v21 trước đó.
Không ghi đè scene nguồn hoặc file Workshop.
