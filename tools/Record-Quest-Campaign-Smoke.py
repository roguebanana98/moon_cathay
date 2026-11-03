"""Record bounded native QA evidence without claiming a full playthrough."""
import hashlib,json,re,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
log=Path('F:/SteamLibrary/steamapps/common/Total War WARHAMMER III/script_log_031126_2050.txt')
raw=log.read_bytes();text=raw.decode('utf-8',errors='replace')
message='[mc_huyen_ve_quests] Six-chapter campaign controller initialised; state 2, chapter 1'
assert message in text
assert 'Visual-test Hero created near Long Vi' not in text
assert '[mc_da_lien_moonstone] Crimson Moonstone granted' not in text
errors=re.findall(r'SCRIPT ERROR.*?(?=\*{10,})',text,re.S)
assert not any(re.search(r'quest_(chain|state|rewards)\.lua',e) for e in errors)
target=O/'native-campaign-smoke-r3.log';shutil.copy2(log,target)
restored=json.loads((O/'campaign-smoke-session.json').read_text())
assert restored['status']=='restored' and restored['original_saves_verified']==69
report=dict(status='new_campaign_initialisation_smoke_passed',pack='mc_huyen_ve_v25_quest_chain_test_r3.pack',
 game_version='9.0.5',new_disposable_campaign=True,engine_campaign_script_name='main_warhammer',map='cr_combi_expanded',
 controller_initialised=True,state_version=2,chapter=1,visual_test_hero_auto_spawn_observed=False,
 native_log=str(target),native_log_sha256=hashlib.sha256(raw).hexdigest(),
 unrelated_native_script_error_blocks=len(errors),
 unrelated_error_notes='Missing native intro for minor faction; native narrative queries receive nil faction. No quest-chain stack in error blocks.',
 full_campaign_playthrough_verified=False,chapters_runtime_verified=[],
 remaining=['Real chapter-1 issuance at rank6/wins/reward','Rescue campaign teleport, win/loss/retry, reward/return',
 'Archive marker path/delivery and ransom/restoration UI','Kill accounting manual/autoresolve/scaling',
 'Save/load at each stage, wounded Hero return and balance'],
 original_saves_restored_and_hash_verified=69,intro_preference_restored=True,latest_test_pack_left_active=True)
(O/'runtime-campaign-smoke-r3.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name in ['AGENTS.md','PROJECT_GOALS.txt','docs/HUYEN-VE-V25-QUEST-INTEGRATION.md']:
 p=R/name;s=p.read_text(encoding='utf-8-sig')
 s=s.replace('R3 native campaign smoke in progress.','R3 native campaign initialisation smoke passed; no old visual spawn observed.')
 s=s.replace('Intro video\n  preference temporarily off.','All69 original save hashes and intro preference restored after exiting game.')
 s=s.replace('Đang thử khởi động campaign riêng; đã backup 69 save trước QA.','Campaign mới IEE đã khởi tạo controller đúng, không spawn Hero visual test; đã thoát game và khôi phục/đối chiếu hash đủ 69 save cùng intro preference.')
 s=s.replace('Smoke r3 đang kiểm tra.','Smoke r3 đã đạt: controller khởi tạo state 2/chương 1; không thấy auto-spawn Hero visual test. Đã thoát game và khôi phục đủ 69 save/hash cùng intro preference. Báo cáo: runtime-campaign-smoke-r3.json.')
 p.write_text(s,encoding='utf-8')
p=R/'src/campaign/huyen-ve-quests.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d['campaign_script_alias']='main_warhammer'
d['campaign_initialisation_smoke']={'verified':True,'game_version':'9.0.5','revision':'r3','report':'build/huyen-ve-v25-quest-chain/runtime-campaign-smoke-r3.json','full_playthrough_verified':False}
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=R/'src/campaign/huyen-ve-rescue-battle.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d['map_review']['replacement']='Native Amber Bow; map loaded, deployment/paths and normal victory verified in prototype v4. Escort-targeting balance in v25 remains unverified.'
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
