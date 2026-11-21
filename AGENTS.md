# Project constraints

## Current handoff (2026-11-03)

- Explicit editable-model Git backup (2026-11-21): user clarified that the
  current model MUST be uploaded, not just code. This authorizes tracking the
  reference-derived editable checkpoint and its packed textures at
  assets/working/moonshadow-assassin/alchemist-11-working.blend, as a scoped
  exception to prior no-third-party-assets-in-Git guidance. Source is latest
  user-saved weapon v3, original SHA 677949771e154bc6b348bbb92e6849e056d0011a48bfb685ecc34b9c131a8bd6.
  Earlier claim that v3 was already fully packed was incorrect: portability
  audit found external image references. New tracked copy explicitly packs all
  used textures, no linked libraries, compressed .blend ~95 MB; local original
  remains unchanged. User pose/visibility/material edits preserved. Portable
  version and SHA are in adjacent portability.json. Clone users continue from
  this tracked file; do not regenerate over it. Still no target animation or
  game deployment approval implied by this backup request.

- Assassin appearance checkpoint (2026-11-21): user asked to SAVE the current
  model for later work, not integrate or animate yet. Live Blender Save completed
  on alchemist-11-khainite-dagger-and-handbow-v3.blend, including latest user
  changes. Authoritative resume path/hash/immutable backup are recorded in
  build/alchemist-11-khainite-weapons/resume-latest.json. Use THIS saved v3 or its
  checkpoint, never regenerate from the build script over the user's edits.
  More Alchemists variant 11, black cloth shader, red/gold details and grey hood,
  Khainite dagger right/handbow left. Native humanoid01e target rig/body retained;
  only native humanoid01d reference stand used to resolve prop grip transforms.
  Target animation/game export remain pending. Keep all user-hidden parts and
  per-view-layer visibility: open full scene, do NOT append all objects (which
  loses hide flags). V1/V2 weapon files are superseded bad attachment/visibility
  previews. See docs/MOONSHADOW-APPEARANCE-CHECKPOINT.md. Do not deploy this scene.

- Moonshadow recruitment revision (2026-11-21): user rejected the new Hideout
  for balance and explicitly requested recruitment at Celestial Tower. V6
  mc_moonshadow_heroes_v6_celestial_tower.pack replaces v5. All seven Hideout
  definition tables and its loc rows removed. Add recruitment and +1 capacity
  to existing magic_tower_1/2/3 (Celestial Tower/Observatory/Beacon), with native
  Region.Owner.RecordKey context restricting both effects to Moon faction.
  +1 at every upgrade, no cumulative +2/+3. No native construction/name/cost or
  Astromancer changes. Character/skill/graphic/spawn payloads byte-identical to
  v5. Authorizes scoped private deployment replacing v5 with launcher backup;
  old pack retained/disabled, unrelated entries and saves untouched. Reports:
  build/moonshadow-celestial-tower/build-report.json and deployment.json.
  No game launch; engine recruitment/context/cap behavior remains unverified.

- Moonshadow Heroes (2026-11-21): user approved BOTH a recruitable assassin line
  and Da Anh as a starting Legendary Hero, using a native temporary model until
  the user selects appearances. Scoped faction-only subtype/unit/art/skill DB,
  tier-III Moonshadow Hideout, new-game-only independent spawn, ASCII English
  localization and private additive deployment are authorized. Intact native
  Khainite Assassin model/rig/animations; no head graft, imported donor pack or
  custom runtime animation key. See docs/MOONSHADOW-HEROES.md and authoritative
  build/moonshadow-heroes/build-report.json + deployment.json. Existing packs,
  launcher entries, saves and Workshop/native files must remain unchanged.
  Static and mocked Lua checks do not establish engine runtime behavior. Game
  testing remains deferred; do not launch the game for this task.
  DEPLOYED/ENABLED additive mc_moonshadow_heroes_v5.pack; all four previously
  active local packs and launcher records unchanged. Static DB/loc/skill graph,
  native compiled battle/campaign animation lookups and 17 mocked spawn cases
  pass. RPFM has 14 schema metadata warnings, zero blocking diagnostics. No
  game launch or engine runtime claims. Da Anh requires a NEW campaign; regular
  assassins recruit via the faction-only Hideout at settlement tier III (+1 cap).

- Playable East Sea Charter (2026-11-18): user asked to select/play the faction.
  v5 `edh_east_sea_charter_playable_v5.pack` exposes original MIXER character
  ID 186992224 via supported frontend enable/major/name/unit-preview APIs.
  Three additive payloads; all v4 campaign/startpos/refuge/model/skill payloads
  byte-identical. Heinrich portrait/subtype; native Karl Franz selection scene
  temporarily reused. New IEE campaign / The Empire; existing saves not converted.
  Actual MIXER library Lua contract and DB roundtrip/diagnostics checks; no game
  testing, human campaign startup not runtime-verified. Deployment authoritative
  in build/east-sea-playable/deployment.json; docs/EAST-SEA-PLAYABLE.md. v5 replaces
  v4, retaining the latter disabled. Character-assets pack remains enabled.

- Refuge/homecoming extension (2026-11-18): user requested Heinrich and Sariwa
  DEPLOYED: v4 enabled locally, v3 retained/disabled. Latest IEE fingerprint
  differs from v3; targeted review preserves original mod startpos, faction-key
  resolution avoids CQI renumbering. See build/east-sea-refuge/dependency-review.json;
  full updated-IEE/runtime compatibility remains unverified. No game/save changes.
  User requested they
  automatically join Agents of the Moon when East Sea Charter dies, then return
  when Home revives. New additive v4 `edh_east_sea_charter_refuge_v4.pack`; v3 is
  the byte-preserved base. Source `edh_east_sea_charter_refuge.lua` +
  `src/campaign/east-sea-refuge.json`; two automatic incidents and Cathay subtype/
  military permissions. Native reassign_character on original CQI/FM identities,
  no character clones, faction revival, XP/skill/inventory rebuilds. Pending
  wounded/partial transfers reconciled on load/round/turn. Return detaches an
  active Heinrich using a Cathay Magistrate replacement so Moon keeps its army.
  No transfers from third-party factions; no event until both ownerships confirm.
  15 mocked Lua scenarios/39 assertions pass; six additive payloads, DB/loc
  roundtrip, all v3 payloads identical, no unexpected diagnostics. In-game native
  reassignment/timing/inventory/recruitment remain UNVERIFIED; user still has
  game testing deferred, DO NOT launch. Deployment status/hashes are recorded in
  `build/east-sea-refuge/deployment.json`. Docs `docs/EAST-SEA-REFUGE.md`.

- Heinrich/Sariwa campaign integration (2026-11-11): user clarified Heinrich is
  Legendary Lord, faction leader/army commander. Sariwa temporarily spawns as an
  independent Hero beside his initial army. `edh_east_sea_charter_characters_v3.pack`
  enabled, territorial v2 disabled; existing graphics/tree v4 remains enabled.
  Static leader replacement preserves IDs 515/2454, government post and force;
  named immortal flags, private art/unit/tree/name changes only. Sariwa native
  create_agent wizard, saved duplicate guard, new-game-only. DB/loc roundtrip,
  exact record reversal, unchanged territorial payloads, 22 Lua cases pass.
  User explicitly said "chưa cần test" after launch: QA process stopped before
  any campaign was selected/created. NO runtime claims for this integration.
  Do not resume in-game testing without further user instruction. QA restoration
  status in `build/east-sea-characters/qa-session.json`; all original saves must
  remain hash-identical, intro option restored. Docs `docs/EAST-SEA-CHARACTERS.md`.

- East Sea Charter (2026-11-10): user requested Dai Loa + Preenn be transferred
  from Agents of the Moon to a new Empire faction, and approved the name East Sea
  Charter. Private add-on `edh_east_sea_charter_faction_v2.pack` deployed/enabled
  ahead of r8. Uses landless MIXER slot `mixer_emp_vaults_gigasdongo`, retains its
  technical key/index; incompatible with another mod activating that slot.
  New IEE campaigns only, native pre-first-tick transfer; Dai Loa capital, Moon
  capital Long Vi. Existing General repositioned/renamed Expedition Commander,
  six native Empire units added. AI faction for now, not frontend-playable;
  Heinrich/Sariwa campaign spawning remains separate. Native campaign reached:
  diplomacy shows East Sea Charter / The Empire / 2 settlements, Preenn tooltip
  confirms ownership; Huyen Ve remains at Long Vi. Read-only native save audit
  confirms exactly the requested ownership and both capitals, eight-unit field
  army and two garrisons. Game exited; all 88 original save hashes verified and
  QA save retained outside user save folder. No engine reload/end-turn test.
  Reports in `build/east-sea-faction/`. Docs `docs/EAST-SEA-CHARTER-FACTION.md`.
  Native campaign/save tested v1. Steam then updated MIXER at Nov10 01:11 local
  (manifest 5077045964861114283), resolving its 301 orphan survival army-unit rows
  with 35 restored parent records. V2 removes the obsolete v1 zero-row workaround;
  all other gameplay/startpos/script/loc payloads are byte-identical to tested v1.
  Faction DB in new MIXER is byte-identical. V1 retained/disabled. Initial
  campaign native intro/narrative warnings persist (already known), not the new
  transfer script. 88 save files backed up/hashed before QA. Never rerun Prepare
  during an active QA session; restore only after exiting the game.

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
