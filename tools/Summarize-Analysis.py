"""Summarize local exports; produces factual reports, not distributable mod assets."""
import csv
import json
from pathlib import Path
from inspect_esf import walk

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'reference/local'
KEY = 'cr_cth_agents_of_the_moon'


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        return [r for r in reader if not str(next(iter(r.values()))).startswith('#')]


loc = {}
for source in ('vanilla','mixer','iee'):
    for file in sorted((REF/source/'text').rglob('*.tsv')):
        for r in rows(file):
            if r.get('text'): loc[r['key']] = r['text']

factions = {}
for file in (REF/'iee/db/factions_tables').glob('*.tsv'):
    factions.update({r['key']:r for r in rows(file)})
provinces = {}
for file in (REF/'iee/db/region_to_province_junctions_tables').glob('*.tsv'):
    provinces.update({r['region']:r for r in rows(file)})
khuresh = set()
for file in (REF/'iee/db/regions_to_region_groups_junctions_tables').glob('*.tsv'):
    for r in rows(file):
        if 'cai_region_hint_area_khuresh' in r.values():
            khuresh.add(next(v for v in r.values() if v.startswith('cr_combi_region_')))


def summarize(file):
    data=json.loads(file.read_text(encoding='utf-8'))
    selected=data['selected']
    faction=next(n for n in selected if n['name']=='FACTION' and n['groups'][0][1]==KEY)
    assert faction['version']==9
    fid=faction['groups'][0][0]
    leader_post=next(n for n in walk(faction) if n['name']=='CHARACTER_POST' and n['groups'][0][1]=='faction_leader')
    leader_id=leader_post['groups'][0][2]
    character=next(n for n in walk(faction) if n['name']=='CHARACTER' and n['groups'][0][1]==leader_id)
    assert character['version']==5
    details=next(n for n in selected if n['name']=='CHARACTER_DETAILS' and n['groups'][0][4]==leader_id and n['groups'][0][3]==KEY)
    assert details['version']==6
    dg=details['groups'][0]
    assert dg[22]==character['groups'][0][3]
    names={}
    for n in walk(details):
        if n['name']=='CHARACTER_NAME_ELEMENT':
            for g in n['groups']:
                k=g[0]['groups'][0][0]
                names[g[1]]={'key':k,'text':loc.get(k,k)}
    regions=[]
    all_regions=[]
    idmap={n['groups'][0][0]:n['groups'][0][1] for n in selected if n['name']=='FACTION'}
    for n in selected:
        if n['name']!='REGION':continue
        assert n['version']==3
        g=n['groups'][0]
        # Compact output omits child records; owner faction ID is scalar position 4.
        owner=idmap.get(g[4],f'UNRESOLVED_ID_{g[4]}')
        p=provinces.get(g[1],{})
        row={'region':g[1],'name':loc.get('regions_onscreen_'+g[1],g[1]),'owner':owner,
             'owner_name':loc.get('factions_screen_name_'+owner,owner),
             'subculture':factions.get(owner,{}).get('subculture','not_in_iee_factions_export'),
             'province':p.get('province',''),'province_name':loc.get('provinces_onscreen_'+p.get('province',''),''),
             'province_capital':p.get('is_capital',''),'esf_offset':n['offset']}
        all_regions.append(row)
        if g[4]==fid: regions.append(row)
    return {'faction':KEY,'esf_faction_id':fid,'faction_offset':faction['offset'],
            'leader':{'character_id':leader_id,'details_id':dg[22],'frontend_id':dg[23],
                      'subtype':dg[13],'art_set':dg[28],'names':names,
                      'post_offset':leader_post['offset'],'character_offset':character['offset'],'details_offset':details['offset']},
            'regions':regions},all_regions


start,all_regions=summarize(REF/'startpos-compact.json')
save,_=summarize(REF/'save-compact.json')
summary={'startpos':start,'existing_save':save,'db_faction':factions[KEY],
         'khuresh_definition':'IEE cai_region_hint_area_khuresh (AI hint group, not a universal geographical boundary)',
         'khuresh_regions':len(khuresh)}
(ROOT/'reports/agents-of-the-moon.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
selected=[r for r in all_regions if r['region'] in khuresh]
assert len(selected)==len(khuresh)
with (ROOT/'reports/khuresh-startpos.tsv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(selected[0]),delimiter='\t')
    writer.writeheader(); writer.writerows(sorted(selected,key=lambda r:(r['province'],r['region'])))
print(json.dumps({'khuresh_regions':len(selected),'khuresh_provinces':len({r['province'] for r in selected}),
 'khuresh_owners':len({r['owner'] for r in selected}),'leader':start['leader'],'regions':start['regions']},indent=2,ensure_ascii=False))
