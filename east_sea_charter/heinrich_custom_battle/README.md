# Heinrich von Adlerhorst — Custom Battle Test v2

Open **Battle → Skirmish vs A.I. → The Empire → Lords → Heinrich von Adlerhorst (Test)**.

This is a separate on-foot lord entry for model/animation testing. It uses the installed Karl Franz Reskin - MM body with native Empire General sword/shield props and `hu1_empire_sword_and_shield` animation table (`humanoid01`). Temporary combat statistics, abilities and cost are copied from the native on-foot Empire General. A portrait was rendered from the tested Blender model.

The character is exposed to the Empire custom-battle roster; no campaign faction membership, recruitment permission, campaign script or startpos was added. No original Karl Franz/General database row or appearance path is overridden. All private asset paths use the `edh_heinrich_cb` prefix. Required reskin geometry/materials/textures are bundled locally; the original Workshop mod does not need to be enabled for this private test.

Pack: `edh_heinrich_custom_battle_v2.pack` (installed in the game's data folder and enabled in the launcher).

Validation: 85 final payloads roundtripped through RPFM; deployed pack hash matches the source. Fresh game dependency diagnostics reported zero blocking issues and 12 schema metadata warnings about unspecified reference columns. Source model bytes are preserved. The prior Blender test includes eight native motion clips.

`pack_validation.json`, `diagnostics_review.json` and `deployment_report.json` record checks and deployment. The launcher configuration was backed up under `deployment_backup/` before adding the new entry; all prior mod entries and activation states were preserved.

To disable the test, switch off `edh_heinrich_custom_battle_v2.pack` in the launcher. Workshop files and campaign saves were not edited. This bundle is for local testing; it contains third-party mod assets and has not been published.

Runtime check on game 9.0.5: the lord appeared in the Empire roster, was recruited, loaded into a land battle, displayed the reskin body/sword/shield and completed a movement command. The initial card fallback was corrected by adding private portrait-settings entries. After restarting with v2, the corrected army card and selected lord were verified in Army Setup. The v2 model bytes are identical to the in-battle-tested v1 model. Full combat, mounts and campaign behavior were not tested. The game is left at Army Setup with Heinrich selected for the user's own battle test.

