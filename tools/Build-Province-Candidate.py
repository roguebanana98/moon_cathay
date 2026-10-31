"""Build a local, experimental IEE startpos patch; never deploys or edits inputs.

Byte-preserves all records outside the explicitly selected records and their
length headers. Locked to the inspected dependency payload, not a general editor.
"""
import hashlib
import json
import lzma
import struct
from pathlib import Path
from inspect_esf import Reader, walk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/province-edit'
EXPECTED = '0621c95fa5008f18930ec03ceed1e6010274d1d6c40ada848680c217faeda2c2'

def var(n):
    parts = [n & 127]
    while n > 127:
        n >>= 7
        parts.append((n & 127) | 128)
    return bytes(reversed(parts))

class Document:
    def __init__(self, data):
        self.data = data
        self.r = r = Reader(data)
        magic = r.number(4)
        assert magic in (0xabca, 0xabcb)
        r.take(8)
        self.table = r.number(4)
        r.p = self.table
        r.names = [r.take(r.number(2)).decode('utf-8') for _ in range(r.number(2))]
        r.strings = {}
        self.added_strings = []
        self.magic = magic
        for marker, encoding, width in ((14,'utf-16-le',2),(15,'utf-8',1)):
            values = {}
            if marker == 15:
                self.ascii_count_offset = r.p
            for _ in range(r.number(4)):
                size = r.number(4 if magic == 0xabcb else 2)
                value = r.take(size * width).decode(encoding)
                values[r.number(4)] = value
            r.strings[marker] = values
        self.ascii_end = r.p

    def add_string(self, value):
        if value in self.r.strings[15].values():
            return self.string(value)
        index = max(self.r.strings[15]) + 1
        self.r.strings[15][index] = value
        self.added_strings.append((index,value))
        return self.string(value)

    def header(self, start):
        r = self.r
        r.p = start
        t = r.number(1)
        assert t & 128
        if start == 16 or t & 32:
            idx, version = r.number(2), r.number(1)
        else:
            idx, version = ((t & 1) << 8) + r.number(1), (t & 30) >> 1
        prefix = self.data[start:r.p]
        length = r.var()
        count = r.var() if t & 64 else None
        return prefix, count, r.p, r.p + length, r.names[idx], version

    def decode(self, start):
        self.r.p = start
        value = self.r.node(start == 16)
        return value, self.r.p

    def children(self, start):
        prefix, count, pos, end, name, version = self.header(start)
        assert count is None, name
        children = []
        while pos < end:
            value, stop = self.decode(pos)
            children.append((pos, stop, value))
            pos = stop
        assert pos == end
        return children

    def record(self, start, body, count=None):
        prefix, old_count, _, _, _, _ = self.header(start)
        assert (count is None) == (old_count is None)
        return prefix + var(len(body)) + (var(count) if count is not None else b'') + body

    def string(self, value):
        ids = [k for k,v in self.r.strings[15].items() if v == value]
        assert len(ids) == 1, value
        return b'\x0f' + struct.pack('<I', ids[0])

    def rewrite(self, patches):
        """Recalculate enclosing sizes, retaining every other byte verbatim."""
        used = set()
        def node(start):
            t = self.data[start]
            if t & 128:
                prefix, count, pos, end, name, version = self.header(start)
                if start in patches:
                    used.add(start)
                    return patches[start], end
                if not any(start < p < end for p in patches):
                    return self.data[start:end], end
                if count is None:
                    body = sequence(pos, end)
                else:
                    groups = []
                    for _ in range(count):
                        self.r.p = pos
                        size = self.r.var()
                        begin = self.r.p
                        stop = begin + size
                        group = sequence(begin, stop)
                        groups.append(var(len(group)) + group)
                        pos = stop
                    assert pos == end
                    body = b''.join(groups)
                return self.record(start, body, count), end
            _, end = self.decode(start)
            if start in patches:
                used.add(start)
                return patches[start], end
            return self.data[start:end], end
        def sequence(pos, end):
            chunks = []
            while pos < end:
                chunk, pos = node(pos)
                chunks.append(chunk)
            assert pos == end
            return b''.join(chunks)
        body, end = node(16)
        assert end == self.table and used == set(patches), (used, patches.keys())
        table = self.data[self.table:]
        if self.added_strings:
            count_pos = self.ascii_count_offset
            old_count = int.from_bytes(self.data[count_pos:count_pos+4],'little')
            entries = []
            for index,value in self.added_strings:
                encoded = value.encode('utf-8')
                entries.append(struct.pack('<I' if self.magic==0xabcb else '<H',len(encoded))+encoded+struct.pack('<I',index))
            table = (self.data[self.table:count_pos]+struct.pack('<I',old_count+len(entries))+
                     self.data[count_pos+4:self.ascii_end]+b''.join(entries)+self.data[self.ascii_end:])
        return self.data[:12] + struct.pack('<I', 16 + len(body)) + body + table

def main():
    raw = (OUT / 'roundtrip-input.raw.esf').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'Dependency payload changed'
    doc = Document(raw)
    patches = {}
    changes = []
    # Keep building ID, tier, health, owner, construction state, port, and all slots.
    # Only use a region-scoped copy of the existing primary building definition.
    primary_offset = 59304987
    primary, _ = doc.decode(primary_offset)
    assert primary['name']=='BUILDING_BASE' and primary['version']==1
    assert primary['groups'][0][:2]==[357,'wh3_main_cth_settlement_minor_2']
    children = doc.children(primary_offset)
    new_key = doc.add_string('mc_long_vi_cth_settlement_2')
    patches[primary_offset] = doc.record(primary_offset,b''.join(new_key if i==1 else raw[a:b] for i,(a,b,_) in enumerate(children)))
    for offset, province, old_capital, old_members, capital, members in (
        (2104977, 'paradise_spires', 'avauka', ['preenn','avauka'], 'dai_loa', ['preenn','avauka','dai_loa']),
        (2107467, 'primal_labyrinth', 'dai_loa', ['long_vi','dai_loa','leilou'], 'long_vi', ['long_vi','leilou']),
    ):
        node, _ = doc.decode(offset)
        key = 'cr_combi_province_' + province
        region = lambda name: 'cr_combi_region_' + name
        assert node['name'] == 'PROVINCE_DATA' and node['version'] == 0
        group = node['groups'][0]
        assert group[0] == key and group[2] == region(old_capital)
        assert group[1]['groups'] == [[region(x)] for x in old_members]
        array = group[1]['offset']
        entries = [doc.string(region(x)) for x in members]
        array_bytes = doc.record(array, b''.join(var(len(e))+e for e in entries), len(entries))
        patches[offset] = doc.record(offset, doc.string(key)+array_bytes+doc.string(region(capital)))
        changes.append({'province': key, 'capital': region(capital), 'members': list(map(region,members))})

    # The existing Moon faction's per-province ownership lists and local capital.
    # No manager IDs, faction IDs, owners or faction capitals are changed.
    for offset, manager_id, old_members, members, old_capital, capital in (
        (65040688, 193, [251], [251,254], 251,254),
        (65809282, 304, [153,254,404], [153,404], 254,153),
    ):
        node, _ = doc.decode(offset)
        assert node['name'] == 'FACTION_PROVINCE_MANAGER' and node['version'] == 1
        children = doc.children(offset)
        scalars = [(a,b,v) for a,b,v in children if not isinstance(v,dict)]
        assert [v for _,_,v in scalars[:3]] == [manager_id,205,old_members]
        assert scalars[7][2] == old_capital
        replacements = {
            scalars[2][0]: b'\x47' + var(2*len(members)) + struct.pack('<'+'H'*len(members),*members),
            scalars[7][0]: b'\x08' + struct.pack('<I',capital),
        }
        body = b''.join(replacements.get(a,raw[a:b]) for a,b,_ in children)
        patches[offset] = doc.record(offset, body)
    edited = doc.rewrite(patches)
    (OUT / 'province-candidate.raw.esf').write_bytes(edited)
    # Verify edited records by walking the independently implemented reader.
    result = Reader(edited).parse()
    actual = {}
    managers = {}
    long_vi = None
    for n in walk(result):
        if n['name']=='REGION' and n['groups'][0][1]=='cr_combi_region_long_vi':
            long_vi = n
        if n['name'] == 'PROVINCE_DATA':
            g = n['groups'][0]
            if g[0] in {x['province'] for x in changes}:
                actual[g[0]] = {'province':g[0], 'capital':g[2], 'members':[x[0] for x in g[1]['groups']]}
        if n['name'] == 'FACTION_PROVINCE_MANAGER':
            g = [v for v in n['groups'][0] if not isinstance(v,dict)]
            if g[0] in (193,304):
                managers[g[0]] = (g[2],g[7])
    assert actual == {x['province']:x for x in changes}
    assert managers == {193:([251,254],254),304:([153,404],153)}
    assert long_vi is not None
    baseline,_ = doc.decode(59304892)
    def clean(x):
        if isinstance(x,dict): return {k:clean(v) for k,v in x.items() if k!='offset'}
        if isinstance(x,list): return [clean(v) for v in x]
        return x
    baseline_primary = next(n for n in walk(baseline) if n['name']=='BUILDING_BASE' and n['groups'][0][0]==357)
    baseline_primary['groups'][0][1] = 'mc_long_vi_cth_settlement_2'
    assert clean(long_vi)==clean(baseline), 'Unexpected change to Long Vi buildings, port, slots or other state'
    assert [n['groups'][0][1] for n in walk(long_vi) if n['name']=='BUILDING_BASE']==['mc_long_vi_cth_settlement_2','wh3_main_cth_port_1']
    del result
    # Reuse the original outer ESF and compression properties.
    source = (OUT / 'roundtrip-input.esf').read_bytes()
    outer = Document(source)
    root, _ = outer.decode(16)
    compressed = [n for n in walk(root) if n['name']=='COMPRESSED_DATA']
    assert len(compressed)==1
    c = compressed[0]
    children = outer.children(c['offset'])
    payload_start = children[0][0]
    info = children[1][2]
    info_children = outer.children(info['offset'])
    original_length, props = info['groups'][0][:2]
    assert original_length == len(raw)
    prop = props[0]
    lc, remainder = prop % 9, prop // 9
    lp, pb = remainder % 5, remainder // 5
    filters = [{'id':lzma.FILTER_LZMA1,'dict_size':int.from_bytes(props[1:5],'little'),'lc':lc,'lp':lp,'pb':pb}]
    packed = lzma.compress(edited, format=lzma.FORMAT_RAW, filters=filters)
    assert lzma.decompress(packed,format=lzma.FORMAT_RAW,filters=filters)==edited
    encoded = outer.rewrite({payload_start:b'\x46'+var(len(packed))+packed,
                             info_children[0][0]:b'\x08'+struct.pack('<I',len(edited))})
    destination = OUT / 'province-candidate.esf'
    destination.write_bytes(encoded)
    report = {'status':'experimental_static_candidate_not_game_tested', 'source_payload_sha256':EXPECTED,
              'output_sha256':hashlib.sha256(encoded).hexdigest(), 'changes':changes,
              'modified_record_offsets':list(patches),
              'long_vi':{'total_slots_target':8,'primary_building':'mc_long_vi_cth_settlement_2','port_preserved':'wh3_main_cth_port_1','all_other_region_data_preserved':True},
              'limitations':['Long Vi eight-slot unlocks require accompanying custom-building DB tables','Other settlement infrastructure unchanged',
                             'AI cached data not audited','No game/load/end-turn test','Not deployed; no live save migration']}
    (OUT/'candidate-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
