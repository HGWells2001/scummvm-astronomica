"""Fresh static P522 save inventory; no game, callback or decoder execution."""
from pathlib import Path
import argparse,collections,hashlib,json,sys
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent
cleanroom=here if (here/'astro_reader.py').is_file() else here.parents[2]/'outputs/astronomica-cleanroom'
sys.path.insert(0,str(cleanroom))
from astro_reader import parse
ap=argparse.ArgumentParser()
ap.add_argument('root',type=Path)
ap.add_argument('--out',type=Path,default=here/'evidence/p522-save-original.json')
a=ap.parse_args()
source=a.root/'PLACES/P522/MEGAFILE.HYP'
raw=source.read_bytes();scene=parse(raw)
assert scene['size']==scene['consumed']==483379
assert scene['mode']==0 and scene['layers']==1 and len(scene['sprites'])==18
assert len(scene['scripts'])==11 and not scene['movies'] and not scene['mouse_rects']
assert scene['conditions']==[[1,0,8,2,1,4],[1,1,8,0,0,8]]
assert [s['clone'] for s in scene['sprites']]==[-1]*10+[10]*3+[-1]*5
assert [len(s.get('frames',[])) for s in scene['sprites']]==[2]*8+[12,10,0,0,0,2,11,11,1,1]
sprites=[]
for i,s in enumerate(scene['sprites']):
    owner=i;seen=set()
    while scene['sprites'][owner]['clone']!=-1:
        assert owner not in seen;seen.add(owner)
        parent=scene['sprites'][owner]['clone']-1
        assert 0<=parent<owner;owner=parent
    frames=scene['sprites'][owner]['frames']
    row={k:v for k,v in s.items() if k!='frames'}
    row.update(id=i+1,frame_owner=owner+1,frame_count=len(frames),
               dimensions=sorted({(f[0]['width'],f[0]['height']) for f in frames}))
    sprites.append(row)
assert [s['frame_count'] for s in sprites]==[2]*8+[12]+[10]*4+[2,11,11,1,1]
assert [s['xy'] for s in sprites[9:13]]==[[160,404],[168,404],[177,404],[186,404]]
assert [s['id'] for s in sprites if s['auto_frame']]==[15,16]
assert all(s['frame_data']==[80,1,0] for s in sprites if s['auto_frame'])
assert not any(s['auto_move'] or s['drag_enabled'] or s['mouse_in'] or s['mouse_out'] for s in sprites)
commands=[]
def walk(v,path):
    if isinstance(v,dict):
        if 'opcode' in v:commands.append(dict(path=path,**v))
        for k,x in v.items():walk(x,path+'/'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(scene,'scene')
counts=collections.Counter(c['opcode'] for c in commands)
assert len(commands)==69 and not counts[20] and not counts[39] and not counts[49]
custom15=[c for c in commands if c['opcode']==23 and c['args'][0]==15]
assert sorted(c['args'] for c in custom15)==[[15,0,15,0,0,0],[15,0,16,106,53,0],[15,0,17,0,0,0],[15,1,0,0,0,0]]
poll=scene['scripts'][0][-1]
assert poll['opcode']==41 and poll['args']==[0] and poll['delay']==200
choices=[]
for id in range(5,9):
    click=scene['sprites'][id-1]['click']
    assign=[c for c in click if c['opcode']==32]
    assert len(assign)==1 and assign[0]['args']==[1,0,id-4]
    frames=[c['args'] for c in click if c['opcode']==15]
    assert frames==[[target,int(target==id)] for target in range(5,9)]
    choices.append(dict(control=id,local0=id-4,frames=frames))
assert [c['args'] for c in scene['scripts'][1] if c['opcode']==15]==[[10,1]]
assert [[c['args'] for c in scene['scripts'][i] if c['opcode']==15] for i in range(1,5)]==[[[10,1]],[[11,9]],[[12,9]],[[13,1]]]
assert sprites[14]['dimensions']==[(54,52)] and sprites[15]['dimensions']==[(40,40)] and sprites[16]['dimensions']==[(43,25)]
def code_reference(name,anchors):
    p=cleanroom/'engine/astronomica'/name;data=p.read_bytes();lines=data.decode().splitlines()
    return dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),
                anchors=[dict(text=needle,line=next(i+1 for i,l in enumerate(lines) if needle in l)) for needle in anchors])
references=[
 code_reference('sprites.h',['struct ProbeMotion {']),
 code_reference('sprites.cpp',['void configureProbe(','void launchProbe(','bool advanceProbe(']),
 code_reference('astronomica.cpp',['_probe = ProbeMotion();','void AstronomicaEngine::onProbe(','advanceProbe(_scene,','_probe.expired)']),
 code_reference('script.cpp',['else if (c.args[0] == 15) {','_probeHandler->onProbe(c.args[1],c.args[2]);','void ScriptRunner::exportSettledValues(']),
 code_reference('resource.h',['uint32 frameSince','uint32 moveSince','int32 orbitSideX'])]
motion=cleanroom/'probe_p522_motion.py'
report=dict(date='2026-10-21',status='PASS',evidence_id='p522-save-original-static-20261021',
 scope='Fresh original resource/static source inventory only; no native run, callback execution or save implementation',
 source=dict(path=str(source),size=len(raw),sha256=hashlib.sha256(raw).hexdigest()),
 conditions=scene['conditions'],initial_values=[c[3] for c in scene['conditions']],
 sprites=sprites,programs=scene['scripts'],sounds=scene['sounds'],intro_sound_id=scene['intro_sound_id'],
 command_count=len(commands),opcode_counts={str(k):v for k,v in sorted(counts.items())},commands=commands,
 custom15=custom15,choices=choices,recurring_program=poll,movies=[],external_picture_commands=0,
 source_references=references,
 prior_original_callback_probe=dict(path=str(motion),sha256=hashlib.sha256(motion.read_bytes()).hexdigest(),
   consulted_as_text_only=True,addresses=['3:0b2b Earth','3:0d75 Mars','3:0e52 probe','4:32c4 launch custom15'],
   prior_probe_assertions_not_rerun=['Calendar reaches2003 and exits388','Five special launch windows and one failed launch','Collision uses the precommit rectangle; Mars correction and retained caller-computed point']),
 observable_motion_fields=dict(ProbeMotion=['year','yearArmed','specialHit','flying','expired','widths[3]','heights[3]'],
   sprite_fields=['selectedFrame','visible','x/y','renderX/renderY','frameSince','moveSince','autoFrame/autoMove','standardMotion','moveDX/moveDY','orbitMotion','orbitSideX/orbitSideY','frameFirst/frameLast','frameData[3]','moveData[5]','clickEnabled'],
   configured_motion_period_ms=30,serialized_frame_period_ms=80,recurring_poll_ms=200,
   bitmap_dimensions=[[54,52],[40,40],[43,25]]),
 requirements=['Treat inactive flight and pending-script idleness separately; the200ms self-poll persists after startup',
 'Preserve active orbit/frame phase, all eighteen own mutable sprite records and the complete ProbeMotion flags/year; hidden probe still has ordinary delta movement',
 'Preserve both declared locals with widths/known flags, unknown retained values, globals, RNG, clock/count, dormant variant state and cross-puzzle comet phase',
 'Do not rerun custom15 setup to restore: configureProbe17 resets calendar/flags and all setup changes positions/motion',
 'Define and validate the exact allowed recurring poll continuation/epoch; do not silently discard it or reset its delay at load',
 'Preflight original asset geometry and restore callback identities from trusted scene logic rather than serialized addresses',
 'Compare no-flight, failed-return and in-flight states; all four choices; month/year edges; sticky specialHit; original success and expiry/unsolved exits; full480 pixels and successor timing'],
 unknowns=['No native save boundary audit or roundtrip/restore was performed; no format version is assigned',
 'Current generic scriptsIdle/exportPersistentState cannot capture nonempty polling work; a future contract needs explicit recurring-work support',
 'Exact reachable invariants between yearArmed, month display, sprite phases and partial loop work require an independent native audit',
 'Source-observed original dimensions may be re-derived from validated assets, but that restoration preflight has not been built',
 'Natural audio end, active-launch/collision continuation, timing rollover, malformed-state atomicity and fresh-process restoration remain untested here',
 'No original runtime, ScummVM process, codec or callback interpreter was executed by this inventory; no support or completion-percentage claim'])
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('P522 static original save inventory PASS: 18 sprites, 2 locals initialized2/0, 11 programs, 69 commands, recurring200ms poll; no native save claim')
