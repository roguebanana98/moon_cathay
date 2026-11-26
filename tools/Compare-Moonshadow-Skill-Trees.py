import csv,json
from pathlib import Path
R=Path.cwd();D=R/'build/da-anh-skill-comparison/db';N=R/'reference/local/lord-vanilla/db'
def read(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader((l for l in f if not l.startswith('#')),delimiter='\t'))
def mods(t):return [r for p in (D/(t+'_tables')).glob('*.tsv') for r in read(p)]
def native(t):return read(N/(t+'_tables/data__.tsv'))
skills={r['key']:r for r in native('character_skills')+mods('character_skills')};effects=native('character_skill_level_to_effects_junctions')+mods('character_skill_level_to_effects_junctions');details=native('character_skill_level_details')+mods('character_skill_level_details');nodes={r['key']:r for r in mods('character_skill_nodes')}
sets={}
for typ in ['mc_da_anh','mc_moonshadow_assassin']:
 a=[nodes[r['item']] for r in mods('character_skill_node_set_items') if r['set']==typ+'_skills' and r['mod_disabled']=='false'];sets[typ]=a
 print('\nTREE',typ,'TOTAL',len(a),'VISIBLE',sum(r['visible_in_ui']=='true' for r in a))
 for r in sorted(a,key=lambda r:(int(r['indent']),int(r['tier']))):
  if r['visible_in_ui']!='true':continue
  k=r['character_skill_key'];s=skills[k];es=[e for e in effects if e['character_skill_key']==k];levels=[d for d in details if d['skill_key']==k]
  print(json.dumps(dict(skill=k,name=s['localised_name'],row=r['indent'],tier=r['tier'],starting=r['points_on_creation'],unlock=s['unlocked_at_rank'],max_level=max([1]+[int(e['level']) for e in es]+[int(x['level']) for x in levels]),levels=[(x['level'],x['unlocked_at_rank']) for x in levels]),ensure_ascii=False))
  if k.startswith('mc_da_anh') or 'mobility' in k:print('EFFECTS',es)
A={n['character_skill_key'] for n in sets['mc_da_anh']};B={n['character_skill_key'] for n in sets['mc_moonshadow_assassin']};print('SHARED',len(A&B),'DA_ONLY',A-B,'GENERIC_ONLY',B-A)
a=[(r['effect_key'],r['level'],r['effect_scope'],r['value']) for r in effects if r['character_skill_key']=='mc_da_anh_execution'];b=[(r['effect_key'],r['level'],r['effect_scope'],r['value']) for r in effects if r['character_skill_key']=='wh2_main_skill_skv_trophy_heads_assassin'];print('TROPHY_EFFECT_EQUAL',a==b)
