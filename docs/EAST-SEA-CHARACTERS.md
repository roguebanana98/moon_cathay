# Heinrich and Sariwa — East Sea Charter integration

User confirmed Heinrich is a Legendary Lord, faction leader and army commander.
Sariwa temporarily spawns independently beside his initial army on new campaigns.

Current private add-on: `edh_east_sea_charter_characters_v3.pack`. It replaces the
active territorial v2 add-on and requires the existing character graphics/skills
pack `edh_heinrich_sariwa_v4.pack`, which remains enabled. No asset duplication or
Workshop edits. The faction remains AI-controlled; no new frontend selection was
requested in this change.

The registered starting leader retains character ID 515, general unit ID 2454,
government post and army. Only its private subtype, art set, general unit key,
names, skill node set and named/immortal flags change in startpos. Reversing the
two affected records reproduces all original record bytes; existing string-table
entries are unchanged. The territorial setup remains Dai Loa + Preenn, capital
Dai Loa; Moon retains Long Vi + Leilou, capital Long Vi.

The existing Heinrich model and 52-node tree are reused. Sariwa uses the approved
Damsel 02 outfit/Naga staff, native animation and existing 21-node tree. Campaign
unit caps and XP are enabled, faction agent permissions added, and both unique
subtypes use native LL/LH character import/export restrictions. The field
`cannot_be_loaded_in_campaign` is also used by native Karl Franz and Ulrika;
it controls reusable character import, not normal campaign-save persistence.

Sariwa's first-tick spawn checks the new-game flag, successful faction setup,
existing characters and a persisted creation marker. A valid position is chosen
around Heinrich with same-region preference and distance 2. She is not embedded.
Creation is persisted before naming/unique/immortality presentation calls, so a
later error cannot create a second Hero. No load-time migration of existing saves
is implemented or requested.

Static validation passed: DB/loc roundtrip, exact starting-leader/unit-only edits,
unchanged territorial payloads, seven schema metadata warnings and one expected
startpos override, no unexpected diagnostics. 22 Lua boundary scenarios passed.

User then requested **no game testing yet**. The launched QA process was stopped
during startup, before selecting or creating a campaign. Runtime is unverified;
do not claim campaign spawn, campaign visuals, save/load or leader gameplay were
observed. Restore status and original-save hashes are recorded in
`build/east-sea-characters/qa-session.json`.

Authored sources: `src/campaign/east-sea-charter.json` and
`src/script/campaign/mod/edh_east_sea_charter_start.lua`.
Build/validation reports: `build/east-sea-characters/`.
