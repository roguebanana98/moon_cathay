# Da Lien — đầu trượng mặt trăng

Tiếp nối: đã export và deploy cùng da ấm/bỏ cổ áo trong
[v22](DA-LIEN-V22-APPEARANCE.md). Các ghi chú scene-only bên dưới là mốc trước tích hợp.

03/11/2026. Người dùng đồng ý màu da hồng nhẹ và yêu cầu thay đầu trượng hình ly
bằng biểu tượng mặt trăng. Scene hiện hành:
`build/da-lien-moon-staff/da-lien-moon-staff.blend`.

- Giữ bản bỏ cổ áo và material da hồng ấm từ scene trước.
- Bỏ cụm ly gồm thân ly, miệng, viền, chân đỡ và trang trí gắn trên cụm đầu;
  giữ nguyên shaft/tay cầm và tua phía dưới của `Neferata_Staff`.
- Thêm trăng lưỡi liềm hướng hai đầu lên, mặt bạc, cạnh vát vàng; khớp nối
  men đỏ rượu/vòng vàng nối với shaft để hợp bảng màu trang phục.
- Các mesh đầu mới đều theo `be_prop_5`, cùng native rig với trượng gốc.
- Phần shaft giữ lại đã đối chiếu chính xác coords/UV/normals/faces; mọi mesh
  và material khác không đổi. Các mesh đầu mới đã kiểm tra manifold kín.
- Tool: `tools/Build-Da-Lien-Moon-Staff.py`; report/island IDs/hashes trong
  `build/da-lien-moon-staff/moon-staff-report.json`.

Đây là bản Blender xem ngoại hình, chưa export/deploy vào game v21. Trước khi
tích hợp cần atlas/bake vật liệu đầu mới và tint da, kiểm tra prop export/attachment
và clipping trong stand/run/cast/attack. Không thay hoặc ghi đè Workshop source.
