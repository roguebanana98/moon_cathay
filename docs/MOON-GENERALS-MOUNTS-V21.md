# Moon generals mount branches - private v21

Restores functional mount branches to both ordinary Moon generals while preserving every existing v20 payload byte-for-byte. The foot appearances, black/white palette, original skin and approved weapons remain unchanged.

| Lord | Mount | Unlock criterion level |
| --- | --- | ---: |
| Assault General | White Warhorse | 4 |
| Assault General | Great Stag | 14 |
| Bastion General | Warhorse | 4 |
| Bastion General | Jade Longma | 9 |
| Bastion General | Celestial Lion | 15 |

Assault uses the original WWD white horse and stag assets, with all four source LODs and complete private WS/material/texture paths. Mount scale follows the donor. Bastion uses native Celestial General mount models and native campaign overrides; the source WWD swapped Longma/Lion campaign override rows are not copied.

The five private skills retain native mount icons and effects. Each grants its own ancillary and mounted unit, with subtype permissions, skill-level criteria, campaign rider animation override, and Custom Battle mount selector/permissions. No native lord body or native mount ancillary is assigned to the new generals. Assault's mounted variant attaches the existing polearm to be_prop_1, matching the source mounted profile; its foot variant retains be_prop_0. Bastion retains weapon_1.

Mounted costs/HP/charge and combat deltas follow native mount upgrades. Bastion inherits native mounted weapon stats and flying mount attributes. Assault remains melee with no bow, ammunition or Elf firing/vanguard attributes. The stag gets the CG mounted attributes plus native fear; its AI/ground behaviour remains Cathayan melee. Native compiled rider lookups and Cathay culture mappings are checked, including the stag creature profile.

## Validation and limits

- Five mounted rider profiles: stand, locomotion and attack, three frames each, 45 samples on the previously roundtripped shipped rider geometry; finite deformation and nonzero animation motion, no importer warnings.
- Rider/weapon idle renders inspected; four LODs on both custom mount bodies, complete material override coverage for every LOD/part and present DDS sources.
- Five complete skill -> private ancillary -> mounted unit chains verified, including automatic level criteria and Custom Battle selectors.
- All new tables/localization roundtripped through RPFM; no blocking diagnostics. All in-game text English ASCII.
- All v20 internal payloads retained exactly; no changes to old hero fixes, foot models, saves, native or Workshop packs.

No game was launched. Campaign acquisition, existing-save skill refresh, full mount/rider fit, flying transitions and combat still require an in-game test. Rider-only Blender renders are not proof of complete mount clipping clearance.

The combined active candidate is mc_moonshadow_heroes_v21_general_mounts.pack. Deployment report, launcher backup and hashes are in build/moon-generals-v21-mounts/deployment.json and pack-validation.json. Previous v20 is retained disabled; enable only one combined version. No public distribution or Git upload.

Tools: Prepare-Moon-General-Mounts.py, Build-Moon-General-Mount-Pack.py, Review-Moon-General-Mount-Animations.py, Deploy-Moon-General-Mounts.py. Private donor assets stay under ignored reference/build paths.
