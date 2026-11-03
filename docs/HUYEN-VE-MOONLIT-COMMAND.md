# Moonlit Command and Army of Renown - v19

2026-11-03 (Asia/Saigon). User requested a new skill between Earth Blood and
Flame Storm and an audit of whether Army of Renown's final +6 is native.

Current private test pack: `build/huyen-ve-v19-moonlit-command/mc_huyen_ve_v19_moonlit_command.pack`.
Installed over v18 with a launcher backup; no save was edited. Restart and load
the existing campaign. The new skill requires one skill point after Earth Blood
is learned; it is not automatically granted to campaign characters. Custom Battle
includes it in Huyen Ve's test skill preset.

## Skill

Row order: Dragon's Breath -> Earth Blood -> Moonlit Command -> Flame Storm.
Existing skill keys and investments are preserved. Flame Storm moves from tier 2
to tier 3; its previous two-parent prerequisite links and required points remain.
The new node has zero starting points and one purchased level.

Native donor: `wh_dlc06_lord_abilities_spite_of_da_bad_moon`.
Affected allies receive +25% base/AP melee weapon damage and +16 bonus vs large
for 20 seconds; area 35m, cooldown 90 seconds, zero Winds of Magic, unlimited uses.
Native targeting and self/friendly phase targeting are preserved. Generic positive
buff VFX are reused; the Greenskin-specific audio event is cleared. No new animation
stance is required. The ability requires its enable effect, granted only by the skill.
English display name: Moonlit Command. UI text is ASCII.

## Army of Renown provenance

Huyen Ve directly references native skill
`wh3_main_skill_all_army_of_renown_legendary_lord`, without any custom effect override.
Its native level effects are:

| Level | Effect | Scope | Value |
| --- | --- | --- | --- |
| 1 | wh3_main_effect_recruitment_cap_ror_units | character_to_force_own_alt_text | +2 |
| 2 | wh3_main_effect_recruitment_cap_ror_units | character_to_force_own_alt_text | +4 |
| 3 | wh3_main_effect_recruitment_cap_ror_units | character_to_force_own_alt_text | +6 |

This is additional Regiments of Renown capacity in the lord's army, not recruit
rank +6 or six additional copies of every RoR. Native node/set links connect this
same skill to Yuan Bo, Miao Ying, Zhao Ming, Karl Franz, Arbaal, Settra, Alarielle,
and many others. The audit records 120 native skill-set owner rows. The skill
therefore remains unchanged, as requested when its values are native.

Evidence is in `build/huyen-ve-v19-moonlit-command/skill-manifest.json`, including
the exact native effect rows and all owner-set records from the installed DB extract.

## Checks and reproduction

`Prepare-Huyen-Ve-Moonlit-Command.py`, then `Build-Huyen-Ve-Moonlit-Command-Pack.py`.
RPFM diagnose followed by `Validate-Huyen-Ve-Moonlit-Command-Diagnostics.py`.
The build checks exact packed table roundtrip, unique new skill/ability keys,
four ordered nodes, unchanged old node properties except Flame Storm's tier,
unchanged native support node and Flame Storm prerequisite tables, ASCII loc,
and unchanged previous model/animation/UI/script payloads. The phase icon alias is
a byte-identical copy of the existing game icon and stays in ignored private build.

No blocking diagnostics remain. Nine schema-enum metadata warnings are recorded
separately; they report missing reference definitions, not missing content rows.
Missing icon/path diagnostics are not allowed. Actual campaign unlock, battle UI
and buff effects still need runtime confirmation.

Deployment: `Deploy-Huyen-Ve-Moonlit-Command-Test.py`; backup path and hashes in
the build's `deployment-report.json`. No Workshop files, native packs or live saves
were changed. No publishing was performed.
