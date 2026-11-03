# Huyen Ve campaign UI and test equipment - v17

Current status note (2026-11-03): v19 is the latest recorded deployed integrated
private test pack. It inherits the v17 UI/test-grant changes and v18 re-equip
hotfix below, then adds Moonlit Command. Version-specific enable/restart notes
below describe their historical deployment stages; use one integrated pack.
See [v19](HUYEN-VE-MOONLIT-COMMAND.md) and [current Lord status](LEGENDARY-LORD.md).

Current test hotfix: `mc_huyen_ve_v18_item_reequip.pack`, deployed over v17 on
2026-11-03 after the user reported that removed items could not be equipped
again. Only the five items' `unique_to_world` and `unique_to_faction` flags
change to false, matching the native Yuan Bo quest-item donor. The cause is a
working hypothesis pending in-game re-equip verification. Subtype restrictions,
`transferrable=false`, stats, existing inventory and grant markers are unchanged.
No re-grant or save edit is needed; restart and reload the current save to test.
Reports are in `build/huyen-ve-v18-item-reequip/`.

Updated 2026-11-03 (Asia/Saigon). User requested missing campaign-name repair,
current model portraits, English item names, no accented mod UI text, and the
full equipment set in campaign for testing.

Private integrated pack: `build/huyen-ve-v17-campaign/mc_huyen_ve_v17_campaign_test.pack`.
It is installed in the configured game data directory; the launcher enables v17
and disables the prior v16 entry. Backups and exact paths are recorded in
`build/huyen-ve-v17-campaign/deployment-report.json`. No save was edited.

## Changes

- On campaign load and faction turn, the scoped Huyen Ve/legacy leader name
  repair uses `change_character_custom_name` with the direct ASCII display name
  `Huyen Ve, Warden of Long Vi`. This avoids an unresolved localisation lookup
  leaving the character name blank. It runs again after initialisation to avoid
  an earlier first-tick name override. Other faction characters are untouched.
- All 71 localisation rows in the submod pack contain ASCII-only text.
- Names: Moonshadow Jade Pendant, Long Vi Mountain-Pattern Armour,
  Warden's Seal, Moon Lantern, Nightwarden's Blade. Item mechanics are unchanged.
  Associated ability names/tooltips and the set title are English.
- Four transparent portraits are rendered from the approved exported model.
  Native portrait-settings BIN files bind `mc_moon_warden_art` to the custom
  images and the actual VMD variant `mc_huyen_ve_human`. Army cards, faction-leader
  thumbnails, portholes and Custom Battle portrait links are covered. No vanilla
  or Workshop portrait path is overridden.
- Private test script grants and equips all five items on Huyen Ve, including
  in existing saves. It runs one second after first tick, with a faction-turn
  fallback if the character is not present yet. Per-item saved markers and
  character ownership checks prevent repeat grants on every reload. Existing
  gear in those five slots may be replaced as part of equipping this test set.
  Quest-based acquisition is still not implemented; this is a test grant.

## Validation

RPFM import/extract matches all authored data rows and scripts. All portrait
settings convert to/from binary and point to included PNGs; dimensions and
transparency checked. No new/changed RPFM diagnostics compared with fixed v16.
Only `unit_card`, `general_portrait`, and the Custom Battle `portrait` field
change in the three display-related DB rows. Ancillary mechanics, 3D graphics,
fixed native animation link and startpos are preserved byte-for-byte.
This is static verification; save-load name/portrait refresh and equipment
effects still require the user's in-game test.

## Test

Restart the game using v17 alone as the local Huyen Ve pack, with the existing
MIXER/IEE dependencies. Load the current campaign; a new campaign is not required.
After first tick, reopen the character panel and check the name, army card,
faction-leader thumbnail and all five equipped items. If Huyen Ve is absent,
the grant retries at the faction's turn. Reloading should not duplicate items.

## Rebuild

1. `Render-Huyen-Ve-Campaign-Portraits.py` in configured Blender 5.2.3.
2. `Prepare-Huyen-Ve-Campaign-UI.py` with configured Python.
3. `Build-Huyen-Ve-Campaign-UI-Pack.py`; existing output is protected from overwrite.
4. RPFM diagnose against configured dependencies and compare with fixed v16.
5. `Deploy-Huyen-Ve-Campaign-UI-Test.py` is a guarded one-time deployment script.

Inputs: the fixed v16 pack, its exported animation review scene, extracted base
TSVs under `reference/local/huyen-ve-v17-base`, and RPFM-decoded portrait-settings
donor JSON in the v17 build directory. Reference-derived artifacts stay in ignored
build/reference folders. Reports: `ui-campaign-manifest.json`,
`portrait-render-report.json`, `pack-validation.json`, `deployment-report.json`.

API reference: [CA campaign scripting documentation mirror](https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html).
