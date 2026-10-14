from pathlib import Path
import json,struct
root=Path('outputs/astronomica-cleanroom')
data=json.loads((root/'evidence/comet-state.json').read_text())
h=2166136261
callbacks={None:0,'_fxm_move_comet':1,'_fxm_move_comet_to_sun':2,'_fxm_move_comet_off_screen':3}
for row in data['rows']:
    nxt=row['commands'][0][1] if row['commands'] else -1 if row['locked'] else 0
    values=row['local']+[nxt]
    sprites={s['id']:s for s in row['sprites']}
    for id in range(1,50):
        s=sprites.get(id,dict(fields=[0]*6+[-1,-1]+[0]*8,callback=None))
        f=s['fields'];values+=f[:10]+f[11:]+[callbacks[s['callback']]]
    for b in struct.pack('<'+'i'*len(values),*values):h=((h^b)*16777619)&0xffffffff
code='''bool verifyCometSetup() {
 uint32 hash = 2166136261U;
 auto add = [&](int32 value) { for (int b = 0; b < 4; ++b) hash = (hash ^ ((uint32(value) >> (8*b)) & 255))*16777619U; };
 for (int mode = 0; mode < 2; ++mode) for (int target = 1; target <= 10; ++target)
  for (int speed = 0; speed < 16; ++speed) for (int direction = 1; direction <= 4; ++direction)
   for (int maskIndex = 0; maskIndex < (mode ? 2 : 1); ++maskIndex) {
    Scene scene; scene.sprites.resize(49); CometMotion m;
    for (uint i = 0; i < scene.sprites.size(); ++i) {
     scene.sprites[i].selectedFrame = 0; scene.sprites[i].frameData[0] = scene.sprites[i].moveData[0] = -1;
    }
    int32 v[9] = {direction,speed,target,0,0,0,0,0,0};
    for (int i = 3; i < 9; ++i) v[i] = ((maskIndex ? 31 : 0) >> (i-3)) & 1;
    int next = 0;
    if (mode) next = configureComet(scene,m,v); else displayCometSpeed(scene,target,speed);
    for (int i = 0; i < 9; ++i) add(v[i]); add(next);
    for (uint i = 0; i < scene.sprites.size(); ++i) {
     const Sprite &s = scene.sprites[i];
     const int32 values[] = {s.visible,s.renderX,s.renderY,s.moveDX,s.moveDY,s.selectedFrame,
      s.frameData[0],s.moveData[0],s.x,s.y,s.moveData[1],s.moveData[2],m.partner[i],s.orbitSideX,s.orbitSideY,m.kind[i]};
     for (uint n = 0; n < ARRAYSIZE(values); ++n) add(values[n]);
    }
   }
 return hash == EXPECTED;
}
'''.replace('EXPECTED',hex(h)+'U')
p=root/'engine/astronomica/sprites.cpp';s=p.read_text();assert 'bool verifyCometSetup()' not in s
p.write_text(s.replace('static void cometFrame(',code+'static void cometFrame('))
print('Original comet setup expected hash:',hex(h))
