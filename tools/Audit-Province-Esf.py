"""Read-only inspection of province-related records; output stays in build."""
import json
import sys
from pathlib import Path
from inspect_esf import Reader, safe_json

source, output = map(Path, sys.argv[1:3])
root = Reader(source.read_bytes()).parse()
targets = {'cr_combi_region_' + x for x in ('long_vi','leilou','dai_loa','avauka','preenn')}
result = []
details = []
def visit(node, path):
    if not isinstance(node, dict) or 'groups' not in node:
        return
    path = path + [node['name']]
    scalar = [[x for x in group if not isinstance(x, dict)] for group in node['groups']]
    if 'PROVINCE' in node['name'] or (node['name'] == 'REGION' and any(x in targets for g in scalar for x in g if isinstance(x,str))):
        result.append({'path': path, 'version': node['version'], 'offset': node['offset'], 'values': scalar,
                       'children': [[x['name'] for x in g if isinstance(x,dict) and 'name' in x] for g in node['groups']]})
    for group in node['groups']:
        if node['name'] == 'PROVINCE_ARRAY' and any(x in ('cr_combi_province_primal_labyrinth','cr_combi_province_paradise_spires') for x in group if isinstance(x,str)):
            details.append({'path': path, 'group': group})
        for child in group:
            visit(child, path)
visit(root, [])
output.write_text(json.dumps(result, default=safe_json, indent=2), encoding='utf-8')
output.with_suffix('.details.json').write_text(json.dumps(details,default=safe_json,indent=2),encoding='utf-8')
print(f'Wrote {len(result)} records to {output}')
