# Moon Warden — first playable prototype

## Spell investment gate — v11 (2026-11-01)

User accepted the recommendation after the native progression audit. All three
custom spell skills now have zero character-rank gates at both skill levels.
Flame Storm has required_num_parents=4 with SUBSET_REQUIRED links from the
Breath and Earth Blood nodes. Each prerequisite has exactly two levels, so the
threshold requires both at level 2. No other node contributes to this gate.
Starting node investments stay 1/1/0; v10 startpos is byte-identical. Flame Storm
still costs a skill point to learn and another to upgrade after unlocking.

Output: build/moon-lord-spell-ranks/mc_moon_warden_v11_spell_progression.pack.
Replace v10 and restart. Existing v10 saves keep the same skill keys and can be
used to test progression; a new campaign remains necessary to verify initial
grants when coming from pre-v10 saves. No save migration or point reset.

Verified zero rank gates, exact two-parent links, four-point threshold, DB
roundtrip, unchanged startpos/unrelated files and no diagnostics on changed
tables. Runtime check: at 1/1 and 2/1 Flame Storm remains locked; at 2/2 it
becomes purchasable. This also verifies engine counting of starting investments.

## Starting spells and rank gates — v10 (2026-11-01)

User requests one starting point in Earth Blood and Dragon's Breath, with rank
locks for the three spells. Dedicated skill keys now scope rank changes to this
Lord; vanilla skill definitions remain unchanged. Visible nodes retain their
identities and positions but reference the new skill keys. Levels:
Dragon's Breath 1/6, Earth Blood 1/8, Flame Storm 12/16 (displayed character levels;
stored ranks 0/5, 0/7, 11/15). Original spell mechanics/effects preserved.
The new campaign startpos grants Breath level 1, Earth level 1 and the hidden
base Breath-enabling skill; it no longer grants Flame Storm. Node creation
points agree (1/1/0). Custom Battle keeps all three test spells via its own
level-40 preset, updated to the new keys.

Output: build/moon-lord-spell-ranks/mc_moon_warden_v10_spell_ranks.pack.
Build with Prepare-Moon-Lord-Spell-Ranks.py, Build-Moon-Lord-Startpos.py with the
output directory argument, and Build-Moon-Lord-Spell-Ranks.ps1.
Paired typed ESF comparison passed against the preserved v3 baseline, along
with DB roundtrip, rank and unchanged-v9-payload checks. No diagnostics on the
new spell tables. Runtime confirmation pending.

Use a NEW campaign to validate starting points and progression. Existing saves
contain previously granted vanilla-key skills; no migration/reset of those
investments has been implemented. Do not claim old saves automatically lose
Flame Storm or preserve/remap invested points. No live saves were modified.

## Standard Lord skills and control tuning — v9 (2026-11-01)

User requests control +2/+4 and the four pictured native support skills.
V9 changes Moonlit Order's two values and description, then adds scoped nodes
at indent 0, tiers 5–8, leaving command nodes at tiers 0–3 untouched.
Reuses Wind Harmony, Ranged Discipline, Army of Renown (legendary_lord version)
and Mentor directly, retaining native effects and unlock requirements.
Wind Harmony and Ranged Discipline are personal spell/missile resistance,
not duplicates of the custom army range/reload buffs. Native unlock ranks:
6 for both resistances, 9/19/29 for Army of Renown, 29/39/49 for Mentor.
No new immortality node. No startpos, existing skill points or other mechanics
changed. Two new tables; only control effect/loc payloads changed from v8.
Roundtrip and node-placement checks pass, with no diagnostics on new tables.

Output: build/moon-lord-command/mc_moon_warden_v9_support_skills.pack.
Replace v8, restart and inspect the existing campaign's top skill row.
Runtime confirmation pending.

## Campaign skill visibility — v8 (2026-11-01)

User reports the command branch is absent in campaign. Installed v7 pack SHA256
matches the delivered build; used_mods.txt confirms v7 loaded. All four nodes
are linked to the correct skill set with visible_in_ui=true, but placed at
indent 7. Audited other visible rows are 1–5; row 0 is entirely unused.
V8 moves only these four indent values from 7 to 0, preserving tiers 0–3,
effects, prerequisites and unlock ranks. Every other payload is byte-identical
to v7. This isolates a suspected layout issue; runtime confirmation pending.

Output: build/moon-lord-command/mc_moon_warden_v8_skill_layout_fix.pack.
Replace v7 with v8, restart the game and inspect the first skill row in the
existing campaign. No new campaign is requested for this layout-only test.

## Command branch — v7 (2026-11-01)

Recruit-rank skills explicitly deferred. New row at indent 7:
- Moonlit Order: +3/+6 control in the owned province where the Lord is present;
  target levels 6/8.
- Bulwark Against Chaos: +5/+10 ward save for the Lord's army under the vanilla
  fighting_culture_beastmen_chaos_daemons_norsca_chaos_dwarfs condition; levels 10/12.
  Verified context includes all four gods, Daemons, Warriors of Chaos, Norsca,
  Beastmen and Chaos Dwarfs. It does not give unconditional ward save.
- Moonwatch Marksmen: +5/+10 percent range; levels 14/16.
- Disciplined Volleys: +10/+20 reload-time-reduction effect; levels 18/20.

The latter two use scoped custom effects with native range_mod/reload bonuses on
cth_missile_units and cth_missile_units_ror. Verified explicit memberships are
disjoint. Includes the stock Cathay missile infantry, artillery and balloons in
those sets, not arbitrary future third-party units. Army buffs use
general_to_force_own. No factionwide buff or recruitment change. Values can stack
with existing native red-line buffs; balance remains provisional.

The new campaign skills start unspent with sequential prerequisite links.
Custom Battle skill preset lists each combat skill twice at distinct sort orders,
matching the native method of granting multi-level skills; control omitted there.
To check conditional defence compare versus Chaos and versus a non-Chaos opponent.
To check ranged buffs bring a Cathay missile infantry unit and a Grand Cannon;
campaign control must be checked on the campaign map, not in Custom Battle.

Output: build/moon-lord-command/mc_moon_warden_v7_command.pack. Replace v6 with v7.
Ten new payloads added; original v6 payloads byte-identical. Roundtrip and RPFM
checks passed; only reference metadata warning on bonus_value_id remains among
new tables. Skill icons corrected to verified native skill paths. No banned
tables. Runtime application, progression and UI are not yet verified.

## Duelist branch — v6 (2026-11-01)

User acknowledges v5 and requests damage buffs, enemy defensive debuffs and
Lord/Hero hunting. Added a new sequential row at indent 3 with four one-point
skills, requiring the previous node, targeting character levels 5/8/12/16
(zero-based unlock ranks 4/7/11/15 in both skill and level-detail records):

- Moonblade: +8 melee attack and +15% weapon strength, own character only.
- The Enfeebling Foe: enables the vanilla Shadows melee debuff spell.
- Spirit Leech: enables the vanilla Death direct-damage spell.
- Deadly Onslaught: enables the vanilla wh_main offensive active ability.

No race-wide changes. Effects reuse verified vanilla effect-to-ability grants,
costs, cooldowns and targeting. Spirit Leech is useful for single entities; this
is not an instant-kill/assassination mechanic and does not guarantee a kill.
Two base spells extend the composite lore to five spells; overcast variants are
not added separately. The new campaign nodes start unspent. Custom Battle's
existing level-40 test skillset receives all four skills for immediate testing.

Output: build/moon-lord-duelist/mc_moon_warden_v6_duelist.pack.
Replace v5 with v6; re-add Moon Warden in a fresh Custom Battle setup and select
the new spells/ability. All ten added payloads roundtrip through RPFM; no
diagnostics on these new files and no banned tables. Every v5 payload, including
startpos, province data, original skills and units, remains byte-identical.
Runtime skill ranks, links, effects and balance still require testing.

## Mixed lore visibility repair — v5 (2026-11-01)

V4 runtime: user can select Moon Warden and select all spells in army setup,
but only Earth Blood appears in battle. The custom lore incorrectly inherited
is_composite_group=false from pure Yang, despite mixing Yang/Life/Fire. Schema
documentation explicitly states composite lores receive different UI treatment.
Vanilla Yuan Bo and Zhao Ming mixed groups use true and list base spells only;
v4 also incorrectly listed overcast variants as independent group members.

V5 sets is_composite_group=true and retains only the three base spell memberships.
Existing unit_abilities overpower_option links still point to upgraded forms.
Only those two DB payloads differ from v4; startpos, skill grants, roster and
province/building data are byte-identical. No RPFM diagnostics on the changed
tables, no banned tables. Output:
build/moon-lord-custom-battle/mc_moon_warden_v5_mixed_lore_fix.pack.

Runtime fix is not yet confirmed. Replace v4 with v5 and create a fresh Custom
Battle setup, removing/re-adding the Lord if reusing an army preset. Verify all
three base spells in battle, then cast each. Overcasts should be handled via
the base spell's overcast UI, not independent duplicate entries.

## Custom Battle test access — v4 (2026-11-01)

User cannot readily test campaign battles and requests a way to select the Lord
in Custom Battle. V4 adds Cathay MP roster permission, a set-piece character,
an explicit battle skillset containing the four existing spell/enable skills,
two zero-frequency name records/localization and Cathay military permission.
The battle test preset uses character level 40 to make the listed skillset
available; it has no mount, dragon transformation or Yuan Bo quest items.
Campaign progression and all v3 payloads remain byte-identical.

Output: build/moon-lord-custom-battle/mc_moon_warden_v4_custom_battle.pack.
Replace v3 with v4. Choose Custom Battle -> Grand Cathay -> Lords -> Moon Warden
(temporary Yuan Bo portrait), then check the spell options before battle.
Use an allied unit as a healing target and enemy infantry to test breath/AOE.
No new campaign is needed for this test.

All seven additions roundtrip through RPFM. Diagnostics report no banned tables
or unresolved record references in the new permission/character/skillset files;
names type/gender metadata is not available to the diagnostic cache. Runtime
roster visibility and spell behavior remain unverified until user testing.

## Runtime confirmation and name label fix (2026-11-01)

User confirms v2 runs without observed errors. They identify Moon Warden being
shown in the subtype/class label where Legendary Lord should appear. V3 changes
only agent_subtypes_onscreen_name_override_mc_moon_warden to Legendary Lord.
The personal name and battle unit name remain Moon Warden. Every gameplay
payload, including startpos, is byte-identical to v2. Output:
build/moon-lord/mc_moon_warden_v3_name_fix.pack. Static checks passed; display
confirmation pending. Replace v2 with v3, do not enable both. As a localization-
only change, it is intended to work with the existing v2 campaign save.

## Startup failure and v2 repair (2026-11-01)

User tested v1: crash at splash screen immediately after Play, BEFORE the main
menu. This is not a new-campaign loading failure. V1 is withdrawn as a test build.
The previous roundtrip/ESF validations did not check forbidden DB table types.

RPFM pack diagnose, using a freshly generated local dependency cache, reports
BannedTable for agent_subtype_ownership_content_pack_junctions_tables and
main_unit_ownership_content_pack_junctions_tables. These engine-owned tables were
incorrectly cloned into v1. V2 removes exactly those two payloads. Every retained
payload, including startpos, is byte-identical to v1. Generator and validator now
exclude/reject these tables. Original game/Workshop data remains untouched.

Output: build/moon-lord/mc_moon_warden_v2_startup_fix.pack.
SHA256: cc8a63b5fa5896b39483ad9badb20eb6fe7383f99b977dd5ff3e1c008274c948.
RPFM no longer reports BannedTable. Remaining diagnostics include unresolved
reference-table metadata, missing optional unit porthole images and intentional
IEE payload overrides; full results are recorded in the pack manifest. These
remaining reports have not been established as crash causes.

This is a confirmed packaging error and candidate cause, not a runtime-confirmed
fix. Disable v1 and other province/Long Vi submods; test v2 with IEE/MIXER. First
verify reaching the main menu. Only then test a new Expanded campaign and battle.

2026-11-01: user authorized implementation of the PROJECT_GOALS design and
confirmed male gender, a temporary name, and replacement of Ju Di. No new model.

## Implemented in the private local candidate

- `mc_moon_warden` subtype, temporary name Moon Warden, Agents of the Moon leader.
- Yuan Bo's existing human sword model, animation, voice, armour and baseline
  combat stats. References existing resources; no copied mesh or texture files.
  Donor resources belong to Shadows of Change / Cathay. Do not put engine-owned
  DLC ownership tables in a mod pack (corrected in v2).
- Human-only custom unit: no dragon transformation grant, dragon alternate unit,
  mounts, Yuan Bo quest items or Blood-line branch.
- Retains character ID 329, army 225, general-unit ID 1575 and existing male /
  is_immortal flags. Original non-general units, faction posts and regions stay.
- Own skill set with Cathay melee, army and campaign lines; three spell nodes.
  Dragon's Breath (Yang), Earth Blood and Flame Storm start at skill level 1 for
  testing. A hidden skill enables base Dragon's Breath. Progression is provisional.
- `auto_generate=false`, cap 1, legendary recruitment category, recruitable=true
  to retain the ordinary wounded-recovery path. Runtime uniqueness/recovery is
  not yet verified.
- Integrates the user-tested v3 province layout and Long Vi tiered capital.

## Build and verification

Prepare-Moon-Lord.py -> Build-Moon-Lord-Startpos.py -> Build-Moon-Lord-Pack.ps1 ->
Validate-Moon-Lord.py. Local audited raw baseline is reference/local/lord-base.raw.esf.
Output: build/moon-lord/mc_moon_warden_v1_test.pack.

Validation passed: all 15 retained added DB/loc payloads roundtrip through RPFM; previous
v3 DB/loc files are byte-identical. A recursive paired ESF comparison verifies
only the 14 scalar changes and one skill block change; all other primitive bytes
are preserved, including province UINT32-array types. Container lengths and
string table additions are adjusted by the writer.

MIXER updated locally since the v3 build. Re-extracted DB/text/scripts, compared
all changes, and decoded the four previously raw reference tables with the
current schema. Those four have no row changes. Other changes add unrelated
factions, frontend entries, Silver Pinnacle slots and helper registrations;
an existing Araby frontend sort number changes. No observed edits to the target
faction/lord or Cathay skill tables. IEE hash unchanged. Fingerprint baseline
updated after this audit, recorded in reports/mixer-update-20261101.json. This
does not substitute for runtime compatibility testing.

## Test and remaining work

Disable previous province/Long Vi submods and use this integrated pack with
IEE/MIXER on a NEW Expanded campaign. No deployment or game launch by assistant.
Check leader name/model, skill tree, all three spells in battle, direction/VFX,
mana/cooldown, no transformation button, end turn and save/load. Test wounding
and return before relying on immortality/recruitment behavior.

Frontend faction selection still uses the existing MIXER/IEE placeholder.
No custom battle roster integration, final portrait/description, new model,
final skill progression, unique items or final balance yet. Reused unit text
and voice may still mention Yuan Bo. These are prototype limitations, not
runtime-confirmed features. Do not mark the full Legendary Lord milestone done.
