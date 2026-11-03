"""Synchronise current private quest integration handoff, preserving history."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8-sig')
a=s.index('## Current handoff');b=s.index('## User-authorized exceptions',a)
s=s[:a]+'''## Current handoff (2026-11-03)

- User requested integration of the entire six-chapter quest chain and continued
  work/testing. All six are implemented and privately deployed in v25 r3,
  mc_huyen_ve_v25_quest_chain_test_r3.pack. V24 remains intact/inactive fallback;
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
  R3 native campaign smoke in progress. Do not claim full campaign playthrough.
- Before campaign QA, all69 user saves copied/hashed. Current restoration status:
  build/huyen-ve-v25-quest-chain/campaign-smoke-session.json. Do not rerun Prepare
  while QA active; exit game then use Restore-Quest-Campaign-Smoke.py. Intro video
  preference temporarily off. User already approved launcher warning Play and
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

''' + s[b:];p.write_text(s,encoding='utf-8')
for name in ['README.md','docs/LEGENDARY-LORD.md','PROJECT_GOALS.txt']:
 p=R/name;s=p.read_text(encoding='utf-8-sig').replace('v25 r2','v25 r3').replace('v25 r2','v25 r3').replace('trong r2','trong r3').replace('56 kiểm tra','58 kiểm tra')
 if name=='PROJECT_GOALS.txt':
  s=s.replace('[ ] Triển khai nhận từng món qua chuỗi','[~] Đã triển khai đủ sáu chương nhận từng món qua chuỗi')
  s=s.replace('Bản test v17 có\n    auto-grant cả bộ; cần tách đường cấp đồ test khỏi bản progression.','Bản v25 chặn\n    auto-grant cả bộ và spawn Hero visual test bằng saved flag.')
  s=s.replace('Mốc 6 chương dự kiến 6/8/10/14/18/22, cần chốt khi triển khai; chỉ mở chương sau','Mốc 6 chương đã tích hợp 6/8/10/14/18/22; chỉ mở chương sau')
  s=s.replace('[ ] Chốt tọa độ campaign IEE, battlefield/catchment, deployment/entry, faction,\n    roster/unit keys/số lượng và timeline cho battle giải cứu sớm trước khi build.','[~] Đã tích hợp điểm đất hợp lệ quanh Long Vi qua API native, Amber Bow/catchment,\n    deployment/entry, faction, roster và timeline; còn kiểm chứng campaign runtime.')
  s=s.replace('(đứng yên vẫn thắng), chưa thử chết/thua/campaign return. Đã khôi phục v24.','(v4 đứng yên vẫn thắng); v25 đổi địch đánh hộ vệ, chờ thử chết/thua/campaign return.\n    Hiện bật đủ sáu chương v25 r3; v24 tắt làm fallback.')
 p.write_text(s,encoding='utf-8')
print('Updated current handoff, overview and goal; historical milestones retained.')
