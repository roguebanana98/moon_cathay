# Moon-only Onyx Crowmen visibility patch

User request, 2026-11-27: hide Onyx Crowmen for Agents of the Moon.

The separate `mc_moon_hide_onyx_crowmen_v1.pack` runs alongside v37 and declares
the IEE dependency. It denies campaign recruitment for
`cr_cth_agents_of_the_moon` for both `wh3_dlc24_cth_inf_onyx_crowmen` and its
`_ror` version. Moon-specific Custom Battle permission rows are marked campaign
exclusive, with siege attacker/defender permissions disabled.

Other factions and the shared Cathay Custom Battle roster remain unchanged.
Existing armies and garrisons are not edited. There are no scripts, model edits
or Skywing replacement assets in this patch.

Built, installed and enabled: 1,155 bytes, SHA256
`8683b190ce867b9c6daf40e519d448bfb14409ec3183777e6b2644a92211480b`.
The builder is `tools/Build-Moon-Hide-Onyx-Crowmen.py`. Local reports are under
`build/moon-hide-onyx-crowmen-v1`, distribution under
`dist/moon-hide-onyx-crowmen-v1`. Both locations remain ignored by Git.

Actual DB import/export roundtrip passed. When diagnosed with v37's Moon faction
definition, the patch has zero diagnostics; v37 retains its 168 schema/cache
reference-definition warnings. The native-only cache does not include the IEE
faction and reports four missing-faction references without that definition.

The launcher backup is
`build/moon-hide-onyx-crowmen-v1/launcher-before-20261127T021947Z.json`.
All prior launcher entries were preserved. Runtime visibility still needs user
confirmation; installation and static checks are not proof of in-game behavior.

The current Git backup includes source and documentation only. No newly built
pack, model, extraction/cache, machine configuration or launcher file is uploaded.
