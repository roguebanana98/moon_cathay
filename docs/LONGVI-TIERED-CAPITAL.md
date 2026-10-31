# Long Vi tiered capital (v3)

User confirmed v2 fixes campaign loading and selected major-settlement tiers I-V
for the follow-up. v3 clones the vanilla Cathay major chain under the existing
Long Vi custom keys, including effects, costs, recruitment, garrisons, art,
upgrades/downgrades and localization. The initial building remains tier II.

Secondary unlock counts by tier I-V are 1, 2, 3, 5, 7, matching the vanilla
Cathay major building slot effects. The primary adds one to the total; the port
occupies a secondary slot. Maximum remains eight total including the port.
No script force-unlocks slots. The same Long Vi-only primary template permission
keeps the new chain scoped to this settlement.

The entire runtime-confirmed v2 startpos and province DB payloads are preserved
byte-for-byte, including port, resource data and province membership/capitals.
Only the 12 scoped building/localization payloads are replaced. All 12 roundtrip
through RPFM successfully. Validation also compares major-city definitions to
vanilla and checks the complete I-V upgrade path and unlock counts.

Build: run Prepare-LongVi-Buildings.py, Build-Tiered-LongVi-Pack.ps1, then
Validate-Tiered-LongVi-Pack.py. Historical Build-Province-Pack.ps1 is not the v3
build entrypoint. Output: build/longvi-tiered/mc_longvi_v3_tiered_capital.pack.

Not deployed or game-tested by the assistant. Disable older province/Long Vi
variants and enable only v3 with IEE and MIXER. Test a new campaign first; verify
the starting tier-II lock state, port, upgrade to III/IV/V and final eight-slot
cap. Existing-save behavior has not been verified.
