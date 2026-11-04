# Long Vi campaign city appearance — 2026-11-04

User requested a major-city appearance for Long Vi. The custom building chain
already uses major-city gameplay, but lacked campaign settlement display IDs.
Added six scoped mappings (tiers I–V and ruin) to native Cathay major-city model
IDs, following the native Bhashiva custom-chain mapping pattern. Native display
definitions supply both normal and port major-city prefabs at each tier.

Build: `tools/Build-LongVi-City-Visual.py`.
Candidate: `build/longvi-city-visual/mc_huyen_ve_v25_r8_longvi_city.pack`.
Based on v25 r7; exactly one additional DB payload. Every previous payload,
including startpos, port, resources, quests, models and slot rules is byte-identical.
All six rows successfully roundtrip through RPFM. Validation report is alongside
the candidate. Not deployed or runtime confirmed. Existing saves may refresh the
DB-driven appearance on load; verify in game, including coastline fit, upgrades,
walls and port. No siege battlefield or campaign map geometry changes were made.

Use this integrated pack instead of r7, not alongside it. Future builds based on
r7 or earlier must carry forward this additional mapping payload.
