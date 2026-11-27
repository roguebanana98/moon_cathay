"""Independent design assertions and optional finished-pack byte audit."""
import argparse,collections,csv,hashlib,json,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-v36-zhao-jade';M=json.loads((O/'design-manifest.json').read_text());P='mc_zhao_v36'
N=R/'reference/local/zhao-shugengan-comparison-20261126/native/db'
def read(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 assert all(len(r)==len(a[0]) for r in a),p
 return [dict(zip(a[0],r)) for r in a[2:]]
def t(name):return [r for p in M['db_paths'] if p.split('/')[1]==name+'_tables' for r in read(O/(p+'.tsv'))]
def native(name):return read(N/(name+'_tables/data__.tsv'))
nodes={r['key']:r for r in t('character_skill_nodes')};skills={r['key']:r for r in t('character_skills')};native_sk={r['key']:r for r in native('character_skills')}
assert len(nodes)==68 and sum(r['visible_in_ui']=='true' for r in nodes.values())==54
assert len(t('character_skill_node_set_items'))==68
assert all(r['character_skill_key'] in skills or r['character_skill_key'] in native_sk for r in nodes.values())
coords=[(r['indent'],r['tier']) for r in nodes.values() if r['visible_in_ui']=='true'];assert len(set(coords))==54
links=t('character_skill_node_links');assert all(r['parent_key'] in nodes and r['child_key'] in nodes for r in links)
visited=set();pending=set(nodes)
while pending:
 ready={k for k in pending if all(l['parent_key'] in visited for l in links if l['child_key']==k)}
 assert ready,'cycle';visited|=ready;pending-=ready
for k in ['evasion','conduit']:
 key=P+'_node_magic_'+k;parents=[r['parent_key'] for r in links if r['child_key']==key and r['link_type']=='SUBSET_REQUIRED']
 assert len(parents)==(3 if k=='evasion' else 5) and nodes[key]['required_num_parents']=='4'
 def maxpoints(node):
  sk=nodes[node]['character_skill_key'];return max([int(r['level']) for r in t('character_skill_level_to_effects_junctions')+native('character_skill_level_to_effects_junctions') if r['character_skill_key']==sk]+[1])
 assert sum(maxpoints(p) for p in parents)>=4
magic=[r for r in nodes.values() if r['indent']=='2' and r['visible_in_ui']=='true']
assert sum(2 if r['character_skill_key'].startswith(P+'_skill_') and r['character_skill_key']!=P+'_skill_passive' else 1 for r in magic)==17
locks=t('character_skill_nodes_skill_locks');assert len(locks)==12
bound={r['skill'] for r in M['bound']}
for a in bound:
 node=next(r['key'] for r in nodes.values() if r['character_skill_key']==a)
 assert {r['character_skill'] for r in locks if r['character_skill_node']==node}==bound-{a}
 assert skills[a]['unlocked_at_rank']=='9'
 assert {r['level'] for r in t('character_skill_level_to_effects_junctions') if r['character_skill_key']==a}=={'1'}
assert skills[P+'_unique_0']['unlocked_at_rank']=='12'
assert skills[P+'_wind_harmony']['unlocked_at_rank']==skills[P+'_ranged_discipline']['unlocked_at_rank']=='6'
assert {r['character_level'] for r in t('character_skills_to_level_reached_criterias')}=={'4','14'}
assert all(r['character_skill_key'] in bound or r['character_skill_key'].startswith(P) for r in t('character_skill_level_to_effects_junctions'))
amap=M['ability_map'];assert len(amap)==13
assert not any(word in k for k in amap for word in ['earth_blood','flame_storm','ancestral_warriors','kindleflame','life_bloom'])
ua={r['key']:r for r in native('unit_abilities')};usa={r['key']:r for r in native('unit_special_abilities')};actual_ua={r['key']:r for r in t('unit_abilities')};actual_usa={r['key']:r for r in t('unit_special_abilities')}
for old,new in amap.items():
 assert dict(actual_ua[new],key=old,overpower_option=ua[old]['overpower_option'])==ua[old]
 assert dict(actual_usa[new],key=old,unique_id=usa[old]['unique_id'],parent_ability=usa[old]['parent_ability'])==usa[old]
effects=t('character_skill_level_to_effects_junctions');bonus=t('effect_bonus_value_unit_ability_junctions')
cd=next(r for r in effects if r['character_skill_key']==P+'_unique_1' and r['effect_key']!= 'wh3_main_effect_spell_mastery')
cdtargets={r['unit_ability'] for r in bonus if r['effect']==cd['effect_key']}
assert len(cdtargets)==4 and all(any(x in old for x in ['storm_of_shadows','talons_of_night']) for old,new in amap.items() if new in cdtargets)
for i in [0,2,3,4,5]:
 actual=[dict(r,character_skill_key=M['skill_donors'][P+'_unique_'+str(i)]) for r in effects if r['character_skill_key']==P+'_unique_'+str(i)]
 expected=[r for r in native('character_skill_level_to_effects_junctions') if r['character_skill_key']==M['skill_donors'][P+'_unique_'+str(i)] and r['level']=='1'];assert actual==expected
foundation=[r for r in effects if r['character_skill_key']==M['foundation']]
assert len(foundation)==2
assert {r['unit_ability'] for r in bonus if r['effect'] in {x['effect_key'] for x in foundation}}=={s['ability'] for s in M['spells'] if s['slug'] in ['ember_bolt','lunar_snare']}
foot=next(r for r in M['land_units'] if r['key'].endswith('_human'))
assert [foot[k] for k in ['bonus_hit_points','armour','melee_attack','melee_defence','charge_bonus','morale','damage_mod_missile']]==['4160','wh2_main_leather_20','45','35','20','70','15']
assert t('battle_entities')[0]['run_speed']=='4.2000'
assert [t('melee_weapons')[0][k] for k in ['damage','ap_damage']]==['210','90']
assert all(r['man_entity']!=P+'_foot_entity' for r in M['land_units'] if not r['key'].endswith('_human'))
assert t('battle_set_piece_armies_characters')[0]['character_level']=='1'
assert not any('_unique_' in r['skill'] for r in t('battle_set_piece_armies_characters_skillsets_skills'))
report=dict(design_passed=True,visible_nodes=54,total_nodes=68,magic_points=17,private_native_spell_copies_exact=True,lunar_cooldown_targets=sorted(cdtargets),bound_one_of_four=True,starting_spells_exact=True,foot_stats_exact=True,mounts_keep_native_movement=True,runtime_verified=False)

def inventory(p):
 with Path(p).open('rb') as f:
  assert f.read(4)==b'PFH5';flags,dc,ds,fc,fs,stamp=struct.unpack('<6I',f.read(24));deps=f.read(ds);raw=f.read(fs);pos=0;entries=[]
  for _ in range(fc):
   size,comp=struct.unpack_from('<IB',raw,pos);pos+=5;assert comp==0;end=raw.index(0,pos);name=raw[pos:end].decode().replace('\\','/');pos=end+1;entries.append((name,size))
  assert pos==len(raw);result={}
  for name,size in entries:
   assert name not in result;digest=hashlib.sha256();left=size
   while left:
    data=f.read(min(left,8*1024*1024));assert data;digest.update(data);left-=len(data)
   result[name]=(size,digest.hexdigest())
  assert f.tell()==Path(p).stat().st_size
  return result,deps
if '--pack' in __import__('sys').argv:
 before,deps=inventory(M['base']);after,afterdeps=inventory(M['pack']);jade,_=inventory(M['jade']);review=json.loads((O/'asset-review.json').read_text());assert deps==afterdeps
 expected=set(M['db_paths'])|{M['loc_path']}|set(review['additional_files'])|{k for k in jade if not k.endswith('.rpfm_reserved')}
 changed=[p for p in before if before[p]!=after.get(p)];added=sorted(set(after)-set(before));assert set(changed)<=expected;assert set(added)<=expected
 assert all(after[p]==v for p,v in before.items() if p not in expected)
 for p,v in jade.items():
  if not p.endswith('.rpfm_reserved'):assert after[p]==v,p
 for p in review['additional_files']:
  with (O/p).open('rb') as f:expected_hash=hashlib.file_digest(f,'sha256').hexdigest()
  assert after[p]==((O/p).stat().st_size,expected_hash),p
 # Actual RPFM import/export equality checks, not merely successful CLI status.
 c=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));roundtrip=R/'reference/local/moon-v36-roundtrip'
 subprocess.run([c['rpfm'],'-g','warhammer_3','pack','extract','-p',M['pack'],'-t',c['schema'],'-F','db;'+str(roundtrip),'text;'+str(roundtrip)],check=True,stdout=subprocess.DEVNULL)
 for p in M['db_paths']+[M['loc_path']]:assert read(O/(p+'.tsv'))==read(roundtrip/(p+'.tsv')),p
 with Path(M['base']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==M['base_sha256']
 report.update(pack=M['pack'],sha256=hashlib.file_digest(Path(M['pack']).open('rb'),'sha256').hexdigest(),bytes=Path(M['pack']).stat().st_size,payloads=len(after),changed_payloads=changed,added_payloads=added,all_unrelated_v35_payloads_byte_identical=True,all_approved_jade_v2_payloads_byte_identical=True,dependencies_unchanged=True,roundtrip_equal=True,original_v35_unchanged=True)
(O/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
