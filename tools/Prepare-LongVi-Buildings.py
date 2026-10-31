"""Private local derivatives: Cathay primary chain scoped to Long Vi, 8 total slots."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/local/vanilla'
OUT=ROOT/'build/province-edit'
OLD='wh3_main_cth_settlement_minor'
NEW='mc_long_vi_cth_settlement'
mapping={OLD:NEW, **{OLD+'_'+x:NEW+'_'+x for x in ('1','2','3','ruin')}}
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
def write(internal,header,meta,rows):
    path=OUT/(internal+'.tsv');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows([header,meta]+rows)
    return internal

files=[];counts={};copies={}
tables={
 'building_chains_tables':['key'],
 'building_levels_tables':['level_name','chain'],
 'building_culture_variants_tables':['building'],
 'building_effects_junction_tables':['building'],
 'building_downgrade_junctions_tables':['from','to'],
 'building_upgrades_junction_tables':['from','to'],
 'building_units_allowed_tables':['building'],
 'building_level_armed_citizenry_junctions_tables':['building_level'],
 'building_set_to_building_junctions_tables':['building_chain','building_level'],
}
for table,columns in tables.items():
    source=read(REF/'db'/table/'data__.tsv');header=source[0];rows=[]
    fields=[header.index(c) for c in columns]
    identities={row[0] for row in source[2:]}
    for row in source[2:]:
        if not any(row[i] in mapping for i in fields):continue
        clone=row.copy()
        for i in fields:clone[i]=mapping.get(row[i],row[i])
        if table in ('building_units_allowed_tables','building_level_armed_citizenry_junctions_tables'):
            value=str(1800310000+len(rows));assert value not in identities
            clone[0]=value
        if table=='building_effects_junction_tables' and row[header.index('effect')]=='wh_main_effect_construction_slot_multiple_dummy':
            for c in ('value','value_damaged','value_ruined'):clone[header.index(c)]='7.0000'
        rows.append(clone)
    if not rows:continue
    internal='db/'+table+'/mc_long_vi_eight_slots'
    meta=source[1].copy();meta[0]=';'.join(meta[0].split(';')[:2]+[internal])
    files.append(write(internal,header,meta,rows));counts[table]=len(rows);copies[table]=rows
assert counts['building_levels_tables']==4
assert counts['building_chains_tables']==1
assert counts['building_level_armed_citizenry_junctions_tables']>=3

# Primary slot stays the same template. Replace only its Cathay primary chain.
table='slot_template_permitted_building_chains_tables'
source=read(ROOT/'reference/local/iee/db'/table/'!cr_start_pos_primary.tsv')
internal='db/'+table+'/mc_long_vi_eight_slots'
meta=source[1].copy();meta[0]=';'.join(meta[0].split(';')[:2]+[internal])
files.append(write(internal,source[0],meta,[[OLD,'','cr_minor_primary_long_vi','','true'],[NEW,'','cr_minor_primary_long_vi','','false']]))
source=read(REF/'db/campaign_building_chain_slot_unlocks_tables/data__.tsv')
internal='db/campaign_building_chain_slot_unlocks_tables/mc_long_vi_eight_slots'
meta=source[1].copy();meta[0]=';'.join(meta[0].split(';')[:2]+[internal])
# active_slot_count is the number unlocked in addition to the primary slot.
# The existing port consumes one of these seven, leaving six general slots.
files.append(write(internal,source[0],meta,[[NEW,str(level),'7'] for level in (-1,1,2,3)]))

# Reuse vanilla localized strings under the new building/chain keys.
localized={}
for path in (REF/'text').rglob('*.tsv'):
    for row in read(path)[2:]:
        if len(row)>=3 and OLD in row[0]:
            clone=row.copy();clone[0]=clone[0].replace(OLD,NEW)
            localized[clone[0]]=clone
assert any('name_'+NEW+'_2' in key for key in localized)
internal='text/db/mc_long_vi_buildings.loc'
files.append(write(internal,['key','text','tooltip'],['#Loc;1;'+internal,'',''],list(localized.values())))
report={'status':'prepared_not_game_tested','region':'cr_combi_region_long_vi','total_slots':8,
        'primary_slots':1,'port_slots':1,'general_slots':6,'unlock_levels':[1,2,3],
        'old_primary_building':OLD+'_2','new_primary_building':NEW+'_2',
        'port_preserved':'wh3_main_cth_port_1','files':files,'cloned_row_counts':counts,
        'original_building_keys_overridden':False}
(OUT/'long-vi-buildings-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
