# Project constraints

## Current handoff (2026-11-03)

- Latest v25 r7 deployed/enabled; r6 disabled and retained installed rollback. New native pre-first-tick/new-game-only script places existing Huyen Ve commander/army on valid land beside owned Long Vi (player/AI). No direct ESF/save edits; no changes on loading saves. One Lua added, all r6 payloads byte-identical. Ten placement boundary checks plus existing Lua suite pass; actual new-game spawn/camera remains runtime QA. docs/HUYEN-VE-LONG-VI-START.md, src/campaign/huyen-ve-start.json.

- Fantasy longsword preview approved; user then explicitly requested game integration. V25 r6 privately deployed and enabled, r5 disabled and retained as installed rollback (older v24 pack no longer installed). Static sword has four LODs 12000/6000/3000/1200 triangles, 2K DDS PBR/mips, same preview placement/weapon_2. Exact exported RMV2/DDS reimport/render and12 native pose samples pass. Six graphics payloads added/replaced, every unrelated payload byte-identical to r5, diagnostics unchanged. No game runtime sword QA claimed. src/campaign/huyen-ve-sword.json records selection; full builder preserves it. Backup/hash report in quest-chain deployment.json.

- Historical Blender-first step (superseded by approved r6 integration above): Separate scene
  build/huyen-ve-fantasy-longsword/huyen-ve-fantasy-sword-preview.blend opened;
  approved body/rig unchanged, old sword hidden/preserved, full 467k-triangle FBX
  retained with 4K PBR maps. Nine stand/run/attack attachment samples pass. No new
  game pack/deploy; v25 r5 remains active. Await visual feedback before exporting.
  See docs/HUYEN-VE-FANTASY-LONGSWORD-PREVIEW.md.

- V25 r5 imports user-supplied Da Lien PNG: five portrait/card PNGs resized to native dimensions. All other payloads byte-identical to r4. Privately deployed after user closed game; r5 on/r4 off, backup/hashes verified. Source/manifest: assets/authored/da-lien/portraits; docs/DA-LIEN-USER-PORTRAIT.md. No runtime portrait QA claimed.

- V25 r4 changes Crimson Moonstone icon to native Gem of Blood artwork at user request. Only ancillary type icon data changed; other DB rows equal, scripts/assets byte-identical. No new runtime QA needed/claimed for this visual reference change.

- User requested integration of the entire six-chapter quest chain and continued
  work/testing. All six are implemented and privately deployed in v25 r7,
  mc_huyen_ve_v25_quest_chain_test_r7.pack. R6 is installed/inactive fallback;
  prototypes and r1/r2 inactive. Other mods unchanged. No public distribution.
- Gates 6/8/10/14/18/22: Long Vi + two wins -> pendant; only QB rescues Da Lien
  rank 5 + gem; Avauka or 2000 ransom -> armour; independent Hero archive near
  Leilou then movement to owned Long Vi -> seal; own army kills -> lantern;
  Huyen Ve at owned Long Vi pays 3000 once, two later faction turns -> sword.
  Ownership loss pauses chapter 6; return resumes. No full-set/level25 Hero gate.
- Version2 scalar save state; migration preserves C1; no duplicate/downgraded
  Hero/item, wounded Hero markers prevent respawn. Visual test auto grants/spawn
  suppressed only in progression by saved flag. All previous appearances,
  animations, caster tree (26 nodes/51 points), Moonstone and CB presets retained.
- 13 C1 state regressions, 58 full adapter checks, 10 Hero reward scenarios,
  mocked battle and native generated_battle library boundary contract pass.
  DB roundtrip, hashes, no new blocking diagnostics/metadata warnings.
  Custom kill set covers all13 native land classes incl inf_spr/spcl.
- Live r2 smoke found campaign alias bug: IEE map cr_combi_expanded scripts as
  main_warhammer. R3 accepts both plus requires Long Vi region, excludes ROC.
  R3 native campaign initialisation smoke passed; no old visual spawn observed. Do not claim full campaign playthrough.
- Before campaign QA, all69 user saves copied/hashed. Current restoration status:
  build/huyen-ve-v25-quest-chain/campaign-smoke-session.json. Do not rerun Prepare
  while QA active; exit game then use Restore-Quest-Campaign-Smoke.py. All69 original save hashes and intro preference restored after exiting game. User already approved launcher warning Play and
  game warning Exit; no repeated question needed for the same test flow.
- Rescue prototype v4 (Amber Bow) won in real engine, Da Lien alive/objectives
  green; too easy. New v25 enemy targets escort (unverified balance). No waves or
  timer victory. Fail/death, teleport/return/rewards, kill accounting manual/auto,
  save/load and six-chapter full playthrough remain runtime QA, not unimplemented.
  Frontend v4 Continue returned to Trials of Fate; routing remains QA issue.
- Current sources src/campaign/huyen-ve-quests.json, huyen-ve-rescue-battle.json,
  da-lien.json and mc_huyen_ve_quest_* Lua; shim quest_campaign.lua inert.
  Current status docs/HUYEN-VE-V25-QUEST-INTEGRATION.md, PROJECT_GOALS.txt.
- Game currently9.0.5 (old battle QA9.0.4). Native minor-faction intro/narrative
  warnings observed on new IEE campaign; do not conflate with own quest errors.
- Da Lien is living human wizard using private Beautiful Neferata derivative,
  removed raised collar, warm skin, crescent staff; Moon Arts Yin/Heavens + Life
  healing/armour, no Undead mechanics. Source Workshop pack read-only.

## User-authorized exceptions (2026-10-31)

- Da Lien signature item v24 (2026-11-03): user explicitly requested integration
  of the proposed Crimson Moonstone. Authorizes scoped item/effect/ability DB,
  native-art references, CB equipment and one-time grant/equip for existing/new
  Da Lien, with private test deployment over v23 and launcher backup. 14 additive
  payloads, roundtrip/item gate checks pass; 6 schema enum metadata warnings,
  zero new blocking diagnostics. Grant/reequip/healing runtime remains pending.

- Da Lien skills v23 (2026-11-03): user approved revised Yin/Heavens direction
  with Earth Blood/Flesh to Stone, explicitly requested integration for testing
  and goal update. Authorizes scoped custom tree/effects, CB preset and legacy
  skill reset via documented native API; private deployment over v22 with backup.
  Static DB/overcast/gate/roundtrip checks pass; model and other characters remain
  byte-identical. No direct save edits, public publishing or runtime claims.

- Da Lien appearance integration v22 (2026-11-03): user approved the moon-staff
  preview and explicitly requested mod integration/game testing. Exported collar
  removal and static moon prop, converted approved warm material tint to native
  DDS and deployed v22 over v21 with launcher backup/hash checks. No gameplay
  payload changes; native rig/animation lookups, Custom Battle and Long Vi spawn
  remain. Six exported-mesh/native-clip regressions pass; game runtime pending.
  Earlier scene-only notes below are historical. No public asset redistribution.

- Da Lien moon-staff edit (2026-11-03): user accepted the subtle warm skin and
  requested replacing only the goblet staff head with a moon symbol. Latest
  scene: build/da-lien-moon-staff/da-lien-moon-staff.blend. Silver upward crescent
  with gold edges and wine-enamel/gold connector; original shaft/tassel preserved,
  all new pieces follow be_prop_5. Keeps collar removal and warm-skin material.
  Scene only, not exported/deployed; see docs/DA-LIEN-MOON-STAFF.md.

- Da Lien skin tone (2026-11-03): user requested slightly healthier warm/rosy
  human skin. Latest scene is build/da-lien-skin-warm/da-lien-skin-warm.blend,
  based on the collar-removed scene. Only a copied body material has a reversible
  tint node; source texture pixels and other materials/geometry remain unchanged.
  Must bake/convert this tint before game integration; v21 remains unchanged.
  See docs/DA-LIEN-SKIN-WARM.md.

- Da Lien collar edit (2026-11-03): user requested removal of only the raised
  rear collar assembly within Neferata_Outfit_Sleeves_Collar. Preserve sleeves,
  front choker, other meshes, rig/weights/UVs and source assets. Live unsaved
  Blender state was saved as a separate before-edit snapshot. Edited scene:
  build/da-lien-collar-edit/da-lien-collar-removed.blend; see docs/DA-LIEN-COLLAR-EDIT.md.
  This scene edit has not been exported/deployed over the v21 game appearance.

- Da Lien Custom Battle extension (2026-11-03): user requested Custom Battle
  animation testing. v21 adds scoped Cathay MP Hero permission, character,
  names and temporary native Alchemist magic preset, with private deployment
  over v20 and launcher backup. No new map or final spell-tree implementation.

- Da Lien visual-test integration (2026-11-03): user explicitly requested
  integration of the selected Beautiful Neferata appearance into the mod and
  a spawn at Long Vi to inspect it in game. Authorizes private scoped Hero DB,
  re-keyed reference-derived graphics/portraits, a one-time campaign spawn
  script and integrated v20 deployment over v19 with launcher backup/hash checks.
  Keep Beautiful Neferata source pack, native packs, other mods and saves intact.
  No final custom skill tree, quest acquisition or public redistribution is
  implied. Use the living Cathay Hero framework, not Neferata's Undead/Lord tree.

- Moonlit Command (2026-11-03): user requested the skill after Earth Blood and
  before Flame Storm, plus a native provenance check of Army of Renown +6.
  v19 adds one purchased Moonlit Command level in the existing magic row,
  clones native Spite of da Bad Moon's buff, and keeps Flame Storm's existing
  prerequisite links. Army of Renown is the unmodified native legendary-lord
  skill (+2/+4/+6 RoR army capacity), present on Yuan Bo, Miao Ying, Zhao Ming,
  Karl Franz and other native skillsets; do not reduce it as an invented bonus.
  v19 deployed over active v18 with launcher backup; saves unchanged. Native
  icon alias remains private build only. See docs/HUYEN-VE-MOONLIT-COMMAND.md.

- Item re-equip hotfix (2026-11-03): user reports campaign items cannot be
  equipped again after removal. v18 changes only unique_to_world and
  unique_to_faction on the five custom ancillaries from true to false, matching
  the native Yuan Bo donor. These non-native flags are the working hypothesis,
  not an engine-confirmed root cause. Subtype whitelist, transferrable=false,
  item stats and one-time grant markers remain unchanged. v18 was deployed over
  the active v17 launcher entry with backup. See build/huyen-ve-v18-item-reequip/
  pack-validation.json and deployment-report.json. Re-equip requires user runtime
  verification on an existing save; no new grant or save edit was performed.

- Campaign UI/test extension (2026-11-03): user requested repair of blank campaign
  names, updated character cards, ASCII-only mod UI text, English magic-item
  names, and the complete item set in campaign for testing. v17 implements a
  scoped ASCII direct-name repair, native portrait-settings for mc_moon_warden_art,
  model-rendered portraits, and one-time force-equip of the five existing items.
  The private test update was deployed as mc_huyen_ve_v17_campaign_test.pack;
  its launcher entry replaces active v16. Launcher backup/deployment report:
  build/huyen-ve-v17-campaign/deployment-report.json. Other mods, saves and
  Workshop files are preserved. No gameplay run or public publishing performed.
  Use docs/HUYEN-VE-CAMPAIGN-V17.md for build and runtime test details.

- Runtime animation correction (2026-11-03): user reports v15 is T-posed in game
  and requests diagnosis/prevention for v16. v15/intermediate v16 wrongly use
  mc_huyen_ve_human as man_animation without a runtime BIN/ANIMPACK. Use native
  hu1e_dlc24_yuan_bo_dragon_jade; fixed candidate is
  build/huyen-ve-v16-approved/mc_huyen_ve_v16_native_anim_fix.pack.
  See runtime-animation-fix.json and docs/HUYEN-VE-APPROVED-MODEL.md.
  Do not deploy the intermediate mc_huyen_ve_v16_approved_model.pack or rely on
  Blender direct clip playback / finite coordinates as an engine lookup test.
  Fixed candidate remains undeployed and not game-runtime verified.

- Approved model integration (2026-11-03): user selected the intact model from
  Workshop 3468491534 with the clean-shaven texture and recorded visibility,
  then requested integration and reuse of the mod's original LODs if possible.
  Private local v16 graphics derivatives and integration over v15 are authorized.
  Use docs/HUYEN-VE-APPROVED-MODEL.md and the pinned approved-model.json snapshot.
  Native LOD vertex channels remain unchanged except excluding disabled parts;
  restore lotus sword native alignment by removing the concept03-only offset.
  Do not import the donor mod's buffs, DB rows or flags. Reference/build only
  for third-party assets; no public redistribution. v16 is not deployed.

- Deployment scope extension (2026-11-02): user explicitly requested putting
  v15 into the game for testing. This authorizes copying the validated private
  pack into the configured WH3 data directory and replacing the active v14
  test entry in local launcher/mod configuration, with backups and hash checks.
  Preserve native game packs, Workshop/dependency packs and saves. No publishing.
  Earlier no-deployment rules below are superseded only for this scoped test
  deployment. Opening the launcher for the user's test is within this scope.

- Animation integration extension (2026-11-02): user requested the complete
  animation integration after approving manual sword placement on
  before-hand-fix. Preserve that body's hands, mesh, skin and native bone bind.
  Local integration may apply the recorded sword offset to all prop LODs,
  export authored graphics, add the scoped native-derived animation table and
  DB links for battle/campaign uniforms, and build a private integrated pack
  based on v14. Native clips/fragments and metadata are referenced in-game,
  not bundled as copied game assets. No deployment, gameplay launch or public
  redistribution is included. Do not use the rejected rebuilt-hand scene.

- Model scope extension (2026-11-02): user explicitly authorized optimizing the
  supplied concept03 Tripo mesh, fitting Yuan Bo's humanoid01e skeleton,
  rigging/weighting, converting materials and attaching the authored lotus
  sword to weapon_2. Local Blender/RMV2/LOD/VMD and graphics-only test pack
  outputs are authorized. Preserve source FBX and sword assets; native donor
  geometry/animations remain in ignored reference/build only. No game/Workshop
  deployment, gameplay launch or publishing is included.

- Tooling scope extension (2026-11-01): user authorized downloading and preparing
  tools for the new lord's 3D model. Portable Blender, Asset Editor, Paint.NET,
  the Total War RMV2 add-on and DirectXTex are prepared under ignored
  `tooling/model-workbench`; paths and validation are documented in
  `docs/MODEL-TOOLS.md`. This does not authorize game/Workshop deployment.

- Campaign scope expanded specifically to regroup Primal Labyrinth (Long Vi capital,
  Leilou) and Paradise Spires (Dai Loa capital, Avauka, Preenn).
- User explicitly approved installing EditSF 1.3.0 under local tooling and packaging
  derived IEE startpos plus the two province-related DB tables in a private local
  test pack. This is an exception to the third-party bundling prohibition below
  only for this ignored local test artifact; no third-party content enters Git/src.
- Deployment to game/Workshop, gameplay launch and public redistribution are not
  included in those approvals. Preserve original dependency packs and live saves.
- User additionally requested 8 total building slots at Long Vi, preserving its
  existing buildings including the port, and approved a separate current WH3
  RPFM schema in local tooling. The private test pack may include the scoped
  building definitions and localization required for that change.
- User selected Cathay major-settlement tiers I-V for Long Vi, including major
  settlement stats/garrison and normal tier-dependent slot unlocking, capped at
  eight total slots. Keep the existing port and resources.

## General constraints

- User preference (2026-11-02): use existing game artwork for equipment/ability
  icons for now; do not generate new art. Native paths are referenced directly;
  the three phase-ID icon aliases may reuse native PNGs byte-for-byte only in
  the ignored private build. No native artwork enters src or authored assets.

- Scope extension (2026-11-02): user requested the five proposed Huyen Ve items
  implemented in the private local mod and equipped/selectable in Custom Battle
  for testing where supported. This authorizes authored icons, scoped ancillary,
  effect/ability/set definitions and native Custom Battle item links. Campaign
  quest acquisition is still pending; no automatic campaign grant, game/Workshop
  deployment, gameplay launch or publishing is included.

- Scope extension (2026-11-01): user authorized implementation of the Legendary
  Lord described in PROJECT_GOALS.txt, replacing Ju Di. Male, temporary name,
  existing human sword model, healing/AOE/Yang Dragon's Breath, no dragon form
  or Blood-line branch. Private local prototype derivatives are part of this
  implementation; preserve v3 campaign changes and do not deploy or publish.

- Phase 1 only until the user explicitly expands scope. Do not change gameplay/campaign.
- Never write to game installation or Workshop paths. Reference packs are read-only inputs.
- Do not install/update software or schemas without user permission.
- All extraction goes to ignored `reference/local/`. Never bundle or commit third-party assets.
- Only authored source may enter `src/`. Keep source, reference, build, and dist separate.
- Use verified paths in ignored `config/local.json`; do not guess tool commands or Lua APIs.
- Any future runtime claim must distinguish static startpos, frontend placeholders, MCT options, and a live save.
- Re-check dependency hashes after Steam updates. Validate schema before importing changed DB tables.
- No publishing or gameplay launch is part of Phase 1.
