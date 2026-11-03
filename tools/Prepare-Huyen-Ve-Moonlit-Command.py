"""Native Army of Renown provenance, plus a scoped Moonlit Command skill."""
import csv,json,copy,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v19-moonlit-command';O.mkdir(exist_ok=True);REF=R/'reference/local/huyen-ve-v19-base';N=R/'reference/local/lord-vanilla/db';files=[]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t'))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
def native(t):return read(N/(t+'_tables/data__.tsv'))
def donor(t,c,k):return copy.deepcopy(next(r for r in native(t)[1] if r[c]==k))
def write(t,rows,name='mc_huyen_ve_moonlit_command',source=None):
 (h,m),_=read(source) if source else native(t);internal='db/'+t+'_tables/'+name;m=m.copy();m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,m]+[[r.get(k,'') for k in h] for r in rows])
 files.append(internal)
ability='mc_huyen_ve_moonlit_command';skill='mc_moon_warden_magic_moonlit_command';effect='mc_huyen_ve_enable_moonlit_command';node='mc_moon_warden_spell_moonlit_command';old='wh_dlc06_lord_abilities_spite_of_da_bad_moon';oldskill='wh_dlc06_skill_grn_night_goblin_warboss_spite_of_da_bad_moon';oldeffect='wh_dlc06_effect_ability_enable_ability_spite_of_da_bad_moon'
ua=donor('unit_abilities','key',old);ua.update(key=ability,requires_effect_enabling='true');write('unit_abilities',[ua])
sa=donor('unit_special_abilities','key',old);uid='1800312400';assert not any(r['unique_id']==uid for r in native('unit_special_abilities')[1]);sa.update(key=ability,unique_id=uid,audio='');assert sa['wind_up_stance']=='' and sa['mana_cost']=='0.0000';write('unit_special_abilities',[sa])
phase=donor('special_ability_phases','id',old);phase['id']=ability;assert not phase['requested_stance'];write('special_ability_phases',[phase])
links=[dict(r,special_ability=ability,phase=ability) for r in native('special_ability_to_special_ability_phase_junctions')[1] if r['special_ability']==old];assert len(links)==1;write('special_ability_to_special_ability_phase_junctions',links)
stats=[dict(r,phase=ability) for r in native('special_ability_phase_stat_effects')[1] if r['phase']==old];assert len(stats)==3;write('special_ability_phase_stat_effects',stats)
write('land_units_to_unit_abilites_junctions',[dict(ability=ability,land_unit='mc_moon_warden_human',culture='*')])
ef=donor('effects','effect',oldeffect);ef['effect']=effect;write('effects',[ef]);junction=donor('effect_bonus_value_unit_ability_junctions','effect',oldeffect);junction.update(effect=effect,unit_ability=ability);write('effect_bonus_value_unit_ability_junctions',[junction])
sk=donor('character_skills','key',oldskill);sk.update(key=skill,localised_name='Moonlit Command',localised_description='Bolsters nearby allies with the resolve of the moonlit watch.',unlocked_at_rank='0');write('character_skills',[sk])
level=donor('character_skill_level_details','skill_key',oldskill);level.update(skill_key=skill,unlocked_at_rank='0',faction_key='',campaign_key='');write('character_skill_level_details',[level])
write('character_skill_level_to_effects_junctions',[dict(character_skill_key=skill,effect_key=effect,level='1',effect_scope='character_to_character_own',value='1.0000')])
p=REF/'db/character_skill_nodes_tables/mc_moon_warden.tsv';_,nodes=read(p);flame=next(r for r in nodes if r['key']=='mc_moon_warden_spell_2');assert flame['tier']=='2';flame['tier']='3';earth=next(r for r in nodes if r['key']=='mc_moon_warden_spell_1');new=dict(earth,key=node,character_skill_key=skill,tier='2',points_on_creation='0',required_num_parents='1');nodes.append(new);write('character_skill_nodes',nodes,'mc_moon_warden',p)
write('character_skill_node_set_items',[dict(set='mc_moon_warden_skills',item=node,mod_disabled='false')])
write('character_skill_node_links',[dict(child_key=node,parent_key='mc_moon_warden_spell_1',initial_descent_tiers='0',parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',child_link_position_offset='0.0000',link_type='REQUIRED')])
write('battle_set_piece_armies_characters_skillsets_skills',[dict(skill=skill,skillset_key='mc_moon_warden_cb_skills',sort_order='4')])
loc=[['character_skills_localised_name_'+skill,'Moonlit Command','true'],['character_skills_localised_description_'+skill,'Unlocks Moonlit Command after learning Earth Blood. Costs one skill point. Does not add a new requirement to Flame Storm.','true'],['unit_abilities_onscreen_name_'+ability,'Moonlit Command','true'],['unit_abilities_tooltip_text_'+ability,'Affected allies: +25% weapon damage and +16 bonus vs large for 20 seconds. Area of effect: 35m. Cooldown: 90 seconds. No Winds of Magic cost.','true'],['special_ability_phases_onscreen_name_'+ability,'Moonlit Command','true'],['effects_description_'+effect,'Ability: Moonlit Command','true']]
internal='text/db/mc_huyen_ve_moonlit_command.loc';p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
icon_source=R/'reference/local/huyen-ve-moonlit-command-icon/ui/battle ui/ability_icons/wh_dlc06_character_abilities_spite_of_da_bad_moon.png'
icon_path='ui/battle ui/ability_icons/'+ability+'.png'
(O/icon_path).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(icon_source,O/icon_path)
assert hashlib.sha256(icon_source.read_bytes()).digest()==hashlib.sha256((O/icon_path).read_bytes()).digest()
files.append(icon_path)
# Keep the original native skill; do not duplicate/override its effects.
k='wh3_main_skill_all_army_of_renown_legendary_lord';native_effects=[r for r in native('character_skill_level_to_effects_junctions')[1] if r['character_skill_key']==k];assert [(r['level'],float(r['value'])) for r in native_effects]==[('1',2),('2',4),('3',6)]
ns={r['key'] for r in native('character_skill_nodes')[1] if r['character_skill_key']==k};sets={r['set'] for r in native('character_skill_node_set_items')[1] if r['item'] in ns};owners=[r for r in native('character_skill_node_sets')[1] if r['key'] in sets]
assert any('cth_yuan_bo' in r['key'] for r in owners);support=read(REF/'db/character_skill_nodes_tables/mc_moon_warden_support.tsv')[1];assert any(r['character_skill_key']==k for r in support)
report={'files':files,'skill':skill,'ability':ability,'node':node,'skill_order':["Dragon's Breath",'Earth Blood','Moonlit Command','Flame Storm'],'one_purchased_level':True,'flame_storm_prerequisites_unchanged':True,'native_donor':old,'stats':stats,'army_of_renown':{'key':k,'effects':native_effects,'native_owners':owners,'decision':'Keep native +2/+4/+6 RoR army capacity; no authored effect override'},'runtime_verified':False}
(O/'skill-manifest.json').write_text(json.dumps(report,indent=2));print('MOONLIT_COMMAND_PREPARED',len(files),'payloads;',len(owners),'native Army of Renown owners')
