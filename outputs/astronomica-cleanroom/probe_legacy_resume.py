"""Original text save and countdown portability evidence; original inputs read only."""
import json,hashlib
import probe_menu_services as menu
import probe_world_countdown as clock
p=menu.p
cases=[]
for place,previous,completed in ((117,523,12),(408,523,31),(409,524,40),(523,117,0),(1,408,0)):
 values=[((i*0x1020304)^0xa5a5a5a5)&0xffffffff for i in range(100)]
 text=menu.run(place,previous,completed,values)
 words=[int(x)&0xffffffff for x in text.split()];h=2166136261
 for value in words:h=((h^value)*16777619)&0xffffffff
 cases.append(dict(place=place,previous=previous,completed=completed,text=text,word_hash=f'{h:08x}'))
# An identical saved global8 timestamp can represent different elapsed times.
# The original successful reader restores it verbatim; no epoch is serialized.
early=clock.run(1,0,7,100,300099);late=clock.run(1,0,7,100,300101)
assert early==[1,7,103,0,0] and late==[3,7,427,1,0]
result=dict(status='Original instruction execution and text layout evidence',date='2026-10-13',source_sha256=hashlib.sha256(p.exe).hexdigest(),
 cases=cases,word_count=102,clock=dict(imported_api=json.loads((p.Path(__file__).parent/'evidence/p409-clock.json').read_text()),
 timestamp_global=8,mode_global=60,stage_global=62,example_same_saved_start=100,early_now=300099,late_now=300101,early_result=early,late_result=late),
 native_policy='Read only; exact102 signed decimal values; validate destination and payload before state mutation. Reject active timer modes1/2 with nonzero global8 because saved timestamp lacks a recoverable clock epoch. Mode1 exploration only; no arbitrary puzzle restoration.',
 limitations=['Original text file has no integrity checksum; syntactically valid value changes are not detectable.','No elapsed-time estimate from file modification time; no countdown reset.'])
p.args.out.write_text(json.dumps(result,indent=2));print('Legacy save original reference:5 payloads and ambiguous-clock counterexample PASS')
