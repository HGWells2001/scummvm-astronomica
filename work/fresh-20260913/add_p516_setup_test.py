from pathlib import Path
import json,struct
root=Path('outputs/astronomica-cleanroom')
h=2166136261
for row in json.loads((root/'evidence/p516-setup.json').read_text())['rows']:
 sprites={s['id']:s for s in row['sprites']};values=[]
 for id in range(1,50):
  s=sprites.get(id,dict(fields=[0]*6+[-1,-1]+[0]*8,callback=None));f=s['fields']
  values+=f[:10]+f[11:]+[{None:0,'_fxm_move_ellipse':4,'_fxm_hit_jup_comet':5}[s['callback']]]
 for b in struct.pack('<'+'i'*len(values),*values):h=((h^b)*16777619)&0xffffffff
code='''bool verifyJupiterSetup() {
 uint32 hash = 2166136261U;
 for (int mode = 0; mode < 2; ++mode) for (int direction = 1; direction <= 4; ++direction) for (int speed = 0; speed < 16; ++speed) {
  Scene scene; scene.sprites.resize(49); CometMotion m;
  for (uint i = 0; i < scene.sprites.size(); ++i) {
   scene.sprites[i].selectedFrame = 0; scene.sprites[i].moveData[0] = scene.sprites[i].frameData[0] = -1;
  }
  configureJupiter(scene,m,mode,direction,speed);
  for (uint i = 0; i < scene.sprites.size(); ++i) {
   const Sprite &s = scene.sprites[i];
   const int32 values[] = {s.visible,s.renderX,s.renderY,s.moveDX,s.moveDY,s.selectedFrame,
    s.frameData[0],s.moveData[0],s.x,s.y,s.moveData[1],s.moveData[2],m.partner[i],s.orbitSideX,s.orbitSideY,
    mode && speed > 0 && i == 12 ? 5 : m.kind[i]};
   for (uint n = 0; n < ARRAYSIZE(values); ++n) for (int b = 0; b < 4; ++b) hash = (hash ^ ((uint32(values[n]) >> (8*b)) & 255))*16777619U;
  }
 }
 return hash == EXPECTED;
}
'''.replace('EXPECTED',hex(h)+'U')
p=root/'engine/astronomica/sprites.cpp';s=p.read_text();assert 'bool verifyJupiterSetup()' not in s
p.write_text(s.replace('bool verifyJupiterMotion() {',code+'bool verifyJupiterMotion() {'))
print('Original setup hash:',hex(h))
