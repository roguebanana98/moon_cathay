# Da Anh turn-one movement fix (v10)

The user clarified that Da Anh could not move at all on turn one. The request was
for normal available campaign action points, not maxing the Increase Mobility skill.
The brief v9 skill-bonus build was disabled and v10 is derived from v8 directly.
All v8 DB, localization, UI and model payloads are byte-identical. Skill trees and
starting skill points are unchanged. No v9 mobility skill exists in v10.

The previous starting-agent script called create_agent but did not explicitly
replenish its action points. The engine helper does not replenish AP in its wrapper;
Mixu's agent-creation helper explicitly does so after creation. This is the likely
missing initialization; no in-game root-cause confirmation has been performed.

The updated mc_moonshadow_start.lua enables character movement and replenishes
normal AP once after creating Da Anh. Existing independent, unwounded Da Anh
characters on turn 1 are also enabled once, and replenished only if AP is zero.
A saved per-character marker prevents repeat grants after callback retries or
saving/reloading after using movement. No later-turn replenishment and no embedded
army AP grants. The existing new-campaign-only spawn and duplicate guards remain.
No skill points, XP or range bonus is added.

Validated with 23 Lua mock scenarios, including existing turn-1 zero/positive AP,
turn2, wounded, embedded, unsupported campaign, duplicate/reload and spawn failures.
The compiled pack differs from v8 in exactly one existing Lua payload. RPFM reports
zero blocking diagnostics (schema metadata warnings only). See
build/da-anh-v10-starting-movement/{lua-check,pack-validation,deployment}.json.

Enabled mc_moonshadow_heroes_v10_starting_movement.pack; v8 and v9 retained disabled.
SHA256 b8a6ee8424e56f407b1ae20e17965cc5bd9a55123ffde92247708485cddbadb4.
Launcher backed up, unrelated entries and packs unchanged. No saves, Workshop or
native packs changed; game not launched, in-game result remains unverified.
Restart the game and reload a turn-1 save or start a new campaign to test.
