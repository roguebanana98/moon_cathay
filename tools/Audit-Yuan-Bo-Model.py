"""Read-only RMV2 v8 / DDS / skeleton-header audit of locally extracted assets.

Offsets checked against TheAssetEditor Shared/GameFiles/RigidModel sources.
Does not decode animation tracks or render the model.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'reference/local/yuan-bo-model'


def model(path):
    b = path.read_bytes()
    magic, version, count = struct.unpack_from('<4sII', b)
    assert magic == b'RMV2' and version == 8
    result = dict(path=path.relative_to(REF).as_posix(), bytes=len(b),
                  sha256=hashlib.sha256(b).hexdigest(), version=version,
                  skeleton=b[12:140].split(b'\0')[0].decode(), lods=[])
    for level in range(count):
        meshes, vb, ib, offset, distance, stored_level = struct.unpack_from('<4IfI', b, 140 + level*28)
        parts = []
        start = offset
        for _ in range(meshes):
            material, flags, size, vo, vertices, io, indices = struct.unpack_from('<HH5I', b, offset)
            bounds = struct.unpack_from('<6f', b, offset+24)
            fmt = struct.unpack_from('<H', b, offset+80)[0]
            assert indices % 3 == 0 and io + indices*2 == size
            stride = (io-vo)//vertices
            assert vo + stride*vertices == io
            idx = struct.unpack_from('<' + 'H'*indices, b, offset+io)
            assert max(idx) < vertices
            parts.append(dict(vertices=vertices, triangles=indices//3,
                              vertex_format=fmt, vertex_stride=stride,
                              material_id=material, bounds=list(bounds)))
            offset += size
        assert sum(p['vertices']*p['vertex_stride'] for p in parts) == vb
        assert sum(p['triangles']*6 for p in parts) == ib
        if level+1 < count:
            assert offset == struct.unpack_from('<I', b, 140+(level+1)*28+12)[0]
        else:
            assert offset == len(b)
        result['lods'].append(dict(level=stored_level, camera_distance=distance,
                                   mesh_count=meshes, vertices=sum(p['vertices'] for p in parts),
                                   triangles=sum(p['triangles'] for p in parts), parts=parts))
    return result


def skeleton(path):
    b = path.read_bytes()
    pos = 0
    def take(fmt):
        nonlocal pos
        value = struct.unpack_from('<'+fmt, b, pos)
        pos += struct.calcsize('<'+fmt)
        return value[0] if len(value) == 1 else value
    def string():
        nonlocal pos
        length = take('H')
        value = b[pos:pos+length].decode()
        pos += length
        return value
    version, unknown, fps = take('IIf')
    name = string()
    if version > 6:
        for _ in range(take('I')):
            string()
    duration = take('f')
    bones = [dict(id=i, name=string(), parent=take('i')) for i in range(take('I'))]
    assert all(-1 <= x['parent'] < len(bones) for x in bones)
    return dict(name=name, version=version, bone_count=len(bones), bones=bones)


textures = []
for path in sorted(REF.rglob('*.dds')):
    b = path.read_bytes()
    assert b[:4] == b'DDS '
    height, width = struct.unpack_from('<II', b, 12)
    textures.append(dict(path=path.relative_to(REF).as_posix(), width=width, height=height,
                         mipmaps=struct.unpack_from('<I', b, 28)[0],
                         fourcc=b[84:88].decode(), bytes=len(b)))
report = dict(date='2026-11-01', provenance='Installed vanilla packs; extracted by RPFM, read-only audit',
              models=[model(p) for p in sorted(REF.rglob('*.rigid_model_v2'))],
              skeleton=skeleton(REF/'animations/skeletons/humanoid01e.anim'), textures=textures)
out = ROOT/'reports/yuan-bo-model-audit.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
for m in report['models']:
    print(Path(m['path']).name, m['skeleton'], [(x['level'], x['vertices'], x['triangles']) for x in m['lods']])
print('Bones:', report['skeleton']['bone_count'])
print('Weapon bones:', [x for x in report['skeleton']['bones'] if 'weapon' in x['name'].lower()])
for t in textures:
    print(Path(t['path']).name, t['width'], t['height'], t['fourcc'], t['mipmaps'])
print(out)
