# Heinrich von Adlerhorst — Skill Tree v3

Standalone local test pack: `edh_heinrich_v3_skill_tree.pack`. Contains the entire tested v2 model/portrait bundle plus Heinrich's approved native-skill campaign tree. Use this pack instead of v1/v2, not alongside them.

The campaign skill-node set `edh_heinrich_skill_node_set` is attached to subtype `edh_heinrich_cb`. It contains 52 visible skills: the approved General of the Empire tree plus **Guardian → Đại Bàng Che Chở** from High Elf Handmaiden, available from rank 11. Native icons, effect values/scopes, level requirements, tree links and the General's two mutually exclusive career paths are preserved. Approved renamed skills use private localization keys. All 52 visible skills and their nodes have private IDs; no vanilla character's tree or skill localization is overridden.

The new set also retains the General's 19 active native background/hidden nodes. Mark of Hysh and Imperial Pegasus are excluded as in the approved design. Native Barded Warhorse and Imperial Griffon ancillary grants and subtype permissions are included. New mounted character models are not supplied by this change.

The original Custom Battle entry remains available under Empire. Custom Battle has no campaign skill-point tree, and its existing skill progression was left unchanged. Heinrich is still not recruitable or spawned in campaign; this work does not add a faction, campaign recruitment or startpos changes. The new tree is ready for the same subtype when campaign integration is added. It has not been visually or functionally tested in campaign.

Validation: all 52 skill effects and level-detail rows match their native sources; 143 effect rows, 58 links and 8 career-lock rows were checked. The twelve added DB/localization payloads roundtripped through RPFM. All 85 v2 payloads were preserved. Dependency diagnostics found no blocking issues and only the same 12 schema metadata warnings present in v2.

`pack_validation.json` records source-to-private IDs and validation. `diagnostics_review.json` records dependency checks. `deployment_report.json` records installation and the launcher backup. Launcher installation disables v2 and leaves all unrelated mod activation settings unchanged. To roll back, disable v3 and re-enable v2. No campaign saves or Workshop files were edited.
