"""Scoped four-node duelist branch; vanilla ability mechanics, custom progression."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];ref=root/'reference/local/lord-vanilla/db';out=root/'build/moon-lord-duelist'
files=[]
def read(t):
 with (ref/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t'))
 return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def write(t,rows):
 (h,m),_=read(t);assert all(set(r)<=set(h) for r in rows)
 internal='db/'+t+'_tables/mc_moon_warden_duelist';m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(internal)
defs=[('moonblade','wh2_dlc11_skill_all_lord_self_blade_master',5,'Moonblade','Melee attack +8 and weapon strength +15% for this Lord.'),
 ('enfeeble','wh2_main_skill_magic_shadow_enfeebling_foe_lord',8,'The Enfeebling Foe','Unlocks a hex that weakens an enemy unit in melee, including Lords and Heroes.'),
 ('leech','wh_main_skill_all_magic_death_01_spirit_leech',12,'Spirit Leech','Unlocks direct damage against a target enemy unit; useful against Lords and Heroes.'),
 ('onslaught','wh_dlc03_skill_bst_all_self_deadly_onslaught',16,'Deadly Onslaught','Unlocks a temporary offensive combat ability for this Lord.')]
_,originals=read('character_skills');_,allnodes=read('character_skill_nodes')
template=next(n for n in allnodes if n['key']=='wh3_dlc24_skill_node_cth_human_combat_1_1')
skills=[];levels=[];nodes=[];items=[];links=[];effects=[];loc=[];battle=[]
for i,(suffix,donor,level,name,desc) in enumerate(defs):
 key='mc_moon_warden_duelist_'+suffix;node=key+'_node'
 s=next(s for s in originals if s['key']==donor)
 skills.append(dict(s,key=key,localised_name=name,localised_description=desc,unlocked_at_rank=str(level-1)))
 levels.append(dict(campaign_key='',faction_key='',level='1',skill_key=key,subculture_key='',image_path='',unlocked_at_rank=str(level-1)))
 nodes.append(dict(template,key=node,character_skill_key=key,campaign_key='',faction_key='cr_cth_agents_of_the_moon',indent='3',tier=str(i),points_on_creation='0',required_num_parents='0' if i==0 else '1',visible_in_ui='true'))
 items.append(dict(set='mc_moon_warden_skills',item=node,mod_disabled='false'))
 if i:links.append(dict(child_key=node,parent_key='mc_moon_warden_duelist_'+defs[i-1][0]+'_node',initial_descent_tiers='0',parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',child_link_position_offset='0.0000',link_type='REQUIRED'))
 for field,value in [('localised_name',name),('localised_description',desc)]:loc.append(['character_skills_'+field+'_'+key,value,'true'])
 battle.append(dict(skill=key,skillset_key='mc_moon_warden_cb_skills',sort_order=str(10+i)))
 grants={'moonblade':[('wh_main_effect_character_stat_melee_attack','8.0000'),('wh_main_effect_character_stat_weapon_strength','15.0000')],
 'enfeeble':[('wh_dlc05_effect_ability_enable_enfeebling_foe','1.0000')],
 'leech':[('wh_main_effect_ability_enable_spirit_leech','1.0000')],
 'onslaught':[('wh_main_effect_ability_enable_deadly_onslaught','1.0000')]}
 for effect,value in grants[suffix]:effects.append(dict(character_skill_key=key,effect_key=effect,level='1',effect_scope='character_to_character_own',value=value))
for table,rows in [('character_skills',skills),('character_skill_level_details',levels),('character_skill_nodes',nodes),('character_skill_node_set_items',items),('character_skill_node_links',links),('character_skill_level_to_effects_junctions',effects),('battle_set_piece_armies_characters_skillsets_skills',battle)]:write(table,rows)
write('special_ability_groups_to_unit_abilities_junctions',[
 {'special_ability_groups':'mc_moon_warden_lore','unit_special_abilities':s} for s in ['wh_dlc05_spell_shadow_the_enfeebling_foe','wh_main_spell_death_spirit_leech']])
write('land_units_to_unit_abilites_junctions',[{'ability':'wh_main_character_abilities_deadly_onslaught','land_unit':'mc_moon_warden_human','culture':'*'}])
internal='text/db/mc_moon_warden_duelist.loc';p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
(out/'report.json').write_text(json.dumps({'files':files,'skills':[s['key'] for s in skills],'character_levels':[d[2] for d in defs],'runtime_verified':False},indent=2))
print('Prepared four sequential duelist nodes and Custom Battle grants.')
