# Sariwa campaign model hotfix

2026-11-21: user reports Sariwa appears as a short/dwarf-like staff wielder on
the campaign map, specifically not a reported battle appearance issue.

Live launcher and nine active packs were inspected. The unique Sariwa art set,
uniform and art record are present in the active character-assets v4 pack, with
no other active pack redefining those keys/ID. Installed asset pack hash matches
the approved source. Body RMV2 declares `humanoid01b`; the variant includes the
approved Damsel 02 body and three-headed Naga staff. Default art-set resolution
or a cached character appearance is suspected, not proven: no affected current
save or live character art/gender state was observed. Do not claim a demonstrated
root cause or an engine-verified visual repair.

v6 `edh_east_sea_charter_sariwa_model_v6.pack` adds one campaign Lua over playable
v5, leaving every existing payload byte-identical. It explicitly applies
`cm:add_character_model_override(character, "edh_sariwa_art")` only to the
`edh_sariwa` subtype in IEE/main_warhammer. First-tick scanning runs on existing
saves as well as new campaigns; creation, faction-change and recovery listeners
handle later appearances. Session-local deduplication resets when loading.
Wounded records wait until available on-map. Faction turns provide a recovery
fallback, including after transfers to Agents of the Moon or another faction.

No spawning, killing, subtype conversion, healing, XP/skill/item changes or direct
save edits. The active installed Damsel/Naga asset pack remains required. Restart
the game to load the updated pack, then reload the current campaign save. The
patch is intended to repair the existing character; a new campaign is not a
requirement of the script. Actual on-screen outcome remains to be confirmed.

Standalone Lua boundary tests pass for old-save load, new Hero, repeated turns,
wounded recovery, faction transfer, another subtype, another campaign and session
reload; identity/progression fields unchanged. Packed-script roundtrip passes;
installed graphics hash verified; eight schema-reference metadata warnings and
the existing intentional startpos override, no unexpected diagnostics. Reports,
exact hashes and rollback launcher backup: `build/sariwa-campaign-appearance/`.
No game launch or save modification performed.

Native installed prologue source uses this same API on Yuri. Mirrored CA WH3 API:
https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html#function:episodic_scripting:add_character_model_override
