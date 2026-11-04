import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'pack_validation.json';v=json.loads(p.read_text())
scope={'installed_game_version':'9.0.5','v1':v['runtime_v1'],'v2':{'enabled_mod_confirmed_in_game_log':True,'custom_battle_empire_lord_visible':True,'selected_lord_name':'Heinrich von Adlerhorst (Test)','army_card_portrait_correct':True,'lord_selected_in_army_setup':True},'combat_completed':False,'mounted_variants_tested':False,'campaign_tested':False,'handoff':'Game left in Skirmish vs A.I. Army Setup with Heinrich selected; press Start Battle to test.'}
v['runtime_verified']=True;v['runtime_verified_scope']='Basic custom-battle loading/model/movement on v1; corrected card and selection on v2. Same gameplay/model payloads.'
for path in v['payloads']:
    if path.endswith('.rigid_model_v2'):
        assert (R/'roundtrip_final'/path).read_bytes()==(R/'roundtrip'/path).read_bytes(),path
v['v2_model_bytes_match_runtime_tested_v1']=True
p.write_text(json.dumps(v,indent=2));(R/'runtime_report.json').write_text(json.dumps(scope,indent=2))
d=R/'deployment_report.json';report=json.loads(d.read_text());report.update(runtime_verified=True,runtime_scope=v['runtime_verified_scope']);d.write_text(json.dumps(report,indent=2))
print('READY: v2 enabled, corrected portrait verified; Heinrich selected in Empire custom battle')
