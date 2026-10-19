"""Original callback: launch velocity and live digit setting can differ."""
import json
import probe_p513_motion as q
rows=[]
for initial in (7,9):
 m,s=q.machine(initial);ticks=0
 while ticks<20:
  proposed=m.read(s+0x17,2)+q.p.signed(m.read(s+0x7d,2),2);q.run(m,s);m.write(s+0x17,proposed,2);ticks+=1
 assert m.read(s+0x10,2)==1
 m.write(0x1000+0x3f8,8)
 while m.read(s+0x10,2):
  proposed=m.read(s+0x17,2)+q.p.signed(m.read(s+0x7d,2),2);q.run(m,s);m.write(s+0x17,proposed,2);ticks+=1
  assert ticks<300
 digits=[m.read(m.read(0x1000+0x20+4*i)+0x5b) for i in (9,10,11)]
 speed=10-initial;expected=177+((266+speed-1)//speed)*speed
 assert proposed==expected and digits==[0,5,0]
 rows.append(dict(initial_setting=initial,setting_after20_ticks=8,last_x=proposed,ticks=ticks,digits=digits))
report=json.loads(q.p.args.out.read_text());report['cross_setting_cases']=rows;report['scope']='Original callback instruction execution with observed SpriteWorld setter effects modeled; not native save verification'
q.p.args.out.write_text(json.dumps(report,indent=2));print('Original cross-setting photon callback PASS:',rows)
