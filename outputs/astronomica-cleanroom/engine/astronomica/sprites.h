// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_SPRITES_H
#define ASTRONOMICA_SPRITES_H
#include "graphics/surface.h"
#include "astronomica/resource.h"
namespace Astronomica {
struct RocketMotion {
 enum Kind { kStopped, kSlow, kOrbit, kFast } kind = kStopped;
 int delta = 0;
 uint32 since = 0;
};
bool supportsRocket(const Scene &scene);
bool positionEclipseMoon(Scene &scene, int phase, int quadrant);
bool startOrbit(Scene &scene, int id, int dx, int dy);
bool advanceOrbit(Scene &scene, uint index, int width, int height, int scenario, uint32 now);
bool orbitAnswer(int scenario, int frame, int choice);
bool verifyOrbitMotion();
int rendezvousRegion(int x, int y);
int astrologyRegion(int x, int y, int cx, int cy, int outer, int inner);
void configureRendezvous(Scene &scene, int mode, int speed);
bool advanceRendezvous(Scene &scene, uint index, int width, int height, uint32 now);
bool verifyRendezvousMotion();
struct BallMotion {
 int scenario = 0, centerX = 0, centerY = 0, side = 2, period = 10;
};
struct CometMotion {
 int kind[50] = {}, partner[50] = {};
 int frame = 4, previousFrame = 0, sound = -1, explosion = 0;
};
bool supportsComet(const Scene &scene, int place);
bool supportsJupiter(const Scene &scene);
void configureJupiter(Scene &scene, CometMotion &motion, int mode, int direction, int speed);
int advanceJupiter(Scene &scene, const int *widths, const int *heights, int width, int height, uint32 now);
bool verifyJupiterMotion();
bool verifyJupiterSetup();
bool verifyJupiterCollision();
bool supportsSpriteLayers(const Scene &scene);
int cometSpeed(int level);
void displayCometSpeed(Scene &scene, int target, int level);
bool verifyCometSetup();
int configureComet(Scene &scene, CometMotion &motion, int32 *locals);
bool advanceComet(Scene &scene, CometMotion &motion, uint index, int width, int height, int target, uint32 now);
bool verifyCometMotion();
void startBall(Sprite &sprite, BallMotion &motion, int scenario);
int advanceBall(Sprite &sprite, BallMotion &motion, int width, int height, uint32 now);
bool verifyBallMotion();
struct ProbeMotion {
 int year = 1991;
 bool yearArmed = false, specialHit = false, flying = false, expired = false;
 int widths[3] = {}, heights[3] = {};
};
void configureProbe(Scene &scene, ProbeMotion &motion, int id);
void launchProbe(Scene &scene, ProbeMotion &motion);
bool advanceProbe(Scene &scene, ProbeMotion &motion, uint index, int32 &state, uint32 now);
bool verifyProbeMotion();
bool startPhoton(Scene &scene, int setting);
bool advancePhoton(Scene &scene, int setting, uint32 now);
bool verifyPhotonMotion();
bool advanceSpriteMove(Sprite &sprite, int width, int height, uint32 now);
int advancePlanet(Sprite &sprite, const Sprite &launcher, int width, int height, uint32 now);
bool verifyRocketOriginalCallbacks(uint32 &hash);
bool startRocket(Scene &scene, RocketMotion &motion, int setting);
// Returns 1 while moving, 2 on failure completion, 3 on successful orbit.
int advanceRocket(Scene &scene, RocketMotion &motion, int setting, uint32 now);
bool compositeSprite(Graphics::Surface &dst, const Graphics::Surface &src, const Graphics::Surface &mask, int x, int y);
bool verifySpriteComposition();
void moveSprite(Sprite &sprite, int32 x, int32 y);
void offsetSprite(Sprite &sprite, int32 dx, int32 dy);
const Frame *staticSpriteFrame(const Scene &scene, uint index);
bool setSpriteFrameRange(Sprite &sprite, uint frameCount, int32 first, int32 last);
bool advanceSpriteFrame(Sprite &sprite, uint frameCount, uint32 now);
bool pointInSprite(const Sprite &sprite, int width, int height, int x, int y);
const Frame *spriteFrameAt(const Scene &scene, uint index, uint frame);
uint spriteFrameCount(const Scene &scene, uint index);
}
#endif
