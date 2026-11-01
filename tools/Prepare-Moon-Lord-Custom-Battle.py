"""Add the existing Moon Warden to the Cathay custom battle roster."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ref=root/'reference/local/lord-vanilla/db'
out=root/'build/moon-lord-custom-battle'
unit='mc_moon_warden_human'
donor='wh3_dlc24_cth_cha_yuan_bo_human'
files=[]
def read(table):
    with (ref/(table+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:
        d=list(csv.reader(f,delimiter='\t'))
    return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def write(table,rows):
    (h,m),_=read(table)
    assert all(set(r)<=set(h) for r in rows)
    internal='db/'+table+'_tables/mc_moon_warden_custom_battle'
    m[0]=';'.join(m[0].split(';')[:2]+[internal])
    p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
    files.append(internal)
_,rows=read('units_custom_battle_permissions')
r=next(r for r in rows if r['unit']==donor and r['faction']=='wh3_main_cth_cathay_mp')
write('units_custom_battle_permissions',[dict(r,unit=unit,set_piece_character=unit)])
_,rows=read('battle_set_piece_armies_characters')
r=next(r for r in rows if r['character_name']==donor)
write('battle_set_piece_armies_characters',[dict(r,character_name=unit,unit_type=unit,
    agent_subtype='mc_moon_warden',forename='1800312100',surname='1800312101',
    magic_lore='mc_moon_warden_lore',character_model='1800312000',skillset='mc_moon_warden_cb_skills',character_level='40')])
write('battle_set_piece_armies_characters_skillsets',[{'key':'mc_moon_warden_cb_skills'}])
skills=json.loads((root/'build/moon-lord/lord-report.json').read_text())['starting_skills']
write('battle_set_piece_armies_characters_skillsets_skills',[
    {'skill':s,'skillset_key':'mc_moon_warden_cb_skills','sort_order':str(i)} for i,s in enumerate(skills)])
_,rows=read('names')
a=next(r for r in rows if r['id']=='1098846955')
b=next(r for r in rows if r['id']=='1896245993')
assert not any(r['id'] in ('1800312100','1800312101') for r in rows)
write('names',[dict(a,id='1800312100',gender='m',frequency='0'),dict(b,id='1800312101',frequency='0')])
_,rows=read('units_to_groupings_military_permissions')
selected=[dict(r,unit=unit) for r in rows if r['unit']==donor and 'wh3_main_cth' in r.values()]
assert len(selected)==1
write('units_to_groupings_military_permissions',selected)
internal='text/db/mc_moon_warden_custom_battle.loc';p=out/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([
      ['key','text','tooltip'],['#Loc;1;'+internal,'',''],
      ['names_name_1800312100','Moon Warden','true'],['names_name_1800312101','','true']])
files.append(internal)
(out/'report.json').write_text(json.dumps({'files':files,'faction':'wh3_main_cth_cathay_mp','unit':unit,'runtime_verified':False},indent=2))
print('Prepared custom battle permissions, character, names, military group and localization.')
