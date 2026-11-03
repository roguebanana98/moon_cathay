# Project constraints

## Current handoff (2026-11-03)

- Current goals/checklist: PROJECT_GOALS.txt sections 5 and 5A. Current Lord
  overview: docs/LEGENDARY-LORD.md. Latest recorded private deployment is v19;
  source and installed pack hashes were rechecked equal. This does not verify
  live launcher state or game runtime. Version-specific notes below are history.
- The approved v16 appearance/native animation fix is inherited by v17-v19.
  Concept03/Tripo is historical, not the selected body for further integration.
- User approved the revised quest design: five campaign item missions and only
  one final quest battle for a new LH. Chapter 3 is Hero investigation/report
  delivery; chapter 5 is paid sword restoration. Older chapter-3/5 quest battle
  plans are superseded. See docs/HUYEN-VE-QUEST-CAMPAIGN-DESIGN.md.
- Lam Anh remains a proposed LH identity. Quests and LH are not implemented;
  the one remaining battle has no validated map/coordinates/roster/timeline yet.
- This handoff update records documentation state, not new authorization to
  deploy, launch gameplay, publish or claim pending fixes runtime-confirmed.

## User-authorized exceptions (2026-10-31)

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
