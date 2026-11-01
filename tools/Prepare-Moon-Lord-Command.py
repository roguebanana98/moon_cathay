"""Control, conditional Chaos defence and scoped Cathay missile support."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];ref=root/'reference/local/lord-vanilla/db';out=root/'build/moon-lord-command';files=[]
def read(t):
 with (ref/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t'))
 return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def write(t,rows):
 (h,m),_=read(t);assert all(set(r)<=set(h) for r in rows)
 internal='db/'+t+'_tables/mc_moon_warden_command';m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(internal)
defs=[('order',6,'Moonlit Order','Control +2/+4 in the owned province containing this Lord.','wh_main_effect_public_order_characters','character_to_province_own',[2,4],'campaign_public_order.png'),
 ('ward',10,'Bulwark Against Chaos','Ward save +5%/+10% for this army when fighting Chaos cultures, including Chaos Dwarfs, Norsca and Beastmen.','wh2_dlc10_effect_force_stat_ward_save_vs_chaos_norsca_beastmen','general_to_force_own',[5,10],'resistance_ward_save.png'),
 ('range',14,'Moonwatch Marksmen','Range +5%/+10% for Cathay missile units in this army, including artillery and eligible Regiments of Renown.','mc_moon_warden_range','general_to_force_own',[5,10],'character_range.png'),
 ('reload',18,'Disciplined Volleys','Reload time reduction +10%/+20% for Cathay missile units in this army, including artillery and eligible Regiments of Renown.','mc_moon_warden_reload','general_to_force_own',[10,20],'battle_ranged_damage.png')]
_,ss=read('character_skills');base=next(s for s in ss if s['key']=='wh2_dlc11_skill_all_lord_self_blade_master')
_,ns=read('character_skill_nodes');nodebase=next(n for n in ns if n['key']=='wh3_dlc24_skill_node_cth_human_combat_1_1')
skills=[];levels=[];nodes=[];items=[];links=[];effects=[];battle=[];loc=[]
for i,(suffix,level,name,desc,effect,scope,values,icon) in enumerate(defs):
 key='mc_moon_warden_command_'+suffix;node=key+'_node'
 skills.append(dict(base,key=key,image_path=icon,localised_name=name,localised_description=desc,unlocked_at_rank=str(level-1)))
 nodes.append(dict(nodebase,key=node,character_skill_key=key,campaign_key='',faction_key='cr_cth_agents_of_the_moon',indent='0',tier=str(i),points_on_creation='0',required_num_parents='0' if i==0 else '1',visible_in_ui='true'))
 items.append(dict(set='mc_moon_warden_skills',item=node,mod_disabled='false'))
 if i:links.append(dict(child_key=node,parent_key='mc_moon_warden_command_'+defs[i-1][0]+'_node',initial_descent_tiers='0',parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',child_link_position_offset='0.0000',link_type='REQUIRED'))
 for rank,value in enumerate(values,1):
  levels.append(dict(campaign_key='',faction_key='',level=str(rank),skill_key=key,subculture_key='',image_path='',unlocked_at_rank=str(level-1+2*(rank-1))))
  effects.append(dict(character_skill_key=key,effect_key=effect,level=str(rank),effect_scope=scope,value=f'{value:.4f}'))
 # A repeated skill in the ordered battle list grants its second level,
 # matching vanilla preset skillsets; order is part of the composite key.
 if suffix!='order':
  for rank in range(2):battle.append(dict(skill=key,skillset_key='mc_moon_warden_cb_skills',sort_order=str(20+i*2+rank)))
 loc.extend([['character_skills_localised_name_'+key,name,'true'],['character_skills_localised_description_'+key,desc,'true']])
for t,rows in [('character_skills',skills),('character_skill_level_details',levels),('character_skill_nodes',nodes),('character_skill_node_set_items',items),('character_skill_node_links',links),('character_skill_level_to_effects_junctions',effects),('battle_set_piece_armies_characters_skillsets_skills',battle)]:write(t,rows)
_,ef=read('effects');new_effects=[];junctions=[]
for new,donor,bonus,text in [('mc_moon_warden_range','wh3_main_effect_range_cth_ranged','range_mod','Range: %+n% for Cathay missile units (including artillery and eligible Regiments of Renown)'),('mc_moon_warden_reload','wh3_main_effect_force_stat_reload_time_reduction_cth_ranged_rank7','reload','Reload time reduction: %+n% for Cathay missile units (including artillery and eligible Regiments of Renown)')]:
 original=next(r for r in ef if r['effect']==donor);new_effects.append(dict(original,effect=new))
 for group in ('cth_missile_units','cth_missile_units_ror'):junctions.append(dict(bonus_value_id=bonus,effect=new,unit_set=group))
 loc.append(['effects_description_'+new,text,'true'])
write('effects',new_effects);write('effect_bonus_value_ids_unit_sets',junctions)
internal='text/db/mc_moon_warden_command.loc';p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
(out/'report.json').write_text(json.dumps({'files':files,'definitions':defs,'runtime_verified':False},indent=2))
print('Prepared command branch; recruitment rank work remains deferred.')


