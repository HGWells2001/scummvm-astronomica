"""Extract condition dispatch tables and usage from original Astronomica data."""
from pathlib import Path
import argparse, collections, hashlib, json, struct
from astro_reader import parse, FormatError

def analyze(root):
    exe = (root / 'SETUP/ASTRO.EXE').read_bytes()
    if hashlib.sha256(exe).hexdigest() != 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e':
        raise ValueError('Unknown executable')
    tables = {}
    # Segment 15 base, checked against the original NE segment table.
    ne = struct.unpack_from('<I', exe, 0x3c)[0]
    segtab = ne + struct.unpack_from('<H', exe, ne + 0x22)[0]
    shift = struct.unpack_from('<H', exe, ne + 0x32)[0]
    base = struct.unpack_from('<H', exe, segtab + 14 * 8)[0] << shift
    for name, offset, count in [('scope',0x1862,4),('global_comparison',0x184a,4),('local_comparison',0x1832,4),('assignment_scope',0x1820,3),('addition_scope',0x17a2,3)]:
        tables[name] = [dict(value=struct.unpack_from('<i',exe,base+offset+i*4)[0], target=f'15:{struct.unpack_from("<H",exe,base+offset+count*4+i*2)[0]:04x}') for i in range(count)]
    counts = collections.Counter(); scopes = collections.Counter(); comparisons = collections.Counter()
    rejected = {}; local_count = 0; ids = []
    def scripts(scene):
        yield from scene['scripts']
        for s in scene['sprites']:
            for key in ['click','drag','mouse_in','mouse_out']:
                yield s.get(key, [])
        for r in scene['mouse_rects']:
            for key in ['click','mouse_in','mouse_out']:
                yield r.get(key, [])
    for path in sorted((root/'PLACES').glob('P*/MEGAFILE.HYP')):
        try: scene = parse(path.read_bytes())
        except FormatError as error:
            rejected[path.parent.name] = str(error); continue
        local_count += sum(c[0] == 1 for c in scene['conditions'])
        for script in scripts(scene):
            for c in script:
                if c['opcode'] in (31,32,42,45,46): counts[c['opcode']] += 1
                if c['opcode'] in (31,32,46):
                    scopes[c['args'][0]] += 1; ids.append(c['args'][1])
                if c['opcode'] == 31: comparisons[c['args'][4]] += 1
    return dict(source='Original ASTRO.EXE and strictly parsed original MEGAFILE.HYP files', tables=tables, opcode_counts=counts, scopes=scopes, comparisons=comparisons, id_min=min(ids), id_max=max(ids), local_declarations=local_count, excluded_scenes=rejected)

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    result=analyze(args.root); args.out.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
