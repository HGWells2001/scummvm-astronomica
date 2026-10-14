from pathlib import Path
import struct,re,hashlib,json,collections
root=Path(r'D:\astro'); out=Path('outputs/astronomica-cleanroom'); out.mkdir(exist_ok=True)
files=sorted(p for p in root.rglob('*') if p.is_file())
rows=[]
for p in files:
 b=p.read_bytes(); rows.append(dict(path=p.relative_to(root).as_posix(),size=len(b),sha256=hashlib.sha256(b).hexdigest(),prefix=b[:16].hex()))
(out/'inventory.json').write_text(json.dumps(rows,indent=2))
print('files',len(rows),'bytes',sum(r['size'] for r in rows),'extensions',collections.Counter(p.suffix.upper() for p in files))
for name in ['SETUP/ASTRO.EXE','PLACES/P0/MEGAFILE.HYP','PLACES/P1/MEGAFILE.HYP','PLACES/P2/MEGAFILE.HYP','PLACES/P3/MEGAFILE.HYP','PLACES/P29/MEGAFILE.HYP']:
 b=(root/name).read_bytes(); print('\nFILE',name,len(b),'head',b[:32].hex())
 if b[:2]==b'MZ':
  off=struct.unpack_from('<I',b,60)[0];print('executable header',hex(off),b[off:off+2]);
  strings=[{'offset':m.start(),'text':m.group().decode('ascii')} for m in re.finditer(rb'[ -~]{5,}',b)]
  (out/'exe-strings.json').write_text(json.dumps(strings,indent=2));print([x for x in strings if re.search('mega|place|hyper|borland|custom|game|\.cpp',x['text'],re.I)][:80])
 else:
  start=16+struct.unpack_from('<I',b,12)[0] if b[16:18]==b'BM' else 0
  print('after bitmap',hex(start),b[start:start+320].hex(' '))
  print('strings',[(hex(m.start()),m.group().decode()) for m in re.finditer(rb'[ -~]{6,}',b[start:])][:20])
