# Da Lien — da hồng ấm nhẹ

Tiếp nối: tint đã được chuyển sang diffuse DDS trong
[v22](DA-LIEN-V22-APPEARANCE.md); ghi chú chưa bake/deploy bên dưới là lịch sử.

03/11/2026. Người dùng yêu cầu giảm cảm giác trắng nhợt, da hồng hào như người sống.

- Scene mới: `build/da-lien-skin-warm/da-lien-skin-warm.blend`.
- Dựa trên `build/da-lien-collar-edit/da-lien-collar-removed.blend`; giữ bản bỏ cổ áo.
- Chỉ tạo bản sao material của `Neferata_Body`, thêm node `DL_Subtle_Human_Skin`
  trước Base Color của Principled BSDF. Multiply linear RGB: 0.98/0.85/0.80.
  Đây là tint ấm nhẹ, giữ họa tiết/chi tiết texture; có thể chỉnh lại hoặc bypass node.
- Không sửa pixel của texture PNG/DDS nguồn, normal/material-map, tóc, quần áo,
  vũ khí, rig, geometry, UV hoặc skin weights. Material các mesh khác giữ nguyên.
- Report: `build/da-lien-skin-warm/skin-warm-report.json`.
- Tool: `tools/Warm-Da-Lien-Skin.py`.

Hiện mới là material trong scene Blender. Khi đưa vào game phải bake/chuyển tint
sang diffuse texture phù hợp rồi kiểm tra DDS/mipmaps và màu trong engine;
không coi node Blender là effect tự được RMV2 export. Game pack v21 chưa đổi.
