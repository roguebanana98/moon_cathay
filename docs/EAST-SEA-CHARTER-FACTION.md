# East Sea Charter — IEE campaign setup

User selected this name and requested a separate Empire faction holding Dai Loa
and Preenn. Source: `src/campaign/east-sea-charter.json` and
`src/script/campaign/mod/edh_east_sea_charter_start.lua`.

The faction uses the registered, landless MIXER slot
`mixer_emp_vaults_gigasdongo` (campaign ID 386, DB index 1270536241). This is a
separate faction from Agents of the Moon, with the existing Empire skeleton of
campaign systems. The technical placeholder key is retained for MIXER/IEE
registration. A mod activating the same reserved slot is incompatible.

On a new IEE campaign only, the pre-first-tick script validates both cities are
still Moon-owned and the destination slot is landless with its single native
Empire General. It finds valid land, teleports that existing commander, then
transfers exactly Dai Loa and Preenn via the native engine. It assigns Dai Loa as
the new capital, Long Vi as the Moon capital, and adds six native Empire units.
The commander is temporarily named Expedition Commander. Heinrich and Sariwa's
existing Custom Battle implementation is unchanged; this does not spawn them
as campaign characters. The faction is initialized as AI, without enabling a new
playable frontend selection in this revision.

Long Vi, Leilou, Avauka, province layout, Moon quest and model data are preserved.
Loading an existing campaign does not transfer land. No user save is edited.

The small add-on contains the r8-derived IEE startpos with only the destination
faction's cached technology manager and flag record replaced with native Empire
records. Reversing those two records reproduces the entire original decompressed
startpos byte-for-byte. Ownership itself is updated by the native script, so
province/settlement bookkeeping and building conversion remain engine-managed.
The current r8 pack remains a required dependency; do not mix with other map or
startpos overrides without revalidation.

The pre-update Workshop MIXER independently crashed at startup: its army parent table
`db/battle_set_piece_armies_tables/!b_mixer` is empty while its corresponding
unit junction has 301 orphan army references. The game reports the first invalid
record in that table even when loading MIXER alone. Test v1 temporarily replaced
only that orphan junction file with a zero-row table at its original internal
path. Workshop files were never edited by this project.

Steam automatically updated MIXER at 2026-11-10 01:11 local (manifest
5077045964861114283), after the successful campaign test. The update restores 35
army records and resolves all 301 orphan references. The faction table is
byte-identical. Current v2 removes the obsolete compatibility file; all other
gameplay/localization/script/startpos payloads are byte-identical to tested v1.
The original broken-dependency hash and test context are retained in the report.

Build/QA reports are in ignored `build/east-sea-faction/`. DB and localization
roundtrip, exact startpos reversal, native General/unit keys, and 16 standalone
Lua boundary tests pass. Expected startpos/file overrides and schema metadata
warnings are distinguished from invalid references. Runtime status is recorded
separately; static checks do not establish completed campaign testing.

Runtime QA passed on WH3 9.0.5: diplomacy identifies East Sea Charter as The
Empire with exactly two settlements. The game-created turn-one save was read
without modification and confirms Dai Loa + Preenn, Dai Loa as capital, and only
Long Vi + Leilou for the Moon faction with Long Vi as capital. There is one native
Empire field army (original commander and Spearmen plus six added units), and
two separate settlement garrisons. Huyen Ve remains at Long Vi. Native minor
faction intro/narrative warnings remain as previously observed; the new transfer
script completed without exception. A transient trespasser event is emitted when
the General is repositioned just before the transfer. End-turn behavior and an
engine reload were not tested. See `build/east-sea-faction/runtime-validation.json`.

Game exited after saving. All 88 original save files are verified against their
backup hashes. The new QA save was retained under
`build/east-sea-faction/qa-created-saves/`; it is outside the user's save folder.

Private deployed pack: `edh_east_sea_charter_faction_v2.pack` (v1 disabled).
Launcher backup preserves previous activation and relative ordering. All 88
existing save files were copied and hashed before runtime QA; use
`Restore-East-Sea-Faction-QA.py` only after exiting the game. It retains new QA
saves separately and restores/verifies every original hash.
