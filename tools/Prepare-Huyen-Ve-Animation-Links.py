"""Scoped battle/campaign model links, preserving v14 gameplay row fields."""
import csv,json,copy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];REF=R/'reference/local/huyen-ve-animation-integration';O=R/'build/huyen-ve-animation-integration'
UNIT='mc_moon_warden_human';VARIANT='mc_huyen_ve_human';ANIM='mc_huyen_ve_human';UNIFORM='mc_huyen_ve_uniform'
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:data=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return data[0],data[1],[dict(zip(data[0],row)) for row in data[2:]]
files=[];changes={}
def write(table,header,meta,rows,name='mc_huyen_ve_model'):
    internal='db/'+table+'_tables/'+name;meta=meta.copy();meta[0]=';'.join(meta[0].split(';')[:2]+[internal]);path=O/(internal+'.tsv');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([header,meta]+[[row.get(k,'') for k in header] for row in rows])
    files.append(internal)
for table,key,value,patch in [
    ('land_units','key',UNIT,{'man_animation':ANIM}),
    ('unit_variants','unit',UNIT,{'variant':VARIANT}),
    ('campaign_character_arts','id','1800312000',{'uniform':UNIFORM})]:
    h,m,rows=read(REF/('v14/db/'+table+'_tables/mc_moon_warden.tsv'));assert len(rows)==1 and rows[0][key]==value
    old=rows[0].copy();rows[0].update(patch);changes[table]={'row_key':value,'fields':{k:{'before':old[k],'after':rows[0][k]} for k in patch}}
    write(table,h,m,rows,'mc_moon_warden')
for table,key,value,patch in [
    ('variants','variant_name','wh3_dlc24_cth_cha_yuan_bo_human',{'variant_name':VARIANT,'variant_filename':VARIANT}),
    ('agent_uniforms','uniform_name','wh3_dlc24_uniform_cth_yuan_bo',{'uniform_name':UNIFORM,'filename':VARIANT,'battle_filename':VARIANT,'campaign_porthole_filename':VARIANT}),
    ('battle_animations_table','key','hu1e_dlc24_yuan_bo_dragon_jade',{'key':ANIM})]:
    h,m,rows=read(REF/('db/'+table+'_tables/data__.tsv'));selected=[row for row in rows if row[key]==value];assert len(selected)==1
    row=dict(selected[0],**patch);write(table,h,m,[row])
native=json.loads((R/'reference/local/yuan-bo-model/animations/database/battle/tables/hu1e_dlc24_yuan_bo_dragon_jade.txt').read_text())
custom=copy.deepcopy(native);custom['Properties']['TableName']=ANIM
assert custom['Entries']==native['Entries'] and custom['Properties']['SkeletonName']=='humanoid01e'
internal='animations/database/battle/tables/'+ANIM+'.txt';p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(custom,indent=4),encoding='utf-8');files.append(internal)
graphics=json.loads((O/'graphics-manifest.json').read_text());files+=graphics['files']
result={'files':files,'variant':VARIANT,'animation_table':ANIM,'uniform':UNIFORM,'unit':UNIT,'changes_to_existing_v14':changes,
 'campaign_animation_preserved':'cam_lord_hu1e_dlc24_yuan_bo_dragon_jade','native_clips_bundled':False,'runtime_verified':False}
(O/'integration-links.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
