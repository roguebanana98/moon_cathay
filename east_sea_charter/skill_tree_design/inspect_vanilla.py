import csv
from pathlib import Path
p=Path('east_sea_charter/skill_tree_design/vanilla_reference/db')
def read(t):
 with (p/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f,delimiter='\t');next(r);return list(r)
sk={r['key']:r for r in read('character_skills')};no={r['key']:r for r in read('character_skill_nodes')};it=read('character_skill_node_set_items')
for se in ['wh_main_skill_node_set_emp_general','wh_main_skill_node_set_brt_damsel']:
 print('\nSET',se)
 for r in it:
  if r['set']==se and r['mod_disabled']=='false':
   n=no[r['item']];s=sk[n['character_skill_key']];print(n['indent'],n['tier'],n['points_on_creation'],s['key'],s['localised_name'],s['image_path'],sep=' | ')
