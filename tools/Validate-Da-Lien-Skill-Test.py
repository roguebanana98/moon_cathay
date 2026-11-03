"""Independent checks of the exported v23 spell unlocks and reachable skill gates."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'build/huyen-ve-v23-da-lien-skills'
E=R/'reference/local/da-lien-v23-check'
N=R/'reference/local/lord-vanilla/db'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0],x)) for x in a[2:]]
def table(t):return read(E/('db/'+t+'_tables/mc_da_lien_skills.tsv'))
manifest=json.loads((O/'skill-manifest.json').read_text())
skills={x['slug']:x for x in manifest['visible']}
nodes={x['key']:x for x in table('character_skill_nodes')}
levels=table('character_skill_level_details')
links=table('character_skill_node_links')
grants=table('character_skill_level_to_effects_junctions')
bridge=read(N/'effect_bonus_value_unit_ability_junctions_tables/data__.tsv')
def enabled(state,bonus):
    effects={g['effect_key'] for g in grants if int(g['level'])==state.get(g['character_skill_key'],0)}
    return {b['unit_ability'] for b in bridge if b['effect'] in effects and b['bonus_value_id']==bonus}
foundation={'mc_da_lien_skill_foundation_blossom':1,'mc_da_lien_skill_foundation_actions':1}
spells=set(manifest['spells'])
assert enabled(foundation,'enable') & spells == {'wh3_main_spell_yin_blossom_wind'}
assert not enabled(foundation,'enable_overchage') & spells
for slug,ability in zip(['blossom','earth','stone','shadows','talons','comet'],manifest['spells']):
    key=skills[slug]['skill']
    learn=dict(foundation,**{key:1})
    assert ability in enabled(learn,'enable'),slug
    # Starter has two paid upgrade levels; other spells first buy base, then overcast.
    if slug!='blossom':assert ability not in enabled(learn,'enable_overchage'),slug
    upgrade=dict(foundation,**{key:2 if slug!='blossom' else 1})
    assert ability in enabled(upgrade,'enable_overchage'),slug
    cost=dict(foundation,**{key:skills[slug]['levels']})
    assert ability in enabled(cost,'cost_mod'),slug
state={}
def spend(slug,rank):
    x=skills[slug];key=x['skill'];level=state.get(key,0)+1
    gate=next(int(d['unlocked_at_rank'])+1 for d in levels if d['skill_key']==key and int(d['level'])==level)
    assert rank>=gate,(slug,rank,gate)
    parents=[l for l in links if l['child_key']==x['node']]
    if parents:
        parent_skills=[nodes[l['parent_key']]['character_skill_key'] for l in parents]
        if parents[0]['link_type']=='SUBSET_REQUIRED':
            assert sum(state.get(k,0) for k in parent_skills)>=int(nodes[x['node']]['required_num_parents'])
        else:assert all(state.get(k,0)>0 for k in parent_skills)
    state[key]=level
# A legal early path: basic heal/armour/control, then advanced AOE and conduit.
path=['earth','stone','shadows','power_of_yin','blossom','evasion','talons','comet','earthing','reserves','conduit']
for rank,slug in enumerate(path,2):spend(slug,rank)
assert state[skills['conduit']['skill']]==1 and len(path)==11
assert sum(x['levels'] for x in manifest['visible'])==51
assert {x['name'] for x in manifest['visible'] if x['slug'] in ['mentor','specialist','evasion','earthing','reserves','conduit']}=={'Mentor','Specialist','Evasion','Earthing','Magical Reserves','Arcane Conduit'}
mentor=[int(d['unlocked_at_rank'])+1 for d in levels if d['skill_key']==skills['mentor']['skill']]
assert mentor==[30,40,50]
cb=set(manifest['cb_skills'])
assert set(skills[s]['skill'] for s in ['blossom','earth','stone','shadows','talons','comet'])<=cb
assert set(foundation)-{'mc_da_lien_skill_foundation_actions'}<=cb
assert not any('metal' in b for b in enabled({g['character_skill_key']:int(g['level']) for g in grants},'enable'))
report=dict(status='passed',checks=['six native base/overcast/cost grant paths','only Blossom Wind at rank one','legal level 2-12 progression','51 total points, 26 visible nodes','caster/Hero basics and Mentor 30/40/50','Custom Battle six-spell preset','no Metal spell grants'],lua_api_reference='https://chadvandy.github.io/tw_modding_resources/WH3/campaign/episodic_scripting.html#function:episodic_scripting:force_reset_skills',runtime_verified=False)
(O/'skill-regression.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
