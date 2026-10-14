"""Fresh inventory of original commands and event types, not a completion metric."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from astro_reader import parse,FormatError
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
custom={};events={};errors=[];hashes={};scenes=0
for path in sorted((a.root/'PLACES').glob('P*/MEGAFILE.HYP')):
    place=int(path.parent.name[1:]);data=path.read_bytes();hashes[str(place)]=hashlib.sha256(data).hexdigest()
    try:
        try:s=parse(data)
        except FormatError as e:
            tail=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e))
            if not tail:raise
            s=parse(data[:int(tail[2],16)])
    except (FormatError,struct.error) as e:
        errors.append(dict(place=place,error=str(e)));continue
    scenes+=1
    def visit(value,location):
        if isinstance(value,dict):
            if value.get('opcode')==23:
                ident=str(value['args'][0]);custom.setdefault(ident,[]).append(dict(place=place,location=location,args=value['args'],offset=value['offset']))
            for key,item in value.items():
                if key in ('mouse_in','mouse_out','drag') and item:
                    events.setdefault(key,[]).append(dict(place=place,location=location,commands=len(item)))
                visit(item,location+'/'+key)
        elif isinstance(value,list):
            for index,item in enumerate(value):visit(item,location+'/'+str(index))
    visit(s,'')
result=dict(scope='Original resource inventory; commands may already be supported depending on context',parsed=scenes,parse_errors=errors,
    custom_commands=custom,event_scripts=events,original_resource_sha256=hashes,
    help_file_sha256=hashlib.sha256((a.root/'HELP/ASTRONOM.HLP').read_bytes()).hexdigest())
a.out.write_text(json.dumps(result,indent=2))
print('Parsed',scenes,'errors',errors)
print('Custom ids:',sorted(map(int,custom)))
for key in ('22','33'):print('Custom',key,[(r['place'],r['args']) for r in custom.get(key,[])])
print('Event script counts:',{k:len(v) for k,v in events.items()})
