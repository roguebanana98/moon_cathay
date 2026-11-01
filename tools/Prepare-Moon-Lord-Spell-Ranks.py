"""Own spell skill keys and level gates; two starting spell investments."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];ref=root/'reference/local/lord-vanilla/db';out=root/'build/moon-lord-spell-ranks';out.mkdir(parents=True,exist_ok=True);files=[]
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t'))
 return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def vanilla(t):return read(ref/(t+'_tables/data__.tsv'))
def write(t,rows,filename='mc_moon_warden_spell_ranks',source=None):
 (h,m),_=read(source) if source else vanilla(t);assert all(set(r)<=set(h) for r in rows)
 internal='db/'+t+'_tables/'+filename;m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(internal)
defs=[('breath','wh3_main_skill_cth_magic_yang_01_dragons_breath_lord',"Dragon's Breath",[1,1]),('earth','wh2_main_skill_magic_life_wizard_earth_blood_lord','Earth Blood',[1,1]),('flame','wh2_main_skill_all_magic_fire_10_flame_storm_lord','Flame Storm',[1,1])]
mapping={old:'mc_moon_warden_magic_'+s for s,old,_,_ in defs}
_,base=vanilla('character_skills');_,effects=vanilla('character_skill_level_to_effects_junctions');skills=[];levels=[];grants=[];loc=[]
for suffix,old,name,ranks in defs:
 key=mapping[old];s=next(s for s in base if s['key']==old);skills.append(dict(s,key=key,unlocked_at_rank=str(ranks[0]-1)))
 for level,rank in enumerate(ranks,1):levels.append(dict(campaign_key='',faction_key='',level=str(level),skill_key=key,subculture_key='',image_path='x',unlocked_at_rank=str(rank-1)))
 grants.extend(dict(e,character_skill_key=key) for e in effects if e['character_skill_key']==old)
 description=('Requires level 2 in both Dragon\'s Breath and Earth Blood. Spend skill points to learn and upgrade Flame Storm.' if suffix=='flame' else 'Starts with one skill level. The second level can be purchased with a skill point without a character-rank gate.')
 loc.extend([['character_skills_localised_name_'+key,name,'true'],['character_skills_localised_description_'+key,description,'true']])
for t,rows in [('character_skills',skills),('character_skill_level_details',levels),('character_skill_level_to_effects_junctions',grants)]:write(t,rows)
source=root/'reference/local/moon-lord-v9-check/db/character_skill_nodes_tables/mc_moon_warden.tsv';_,nodes=read(source)
for n in nodes:
 if n['character_skill_key'] in mapping:
  n['character_skill_key']=mapping[n['character_skill_key']]
  n['points_on_creation']='0' if n['character_skill_key'].endswith('_flame') else '1'
  n['required_num_parents']='4' if n['character_skill_key'].endswith('_flame') else '0'
write('character_skill_nodes',nodes,'mc_moon_warden',source)
write('character_skill_node_links',[
 dict(child_key='mc_moon_warden_spell_2',parent_key=parent,initial_descent_tiers='0',
      parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',
      child_link_position_offset='0.0000',link_type='SUBSET_REQUIRED')
 for parent in ('mc_moon_warden_spell_0','mc_moon_warden_spell_1')])
source=root/'reference/local/moon-lord-v9-check/db/battle_set_piece_armies_characters_skillsets_skills_tables/mc_moon_warden_custom_battle.tsv';_,rows=read(source)
for r in rows:r['skill']=mapping.get(r['skill'],r['skill'])
write('battle_set_piece_armies_characters_skillsets_skills',rows,'mc_moon_warden_custom_battle',source)
internal='text/db/mc_moon_warden_spell_ranks.loc';p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
spec=json.loads((root/'build/moon-lord/lord-report.json').read_text());spec['starting_skills']=[mapping[defs[0][1]],mapping[defs[1][1]],'wh3_main_skill_cth_magic_yang_dummy_dragons_breath'];spec['files']=files;spec['spell_rank_definitions']=defs;spec['starting_spells']='Dragon Breath 1, Earth Blood 1; Flame Storm 0'
(out/'lord-report.json').write_text(json.dumps(spec,indent=2));print(spec['starting_spells'])
