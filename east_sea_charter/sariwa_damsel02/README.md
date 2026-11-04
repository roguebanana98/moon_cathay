# Sariwa — Endo Damsel 02, textile v1

## Latest model: Naga staff v2

`Sariwa_Damsel02_Naga3_v2.blend` adds a cast-bronze **three-headed Naga** crown with a higher middle head, fanned side heads, flared cobra hoods, tapered skulls and six small jade eyes. The native orb is removed; the original shaft below the crown and the grip remain unchanged. The crown is an editable UV-unwrapped mesh attached through the original staff's `be_prop_5` constraint. Test rotations produced zero attachment-matrix error. Character, clothing, hair and sword geometry remain unchanged. No game pack has been updated.

`Sariwa_Naga3_full_v2.png` and `Sariwa_Naga3_detail_v2.png` show the full model and the crown. `naga3_report.json` records geometry and attachment checks. The earlier textile-v1 scene remains available separately.

Chosen base: **[Endo] Damsel campaign variant 02**, using `endo_damsel_head_04` and `endo_damsel_body_02`. The dark wavy hair, face, source skin texture, mesh, UV coordinates, vertex weights, native humanoid01b rig, sword and staff are retained.

Clothing remains ivory white with jade and muted bronze borders. Ornament uses geometric diamond/chevron weaving, intertwined Naga-inspired scale bands and a hem of stylized long-beaked birds and triangular rays inspired by Southeast Asian textiles and Dong Son bronze drum decoration. This is fantasy ornament, not a reproduction of one historical costume.

Files:

- `Sariwa_Damsel02_Textile_v1.blend`: single-character textured scene with packed images; front, back and side cameras.
- `Sariwa_front_v1.png`: rendered model preview.
- `textures/edh_sariwa_body_base_colour_v1.png`: final 2048×2048 clothing albedo on the native UV layout.
- `textures/edh_sariwa_body_base_colour_v1.dds`: BC3 sRGB with mipmaps, ready for an asset integration step.
- `textures/edh_sariwa_body_ai_atlas_v1.png`: raw imagegen edit, retained for traceability.
- `texture-prompt-v1.txt`: exact prompt, using the built-in imagegen tool, not the API/CLI fallback.
- `asset_report.json`: identity and mesh/UV/weight verification.

The raw edited atlas was limited to garment areas through the original cloth mask in Blender, keeping the original skin, belt and sandals outside the edit. The resulting material was baked to a new UV albedo. Original normal and material maps remain; the ornaments are a surface-colour treatment. Faction tint is bypassed on the preview clothing so the white base and ornament stay visible. The source Workshop pack and earlier preview files are unchanged. No game pack was created or installed in this step.
