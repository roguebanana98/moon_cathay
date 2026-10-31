"""Check the first compressed payload byte-for-byte, without decoding it."""
import hashlib
import lzma
import sys
from pathlib import Path
from inspect_esf import Reader

class Captured(Exception):
    pass

decompress = lzma.decompress
payloads = []
def capture(*args, **kwargs):
    payloads.append(decompress(*args, **kwargs))
    raise Captured()

lzma.decompress = capture
for filename in sys.argv[1:]:
    source = Path(filename)
    before = len(payloads)
    try:
        Reader(source.read_bytes()).parse()
    except Captured:
        pass
    assert len(payloads) == before + 1
    source.with_suffix('.raw.esf').write_bytes(payloads[-1])
    print(source.name, len(payloads[-1]), hashlib.sha256(payloads[-1]).hexdigest())
print('Decompressed payloads identical:', payloads[0] == payloads[1])
