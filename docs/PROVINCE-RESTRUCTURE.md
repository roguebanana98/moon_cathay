# Province restructure — requested 2026-10-31

User-authorized campaign scope: regroup these five regions and change province capitals.
The existing Phase 1 reports remain baseline evidence, not the desired new state.

| Existing province name | Target members | Target province capital |
|---|---|---|
| Primal Labyrinth | Long Vi, Leilou | Long Vi |
| Paradise Spires | Dai Loa, Avauka, Preenn | Dai Loa |

Machine-readable authored specification: `src/campaign/province-layout.json`.
Leilo refers to the existing Leilou region; Paradise Spries refers to Paradise Spires.
Preserve existing province keys/localization. Ownership and faction capitals are outside
this change; Avauka remains owned by Snakebiters in the static baseline.

## Verified changes needed

- `region_to_province_junctions`: move Dai Loa from Primal Labyrinth to Paradise Spires;
  set Long Vi capital true and Avauka capital false; Dai Loa remains capital true.
- `regions_to_region_groups_junctions`: move Dai Loa's province group accordingly.
  Other unrelated region groups must remain intact.
- Resolve removal/replacement of old junctions with the actual schema keys and load
  precedence. Adding the new province/group row alone may leave the old association.
- Inspect and synchronize campaign map/startpos province membership, province capital
  references, settlement slots/building compatibility and affected province adjacency.
  Do not assume a DB-only override updates an existing campaign or live save.

## Initial delivery status (superseded by local candidate below)

Specification only. No playable pack, startpos edit, save edit or deployment was made.
The repository's `inspect_esf.py` is explicitly read-only and has no encoder. The
current build script creates an empty Phase 1 pack. A verified campaign editing/export
pipeline is needed before this request can be delivered as a working mod.

Next implementation work: establish an IEE-compatible map/startpos editing workflow,
build locally, check that each of the five regions belongs to exactly one target province
and each province has exactly one capital, then test new campaign, end turn and save/load.
Live-save migration is separate and has not been established.

## Assembly Kit inspection after installation

- Steam app 1880380 is installed, StateFlags 4, build 25922678, under
  `D:/SteamLibrary/steamapps/common/Total War WARHAMMER III/assembly_kit`.
  Game remains on F:. Verified Kit path added to ignored local configuration.
- Kit `TWaD_region_to_province_junctions.xml` marks both region and province as
  primary keys, and marks changes to them as requiring startpos reprocessing.
  It does not mark these fields as requiring campaign map reprocessing; therefore
  CAIME is not yet established as necessary for this particular change.
- Kit `start_pos_regions.xml` and `campaigns.xml` contain no target IEE campaign/region.
  The inspected IEE pack index has no `db/start_pos_` source tables. Installing the
  Kit alone does not provide IEE's campaign generation source.
- Regenerating IEE startpos through the Kit is blocked on obtaining compatible IEE
  source tables. Direct binary editing remains an unverified alternative, not a
  completed implementation. No additional tool installation requested yet.

## Direct-editor feasibility check

User confirmed no IEE source project is available. The extracted startpos is
14,097,669 bytes with magic `0xABCB`. Installed EditSF 1.1.1 exposes ABCE/ABCF/ABCA
codecs but no ABCB codec; its `LoadEsfFile` throws a NullReferenceException on this
file. No file was written by that probe.

xADDBx/EditSF release v1.3.0 explicitly adds ABCB support and targets .NET 10:
https://github.com/xADDBx/EditSF/releases/tag/v1.3.0
It is a candidate for a separate local tool installation, followed by unmodified
read/write/reopen verification on a disposable copy before any province edits.
Support for the codec alone does not establish correct province migration.

## Local candidate prepared after tool approval

EditSF v1.3.0 with runtime was downloaded to `tooling/EditSF-1.3.0` with user
approval. Archive SHA256:
`901A863CD7ACB3B52A5ADA5B69391646456DBB49175C2BE0C33036243F7F9666`.
EditSF successfully opened and saved a disposable copy. Its 134,903,264-byte
decompressed payload is byte-identical to the original. Compressed files differ.

`tools/Build-Province-Candidate.py` creates an experimental local startpos in
`build/province-edit/province-candidate.esf`. It verifies the baseline payload
hash, patches two PROVINCE_DATA records and two Moon FACTION_PROVINCE_MANAGER
records, and preserves unrelated record bytes. It adjusts enclosing lengths and
recompresses with the original LZMA properties. An independent read of the final
compressed file succeeded and confirmed the requested capitals and membership.

`tools/Prepare-Province-Db.py` prepares two derived TSVs under the same build
directory, changing exactly four rows. These need full-file overrides at the
original internal paths so Dai Loa's old composite-key associations are removed.
Load precedence and binary schema import still require verification.

The extracted map_data.esf was also read successfully and contains no records
with PROVINCE in their names. This does not establish that all AI caches are
independent of province structure, but gives no reason yet to install CAIME.

Both dependency pack hashes remain unchanged. No game/Workshop files or live
saves were edited. No pack was built or deployed. Packaging derived IEE data
needs a narrowly scoped exception to AGENTS.md's ban on bundling third-party
assets. Candidate files are ignored local work, not a public release.

Remaining limits: settlement slots, minor/major building chains and settlement
visuals are unchanged (Long Vi retains minor-city infrastructure, Avauka retains
major-city infrastructure). Faction capital remains Dai Loa and Avauka ownership
remains Snakebiters. AI caches, pack priority, new campaign, end-turn and save/load
are untested. Do not present this candidate as a finished playable mod.

## Private test pack built with explicit user approval

The user subsequently approved packaging the derived startpos and two DB tables.
`tools/Build-Province-Pack.ps1` built a new GUID-named local mod pack; no deployment
or public distribution was performed. `tools/Validate-Province-Pack.py` passed:
PFH5 mod type, exact dependency header, exactly three gameplay payloads, byte-exact
startpos extraction, lossless DB binary import/export, unique membership of all five
regions, and exactly one capital in each target province.

Current artifact and checksum are recorded in `build/province-edit/pack-manifest.json`.
The RPFM internal metadata remove_path warning occurred during writes; direct pack
header validation nevertheless confirmed both required dependency names. There were
no DB import/export failures. Settlement infrastructure and runtime limitations above
still apply. Only the `cr_combi_expanded` startpos is overridden.

Tool-author reference for the map/database workflow:
https://github.com/TW-Campaign-Map-Modding-Team/CampaignMapToolkit/blob/main/docs/user-guide-modifying-an-existing-map.md
