"""Original zodiac-region execution for P507's annulus and twelve selections."""
import json,hashlib,math
from astro_reader import parse
from probe_p514_motion import Machine,p
m=Machine();digest=2166136261;counts=[0]*13
for y in range(35,296):
    for x in range(314,575):
        region=m.call_region(444,165,122,30,x,y)
        counts[region]+=1;digest=((digest^region)*16777619)&0xffffffff
points=[]
for sector in range(12):
    angle=math.radians(75-30*sector)
    x=444+round(80*math.cos(angle));y=165-round(80*math.sin(angle))
    region=m.call_region(444,165,122,30,x,y)
    assert region==sector+1
    points.append(dict(region=region,x=x,y=y,sprite=17+region))
edges=[]
for x,y in ((444,165),(473,165),(474,165),(566,165),(567,165),(444,135),(444,43),(322,165),(444,287)):
    edges.append(dict(x=x,y=y,region=m.call_region(444,165,122,30,x,y)))
raw=(p.args.root/'PLACES/P507/MEGAFILE.HYP').read_bytes();scene=parse(raw)
assert len(scene['sprites'])==30 and len(scene['scripts'])==2 and len(scene['mouse_rects'])==2
assert [c['args'] for c in scene['mouse_rects'][0]['click'] if c['opcode']==23]==[[11,0,0,0,0,0]]
names=[c['args'][0] for c in scene['mouse_rects'][0]['click'] if c['opcode']==20]
assert len(names)==12
p.args.out.write_text(json.dumps(dict(scene=507,status='Original evidence; native checks recorded separately',
 region_grid_cases=261*261,region_hash=hex(digest),counts=counts,points=points,edges=edges,
 images=names,custom='11: use last accepted click coordinates; region0 leaves local0 unchanged; other regions play S6 and show sprite17+region',
 resource_sha256=hashlib.sha256(raw).hexdigest()),indent=2))
print('Original P507 wheel: PASS',hex(digest),points)
