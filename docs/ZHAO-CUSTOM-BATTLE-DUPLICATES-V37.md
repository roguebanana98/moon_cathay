# Zhao Custom Battle duplicate repair — v37

The user reported two visually identical Zhao cards and duplicate spell/passive
checkboxes in v36 on 2026-11-27. The screenshots show duplicate basic spells and
Lunar Ascendancy, in addition to separately labelled upgraded spells.

## Scoped correction

- Remove all 13 private Moon Arts spell/overcast/passive entries from the direct
  land-unit ability list on foot, horse and Longma (39 rows). The existing lore
  group is the single selection source, matching the native Shugengan pattern.
  The spell definitions, effects, campaign skills and lore membership stay intact.
- Clear `general_uniform` consistently on all six Zhao Custom Battle permissions
  (two factions × three forms). V36 used a foot uniform and a different mounted
  uniform, splitting the family into two appearance selections. Native lords
  support an empty uniform; the existing unit variants select the approved foot
  or mounted mesh. The mount links and set-piece character remain unchanged.

The blank-uniform path needs an actual mounted appearance check in game. This
repair does not establish full Longma rider/flight fit.

## Artifacts and validation

Pack: `mc_moonshadow_heroes_v37_zhao_cb_fix.pack`, 1,307,123,794 bytes.

SHA256: `da1d0ffe06b5ea210b55e1941bc43ed609dcbfda2680bc84209e8a4b1d2df2c1`.

Source is the immutable final v36 pack, SHA256
`2584f38b44cf2e9d8f9f4feba87a809cfbfc187dd17f71d638292c2d905087e3`.
Exactly two existing DB payloads differ; no payload added or removed. All other
payloads, including Jade, Zhao stats/tree, migration Lua, models and sword LODs,
are byte-identical. Actual RPFM import/export equality passed. Diagnostics retain
168 `NoReferenceTableNorColumnFoundNoPak` schema/cache warnings and zero other
diagnostic types. Runtime confirmation is pending.

Build and validation: `tools/Fix-Moon-V37-Zhao-Custom-Battle.py`.
Install/launcher backup: `tools/Install-Moon-V37-Zhao-CB-Fix.py`.
Reports: `build/moon-v37-zhao-cb-fix`; distribution:
`dist/moon-v37-zhao-cb-fix`.

Enable v37 instead of v36; keep standalone Jade v1/v2 disabled. Preserve all
unrelated mods and existing saves. No Git push or LFS change is part of this fix.
