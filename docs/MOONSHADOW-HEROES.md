# Moonshadow Heroes

User approved both a recruitable assassin Hero line and an independent starting
Legendary Hero for Agents of the Moon on 2026-11-21. The user will select models
later. Current appearance is the intact native Khainite Assassin, including its
sword/handbow and matching battle/campaign animation lookups. No mesh grafts,
custom animation database, or external model assets are included.

## Recruitment and starting Hero

- Moonshadow Assassin: faction-exclusive spy subtype `mc_moonshadow_assassin`.
  Costs 1000 to recruit, upkeep 250. Starts with zero subtype capacity.
- Recruitment is now attached to the existing **Celestial Tower** (settlement
  tier III) and retained on Celestial Observatory (IV) and Celestial Beacon (V).
  Each intact building enables provincial recruitment and adds +1 factionwide
  assassin capacity, total +1 at any upgrade level, not +1/+2/+3. Native costs,
  construction times, slot usage, names and Astromancer effects are unchanged.
  A native-format owner context restricts BOTH new effects to Agents of the Moon,
  including the spy-category capacity effect. Other Cathay factions get no new
  bonuses. User rejected a new building for balance: all Moonshadow Hideout
  definitions and its localization have been removed from v6.
- Da Anh: separate `mc_da_anh` subtype, not randomly recruitable, unique and
  immortal, excluded from normal Hero capacity. One independent rank-1 Hero is
  created on valid land beside Huyen Ve's existing army on the first turn of a
  new IE/IEE campaign. Existing pre-first-tick Long Vi placement runs first.
  Existing saves do not receive a newly spawned Da Anh.
- Saved markers and an existing-character scan, including wounded characters,
  prevent duplicate creation. Invalid placement/creation is retried once during
  first tick. No new army, saved-game edits or end-turn auto-respawn are used.

## Skills and abilities

Both have a separately keyed, curated native assassin tree: combat, poisons,
assassination, assault units/garrison, damage buildings, scouting and embedded
army mobility. Slave economy, loyalty skills, Dark Elf innate backgrounds and
Murderous Prowess/Mastery unit abilities are excluded. Normal assassin immortality
and Mentor remain; Da Anh receives immortality from the starting script instead.

Da Anh has +8 base melee attack, +6 melee defence and +400 bonus hit points over
the regular Hero. Personal skills use one purchased level each:

| Skill | Display rank | Effect |
| --- | --- | --- |
| Moonshadow Veil | 6 | Unlocks native Concealment Bombs: temporary concealment, three uses, 90-second cooldown. |
| Silent Execution | 12 | Unlocks native Assassin's Trophy targeted debuff; replaces the copied final trophy node. |
| Sever the Supply Lines | 8 | Hero action cost -15%, action success chance +10 percentage points. |

Skill names are authored; ability names/effects remain native. No guaranteed
assassinations, instant army destruction, faction deletion or new quest rewards.
All mod UI strings are ASCII English. Regular Heroes inherit faction names.

## Build, installation and limits

`tools/Build-Moonshadow-Heroes.py` creates the additive private pack
`build/moonshadow-celestial-tower/mc_moonshadow_heroes_v6_celestial_tower.pack`.
V5 was deployed previously and is retained/disabled as rollback; v1-v4 were local
build candidates, never deployed. Native artwork aliases stay in ignored build.
`Check-Moonshadow-Heroes.py` verifies DB/loc roundtrip, faction permissions,
capacity/recruitment links, skill graph, native compiled animation lookups,
portraits, and 17 standalone Lua scenarios with mocked CA interfaces.

RPFM uses the newer local game dependency cache from the East Sea character
work; the older November-1 cache is rejected by the current game. Only schema
enum/reference metadata warnings are accepted. Any actual missing record/file,
invalid portrait variant or other diagnostic blocks deployment.

`Deploy-Moonshadow-Heroes.py` replaces the active v5 addon with v6. All unrelated
active mods and launcher records remain unchanged and their files are hash
checked. Launcher config is backed up. Native packs, Workshop files and saves
are untouched. Dependency fingerprints and installed hashes are recorded in
`build/moonshadow-celestial-tower/build-report.json` and `deployment.json`.
The packed v6 differs from deployed v5 only in removal of seven Hideout definition
tables and its loc rows, addition of an owner context and reassignment of the two
building effects to the three native Celestial Tower levels. All character,
skill, graphic and Lua payloads are byte-identical.

No game was launched. Actual recruitment UI, building availability, subtype cap,
Da Anh spawn, campaign actions, wounded return and skill/battle behavior still
require engine testing. Suggested test: create a new Agents of the Moon campaign,
check Da Anh beside Huyen Ve, save/reload without duplicates; construct Celestial
Tower, recruit a regular Assassin, verify capacity and actions. Upgrade through
Observatory/Beacon and confirm capacity stays +1 and recruitment remains enabled.
