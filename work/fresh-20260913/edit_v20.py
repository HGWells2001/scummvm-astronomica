from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'resource.h';s=f.read_text();s=s.replace('int32 selectedFrame = -1;', 'int32 frameFirst = 0, frameLast = -1; // -1 upper bound uses all loaded frames.\n int32 selectedFrame = -1;');f.write_text(s)
f=p/'sprites.h';s=f.read_text().replace('bool advanceSpriteFrame(', 'bool setSpriteFrameRange(Sprite &sprite, uint frameCount, int32 first, int32 last);\nbool advanceSpriteFrame(');f.write_text(s)
f=p/'sprites.cpp';s=f.read_text().replace('bool advanceSpriteFrame(', '''bool setSpriteFrameRange(Sprite &sprite, uint frameCount, int32 first, int32 last) {
 // Opcode 48 clamps before passing signed words to 7:0981. The setter
 // changes neither the current frame nor the animation timestamp.
 if (!frameCount) return false;
 if (first < 0) first = 0;
 if (last >= int64(frameCount)) last = frameCount - 1;
 if (first > last || first > 32767 || last > 32767) return false;
 sprite.frameFirst = first; sprite.frameLast = last;
 return true;
}
bool advanceSpriteFrame(''');s=s.replace('sprite.selectedFrame = (uint(sprite.selectedFrame) + 1) % frameCount;', '''const int32 last = sprite.frameLast < 0 ? int32(frameCount - 1) : sprite.frameLast;
 ++sprite.selectedFrame;
 if (sprite.selectedFrame < sprite.frameFirst) sprite.selectedFrame = last;
 else if (sprite.selectedFrame > last) sprite.selectedFrame = sprite.frameFirst;''');f.write_text(s)
f=p/'script.cpp';s=f.read_text();s=s.replace('c.opcode == 47 ||', 'c.opcode == 47 || c.opcode == 48 ||');s=s.replace('case 7: case 47:', 'case 7: case 47: case 48:');needle='if (c.opcode == 15 && uint(c.args[1]) >= _spriteTargets[c.args[0] - 1]) return false;';s=s.replace(needle,needle+'''
    if (c.opcode == 48) {
     const int64 first = c.args[1] < 0 ? 0 : c.args[1];
     const int64 maximum = _spriteTargets[c.args[0] - 1] - 1;
     const int64 last = c.args[2] > maximum ? maximum : c.args[2];
     if (first > last || first > 32767 || last > 32767) return false;
    }''');s=s.replace('c.opcode == 7 || c.opcode == 47) { action.x', 'c.opcode == 7 || c.opcode == 47 || c.opcode == 48) { action.x');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace('    if (action.opcode == 15)', '    if (action.opcode == 15)')
needle='  if (action.opcode == 15) {'
assert needle in s
s=s.replace(needle,'''  if (action.opcode == 48) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size())
    setSpriteFrameRange(_scene.sprites[action.value - 1], spriteFrameCount(_scene, action.value - 1), action.x, action.y);
   continue;
  }
'''+needle);f.write_text(s)
