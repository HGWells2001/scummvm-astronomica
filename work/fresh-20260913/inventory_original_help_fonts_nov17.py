"""Measure original help font descriptions and standard NE font resources without execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct
w=Path(__file__).resolve().parent;r=w.parents[1];root=Path('D:/astro');read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
hlp=(root/'HELP/ASTRONOM.HLP').read_bytes();directory=read(r/'outputs/astronomica-cleanroom/evidence/help-directory.json');assert sha(hlp)==directory['source_sha256']
entry=directory['streams']['|FONT'];data=hlp[entry['offset']+9:entry['offset']+9+entry['used']]
names,count,name_at,font_at=struct.unpack_from('<4H',data);assert(names,count,name_at,font_at)==(93,16,8,1868)and len(data)==font_at+11*count
styles=[]
for i in range(count):
 record=data[font_at+11*i:font_at+11*(i+1)];index=int.from_bytes(record[3:5],'little');assert index<names
 name=data[name_at+20*index:name_at+20*(index+1)].split(b'\0')[0].decode('cp1252')
 styles.append(dict(index=i,flags=record[0],half_points=record[1],family=record[2],face=name,record_sha256=sha(record)))
super_styles=[s for s in styles if s['face']=='Arial Super'];assert len(super_styles)==1 and super_styles[0]['index']==13 and super_styles[0]['half_points']==22
exe=(root/'SETUP/ASTRO.EXE').read_bytes();assert exe[:2]==b'MZ';ne=struct.unpack_from('<I',exe,0x3c)[0];assert exe[ne:ne+2]==b'NE'
table=ne+struct.unpack_from('<H',exe,ne+0x24)[0];end=ne+struct.unpack_from('<H',exe,ne+0x26)[0];assert table+2<=end<=len(exe)
shift=struct.unpack_from('<H',exe,table)[0];assert shift<=16;at=table+2;types=[]
while True:
 assert at+2<=end;kind=struct.unpack_from('<H',exe,at)[0];at+=2
 if not kind:break
 assert at+6<=end;number,reserved=struct.unpack_from('<HI',exe,at);at+=6;assert at+12*number<=end
 for n in range(number):
  offset,length,flags,identifier,handle,usage=struct.unpack_from('<6H',exe,at);at+=12
  assert(offset<<shift)+(length<<shift)<=len(exe)
 types.append(dict(type_id=kind,count=number))
standalone=sorted(p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p.suffix.casefold()in{'.ttf','.otf','.fon','.fnt'})
j=dict(status='ORIGINAL_HELP_FONT_METADATA_OBSERVATION_COMPLETE',at=datetime.now(timezone.utc).isoformat(),help_sha256=sha(hlp),original_exe_sha256=sha(exe),styles=styles,exponent_style=super_styles[0],standard_ne_font_resources=sum(t['count']for t in types if t['type_id']==0x8008),standard_ne_font_directory_resources=sum(t['count']for t in types if t['type_id']==0x8007),standalone_font_files=standalone,engine_modified=False,limits=['Raw font13 names Arial Super at11points; no inference about original WinHelp font mapping or pixel metrics','No standalone font files does not exclude compressed installer containers,custom resource payloads or fonts supplied by Windows','Standard NE resource inventory only; no original program or installer executed','Typography acceptance A08 remains partial; no speculative Unicode or font substitution applied'])
(w/'original-help-font-metadata-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],j['exponent_style'],j['standard_ne_font_resources'],len(standalone))
