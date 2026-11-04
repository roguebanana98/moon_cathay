"""Build Heinrich's approved native-skill tree into a standalone v3 test pack."""
import csv, hashlib, json, shutil, subprocess
from pathlib import Path

R = Path(__file__).resolve().parent
BASE = R.parent / 'heinrich_custom_battle'
REF = R.parent / 'skill_tree_design/vanilla_reference/db'
OUT = R / 'payload'
PACK = R / 'edh_heinrich_v3_skill_tree.pack'
CLI = Path(r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe')
SCHEMA = Path(r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron')
GAME = Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III')
SUBTYPE = 'edh_heinrich_cb'
SET = 'edh_heinrich_skill_node_set'
DONOR = 'wh_main_skill_node_set_emp_general'
GUARDIAN = 'wh2_dlc10_skill_hef_handmaiden_protector_2'
EXCLUDED = {
    'wh3_dlc25_skill_emp_all_unique_mark_of_hysh',
    'wh_main_skill_emp_lord_unique_general_imperial_pegasus',
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(*args, **kwargs):
    return subprocess.run([str(CLI), '-g', 'warhammer_3', *map(str, args)], check=True, **kwargs)

def read(table):
    with (REF / (table + '_tables/data__.tsv')).open(encoding='utf-8-sig', newline='') as f:
        values = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return values[:2], [dict(zip(values[0], row)) for row in values[2:]]

tables = {}
def write(table, rows):
    if not rows:
        return
    (header, meta), _ = read(table)
    assert all(set(r) == set(header) for r in rows), table
    path = 'db/' + table + '_tables/edh_heinrich_skills'
    meta[0] = ';'.join(meta[0].split(';')[:2] + [path])
    target = OUT / (path + '.tsv')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None).writerows(
            [header, meta] + [[r[k] for k in header] for r in rows])
    tables[table] = {'path': path, 'rows': rows}

def remap_rows(table, column, mapping):
    rows = [dict(r, **{column: mapping[r[column]]}) for r in read(table)[1] if r[column] in mapping]
    write(table, rows)
    return rows

assert not PACK.exists(), 'Build a new version instead of replacing a released pack.'
OUT.mkdir(parents=True, exist_ok=True)
approved = json.loads((R.parent / 'skill_tree_design/skills-vanilla-v2.json').read_text(encoding='utf8'))['h']
assert len(approved) == 52 and len({s['key'] for s in approved}) == 52
source_skills = {r['key']: r for r in read('character_skills')[1]}
source_nodes = {r['key']: r for r in read('character_skill_nodes')[1]}
source_items = [r for r in read('character_skill_node_set_items')[1] if r['set'] == DONOR]
skill_map = {s['key']: 'edh_heinrich_skill_h' + str(i).zfill(2) for i, s in enumerate(approved, 1)}
assert not set(skill_map.values()) & set(source_skills)
node_map, new_nodes, old_to_new_skills = {}, [], []

for i, skill in enumerate(approved, 1):
    old = skill['key']
    original = source_skills[old]
    new_key = skill_map[old]
    new_skill = dict(original, key=new_key, localised_name=skill['name'])
    old_to_new_skills.append(new_skill)
    if old == GUARDIAN:
        # Independent added node, not the Handmaiden's Protector/Diplomat career fork.
        donor_node = next(n for n in source_nodes.values() if n['character_skill_key'] == old)
        node = dict(donor_node, indent='0', tier='8', required_num_parents='0',
                    points_on_creation='0', faction_key='', subculture='', campaign_key='')
    else:
        donor_node = source_nodes[skill['node']['key']]
        assert donor_node == skill['node'], 'Donor node changed after design approval'
        node = dict(donor_node)
        node_map[donor_node['key']] = 'edh_heinrich_node_h' + str(i).zfill(2)
    node.update(key='edh_heinrich_node_h' + str(i).zfill(2), character_skill_key=new_key)
    new_nodes.append(node)

write('character_skills', old_to_new_skills)
write('character_skill_nodes', new_nodes)
source_set = next(r for r in read('character_skill_node_sets')[1] if r['key'] == DONOR)
write('character_skill_node_sets', [dict(source_set, key=SET, agent_subtype_key=SUBTYPE)])
new_items = []
for item in source_items:
    node = source_nodes[item['item']]
    if node['character_skill_key'] not in EXCLUDED:
        new_items.append(dict(item, set=SET, item=node_map.get(item['item'], item['item'])))
guardian_node = next(n for n in new_nodes if n['character_skill_key'] == skill_map[GUARDIAN])
new_items.append({'set': SET, 'item': guardian_node['key'], 'mod_disabled': 'false'})
write('character_skill_node_set_items', new_items)

new_links = []
for link in read('character_skill_node_links')[1]:
    if link['child_key'] in node_map:
        new_links.append(dict(link, child_key=node_map[link['child_key']],
                              parent_key=node_map.get(link['parent_key'], link['parent_key'])))
write('character_skill_node_links', new_links)
locks = [dict(r, character_skill_node=node_map[r['character_skill_node']],
              character_skill=skill_map.get(r['character_skill'], r['character_skill']))
         for r in read('character_skill_nodes_skill_locks')[1] if r['character_skill_node'] in node_map]
write('character_skill_nodes_skill_locks', locks)
remap_rows('character_skill_node_ancillary_locks', 'character_skill_node', node_map)
new_effects = remap_rows('character_skill_level_to_effects_junctions', 'character_skill_key', skill_map)
details = remap_rows('character_skill_level_details', 'skill_key', skill_map)
grants = remap_rows('character_skill_level_to_ancillaries_junctions', 'skill', skill_map)
remap_rows('character_skill_utilization_hints_junctions', 'key', skill_map)
remap_rows('character_skill_to_unit_list_display_junctions', 'character_skill', skill_map)
remap_rows('character_skill_level_to_dilemmas_junctions', 'character_skill_key', skill_map)
remap_rows('character_skills_to_quest_ancillaries', 'skill', skill_map)
# Native mount items must be permitted for the new character subtype as well.
mount_items = {g['granted_ancillary'] for g in grants}
permissions = [dict(r, agent_subtype=SUBTYPE) for r in read('ancillaries_included_agent_subtypes')[1]
               if r['agent_subtype'] == 'wh_main_emp_lord' and r['ancillary'] in mount_items]
assert {r['ancillary'] for r in permissions} == mount_items
write('ancillaries_included_agent_subtypes', permissions)

loc = 'text/db/edh_heinrich_skills.loc'
target = OUT / (loc + '.tsv'); target.parent.mkdir(parents=True, exist_ok=True)
loc_rows = []
for skill in approved:
    key = skill_map[skill['key']]
    loc_rows += [[f'character_skills_localised_name_{key}', skill['name'], 'true'],
                 [f'character_skills_localised_description_{key}', source_skills[skill['key']]['localised_description'], 'true']]
with target.open('w', encoding='utf8', newline='') as f:
    csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None).writerows(
        [['key', 'text', 'tooltip'], ['#Loc;1;' + loc, '', '']] + loc_rows)

# Meaningful structural checks before packaging.
active = {r['item'] for r in new_items if r['mod_disabled'] == 'false'}
assert len(active) == len(set(active))
assert all(n['key'] in active for n in new_nodes)
assert all(l['child_key'] in active and l['parent_key'] in active for l in new_links)
assert len({(n['indent'], n['tier']) for n in new_nodes}) == len(new_nodes), 'Overlapping visible nodes'
for skill in approved:
    old = skill['key']; new = skill_map[old]
    native = [r for r in read('character_skill_level_to_effects_junctions')[1] if r['character_skill_key'] == old]
    actual = [dict(r, character_skill_key=old) for r in new_effects if r['character_skill_key'] == new]
    assert actual == native, old
    orig_details = [r for r in read('character_skill_level_details')[1] if r['skill_key'] == old]
    assert [dict(r, skill_key=old) for r in details if r['skill_key'] == new] == orig_details
assert all(r['character_skill'].startswith('edh_heinrich_') for r in locks), 'Career locks must use the private skills'
assert not any(EXCLUDED & {source_nodes[r['item']]['character_skill_key']} for r in source_items
               if r['item'] in active and r['item'] in source_nodes)
guardian_effects = [r for r in new_effects if r['character_skill_key'] == skill_map[GUARDIAN]]
assert len(guardian_effects) == 1 and guardian_effects[0]['effect_key'] == 'wh2_dlc10_effect_ability_enable_guardian'

previous = BASE / 'edh_heinrich_custom_battle_v2.pack'
shutil.copy2(previous, PACK)
paths = [v['path'] for v in tables.values()] + [loc]
for path in paths:
    run('pack', 'add', '-p', PACK, '-t', SCHEMA, '-f', str(OUT / (path + '.tsv')) + ';' + path,
        stdout=subprocess.DEVNULL)
roundtrip = R / 'roundtrip'
run('pack', 'extract', '-p', PACK, '-t', SCHEMA, '-F', '/;' + str(roundtrip), stdout=subprocess.DEVNULL)
def raw_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))[2:]
for path in paths:
    assert raw_rows(OUT / (path + '.tsv')) == raw_rows(roundtrip / (path + '.tsv')), path
base_validation = json.loads((BASE / 'pack_validation.json').read_text())
for path in base_validation['payloads']:
    if path.startswith(('db/', 'text/')):
        assert raw_rows(BASE / 'roundtrip_final' / (path + '.tsv')) == raw_rows(roundtrip / (path + '.tsv')), path
    else:
        assert sha(BASE / 'roundtrip_final' / path) == sha(roundtrip / path), path

report = {
    'status': 'roundtrip_passed_pending_diagnostics', 'pack': str(PACK), 'sha256': sha(PACK),
    'previous_pack': str(previous), 'unit': SUBTYPE, 'skill_node_set': SET,
    'visible_skills': len(approved), 'active_nodes_including_native_background': len(active),
    'native_effect_rows_preserved': len(new_effects), 'native_level_details_preserved': len(details),
    'links': len(new_links), 'career_lock_rows': len(locks),
    'added_guardian': skill_map[GUARDIAN], 'guardian_unlock_rank': source_skills[GUARDIAN]['unlocked_at_rank'],
    'new_payloads': paths, 'base_payloads_preserved': len(base_validation['payloads']),
    'source_to_private_skill': skill_map, 'source_to_private_node': node_map,
    'campaign_recruitment_added': False, 'runtime_skill_tree_verified': False,
    'notes': ['Campaign tree is selected by agent subtype. Custom Battle uses a separate native skill progression.',
              'Mounted visuals are not part of this change; native mount ancillaries retained.']}
(R / 'pack_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
with (R / 'diagnostics.txt').open('w', encoding='utf8') as f:
    run('pack', 'diagnose', '-g', GAME, '-P', BASE / 'wh3-current.pak2', '-s', SCHEMA, '-p', PACK,
        stdout=f, stderr=subprocess.STDOUT)
print(json.dumps({k:v for k,v in report.items() if k not in ('source_to_private_skill','source_to_private_node')}, ensure_ascii=False, indent=2))
