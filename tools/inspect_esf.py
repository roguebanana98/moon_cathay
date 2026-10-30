"""Read-only CAAB/CBAB inspector. No write/encode API and no external packages.

Format reference: RPFM esf/{mod,cbab,utils}.rs (Frodo45127/rpfm).
This is a deliberately limited analysis reader, not a campaign editor.
"""
import struct
import lzma
import json
import sys
from pathlib import Path


class Reader:
    def __init__(self, data):
        self.data, self.p = data, 0

    def take(self, n):
        assert 0 <= n <= len(self.data) - self.p, (self.p, n)
        b = self.data[self.p:self.p+n]
        self.p += n
        return b

    def number(self, n, signed=False):
        return int.from_bytes(self.take(n), 'little', signed=signed)

    def var(self):
        n = 0
        for _ in range(5):
            b = self.number(1)
            n = (n << 7) | (b & 127)
            if b < 128:
                return n
        raise ValueError('Overlong variable integer')

    def primitive(self, t):
        constants = {0x12: True, 0x13: False, 0x14: 0, 0x15: 1, 0x19: 0, 0x1d: 0.0}
        if t in constants:
            return constants[t]
        sizes = {1:1,2:1,3:2,4:4,5:8,6:1,7:2,8:4,9:8,0x10:2,
                 0x16:1,0x17:2,0x18:3,0x1a:1,0x1b:2,0x1c:3,0x21:4,0x23:1,0x24:2,0x25:4}
        if t in sizes:
            return self.number(sizes[t], t in (2,3,4,5,0x10,0x1a,0x1b,0x1c))
        if t in (0xa,0xb,0xc,0xd):
            fmt = {0xa:'f',0xb:'d',0xc:'2f',0xd:'3f'}[t]
            v = struct.unpack('<'+fmt, self.take(struct.calcsize('<'+fmt)))
            return v[0] if len(v)==1 else v
        if t in (0xe,0xf):
            return self.strings[t][self.number(4)]
        if t == 0x26:
            b = self.number(1)
            result = self.take(b if b and b % 8 == 0 else 7).hex()
            if self.data[self.p:self.p+1] == b'\x9c': self.p += 1
            return {'unknown26': result}
        raise ValueError(f'Unsupported marker {t:x} at {self.p-1:x}')

    def node(self, root=False):
        offset = self.p
        t = self.number(1)
        if t & 128:
            if root or t & 32:
                idx, version = self.number(2), self.number(1)
            else:
                idx, version = ((t & 1)<<8) + self.number(1), (t & 30)>>1
            size = self.var()
            count = self.var() if t & 64 else 1
            end = self.p + size
            name = self.names[idx]
            # These branches are unrelated to ownership/character identity.
            # Their declared boundaries are checked, but their children are not decoded.
            if name == 'OLD_DIPLOMACY_MANAGER' or name.startswith('CAI_'):
                assert end <= len(self.data)
                self.p = end
                return {'name':name, 'version':version, 'offset':offset, 'skipped':True, 'groups':[]}
            groups = []
            for _ in range(count):
                if t & 64:
                    length = self.var()
                    stop = self.p + length
                else: stop = end
                group = []
                while self.p < stop: group.append(self.node())
                assert self.p == stop, (self.p, stop)
                groups.append(group)
            assert self.p == end, (self.p, end)
            return {'name':self.names[idx], 'version':version, 'offset':offset, 'groups':groups}
        if 0x41 <= t <= 0x5d:
            size = self.var()
            if t == 0x46: return self.take(size)
            end = self.p + size
            result = []
            while self.p < end: result.append(self.primitive(t-0x40))
            assert self.p == end
            return result
        return self.primitive(t)

    def parse(self):
        magic = self.number(4)
        assert magic in (0xabca,0xabcb), hex(magic)
        self.take(8)
        table_offset = self.number(4)
        self.p = table_offset
        self.names = [self.take(self.number(2)).decode('utf-8') for _ in range(self.number(2))]
        self.strings = {}
        for marker, encoding, width in ((0xe,'utf-16-le',2),(0xf,'utf-8',1)):
            values = {}
            for _ in range(self.number(4)):
                size = self.number(4 if magic == 0xabcb else 2)
                value = self.take(size*width).decode(encoding)
                values[self.number(4)] = value
            self.strings[marker] = values
        assert self.p == len(self.data) or not any(self.data[self.p:])
        self.p = 16
        root = self.node(True)
        assert self.p == table_offset
        for n in walk(root):
            if n['name'] == 'COMPRESSED_DATA':
                payload, info = n['groups'][0][:2]
                length, props = info['groups'][0][:2]
                raw = lzma.decompress(props + struct.pack('<Q', length) + payload, format=lzma.FORMAT_ALONE)
                assert len(raw) == length
                return Reader(raw).parse()
        return root


def walk(node):
    if isinstance(node, dict) and 'groups' in node:
        yield node
        for group in node['groups']:
            for child in group: yield from walk(child)


def safe_json(obj):
    if isinstance(obj, bytes): return {'bytes':len(obj), 'hex':obj.hex() if len(obj)<64 else None}
    raise TypeError(type(obj).__name__)


if __name__ == '__main__':
    source, destination = map(Path, sys.argv[1:3])
    root = Reader(source.read_bytes()).parse()
    names = {}
    selected = []
    for n in walk(root):
        names[n['name']] = names.get(n['name'],0)+1
        if n['name'] in ('FACTION','REGION','CHARACTER_DETAILS','SAVE_GAME_HEADER','CAMPAIGN_MODEL'):
            if n['name'] in ('REGION','CAMPAIGN_MODEL') or (n['name']=='FACTION' and 'cr_cth_agents_of_the_moon' not in n['groups'][0]):
                selected.append({**n, 'groups':[[x for x in g if not isinstance(x,dict)] for g in n['groups']]})
            else:
                selected.append(n)
    destination.write_text(json.dumps({'counts':names,'selected':selected},default=safe_json),encoding='utf-8')
    print(json.dumps(names,indent=2))
