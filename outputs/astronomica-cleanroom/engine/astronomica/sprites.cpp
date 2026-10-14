// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/sprites.h"
#include <math.h>
namespace Astronomica {
void startBall(Sprite &s, BallMotion &m, int scenario) {
 m.scenario = scenario; m.centerX = int16(s.renderX+(scenario == 4 ? 320 : 200));
 m.centerY = s.renderY; m.side = 2; m.period = 10;
 s.moveData[0] = 10; s.standardMotion = s.autoMove = true;
 s.moveDX = scenario == 1 ? 5 : 2; s.moveDY = scenario == 1 ? -3 : scenario == 4 ? -2 : 0;
}
int advanceBall(Sprite &s, BallMotion &m, int width, int height, uint32 now) {
 if (!s.autoMove || s.moveData[0] < 0 || int32(now-s.moveSince) < s.moveData[0]) return 0;
 s.moveSince = now;
 int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 bool stop = false, wrapped = false;
 const bool vesta = m.scenario == 4;
 if (vesta && m.period == 5000) m.period = s.moveData[0] = 10;
 if (s.renderX > s.rect[2]) {
  x = int16(s.rect[0]-width);
  if (vesta) { m.period = s.moveData[0] = 5000; m.side = 0; wrapped = true; }
  else stop = true;
 } else if (int16(s.renderX+width) < s.rect[0]) { x = int16(s.rect[2]); stop = !vesta; }
 if (s.renderY > s.rect[1]) { y = int16(s.rect[3]-height); stop = true; }
 else if (int16(s.renderY+height) < s.rect[3]) { y = int16(s.rect[vesta ? 3 : 1]); stop = true; }
 if (stop) {
  s.autoMove = s.autoFrame = false; s.visible = 0;
  s.moveData[0] = s.frameData[0] = -1; s.moveDX = s.moveDY = 0;
 }
 if (m.scenario == 5 && x >= m.centerX && s.moveDX == 2) s.moveDX = 1;
 if (vesta || (m.scenario == 5 && (m.side || x > m.centerX))) {
  const int32 dx = (vesta && !m.side && x <= m.centerX ? int16(x+640) : x)-m.centerX;
  y = int16(dx*dx/(vesta ? 640 : 400)+m.centerY-(vesta ? 160 : 100));
 }
 s.renderX = x; s.renderY = y;
 return wrapped ? 2 : 1;
}
bool verifyBallMotion() {
 static const uint32 hashes[] = {0x159a26acU,0x804cada0U,0x929bee03U,0x30587a1aU,0x2c25f109U,0xf0b97e80U,0xc812bb1eU,0xe4347c9U,0xad085ffdU};
 static const int ticks[] = {76,76,76,390,390,390,332,302,282};
 const int scenarios[] = {1,4,5}, starts[] = {210,240,260}, ys[] = {207,182,197};
 for (int i = 0; i < 9; ++i) {
  Sprite s; BallMotion m; s.visible = 1; s.renderX = starts[i%3]; s.renderY = ys[i/3];
  s.rect[2] = 640; s.rect[1] = 320; startBall(s,m,scenarios[i/3]);
  uint32 hash = 2166136261U, now = 0;
  for (int tick = 1; tick <= ticks[i]; ++tick) {
   now += s.moveData[0];
   if (advanceBall(s,m,16,16,now-1) || !advanceBall(s,m,16,16,now)) return false;
   const int32 values[] = {int32(now),s.renderX,s.renderY,s.moveDX,s.moveDY,s.visible,m.period,s.moveData[0],m.side};
   for (uint j = 0; j < ARRAYSIZE(values); ++j) for (int byte = 0; byte < 4; ++byte)
    hash = (hash ^ ((uint32(values[j]) >> (byte*8)) & 255))*16777619U;
  }
  if (hash != hashes[i]) return false;
 }
 return true;
}
bool startPhoton(Scene &scene, int setting) {
 if (scene.sprites.size() != 32 || setting < 1 || setting > 9) return false;
 Sprite &s = scene.sprites[31];
 s.moveData[0] = 10; s.autoMove = s.standardMotion = true; s.visible = 1;
 s.moveDX = 10-setting; s.moveDY = 0; return true;
}
bool advancePhoton(Scene &scene, int setting, uint32 now) {
 if (scene.sprites.size() != 32) return false;
 Sprite &s = scene.sprites[31];
 if (!s.autoMove || int32(now-s.moveSince) < 10) return false;
 s.moveSince = now; const int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 if (x > 442 && s.visible == 1) {
  // _hide_and_stop clears both timers and deltas, but the SpriteWorld
  // caller still applies the point computed before entering the callback.
  s.autoMove = s.autoFrame = false; s.visible = 0;
  s.moveData[0] = s.frameData[0] = -1; s.moveDX = s.moveDY = 0;
  for (uint id = 8; id <= 10; ++id) scene.sprites[id].visible = 1;
  static const int digits[9][3] = {{0,0,5},{0,1,1},{0,0,4},{0,3,0},{0,0,2},{1,0,0},{0,0,4},{0,5,0},{0,1,5}};
  static const uint result[] = {12,13,14,14,15,15,16,16,17};
  if (setting >= 1 && setting <= 9) {
   scene.sprites[result[setting-1]-1].visible = 1;
   for (uint id = 0; id < 3; ++id) scene.sprites[id+8].selectedFrame = digits[setting-1][id];
  }
 }
 s.renderX = x; s.renderY = y; return true;
}
bool verifyPhotonMotion() {
 static const uint32 hashes[] = {0x51035100U,0x813a5992U,0xb578cf61U,0xbc82dffaU,0xfd04397bU,0x8a811924U,0xcad832f6U,0x515b7a06U,0xa3fb9950U};
 static const int ticks[] = {30,34,38,45,54,67,89,133,266};
 for (int setting = 1; setting <= 9; ++setting) {
  Scene scene; scene.sprites.resize(32); Sprite &s = scene.sprites[31]; s.renderX = 177; s.renderY = 147;
  if (!startPhoton(scene,setting)) return false;
  uint32 h = 2166136261U;
  for (int tick = 1; tick <= ticks[setting-1]; ++tick) {
   if (advancePhoton(scene,setting,tick*10-1) || !advancePhoton(scene,setting,tick*10)) return false;
   for (uint b = 0; b < 4; ++b) h = (h ^ ((uint32(s.renderX) >> (8*b)) & 255))*16777619U;
  }
  if (h != hashes[setting-1] || s.visible || s.autoMove || s.autoFrame || s.moveDX || s.moveDY) return false;
 }
 return true;
}
bool startOrbit(Scene &scene, int id, int dx, int dy) {
 if (scene.sprites.size() != 23 || (id != 20 && id != 22 && id != 23)) return false;
 Sprite &s = scene.sprites[id-1];
 // 4:26a4-284e: keep the rendered position and timer timestamp.
 s.x = 300+dx; s.y = 120+dy;
 s.moveData[0] = 10; s.moveData[1] = 200; s.moveData[2] = 100; s.moveData[3] = 0;
 s.orbitSideX = s.orbitSideY = 0;
 s.moveDX = 2; s.moveDY = 0; s.orbitMotion = s.standardMotion = s.autoMove = true;
 return true;
}
static void orbitEllipse(Sprite &s, int width, int height, int16 &x, int16 &y, int verticalStep = 1, Scene *scene = nullptr, CometMotion *comet = nullptr, uint index = 0) {
 // P526's subset of 3:2733: no partner handoff (b9 is zero), no P514
 // astrology callbacks, and no local2==10 angle-to-frame conversion.
 if (!s.visible && !s.moveDX && !s.moveDY) return;
 const int32 a = s.moveData[1], b = s.moveData[2];
 if (s.renderX > s.x+a) x = int16(s.x+a);
 else if (int16(s.renderX+width) < s.x-a) x = int16(s.x-a);
 if (s.renderY > s.y+b) y = int16(s.y+b);
 else if (int16(s.renderY+height) < s.y-b) y = int16(s.y-b);
 const int32 dx = x-s.x, dy = y-s.y;
 if (2*dy < dx && -2*dy < dx && !s.moveDY) {
  s.moveDX = 0; s.moveDY = -verticalStep; s.orbitSideX = 1; s.orbitSideY = 0;
 } else if (2*dy > dx && -2*dy > dx && !s.moveDY) {
  s.moveDX = 0; s.moveDY = verticalStep; s.orbitSideX = s.orbitSideY = 0;
 } else if (2*dy > dx && -2*dy < dx && !s.moveDX) {
  s.moveDX = 2; s.moveDY = 0; s.orbitSideX = s.orbitSideY = 0;
 } else if (2*dy < dx && -2*dy > dx && !s.moveDX) {
  s.moveDX = -2; s.moveDY = 0; s.orbitSideX = 0; s.orbitSideY = 1;
 }
 // 1:15c3 selects x87 truncation before multiplying by the other radius.
 if (s.moveDX) {
  const int32 root = a*a-(x-s.x)*(x-s.x);
  if (root < 0 || a <= 0) return;
  const int32 e = -int32(sqrt(double(root)))*b/a;
  y = int16(s.y+(s.orbitSideY ? e : -e));
 } else if (s.moveDY) {
  const int32 root = b*b-(y-s.y)*(y-s.y);
  if (root < 0 || b <= 0) return;
  const int32 e = -int32(sqrt(double(root)))*a/b;
  // 3:2b13..2e76 swaps the visible partner before committing corrected X.
  const int partner = comet ? comet->partner[index] : 0;
  if (scene && s.visible && ((partner > 0 && y > s.y) || (partner < 0 && y < s.y))) {
   const uint other = uint(partner > 0 ? partner-1 : -partner-1);
   if (other < scene->sprites.size()) {
    Sprite &next = scene->sprites[other];
    s.visible = 0; next.renderX = x; next.renderY = y; next.visible = 1;
    next.orbitSideX = s.orbitSideX; next.orbitSideY = s.orbitSideY;
    next.moveDX = s.moveDX; next.moveDY = s.moveDY; next.moveData[0] = s.moveData[0];
    next.autoMove = true; next.selectedFrame = s.selectedFrame;
    s.moveDX = s.moveDY = 0;
   }
  }
  x = int16(s.x+(s.orbitSideX ? -e : e));
 }
}
bool supportsComet(const Scene &scene, int place) {
 return (place == 502 && scene.layers == 1 && scene.sprites.size() == 35) ||
  (place == 503 && scene.layers == 2 && scene.sprites.size() == 48) ||
  (place == 504 && scene.layers == 2 && scene.sprites.size() == 45);
}
bool supportsSpriteLayers(const Scene &scene) {
 return scene.layers == 1 || supportsComet(scene,503) || supportsComet(scene,504) || supportsJupiter(scene);
}
bool supportsJupiter(const Scene &scene) { return scene.layers == 2 && scene.sprites.size() == 37; }
void configureJupiter(Scene &scene, CometMotion &m, int mode, int direction, int speed) {
 if (mode == 1) {
  if (speed <= 0) return;
  Sprite &s = scene.sprites[12];
  s.standardMotion = s.autoMove = true; s.moveData[0] = 50;
  s.moveDX = (2*direction-5)*(speed+3)/3; s.moveDY = -2*(speed+3)/3;
  s.visible = 1; s.renderX = 320; s.renderY = 300; return;
 }
 for (int id = 14; id <= 21; ++id) {
  Sprite &s = scene.sprites[id-1]; const int radius = id <= 17 ? 18-id : id-17;
  s.x = 320; s.y = 100; s.moveData[0] = 10; s.moveData[1] = radius*40+100; s.moveData[2] = radius*12+50;
  s.moveDX = s.moveDY = 0; s.orbitSideX = s.orbitSideY = 0;
  s.autoMove = s.standardMotion = true; m.kind[id-1] = 4;
  m.partner[id-1] = id <= 17 ? 35-id : id-35; s.visible = id >= 18;
  if (id >= 18) { s.renderX = 320; s.renderY = 100+s.moveData[2]; }
 }
}
int advanceJupiter(Scene &scene, const int *widths, const int *heights, int width, int height, uint32 now) {
 Sprite &s = scene.sprites[12];
 if (!s.autoMove || s.moveData[0] < 0 || int32(now-s.moveSince) < s.moveData[0]) return 0;
 s.moveSince = now; const int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 auto stop = [](Sprite &a) { a.visible = 0; a.autoMove = a.autoFrame = false; a.moveData[0] = a.frameData[0] = -1; a.moveDX = a.moveDY = 0; };
 // Callback reads the old rectangle; SpriteWorld commits the proposed point afterwards.
 if (s.renderX > int16(s.rect[2]) || int16(s.renderX+width) < int16(s.rect[3]) ||
     s.renderY > int16(s.rect[1]) || int16(s.renderY+height) < int16(s.rect[0])) stop(s);
 const int16 px = int16(s.renderX+16), py = int16(s.renderY+16); int result = 1;
 for (int id = 14; id <= 21; ++id) {
  Sprite &target = scene.sprites[id-1]; const int n = id-14;
  // Imported USER PtInRect excludes right/bottom (unlike SWIsPointInSprite).
  if (!target.visible || px < target.renderX || px >= int16(target.renderX+widths[n]) || py < target.renderY || py >= int16(target.renderY+heights[n])) continue;
  if (id == 17 || id == 18) {
   for (int other = 14; other <= 21; ++other) { scene.sprites[other-1].moveData[0] = -1; scene.sprites[other-1].autoMove = false; }
   stop(target); result |= id == 17 ? 2 : 4;
  }
  stop(s);
 }
 s.renderX = x; s.renderY = y; return result;
}
bool verifyJupiterCollision() {
 const int points[][2] = {{84,84},{130,84},{84,130},{650,84}};
 for (int target = 14; target <= 21; ++target) for (int visible = 0; visible < 2; ++visible) for (int point = 0; point < 4; ++point) {
  Scene scene; scene.sprites.resize(37); int sizes[8]; for (int n = 0; n < 8; ++n) sizes[n] = 16;
  Sprite &projectile = scene.sprites[12], &victim = scene.sprites[target-1];
  projectile.autoMove = true; projectile.moveData[0] = 50; projectile.visible = 1;
  projectile.renderX = points[point][0]; projectile.renderY = points[point][1];
  projectile.rect[1] = 320; projectile.rect[2] = 640;
  victim.visible = visible; victim.renderX = victim.renderY = 90;
  const int result = advanceJupiter(scene,sizes,sizes,16,16,50);
  const bool hit = visible && point == 0, solved = hit && (target == 17 || target == 18);
  if (bool(result & 6) != solved || bool(projectile.visible) != (!hit && point != 3) || bool(victim.visible) != (visible && !solved)) return false;
 }
 // USER PtInRect includes left/top, excludes right/bottom.
 const int edgePoints[][2] = {{90,90},{105,105},{106,100},{100,106}};
 for (int point = 0; point < 4; ++point) {
  Scene scene; scene.sprites.resize(37); int sizes[8]; for (int n = 0; n < 8; ++n) sizes[n] = 16;
  Sprite &projectile = scene.sprites[12], &victim = scene.sprites[16];
  projectile.autoMove = true; projectile.moveData[0] = 50; projectile.visible = 1;
  projectile.renderX = edgePoints[point][0]-16; projectile.renderY = edgePoints[point][1]-16;
  projectile.rect[1] = 320; projectile.rect[2] = 640;
  victim.visible = 1; victim.renderX = victim.renderY = 90;
  if (bool(advanceJupiter(scene,sizes,sizes,16,16,50) & 6) != (point < 2)) return false;
 }
 return true;
}
bool verifyJupiterSetup() {
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
 return hash == 0x39418dfbU;
}
bool verifyJupiterMotion() {
 Scene scene; scene.sprites.resize(37); CometMotion m;
 const int widths[] = {50,39,110,60,60,110,39,50}, heights[] = {50,100,40,60,60,40,100,50};
 for (int id = 14; id <= 21; ++id) {
  Sprite &s = scene.sprites[id-1]; s.renderX = id <= 17 ? 454 : 154; s.renderY = 100; s.selectedFrame = 0;
 }
 configureJupiter(scene,m,0,1,0); uint32 hash = 2166136261U;
 for (uint32 now = 10; now <= 20000; now += 10) {
  for (int id = 14; id <= 21; ++id) advanceComet(scene,m,id-1,widths[id-14],heights[id-14],0,now);
  for (int id = 14; id <= 21; ++id) {
   const Sprite &s = scene.sprites[id-1];
   const int32 values[] = {s.renderX,s.renderY,s.moveDX,s.moveDY,s.visible,s.selectedFrame,s.moveData[0],s.orbitSideX,s.orbitSideY};
   for (uint n = 0; n < ARRAYSIZE(values); ++n) for (int b = 0; b < 4; ++b) hash = (hash ^ ((uint32(values[n]) >> (8*b)) & 255))*16777619U;
  }
 }
 return hash == 0x7780b563U;
}
int cometSpeed(int level) {
 const int speeds[] = {0,5010,10080,11520,14400,20880,28080,51840,64800,75600,102960,120610,140810,162000,181300,200000};
 return level >= 0 && level < 16 ? speeds[level] : 0;
}
int configureComet(Scene &scene, CometMotion &m, int32 *v) {
 const int target = v[2], level = v[1], direction = v[0];
 const int id = target == 10 ? 20 : target+(target <= 4 ? 22 : 19);
 if (target < 1 || target > 10 || uint(id) > scene.sprites.size()) return 0;
 Sprite &s = scene.sprites[id-1];
 s.renderX = 520; s.renderY = target == 10 ? 310 : 285;
 s.moveData[0] = target <= 4 ? 15 : 10; s.standardMotion = s.autoMove = true; s.visible = 1;
 m.partner[id-1] = 0;
 if (target == 10) { s.selectedFrame = 0; s.autoFrame = false; s.frameData[0] = -1; }
 const int required = target == 10 ? 13 : 11-target;
 const bool orbit = level == required && (target == 10 ? direction == 1 || direction == 4 :
  target <= 4 ? direction == target : direction == target-4 || target == 9);
 if (!orbit) {
  if (target <= 4) v[target+2] = 0;
  if (target == 10) v[3] = 0;
  m.kind[id-1] = level > required ? 3 : 2; s.moveDX = 0; s.moveDY = level > required ? -4 : -1;
  return 0;
 }
 v[target == 10 ? 3 : target <= 4 ? target+2 : target-2] = 1;
 s.x = 320; s.y = 160; s.moveData[1] = target == 10 ? 200 : target*25+(target <= 4 ? 100 : 0);
 s.moveData[2] = target == 10 ? 100 : target*12+(target <= 4 ? 50 : 0);
 s.moveData[0] = target == 10 ? 10 : 40; s.orbitSideX = s.orbitSideY = 1;
 s.moveDX = 0; s.moveDY = -2; m.kind[id-1] = 1;
 if (target != 10) {
  const int partner = (target <= 4 ? 53 : 57)-id; Sprite &other = scene.sprites[partner-1];
  m.partner[id-1] = -partner; m.partner[partner-1] = id; m.kind[partner-1] = 1;
  other.x = s.x; other.y = s.y; other.moveData[1] = s.moveData[1]; other.moveData[2] = s.moveData[2];
  other.frameData[0] = 30; other.frameData[1] = 1; other.frameData[2] = 0; other.autoFrame = other.standardMotion = true;
 }
 if (target == 10) return 503;
 if (v[3] && v[4] && v[5] && v[6]) {
  if (target <= 4) { v[7] = 1; return -1; }
  if (v[7]) { v[8] = 1; return 504; }
 }
 return 0;
}
void displayCometSpeed(Scene &scene, int target, int level) {
 const int first = target <= 4 ? 13 : target <= 9 ? 14 : 10;
 int speed = cometSpeed(level);
 for (int n = 5; n >= 0; --n) { scene.sprites[first+n-1].selectedFrame = speed%10; speed /= 10; }
}
bool verifyCometSetup() {
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
 return hash == 0x6eadc5e5U;
}
static void cometFrame(CometMotion &m, int x, int y) {
 // Original ordered, stateful direction transitions at3:2f5c..33cb.
 const int f = m.frame, p = m.previousFrame; int next = f;
 if (f == 4 && p != 3) { if (y >= 0) next = 3; }
 else if (f == 3 && p == 4) { if (4*y >= x) next = 2; }
 else if (f == 2 && p == 3) { if (5*y >= 3*x) next = 1; }
 else if (f == 1 && p == 2) { if (y >= x) next = 12; }
 else if (f == 12 && p == 1) { if (4*y >= 7*x) next = 11; }
 else if (f == 11 && p == 12) { if (4*y >= 15*x) next = 10; }
 else if (f == 10 && p == 11) { if (x <= 0) next = 9; }
 else if (f == 9 && p == 10) { if (4*y <= -15*x) next = 8; }
 else if (f == 8 && p == 9) { if (4*y <= -7*x) next = 7; }
 else if (f == 7) { if (5*y <= -3*x) next = 8; }
 else if (f == 8) { if (-4*y <= x) next = 9; }
 else if (f == 9) { if (y <= 0) next = 10; }
 else if (f == 10) { if (4*y <= x) next = 11; }
 else if (f == 11) { if (5*y <= 3*x) next = 12; }
 else if (f == 12) { if (y <= x) next = 1; }
 else if (f == 1) { if (4*y <= 7*x) next = 2; }
 else if (f == 2) { if (4*y <= 15*x) next = 3; }
 else if (f == 3) { if (x >= 0) next = 4; }
 else if (f == 4) { if (4*y >= -15*x) next = 5; }
 else if (f == 5 && p == 4) { if (4*y >= -7*x) next = 6; }
 else if (f == 6) { if (5*y >= -3*x) next = 5; }
 else if (f == 5) { if (-4*y >= x) next = 4; }
 if (next != f) { m.previousFrame = f; m.frame = next; }
}
bool advanceComet(Scene &scene, CometMotion &m, uint index, int width, int height, int target, uint32 now) {
 m.sound = -1; m.explosion = 0;
 Sprite &s = scene.sprites[index]; const int kind = m.kind[index];
 if (!kind || !s.autoMove || s.moveData[0] < 0 || int32(now-s.moveSince) < s.moveData[0]) return false;
 s.moveSince = now; int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 bool stop = false;
 if (kind == 1) {
  m.frame = 4;
  if (target == 10 && s.renderY <= 240) s.selectedFrame = 2;
  if (s.renderY <= 160) {
   if (target == 10) m.sound = 2;
   s.moveDX = s.moveDY = 0; m.kind[index] = 4;
  }
  if ((y%5 == 0 || (y-1)%5 == 0) && y != 285) {
   if (target <= 4) x = int16(x+target-4);
   else if (target <= 9) x = int16(x+target-8);
  }
 } else if (kind == 2 || kind == 3) {
  if (kind == 2 && target == 10) s.selectedFrame = s.renderX <= 370 ? 5 : s.renderX <= 400 ? 4 : s.renderX <= 430 ? 3 : s.renderX <= 460 ? 2 : s.renderX <= 490 ? 1 : 0;
  const int d = int16(310-y); x = int16(520-d*d/(kind == 2 ? 80 : 280));
  if (kind == 2 && x <= 340) { stop = true; m.sound = 3; m.explosion = target <= 4 ? 31 : target <= 9 ? 34 : 21; }
  if (kind == 3 && (x <= 10 || y <= 10)) stop = true;
 } else {
  orbitEllipse(s,width,height,x,y,1,&scene,&m,index);
  if (target == 10) { cometFrame(m,x-s.x,s.y-y); s.selectedFrame = m.frame-1; }
 }
 if (stop) { s.autoMove = s.autoFrame = false; s.visible = 0; s.moveData[0] = s.frameData[0] = -1; s.moveDX = s.moveDY = 0; }
 s.renderX = x; s.renderY = y; return true;
}
bool verifyCometMotion() {
 static const uint32 hashes[] = {0x5f6476ceU,0x3e1f8444U,0xd8e469b5U,0x5f6476ceU,0x3e1f8444U,0x80871ca2U,0x5f6476ceU,0x3e1f8444U,0xb88e440fU,0x5f6476ceU,0x3e1f8444U,0x356a6350U,0x1dbf3986U,0x441663dfU,0x6177ea6eU,0x1dbf3986U,0x441663dfU,0xb95422a8U,0x1dbf3986U,0x441663dfU,0x76c8c528U,0x1dbf3986U,0x441663dfU,0x614142e7U,0x1dbf3986U,0x441663dfU,0xc9ac79ceU,0x471ee8d3U,0x2ba63ff9U,0xd749db36U};
 static const int times[] = {1900,1380,20000,1900,1380,20000,1900,1380,20000,1900,1380,20000,950,690,20000,950,690,20000,950,690,20000,950,690,20000,950,690,20000,1200,750,20000};
 for (int t = 1; t <= 10; ++t) for (int outcome = 0; outcome < 3; ++outcome) {
  Scene scene; scene.sprites.resize(49); CometMotion m;
  for (uint i = 0; i < scene.sprites.size(); ++i) { scene.sprites[i].selectedFrame = 0; scene.sprites[i].frameData[0] = scene.sprites[i].moveData[0] = -1; }
  int32 v[9] = {}; v[0] = outcome == 2 ? (t == 10 || t == 9 ? 1 : t <= 4 ? t : t-4) : 1;
  v[1] = outcome == 0 ? 0 : outcome == 1 ? 15 : t == 10 ? 13 : 11-t; v[2] = t;
  configureComet(scene,m,v);
  const int id = t == 10 ? 20 : t+(t <= 4 ? 22 : 19);
  const int partner = outcome == 2 && t != 10 ? (t <= 4 ? 53 : 57)-id : 0;
  uint32 hash = 2166136261U;
  for (int now = 10; now <= times[(t-1)*3+outcome]; now += 10) {
   advanceComet(scene,m,id-1,16,16,t,now);
   if (partner) advanceComet(scene,m,partner-1,16,16,t,now);
   for (int n = 0; n < (partner ? 2 : 1); ++n) {
    const Sprite &s = scene.sprites[(n ? partner : id)-1];
    const int32 values[] = {s.renderX,s.renderY,s.moveDX,s.moveDY,s.visible,s.selectedFrame,s.moveData[0],s.orbitSideX,s.orbitSideY};
    for (uint i = 0; i < ARRAYSIZE(values); ++i) for (int byte = 0; byte < 4; ++byte)
     hash = (hash ^ ((uint32(values[i]) >> (8*byte)) & 255))*16777619U;
   }
  }
  if (hash != hashes[(t-1)*3+outcome]) return false;
 }
 return true;
}
int rendezvousRegion(int x, int y) {
 return astrologyRegion(x,y,295,140,256,0);
}
int astrologyRegion(int x, int y, int cx, int cy, int outer, int inner) {
 // Original 3:3748, including the stored decimal (not exact trig) slopes.
 const int dx = x-cx, dy = cy-y;
 const int64 distance = int64(dx)*dx+int64(dy)*dy;
 if (distance > int64(outer)*outer || distance < int64(inner)*inner) return 0;
 if (dx >= 0 && dy >= 0) return dx*1.732 < dy ? 1 : dx*0.577 < dy ? 2 : 3;
 if (dx >= 0) return dx*-1.732 > dy ? 6 : dx*-0.577 > dy ? 5 : 4;
 if (dy >= 0) return dx*-1.732 < dy ? 12 : dx*-0.577 < dy ? 11 : 10;
 return dx*1.732 > dy ? 7 : dx*0.577 > dy ? 8 : 9;
}
void configureRendezvous(Scene &scene, int mode, int speed) {
 if (scene.sprites.size() != 20 || mode < 0 || mode > 2 || speed < 0 || speed > 15) return;
 Sprite &s = scene.sprites[mode ? 18 : 16];
 if (mode < 2) {
  s.x = 295; s.y = 140; s.moveData[1] = s.moveData[2] = 145;
  s.moveData[3] = 0; s.orbitSideX = s.orbitSideY = 0;
  s.moveDX = 2; s.moveDY = 0; s.orbitMotion = s.standardMotion = true;
 }
 s.moveData[0] = mode ? 100-4*speed : 100; s.autoMove = true;
 if (mode) {
  Sprite &fuel = scene.sprites[13];
  fuel.moveData[0] = 1000-40*speed; fuel.autoMove = true;
  if (mode == 1) { fuel.standardMotion = true; fuel.moveDX = 0; fuel.moveDY = 1; }
 }
}
bool advanceRendezvous(Scene &scene, uint index, int width, int height, uint32 now) {
 if (scene.sprites.size() != 20 || (index != 13 && index != 16 && index != 18)) return false;
 Sprite &s = scene.sprites[index];
 if (!s.autoMove || s.moveData[0] < 0 || int32(now-s.moveSince) < s.moveData[0]) return false;
 s.moveSince = now;
 int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 if (index != 13) {
  orbitEllipse(s,width,height,x,y,2);
  if (index == 18) s.selectedFrame = (rendezvousRegion(x,y)+10)%12;
 } else if (y > 412) {
  for (uint i = 0; i < 3; ++i) {
   Sprite &stopped = scene.sprites[i == 0 ? 13 : i == 1 ? 16 : 18];
   stopped.moveData[0] = -1; stopped.autoMove = false;
  }
 }
 s.renderX = x; s.renderY = y; return true;
}
void configureProbe(Scene &scene, ProbeMotion &motion, int id) {
 if (scene.sprites.size() != 18 || id < 15 || id > 17) return;
 Sprite &s = scene.sprites[id-1];
 s.x = 300; s.y = 140; s.moveData[0] = 30;
 s.moveData[1] = id == 16 ? 226 : 120; s.moveData[2] = id == 16 ? 113 : 60;
 s.moveData[3] = 0; s.frameData[0] = 80;
 s.orbitSideX = s.orbitSideY = 0; s.moveDX = 2; s.moveDY = 0;
 s.autoMove = s.standardMotion = s.orbitMotion = true;
 if (id == 17) {
  motion.year = 1991; motion.yearArmed = motion.specialHit = motion.flying = motion.expired = false;
 }
}
void launchProbe(Scene &scene, ProbeMotion &motion) {
 const Sprite &earth = scene.sprites[14];
 const int month = (20-astrologyRegion(earth.renderX,earth.renderY,300,140,300,20))%12;
 motion.flying = true;
 // 4:334a-33b2 only sets this flag; it does not clear an earlier hit.
 if ((motion.year == 1992 && month == 8) || (motion.year == 1994 && month == 10) ||
     (motion.year == 1997 && month == 0) || (motion.year == 1999 && month == 3) || (motion.year == 2001 && month == 5))
  motion.specialHit = true;
}
bool advanceProbe(Scene &scene, ProbeMotion &motion, uint index, int32 &state, uint32 now) {
 if (scene.sprites.size() != 18 || index < 14 || index > 16) return false;
 Sprite &s = scene.sprites[index], &probe = scene.sprites[16];
 if (!s.autoMove || int32(now-s.moveSince) < s.moveData[0]) return false;
 s.moveSince = now;
 // A null probe callback still leaves its ordinary SpriteWorld delta active.
 int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 if (index != 16 || motion.flying) orbitEllipse(s,motion.widths[index-14],motion.heights[index-14],x,y);
 if (index == 14) {
  if (state == 0) {
   probe.renderX = x; probe.renderY = y;
   probe.orbitSideX = s.orbitSideX; probe.orbitSideY = s.orbitSideY;
   probe.moveDX = s.moveDX; probe.moveDY = s.moveDY;
  }
  const int month = (20-astrologyRegion(x,y,300,140,300,20))%12;
  scene.sprites[8].selectedFrame = month;
  if (month == 0 && motion.yearArmed) {
   motion.yearArmed = false; ++motion.year; motion.expired = motion.year == 2003;
   int value = motion.year;
   for (int i = 12; i >= 9; --i) { scene.sprites[i].selectedFrame = value%10; value /= 10; }
  } else if (month == 1) motion.yearArmed = true;
 } else if (index == 15) {
  if (state == 1 && motion.specialHit && probe.moveData[1] > 173) {
   probe.renderX += (x > probe.renderX)-(x < probe.renderX);
   probe.renderY += (y > probe.renderY)-(y < probe.renderY);
  }
 } else if (motion.flying) {
  if (s.moveData[1] < 226) {
   if ((!s.moveDX && y%5 == 0) || (s.moveDX && !s.moveDY && x%10 == 0)) {
    s.moveData[1] += 2; ++s.moveData[2];
   }
  } else if (s.moveData[1] != 226) { s.moveData[1] = 226; s.moveData[2] = 113; }
  if (s.moveData[1] == 226 && state == 1) {
   const Sprite &mars = scene.sprites[15];
   const int left = mars.renderX, top = mars.renderY;
   const int right = left+motion.widths[1], bottom = top+motion.heights[1];
   const int w = motion.widths[2], h = motion.heights[2];
   if (motion.specialHit || pointInSprite(s,w,h,left,top) || pointInSprite(s,w,h,right,top) ||
       pointInSprite(s,w,h,left,bottom) || pointInSprite(s,w,h,right,bottom)) state = 2;
   else { s.visible = 0; motion.flying = false; s.moveData[1] = 120; s.moveData[2] = 60; state = 0; }
  }
 }
 s.renderX = x; s.renderY = y; return true;
}
bool verifyProbeMotion() {
 auto setup = [](Scene &scene, ProbeMotion &motion) {
  scene.sprites.resize(18);
  const int widths[] = {54,40,43}, heights[] = {52,40,25}, left[] = {180,40,180};
  for (int i = 0; i < 3; ++i) {
   motion.widths[i] = widths[i]; motion.heights[i] = heights[i];
   Sprite &s = scene.sprites[i+14]; s.renderX = left[i]; s.renderY = 140; s.visible = i != 2;
   configureProbe(scene,motion,i+15);
  }
 };
 auto add = [](uint32 &hash, int value) {
  for (uint b = 0; b < 4; ++b) hash = (hash ^ ((uint32(value) >> (8*b)) & 255))*16777619U;
 };
 Scene scene; ProbeMotion motion; setup(scene,motion); int32 state = 0; uint32 hash = 2166136261U;
 for (int tick = 1; tick <= 4128; ++tick) {
  for (int i = 14; i <= 16; ++i) {
   if (advanceProbe(scene,motion,i,state,tick*30-1)) return false;
   if (!advanceProbe(scene,motion,i,state,tick*30)) return false;
  }
  add(hash,motion.year); add(hash,motion.yearArmed); add(hash,scene.sprites[8].selectedFrame);
  for (int i = 14; i <= 16; ++i) {
   const Sprite &s = scene.sprites[i]; add(hash,s.renderX); add(hash,s.renderY); add(hash,s.moveDX); add(hash,s.moveDY);
  }
 }
 if (hash != 0x865b4d54U || !motion.expired || motion.year != 2003) return false;
 const int years[] = {1991,1992,1994,1997,1999,2001}, months[] = {8,8,10,0,3,5};
 const int launchTicks[] = {257,597,1315,2088,2823,3571}, endTicks[] = {527,870,1534,2335,3105,3880};
 const uint32 hashes[] = {0x32465abdU,0x24d79d40U,0x5be8c380U,0x9cf97e72U,0xf2830240U,0xc0478718U};
 for (int route = 0; route < 6; ++route) {
  scene = Scene(); motion = ProbeMotion(); setup(scene,motion); state = 0; hash = 2166136261U; bool launched = false;
  for (int tick = 1; tick <= endTicks[route]; ++tick) {
   advanceProbe(scene,motion,14,state,tick*30); advanceProbe(scene,motion,15,state,tick*30);
   const Sprite &earth = scene.sprites[14];
   if (!launched && motion.year == years[route] && (20-astrologyRegion(earth.renderX,earth.renderY,300,140,300,20))%12 == months[route]) {
    if (tick != launchTicks[route]) return false;
    launchProbe(scene,motion); state = 1; launched = true; scene.sprites[16].visible = 1;
   }
   advanceProbe(scene,motion,16,state,tick*30);
   if (launched) {
    const Sprite &s = scene.sprites[16];
    add(hash,state); add(hash,motion.specialHit); add(hash,s.moveData[1]); add(hash,s.moveData[2]);
    add(hash,s.renderX); add(hash,s.renderY); add(hash,s.moveDX); add(hash,s.moveDY);
    if (tick < endTicks[route] && state != 1) return false;
   }
  }
  if (!launched || state != (route ? 2 : 0) || hash != hashes[route]) return false;
 }
 return true;
}
bool verifyRendezvousMotion() {
 uint32 regionHash = 2166136261U;
 for (int y = -120; y <= 400; y += 4) for (int x = 35; x <= 555; x += 4)
  regionHash = (regionHash ^ uint32(rendezvousRegion(x,y)))*16777619U;
 if (regionHash != 0xd08a891aU) return false;
 const uint32 expected[] = {0x12bc0440U,0x56d15423U};
 for (uint trace = 0; trace < 2; ++trace) {
  Scene scene; scene.sprites.resize(20); const uint index = trace ? 18 : 16;
  Sprite &s = scene.sprites[index]; s.renderX = trace ? 110 : 300; s.renderY = trace ? 170 : 2;
  s.visible = 1; s.selectedFrame = 0; configureRendezvous(scene,trace,0);
  uint32 hash = 2166136261U;
  for (uint tick = 1; tick <= 1000; ++tick) {
   advanceRendezvous(scene,index,trace ? 56 : 52,trace ? 56 : 54,tick*100);
   const int values[] = {s.renderX,s.renderY,s.moveDX,s.moveDY,s.selectedFrame};
   for (uint i = 0; i < ARRAYSIZE(values); ++i)
    for (uint b = 0; b < 4; ++b) hash = (hash ^ ((uint32(values[i]) >> (8*b)) & 255))*16777619U;
  }
  if (hash != expected[trace]) return false;
 }
 return true;
}
bool advanceOrbit(Scene &scene, uint index, int width, int height, int scenario, uint32 now) {
 if (scene.sprites.size() != 23 || index >= 23) return false;
 Sprite &s = scene.sprites[index];
 if (!s.orbitMotion || !s.autoMove || int32(now-s.moveSince) < 10) return false;
 s.moveSince = now;
 int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 Sprite &front = scene.sprites[19], &back = scene.sprites[21], &shadow = scene.sprites[22], &phase = scene.sprites[17];
 // SWProcess supplies a proposed point to each callback in sprite order.
 // 21/23 return immediately, but their proposed delta still takes effect.
 if (index != 20 && index != 22) {
  if (index == 19) {
   orbitEllipse(s,width,height,x,y);
   scene.sprites[20].renderX = int16(x+11); scene.sprites[20].renderY = int16(y-50);
   back.renderX = x; back.renderY = y;
   shadow.renderX = int16(x+11); shadow.renderY = int16(y-50);
  }
  if (front.visible || back.visible) {
   front.visible = int16(y*10) > int16(x*4-200); back.visible = !front.visible; shadow.visible = 1;
   if (scenario == 3 && front.moveData[1] == 200) {
    if (x >= 295 && x <= 305) front.moveData[1] = 250;
    front.moveData[2] = 125;
   }
   bool stop = false;
   switch (scenario) {
   case 1: stop = x >= 285 && x <= 315 && y > s.y; break;
   case 2: stop = x >= 175 && x <= 205 && y > s.y; break;
   case 3: stop = front.moveData[1] == 250 && x >= 175 && x <= 205 && y > s.y; break;
   case 4: stop = x >= 195 && x <= 225 && y > s.y; break;
   case 5: stop = x >= 425 && x <= 435 && y < s.y; break;
   case 6: stop = x >= 445 && x <= 455 && y < s.y; break;
   }
   if (stop) {
    phase.autoFrame = false; phase.frameData[0] = -1;
    back.renderX = x; back.renderY = y;
    shadow.renderX = int16(x+13); shadow.renderY = int16(y-50);
    front.autoMove = back.autoMove = shadow.autoMove = false;
    if (phase.selectedFrame >= 6 && phase.selectedFrame <= 8) phase.selectedFrame = 5;
    else if (phase.selectedFrame == 9 || phase.selectedFrame == 10) phase.selectedFrame = 11;
   }
  }
 }
 s.renderX = x; s.renderY = y;
 return true;
}
bool orbitAnswer(int scenario, int frame, int choice) {
 // Exhaustively compared with 588 executions of original 4:2851-2e1d.
 static const uint8 masks[2][14] = {
  {10,10,2,66,64,96,96,96,48,24,24,24,26,26},
  {96,96,112,56,24,28,26,14,14,70,102,98,96,96}
 };
 // The original selects its table solely with scenario > 4; zero is also
 // a real intermediate state while the experiment is running.
 return frame >= 0 && frame < 14 && choice >= 0 && choice <= 6 && (masks[scenario > 4][frame] & (1 << choice));
}
bool verifyOrbitMotion() {
 uint32 answersHash = 2166136261U;
 for (int scenario = 1; scenario <= 6; ++scenario)
  for (int frame = 0; frame < 14; ++frame)
   for (int choice = 0; choice < 7; ++choice) answersHash = (answersHash ^ uint32(orbitAnswer(scenario,frame,choice)))*16777619U;
 if (answersHash != 0x4527a881U) return false; // probe_p526_answers.py, original CMP/Jcc execution.
 if (!orbitAnswer(0,0,1) || !orbitAnswer(-1,0,1) || !orbitAnswer(7,0,5)) return false;
 // Independent fixtures: probe_p526_motion.py executes original x86.
 struct Trace { int scenario, delay, phase, ticks; uint32 hash; };
 static const Trace traces[] = {
  {1,1,0,1,0xc0b7b9bcU},{1,1,7,1,0xd032fc89U},
  {1,500,0,560,0x4df1394dU},{1,500,7,560,0x9235bc94U},
  {2,1,0,505,0x27c94bb4U},{2,1,7,505,0xd6191a3dU},
  {2,500,0,505,0x27c94bb4U},{2,500,7,505,0xd6191a3dU},
  {3,1,0,645,0x1cf00162U},{3,1,7,645,0x5cfeb965U},
  {3,500,0,1213,0x5ade81b9U},{3,500,7,1213,0xe872c9bfU},
  {4,1,0,515,0x34d476f5U},{4,1,7,515,0xd193c3cfU},
  {4,500,0,515,0x34d476f5U},{4,500,7,515,0xd193c3cfU},
  {5,1,0,217,0x19c2a329U},{5,1,7,217,0x9f681f38U},
  {5,500,0,785,0xa0f511b8U},{5,500,7,785,0xf8504d24U},
  {6,1,0,205,0x6263e3a9U},{6,1,7,205,0xbdabc9e7U},
  {6,500,0,773,0x3184453cU},{6,500,7,773,0xd539bf37U}
 };
 for (uint n = 0; n < ARRAYSIZE(traces); ++n) {
  const Trace &t = traces[n]; Scene scene; scene.sprites.resize(23);
  for (uint i = 0; i < scene.sprites.size(); ++i) scene.sprites[i].layer = 1;
  const int ids[] = {20,22,23};
  for (uint i = 0; i < 3; ++i) {
   Sprite &s = scene.sprites[ids[i]-1];
   s.renderX = ids[i] == 23 ? 313 : 300; s.renderY = ids[i] == 23 ? 170 : 220;
   s.visible = ids[i] != 22;
   startOrbit(scene,ids[i],ids[i] == 23 ? 13 : 0,ids[i] == 23 ? -50 : 0);
  }
  Sprite &phase = scene.sprites[17]; phase.selectedFrame = t.phase;
  phase.autoFrame = true; phase.frameData[0] = 100; phase.frameData[1] = 1;
  uint32 hash = 2166136261U;
  int tick;
  for (tick = 1; tick <= 2500; ++tick) {
   advanceSpriteFrame(phase,12,tick*10);
   for (uint i = 0; i < 3; ++i) advanceOrbit(scene,ids[i]-1,26,26,tick >= t.delay ? t.scenario : 0,tick*10);
   int32 values[10];
   for (uint i = 0; i < 3; ++i) {
    const Sprite &s = scene.sprites[ids[i]-1];
    values[i*3] = s.renderX; values[i*3+1] = s.renderY; values[i*3+2] = s.visible;
   }
   values[9] = phase.selectedFrame;
   for (uint i = 0; i < 10; ++i) for (uint b = 0; b < 4; ++b) hash = (hash ^ ((uint32(values[i]) >> (b*8)) & 255))*16777619U;
   if (!scene.sprites[19].autoMove) break;
  }
  if (tick != t.ticks || hash != t.hash) return false;
 }
 return true;
}
static int frameOwner(const Scene &scene, uint index) {
 if (index >= scene.sprites.size()) return -1;
 // The file loads sprites in order. Resolve only already loaded sources;
 // this also rejects self references, forward references and cycles.
 for (;;) {
  const Sprite &s = scene.sprites[index];
  if (s.clone == -1) return index;
  if (s.clone <= 0 || uint(s.clone) > index) return -1;
  index = s.clone - 1;
 }
}
bool setSpriteFrameRange(Sprite &sprite, uint frameCount, int32 first, int32 last) {
 // Opcode 48 clamps before passing signed words to 7:0981. The setter
 // changes neither the current frame nor the animation timestamp.
 if (!frameCount) return false;
 if (first < 0) first = 0;
 if (last >= int64(frameCount)) last = frameCount - 1;
 if (first > last || first > 32767 || last > 32767) return false;
 sprite.frameFirst = first; sprite.frameLast = last;
 return true;
}
bool advanceSpriteFrame(Sprite &sprite, uint frameCount, uint32 now) {
 // _load_place passes the first timing field through signed 16-bit AX.
 const int32 period = int16(sprite.frameData[0]);
 if (!sprite.autoFrame || (sprite.autoMove && !sprite.standardMotion) || (sprite.layer != 1 && sprite.layer != 2) ||
     sprite.frameData[1] != 1 || sprite.frameData[2] != 0 || period < 0 ||
     !frameCount || sprite.selectedFrame < 0 || uint(sprite.selectedFrame) >= frameCount) return false;
 if (int32(now - sprite.frameSince) < period) return false;
 // Original updates time to now, never catches up multiple missed frames.
 sprite.frameSince = now;
 const int32 last = sprite.frameLast < 0 ? int32(frameCount - 1) : sprite.frameLast;
 ++sprite.selectedFrame;
 if (sprite.selectedFrame < sprite.frameFirst) sprite.selectedFrame = last;
 else if (sprite.selectedFrame > last) sprite.selectedFrame = sprite.frameFirst;
 return true;
}
bool pointInSprite(const Sprite &sprite, int width, int height, int x, int y) {
 // 7:0ec1 uses signed 16-bit, inclusive comparisons on all four edges.
 const int16 right = int16(int32(sprite.renderX) + width);
 const int16 bottom = int16(int32(sprite.renderY) + height);
 return int16(x) >= sprite.renderX && int16(x) <= right && int16(y) >= sprite.renderY && int16(y) <= bottom;
}
bool advanceSpriteMove(Sprite &s, int width, int height, uint32 now) {
 const int32 period = int16(s.moveData[0]);
 if (!s.standardMotion || !s.autoMove || period < 0 || s.layer != 1 || width <= 0 || height <= 0 || int32(now-s.moveSince) < period) return false;
 s.moveSince = now;
 int16 x = int16(s.renderX+s.moveDX), y = int16(s.renderY+s.moveDY);
 const int16 left = int16(s.rect[3]), top = int16(s.rect[0]);
 const int16 right = int16(s.rect[2]), bottom = int16(s.rect[1]);
 // 7:0c30/0d30 inspect the OLD rectangle, not the proposed location.
 // Runtime deltas can reverse without changing serialized GameSprite data.
 if (s.moveData[3] == 1) {
  if (s.renderX < left) { s.moveDX = int16(-s.moveDX); x = left; }
  else if (int16(s.renderX+width) > right) { s.moveDX = int16(-s.moveDX); x = int16(right-width); }
  if (s.renderY < top) { s.moveDY = int16(-s.moveDY); y = top; }
  else if (int16(s.renderY+height) > bottom) { s.moveDY = int16(-s.moveDY); y = int16(bottom-height); }
 } else if (s.moveData[3] == 2) {
  if (s.renderX > right) x = int16(left-width);
  else if (int16(s.renderX+width) < left) x = right;
  if (s.renderY > bottom) y = int16(top-height);
  else if (int16(s.renderY+height) < top) y = bottom;
 }
 const bool changed = x != s.renderX || y != s.renderY;
 s.renderX = x; s.renderY = y;
 return changed;
}
const Frame *spriteFrameAt(const Scene &scene, uint index, uint frame) {
 const int owner = frameOwner(scene, index);
 if (owner < 0 || frame >= scene.sprites[owner].frames.size()) return nullptr;
 return &scene.sprites[owner].frames[frame];
}
int advancePlanet(Sprite &s, const Sprite &launcher, int width, int height, uint32 now) {
 if (!s.autoMove || !s.planetMotion || s.planetPeriod < 0 || int32(now-s.moveSince) < s.planetPeriod) return 0;
 if (s.planetMotion == 1) {
  // 3:15fd: proposed point already contains the OLD velocity when the
  // callback copies the launcher's current delta for the following step.
  s.moveSince = now;
  s.renderX = int16(s.renderX+s.moveDX); s.renderY = int16(s.renderY+s.moveDY);
  s.moveDX = launcher.moveDX; s.moveDY = launcher.moveDY;
  return 1;
 }
 const int center = int16(int16(s.renderX+width)+s.renderX)/2;
 const int32 setting = s.moveData[0], kind = s.moveData[3];
 s.moveData[0] = s.planetPeriod; s.moveData[3] = 1;
 advanceSpriteMove(s,width,height,now);
 s.moveData[0] = setting; s.moveData[3] = kind;
 // 3:2164-21cb tests the old center after the bounce may reverse dx.
 const bool arrived = setting <= 9 ? center < (10-setting)*56+28 && s.moveDX < 0 : center > (setting-9)*56+28 && s.moveDX > 0;
 if (!arrived) return 1;
 s.autoMove = false; s.planetPeriod = -1;
 const bool correct = setting <= 9 ? setting+s.x == 10 : setting-s.x == 9;
 if (!correct) s.visible = 0;
 return correct ? 3 : 2;
}
uint spriteFrameCount(const Scene &scene, uint index) {
 const int owner = frameOwner(scene,index);
 return owner < 0 ? 0 : scene.sprites[owner].frames.size();
}
bool supportsRocket(const Scene &scene) {
 if (scene.layers != 1 || scene.sprites.size() != 48 || spriteFrameCount(scene,33) != 10) return false;
 for (uint id = 9; id <= 29; ++id)
  if (spriteFrameCount(scene,id-1) != 10 || scene.sprites[id-1].layer != 1) return false;
 for (uint id = 30; id <= 32; ++id)
  if (spriteFrameCount(scene,id-1) != 1) return false;
 return true;
}
bool positionEclipseMoon(Scene &scene, int phase, int quadrant) {
 // Original custom 18/0, 4:3a70-4449. Only the SpriteWorld location is
 // changed; the stored GameSprite coordinates and frame stay intact.
 static const int16 positions[12][4][2] = {
  {{362,42},{315,78},{268,89},{317,46}},
  {{279,48},{238,85},{190,94},{221,64}},
  {{211,60},{167,99},{111,118},{150,76}},
  {{154,96},{107,142},{46,157},{87,116}},
  {{171,140},{115,196},{40,217},{90,165}},
  {{248,171},{196,241},{107,258},{158,192}},
  {{390,193},{310,278},{240,282},{313,193}},
  {{528,179},{473,252},{371,252},{429,183}},
  {{603,144},{548,204},{460,210},{509,144}},
  {{598,103},{551,149},{470,154},{516,104}},
  {{531,63},{492,106},{426,113},{468,69}},
  {{447,48},{411,85},{347,98},{387,58}}
 };
 if (scene.layers != 1 || scene.sprites.size() != 9 || !spriteFrameCount(scene,8) || phase < 0 || phase >= 12 || quadrant < 0 || quadrant >= 4) return false;
 scene.sprites[8].renderX = positions[phase][quadrant][0];
 scene.sprites[8].renderY = positions[phase][quadrant][1];
 return true;
}
static Sprite &rocketSprite(Scene &scene, uint id) { return scene.sprites[id-1]; }
static void rocketLocation(Sprite &s, int x, int y) {
 // Native callbacks change the SpriteWorld rectangle, not GameSprite x/y.
 s.renderX = int16(x); s.renderY = int16(y);
}
bool startRocket(Scene &scene, RocketMotion &motion, int setting) {
 if (!supportsRocket(scene) || setting < 1 || setting > 15) return false;
 // _do_custom 4:2e22-3048, command 14. Keep the previous movement timestamp.
 Sprite &rocket = rocketSprite(scene,34);
 rocketLocation(rocket,0,100); rocket.visible = 1;
 rocketLocation(rocketSprite(scene,30),393,361);
 rocketLocation(rocketSprite(scene,31),462,361);
 rocketLocation(rocketSprite(scene,32),529,414);
 for (uint id = 30; id <= 32; ++id) rocketSprite(scene,id).visible = 1;
 for (uint id = 9; id <= 29; ++id) {
  Sprite &digit = rocketSprite(scene,id);
  digit.autoFrame = true; digit.frameData[0] = 0; digit.frameData[1] = 1; digit.frameData[2] = 0;
 }
 if (setting <= 10) {
  motion.kind = RocketMotion::kSlow; motion.delta = 2;
  rocketLocation(rocket,0,50); rocket.selectedFrame = 9;
 } else if (setting <= 12) {
  motion.kind = RocketMotion::kOrbit; motion.delta = 4;
 } else {
  motion.kind = RocketMotion::kFast; motion.delta = 16;
 }
 return true;
}
static void finishRocketDigits(Scene &scene, int setting) {
 // Identical readout tail in all three original callbacks (3:1715 onward).
 for (uint id = 9; id <= 29; ++id) {
  Sprite &digit = rocketSprite(scene,id); digit.autoFrame = false; digit.selectedFrame = 0;
 }
 rocketSprite(scene,10).selectedFrame = 9;
 rocketSprite(scene,26).selectedFrame = 2;
 rocketSprite(scene,27).selectedFrame = 5;
 if (setting >= 11) {
  for (uint id = 11; id <= 20; ++id) rocketSprite(scene,id).selectedFrame = 9;
  rocketSprite(scene,25).selectedFrame = 1;
 } else if (setting >= 9) {
  for (uint id = 11; id <= 13; ++id) rocketSprite(scene,id).selectedFrame = 9;
  rocketSprite(scene,23).selectedFrame = 3;
 } else if (setting >= 7) {
  for (uint id = 11; id <= 12; ++id) rocketSprite(scene,id).selectedFrame = 9;
  rocketSprite(scene,22).selectedFrame = 1;
 } else if (setting >= 5) {
  rocketSprite(scene,11).selectedFrame = 9;
  rocketSprite(scene,22).selectedFrame = 3;
  rocketSprite(scene,23).selectedFrame = 5;
 } else if (setting >= 3) {
  rocketSprite(scene,11).selectedFrame = 8;
  rocketSprite(scene,22).selectedFrame = 5;
 } else rocketSprite(scene,21).selectedFrame = 1;
}
int advanceRocket(Scene &scene, RocketMotion &motion, int setting, uint32 now) {
 if (motion.kind == RocketMotion::kStopped || int32(now-motion.since) < 10) return 0;
 // _SWProcessSpriteWorld 6:09ee-0abb: one step, proposed x += delta,
 // callback, then commit its rectangle. Missed intervals are not caught up.
 motion.since = now;
 Sprite &rocket = rocketSprite(scene,34);
 const int x = int16(rocket.renderX + motion.delta);
 int y = rocket.renderY;
 bool done = false, success = false;
 auto shiftGauge = [&](uint id, int dy) { Sprite &s = rocketSprite(scene,id); s.renderY = int16(s.renderY+dy); };
 if (motion.kind == RocketMotion::kSlow) {
  y = x*3/10+50;
  if (x <= 245) {
   if (x%4 == 0) shiftGauge(31,1);
   if (x%9 == 0) { shiftGauge(30,1); shiftGauge(32,-1); }
  }
  done = x >= 500;
 } else if (motion.kind == RocketMotion::kOrbit) {
  if (x >= 300) motion.delta = 2;
  y = x <= 300 ? -3*x/10+100 : (x-400)*(x-400)/1000;
  if (x <= 360) rocket.selectedFrame = x/90;
  if (x%24 == 0) { shiftGauge(30,1); shiftGauge(31,1); shiftGauge(32,-1); }
  done = x >= 450; success = done;
 } else {
  if (x >= 180) motion.delta = 10;
  y = -3*x/10+100;
  if (x <= 375) rocket.selectedFrame = x/42;
  if (x <= 180 && x%3 == 0) { shiftGauge(30,20); shiftGauge(31,10); shiftGauge(32,-20); }
  done = x >= 630;
 }
 rocketLocation(rocket,x,y);
 if (!done) return 1;
 if (!success) rocket.visible = 0;
 motion.kind = RocketMotion::kStopped;
 finishRocketDigits(scene,setting);
 return success ? 3 : 2;
}
const Frame *staticSpriteFrame(const Scene &scene, uint index) {
 const int owner = frameOwner(scene,index);
 if (owner < 0) return nullptr;
 const Common::Array<Frame> &frames = scene.sprites[owner].frames;
 int frame = scene.sprites[index].selectedFrame;
 if (frame < 0 && frames.size() == 1) frame = 0;
 return frame >= 0 && uint(frame) < frames.size() ? &frames[frame] : nullptr;
}
void offsetSprite(Sprite &sprite, int32 dx, int32 dy) {
 // Independent wrapping for the original 16-bit rectangle and 32-bit state.
 sprite.renderX = int16(int32(sprite.renderX) + int16(dx));
 sprite.renderY = int16(int32(sprite.renderY) + int16(dy));
 sprite.x = int32(uint32(sprite.x) + uint32(dx));
 sprite.y = int32(uint32(sprite.y) + uint32(dy));
}
void moveSprite(Sprite &sprite, int32 x, int32 y) {
 // _SWMoveSprite receives signed 16-bit coordinates and ignores (0,0).
 // The opcode separately stores both full 32-bit coordinates afterwards.
 const int16 px = int16(x), py = int16(y);
 if (px || py) { sprite.renderX = px; sprite.renderY = py; }
 sprite.x = x; sprite.y = y;
}
bool compositeSprite(Graphics::Surface &dst, const Graphics::Surface &src, const Graphics::Surface &mask, int x, int y) {
 if (src.w != mask.w || src.h != mask.h || src.format != dst.format || mask.format != dst.format) return false;
 const uint32 white = dst.format.RGBToColor(255, 255, 255), black = dst.format.RGBToColor(0, 0, 0);
 // Validate the whole mask before changing the destination.
 for (int sy = 0; sy < mask.h; ++sy) for (int sx = 0; sx < mask.w; ++sx) {
  uint32 m = mask.getPixel(sx, sy);
  if (m != white && m != black) return false;
 }
 // Original 7:055a: (destination XOR image) AND mask XOR image.
 // For binary masks this is image on black, destination on white.
 for (int sy = 0; sy < src.h; ++sy) for (int sx = 0; sx < src.w; ++sx) {
  const int64 dx = int64(x) + sx, dy = int64(y) + sy;
  if (dx >= 0 && dy >= 0 && dx < dst.w && dy < dst.h && mask.getPixel(sx, sy) == black)
   dst.setPixel(dx, dy, src.getPixel(sx, sy));
 }
 return true;
}
bool verifySpriteComposition() {
 Sprite launcher; launcher.moveDY = -2;
 Sprite planet; planet.layer = 1; planet.standardMotion = planet.autoMove = true;
 planet.planetMotion = 1; planet.planetPeriod = 10; planet.moveDY = 2; planet.renderY = 10;
 if (advancePlanet(planet,launcher,8,8,9) || advancePlanet(planet,launcher,8,8,10) != 1 || planet.renderY != 12 || planet.moveDY != -2) return false;
 if (advancePlanet(planet,launcher,8,8,20) != 1 || planet.renderY != 10) return false;
 planet.planetMotion = 2; planet.moveDX = -2; planet.moveDY = 0; planet.renderX = 80;
 planet.rect[1] = 480; planet.rect[2] = 640; planet.moveData[0] = 9; planet.x = 1; planet.visible = 1;
 if (advancePlanet(planet,launcher,8,8,30) != 1 || planet.renderX != 78) return false;
 if (advancePlanet(planet,launcher,8,8,40) != 3 || planet.autoMove || !planet.visible || planet.x != 1 || planet.moveData[0] != 9) return false;
 planet.autoMove = true; planet.planetPeriod = 10; planet.moveData[0] = 10;
 planet.renderX = -1; planet.moveDX = -2;
 if (advancePlanet(planet,launcher,8,8,50) != 1 || planet.renderX != 0 || planet.moveDX != 2) return false;
 planet.renderX = 80;
 if (advancePlanet(planet,launcher,8,8,60) != 1 || advancePlanet(planet,launcher,8,8,70) != 3) return false;
 planet.autoMove = true; planet.planetPeriod = 10; planet.moveData[0] = 1;
 planet.renderX = 527; planet.moveDX = -2;
 if (advancePlanet(planet,launcher,8,8,80) != 2 || planet.visible || planet.autoMove || planet.moveData[0] != 1) return false;
 Sprite moving; moving.layer = 1; moving.autoMove = moving.standardMotion = true;
 moving.rect[0] = 10; moving.rect[1] = 110; moving.rect[2] = 100; moving.rect[3] = 0;
 moving.moveData[0] = 10; moving.moveData[3] = 1; moving.moveDX = 3; moving.moveDY = 4;
 moving.renderX = 89; moving.renderY = 99;
 if (advanceSpriteMove(moving,10,10,9) || !advanceSpriteMove(moving,10,10,10) || moving.renderX != 92 || moving.renderY != 103) return false;
 if (!advanceSpriteMove(moving,10,10,20) || moving.renderX != 90 || moving.renderY != 100 || moving.moveDX != -3 || moving.moveDY != -4) return false;
 if (!advanceSpriteMove(moving,10,10,1000) || moving.renderX != 87 || moving.renderY != 96 || moving.x || moving.y) return false;
 moving.renderX = -1; moving.renderY = 9;
 if (!advanceSpriteMove(moving,10,10,1010) || moving.renderX || moving.renderY != 10 || moving.moveDX != 3 || moving.moveDY != 4) return false;
 moving.moveData[3] = 2; moving.renderX = 100; moving.renderY = 110;
 if (!advanceSpriteMove(moving,10,10,1020) || moving.renderX != 103 || moving.renderY != 114) return false;
 if (!advanceSpriteMove(moving,10,10,1030) || moving.renderX != -10 || moving.renderY != 0) return false;
 moving.moveDX = -3; moving.moveDY = -4;
 if (!advanceSpriteMove(moving,10,10,1040) || moving.renderX != -13 || moving.renderY != -4) return false;
 if (!advanceSpriteMove(moving,10,10,1050) || moving.renderX != 100 || moving.renderY != 110) return false;
 moving.moveSince = 0xfffffff8U;
 if (advanceSpriteMove(moving,10,10,1) || !advanceSpriteMove(moving,10,10,2)) return false;
 moving.moveData[0] = -1;
 if (advanceSpriteMove(moving,10,10,10000)) return false;
 Sprite animated; animated.autoFrame = true; animated.layer = 1;
 animated.frameData[0] = 400; animated.frameData[1] = 1; animated.selectedFrame = 0;
 if (advanceSpriteFrame(animated,2,399) || !advanceSpriteFrame(animated,2,400) || animated.selectedFrame != 1) return false;
 if (!advanceSpriteFrame(animated,2,2000) || animated.selectedFrame != 0 || advanceSpriteFrame(animated,2,2399)) return false;
 animated.frameSince = 0xffffff00U;
 if (advanceSpriteFrame(animated,2,143) || !advanceSpriteFrame(animated,2,144)) return false;
 animated.frameData[0] = -1;
 if (advanceSpriteFrame(animated,2,10000)) return false;
 animated.frameData[0] = 0;
 if (!advanceSpriteFrame(animated,2,144) || !advanceSpriteFrame(animated,2,144)) return false;
 Sprite hit; hit.renderX = 10; hit.renderY = 20; hit.visible = 0;
 if (!pointInSprite(hit, 4, 5, 10, 20) || !pointInSprite(hit, 4, 5, 14, 25) || pointInSprite(hit, 4, 5, 15, 25) || pointInSprite(hit, 4, 5, 14, 26) || pointInSprite(hit, 4, 5, 9, 20)) return false;
 hit.renderX = 32767;
 if (pointInSprite(hit, 4, 5, 32767, 20)) return false;
 Scene chain; Sprite source; source.frames.push_back(Frame()); chain.sprites.push_back(source);
 Sprite clone; clone.clone = 1; clone.x = 90; chain.sprites.push_back(clone);
 clone.clone = 2; chain.sprites.push_back(clone);
 if (staticSpriteFrame(chain,2) != &chain.sprites[0].frames[0] || chain.sprites[1].x != 90) return false;
 chain.sprites[1].clone = 2;
 if (staticSpriteFrame(chain,2)) return false;
 chain.sprites[1].clone = 0;
 if (staticSpriteFrame(chain,1)) return false;
 chain.sprites[1].clone = 1;
 chain.sprites[0].frames.push_back(Frame());
 chain.sprites[0].selectedFrame = 0; chain.sprites[1].selectedFrame = 1;
 if (staticSpriteFrame(chain,0) != &chain.sprites[0].frames[0] || staticSpriteFrame(chain,1) != &chain.sprites[0].frames[1]) return false;
 chain.sprites[1].selectedFrame = 2;
 if (staticSpriteFrame(chain,1)) return false;
 Sprite relative; relative.x = 0x7fffffff; relative.renderX = 32767;
 relative.y = relative.renderY = 10;
 offsetSprite(relative, 1, -5);
 if (relative.x != int32(0x80000000U) || relative.renderX != -32768 || relative.y != 5 || relative.renderY != 5) return false;
 offsetSprite(relative, -1, 5);
 if (relative.x != 0x7fffffff || relative.renderX != 32767 || relative.y != 10) return false;
 Sprite probe; probe.x = probe.renderX = 20; probe.y = probe.renderY = 30;
 moveSprite(probe, 0, 0);
 if (probe.renderX != 20 || probe.renderY != 30 || probe.x || probe.y) return false;
 moveSprite(probe, 65535, 65537);
 if (probe.renderX != -1 || probe.renderY != 1 || probe.x != 65535 || probe.y != 65537) return false;
 Graphics::Surface dst, src, mask;
 const Graphics::PixelFormat f(4, 8, 8, 8, 0, 16, 8, 0, 0);
 dst.create(3, 3, f); src.create(2, 2, f); mask.create(2, 2, f);
 dst.fillRect(Common::Rect(3,3), 0x112233); src.fillRect(Common::Rect(2,2), 0x445566);
 mask.fillRect(Common::Rect(2,2), 0xffffff); mask.setPixel(1,1,0);
 bool ok = compositeSprite(dst,src,mask,-1,-1) && dst.getPixel(0,0) == 0x445566 && dst.getPixel(1,0) == 0x112233;
 mask.setPixel(0,0,0x123456);
 ok = !compositeSprite(dst,src,mask,1,1) && dst.getPixel(2,2) == 0x112233 && ok;
 mask.setPixel(0,0,0xffffff);
 ok = compositeSprite(dst,src,mask,2,2) && dst.getPixel(2,2) == 0x112233 && ok;
 dst.free(); src.free(); mask.free(); return ok;
}
}
