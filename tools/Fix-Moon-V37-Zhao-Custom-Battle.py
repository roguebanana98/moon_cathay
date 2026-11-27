"""Remove duplicate Custom Battle sources without changing Zhao's campaign design."""
import csv, hashlib, json, shutil, struct, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-v37-zhao-cb-fix'
O.mkdir(parents=True, exist_ok=True)
SOURCE = R / 'build/moon-v36-zhao-jade/mc_moonshadow_heroes_v36_zhao_jade.pack'
PACK = O / 'mc_moonshadow_heroes_v37_zhao_cb_fix.pack'
REF = R / 'reference/local/moon-v36-roundtrip'
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
M = json.loads((R / 'build/moon-v36-zhao-jade/design-manifest.json').read_text())

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        a = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return a[:2], [dict(zip(a[0], row)) for row in a[2:]]

def inventory(p):
    with p.open('rb') as f:
        assert f.read(4) == b'PFH5'
        flags, dc, ds, count, fs, stamp = struct.unpack('<6I', f.read(24))
        deps, index = f.read(ds), f.read(fs)
        pos, entries = 0, []
        for _ in range(count):
            size, compressed = struct.unpack_from('<IB', index, pos)
            assert not compressed
            pos += 5
            end = index.index(0, pos)
            name = index[pos:end].decode().replace('\\', '/')
            entries.append((name, size))
            pos = end + 1
        assert pos == len(index)
        result = {}
        for name, size in entries:
            assert name not in result
            h, left = hashlib.sha256(), size
            while left:
                block = f.read(min(left, 8 * 1024 * 1024))
                assert block
                h.update(block)
                left -= len(block)
            result[name] = (size, h.hexdigest())
        assert f.tell() == p.stat().st_size
        return deps, result

assert sha(SOURCE) == '2584f38b44cf2e9d8f9f4feba87a809cfbfc187dd17f71d638292c2d905087e3'
assert not PACK.exists(), 'Preserve completed candidates; use a new version.'
units = {row['key'] for row in M['land_units']}
spell_abilities = set(M['ability_map'].values())
paths, patches = [], {}
for table in ['land_units_to_unit_abilites_junctions', 'units_custom_battle_permissions']:
    internal = 'db/' + table + '_tables/zzzz_mc_mooncourt_lord'
    headers, rows = read(REF / (internal + '.tsv'))
    original = [dict(row) for row in rows]
    if table == 'land_units_to_unit_abilites_junctions':
        # Native casters expose their spells through the lore group. Listing the
        # same abilities directly as well creates a second CB selection source.
        rows = [row for row in rows if not (row['land_unit'] in units and row['ability'] in spell_abilities)]
        assert len(original) - len(rows) == 39
        assert not any(row['ability'] in spell_abilities for row in rows)
    else:
        # Different general_uniform values split one foot/mount family into two
        # cards. Native lords also permit an empty uniform, resolving each mount
        # through its unit_variants row. Keep the approved distinct sword VMDs.
        for row in rows:
            assert row['unit'] in units
            row['general_uniform'] = ''
        for faction in {row['faction'] for row in rows}:
            family = [row for row in rows if row['faction'] == faction]
            assert len(family) == 3
            assert len({(row['set_piece_character'], row['general_uniform'], row['general_portrait']) for row in family}) == 1
    dest = O / (internal + '.tsv')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None, lineterminator='\n').writerows(headers + [[row[k] for k in headers[0]] for row in rows])
    paths.append(internal)
    patches[table] = dict(before=len(original), after=len(rows))

def cli(*args):
    p = subprocess.run([C['rpfm'], '-g', 'warhammer_3', *map(str, args)], capture_output=True, text=True, encoding='utf-8')
    with (O / 'build.log').open('a', encoding='utf-8') as f:
        f.write(p.stdout + p.stderr)
    assert p.returncode == 0, p.stdout + p.stderr

shutil.copy2(SOURCE, PACK)
cli('pack', 'add', '-p', PACK, '-t', C['schema'], '-f', *[str(O / (p + '.tsv')) + ';' + p for p in paths])
roundtrip = R / 'reference/local/moon-v37-roundtrip'
cli('pack', 'extract', '-p', PACK, '-t', C['schema'], '-F', 'db;' + str(roundtrip))
for p in paths:
    assert read(O / (p + '.tsv')) == read(roundtrip / (p + '.tsv'))
deps, before = inventory(SOURCE)
newdeps, after = inventory(PACK)
assert deps == newdeps and before.keys() == after.keys()
changed = [p for p in before if before[p] != after[p]]
assert set(changed) == set(paths)
# Models, mounts, migration script, skill tree, stats, effects, VFX and Jade are
# all outside the two allowed DB payloads and must remain byte-identical.
report = dict(pack=str(PACK), sha256=sha(PACK), bytes=PACK.stat().st_size,
              source=str(SOURCE), source_sha256=sha(SOURCE), changed_payloads=changed,
              patches=patches, roundtrip_equal=True, all_other_payloads_byte_identical=True,
              no_direct_spell_passive_duplicates=True, cb_family_uniform_consistent=True,
              runtime_verified=False, mounted_uniform_runtime_review_required=True)
(O / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
