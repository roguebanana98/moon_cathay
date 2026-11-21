# East Sea Charter — refuge and homecoming

User request, 2026-11-18: when East Sea Charter is destroyed, Heinrich and Sariwa
join Agents of the Moon through an event. When their original faction returns,
they return to it. Game testing remains deferred by the user's earlier request.

Current pack: `edh_east_sea_charter_refuge_v4.pack`, replacing the active v3 pack.
Deployed and enabled locally on 2026-11-18; v3 remains on disk, disabled.
The separate character assets/skills pack `edh_heinrich_sariwa_v4.pack` remains
required. All existing v3 gameplay, startpos, models and skills are byte-identical.
Six additive payloads provide the script, two incidents and their options/text,
and Cathay recruitment/military permissions for the two custom subtypes.

## Player-visible behavior

- **Sanctuary of the Moon**: after East Sea Charter dies, transfer the original
  Heinrich and Sariwa to Agents of the Moon. Announce only once both ownerships
  are confirmed. No accept/reject branch was requested, so this is automatic.
- **The Charter Restored**: once East Sea Charter is alive again, return the
  original pair and notify Agents of the Moon. Also notify the home faction if
  it is human-controlled. This does not itself resurrect either faction.
- Wounded characters retain their recovery state. A transferred Lord can be
  recruited through the normal interface when available. No free army is spawned.
- If Heinrich commands an Agents of the Moon army when returning, replace its
  general with a native Cathay Magistrate before transferring Heinrich alone.
  That faction keeps its troops. The script does not copy Heinrich's equipment
  to the replacement. Huyen Ve is not renamed, replaced or moved by this script.
- An active independent Sariwa travels to her new faction's capital when a valid
  location is available. An embedded Hero must be unlinked by native reassignment
  before completion is acknowledged; otherwise the transfer remains pending.

## Identity and persistence

The script stores the original family-member CQIs and current character CQIs.
Native `cm:reassign_character(character_cqi, faction_cqi)` moves that identity;
the script never creates/clones either character, grants XP, resets skills,
reconstructs inventory, heals characters, or resets convalescence timers.

Native references used: installed `wh3_dlc29_archaon_subjugation.lua` (LL and Hero
reassignment, including wounded characters) and `wh3_dlc29_nag_mortarchs.lua`.
The original family-member identity is used again when map CQIs change.
Third-party faction ownership is respected; no character is taken from a faction
other than East Sea Charter or Agents of the Moon.

The four persisted phases are `home`, `to_moon`, `moon`, `to_home`. Partial
transfers resume on load/round/turn boundaries without retransferring a character
already at the destination. A revival during an incomplete refuge cancels that
transition without inventing a completed-arrival/homecoming notification.
Repeated destruction/revival cycles are supported. A dead host faction is never
revived or used as a destination. Unavailable wounded/archived records remain
pending rather than being replaced with new characters.

Entry points: `FactionDeath`, `RegionFactionChangeEvent`, `FactionLiberated`,
`FactionTurnStart`, `WorldStartRound`, first tick, and character creation/ownership/
convalescence events. The existing v3 campaign-start marker and IEE campaign alias
gate prevent changes to unrelated campaigns. Existing v3 saves can register the
feature on load; inaccessible archived characters still require native
reassignment/identity availability before completion can be confirmed.

## Validation and practical limit

15 standalone Lua world scenarios / 39 assertions pass: repeated cycles,
save/load re-entry, wounded/archived identities, partial failures and retries,
dead hosts, embedded Hero boundary, army preservation, third-party ownership,
and cancelled transitions. These use mocked CA interfaces and do not prove the
engine's internal reassignment behavior. Native battle/death timing, cross-culture
recruitment, embedded-Hero extraction, actual item retention and popup presentation
remain **unverified in game**. No game launch or save modification is part of this
delivery.

DB/loc import-export is lossless; both incident text keys resolve. The six added
payloads are the only difference from v3. RPFM reports seven schema metadata
warnings and the existing intentional IEE startpos override, no unexpected
diagnostics. Build, tests and deployment reports are in `build/east-sea-refuge/`.

IEE changed since the original v3 build. A targeted review of 54 extracted files
confirmed the relevant faction definitions and region definitions are unchanged;
new optional factions, frontend unlock mappings and a Land of the Dead fix were
observed. The updated native startpos renumbers faction CQIs (Moon 208/Home 394),
whereas this mod retains its existing v3 startpos (Moon 205/Home 386). Refuge uses
faction keys rather than numeric faction IDs. No rebase of the existing mod's
startpos was performed. Full compatibility with the updated IEE startpos remains
unverified in game; exact reviewed fingerprints are in `dependency-review.json`.

CA API reference for general replacement (mirrored CA scripting documentation):
https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html#function:episodic_scripting:replace_general_in_force
