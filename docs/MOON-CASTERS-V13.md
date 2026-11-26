# Moon casters v13: model and recruitment preview

The user selected three Hakutaku Diviner appearances for three new Agents of the Moon wizard subtypes. The user explicitly chose to decide spell lists later. This build therefore implements models, English names, recruitment and basic campaign actions; it is not a completed elemental spell roster.

| Source model | Hero | Palette |
|---|---|---|
| 1 | Pyromancer | Charcoal and red |
| 2 | Astral Weaver | Charcoal and silver garment |
| 3 | Tidecaller | Dark blue garment |

Original faces, horns, accessories and body geometry are retained. Astral Weaver uses the charcoal garment textures with neutral silver shader bakes; Tidecaller uses darker blue shader bakes. The original cutout alpha is preserved. No AI-generated artwork. Separate rendered cards and campaign portraits show each actual model.

## Recruitment and balance

- Faction: `cr_cth_agents_of_the_moon` only. All three are `wizard` heroes.
- Recruitment: the existing Celestial Tower chain, `wh3_main_cth_magic_tower_1`, `_2`, `_3`, matching the Astromancer's native availability at those buildings.
- Capacity: the existing shared wizard/Astromancer pool. No extra starting capacity or per-subtype capacity effects; Astromancer's normal capacity requirements still apply.
- Native foot Astromancer recruitment cost, upkeep and combat stats are retained. Female names/art/voice and the matching native animation links are used. No new building, auto-spawn, quests or mounts.
- General skills retain native resistance, support, campaign actions and innate traits. Heavens spells, starting Harmonic Convergence, mounts and Astromancer-specific unique/army branches are deliberately omitted pending the user's spell design. No temporary Fire/Yin/Water lore was assigned.

## Models and animation

Source is the read-only local Workshop pack `3270368516/@mustdy_sarv_hakutaku_diviner.pack`. Dependency geometry, WSModels, materials and texture paths are isolated beneath `variantmeshes/wh_variantmodels/mc_moon_casters/`; private VMDs use each new subtype name. No original Sarvente, native or other-mod graphics paths are overridden.

All three rigid models preserve the original geometry bytes and four LODs, with 27/26/24 parts respectively per LOD. No skinning conversion or head graft. Battle lookup: native `hu1e_mage_storm_dragon`; campaign lookup: native `cam_hu1e_mage_storm_dragon`. The native compiled battle BIN was verified; no custom source-only lookup that could cause the previous T-pose problem. Native animations remain referenced, not bundled.

Actual namespaced WSModels were imported into Blender on the native 96-bone humanoid01e skeleton. Seven native clips per model (stand, walk, run, forward cast, upward cast, attack, campaign run), three sampled frames per clip: 63 finite pose samples. Motion checks passed for moving clips. This is a static/Blender check, not proof of in-game behavior or absence of cloth/accessory clipping.

Editable, texture-packed scene: `assets/working/moon-casters/moon-casters-models.blend`. Checkpoint, source hash and model mapping: `assets/working/moon-casters/checkpoint.json`. Review image: `build/moon-casters-v13/renders/three-casters.png` (left to right: Pyromancer, Astral Weaver, Tidecaller).

## Pack and verification

Installed and enabled: `mc_moonshadow_heroes_v13_three_casters.pack` (v12 retained disabled, launcher backed up). SHA256: `841d7c91ccab5c97442d9538189e8f4db6a6ec4449c9f8debaf35cd3c31842ea`. Pack, additive over installed v12. Every existing payload is byte-identical, including Da Anh/Moonshadow models, v12 skills and turn-one AP Lua. All added loc is English ASCII. Namespace dependency checks, DB/loc export roundtrip and RPFM diagnostics passed with zero blocking issues.

Build inputs/output and reports: `build/moon-casters-v13/models.json`, `model-review.json`, `pack-validation.json`, `diagnostics.txt`, `deployment.json`. No public upload, Git push, game launch, native/Workshop or save modifications.

Scripts, in order: `tools/Prepare-Moon-Caster-Models.py`, Blender background `tools/Review-Moon-Caster-Models.py`, `tools/Build-Moon-Casters-Pack.py`, `tools/Deploy-Moon-Casters.py`. Completed deployed packs are protected from rebuild.

## In-game check

Restart the game with v13 as the sole active Moonshadow roster pack. With an Agents of the Moon province containing a Celestial Tower and an available native wizard slot, inspect the recruitment list and all three cards. Recruit one and check its campaign portrait, map movement and battle model/animations. Confirm other Cathay factions cannot recruit these subtypes and that wizard capacity did not increase. Elemental spell trees remain pending by request.
