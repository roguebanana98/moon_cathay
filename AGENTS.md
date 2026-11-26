# Project constraints

## Current handoff (2026-11-03)

- ACTIVE V34 ZHAO YUAN BO INTEGRATION (2026-11-24): user approved grip-fixed Blender and requested mod update. Enabled mc_moonshadow_heroes_v34_yuan_bo_lord.pack SHA256 1c46a88ecfbcf54f7eb3481677775ebf9704d4bd90f3a4c2ca9aceb87e569b01; v33 retained disabled; current load-order14 preserved (launcher reordered since previous deployment). mc_mooncourt_lord_human man_animation=hu1e_dlc24_yuan_bo_dragon_jade, art1986113200 campaign=cam_lord_hu1e_dlc24_yuan_bo_dragon_jade. Real native compiledbattleBIN+campaignBIN and nativehumanoid01e mappingverified; no customlookup/clipexport/Blender montage bundled. Private sword WS/material/textures, original RMV2 geometry/all4LODs/materialpivots byte-identical; native weapon_2 VMDslot added. Correct native materialpivot handles grip; no hand/body/weight or arbitrarymesh edits. Four portrait/card PNGs rerendered exactapprovedscene. Only7existingpayloads changed (2DB onefield each,VMD,4PNG)+7swordassets added; allother v33payloads exact, including skills/stats/recruitment/Moonveil. Source WWD skills REMAIN, Moon/water/fire redesign STILL PROPOSAL. RPFM roundtrip zero blocking diagnostics. No game launch/runtimeverified, no saves/native/Workshopmodified. Reports build/moon-v34-yuan-bo-lord; docs/ZHAO-YUAN-BO-INTEGRATION-V34.md; currentreference reference/local/moon-v34-roundtrip/db. Finalpreview build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-grip-fixed.blend preserved.

- ZHAO SWORD GRIP FIX (2026-11-24): user correctly reported blade-in-hand on original trial. Cause was preview COPY_TRANSFORMS overriding imported native sword RMV2 pivot. Corrected separate scene build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-grip-fixed.blend uses CHILD_OF identityinverse preserving matrix_basis pivot(-.4833669,-.0021239,-.0019782). Sword/body vertices, hands, skin weights and rig unchanged. All341frames matrix/palm-handle checks;attack+cast renders visually inspected. Original bad scene/report explicitlysuperseded, userunsavedwindowpreserved. Original builder corrected too. DO NOT rely on weapon2 attachment equality alone as grip proof; expected includes native material pivot. Active mod remainsv33, no integration. User visual approval pending. Docs ZHAO-YUAN-BO-ANIMATION-TRIAL.md, grip-fix-report.json, tools/Fix-Zhao-Yuan-Bo-Sword-Pivot.py.

- ZHAO/YUAN BO BLENDER TRIAL (2026-11-24): user requested trying Yuan Bo skeleton/weapon/animations on current Zhao Yixuan lord. Separate scene build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-animation-trial.blend; v33 mod NOT changed. Native humanoid01e bind/weights preserved, original Yuan Bo sword zero-offset weapon_2;7native clips (idle,walk,run,2attacks,2casts) +stationary review montage with markers.21sampled body checks,per-frame native swordattachment checks passed;no missingtextures. Review docs/ZHAO-YUAN-BO-ANIMATION-TRIAL.md and preview-report.json. Montage is Blender-only;do not export as game animation. Await user visual approval before integration. Proposed Moon/water/fire skill redesign is STILL PROPOSAL, v33 retains WWD originalskills. Original open unsaved WWD gallery preserved.

- ACTIVE V33 LORD ROSTER (2026-11-24): enabled mc_moonshadow_heroes_v33_lord_roster.pack SHA256 909cab5c8a97ce6112b6bad90d8aa955ae0d336120a890a4b0690b13f936e16b, v32 retained disabled, active load-order11 preserved. Bastion+Assault now share native Shugengan category wh3_main_cth_dragon_blooded_shugengan (native Yin/Yang actually ONE tab); native Shugengan disabled Moon-only; private Assault category cleared; shared labels unchanged, no UI script. NativeCGcategory hosts mc_mooncourt_lord, temporary Zhao Yixuan, WWD gallery20 deer_cth_zhaoyixuan. User explicitly requested original WWD skills:73nodes,14customskills,3customabilities,5phases,original seal unlock/growth/rank gates/Yin+Undeath spells. Namespaced dependencies, English ASCII text and reused source icons, exact source unit stats/costs. Repeatable regular subtype, Vietnamese namepool; original female art/name mismatch corrected consistently. Source has no mounts. No original WWD pack dependency; no imported campaign scripts/other faction changes. Native hu1e_mage_lord, humanoid01e, source4LODs and textures;18 Blender samples passed. RPFM roundtrip zero blocking diagnostics and independent source graph/stats/category audit passed. Runtime NOT verified; no game launch. v32 Moonveil selections and all other v32 payloads unchanged except2category DBs. Reports build/moon-v33-lord-roster, docs/MOON-LORD-ROSTER-V33.md; current reference/local/moon-v33-roundtrip/db. No saves/native/Workshop/public modifications.

- ACTIVE V32 APPROVED MOONVEIL (2026-11-24): user selected BLACK gallery models02,06,10,14 = body01/body03/body01a/body03a with head2 for ALL FOUR. Do not add other heads/colours/body random options. Enabled mc_moonshadow_heroes_v32_moonveil_approved.pack SHA256 137dba76c2a95c065a935434fbf2ecd0ef67e6b4f1de050da1bca9c1715f702a, v30 retained disabled, load-order11 preserved. Built directly on v30, NOT rejected v31. Four old appearance IDs white/black/blue/red retained for saved artsets; each now exactly one selected black body + head2. Four VMD +12 PNG replacements only; all DB/scripts/localization/native mesh/material/texture DDS/weights/skeleton/LODs unchanged. Portrait/card rerenders,108 Blender animation samples passed, RPFM roundtrip and diagnostics passed. Runtime not verified; no game launch. Original16-model gallery unchanged; separate final editable scene build/moonveil-v32-approved-variants/moonveil-approved-02-06-10-14.blend. Docs MOONVEIL-APPROVED-VARIANTS-V32.md; current DB reference reference/local/moon-v32-roundtrip/db. Reports build/moonveil-v32-approved-variants. No saves/native/Workshop/public/Git modifications.

- V31 MOONVEIL CANDIDATE STOPPED / REJECTED (2026-11-24): user stopped black-body/four-head-family candidate because preview repeats one head. Source four palettes share only TWO head geometries (head1/head2); representative renders all used head1, differing accessory colours. Do not call these four distinct faces. V31 remains undeployed; active mod v30 unchanged. See build/moonveil-v31-black-outfits/USER-REJECTED.txt. Do not deploy this rejected candidate.

- ACTIVE V30 BUILDING PREVIEWS (2026-11-23): supersedes v29 activation below. Enabled mc_moonshadow_heroes_v30_building_previews.pack SHA256 06a2ac285b6ae858907061ad3f621daab95ffa2b771acaaa5c264ee229f80ff6, v29 retained disabled. Prior active load-order slot11 preserved (launcher had reordered since v29 deployment). Adds Moon-faction campaign_exclusive units_custom_battle_permissions for six regular heroes: Moonshadow, three casters, Ordnance Master, Moonveil. Moonshadow previously had no CB permission; adds its native Cathay military grouping too. All existing v29 payloads byte-identical; no recruitment/cap/skill/model/script changes. All portraits/cards/uniforms resolve; RPFM roundtrip and diagnostics passed. Building-browser rendering still requires live confirmation; do not claim runtime fix proven. Current DB reference reference/local/moon-v30-roundtrip/db. Reports build/moon-v30-building-previews and docs/MOON-HERO-BUILDING-PREVIEWS-V30.md. No game launch, save/native/Workshop modification.

- ACTIVE V29 GENERAL TABS (2026-11-23): supersedes the v26 activation in the crash rollback entry below. mc_moonshadow_heroes_v29_general_tabs.pack is deployed/enabled at load-order slot9; v26/v27/v28 disabled. SHA256 b2f13fdc6022b2459b15097be9a28298684f09bc7557ba03cc5a05d24c9dbf67. Built directly from v26: Bastion recruitment_category now wh3_dlc24_cth_celestial_general; private Bastion category removed; Assault retains its own category at order4. Shared native tab label remains Celestial General; native CG Yin/Yang subtypes remain disabled for Moon. Only two DB payloads changed, all other payloads byte-identical to v26. No UI hiding script. Static/RPFM checks passed, runtime and crash resolution unverified; no game launched. Current DB reference: reference/local/moon-v29-roundtrip/db. See docs/MOON-GENERAL-TABS-V29.md and build/moon-v29-general-tabs reports.

- LIVE CRASH / V28 ROLLED BACK (2026-11-22 local): user reports native CTD
  when clicking Huyen Ve army. CONFIRMED run used v28, script_log_221126_1813.txt
  has UI errors beginning152.8s in our mc_moon_hide_celestial_general_tab.lua
  matches/apply, then lord_list, followed by native and CustomLordCreation UI
  component failures; crash18:16:17 mdmp/unsymbolicated stack. Exact native
  crash cause not proven; new script is observed broken. DO NOT claim mocked
  UI tests prove live safety. Removed from active mod by RE-ENABLING EXISTING
  v26 mc_moonshadow_heroes_v26_recruitment_names.pack, SHA256
  c3b6a083c76d0f1360a4c6a3afef736921c115858fd54a56824c58d6c20d0e79.
  v28 disabled, all other versions disabled; order restored to active slot9.
  Payload audit: v28 minusexactONE tab-hiding script ==v26 byte-for-byte. All
  names/recruitment/buildings/Moonveil/skills/models/v25Assaultrepair retained.
  EmptyCGtab may reappear; native CG recruitment stilldisabled. No saves or
  pack files edited. Unsafe source and test now .lua.disabled, retained not
  destroyed. Four v27/v28 build/deploy scripts explicitly raise retired error.
  Do NOT rebuild/re-enable them or add another deferred UI/simulatedclick patch
  without actual lifecycle reproduction. Earlier v27/v28 success claims are
  STATIC/MOCK ONLY, invalid as runtime assurance. No other mods disabled.
  tools/Rollback-Moon-UI-Crash.py performed exact payload/hash audit and atomic
  launcher rollback, unrelatedentriesunchanged, backup in build/moon-ui-crash-
  rollback/rollback.json. Logs/usedmods/native stack preserved there; no debugger
  attach or game launch after rollback. User must restartgame/loadsame save and
  selectarmy to confirm whether removal resolvesCTD; runtime status UNKNOWN.
  docs/MOON-UI-CRASH-ROLLBACK.md, source manifests now activev26 +tabhidingoff.
  Do not mark crash fixed without that live confirmation. Other earlier intro/
  narrative Lua warnings exist but are separate, not patched in this turn.

- EMPTY CELESTIAL GENERAL TAB HIDDEN (2026-11-22 local): user explicitly
  clarified native CG recruitment tab is EMPTY, not recruitable lords. Native
  Yin/Yang permissions were alreadydisabled. Active final combined v28
  mc_moonshadow_heroes_v28_hide_celestial_tab.pack, SHA256
  10d30f33fb9b86cddf2d1e1127cb56f45afa157cfe1683ffa3abb48973ea5007.
  v27 interim and v26 retained disabled. One added UI-only campaign script over
  v26; no global category/DB/UI-XML overrides. All other payloads unchanged.
  src/script/campaign/mod/mc_moon_hide_celestial_general_tab.lua hides exact
  wh3_dlc24_cth_celestial_general button only for local Moon faction. Native
  character_panel/.../lords_and_agents_holder/lord_parent/list_box hierarchy
  and label child verified from current ui3.pack. Match categorykey or native
  localised label. If emptyCG selected, select Assault(Bastion fallback); preserve
  existingotherselection. IMPORTANT lord_parent:Visible guard prevents touching
  HERO recruitment (samepanel), added infinalv28 afterv27. Panelopenbounded
  refresh .1/.4/1sec; clickdebounce onlywhileopen; missing/closedpanels safe.
  Lua tests forscope, translationfallback, defaultselection, otherfactions/tabs,
  absent/closed/load/hero-modepassed. NativeUIAPI usagesverified. RPFM roundtrip
  zero blocking diagnostics. No game launch; visible tab removal NOT runtime
  observed. User restartv28 and reopen lordrecruitment, no newcampaign needed.
  No save/native/Workshop/Git/public writes. tools/Hide-Moon-Celestial-General-
  Tab.py and Deploy-Hide-Moon-Celestial-Tab.py built interimv27; FINAL tools/
  Hide-Moon-Celestial-Tab-Lord-Guard.py +Deploy-Moon-Celestial-Tab-Guard.py.
  tools/tests/moon-hide-celestial-general-tab.lua; docs/MOON-HIDE-CELESTIAL-TAB-
  V28.md; build/moon-v28-celestial-tab-guard reports/launcherbackup. DB reference
  remains reference/local/moon-v26-roundtrip (v27/v28 onlyLua); faction row now
  includes privateVietnamese namegroup fromv26, do not revert toold IEE template.

- MOON RECRUITMENT + VIETNAMESE NAMES (2026-11-22 local): user requested
  removing native Astromancer/Alchemist from Moon recruitment, Moonshadow at
  infantry buildingtier2, and Vietnamese ASCII names. Active combined v26
  mc_moonshadow_heroes_v26_recruitment_names.pack, SHA256
  c3b6a083c76d0f1360a4c6a3afef736921c115858fd54a56824c58d6c20d0e79.
  v25 retained disabled. Astromancer wizard permission mod_disabled=true added
  to existing Moonveil permission table; original Alchemist alreadydisabled,
  replacements unchanged. No characters deleted. Assassin availability AND +1
  cap moved from3 towerlevels to wh3_main_cth_jade_barracks_2/_3, ownercontext
  mc_moonshadow_owner/scopes/values unchanged; no tier1unlock/no stacking or
  native building stat/garrison/cost change. Threecasters still use towers.
  Authored src/data/agents-of-the-moon-vietnamese-names.json +CSV:50surnames,
  152male/283female/14unisex given names,499records,22450distinct combinations.
  StableID blocks1986120000/1000/2000/3000, positivefrequency, ASCIIletters/spaces.
  Private group names_mc_agents_of_the_moon_vietnamese, family_name before
  forename fordefault/cn/kr/zh. Actual current IEE faction row freshly extracted
  after auditing all active factions_tables: only IEE defines Moon. Only its
  name_group changed, all otherfields exact.8 authored regular subtypes get
  explicit group:2generals,3casters,Moonveil,Moonshadow,LukeOrdnance. Fixed
  HuyenVe/DaAnh untouched. Native humans withblank names_group inheritfaction;
  explicit nonhuman groups(Tigermen) retained. Existing characters, pregenerated
  pools and manualCustomLordCreation names NOT retroactively renamed; new names
  require generation/poolrefresh. No new renameLua or save migration.
  RPFM roundtrip/zero blocking diagnostics; IDcollisions/ASCII/uniqueness/CSVJSON
  equality/length<32/nativefaction/subtypefield equality checked. All script,
  model/UI/skill payloads retained byte-identical inclv25Assaultrepair. No game
  runtime test or save/native/Workshop/Git/public writes. tools/Create-Moon-
  Vietnamese-Name-Data.py(one-time refuses overwrite), Build-Moon-Recruitment-
  Vietnamese-Names.py, Deploy-Moon-Recruitment-Vietnamese-Names.py; docs/MOON-
  RECRUITMENT-NAMES-V26.md; src/campaign/moon-roster-names.json and moonshadow-
  heroes.json updated; build/moon-v26-recruitment-names reports/launcherbackup.

- ASSAULT CAMPAIGN MODEL REPAIR (2026-11-22 local): user reports wrong model
  BOTH map and character window. Deployed/enabled mc_moonshadow_heroes_v25_
  assault_campaign.pack, SHA256 7c8aca0609149db94d5a01ac77aea31e7655c4882ca1dbe6be57b6e2821fa283.
  v24 retained disabled. Approved model08 body/weapon/VMD bytes unchanged.
  Observed mismatch: original WWD guanshanart male=true, our Assault only had
  female artset. Added male-compatible mc_assault_general_art_male, id1986113100,
  same uniform/VMD and approved portrait images; existing female artset retained.
  All4 uniform filename fields explicitly mc_assault_general, politician was
  blank. Only existing changed payload agent_uniforms/zzzz_mc_moon_generals,
  only Assault politician field. Other assets/skills/stats/mounts/heroes unchanged.
  Added src/script/campaign/mod/mc_assault_campaign_appearance.lua: native
  cm:add_character_model_override chooses matching male/female private artset,
  exact subtype + Moon faction + main_warhammer/cr_combi_expanded only; old-save
  first tick, created/selected/transferred/recovered/turn events, session cache.
  Does not spawn/replace characters or alter XP/gear/skills/movement. Lua boundary
  tests and RPFM roundtrip/diagnostics passed. Native is_male, CharacterSelected
  context and model override usages verified from native/local scripts.
  Fuwuvi Custom Lord Creation active; its files/mapping not changed. Latest
  used_mods.txt listed v22 despite launcher v24 before update. User should launch
  v25, load existing save and select Assault; no new campaign required by repair.
  NO in-game visual confirmation yet: gender mismatch plausible, not proven
  sole root cause. No saves/native/Workshop/Git/public writes. Tools/Fix-Assault-
  Campaign-Appearance.py, Deploy-Assault-Campaign-Appearance.py (actual lowercase
  tools dir); tools/tests/assault-campaign-appearance.lua; docs/ASSAULT-CAMPAIGN-
  APPEARANCE-V25.md; build/assault-v25-campaign-appearance reports/launcher backup.

- MOONVEIL ADEPT IMPLEMENTED (2026-11-22 local): user approved an ordinary hero
  replacing Alchemist's role, Element Bender model, Lore of Light protective/
  control theme, no metallurgy. Active combined v24 mc_moonshadow_heroes_v24_
  moonveil_adept.pack, SHA256 fbc216739933f919c87326ed548e772f4148e6e13e432a7e6aa5d727e50af60f.
  v23 retained disabled; every v23 payload byte-identical. New subtype
  mc_moonveil_adept, agenttypeengineer (native Alchemist actions/capacity), caster,
  ordinary/repeatable. Moon faction-only Alchemist permission disabled, new
  private recruitment category enabled;7 original Alchemist building availability
  rows owner-scoped; no new building/cap. Native Alchemist foot/horse/lantern
  stats/costs exact. Full native Light hero tree, native spell names/icons/VFX,
  hidden starting Shem's, generic mage support; no Metal/metallurgy branches.
  Warhorse/Sky Lantern private mount grants, native level6/14;3 hero units in
  Cathay CB Heroes, wizard_light parentheroes_agents, general_unit=false.
 4 appearance families from Workshop3836052402 @taolu_cth_esoteric_masters.pack
  (hash b1eef9a9c77dec10cc8ef569f3419a506a5911ea09fbb6f89d011bd16ca0b9de):
  Air/sourcewhite visually GOLD, Earthblack, Waterblue, Firered. Source colours,
  visible clothing/skin unchanged.40 namespaced WSModels, each4LODs, complete
  materials/texture closure,8 body+2head options/family; coherent nested VMDs.
 4 artsets/uniforms/portrait settings; CB default sourcewhite/gold. No source
  regiment gameplay/assets outside private ignoredbuild. Source mod not required.
  108 representative native battle/cast/rider pose samples, no warnings;4 body/
  head portrait renders inspected. Native compiled anim profiles retained01e.
  RPFM roundtrip/diagnostics passed; stats/cost/starting spell/prerequisite/CB
  checks passed. No game runtime test: recruitment refresh, full mount/crew fit,
  campaign overrides, spell VFX in-game remain unverified. No saves/native/
  Workshop/Git/public writes. Source pack hash unchanged verified after deploy.
  tools/Prepare-Moonveil-Adept-Models.py, Review-Moonveil-Adept-Models.py,
  Build-Moonveil-Adept-Pack.py, Deploy-Moonveil-Adept.py; docs/MOONVEIL-ADEPT-V24.md,
  src/campaign/moonveil-adept.json, build/moonveil-v24 reports and launcher backup.

- THREE CASTER ASTROMANCER SUPPORT ADDED (2026-11-22 local): user approved
  seven native support skills for all3 regular casters, keeping all existing
  skills and skill points/level; omit Heavens-only cooldown. Deployed/enabled
  mc_moonshadow_heroes_v23_caster_support.pack, SHA256
  9224432b00ed01da007512bf24f28ada3371b1cb5d4270787196ef2607727e4e.
  v22 retained disabled. All v22 payloads byte-identical; additive tables only.
  Each caster tree41->48 nodes. Shared private NAME aliases: Attuned to the Moon,
  Martial Discipline, Counsel of the Moon, Lunar Conduit, Moonlit Warding,
  Moonbound Beasts, Mastery of the Moon. Native Astromancer effects/scopes/values,
  icons and rank gates exact; descriptions ASCII punctuation only. No new
  ability/effect/phase/VFX. 21nodes+21memberships,12links,18locks. Row3 Warding/
  Bonds/Mastery is native1-of-3 exclusive, level13. Attuned level11. Omitting
  Weavings leaves Martial/Counsel as both required subset parents for Conduit;
  native threshold2 and initial Attuned prerequisite retained, same point cost.
  Existing spell lines/campaign actions/innates/points/capacity/buildings/CB
  spell presets/models/animations/lords/heroes unchanged. Verified free node
  positions, reachable capstone and exact source data; RPFM roundtrip and zero
  blocking diagnostics. No game launch/runtime test/save edit/public/Git write.
  tools/Build-Moon-Caster-Astromancer-Support.py,
  Deploy-Moon-Caster-Astromancer-Support.py; docs/MOON-CASTER-SUPPORT-V23.md;
  src/campaign/moon-casters.json updated. build/moon-casters-v23-astromancer-
  support contains validation/deployment reports and launcher backup.

- ORDINARY GENERAL NATIVE SKILLS (2026-11-22 local): user requires only existing
  game skills, six special nodes like CG; Bastion rename-only, Assault replace
  Bulwark with native offensive skill. Deployed/enabled combined v22
  mc_moonshadow_heroes_v22_native_general_skills.pack, SHA256
  9770b6e5e89cfa4dd3f1983d2379a83e8b75feabcfeb1717270a60571e086f48.
  v21 retained disabled. Each lord has6 private NAME aliases of native skills,
  no new ability/phase/effect/icon/VFX/mechanics. Bastion donorCG unique1-6 exact;
  Assault donorunique2 replaced by wh_main_skill_all_all_self_deadly_onslaught.
  Names: Lunar Command, Moonlit Bulwark (Assault Moonlit Onslaught), Might of the
  Moon, Moonfall Charge, Lunar Impact, Unyielding Advance. Native icons, effects,
  rank details and criteria copied exactly. Stable node keys/count/positions/
  prerequisites retained.12 mutually exclusive lock rows mapped to aliases:
  Bulwark(or Onslaught)/Hammer/Comet still one choice, not all three together.
  Native Deadly Onslaught effect-gated on Assault foot/horse/stag. CB correction:
  native CG level1/empty skillset replaces prior over-granted all-yellow/all-six
  preset on these2 characters. Old unused preset rows inert, unrelated payloads
  preserved. Only3 existing payloads changed: own nodes, locks and CB characters.
  All5 mounts/appearances/stats/animations/other heroes/Lua unchanged. RPFM
  roundtrip/diagnostics and exact donor equality checks passed. No game runtime
  test/save migration; old recruited lords may retain prior skill investments,
  use new recruits/campaign for clean test. No save/native/Workshop/Git writes.
  tools/Build-Moon-General-Native-Skills.py, Deploy-Moon-General-Native-Skills.py;
  docs/MOON-GENERALS-NATIVE-SKILLS-V22.md; build/moon-generals-v22-native-skills
  reports, hash and launcher backup. This supersedes earlier skill proposals.

- MOUNT BRANCHES RESTORED (2026-11-22 local): user explicitly requested mounts
  restored for both generals. Deployed/enabled combined v21 mc_moonshadow_heroes_
  v21_general_mounts.pack, SHA256 52f5d8a84b392074c6f135233aaea386a1c52a5f1dbc78b02d1b903ccd246aa2.
  v20 retained disabled. Every v20 internal payload unchanged. Assault White
  Warhorse + Great Stag (original donor mounts, native01b rider profiles),
  Bastion Warhorse + Jade Longma + Celestial Lion (native CG mount profiles).
  Five private mount skills/ancillaries/units, subtype permissions, automatic
  level criteria4/14 and4/9/15, campaign rider overrides and CB selectors. Source
  WWD Bastion Longma/Lion campaign overrides were swapped; use correct native
  CG mappings instead. Assault mounted weapon slot be_prop_1; foot remains
  be_prop_0. Approved exported bodies/colours/weapons reused. Four source LODs
  for both custom mount bodies, namespaced WS/material/DDS; every LOD/part has
  material override. Creature/rider native compiled BIN keys and Cathay culture
  mappings verified. Native mounted stats/cost deltas; no Elf bow/firing/vanguard
  traits copied to Assault stag (CG mounted attrs + fear, melee AI). Five chain
  checks and45 rider-only animation samples passed; idle renders inspected.
  RPFM roundtrip/diagnostics passed, no blocking issues. Game NOT launched;
  existing-save refresh, full rider/mount clipping, flight transitions and
  campaign acquisition NOT runtime verified. No save/native/Workshop/Git writes.
  tools/Prepare-Moon-General-Mounts.py, Build-Moon-General-Mount-Pack.py,
  Review-Moon-General-Mount-Animations.py, Deploy-Moon-General-Mounts.py;
  docs/MOON-GENERALS-MOUNTS-V21.md, build/moon-generals-v21-mounts reports and
  launcher backup. Earlier foot-only statements below superseded.

- TWO GENERALS INTEGRATED AND DEPLOYED (2026-11-22 local): user approved
  adding reviewed models to mod. Active combined v20 mc_moonshadow_heroes_v20_
  two_generals.pack, SHA256 03a7f8819c51c1ff913b1b8e11b1f3359436bfe49fc7d262ba0fb8100fa9686f.
  v19 retained disabled; all v19 internal payloads byte-identical. Agents of the
  Moon now has regular Assault/Bastion lord recruitment, replacing its native CG
  Yin/Yang permissions only; both in Cathay Custom Battle LORDS. Assault native
  humanoid01b/hu1b_elf_2handed_spear, campaign cam_hu1b_bretonnian_staff_and_sword
  (same native profile as original WWD donor). Bastion native humanoid01e/CG,
  true vanilla hammer shaft + strike-axis-aligned guandao head. Exact latest
  connected-polearm static source retained. Approved black/white palette baked
  to DDS, human skin preserved. Four LODs each body/weapon; actual RMV/DDS
  reimported, 20 native battle/campaign clips x3 samples passed. Compiled native
  BIN lookups include all reviewed battle clips; explicit Cathay culture mapping.
  Native CG Yang/Yin skill trees cloned excluding3 mounts; foot only. Assault
  armour90/MA65/MD35/charge45; Bastion110/55/50/20; other core stats nativeCG.
  English ASCII names and private portraits/cards. RPFM roundtrip and diagnostics
  passed (only known metadata reference warning exempted); banned ownership
  tables NOT packaged, native DLC tables untouched. No donor model mod needed.
  tools/Export-Moon-General-Models.py, Review-Moon-General-Exports.py,
  Build-Moon-Generals-Pack.py, Deploy-Moon-Generals.py; docs/MOON-GENERALS-V20.md.
  build/moon-generals-v20 reports/deployment backup. Native/Workshop packs,
  saves and unrelated launcher entries unchanged. No game launch/runtime test,
  public upload or Git operation. Native Assault twirl hand-release preserved
  from user-approved review; no claim of perfect grip. Earlier not-exported /
  not-deployed preview entries below are historical, superseded by this entry.

- TWO-GENERAL ANIMATION REVIEW (2026-11-22 local): user requested animation
  test, then explicitly SELF-VIEW test playback. Opened and LEFT PLAYING native
  timeline build/moon-generals-preview/moon-generals-animation-review-v3.blend,
  Outliner + enlarged fitted timeline. 1-120Idle,121-240Walk,241-360Run,
  361-480Charge,481-685AttackA,686-766AttackB,767-871JumpAttack,872-918Defend.
  Space pauses/resumes; captions identify model/stage.16 original clips (8 per
  native rig), native hand grip applied; all constant pose channels and every
  bone baked (prevents residual poses/action-slot issues). Root animroot XY
  removed in ARMATURE pose space, not local basis axes (v1/v2 bad root-motion
  previews superseded). Locomotion loops120frames; shorter attack holds endpoint
  until other model finishes. Geometry/weapon frames unchanged.80 source pose
  samples finite, body deforms, importer warnings0, weapon-frame errors<1e-4.
  Rendered+inspected frames180walk/530attack/815jump; UI playback observed running
  (about16fps with frame drop). No T-pose freeze or separating weapon joints.
  IMPORTANT UNRESOLVED VISUAL: Assault AttackA has open/released hands during
  spear twirl; closest hand-axis midpoint distance up to.168m versus.077-.083
  elsewhere. Could be native choreography; not proven intentional, not corrected.
  Assault jump very acrobatic. Do not claim perfect grip/full runtime pass.
  Bastion sampled nearest-hand distances .038-.064m; joints stay rigid.
  User wants to judge animation themselves, avoid overlong reports or changing
  native moves without further direction. Engine NOT tested/exported/deployed.
  Source static checkpoint remains moon-generals-assault-polearm-connected.blend.
  tools/Prepare-Moon-General-Animation-Review.py, Build-Moon-Generals-Animation-
  Review.py; animation-review-report.json, animation-review-clips.json and three
  animation-review-frame-*.png. No game/Workshop/save/Git changes.

- ASSAULT POLEARM JOINT FIX (2026-11-22 local): user observed three separated
  pieces. Saved live edits in aligned.blend first. Root cause model09 collar
  centred localY=-.04866 while shaft/blade axisY=.02338. Shifted collar +.07204Y
  and -.003X to overlap blade base; attached flag moved with collar. Original
  shaft/blade/pommel dimensions and attachment be_prop_0 unchanged. Joined four
  copied visible meshes into Assault | Connected model09 polearm; retained all
  originals hidden. Latest scene build/moon-generals-preview/moon-generals-assault-
  polearm-connected.blend opened, visibly continuous neck and saved. Bastion
  aligned blade/body/palettes and user mesh visibility preserved. tools/Fix-
  Assault-General-Polearm-Joints.py, assault-polearm-joint-fix.json; ignored
  assault-weapon-audit.json records original disconnected part bounds. No game
  integration, source pack edits or Git upload.

- BASTION BLADE ROLL FIX (2026-11-22 local): user said guandao was sideways
  relative to hammer strike direction. Undid cosmetic local X90 roll on blade
  ONLY (-90 correction). Wide cutting profile now local XY, normal Z; width/edge
  aligned with native hammer opposed Y impact caps. Blade extentY >5*extentZ;
  shaft vertex equality and weapon_1 unchanged verified. Authoritative trial
  build/moon-generals-preview/moon-generals-bastion-guandao-aligned.blend opened
  and saved with three-quarter view. Front view sees blade edge-on by design.
  tools/Align-Bastion-Guandao-To-Hammer.py and guandao-alignment.json. Prior
  hybrid preview had incorrect roll; no body/material/rig/game changes.

- BASTION HYBRID WEAPON PREVIEW (2026-11-22 local): user requested retaining
  native CG hammer SHAFT, replacing only golden head with guandao head. Opened
  build/moon-generals-preview/moon-generals-bastion-hammer-shaft-guandao.blend.
  Native head disconnected components split into hidden OPTION object; original
  full hammer also hidden. Visible original shaft vertices/UV unchanged. Copied
  only416 blade vertices from guandao spear_to (excluded donor pommel/shaft),
  untransformed to donor local then Tx(-.80) Rx90, native weapon_1 attachment.
  Original collar/cube grip and shaft retained. Body/palette/rig/Assault untouched.
  Render inspected and UI opened. tools/Build-Bastion-Hammer-Shaft-Guandao.py,
  hammer-shaft-guandao.json/.log and same-name PNG. Appearance review only, no
  mod/DB/Workshop/game/save changes; prior previews retained.

- BASTION NATIVE HAMMER TRIAL (2026-11-22 local): user rejected guandao and
  asked to preview DEFAULT Celestial General hammer. Opened and saved private
  build/moon-generals-preview/moon-generals-bastion-native-hammer.blend; guandao
  and shaft continuation retained hidden, corrected palette/skin/body/Assault
  untouched. Actual vanilla RMV+WS+3 textures extracted to separate ignored
  reference/local/vanilla-celestial-hammer from native game packs. IMPORTANT:
  same-path WWD hammer_2h_01 is an override with SIX assembled parts; native
  hammer_2h_01 has ONE mesh. Do not restore WWD fake hammer when user asks vanilla.
  Native hammer unchanged default gold/grey texture, direct weapon_1 attachment,
  native original proportions, no custom offset. tools/Preview-Bastion-Native-
  Hammer.py, native-hammer-preview.json. Appearance trial only, not approval for
  final weapon selection; no mod/DB/game/save/Git changes.

- BASTION PALETTE CORRECTION (2026-11-22 local): user rejected globally grey
  skin and requested model08-style BLACK plate borders / WHITE scale fields.
  Saved live edits before snapshot before-palette-fix.blend. Authoritative preview
  NOW build/moon-generals-preview/moon-generals-skin-and-armour-v3.blend.
  Face restores ORIGINAL shared guard-head texture only within its two face UV
  islands; hands restore original source colour based on hand/finger weights,
  excluding cuffs. Existing gloves remain gloves. Reuses model08 compatible white
  Celestial Guard and Alchemist atlases, WWD General iron_white compatible atlas,
  and explicit original Yuan Bo body UV scale-field masks (white inside, dark
  borders). Source DDS unchanged; materials copied, no mesh/rig/weapon/visibility
  change, Assault unchanged. Render inspected: skin warm, white scale fields,
  black surrounds. tools/Fix-Bastion-General-Palette.py, palette-fix.json and
  moon-generals-skin-and-armour-v3.png. Shader-only private preview; not deployed.
  Prior final.blend and source checkpoint retained. Corrects prior blanket
  charcoal/ivory and head hue-mask approach; never globally desaturate skin.

- TWO REGULAR LORD TYPES selected (2026-11-22 local), APPEARANCE PREVIEW ONLY:
  Assault General = user's CURRENT edited WWD gallery08 Guan Zimo body + gallery09
  Yi Qing long polearm, native humanoid01b/cth_hu1b_elf_2handed_spear retained.
  Model09 offhand sword kept hidden as an option; native two-handed anim requires
  the other hand on the shaft. Bastion General = CURRENT gallery01 Yi Shao body,
  native humanoid01e/Celestial General animation, WWD Guan Yu guandao replacing
  hammer, private charcoal/ivory-steel shader palette. Original hidden pieces and
  weapons retained, all source DDS/body geometry untouched. Shaft continuation
  bridges an existing donor guandao pommel gap. User-edited gallery CtrlS saved
  BEFORE copying exact build/moon-generals-preview/user-edited-gallery-source.blend.
  Authoritative editable preview: build/moon-generals-preview/moon-generals-final.blend,
  checkpoint.json; Outliner open for individual part toggles. Six sampled attack
  poses (3 per native clip) finite and deforming, importer warnings empty; no
  engine/LOD/export/DB integration yet. Original idle reimported after attack tests
  to restore constant pose channels (merely reassigning action left attack pose).
  src/campaign/moon-generals.json records roles/names and planned CG skill base;
  stats/personal branches/recruitment remain pending. Active game pack remains
  v19 unchanged. tools/Build-Moon-Generals-Preview.py and
  Refine-Moon-Generals-Preview.py; supporting ignored scripts in preview directory.
  No Workshop/game/save modification or Git upload. Do not deploy preview shaders
  directly: bake private base-colour textures and export/check LODs first.

- DEPLOYED Ordnance Master Hero CATEGORY FIX v19 (2026-11-22 local): user
  observed engineer under Lords. Root: original main_units.ui_unit_group_land
  wh3_dlc24_cth_cha_celestial_general has parent_group=commander, despite caste=hero
  and general_unit=false. Prior validation missed the UI hierarchy. MUST verify
  all3 controls for hero categorization, not just caste/permission flags.
  Exactly ui_unit_group_land changed to native emp_engineer (heroes_agents parent)
  in all5 engineer unit rows; every other payload/field identical to v18. Hero
  remains ordinary repeatable, campaign/stats/skills/models/mounts unchanged.
  Active mc_moonshadow_heroes_v19_hero_category.pack SHA
  2ee1d5ce81a64ab5979ab0b4d3201492e346d3f3d034d99a0a945401076bed33;
  v18 retained disabled, original engineer/portrait Workshop mods still off.
  Regression checks all5 variants caste=hero, general_unit=false and referenced
  UI group parent=heroes_agents; roundtrip passed, zero blocking diagnostics.
  Launcher backed up, unrelated entries/active hashes preserved. No game launch/
  save/native/Workshop edits/Git upload. UI/engine NOT verified. Restart, inspect
  Grand Cathay > Heroes > Ordnance Master. docs/ORDNANCE-MASTER-HERO-CATEGORY-V19.md,
  tools/Fix-Ordnance-Master-Hero-Category.py, Deploy-Ordnance-Master-Hero-Fix.py;
  build/ordnance-master-v19-hero-category reports. Supersedes v18 active and prior
  inaccurate statements that its Lord/Hero UI categorization had been verified.

- DEPLOYED Ordnance Master rename + Custom Battle v18 (2026-11-22 local): user
  requested hero display name Ordnance Master, then enable in Custom Battle.
  Active mc_moonshadow_heroes_v18_ordnance_master.pack SHA
  7efa84399e3014fefdd77769bac8ec979d8c37e00550b4ceea42fe778502af2a;
  v17 retained disabled. Both original engineer/portrait Workshop mods still off.
  All5 unit names, subtype labels and engineer effect descriptions use English
  Ordnance Master; stable Luke_cth_master_engineer subtype/unit keys retained.
  Added explicit mc_ordnance_master_cb_character, male wizard-category non-caster,
  own English zero-frequency name, art354212573, CB level40, preset4 existing
  source-tree options: engineer_rocket, Ballistics Calibration, Flash Bomb,
  wh2_dlc11_skill_cst_gunnery_wight_support_2. Five CB permissions remain Hero
  entries under Grand Cathay; set-piece and proper foot/horse/Gyrobomber uniforms
  now explicit. Four original mount links unchanged. Ability availability per
  mounted unit remains source-defined. No campaign XP/skills/stats/recruitment/
  capacity/model changes. Ordinary repeatable hero retained, other heroes/Tide
  healing fix unchanged. Roundtrip and CB/name/mount checks pass, zero blocking
  diagnostics. Launcher backed up, other entries/hashes preserved. No gameplay
  launch/native/Workshop/save edits/Git upload. UI/runtime UNVERIFIED.
  docs/ORDNANCE-MASTER-V18.md; tools/Build-Ordnance-Master-Custom-Battle.py,
  Deploy-Ordnance-Master-Custom-Battle.py; build/moon-heroes-v18-ordnance-master
  reports authoritative. Restart, Grand Cathay > Heroes > Ordnance Master.
  Supersedes v17 active pack and Master Engineer display name below.

- DEPLOYED STANDALONE Master Engineer integration v17 (2026-11-22 local): user
  requested original Cathay engineer in Agents of the Moon, then explicitly ONLY
  current pack enabled (no original/submod runtime dependency). Active
  mc_moonshadow_heroes_v17_master_engineer.pack SHA
  199413834a0e024b7bcf580dc3ca565689e1d38ab6a823a8ba438972fd599c00.
  V16 retained disabled. Both original Luke_cth_master_engineer.pack (2815205063)
  and portrait !Luke_cth_master_engineer.pack (3782216577) disabled in launcher.
  Required hero DB/model/UI assets embedded privately in ignored build. Workshop
  source hash f63f7488dca880768851400e7be2c23715757f92b01370c8147064679e6f1c4f
  unchanged; no Workshop/native/save modifications/public redistribution/Git push.
  Master Engineer subtype Luke_cth_master_engineer, ordinary repeatable hero,
  auto_generate/recruitable=true, subtype cap=-1, five main unit campaign caps=-1.
  Faction permission ONLY cr_cth_agents_of_the_moon, original wizard category.
  Existing gunners1/2/3 Forge enables hero, adds1/2/3 SHARED wizard capacity as
  donor does; owner context limits Forge additions to Agents of the Moon. Not
  a separate independent engineer pool. Original stats/costs/weapons/skill effects/
  ability definitions/four mount criteria retained. Foot/Sky Lantern/Sky Junk/
  Warhorse/Gyrobomber; original Grand Cathay CB entries retained.
  All new text English ASCII. Original PNGs reused for missing cards/minspec,
  invalid portrait mask path0 fixed, material namespace isolates native peasant
  head overwrite. Omitted5 unrelated native Astromancer art overrides and3 global
  native tech effect additions; no invented hero skill/balance redesign.
  ALL v16 payloads byte-identical incl Tidecaller heal fix/Da Anh/movement Lua.
  Roundtrip and independent recruitment/stat equality checks passed, zero blocking
  diagnostics. Launcher backed up, unrelated entries/active hashes preserved.
  Engine NOT tested; no gameplay launch. Existing saves may need recruit pool
  refresh. Existing IEE/MIXER/project dependencies remain; only engineer donor/
  portrait runtime requirements eliminated. docs/MASTER-ENGINEER-INTEGRATION-V17.md,
  src/campaign/master-engineer.json; tools/Integrate-Cathay-Master-Engineer.py,
  Deploy-Integrated-Master-Engineer.py; build/moon-heroes-v17-engineer reports.
  This supersedes v16 as current active pack and earlier dependency-patch proposal.

- DEPLOYED Tidecaller healing selection FIX v16 (2026-11-22 local): user
  reported missing healing spells in Custom Battle. V15 CB selected Deep group
  only while Earth Blood/Regrowth lived in separate Life page1. Prior validator
  wrongly accepted union of owned groups instead of actual CB-selected group.
  New mc_tidecaller_lore_combined composite UI group (native Teclis pattern),
  single assigned page0, includes6spells+Life Bloom; companion upgraded group6.
  Actual CB magic_lore now points to combined group. Original Deep/Life private
  groups/member lists/modifier bindings retained for native lore-specific effects.
  Native Deep icon unchanged, no image/VFX/ability definition/skill/stat/model/
  recruitment/AP Lua changes. Other heroes and Da Anh unchanged.
  Active mc_moonshadow_heroes_v16_tidecaller_healing.pack SHA
  594a980327a20e439692106d71116b8f8313f8bcd5744aa30e046df881eba6ce;
  v15 retained disabled (this postdates20-old-pack cleanup below). Launcher
  backed up, active hashes/unrelated entries preserved. Regression checks require
  both heals in actual CB-selected group + matching preset skills + level1
  enable effects. Roundtrip passed, zero blocking diagnostics. Game/UI runtime
  UNVERIFIED; no game launch/native/Workshop/save edits/Git push. Restart and
  re-add fresh Tidecaller to CB army; saved army preset may retain old selections.
  docs/TIDECALLER-HEALING-SELECTION-V16.md; tools/Fix-Tidecaller-Healing-Selection.py,
  Deploy-Tidecaller-Healing-Fix.py; build/tidecaller-v16-healing-selection reports.
  Supersedes v15 as active pack and two-visible-group configuration below.

- OLD INSTALLED PACK CLEANUP (2026-11-22 local), explicitly requested by user:
  sent20 INACTIVE previous handmade packs in game/data to Windows Recycle Bin
  via FileIO SendToRecycleBin (no permanent fallback), total2.620769 GiB. Removed
  corresponding20 inactive launcher entries after backup; all active entries and
  active pack hashes preserved. Kept active Moonshadow v15, Huyen Ve r7+r8 and
  both active EDH packs. Project source/build archives/Blender files, Workshop,
  native packs and saves untouched. Historical installed fallback paths v5-v14
  Moonshadow, r5/r6 Huyen Ve and old EDH versions are now absent; restore from
  Recycle Bin or use retained build outputs when needed. Reports, exact original
  paths/hashes and launcher backup: build/cleanup-old-mods-20261122/.
  tools/Recycle-Old-Installed-Mods.ps1 used the prevalidated exact20-file inventory.
  Earlier retained-installed rollback notes below are superseded for these files.

- USER CLARIFICATION (2026-11-22 local): Pyromancer, Tidecaller and Astral Weaver
  are REGULAR recruitable heroes, many copies per subtype, not legendary/unique.
  Verified deployed v15 decoded DB: auto_generate/recruitable=true, subtype cap=-1,
  main_units campaign_cap=-1, contributes_to_agent_cap=true. Shared native wizard
  capacity and ordinary recruitment pool still apply. No pack change needed.
  Preserve this classification in future edits; Da Anh remains the separate LH.

- DEPLOYED native caster spells v15 (2026-11-22 local): user approved revised
  proposal using EXISTING spells/skills ONLY, renamed English, NO icon/VFX edits.
  Active mc_moonshadow_heroes_v15_caster_spells.pack; v14 retained disabled.
  SHA f760fa5fc705efaa12c945805a4076e5e8f2bb5cd4d4ee717ba2c79d44868648.
  Pyromancer=full Fire +Kindleflame; Tidecaller=Spiteful Shot, Tidecall, Fog of
  the Damned, Kraken's Pull, Earth Blood, Regrowth +Life Bloom; Astral Weaver=
  full Yin +Power of Yin. Approved English names in src/campaign/moon-caster-
  spells.json; private skills/abilities/effects/groups preserve vanilla labels.
  Each magic row11 visible nodes (6spells+passive+Evasion/Earthing/Reserves/Conduit)
  and one hidden starter, native graph/requirements and skill rank effects.
  New recruits: Fireball / Blessing of the Tides / Veil of the Moon starter.
  Native active definitions mechanically identical except IDs/link remapping;
  native icons, VFX, projectiles, phases, costs, cooldowns, overcasts untouched.
  No icon/VFX/model/animation payload added or changed. Native effect/group
  mappings extended to private copies; Tide separates Deep/Life native groups
  (original icons) to preserve source-lore modifiers. Life healing VFX stays green.
  Custom Battle Grand Cathay > Heroes level40 spell presets for all3 casters;
  Da Anh preset unchanged. All models/stats/recruitment/capacity/general nodes/
  existing skills/AP Lua preserved. No fabricated three-skill personal branches.
  Roundtrip, native mechanics/rank equivalence and independent starter/title/
  ownership/CB preset checks passed; zero blocking RPFM diagnostics. Launcher
  backed up; unrelated entries and previous pack hashes unchanged. No saves/
  native/Workshop edits, game launch or Git upload. Engine UNVERIFIED; existing
  save free-starter migration unverified, freshly recruited heroes baseline.
  docs/MOON-CASTER-SPELLS-V15.md; tools/Build-Moon-Caster-Spells.py,
  Validate-Moon-Caster-Spells.py, Deploy-Moon-Caster-Spells.py; reports under
  build/moon-casters-v15-spells. Supersedes v14 active and spells-pending notes.

- DEPLOYED four heroes Custom Battle v14 (2026-11-22 local): user explicitly
  requested all three casters, then also Da Anh, for convenient Custom Battle tests.
  Active mc_moonshadow_heroes_v14_custom_battle.pack; v13 retained disabled.
  SHA 4eead338f8daab6f76f5dab468b71d17a03f7806267ab59f05fe94d1d40a5ce6.
  Grand Cathay > Heroes (native wh3_main_cth_cathay_mp, same CB faction as Huyen Ve
  and Da Lien), not a new playable Agents of the Moon frontend faction. Four hero
  entries (general_unit=false): Pyromancer, Astral Weaver, Tidecaller, Da Anh.
  Own portrait/uniform/art/subtype and English names, Cathay military grouping.
  Da Anh CB level40 preset: mc_da_anh_veil, mc_da_anh_execution (Moonlit Prey),
  mc_da_anh_last_shadow. Casters still NO lore or starting spell, pending user's
  explicit decision to design spell trees later. No campaign XP/points/skills.
  All v13 payloads byte-identical; new CB tables/names/loc only. Roundtrip passed,
  zero blocking diagnostics. Launcher backed up, unrelated entries unchanged.
  No native/Workshop/save edits, game launch or Git upload. UI/engine UNVERIFIED.
  docs/MOON-HEROES-CUSTOM-BATTLE-V14.md, tools/Build-Moon-Heroes-Custom-Battle.py,
  Deploy-Moon-Heroes-Custom-Battle.py; build/moon-heroes-v14-custom-battle reports.
  Supersedes v13 below as latest active pack and its absence from Custom Battle.

- DEPLOYED three-caster MODEL/RECRUITMENT preview v13 (2026-11-22 local): user
  chose Hakutaku Diviners three models and native Astromancer building recruitment.
  Explicit async answer 2: decide spell lists LATER, do models/recruitment first.
  Model1=Pyromancer (charcoal/red), model2=Astral Weaver (charcoal/silver garment),
  model3=Tidecaller (dark blue garment). ALL new UI text English ASCII.
  Active mc_moonshadow_heroes_v13_three_casters.pack; v12 retained disabled.
  SHA 841d7c91ccab5c97442d9538189e8f4db6a6ec4449c9f8debaf35cd3c31842ea.
  Three new wizard subtypes mc_pyromancer, mc_astral_weaver, mc_tidecaller,
  faction cr_cth_agents_of_the_moon ONLY, at native magic_tower_1/_2/_3. Share
  existing wizard/Astromancer capacity; ZERO extra capacity effects. Native foot
  Astromancer costs/stats, female names/art/VO, general actions/support tree.
  NO lore/starting spell assigned, no mounts or Astromancer-specific magic/unique/
  army branches. Spell design intentionally deferred, not a complete spell roster.
  Namespaced self-contained WSModel/material/texture/VMDs, actual rendered cards.
  Source Workshop3270368516 @mustdy_sarv_hakutaku_diviner.pack read-only hash
  13db2dc05aa189820c26a058ad79c8351184e71bce8f572eecb548ae2e849f5d.
  Geometry bytes unchanged, native humanoid01e 96 bones, original four LODs
  (27/26/24 parts respectively), shader bakes for moon garment and darker blue.
  Native hu1e_mage_storm_dragon + cam_hu1e_mage_storm_dragon lookup; compiled
  battle BIN verified. 63 pose samples (7 clips x3frames x3models), packed editable
  assets/working/moon-casters/moon-casters-models.blend and checkpoint.json.
  All existing v12 payloads byte-identical including Da Anh/Moonshadow models,
  skills and turn1 AP Lua. Roundtrip passed, zero blocking RPFM diagnostics.
  Launcher backed up, unrelated entries unchanged. No saves/native/Workshop edits,
  gameplay launch or Git upload. Engine recruitment/capacity/animation UNVERIFIED.
  docs/MOON-CASTERS-V13.md; src/campaign/moon-casters.json; tools/Prepare-Moon-
  Caster-Models.py, Review-Moon-Caster-Models.py, Build-Moon-Casters-Pack.py,
  Deploy-Moon-Casters.py; build/moon-casters-v13 reports authoritative.
  This supersedes v12 below as latest active roster pack.

- DEPLOYED moon skills v12 (2026-11-22 local): user approved Da Anh signature
  skills and faction-themed English names; explicitly NO Vietnamese game names.
  Active mc_moonshadow_heroes_v12_moon_skills.pack; v11 retained disabled.
  SHA ec666bfa8561a7b8e3b7ead6159e1d68fe8004c6923c2f8dea865a87ada9d24f.
  27 visible native/shared skills cloned as private mc_moon_skill_* keys with
  English ASCII names/descriptions; original nodes preserved, effect/rank copies
  exact, poison locks remapped. No global vanilla localization overrides.
  Da Anh Silent Execution key mc_da_anh_execution now Moonlit Prey, level12:
  enemy lord/hero within100m, -15MD, speed x0.8, 20s, 90s cooldown.
  New The Last Shadow level20 requires Prey: self melee base/AP x1.5, -15MD,
  10s, 120s cooldown. Both skill-unlocked, zero WoM, unlimited uses with cooldown.
  Veil6/Supply8 unchanged; personal row Veil, Supply, Prey, Last Shadow.
  All non-skill/ability/loc payloads byte-identical to v11, including movement
  Lua, unit stats, approved graphics, recruitment/spawn. Roundtrip passed, zero
  blocking RPFM diagnostics. Launcher backed up, unrelated entries unchanged.
  No saves/native/Workshop edits, game launch or Git upload. Engine and old-save
  learned-skill migration UNVERIFIED (shared skills now new keys; use fresh game
  as baseline, inspect learned ranks/reset via in-game UI if needed).
  docs/MOONSHADOW-MOON-SKILLS-V12.md; tools/Build-Moonshadow-Moon-Skills.py,
  Deploy-Moonshadow-Moon-Skills.py; build/moonshadow-v12-moon-skills reports.
  This supersedes v11 as latest active pack and old skill-comparison facts below.

- DEPLOYED APPROVED Da Anh dagger/handbow v11 (2026-11-21): user accepted corrected
  nỏ fitting and explicitly requested mod update. Enabled
  mc_moonshadow_heroes_v11_da_anh_handbow.pack; v10 retained disabled. SHA
  7ed15a7ea89b7cfab44c0096709a7887a872953d4973a985177ff1c9572b40cb.
  Authoritative source assets/working/da-anh/da-anh-dagger-handbow-approved.blend
  (96-bone 01e editable preview); checkpoint.json current. Runtime is NOW native
  83-bone humanoid01d, same as Moonshadow Assassin, with native sword/handbow battle
  + campaign lookup keys. Inverse-skinned approved posed surface/normals into true
  native bind with native grip overlay; static knife/handbow offsets preserve
  corrected approved world grips via be_prop_1/be_prop_5 VMD slots. No custom lookup.
  Three RMVs, four LODs, self-contained textures, new cards and portraits. Restored
  Da Anh handbow/50ammo/ranged class/skirmish/missile value; combat stats/skills/
  spawn/recruitment unchanged. V10 turn1 AP fix Lua byte-identical; ALL Moonshadow
  and skill/loc payloads unchanged. Actual exported models reimported and checked
  in30 pose samples (8battle+2campaign clips); zero blocking pack diagnostics.
  Native/Workshop/saves untouched, launcher backed up, no Git upload/game launch.
  Runtime/projectile muzzle alignment/old-save caching/clipping remain UNVERIFIED.
  docs/DA-ANH-V11-DAGGER-HANDBOW.md and build/da-anh-v11-dagger-handbow reports.
  This supersedes earlier trial NOT-deployed and v10 active statements below.


- CURRENT Da Anh handbow grip trial FIX (2026-11-21), NOT deployed: user requested
  trying Moonshadow Assassin weapons/animations on Da Anh, then correcting nỏ.
  Authoritative trial: build/da-anh-moonshadow-animation-trial/
  da-anh-moonshadow-handbow-native-grip-fixed.blend. Script
  tools/Fix-Da-Anh-Native-Handbow-Grip.py. Original native Khainite handbow replaces
  the exported donor bow that carried an inherited bad offset. Native 01d standing
  prop + grip overlay hand frames, target 01e rest-axis/palm compensation; copied
  existing bow material retains textures. Old bow retained hidden; body and right
  knife unchanged. Eleven attachment frame checks passed, close front/side renders
  inspected: bow-native-grip-after-*.png. Timeline explicitly restored to 1..442
  after importing grip pose. Opened latest Blender window id330832, paused aim370.
  Earlier guessed-handle intermediate da-anh-moonshadow-handbow-grip-fixed.blend
  was rejected (hand in loop/void); DO NOT use it. Report handbow-native-grip-fix.json.
  Original trial window id5177590 retains unsaved user view changes. No deployment.

- Prior Da Anh retarget trial: tools/Try-Da-Anh-Moonshadow-Animations.py and
  build/da-anh-moonshadow-animation-trial/da-anh-moonshadow-dagger-handbow-trial.blend.
  Eight native Moonshadow 01d sword/handbow clips retargeted onto approved Da Anh
  01e 96-bone rig with rest-axis rotation correction and finger grip overlay;
  24 finite/moving sampled poses. Dao + nỏ tay, left knife hidden. Native unmatched
  cloth/hair may clip. Blender playback and aiming observed; no engine claims.
  User has NOT adopted this trial into the mod; v10 below remains sword/shield.

- DEPLOYED Da Anh turn-one movement fix v10 (2026-11-21): user clarified normal
  AVAILABLE MOVEMENT/AP at spawn, NOT max Increase Mobility skill. Mistaken v9
  max-skill build was briefly enabled, then immediately disabled; no saves/game
  launch. V10 derives directly from v8, all DB/loc/model/UI payloads byte-identical.
  Exactly mc_moonshadow_start.lua changes: enable movement + replenish normal AP
  once after spawn; existing turn-1 independent unwounded zero-AP Da Anh repaired
  once. Saved per-CQI marker prevents reload/retry grants. No later-turn refill,
  embedded-army refill, XP/free points/skill/range bonus. Original new-game-only
  spawn/duplicate guards preserved. 23 Lua boundary scenarios passed; zero blocking
  pack diagnostics. Enabled mc_moonshadow_heroes_v10_starting_movement.pack,
  SHA b8a6ee8424e56f407b1ae20e17965cc5bd9a55123ffde92247708485cddbadb4.
  v8/v9 retained disabled, unrelated entries and previous packs unchanged. Runtime
  NOT verified. docs/DA-ANH-STARTING-MOVEMENT.md and build/da-anh-v10-starting-movement
  reports authoritative. Restart/reload turn1 save to test. No Git upload.

- Skill comparison verified from v10: Da Anh has 28 visible skills, generic
  Moonshadow Assassin 27; 25 shared visible. Same melee, poison, ranged, campaign
  action and support skills. Da Anh personal row Moonshadow Veil (display rank6),
  Sever the Supply Lines (rank8, action cost -15%, success +10 percentage points),
  Silent Execution (rank12). Execution effects IDENTICAL to generic Assassin's
  Trophy, renamed/repositioned rather than a new effect. Generic has Immortality
  rank20; Da Anh immortal at spawn. Ranged skills remain on melee Da Anh and were
  flagged to user; no skill-tree redesign authorized. Comparison artifact:
  build/da-anh-skill-comparison/comparison.txt; tools/Compare-Moonshadow-Skill-Trees.py.

- DEPLOYED Da Anh Legendary Hero appearance v8 (2026-11-21), superseded by v10:
  approved Celestial Concubines body01/head01; black fitted torso/arm/leg fabric;
  original charcoal outer cloth across chest; gold ornaments/shoulder dragons
  hidden, plain shoulder plates retained; structural footwear charcoal. Two Death
  Squad knives corrected to this model's finger/palm geometry. User explicitly
  chose sword/shield animation while retaining two knives. Self-contained editable
  assets/working/da-anh/da-anh-legendary-hero.blend and checkpoint.json. Native 96-bone
  humanoid01e, nine-part RMV with hand-weighted knives; four LODs 46296/23145/11570/5781.
  Battle hu1e_sword_and_shield; campaign cam_hero_hu1e_dlc24_gatemaster_sword_and_shield.
  Old bow/ammo/skirmish disabled for Da Anh melee configuration, combat stats,
  skills, spawn/recruitment unchanged. ALL Moonshadow appearances preserved. New
  cards/portraits/uniform/VMD. Reimported exported RMV checked in 18 battle +6
  campaign poses; zero blocking diagnostics. SHA v8:
  37f3aa7a52438aca2ff56e439feb073d76135890dd5f3ad168036222695a26e6.
  docs/DA-ANH-V8-APPEARANCE.md and build/da-anh-v8-appearance reports authoritative.
  No native/Workshop/save modifications, no game runtime test, no Git upload.

- Da Anh appearance authoring history (all separate files in
  build/celestial-concubines-dual-knives): corrected grips
  celestial-concubine-01-dual-knives-grip-fixed.blend; black-leggings; black-bodysuit;
  no-gold-ornaments (ornaments retained hidden, shoes recoloured); closed-chest-outfit
  intermediate then approved closed-chest-textured.blend. Source torso Iron_Body,
  outfit IronWarriors_01, two shoulder base islands keys2408/2600 retained. Source
  backup geometry and all rejected/hidden variants preserved. Relevant tools
  Fit-Concubine-01-Dual-Knives.py, Fix-Concubine-01-Knife-Grips.py,
  Add-Concubine-Black-Leggings.py, Extend-Concubine-Black-Bodysuit.py,
  Hide-Concubine-Gold-Ornaments.py, Close-Concubine-Chest-Outfit.py,
  Match-Concubine-Chest-Cloth.py. Native sword/shield comparison file:
  build/celestial-concubines-animation/celestial-concubines-animation-review.blend.

- DEPLOYED Moonshadow Assassin appearance v7 (2026-11-21), included unchanged in
  later v8/v10. mc_moonshadow_heroes_v7_appearance.pack SHA
  69da89bd4e3b462d3bf21b46b1d98bbe69269df59afe08a5e3c4d620d1e4643a.
  Four approved faces8/11/3/12, four LODs each, self-contained baked maps, native
  prop-bound knife/handbow, uniforms/VMDs/cards/portraits. Generic art original ID
  maps face8; other rows offer 11/3/12. Gameplay unchanged. Genuine83-bone native
  humanoid01d bind, inverse skinning preserves approved evaluated source surface;
  direct-rest conversion attempts rejected. Native hu1d_elf_sword_and_handbow and
  cam_hero_hu1d_elf_sword_and_handbow links avoid source-only T-pose lookup bug.
  96 sampled poses on reimported exported geometry passed; zero blocking pack
  diagnostics. Actual engine untested; finger/cloth clipping may remain.
  docs/MOONSHADOW-ASSASSIN-V7-INTEGRATION.md and build/moonshadow-v7-appearance reports.

- APPROVED editable Moonshadow final checkpoint (2026-11-21): user requested save
  final files and close Blender; all ten windows saved/closed then. Authoritative
  build/moonshadow-assassin-final/moonshadow-assassin-final.blend plus face08/11/03/12
  .blends; final-checkpoint.json hashes. Original editable rig is 96-bone 01e,
  unlike actual exported 83-bone 01d runtime above. Same model11 outfit, black hood,
  charcoal formerly-gold ornaments, original short lower robe. Rear cape, centre
  strip, red shoulder plates and patterned shoulder ribbons hidden; legs retained.
  Corrected Death Squad knife actual handle midpoint(.3226,0,0) aligned to palm;
  left Khainite handbow. Four faces preserve body; face03/12 upper bun/hairpin islands
  and face12 wide scarf omitted to fit hood. Hidden originals preserved.
  docs/MOONSHADOW-ASSASSIN-FOUR-FACES.md, build/moonshadow-assassin-four-faces reports.
  Earlier source assets/working/moonshadow-assassin/alchemist-11-working.blend remains
  pre-later-edits tracked portable backup, not the current final checkpoint.

- Sariwa campaign model v6 hotfix (2026-11-21): original v4 assets/config hashes
  valid, no active collision found; root cause of dwarf-like campaign model UNPROVEN.
  edh_east_sea_charter_sariwa_model_v6.pack adds native add_character_model_override
  for edh_sariwa only, art edh_sariwa_art; old-save first tick plus lifecycle events.
  No gameplay/respawn/save changes, v5 payloads preserved; v4 assets remain active.
  Status build/sariwa-campaign-appearance/deployment.json and
  docs/SARIWA-CAMPAIGN-APPEARANCE.md authoritative. Runtime unconfirmed.

- Donor previews inspected/opened (2026-11-21), no donor pack edits: Dragon Witch
  3820285833 (body/head/hair/eye/armour five parts, native01e, four identical-density
  LODs, halberd; preview-only longv_weapon texture typo mapped to hongye_weapon).
  Hakutaku continued3270368516 three models; DEER24 Miao2824431771 two RMVs assemble
  one appearance. DEER Miao Witch Elf two-knife trial uses native01b->01e retarget,
  saved build/deer-miao-witch-preview, not deployed. Night Assassin3810018142 pack
  contains no model, uses vanilla def_assassin + 01d sword/handbow; opened four
  native outfit combinations. Steam download had been paused; resumed authorized
  Workshop queue, confirmed completion. Original Xiao3107188023 @sarv_lord_judge.pack
  correctly opened build/xiao-original-preview/xiao-original-preview.blend. Earlier
  build/xiao-preview/sarvente-xiao-preview.blend is actually ENHI3317294488,
  misidentification acknowledged to user; correct continued Xiao is3271568934.

- Handoff note recovery: an encoding error while adding the latest handbow note
  truncated AGENTS.md. Restored the complete committed baseline below and rebuilt
  these recent handoff notes from verified reports/docs and session context, using
  explicit UTF-8 and atomic replacement. No model/script/pack was affected.


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
