# Assault General campaign appearance repair - private v25

User reports the wrong Assault General model both on the campaign map and in the character window. The packed body/weapon/VMD path still points to the approved edited gallery08 model; this update does not replace or edit that geometry.

## Evidence and fix

The previous Assault art set was female-only (is_male=false), unlike the original donor guanshanart (is_male=true). This is an observed data mismatch and a plausible fallback cause, not a proven in-game diagnosis. Added male-compatible mc_assault_general_art_male plus campaign art1986113100, both pointing to the same approved mc_assault_general_uniform/VMD as the existing female art set. Added male portrait-settings aliases to the already-approved Assault images. Campaign politician filename was blank; all four uniform model fields now explicitly point to mc_assault_general.

A narrowly scoped campaign script calls the native cm:add_character_model_override(character, art_set) for mc_assault_general in cr_cth_agents_of_the_moon only. It chooses the matching male/female art set using the native is_male() API. It runs after save load, handles new characters, selection, faction changes, recovery and turn-start fallback scans. This repairs old characters without spawning/replacing them or changing skills, equipment, level, mounts or movement. The session cache avoids repeated turn-start binding; selection can refresh a stale model assignment.

The script is limited to main_warhammer and cr_combi_expanded. No Sariwa, Huyen Ve, Bastion, hero or third-party script is changed. The active Custom Lord Creation mod has a separate art-mapping/gender subsystem; this repair does not patch its files or register ambiguous mixed-gender mappings. It binds this subtype after creation regardless of a prior appearance choice.

## Validation

- Lua boundary tests: existing/new male/female characters, selection refresh, wounded recovery, faction transfer, reload, both supported campaigns and unsupported campaign; no other subtype/faction affected. Character identity, XP, skills and equipment preserved in tests.
- All new/changed DB tables and packed Lua roundtripped. Zero blocking RPFM diagnostics.
- The only existing payload changed is the two-lord agent_uniforms table, and only Assault's politician filename changes there. Every other existing payload is byte-identical, including approved body/weapon, battle variants, stats, skills, all mounts and Moonveil Adept.
- New pack: mc_moonshadow_heroes_v25_assault_campaign.pack, installed/enabled with v24 retained disabled and launcher backup. No saves, native packs or Workshop files modified.

The last observed used_mods.txt still listed v22, while the launcher had v24 enabled before this repair. Restart via the launcher with v25 enabled, load the existing save and select Assault General to exercise the repair. No new campaign or newly recruited lord is required by this binding logic. The game was not launched to verify the visible result; user runtime confirmation remains necessary.

Build/report folder: build/assault-v25-campaign-appearance. Scripts: Fix-Assault-Campaign-Appearance.py, Deploy-Assault-Campaign-Appearance.py and src/script/campaign/mod/mc_assault_campaign_appearance.lua. Tests: tools/tests/assault-campaign-appearance.lua.
