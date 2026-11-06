"""Inventory original HYP syntax and branch references, without claiming execution."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,re
from astro_reader import parse,FormatError

ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
here=Path(__file__).resolve().parent
original_inventory={row['path']:row['sha256']for row in json.loads((here/'inventory.json').read_text())}
layout=here/'opcode-layout.json';reader=here/'astro_reader.py'
def scripts(scene):
    for i,commands in enumerate(scene['scripts']):yield 'entry/%d'%i,commands
    for kind,key in [('sprite','sprites'),('rectangle','mouse_rects')]:
        for i,obj in enumerate(scene[key]):
            for trigger in('click','drag','mouse_in','mouse_out'):
                if obj.get(trigger):yield '%s/%d/%s'%(kind,i+1,trigger),obj[trigger]
def arguments(args):
    # Do not publish original text bodies or derived image/media data.
    return [dict(text_length=len(v),text_sha256=sha(v.encode('cp1252',errors='replace')))if isinstance(v,str)else v for v in args]
rows=[];commands=[];edges=[];failures=[];tails=[];opcode_counts=collections.Counter();custom_counts=collections.Counter()
for path in sorted((a.root/'PLACES').glob('P*/MEGAFILE.HYP'),key=lambda p:int(p.parent.name[1:])):
    data=path.read_bytes();relative=path.relative_to(a.root).as_posix();pin=sha(data)
    assert original_inventory.get(relative)==pin,('Original input changed or missing baseline',relative)
    tail=0
    try:scene=parse(data)
    except FormatError as error:
        match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error))
        if not match:failures.append(dict(path=relative,sha256=pin,error=str(error)));continue
        end=int(match[2],16);tail=len(data)-end;scene=parse(data[:end])
        tails.append(dict(path=relative,offset=end,bytes=tail,sha256=sha(data[end:]),meaning='Retained opaque tail, not silently discarded or classified as executable syntax'))
    place=int(path.parent.name[1:]);scene_scripts=[]
    for direction,destination in zip(('left','forward','right'),scene['navigation']or[]):
        if destination>0:edges.append(dict(source=place,kind='navigation',direction=direction,destination=destination,execution_verified=False))
    for name,body in scripts(scene):
        branch_markers=[];indices=[]
        for i,c in enumerate(body):
            key='P%d/%s/%d'%(place,name,i);opcode_counts[c['opcode']]+=1
            item=dict(id=key,scene=place,trigger=name,index=i,file_offset=c['offset'],opcode=c['opcode'],args=arguments(c['args']),delay_ms=c['delay'],execution_verified=False)
            if c['opcode']==23 and c['args']:custom_counts[str(c['args'][0])]+=1
            if c['opcode']in(31,42,45):branch_markers.append(dict(command=key,index=i,opcode=c['opcode']))
            if c['opcode']==5:
                edges.append(dict(source=place,kind='script_place_operand',command=key,file_offset=c['offset'],operands=arguments(c['args']),execution_verified=False,conditional=None,delay_ms=c['delay']))
            indices.append(len(commands));commands.append(item)
        scene_scripts.append(dict(trigger=name,command_indices=indices,literal_condition_markers=branch_markers,condition_link_semantics_verified=False))
    rows.append(dict(scene=place,path=relative,sha256=pin,size=len(data),parsed_bytes=scene['consumed'],opaque_tail_bytes=tail,mode=scene['mode'],layers=scene['layers'],sprite_count=len(scene['sprites']),rectangle_count=len(scene['mouse_rects']),entry_script_count=len(scene['scripts']),movies=scene['movies'],conditions=scene['conditions'],scripts=scene_scripts,execution_verified=False))
known={row['scene']for row in rows}
for edge in edges:
    if edge['kind']=='navigation':edge['destination_asset_present']=edge['destination']in known
result=dict(status='ORIGINAL_HYP_SYNTACTIC_BRANCH_INVENTORY_ONLY',scheme='astronomica-hyp-syntax-v1',created_at=datetime.now(timezone.utc).isoformat(),reader_sha256=sha(reader.read_bytes()),opcode_layout_sha256=sha(layout.read_bytes()),source_inventory_sha256=sha((here/'inventory.json').read_bytes()),summary=dict(original_files=len(rows)+len(failures),parsed_scenes=len(rows),failures=len(failures),commands=len(commands),scripts=sum(len(row['scripts'])for row in rows),condition_tests=opcode_counts[31],else_tokens=opcode_counts[45],condition_ends=opcode_counts[42],delayed_commands=sum(c['delay_ms']>0 for c in commands),script_place_operands=sum(e['kind']=='script_place_operand'for e in edges),navigation_edges=sum(e['kind']=='navigation'for e in edges),opaque_tails=len(tails),executed_branch_count=None),opcode_counts=dict(sorted(opcode_counts.items())),custom_selector_counts=dict(sorted(custom_counts.items(),key=lambda item:int(item[0]))),scenes=rows,commands=commands,route_references=edges,opaque_tails=tails,failures=failures,limits=['Syntactic denominator only; no reachability, alternative route completeness or playability claim','Literal31/45/42markers are inventoried without imposing nested-if semantics; the engine uses a single last-condition pointer and original link semantics need separate evidence','Custom native callbacks, timeouts, failure choices and dynamically generated destinations are not enumerated by HYP operands alone','Every command begins execution_verified=false; no component test is silently attributed to individual source branches','Opaque tails retained by hash; no historical purpose inferred','Does not complete fixed acceptance gateA03; no whole-game percentage'])
assert len(commands)==len({c['id']for c in commands})
assert all(c['file_offset']<next(row['parsed_bytes']for row in rows if row['scene']==c['scene'])for c in commands)
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary']))
