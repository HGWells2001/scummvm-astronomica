#include <type_traits>
// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/astronomica.h"
#include "astronomica/sprites.h"
#include "astronomica/mentors.h"
#include "astronomica/advice.h"
#include "astronomica/countdown.h"
#include "audio/decoders/wave.h"
#include "audio/audiostream.h"
#include "common/config-manager.h"
#include "common/events.h"
#include "common/endian.h"
#include "common/file.h"
#include "common/fs.h"
#include "common/memstream.h"
#include "common/system.h"
#include "common/random.h"
#include "graphics/font.h"
#include "graphics/cursorman.h"
#include "graphics/fontman.h"
#include "image/bmp.h"
#include "video/qt_decoder.h"
#include "engines/util.h"

namespace Astronomica {
namespace {
const char *const kP519Large[] = {"", "black_b", "asuper", "m82view", "asun", "apulsar"};
const char *const kP519Small[] = {"", "jupno", "m82no", "losun", "msun", "lopulsar"};
enum { kP519Words = 13 + 27 + ScriptRunner::kIdleStateWords };
uint p519ImageId(const Common::String &name, bool large) {
 for (uint i = 1; i <= 5; ++i) if (name.equalsIgnoreCase(large ? kP519Large[i] : kP519Small[i])) return i;
 return 0;
}
uint p519Frames(uint i) { return (i == 24 || i == 26) ? 3 : (i < 4 || i >= 14) ? 2 : 1; }
bool validP519State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 8 ? 1U : 0U)) return false;
  if (i < 8 && (state[301+i*3] != (i < 2 ? 5U : 1U) || state[300+i*3] > (i < 2 ? 5U : 1U))) return false;
 }
 if (state[321] != 1) return false;
 return !(state[306] && state[309] && state[312] && state[315] && state[318]);
}
bool validP519Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 27 || scene.mouseRects.size() != 10 ||
     scene.conditions.size() != 8 || scene.scripts.size() != 3 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 27; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != p519Frames(i) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}

const char *const kP524Images[] = {"", "viewio", "viewmars", "viewmerc", "viewmira", "viewplut", "viewtita", "viewtrit", "viewvenu", "viewmoon"};
enum { kP524Words = 15 + 32 + ScriptRunner::kIdleStateWords };
uint p524Frames(uint i) { return i == 31 ? 8 : (i < 9 || i == 27 || i == 29 || i == 30) ? 2 : 1; }
bool validP524State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 const uint widths[] = {8,8,1,3,1,4};
 const bool help = state[320] != 0;
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 6 || (help && i < 10) ? 1U : 0U)) return false;
  if (state[301+i*3] != (i < 6 ? widths[i] : 0U)) return false;
  // Inert locals retain values from earlier scenes. Only the additional
  // known mentor-return locals are required to be zero here.
  if (i >= 6 && state[302+i*3] && state[300+i*3]) return false;
 }
 const uint choice = state[300], mask = state[303];
 if (!choice || choice > 9 || mask > 255 || state[306] != 1 || state[309] >= 3 || state[312] || state[315]) return false;
 if (choice == 9) return mask == 255;
 return (mask & (1U << (choice-1))) != 0;
}
bool validP524Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 32 || !scene.mouseRects.empty() ||
     scene.conditions.size() != 6 || scene.scripts.size() != 5 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 32; ++i) if (spriteFrameCount(scene,i) != p524Frames(i)) return false;
 return true;
}
bool validP524Animation(uint32 enabled, uint32 period, uint32 step, uint32 mode, uint32 move, uint32 choice) {
 return enabled <= 1 && enabled == uint32(choice == 7) && period == (enabled ? 200U : 0xffffffffU) &&
  step <= 1 && (!enabled || step == 1) && !mode && move == 0xffffffffU;
}

enum { kP528Words = 12 + 9*27 + ScriptRunner::kIdleStateWords };
enum { kP530Words = 12 + 29*27 + ScriptRunner::kIdleStateWords };
enum { kP513Words = 12 + 32*27 + ScriptRunner::kIdleStateWords };
enum { kP517Words = 12 + 11*27 + ScriptRunner::kIdleStateWords };
enum { kRocketWords = 16 + 48*27 + ScriptRunner::kPersistentStateWords };
enum { kBuilderWords = 12 + 60*27 + ScriptRunner::kPersistentStateWords };
bool builderScene(uint place) { return place == 515 || place == 536; }
int builderImageId(const Common::String &name) {
 if (name.empty()) return 0;
 if (name.equalsIgnoreCase("drydock")) return 1;
 if (name.equalsIgnoreCase("pad")) return 2;
 return -1;
}
bool validBuilderState(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validPersistentState(state)) return false;
 const uint widths[] = {5,5,5,6,7,1,1,1,1,1,1,1,1};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 13 ? 1U : 0U) || state[301+i*3] != (i < 13 ? widths[i] : 0U)) return false;
  if (i >= 5 && i < 13 && state[300+i*3] > 1) return false;
 }
 return state[300] <= 31 && state[303] <= 5 && state[306] <= 5 &&
  (state[309] == 0 || state[309] == 4 || state[309] == 5 || state[309] == 6) && state[312] <= 6;
}
bool validBuilderScene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 60 || !scene.mouseRects.empty() ||
     scene.conditions.size() != 13 || scene.scripts.size() != 7 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 60; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i >= 4 && i < 14 ? 2U : 1U) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
bool builderPosition(uint id, int32 x, int32 y, const Sprite &initial) {
 if (x == initial.x && y == initial.y) return true;
 switch (id) {
 case 15: return (x == 73 || x == 99) && y >= 87 && y <= 313;
 case 21: return x == 101 && (y == 3 || y == 42 || y == 81 || y == 120 || y == 159);
 case 27: return x == 112 && y == 99;
 case 28: return x == 112 && (y == 117 || y == 157);
 case 37: return x == 110 && y == 61;
 case 39: return x == 112 && (y == 60 || y == 66);
 case 40: return x == 78 && y >= -148 && y <= 77;
 case 41: return x == 78 && y >= -165 && y <= 35;
 case 42: return x == 79 && y >= -207 && y <= 3;
 default: break;
 }
 static const int slots[18][2] = {{297,208},{297,208},{297,208},{296,14},{439,62},{439,62},
  {297,208},{456,257},{456,257},{456,257},{295,110},{295,110},{436,159},{436,159},{436,159},{436,159},{297,208},{297,208}};
 return id >= 43 && id <= 60 && ((x == 0 && y == 0) || (x == slots[id-43][0] && y == slots[id-43][1]));
}
const int kAuroraLevels[] = {4,3,2,1,2,3,4,3,2,1,2,3,4,3};
const int kAuroraMarkerX[] = {72,87,98,114,131,140,158,174,185,201,216,225,244,261};
const int kAuroraMarkerY[] = {368,390,413,429,411,388,370,386,408,425,408,386,368,384};
const int kAuroraGaugeX[] = {447,477,507,536};
int p517ImageId(const Common::String &name) {
 for (int level = 1; level <= 4; ++level) if (name.equalsIgnoreCase(Common::String::format("aurback%d",level))) return level;
 return -1;
}
bool validP517State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 2 ? 1U : 0U) || state[301+i*3] != (i == 0 ? 4U : i == 1 ? 14U : 0U)) return false;
 }
 return state[303] >= 1 && state[303] <= 14 && state[300] == uint32(kAuroraLevels[state[303]-1]);
}
bool validP517Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 11 || !scene.mouseRects.empty() ||
     scene.conditions.size() != 2 || scene.scripts.size() != 2 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 11; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i == 4 || i == 5 || i == 10 ? 2U : i == 8 || i == 9 ? 4U : 1U) || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
int p513ImageId(const Common::String &name, bool intermediate = false) {
 for (uint i = 1; i <= 9; ++i) {
  if (name.equalsIgnoreCase(Common::String::format("cube%u",i))) return int(i);
  if (intermediate && i < 9 && name.equalsIgnoreCase(Common::String::format("cube%u_50",i))) return int(i+9);
 }
 return -1;
}
bool validP513State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 const uint widths[] = {18,14,14,14,4,14};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 6 ? 1U : 0U) || state[301+i*3] != (i < 6 ? widths[i] : 0U)) return false;
 }
 const uint setting = state[300], scenario = state[303], mask = state[306], wrong = state[312], right = state[315];
 if (!setting || setting > 9 || !scenario || scenario > 14 || mask > 0x3fff || !(mask & (1U << (scenario-1))) || state[309] > 1 || wrong >= 10 || right >= 7) return false;
 uint count = 0; for (uint bits = mask; bits; bits >>= 1) count += bits & 1;
 return count == wrong+right+1;
}
bool validP513Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 32 || !scene.mouseRects.empty() ||
     scene.conditions.size() != 6 || scene.scripts.size() != 4 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 32; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i < 8 ? 2U : i < 11 ? 10U : 1U) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
const char *const kP530Images[] = {"","m3110","m3130","m31100","m31250","m31500",
 "hub10x","hub30x","hub100x","hub250x","hub500x","sat10x","sat30x","sat100x","sat250x","sat",
 "star10x","star30x","star100x","star250x","star500x","glob10x","glob30x","glob100x","glob","glob500x"};
int p530ImageId(const Common::String &name) {
 for (uint i = 0; i < ARRAYSIZE(kP530Images); ++i) if (name.equalsIgnoreCase(kP530Images[i])) return int(i);
 return -1;
}
bool validP530State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 const uint widths[] = {1,1,1,1,1,1,1,1,1,5,5,5,1,5};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 14 ? 1U : 0U) || state[301+i*3] != (i < 14 ? widths[i] : 0U)) return false;
  if ((i < 9 || i == 12) && state[300+i*3] > 1) return false;
 }
 const uint choice = state[327], mask = state[333], round = state[339];
 if (!choice || choice > 5 || mask > 31 || !(mask & (1U << (choice-1))) || !round || round > 3 || state[330] > 5 || (round == 3 && state[336])) return false;
 uint used = 0; for (uint bits = mask; bits; bits >>= 1) used += bits & 1;
 return used == round && state[315] == uint32(choice == 1 || choice == 5) && state[312] == uint32(choice != 1 && choice != 5);
}
bool validP530Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 29 || scene.mouseRects.size() != 3 ||
     scene.conditions.size() != 14 || scene.scripts.size() != 11 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 29; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i < 4 ? 2U : 1U) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
bool validP528State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 const uint widths[] = {13,4,4,1,1};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 5 ? 1U : 0U) || state[301+i*3] != (i < 5 ? widths[i] : 0U)) return false;
 }
 return state[300] < 12 && state[303] < 4 && !state[306] && state[309] <= 1 && state[312] <= 1 && !(state[309] && state[312]);
}
bool validP528Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 9 || !scene.mouseRects.empty() ||
     scene.conditions.size() != 5 || !scene.scripts.empty() || !scene.movies.empty()) return false;
 for (uint i = 0; i < 9; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i == 7 ? 12U : i == 8 ? 1U : 2U) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
uint p528ImageId(const Common::String &name, bool moon) {
 for (uint i = 1; i <= 12; ++i) if (name.equalsIgnoreCase(Common::String::format(moon ? "mo_s%u" : "ge_s%u",i))) return i;
 return 0;
}
bool p528Tall(uint id) { return id == 1 || id == 2 || id == 10 || id == 11; }
bool validP528History(const Common::Array<uint32> &state, uint pair, uint tall) {
 const uint phase = state[300];
 if (!pair) return phase == 11 && !tall && !state[309] && !state[312];
 if (pair != 12-phase) return false;
 if (!phase) return tall == 0 || tall == 1;
 return tall == (phase == 1 ? 11U : phase < 10 ? 10U : phase == 10 ? 2U : 1U);
}
const Command *p528PhaseCommand(const Scene &scene, uint phase) {
 const Script &script = scene.sprites[4].click;
 for (uint i = 1; i < script.size(); ++i) {
  const Command &c = script[i-1], &move = script[i];
  if (c.opcode == 31 && c.args.size() == 6 && c.args[0] == 1 && c.args[1] == 0 && c.args[2] == int32(phase) && !c.args[4] &&
      move.opcode == 24 && move.args.size() == 4 && move.args[0] == 8 && move.args[3] == int32(11-phase)) return &move;
 }
 return nullptr;
}
enum { kP508StateWords = 10 + ScriptRunner::kIdleStateWords };
enum { kP526SpriteWords = 27, kP526Words = 12 + 23*kP526SpriteWords + ScriptRunner::kIdleStateWords };
const char *const kP526Images[] = {"","s1","s2","s3","s4","s5","s6"};
int p526ImageId(const Common::String &name) {
 for (uint i = 0; i < 7; ++i) if (name.equalsIgnoreCase(kP526Images[i])) return i;
 return -1;
}
uint p526Frames(uint i) { return i == 17 || i == 19 || i == 21 ? 12 : i < 5 || (i >= 11 && i <= 16) ? 2 : 1; }
bool validP526State(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validIdleState(state)) return false;
 const uint widths[] = {6,9,6,6,1,4,1};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 7 ? 1U : 0U) || state[301+i*3] != (i < 7 ? widths[i] : 0U)) return false;
 }
 if (state[300] > 63 || state[303] != 1 || !state[306] || state[306] > 6 || state[309] > 6 ||
     state[312] > 1 || state[315] > 3 || state[318] > 1) return false;
 return !state[300] || (state[300] & (1U << (state[306]-1)));
}
bool validP526Scene(const Scene &scene) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != 23 || scene.mouseRects.size() != 6 ||
     scene.conditions.size() != 7 || scene.scripts.size() != 2 || !scene.movies.empty()) return false;
 for (uint i = 0; i < 23; ++i) if (spriteFrameCount(scene,i) != p526Frames(i)) return false;
 return true;
}
void p526SpriteWords(const Sprite &s, Common::Array<uint32> &words) {
 for (int32 v : {s.visible,s.selectedFrame,s.x,s.y,int32(s.renderX),int32(s.renderY),int32(s.autoFrame),int32(s.autoMove),
      int32(s.frameSince),int32(s.moveSince),int32(s.standardMotion),int32(s.moveDX),int32(s.moveDY),int32(s.orbitMotion),
      s.orbitSideX,s.orbitSideY,s.frameFirst,s.frameLast,int32(s.clickEnabled)}) words.push_back(uint32(v));
 for (int32 v : s.frameData) words.push_back(uint32(v));
 for (int32 v : s.moveData) words.push_back(uint32(v));
}
void p526RestoreSprite(Sprite &s, const uint32 *w) {
 s.visible = int32(w[0]); s.selectedFrame = int32(w[1]); s.x = int32(w[2]); s.y = int32(w[3]);
 s.renderX = int16(w[4]); s.renderY = int16(w[5]); s.autoFrame = w[6] != 0; s.autoMove = w[7] != 0;
 s.frameSince = w[8]; s.moveSince = w[9]; s.standardMotion = w[10] != 0; s.moveDX = int16(w[11]); s.moveDY = int16(w[12]);
 s.orbitMotion = w[13] != 0; s.orbitSideX = int32(w[14]); s.orbitSideY = int32(w[15]);
 s.frameFirst = int32(w[16]); s.frameLast = int32(w[17]); s.clickEnabled = w[18] != 0;
 for (uint i = 0; i < 3; ++i) s.frameData[i] = int32(w[19+i]);
 for (uint i = 0; i < 5; ++i) s.moveData[i] = int32(w[22+i]);
}
bool validRocketState(const Common::Array<uint32> &state) {
 if (!ScriptRunner::validPersistentState(state) || state[300] > 15) return false;
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != uint32(i == 0) || state[301+i*3] != (i == 0 ? 16U : 0U)) return false;
 }
 return true;
}
bool validRocketScene(const Scene &scene) {
 return supportsRocket(scene) && !scene.mode && scene.layers == 1 && scene.sprites.size() == 48 &&
  scene.conditions.size() == 1 && scene.scripts.size() == 1 && scene.mouseRects.empty() && scene.movies.empty();
}
void rocketReadout(int *digits, int setting) {
 for (uint i = 0; i < 21; ++i) digits[i] = 0;
 digits[0] = 9; digits[16] = 2; digits[17] = 5;
 if (setting >= 11) { for (uint i = 1; i <= 10; ++i) digits[i] = 9; digits[15] = 1; }
 else if (setting >= 9) { for (uint i = 1; i <= 3; ++i) digits[i] = 9; digits[13] = 3; }
 else if (setting >= 7) { digits[1] = digits[2] = 9; digits[12] = 1; }
 else if (setting >= 5) { digits[1] = 9; digits[12] = 3; digits[13] = 5; }
 else if (setting >= 3) { digits[1] = 8; digits[12] = 5; }
 else digits[11] = 1;
}
bool validRocketSprites(const Common::Array<uint32> &words, const Scene &original, const Common::Array<uint32> &state, uint32 delta, uint32 since) {
 if (words.size() != 48*27 || !validRocketScene(original) || !validRocketState(state) || (delta != 0 && delta != 2 && delta != 10) || (!delta && since)) return false;
 Scene expected = original;
 for (Sprite &s : expected.sprites) s.selectedFrame = 0;
 expected.sprites[6].visible = state[300] >= 1;
 for (uint id = 35; id <= 48; ++id) expected.sprites[id-1].visible = state[300] >= id-33;
 for (uint i = 29; i <= 31; ++i) expected.sprites[i].visible = delta != 0;
 expected.sprites[33].visible = 0;
 if (delta) {
  const bool fast = delta == 10; const int slowY[] = {374,422,401},fastY[] = {421,391,354};
  for (uint i = 0; i < 3; ++i) expected.sprites[29+i].renderY = fast ? fastY[i] : slowY[i];
  expected.sprites[33].renderX = fast ? 632 : 500; expected.sprites[33].renderY = fast ? -89 : 200;
  expected.sprites[33].selectedFrame = fast ? 8 : 9;
  bool readout = false;
  for (int setting = delta == 10 ? 13 : 1; setting <= (delta == 10 ? 13 : 10); setting += 2) {
   int digits[21]; rocketReadout(digits,setting); bool match = true;
   for (uint i = 0; i < 21; ++i) if (words[(8+i)*27+1] != uint32(digits[i])) match = false;
   if (match) readout = true;
  }
  if (!readout) return false;
  for (uint i = 8; i <= 28; ++i) { expected.sprites[i].selectedFrame = words[i*27+1]; expected.sprites[i].frameSince = since; expected.sprites[i].frameData[0] = -1; expected.sprites[i].frameData[1] = 1; }
 }
 Common::Array<uint32> baseline; for (const Sprite &s : expected.sprites) p526SpriteWords(s,baseline);
 return words == baseline;
}

bool validP526Sprite(const uint32 *w, const Sprite &initial, uint i) {
 for (uint n : {0U,6U,7U,10U,13U,14U,15U,18U}) if (w[n] > 1) return false;
 if (w[7] || w[16] != uint32(initial.frameFirst) || w[17] != uint32(initial.frameLast) || w[18] != uint32(initial.clickEnabled) ||
     w[1] >= p526Frames(i) || (i != 17 && i != 19 && i != 21 && w[1])) return false;
 for (uint n : {4U,5U}) if (int32(w[n]) < -640 || int32(w[n]) > 1280) return false;
 if (int32(w[11]) < -2 || int32(w[11]) > 2 || int32(w[12]) < -1 || int32(w[12]) > 1) return false;
 const bool orbit = i == 19 || i == 21 || i == 22;
 if (!orbit && (w[2] != uint32(initial.x) || w[3] != uint32(initial.y) || w[10] || w[11] || w[12] || w[13] || w[14] || w[15] ||
     memcmp(w+22,initial.moveData,sizeof(initial.moveData)))) return false;
 if (!orbit && i != 20 && (w[4] != uint32(int32(initial.renderX)) || w[5] != uint32(int32(initial.renderY)))) return false;
 if (orbit && (w[2] != uint32(initial.x) || (w[3] != uint32(initial.y) && w[3] != (i == 22 ? 70U : 120U)) ||
     (w[22] != 0 && w[22] != 10) || (w[23] != 0 && w[23] != 200 && w[23] != 250) ||
     (w[24] != 0 && w[24] != 100 && w[24] != 125) || w[25] || w[26])) return false;
 if (i == 17) return (w[19] == 100 || w[19] == 0xffffffffU) && w[6] == uint32(w[19] == 100) && w[20] == 1 && !w[21];
 if (i == 19 || i == 21) return w[6] == 1 && w[19] == 30 && w[20] == 1 && !w[21];
 if (i == 22) return !w[6] && (w[19] == 0 || w[19] == 0xffffffffU) && !w[20] && !w[21];
 return !w[6] && !memcmp(w+19,initial.frameData,sizeof(initial.frameData));
}
bool validP528Sprites(const Common::Array<uint32> &words, const Scene &original, const Common::Array<uint32> &state) {
 if (words.size() != 9*27 || !validP528Scene(original)) return false;
 Scene expected = original;
 for (Sprite &s : expected.sprites) s.selectedFrame = 0;
 const Command *move = p528PhaseCommand(original,state[300]); if (!move) return false;
 Sprite &earth = expected.sprites[7]; earth.x = move->args[1]; earth.y = move->args[2];
 earth.renderX = int16(earth.x); earth.renderY = int16(earth.y); earth.selectedFrame = move->args[3];
 if (!positionEclipseMoon(expected,state[300],state[303])) return false;
 Common::Array<uint32> baseline;
 for (const Sprite &s : expected.sprites) p526SpriteWords(s,baseline);
 for (uint i = 0; i < words.size(); ++i) if (i%27 != 8 && i%27 != 9 && words[i] != baseline[i]) return false;
 return true;
}
struct QuestionSaveProfile { uint place, version, sprites, locals; int x, y, width, height; uint widths[6]; };
bool validP513Sprites(const Common::Array<uint32> &words, const Scene &original) {
 if (words.size() != 32*27 || !validP513Scene(original)) return false;
 for (uint i = 0; i < 32; ++i) {
  Sprite s = original.sprites[i]; s.selectedFrame = 0;
  Common::Array<uint32> baseline; p526SpriteWords(s,baseline);
  const uint32 *w = &words[i*27];
  if (w[0] > 1 || (i < 8 && w[0] != baseline[0]) || (i == 31 && w[0]) || w[1] > (i >= 8 && i <= 10 ? 9U : 0U)) return false;
  const bool stopped = i == 31 && w[10] == 1 && int32(w[4]) >= 443 && int32(w[4]) <= 451 && w[19] == 0xffffffffU && w[22] == 0xffffffffU;
  for (uint field = 2; field < 27; ++field) {
   if (field == 8 || field == 9 || (stopped && (field == 4 || field == 10 || field == 19 || field == 22))) continue;
   if (w[field] != baseline[field]) return false;
  }
 }
 return true;
}
struct VariantSaveProfile { uint place, sprites, choices, answers; };
bool validBuilderSprites(const Common::Array<uint32> &words, const Scene &original) {
 if (words.size() != 60*27 || !validBuilderScene(original)) return false;
 for (uint i = 0; i < 60; ++i) {
  Sprite s = original.sprites[i]; s.selectedFrame = 0;
  Common::Array<uint32> baseline; p526SpriteWords(s,baseline);
  const uint32 *w = &words[i*27];
  if (w[0] > 1 || (i < 14 && w[0] != baseline[0]) || w[1] ||
      !builderPosition(i+1,int32(w[2]),int32(w[3]),s) || !builderPosition(i+1,int32(w[4]),int32(w[5]),s)) return false;
  // Only part icons receive a zero setter that retains an earlier rendered
  // position. Every nonzero setter, and each launch offset, updates both.
  if ((i < 42 || w[2] || w[3]) && (w[2] != w[4] || w[3] != w[5])) return false;
  for (uint field = 6; field < 27; ++field) if (field != 8 && field != 9 && w[field] != baseline[field]) return false;
 }
 return true;
}
bool validP517Sprites(const Common::Array<uint32> &words, const Scene &original, uint setting) {
 if (words.size() != 11*27 || !validP517Scene(original) || setting < 1 || setting > 14) return false;
 const uint level = kAuroraLevels[setting-1];
 for (uint i = 0; i < 11; ++i) {
  Sprite s = original.sprites[i]; s.selectedFrame = 0;
  if (i == 6) moveSprite(s,kAuroraGaugeX[level-1],361);
  if (i == 7) moveSprite(s,kAuroraMarkerX[setting-1],kAuroraMarkerY[setting-1]);
  Common::Array<uint32> baseline; p526SpriteWords(s,baseline);
  const uint32 *w = &words[i*27];
  const bool cycle = i >= 8, active = cycle && level == i-6;
  if (w[0] != (cycle ? uint32(active) : baseline[0]) || w[6] != uint32(active) ||
      w[1] >= (i == 10 ? 2U : cycle ? 4U : 1U)) return false;
  if (cycle && (w[19] != (active ? (i == 10 ? 300U : 100U) : 0xffffffffU) ||
      w[20] > 1 || (active && w[20] != 1) || w[21] ||
      (active ? w[22] != 0 && w[22] != 0xffffffffU : w[22] != 0xffffffffU))) return false;
  for (uint field = 2; field < 27; ++field) {
   if (field == 8 || field == 9 || field == 6 || (cycle && (field == 19 || field == 20 || field == 22))) continue;
   if (w[field] != baseline[field]) return false;
  }
 }
 return true;
}
const VariantSaveProfile *variantProfile(uint place) {
 static const VariantSaveProfile profiles[] = {{506,14,5,3},{531,14,5,4},{532,12,4,3},{533,12,4,3},{534,18,7,5},{535,12,4,3}};
 for (const VariantSaveProfile &p : profiles) if (p.place == place) return &p;
 return nullptr;
}
bool validVariantScene(const Scene &scene, const VariantSaveProfile &p) {
 if (scene.mode || scene.layers != 1 || scene.sprites.size() != p.sprites || scene.mouseRects.size() != 1 ||
     scene.conditions.size() != 7 || scene.scripts.size() != 2 || !scene.movies.empty()) return false;
 for (uint i = 0; i < p.sprites; ++i) {
  const Sprite &s = scene.sprites[i];
  if (spriteFrameCount(scene,i) != (i < 4+p.choices ? 2U : 1U) || s.autoFrame || s.autoMove || s.dragEnabled || s.cursor) return false;
 }
 return true;
}
bool validVariantValues(const Common::Array<uint32> &state, const VariantSaveProfile &p) {
 if (!ScriptRunner::validVariantState(state)) return false;
 const uint widths[] = {p.answers,p.choices == 7 ? 8U : 6U,1,1};
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1 || state[300+i*3+2] != (i < 4 ? 1U : 0U) || state[301+i*3] != (i < 4 ? widths[i] : 0U)) return false;
 }
 // Unknown local values are inert, but can retain data from a previous scene.
 // Keep them verbatim rather than restricting valid entry histories.
 return state[300] < (1U << p.answers)-1 && state[303] <= p.choices && state[306] == 1 && state[309] <= 1;
}
bool validVariantSprites(const Common::Array<uint32> &words, const Scene &original, const VariantSaveProfile &p) {
 if (words.size() != p.sprites*27 || !validVariantScene(original,p)) return false;
 for (uint i = 0; i < p.sprites; ++i) {
  Sprite s = original.sprites[i]; s.selectedFrame = 0;
  Common::Array<uint32> baseline; p526SpriteWords(s,baseline);
  const uint32 *w = &words[i*27];
  if (w[0] > 1 || (i < 4+p.choices && w[0] != baseline[0]) || w[1] > uint32(i >= 4 && i < 4+p.choices)) return false;
  for (uint field = 2; field < 27; ++field) if (field != 8 && field != 9 && w[field] != baseline[field]) return false;
 }
 return true;
}
bool validP530Sprites(const Common::Array<uint32> &words, const Scene &original) {
 if (words.size() != 29*27 || !validP530Scene(original)) return false;
 for (uint i = 0; i < 29; ++i) {
  Sprite s = original.sprites[i]; s.selectedFrame = 0;
  Common::Array<uint32> baseline; p526SpriteWords(s,baseline);
  const uint32 *w = &words[i*27];
  const bool visibility = i == 5 || i == 6 || i == 12 || i == 13 || i == 14 || (i >= 16 && i <= 28);
  if (w[0] > 1 || (!visibility && w[0] != baseline[0])) return false;
  const bool moved = i >= 23 && w[2] == 466 && w[3] == 115 && w[4] == 466 && w[5] == 115;
  for (uint field = 1; field < 27; ++field) {
   if (field == 8 || field == 9 || (moved && field >= 2 && field <= 5)) continue;
   if (w[field] != baseline[field]) return false;
  }
 }
 return true;
}
const QuestionSaveProfile *questionProfile(uint place) {
 static const QuestionSaveProfile profiles[] = {
  {508,3,23,6,67,354,508,108,{18,18,1,3,8,10}},
  {505,4,18,4,254,362,135,86,{8,8,4,1,0,0}}
 };
 for (const QuestionSaveProfile &profile : profiles) if (profile.place == place) return &profile;
 return nullptr;
}
uint questionFrames(const QuestionSaveProfile &profile, uint index) {
 return (profile.place == 508 ? index < 4 : index < 8 && !(index & 1)) ? 2 : 1;
}
bool validQuestionLocals(const Common::Array<uint32> &state, const QuestionSaveProfile &profile) {
 if (!ScriptRunner::validIdleState(state)) return false;
 for (uint i = 0; i < 100; ++i) {
  if (state[i*3+2] != 1) return false; // All globals are required.
  if (state[300+i*3+2] != (i < profile.locals ? 1U : 0U)) return false;
  if (i < profile.locals && state[301+i*3] != profile.widths[i]) return false;
 }
 const uint choice = state[300], mask = state[303], wrong = state[309], right = state[312];
 if (profile.place == 505) {
  if (choice < 1 || choice > 8 || mask > 255 || !(mask & (1U << (choice-1))) || state[306] >= 3 || state[309] != 1) return false;
  uint used = 0; for (uint bits = mask; bits; bits >>= 1) used += bits & 1;
  return state[306] < used;
 }
 if (choice < 1 || choice > 18 || mask > 0x3ffff || !(mask & (1U << (choice-1))) ||
     state[306] != 1 || wrong >= 3 || right >= 8 || state[315] != 0) return false;
 uint used = 0; for (uint bits = mask; bits; bits >>= 1) used += bits & 1;
 return used == wrong+right+1;
}
const Command *questionImage(const Scene &scene, uint choice, const QuestionSaveProfile &profile) {
 if (scene.mode != 0 || scene.layers != 1 || scene.sprites.size() != profile.sprites || scene.scripts.size() != 3 ||
     scene.conditions.size() != profile.locals || scene.mouseRects.size() != (profile.place == 505 ? 10U : 0U) || !scene.movies.empty()) return nullptr;
 const Script &script = scene.scripts[1];
 for (uint i = 1; i < script.size(); ++i) {
  const Command &condition = script[i-1], &image = script[i];
  if (condition.opcode == 31 && condition.args.size() == 6 && condition.args[0] == 1 && condition.args[1] == 0 &&
      condition.args[2] == int32(choice) && condition.args[4] == 0 && image.opcode == 20 && image.args.size() == 2 &&
      image.args[0] == profile.x && image.args[1] == profile.y) return &image;
 }
 return nullptr;
}
}
bool AstronomicaEngine::canSaveQuestion() const {
 const QuestionSaveProfile *profile = questionProfile(_place);
 if (!profile || !_runner.idle() || _pendingImage.w || _movie ||
     (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound)) return false;
 Common::Array<uint32> state;
 if (!_runner.exportIdleState(state) || !validQuestionLocals(state,*profile)) return false;
 const Command *question = questionImage(_scene,state[300],*profile);
 if (!question || !_displayedImageName.equalsIgnoreCase(question->text) || _questionSaveBaseline.size() != _scene.sprites.size()) return false;
 if (_loopSound != -1 && _loopSound != 0) return false;
 if (_mixer->isSoundHandleActive(_soundHandle) && !_loopEnabled) return false;
 if (_place == 505) {
  if (_hoverSprites.size() != 18 || _hoverRects.size() != 10) return false;
  for (const HoverTarget &hover : _hoverSprites) if (hover.entered && !hover.ready) return false;
  for (const HoverTarget &hover : _hoverRects) if (hover.entered && !hover.ready) return false;
 }
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  const Sprite &sprite = _scene.sprites[i];
  const Sprite &initial = _questionSaveBaseline[i];
  if (sprite.x != initial.x || sprite.y != initial.y || sprite.clickEnabled != initial.clickEnabled ||
      sprite.frameFirst != initial.frameFirst || sprite.frameLast != initial.frameLast ||
      memcmp(sprite.frameData,initial.frameData,sizeof(sprite.frameData)) ||
      memcmp(sprite.moveData,initial.moveData,sizeof(sprite.moveData))) return false;
  if (sprite.autoFrame || sprite.autoMove || sprite.standardMotion || sprite.planetMotion || sprite.orbitMotion ||
      sprite.dragEnabled || sprite.visible < 0 || sprite.visible > 1 || sprite.selectedFrame < -1 ||
      sprite.selectedFrame > 0 || spriteFrameCount(_scene,i) != questionFrames(*profile,i)) return false;
 }
 return true;
}
Common::Error AstronomicaEngine::saveQuestion(Common::WriteStream *stream) {
 if (!canSaveQuestion()) return Common::kWritingFailed;
 Common::Array<uint32> state; _runner.exportIdleState(state);
 uint32 visible = 0, selected = 0;
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  if (_scene.sprites[i].visible) visible |= 1U << i;
  if (_scene.sprites[i].selectedFrame == 0) selected |= 1U << i;
 }
 const uint32 header[] = {uint32(_place),_puzzlesCompleted,scriptClock(),uint32(_previousPlace),visible,selected,
  uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle))};
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(questionProfile(_place)->version);
 uint32 hash = 2166136261U;
 for (uint32 word : header) { stream->writeUint32LE(word); hash = (hash ^ word)*16777619U; }
 for (uint32 word : state) { stream->writeUint32LE(word); hash = (hash ^ word)*16777619U; }
 if (_place == 505) {
  uint32 sprites = 0, rects = 0;
  for (uint i = 0; i < _hoverSprites.size(); ++i) if (_hoverSprites[i].entered) sprites |= 1U << i;
  for (uint i = 0; i < _hoverRects.size(); ++i) if (_hoverRects[i].entered) rects |= 1U << i;
  for (uint32 word : {sprites,rects}) { stream->writeUint32LE(word); hash = (hash ^ word)*16777619U; }
 }
 stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadQuestion(Common::SeekableReadStream *stream, uint32 version) {
 const QuestionSaveProfile &profile = *questionProfile(version == 3 ? 508 : 505);
 if (stream->size()-stream->pos() < (kP508StateWords+1+(version == 4 ? 2 : 0))*4) return Common::kReadingFailed;
 uint32 header[10], hash = 2166136261U;
 for (uint32 &word : header) { word = stream->readUint32LE(); hash = (hash ^ word)*16777619U; }
 Common::Array<uint32> state; state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &word : state) { word = stream->readUint32LE(); hash = (hash ^ word)*16777619U; }
 uint32 hover[2] = {};
 if (version == 4) for (uint32 &word : hover) { word = stream->readUint32LE(); hash = (hash ^ word)*16777619U; }
 if (stream->readUint32LE() != hash || stream->err() || !validQuestionLocals(state,profile) || header[0] != profile.place ||
     (header[3] > 537 && header[3] != 0xffffffffU) || header[4] >= (1U << profile.sprites) || header[5] >= (1U << profile.sprites) ||
     (header[6] != 0 && header[6] != 0xffffffffU) || header[7] > 1 || header[9] > 1 ||
     (header[9] && (header[6] != 0 || !header[7])) || (hover[0] & ~0x55U) || (hover[1] & ~0x3ffU)) return Common::kReadingFailed;
 if (version == 4 && (!ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input"))) return Common::kReadingFailed;
 // Preflight the original question image and its invariant footprint before
 // changing any live state. Each scene replaces one complete rectangle.
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::String::format("PLACES/P%u/MEGAFILE.HYP",profile.place))))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed)) return Common::kReadingFailed;
 const Command *question = questionImage(parsed,state[300],profile);
 if (!question) return Common::kReadingFailed;
 for (uint i = 0; i < parsed.sprites.size(); ++i)
  if (spriteFrameCount(parsed,i) != questionFrames(profile,i) || parsed.sprites[i].autoFrame || parsed.sprites[i].autoMove) return Common::kReadingFailed;
 Graphics::Surface *picture = openBackgroundImage(question->text,profile.place);
 if (!picture) return Common::kReadingFailed;
 if (picture->w != profile.width || picture->h != profile.height) { picture->free(); delete picture; return Common::kReadingFailed; }
 if (!loadPlace(profile.place,false,true)) { picture->free(); delete picture; return Common::kReadingFailed; }
 // loadPlace rebuilt programs, resources and handlers but deliberately did
 // not enqueue startup, play its introduction or consume a random draw.
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[6]); _loopEnabled = header[7] != 0; _lastSoundAt = header[8];
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  _scene.sprites[i].visible = (header[4] >> i) & 1;
  _scene.sprites[i].selectedFrame = (header[5] & (1U << i)) ? 0 : -1;
 }
 for (uint i = 0; i < _hoverSprites.size(); ++i) _hoverSprites[i].entered = (hover[0] & (1U << i)) != 0;
 for (uint i = 0; i < _hoverRects.size(); ++i) _hoverRects[i].entered = (hover[1] & (1U << i)) != 0;
 _pendingImage.copyFrom(*picture); _pendingImageName = question->text; _pendingImageX = profile.x; _pendingImageY = profile.y;
 picture->free(); delete picture; displayBackgroundImage(); presentScene();
 // Ambient music restarts at its beginning; foreground speech is never cut
 // by an admitted save. Retain its last-end epoch for the five-second delay.
 if (header[9]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveP519() const {
 if (_place != 519 || !_runner.idle() || _pendingImage.w || _movie || !validP519Scene(_scene) ||
     !_p519LargeImage || _p519LargeImage > 5 || _p519SmallImage > 5 || _questionSaveBaseline.size() != 27 ||
     _hoverSprites.size() != 27 || _hoverRects.size() != 10) return false;
 if ((_loopSound != -1 && _loopSound != 0) ||
     (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state;
 if (!_runner.exportIdleState(state) || !validP519State(state)) return false;
 for (const HoverTarget &hover : _hoverSprites) if (hover.entered) return false;
 for (const HoverTarget &hover : _hoverRects) if (!hover.ready) return false;
 for (uint i = 0; i < 27; ++i) {
  const Sprite &s = _scene.sprites[i], &initial = _questionSaveBaseline[i];
  if (s.x != initial.x || s.y != initial.y || s.clickEnabled != initial.clickEnabled ||
      s.frameFirst != initial.frameFirst || s.frameLast != initial.frameLast ||
      memcmp(s.frameData,initial.frameData,sizeof(s.frameData)) || memcmp(s.moveData,initial.moveData,sizeof(s.moveData)) ||
      s.standardMotion || s.planetMotion || s.orbitMotion || s.visible < 0 || s.visible > 1 ||
      s.selectedFrame < -1 || s.selectedFrame >= int(p519Frames(i)) || (i < 4 && s.selectedFrame > 0)) return false;
 }
 return true;
}
Common::Error AstronomicaEngine::saveP519(Common::WriteStream *stream) {
 if (!canSaveP519()) return Common::kWritingFailed;
 uint32 visible = 0, hover = 0;
 for (uint i = 0; i < 27; ++i) if (_scene.sprites[i].visible) visible |= 1U << i;
 for (uint i = 0; i < 10; ++i) if (_hoverRects[i].entered) hover |= 1U << i;
 const uint32 header[] = {519,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),visible,uint32(_loopSound),
  uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),_p519LargeImage,_p519SmallImage,0,hover};
 Common::Array<uint32> state; _runner.exportIdleState(state);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(5);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 value) { stream->writeUint32LE(value); hash = (hash ^ value)*16777619U; };
 for (uint32 value : header) word(value);
 for (const Sprite &sprite : _scene.sprites) word(uint32(sprite.selectedFrame));
 for (uint32 value : state) word(value);
 stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP519(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP519Words+1)*4 ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[13], frames[27], hash = 2166136261U;
 auto word = [&]() { const uint32 value = stream->readUint32LE(); hash = (hash ^ value)*16777619U; return value; };
 for (uint32 &value : header) value = word();
 for (uint32 &value : frames) value = word();
 Common::Array<uint32> state; state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &value : state) value = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP519State(state) || header[0] != 519 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || header[4] >= (1U << 27) ||
     (header[5] != 0 && header[5] != 0xffffffffU) || header[6] > 1 || header[8] > 1 ||
     (header[8] && (header[5] != 0 || !header[6])) || !header[9] || header[9] > 5 || header[10] > 5 ||
     header[11] || (header[12] & ~0x3ffU)) return Common::kReadingFailed;
 for (uint i = 0; i < 27; ++i)
  if (frames[i] != 0xffffffffU && (frames[i] >= p519Frames(i) || (i < 4 && frames[i]))) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P519/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP519Scene(parsed)) return Common::kReadingFailed;
 // Decode both originals before mutating the live scene. Loading the large
 // image first reconstructs the border retained around the last small image.
 Graphics::Surface *large = openBackgroundImage(kP519Large[header[9]],519);
 Graphics::Surface *small = header[10] ? openBackgroundImage(kP519Small[header[10]],519) : nullptr;
 auto release = [&]() { if (large) { large->free(); delete large; } if (small) { small->free(); delete small; } };
 if (!large || large->w != 143 || large->h != 108 || (header[10] && (!small || small->w != 99 || small->h != 99))) {
  release(); return Common::kReadingFailed;
 }
 if (!loadPlace(519,false,true)) { release(); return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[5]); _loopEnabled = header[6] != 0; _lastSoundAt = header[7];
 for (uint i = 0; i < 27; ++i) {
  _scene.sprites[i].visible = (header[4] >> i) & 1; _scene.sprites[i].selectedFrame = int32(frames[i]);
 }
 for (uint i = 0; i < 10; ++i) _hoverRects[i].entered = (header[12] & (1U << i)) != 0;
 _pendingImage.copyFrom(*large); _pendingImageName = kP519Large[header[9]]; _pendingImageX = 258; _pendingImageY = 356;
 displayBackgroundImage();
 if (small) {
  _pendingImage.copyFrom(*small); _pendingImageName = kP519Small[header[10]]; _pendingImageX = 282; _pendingImageY = 358;
  displayBackgroundImage();
 }
 release(); presentScene();
 if (header[8]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}

bool AstronomicaEngine::canSaveP524() const {
 if (_place != 524 || !_runner.idle() || _pendingImage.w || _movie || !validP524Scene(_scene) ||
     _questionSaveBaseline.size() != 32) return false;
 if ((_loopSound != -1 && _loopSound != 0) ||
     (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state;
 if (!_runner.exportIdleState(state) || !validP524State(state) || !_displayedImageName.equalsIgnoreCase(kP524Images[state[300]])) return false;
 const Sprite &a = _scene.sprites[31];
 if (!validP524Animation(a.autoFrame,uint32(a.frameData[0]),a.frameData[1],a.frameData[2],uint32(a.moveData[0]),state[300])) return false;
 for (uint i = 0; i < 32; ++i) {
  const Sprite &s = _scene.sprites[i], &initial = _questionSaveBaseline[i];
  if (s.x != initial.x || s.y != initial.y || s.clickEnabled != initial.clickEnabled ||
      s.frameFirst != initial.frameFirst || s.frameLast != initial.frameLast ||
      (i != 31 && (s.autoFrame || memcmp(s.frameData,initial.frameData,sizeof(s.frameData)))) ||
      memcmp(s.moveData+(i == 31),initial.moveData+(i == 31),sizeof(s.moveData)-(i == 31 ? sizeof(int32) : 0)) ||
      s.autoMove || s.standardMotion || s.planetMotion || s.orbitMotion || s.dragEnabled ||
      s.visible < 0 || s.visible > 1 || s.selectedFrame < -1 || s.selectedFrame >= int(p524Frames(i)) ||
      (i != 31 && s.selectedFrame > 0)) return false;
 }
 return true;
}
Common::Error AstronomicaEngine::saveP524(Common::WriteStream *stream) {
 if (!canSaveP524()) return Common::kWritingFailed;
 uint32 visible = 0;
 for (uint i = 0; i < 32; ++i) if (_scene.sprites[i].visible) visible |= 1U << i;
 const Sprite &a = _scene.sprites[31];
 const uint32 header[] = {524,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),visible,uint32(_loopSound),
  uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(a.autoFrame),a.frameSince,
  uint32(a.frameData[0]),uint32(a.frameData[1]),uint32(a.frameData[2]),uint32(a.moveData[0])};
 Common::Array<uint32> state; _runner.exportIdleState(state);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(6);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 value) { stream->writeUint32LE(value); hash = (hash ^ value)*16777619U; };
 for (uint32 value : header) word(value);
 for (const Sprite &sprite : _scene.sprites) word(uint32(sprite.selectedFrame));
 for (uint32 value : state) word(value);
 stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP524(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP524Words+1)*4 ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[15], frames[32], hash = 2166136261U;
 auto word = [&]() { const uint32 value = stream->readUint32LE(); hash = (hash ^ value)*16777619U; return value; };
 for (uint32 &value : header) value = word();
 for (uint32 &value : frames) value = word();
 Common::Array<uint32> state; state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &value : state) value = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP524State(state) || header[0] != 524 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[5] != 0 && header[5] != 0xffffffffU) ||
     header[6] > 1 || header[8] > 1 || (header[8] && (header[5] != 0 || !header[6])) ||
     !validP524Animation(header[9],header[11],header[12],header[13],header[14],state[300])) return Common::kReadingFailed;
 for (uint i = 0; i < 32; ++i)
  if (frames[i] != 0xffffffffU && (frames[i] >= p524Frames(i) || (i != 31 && frames[i]))) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P524/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP524Scene(parsed)) return Common::kReadingFailed;
 Graphics::Surface *picture = openBackgroundImage(kP524Images[state[300]],524);
 if (!picture) return Common::kReadingFailed;
 if (picture->w != 640 || picture->h != 320) { picture->free(); delete picture; return Common::kReadingFailed; }
 if (!loadPlace(524,false,true)) { picture->free(); delete picture; return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _runner.setResumeSupport(true,_previousPlace == 408);
 _loopSound = int32(header[5]); _loopEnabled = header[6] != 0; _lastSoundAt = header[7];
 for (uint i = 0; i < 32; ++i) {
  _scene.sprites[i].visible = (header[4] >> i) & 1; _scene.sprites[i].selectedFrame = int32(frames[i]);
 }
 Sprite &a = _scene.sprites[31]; a.autoFrame = header[9] != 0; a.frameSince = header[10];
 for (uint i = 0; i < 3; ++i) a.frameData[i] = int32(header[11+i]);
 a.moveData[0] = int32(header[14]);
 _pendingImage.copyFrom(*picture); _pendingImageName = kP524Images[state[300]]; _pendingImageX = _pendingImageY = 0;
 picture->free(); delete picture; displayBackgroundImage(); presentScene();
 if (header[8]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}

bool AstronomicaEngine::canSaveP526() const {
 if (_place != 526 || !_runner.idle() || _pendingImage.w || _movie || !validP526Scene(_scene) ||
     _questionSaveBaseline.size() != 23 || _hoverSprites.size() != 23 || _hoverRects.size() != 6 ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) ||
     (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state;
 if (!_runner.exportIdleState(state) || !validP526State(state) || p526ImageId(_displayedImageName) < 0) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (!h.ready) return false;
 for (uint i = 0; i < 23; ++i) {
  const Sprite &s = _scene.sprites[i];
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  Common::Array<uint32> words; p526SpriteWords(s,words);
  if (!validP526Sprite(&words[0],_questionSaveBaseline[i],i)) return false;
 }
 return true;
}
Common::Error AstronomicaEngine::saveP526(Common::WriteStream *stream) {
 if (!canSaveP526()) return Common::kWritingFailed;
 uint32 hover = 0;
 for (uint i = 0; i < 6; ++i) if (_hoverRects[i].entered) hover |= 1U << i;
 const uint32 header[] = {526,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(p526ImageId(_displayedImageName)),0,hover,0};
 Common::Array<uint32> state; _runner.exportIdleState(state);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(7);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 value) { stream->writeUint32LE(value); hash = (hash ^ value)*16777619U; };
 for (uint32 value : header) word(value);
 Common::Array<uint32> sprites;
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 for (uint32 value : sprites) word(value);
 for (uint32 value : state) word(value);
 stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP526(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP526Words+1)*4 || !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12], hash = 2166136261U;
 auto word = [&]() { const uint32 value = stream->readUint32LE(); hash = (hash ^ value)*16777619U; return value; };
 for (uint32 &value : header) value = word();
 Common::Array<uint32> sprites; sprites.resize(23*kP526SpriteWords);
 for (uint32 &value : sprites) value = word();
 Common::Array<uint32> state; state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &value : state) value = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP526State(state) || header[0] != 526 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] > 6 ||
     header[9] || (header[10] & ~0x3fU) || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P526/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP526Scene(parsed)) return Common::kReadingFailed;
 // The baseline render position is the serialized center before any motion.
 for (uint i = 0; i < 23; ++i) {
  parsed.sprites[i].renderX = int16(parsed.sprites[i].x); parsed.sprites[i].renderY = int16(parsed.sprites[i].y);
  if (!validP526Sprite(&sprites[i*kP526SpriteWords],parsed.sprites[i],i)) return Common::kReadingFailed;
 }
 Graphics::Surface *picture = header[8] ? openBackgroundImage(kP526Images[header[8]],526) : nullptr;
 if (header[8] && (!picture || picture->w != 98 || picture->h != 94)) {
  if (picture) { picture->free(); delete picture; } return Common::kReadingFailed;
 }
 if (!loadPlace(526,false,true)) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 23; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*kP526SpriteWords]);
 for (uint i = 0; i < 6; ++i) _hoverRects[i].entered = (header[10] & (1U << i)) != 0;
 if (picture) {
  _pendingImage.copyFrom(*picture); _pendingImageName = kP526Images[header[8]]; _pendingImageX = 90; _pendingImageY = 361;
  picture->free(); delete picture; displayBackgroundImage();
 } else redrawSprites();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveP528() const {
 if (_place != 528 || !_runner.idle() || _pendingImage.w || _movie || !validP528Scene(_scene) || _questionSaveBaseline.size() != 9 ||
     !_p528HistoryValid ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) ||
     (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state, sprites;
 if (!_runner.exportIdleState(state) || !validP528State(state) || !validP528History(state,_p528MoonImage,_p528TallMoon)) return false;
 const uint earth = _p528MoonImage == 10 ? 1 : _p528MoonImage;
 if (_p528EarthImage != earth || (_p528MoonImage ? !_displayedImageName.equalsIgnoreCase(Common::String::format("mo_s%u",_p528MoonImage)) : !_displayedImageName.empty())) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validP528Sprites(sprites,original,state);
}
Common::Error AstronomicaEngine::saveP528(Common::WriteStream *stream) {
 if (!canSaveP528()) return Common::kWritingFailed;
 const uint32 header[] = {528,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),_p528MoonImage,_p528TallMoon,0,0};
 Common::Array<uint32> state,sprites; _runner.exportIdleState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(8);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP528(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP528Words+1)*4 || !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 Common::Array<uint32> sprites,state; sprites.resize(9*27); state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP528State(state) || !validP528History(state,header[8],header[9]) ||
     header[0] != 528 || (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[10] || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P528/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP528Sprites(sprites,parsed,state)) return Common::kReadingFailed;
 Graphics::Surface *earth = nullptr,*moon = nullptr,*tall = nullptr;
 auto release = [&]() { for (Graphics::Surface *p : {earth,moon,tall}) if (p) { p->free(); delete p; } };
 if (header[8]) {
  earth = openBackgroundImage(Common::String::format("ge_s%u",header[8] == 10 ? 1 : header[8]),528);
  moon = openBackgroundImage(Common::String::format("mo_s%u",header[8]),528);
  if (header[9]) tall = openBackgroundImage(Common::String::format("mo_s%u",header[9]),528);
  if (!earth || earth->w != 171 || earth->h != 105 || !moon || moon->w != 143 || moon->h != (p528Tall(header[8]) ? 81 : 80) ||
      (header[9] && (!tall || tall->w != 143 || tall->h != 81))) { release(); return Common::kReadingFailed; }
 }
 if (!loadPlace(528,false,true)) { release(); return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 9; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 auto commit = [&](Graphics::Surface *p, const Common::String &name, int x, int y) {
  _pendingImage.copyFrom(*p); _pendingImageName = name; _pendingImageX = x; _pendingImageY = y; displayBackgroundImage();
 };
 if (tall) commit(tall,Common::String::format("mo_s%u",header[9]),401,369);
 if (earth) {
  commit(earth,Common::String::format("ge_s%u",header[8] == 10 ? 1 : header[8]),87,356);
  commit(moon,Common::String::format("mo_s%u",header[8]),401,369);
 } else redrawSprites();
 release();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveP530() const {
 if (_place != 530 || !_runner.idle() || _pendingImage.w || _movie || !validP530Scene(_scene) || _questionSaveBaseline.size() != 29 || !_p530HistoryValid ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) ||
     (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites;
 if (!_runner.exportIdleState(state) || !validP530State(state) || p530ImageId(_displayedImageName) < 0) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validP530Sprites(sprites,original);
}
Common::Error AstronomicaEngine::saveP530(Common::WriteStream *stream) {
 if (!canSaveP530()) return Common::kWritingFailed;
 const uint32 header[] = {530,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(p530ImageId(_displayedImageName)),0,0,0};
 Common::Array<uint32> state,sprites; _runner.exportIdleState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(9);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP530(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP530Words+1)*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 Common::Array<uint32> sprites,state; sprites.resize(29*27); state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP530State(state) || header[0] != 530 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] > 25 || header[9] || header[10] || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P530/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP530Sprites(sprites,parsed)) return Common::kReadingFailed;
 Graphics::Surface *picture = header[8] ? openBackgroundImage(kP530Images[header[8]],530) : nullptr;
 if (header[8] && (!picture || picture->w != 172 || picture->h != 172)) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 if (!loadPlace(530,false,true)) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 29; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 if (picture) {
  _pendingImage.copyFrom(*picture); _pendingImageName = kP530Images[header[8]]; _pendingImageX = 460; _pendingImageY = 10;
  picture->free(); delete picture; displayBackgroundImage();
 } else redrawSprites();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveP513() const {
 if (_place != 513 || !_runner.idle() || _pendingImage.w || _movie || !validP513Scene(_scene) || _questionSaveBaseline.size() != 32 || !_p513HistoryValid ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites;
 if (!_runner.exportIdleState(state) || !validP513State(state) || p513ImageId(_displayedImageName) != int(state[300])) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validP513Sprites(sprites,original);
}
Common::Error AstronomicaEngine::saveP513(Common::WriteStream *stream) {
 if (!canSaveP513()) return Common::kWritingFailed;
 const uint32 header[] = {513,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(p513ImageId(_displayedImageName)),0,0,0};
 Common::Array<uint32> state,sprites; _runner.exportIdleState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(11);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP513(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP513Words+1)*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 Common::Array<uint32> sprites,state; sprites.resize(32*27); state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP513State(state) || header[0] != 513 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] != state[300] || header[9] || header[10] || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P513/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP513Sprites(sprites,parsed)) return Common::kReadingFailed;
 const Common::String name = Common::String::format("cube%u",header[8]);
 Graphics::Surface *picture = openBackgroundImage(name,513);
 if (!picture || picture->w != 313 || picture->h != 320) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 if (!loadPlace(513,false,true)) { picture->free(); delete picture; return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 32; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 _pendingImage.copyFrom(*picture); _pendingImageName = name; _pendingImageX = 177; _pendingImageY = 22;
 picture->free(); delete picture; displayBackgroundImage();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveP517() const {
 if (_place != 517 || !_runner.idle() || _pendingImage.w || _movie || !validP517Scene(_scene) || _questionSaveBaseline.size() != 11 || !_p517HistoryValid ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites;
 if (!_runner.exportIdleState(state) || !validP517State(state) || p517ImageId(_displayedImageName) != int(state[300])) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validP517Sprites(sprites,original,state[303]);
}
Common::Error AstronomicaEngine::saveP517(Common::WriteStream *stream) {
 if (!canSaveP517()) return Common::kWritingFailed;
 const uint32 header[] = {517,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(p517ImageId(_displayedImageName)),0,0,0};
 Common::Array<uint32> state,sprites; _runner.exportIdleState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(12);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadP517(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kP517Words+1)*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 Common::Array<uint32> sprites,state; sprites.resize(11*27); state.resize(ScriptRunner::kIdleStateWords);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validP517State(state) || header[0] != 517 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] != state[300] || header[9] || header[10] || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P517/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validP517Sprites(sprites,parsed,state[303])) return Common::kReadingFailed;
 const Common::String name = Common::String::format("aurback%u",header[8]);
 Graphics::Surface *picture = openBackgroundImage(name,517);
 if (!picture || picture->w != 640 || picture->h != 320) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 if (!loadPlace(517,false,true)) { picture->free(); delete picture; return Common::kReadingFailed; }
 _runner.resetVariantSequence(); _runner.importIdleState(state);
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 11; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 _pendingImage.copyFrom(*picture); _pendingImageName = name; _pendingImageX = 0; _pendingImageY = 0;
 picture->free(); delete picture; displayBackgroundImage();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
// Universe v15 stores settled state and a retained original video sample.
// The verified linear edit and VFR mapping do not resume active playback.
static bool universeFileIdentity(const Common::Path &path, uint32 size, uint32 expected) {
 Common::File f; if (!f.open(Common::FSNode(path)) || f.size() != size) return false;
 uint32 hash = 2166136261U; byte bytes[4096];
 while (f.pos() < f.size()) { const uint n = f.read(bytes,sizeof(bytes)); if (!n) return false; for (uint i = 0; i < n; ++i) hash = (hash ^ bytes[i])*16777619U; }
 return !f.err() && hash == expected;
}
static bool validUniverseState(const Common::Array<uint32> &s) {
 if (!ScriptRunner::validPersistentState(s) || s[300] > 15 || s[303] != 1 || s[306] != uint32((s[309] & 8) != 0) || s[309] > 14) return false;
 const uint widths[] = {16,1,1,4};
 for (uint i = 0; i < 100; ++i) {
  if (s[3*i+2] != 1 || s[302+3*i] != uint32(i < 4) || s[301+3*i] != (i < 4 ? widths[i] : 0U)) return false;
 }
 return true;
}
static bool validUniverseScene(const Scene &s) {
 if (s.mode || s.layers != 1 || s.sprites.size() != 11 || s.conditions.size() != 4 || s.scripts.size() != 3 ||
     !s.mouseRects.empty() || s.movies.size() != 1 || !s.movies[0].equalsIgnoreCase("FUNIV.MOV")) return false;
 for (uint i = 0; i < 11; ++i) if (spriteFrameCount(s,i) != (i < 7 ? 2U : i == 7 ? 16U : 10U)) return false;
 return true;
}
static bool validUniverseSprites(const Common::Array<uint32> &w, const Scene &original, const Common::Array<uint32> &state, int frame, uint start, uint end) {
 if (!validUniverseScene(original) || !validUniverseState(state) || w.size() != 11*27 || frame < -1 || frame > 252 || frame == 214) return false;
 Scene expected = original; for (Sprite &s : expected.sprites) s.selectedFrame = 0;
 expected.sprites[7].selectedFrame = state[300];
 // Last attempted segment owns the readout; the retained picture may belong
 // to an older attempt or be absent if no update committed before the end.
 int middle = 0, right = 0; uint attemptedBit = 0;
 if (start == 0 && end == 359) { right = 2; attemptedBit = 2; }
 else if (start == 360 && end == 719) { right = 5; attemptedBit = 1; }
 else if (start == 720 && end == 946) { middle = 1; right = 5; attemptedBit = 8; }
 else if (start == 1029 && end == 1261) { right = 5; attemptedBit = 4; }
 else if (start || end || state[306] || state[309] || frame != -1) return false;
 if (attemptedBit) {
  if (!(state[309] & attemptedBit)) return false;
  const uint since = w[8*27+8];
  for (uint i = 8; i < 11; ++i) {
   expected.sprites[i].frameSince = since;
   expected.sprites[i].frameData[0] = -1; expected.sprites[i].frameData[1] = 1;
  }
 }
 if (frame >= 0) {
  const uint retainedBit = frame <= 79 ? 2U : frame <= 159 ? 1U : frame <= 213 ? 8U : 4U;
  if (!(state[309] & retainedBit)) return false;
 }
 expected.sprites[9].selectedFrame = middle; expected.sprites[10].selectedFrame = right;
 Common::Array<uint32> baseline; for (const Sprite &s : expected.sprites) p526SpriteWords(s,baseline);
 return baseline == w;
}
static Graphics::Surface *decodeSpriteBitmap(Common::SeekableReadStream &, const BitmapRef &, const Graphics::PixelFormat &);
// Native v16 preserves ordinary/failed-return P522, not an active flight.
// P514 ordinary settled orbit state. No queued launch/docking/exit continuation.
static bool validP509Scene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=19||s.conditions.size()!=17||s.scripts.size()!=6||s.mouseRects.size()!=6||!s.movies.empty())return false;
 const uint frames[]={2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,2,1,1};for(uint i=0;i<19;++i)if(s.sprites[i].clone!=-1||spriteFrameCount(s,i)!=frames[i])return false;return true;
}
static bool validP509PlayState(const Common::Array<uint32>&w){
 if(w.size()!=608)return false;const uint phase=w[348];if(phase==2){if(w[318]!=1||!(w[303]||w[306]||w[309]||w[312]))return false;}
 else if(phase==1){if(w[303]||w[306]||w[315]||w[318]||!(w[309]||w[312]))return false;}else return false;return true;
}
static bool validP509Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,uint32 clock){
 if(w.size()!=19*27||!validP509Scene(original)||!validP509PlayState(state))return false;Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint choice=state[321],phase=state[348];for(uint i=4;i<10;++i)expected.sprites[i].selectedFrame=choice==i-3?1:0;
 expected.sprites[11].visible=phase==1;expected.sprites[12].visible=phase==1&&state[312];expected.sprites[13].visible=state[303];expected.sprites[14].visible=phase==2;expected.sprites[15].visible=phase==2&&state[312];expected.sprites[16].visible=state[306];expected.sprites[17].visible=phase==2&&state[315];expected.sprites[18].visible=state[309];
 Sprite&s=expected.sprites[10];const uint at=10*27;const int x=int32(w[at+4]),y=int32(w[at+5]),dx=int32(w[at+11]),dy=int32(w[at+12]);
 if(w[at+1]>1||x<448||x>589||y< -1||y>66||(dx!=-2&&dx!=2)||(dy!=-1&&dy!=1)||int32(clock-w[at+8])<0||int32(clock-w[at+9])<0)return false;
 s.standardMotion=true;s.selectedFrame=w[at+1];s.renderX=x;s.renderY=y;s.moveDX=dx;s.moveDY=dy;s.frameSince=w[at+8];s.moveSince=w[at+9];
 Common::Array<uint32>baseline;for(const Sprite&v:expected.sprites)p526SpriteWords(v,baseline);return baseline==w;
}
static bool p509Assets(){const Common::Path base=ConfMan.getPath("path").join("PLACES/P509");return universeFileIdentity(base.join("MEGAFILE.HYP"),713948,3651436523U)&&universeFileIdentity(base.join("SKY1"),205878,0x1362d518U)&&universeFileIdentity(base.join("SKY2"),205878,0xf33e47a0U)&&universeFileIdentity(base.join("SKY3"),205878,0x8da73602U);}
static int p509Image(const Common::String&name){if(name.equalsIgnoreCase("SKY1"))return 1;if(name.equalsIgnoreCase("SKY2"))return 2;return 0;}
bool AstronomicaEngine::canSaveP509()const{
 if(_place!=509||!_p509AssetsValid||!validP509Scene(_scene)||_questionSaveBaseline.size()!=19||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!p509Image(_displayedImageName)||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if(_loopEnabled||(_loopSound!=-1&&_loopSound!=0)||_mixer->isSoundHandleActive(_soundHandle))return false;for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w;if(!_runner.exportP509PendingState(state,scriptClock())||!validP509PlayState(state)||uint(p509Image(_displayedImageName))!=state[348])return false;
 for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP509Sprites(w,original,state,scriptClock());
}
Common::Error AstronomicaEngine::saveP509(Common::WriteStream*stream){
 if(!canSaveP509())return Common::kWritingFailed;Common::Array<uint32>state,w;_runner.exportP509PendingState(state,scriptClock());for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);
 const uint32 h[]={509,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),uint32(p509Image(_displayedImageName))};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(20);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP509(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+19*27+608+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state;w.resize(19*27);state.resize(608);for(uint32&v:w)v=read();for(uint32&v:state)v=read();
 if(stream->readUint32LE()!=hash||stream->err()||h[0]!=509||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]||h[7]||h[8]<1||h[8]>12||h[9]>12||h[10]<1||h[10]>2||h[10]!=state[348]||!p509Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P509/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP509Sprites(w,parsed,state,h[2]))return Common::kReadingFailed;
 ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);prepared.setPrograms(parsed.scripts,state[601]);prepared.setP509PendingSupport(true);if(!prepared.importP509PendingState(state,h[2]))return Common::kReadingFailed;
 for(const char*name:{"SKY1","SKY2","SKY3"}){Common::File image;if(!image.open(Common::FSNode(ConfMan.getPath("path").join(Common::String::format("PLACES/P509/%s",name)))))return Common::kReadingFailed;Image::BitmapDecoder decoder;if(!decoder.loadStream(image)||!decoder.getSurface()||decoder.getSurface()->w!=640||decoder.getSurface()->h!=320)return Common::kReadingFailed;Graphics::Surface*converted=decoder.getSurface()->convertTo(_screen.format,decoder.getPalette().data(),decoder.getPalette().size());if(!converted)return Common::kReadingFailed;converted->free();delete converted;}
 for(uint i=0;i<2;++i){Graphics::Surface*bmp=decodeSpriteBitmap(file,parsed.sprites[10].frames[i].image,_screen.format);if(!bmp)return Common::kReadingFailed;const bool valid=bmp->w==int(i?53:55)&&bmp->h==55;bmp->free();delete bmp;if(!valid)return Common::kReadingFailed;}
 if(!loadPlace(509,false,true))return Common::kReadingFailed;if(!_runner.importP509PendingState(state,h[2]))error("Validated P509 queue could not be installed");_p509AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=h[5]!=0;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<19;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);if(!stageBackgroundImage(h[10]==1?"sky1":"sky2",0,0))error("Preflighted P509 image disappeared");displayBackgroundImage();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

// P511 ordinary idle boundaries. The full original identities bind this profile.
// P516 supports only configured ordinary prelaunch/true failed-return states.
// Active flight, sticky hits and stopped moon/explosion histories are excluded.
// Quiet P527 preserves the displayed movie sample independently of the selector.
// P502 quiet nonflight states preserve real failed-return and explosion history.
// First P503 scope: healthy partial orbits and never-solved stopped failures.
// Solved->failed one-way partner histories are intentionally rejected.
static bool validP501Scene(const Scene&s){if(s.mode||s.layers!=1||s.sprites.size()!=27||s.conditions.size()!=5||s.scripts.size()!=1||s.scripts[0].size()!=8||!s.mouseRects.empty()||!s.movies.empty()||s.consumed!=786726||s.trailing)return false;const uint frames[]={1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,2,2,6,12,3};for(uint i=0;i<27;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=-1)return false;
{const Command&c=s.scripts[0][0];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=3)return false;if(c.args[2]!=1)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[0][1];if(c.opcode!=28||c.delay!=0||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=-1)return false;}
{const Command&c=s.scripts[0][2];if(c.opcode!=10||c.delay!=3500||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=-1)return false;}
{const Command&c=s.scripts[0][3];if(c.opcode!=23||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=25)return false;if(c.args[1]!=0)return false;if(c.args[2]!=0)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[0][4];if(c.opcode!=5||c.delay!=3500||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=388)return false;}
{const Command&c=s.scripts[0][5];if(c.opcode!=29||c.delay!=150||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=-1)return false;}
{const Command&c=s.scripts[0][6];if(c.opcode!=42||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[0][7];if(c.opcode!=41||c.delay!=200||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=0)return false;}
return true;}
static const char*kP501Images[]={"","backorbi","phobos","blackdwa","jupiter","vesta","moon"};
static int p501ImageId(const Common::String&name){for(uint i=0;i<7;++i)if(name==kP501Images[i])return i;return -1;}
static bool validP501State(const Common::Array<uint32>&s){
 if(s.size()!=607)return false;Common::Array<uint32>base;for(uint i=0;i<605;++i)base.push_back(s[i]);if(!ScriptRunner::validPersistentState(base)||s[300]>5||s[303]||s[306]>2||s[309]||s[312]!=1||(s[605]!=0&&s[605]!=7))return false;
 const uint widths[]={8,8,8,1,1};for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<5)||s[301+3*i]!=(i<5?widths[i]:0U))return false;return true;
}
static bool validP501Extra(const Common::Array<uint32>&w){
 if(w.size()!=118||w[100]!=0xffffffffU||w[101])return false;for(uint i=0;i<100;++i)if(w[i])return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;for(uint i=0;i<8;++i){empty&=!w[102+i]&&!w[110+i];configured&=w[102+i]==widths[i]&&w[110+i]==heights[i];}return empty||configured;
}
static bool validP501Ball(const Common::Array<uint32>&b){
 if(b.size()!=5)return false;if(!b[0])return !b[1]&&!b[2]&&b[3]==2&&b[4]==10;
 if(b[0]==1)return b[1]>=410&&b[1]<=468&&b[2]==207&&b[3]==2&&b[4]==10;
 if(b[0]==5)return b[1]>=401&&b[1]<=459&&b[2]==197&&b[3]==2&&b[4]==10;
 return b[0]==4&&b[1]>=518&&b[1]<=576&&b[2]==182&&((b[3]==2&&b[4]==10)||(!b[3]&&(b[4]==10||b[4]==5000)));
}
static bool validP501Loop(uint32 loop,const Common::Array<uint32>&s){if(s.size()!=607||s[300]>5)return false;const int loops[]={0,1,5,4,2,3};return s[300]?int32(loop)==loops[s[300]]:(loop==0||loop==0xffffffffU);}
static bool validP501Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,const Common::Array<uint32>&extra,const Common::Array<uint32>&ball,uint image,uint32 clock){
 if(w.size()!=729||!validP501Scene(original)||!validP501State(state)||!validP501Extra(extra)||!validP501Ball(ball)||image>6||int32(clock-state[601])<0||int32(clock-state[606])<0||(state[605]==0&&state[606]!=state[601]))return false;
 const uint world=state[300];if(world?image!=world+1:image>1)return false;
 Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 if(!image){if(world||state[306]||ball[0])return false;Common::Array<uint32>pristineWords;for(const Sprite&sprite:expected.sprites)p526SpriteWords(sprite,pristineWords);return pristineWords==w;}
 const int buttons[]={-1,10,7,8,11,9};for(uint i=7;i<=11;++i)expected.sprites[i].visible=world&&i==uint(buttons[world]);
 const int hitterX[]={193,169,166,184,157,160},hitterY[]={145,176,180,140,151,169},pitcherX[]={336,311,303,339,312,308},pitcherY[]={173,207,207,172,182,197};
 uint oldWorld=world;if(!world&&image==1){bool found=false;for(uint i=1;i<=5;++i)if(w[25*27+2]==uint(hitterX[i])&&w[25*27+3]==uint(hitterY[i])&&w[26*27+2]==uint(pitcherX[i])&&w[26*27+3]==uint(pitcherY[i])){oldWorld=i;found=true;break;}if(!found)return false;for(uint i=7;i<=11;++i)expected.sprites[i].visible=i==uint(buttons[oldWorld]);}
 Sprite&h=expected.sprites[25];h.x=h.renderX=hitterX[oldWorld];h.y=h.renderY=hitterY[oldWorld];h.visible=world!=0;if(w[25*27+1]>=12)return false;h.selectedFrame=w[25*27+1];
 Sprite&p=expected.sprites[26];p.x=p.renderX=pitcherX[oldWorld];p.y=p.renderY=pitcherY[oldWorld];p.visible=world!=0;
 const bool crushed=w[21*27+1]==2&&w[22*27+1]==1&&w[23*27+1]==1;const bool pristine=!w[21*27+1]&&!w[22*27+1]&&!w[23*27+1];if(!crushed&&!pristine)return false;
 for(uint i=21;i<=23;++i){expected.sprites[i].selectedFrame=crushed?(i==21?2:1):0;expected.sprites[i].visible=world==2&&crushed;}
 expected.sprites[12].visible=world==2&&!crushed;if(world==2&&crushed)h.visible=p.visible=0;
 const uint at=24*27;Sprite&s=expected.sprites[24];if(w[at]||w[at+1]>=6||w[at+6]||w[at+7]||w[at+8]||w[at+10]>1||(w[at+10]&&int32(clock-w[at+9])<0))return false;
 bool stored=false;for(uint i=0;i<5;++i){const int xs[]={300,311,339,312,308},ys[]={233,207,172,182,197};stored|=w[at+2]==uint(xs[i])&&w[at+3]==uint(ys[i]);}if(!stored)return false;
 const int x=int32(w[at+4]),y=int32(w[at+5]),dx=int32(w[at+11]),dy=int32(w[at+12]);if(x< -16||x>645||y< -19||y>700)return false;
 const bool delta=(!dx&&!dy)||((dx==-1||dx==1)&&dy>=-1&&dy<=1)||(dx==5&&dy==-3)||(dx==2&&(dy==-2||dy==0));if(!delta)return false;
 if(w[at+10]){if(w[at+19]!=0xffffffffU||w[at+22]!=0xffffffffU||w[at+23]!=0xffffffffU||w[at+24]>1||w[at+25]!=1||w[at+26])return false;}
 else if((w[at+19]!=0&&w[at+19]!=0xffffffffU)||(w[at+22]!=0&&w[at+22]!=0xffffffffU)||dx||dy||w[at+9]||w[at+23]||w[at+24]||w[at+25]||w[at+26])return false;
 s.selectedFrame=w[at+1];s.x=w[at+2];s.y=w[at+3];s.renderX=x;s.renderY=y;s.moveSince=w[at+9];s.standardMotion=w[at+10];s.moveDX=dx;s.moveDY=dy;s.frameData[0]=int32(w[at+19]);for(uint i=0;i<5;++i)s.moveData[i]=int32(w[at+22+i]);
 Common::Array<uint32>baseline;for(const Sprite&sprite:expected.sprites)p526SpriteWords(sprite,baseline);return baseline==w;
}

static bool p501Assets(){
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/MEGAFILE.HYP"),786726,1856216578U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/BACKORBI"),205878,2268106733U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/PHOBOS"),205878,4082642725U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/BLACKDWA"),205878,2929933636U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/JUPITER"),205878,3019756444U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/VESTA"),205878,3043524317U))return false;
if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P501/MOON"),205878,1466390967U))return false;
return true;}
bool AstronomicaEngine::canSaveP501()const{
 if(_place!=501||!_p501AssetsValid||!validP501Scene(_scene)||_questionSaveBaseline.size()!=27||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||p501ImageId(_displayedImageName)<0||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound< -1||_loopSound>5)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;
 if(_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_plotEvent||_plotTime||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w,extra,ball;if(!_runner.exportP501ReadyState(state,scriptClock()))return false;p516Extra(extra);for(int32 value:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})ball.push_back(uint32(value));for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP501Loop(uint32(_loopSound),state)&&validP501Sprites(w,original,state,extra,ball,p501ImageId(_displayedImageName),scriptClock());
}
Common::Error AstronomicaEngine::saveP501(Common::WriteStream*stream){
 if(!canSaveP501())return Common::kWritingFailed;Common::Array<uint32>state,w,extra,ball;_runner.exportP501ReadyState(state,scriptClock());for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);p516Extra(extra);for(int32 value:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})ball.push_back(uint32(value));const uint32 h[]={501,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),0,uint32(p501ImageId(_displayedImageName))};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(27);uint32 hash=2166136261U;auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)put(v);for(uint32 v:w)put(v);for(uint32 v:state)put(v);for(uint32 v:extra)put(v);for(uint32 v:ball)put(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP501(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(12+27*27+607+118+5+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[12],hash=2166136261U;auto get=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();Common::Array<uint32>w,state,extra,ball;w.resize(729);state.resize(607);extra.resize(118);ball.resize(5);for(uint32&v:w)v=get();for(uint32&v:state)v=get();for(uint32&v:extra)v=get();for(uint32&v:ball)v=get();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=501||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]>5&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4]==0xffffffffU)||h[8]<1||h[8]>12||h[9]>12||h[10]||h[11]>6||!validP501Loop(h[4],state)||!p501Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P501/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP501Sprites(w,parsed,state,extra,ball,h[11],h[2]))return Common::kReadingFailed;ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);prepared.setPrograms(parsed.scripts,state[601]);prepared.setBallHandler(this);prepared.setP501ReadySupport(true);if(!prepared.importP501ReadyState(state,h[2]))return Common::kReadingFailed;
 Graphics::Surface*picture=h[11]?openBackgroundImage(kP501Images[h[11]],501):decodeSpriteBitmap(file,parsed.background,_screen.format);if(!picture)return Common::kReadingFailed;if(picture->w!=640||picture->h!=320){picture->free();delete picture;return Common::kReadingFailed;}
 if(!loadPlace(501,false,true)){picture->free();delete picture;return Common::kReadingFailed;}if(!_runner.importP501ReadyState(state,h[2]))error("Validated P501 state could not be installed");_p501AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<27;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}_ball.scenario=int32(ball[0]);_ball.centerX=int32(ball[1]);_ball.centerY=int32(ball[2]);_ball.side=int32(ball[3]);_ball.period=int32(ball[4]);_pendingImage.copyFrom(*picture);_pendingImageName=kP501Images[h[11]];_pendingImageX=_pendingImageY=0;picture->free();delete picture;displayBackgroundImage();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool p504Programs(const Scene&s){if(s.scripts.size()!=3)return false;
if(s.scripts[0].size()!=11)return false;
{const Command&c=s.scripts[0][0];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=8)return false;if(c.args[2]!=1)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[0][1];if(c.opcode!=32||c.delay!=0||c.args.size()!=3||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=8)return false;if(c.args[2]!=1)return false;}
{const Command&c=s.scripts[0][2];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[0][3];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=7)return false;if(c.args[2]!=1)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[0][4];if(c.opcode!=32||c.delay!=0||c.args.size()!=3||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=8)return false;if(c.args[2]!=1)return false;}
{const Command&c=s.scripts[0][5];if(c.opcode!=9||c.delay!=400||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=3)return false;}
{const Command&c=s.scripts[0][6];if(c.opcode!=23||c.delay!=4400||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=25)return false;if(c.args[1]!=0)return false;if(c.args[2]!=0)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[0][7];if(c.opcode!=9||c.delay!=6500||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=15)return false;}
{const Command&c=s.scripts[0][8];if(c.opcode!=5||c.delay!=3500||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=527)return false;}
{const Command&c=s.scripts[0][9];if(c.opcode!=42||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[0][10];if(c.opcode!=41||c.delay!=200||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=0)return false;}
if(s.scripts[1].size()!=62)return false;
{const Command&c=s.scripts[1][0];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=15)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][1];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=45)return false;}
{const Command&c=s.scripts[1][2];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][3];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=14)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][4];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=45)return false;}
{const Command&c=s.scripts[1][5];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=44)return false;}
{const Command&c=s.scripts[1][6];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][7];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=13)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][8];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=44)return false;}
{const Command&c=s.scripts[1][9];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=43)return false;}
{const Command&c=s.scripts[1][10];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][11];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=12)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][12];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=43)return false;}
{const Command&c=s.scripts[1][13];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=42)return false;}
{const Command&c=s.scripts[1][14];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][15];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=11)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][16];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=42)return false;}
{const Command&c=s.scripts[1][17];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=41)return false;}
{const Command&c=s.scripts[1][18];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][19];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=10)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][20];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=41)return false;}
{const Command&c=s.scripts[1][21];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=40)return false;}
{const Command&c=s.scripts[1][22];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][23];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=9)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][24];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=40)return false;}
{const Command&c=s.scripts[1][25];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=39)return false;}
{const Command&c=s.scripts[1][26];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][27];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=8)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][28];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=39)return false;}
{const Command&c=s.scripts[1][29];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=38)return false;}
{const Command&c=s.scripts[1][30];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][31];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=7)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][32];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=38)return false;}
{const Command&c=s.scripts[1][33];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=37)return false;}
{const Command&c=s.scripts[1][34];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][35];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=6)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][36];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=37)return false;}
{const Command&c=s.scripts[1][37];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=36)return false;}
{const Command&c=s.scripts[1][38];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][39];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=5)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][40];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=36)return false;}
{const Command&c=s.scripts[1][41];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=35)return false;}
{const Command&c=s.scripts[1][42];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][43];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=4)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][44];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=35)return false;}
{const Command&c=s.scripts[1][45];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=34)return false;}
{const Command&c=s.scripts[1][46];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][47];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=3)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][48];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=34)return false;}
{const Command&c=s.scripts[1][49];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=33)return false;}
{const Command&c=s.scripts[1][50];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][51];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=2)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][52];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=33)return false;}
{const Command&c=s.scripts[1][53];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=32)return false;}
{const Command&c=s.scripts[1][54];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][55];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=1)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][56];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=32)return false;}
{const Command&c=s.scripts[1][57];if(c.opcode!=16||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=11)return false;}
{const Command&c=s.scripts[1][58];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
{const Command&c=s.scripts[1][59];if(c.opcode!=31||c.delay!=-1||c.args.size()!=6||!c.text.empty())return false;if(c.args[0]!=1)return false;if(c.args[1]!=1)return false;if(c.args[2]!=0)return false;if(c.args[3]!=0)return false;if(c.args[4]!=0)return false;if(c.args[5]!=0)return false;}
{const Command&c=s.scripts[1][60];if(c.opcode!=17||c.delay!=-1||c.args.size()!=1||!c.text.empty())return false;if(c.args[0]!=11)return false;}
{const Command&c=s.scripts[1][61];if(c.opcode!=42||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;}
if(s.scripts[2].size()!=1)return false;
{const Command&c=s.scripts[2][0];if(c.opcode!=15||c.delay!=0||c.args.size()!=2||!c.text.empty())return false;if(c.args[0]!=5)return false;if(c.args[1]!=1)return false;}
return true;}
// First P504 scope: healthy partial orbits and never-solved stopped failures.
// Solved->failed one-way partner histories are intentionally rejected.
static bool validP504Scene(const Scene&s){
 if(s.mode||s.layers!=2||s.sprites.size()!=45||s.conditions.size()!=9||s.scripts.size()!=3||!s.mouseRects.empty()||!s.movies.empty()||s.consumed!=656595||s.trailing!=148864)return false;
 const uint frames[]={2,2,2,2,1,1,1,1,2,2,1,6,10,10,10,10,10,10,1,1,1,1,3,3,11,11,11,11,3,3,10,1,1,1,1,1,1,1,1,1,1,1,1,1,1};const int clones[]={-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,13,13,13,13,13,-1,-1,-1,-1,-1,-1,-1,-1,26,25,24,23,-1,11,11,11,11,11,11,11,11,11,11,11,11,11,11};
 for(uint i=0;i<45;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=int(clones[i]))return false;return p504Programs(s);
}
static bool validP504State(const Common::Array<uint32>&s){
 if(s.size()!=607)return false;Common::Array<uint32>base;for(uint i=0;i<605;++i)base.push_back(s[i]);if(!ScriptRunner::validPersistentState(base)||s[300]<1||s[300]>4||s[303]>15||s[306]<1||s[306]>4||s[321]||s[324]||(s[605]!=0&&s[605]!=10))return false;
 uint mask=0;for(uint i=3;i<=6;++i){if(s[300+3*i]>1)return false;mask|=s[300+3*i]<<(i-3);}if(mask==15)return false;
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<9)||s[301+3*i]!=(i<9?(i==0?8U:i==8?1U:20U):0U))return false;return true;
}
static bool validP504Extra(const Common::Array<uint32>&w,const Common::Array<uint32>&s){
 if(w.size()!=118||!validP504State(s))return false;
 for(uint i=0;i<50;++i)if((i<22||i>29)&&(w[i]||w[50+i]))return false;
 for(int t=1;t<=4;++t){const uint p=t+21,q=30-t;const bool solved=s[300+3*(t+2)]!=0;
  if(solved){if(w[p]!=4||(w[q]!=1&&w[q]!=4)||int32(w[50+p])!=-int(q+1)||w[50+q]!=p+1)return false;}
  else if((w[p]!=0&&w[p]!=2&&w[p]!=3)||w[q]||w[50+p]||w[50+q])return false;
 }
 if(!((w[100]==0xffffffffU&&!w[101])||(w[100]==3&&w[101]==31)))return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;for(uint i=0;i<8;++i){empty&=!w[102+i]&&!w[110+i];configured&=w[102+i]==widths[i]&&w[110+i]==heights[i];}return empty||configured;
}
static bool validP504Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,const Common::Array<uint32>&extra,uint32 clock){
 if(w.size()!=45*27||!validP504Scene(original)||!validP504Extra(extra,state)||int32(clock-state[601])<0)return false;
 Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint speed=state[303],direction=state[300],target=state[306];for(uint i=4;i<=7;++i)expected.sprites[i].visible=target==i-3;for(uint i=18;i<=21;++i)expected.sprites[i].visible=direction==i-17;
 int digits=cometSpeed(speed);for(int i=17;i>=12;--i){expected.sprites[i].selectedFrame=digits%10;digits/=10;}
 expected.sprites[10].visible=speed>=1;for(uint i=31;i<45;++i)expected.sprites[i].visible=speed>=i-29;
 bool launched=false,low=false,orbit=false;
 for(int t=1;t<=4;++t){const uint p=t+21,q=30-t;launched|=extra[p]!=0;low|=extra[p]==2;orbit|=extra[p]==4;
  for(uint index:{p,q}){Sprite&s=expected.sprites[index];const uint at=index*27,kind=extra[index];
   if(w[at+1]>=spriteFrameCount(original,index)||((s.autoFrame||kind)&&int32(clock-w[at+8])<0)||(kind!=0&&kind!=1&&int32(clock-w[at+9])<0))return false;
   if(!kind){if(index==q&&(extra[p]==2||extra[p]==3)){s.autoFrame=true;s.frameData[0]=30;s.frameData[1]=1;s.frameData[2]=0;}if(s.autoFrame){s.selectedFrame=w[at+1];s.frameSince=w[at+8];}continue;}
   if(kind==2||kind==3){s.y=285;s.renderX=kind==2?340:197;s.renderY=kind==2?190:9;s.standardMotion=true;s.autoFrame=false;s.frameData[0]=s.moveData[0]=-1;s.selectedFrame=w[at+1];s.frameSince=w[at+8];s.moveSince=w[at+9];continue;}
   s.x=320;s.y=160;s.moveData[1]=t*25+100;s.moveData[2]=t*12+50;s.standardMotion=s.autoFrame=true;s.frameData[0]=30;s.frameData[1]=1;s.frameData[2]=0;s.selectedFrame=w[at+1];s.frameSince=w[at+8];
   if(kind==1){if(index!=q||w[at]||w[at+7]||w[at+9])return false;continue;}
   const int x=int32(w[at+4]),y=int32(w[at+5]),dx=int32(w[at+11]),dy=int32(w[at+12]);
   const int widths[]={30,44,54,40},heights[]={32,44,52,40};const int width=widths[t-1],height=heights[t-1];
   if(!width||!height||w[at]>1||w[at+14]>1||w[at+15]>1||x<320-(t*25+100)-width-2||x>MAX(320+(t*25+100)+2,545)||y<160-(t*12+50)-height-1||y>160+(t*12+50)+1||!((dx==0&&dy>=-1&&dy<=1)||(dy==0&&(dx==-2||dx==2)))||(!w[at]&&(dx||dy)))return false;
   s.visible=w[at];s.autoMove=true;s.moveData[0]=40;s.renderX=x;s.renderY=y;s.moveDX=dx;s.moveDY=dy;s.orbitSideX=w[at+14];s.orbitSideY=w[at+15];s.moveSince=w[at+9];
  }
  if(extra[p]==4&&w[p*27]+w[q*27]!=1)return false;
 }
 if(launched){Sprite&launch=expected.sprites[11];launch.visible=0;launch.frameData[0]=launch.moveData[0]=-1;}
 const uint at=30*27;const bool exploded=w[at+19]==0xffffffffU&&w[at+22]==0xffffffffU;if(low&&!exploded)return false;if(!launched&&exploded)return false;
 if(exploded){Sprite&e=expected.sprites[30];e.selectedFrame=9;e.renderX=320;e.renderY=160;e.frameData[0]=e.moveData[0]=-1;}
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}

static bool p504Assets(){return universeFileIdentity(ConfMan.getPath("path").join("PLACES/P504/MEGAFILE.HYP"),805459,3359071051U);}
bool AstronomicaEngine::canSaveP504()const{
 if(_place!=504||!_p504AssetsValid||!validP504Scene(_scene)||_questionSaveBaseline.size()!=45||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;
 if(_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_ball.scenario||_ball.centerX||_ball.centerY||_ball.side!=2||_ball.period!=10||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_plotEvent||_plotTime||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w,extra;if(!_runner.exportP504PollState(state,scriptClock()))return false;p516Extra(extra);for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP504Sprites(w,original,state,extra,scriptClock());
}
Common::Error AstronomicaEngine::saveP504(Common::WriteStream*stream){
 if(!canSaveP504())return Common::kWritingFailed;Common::Array<uint32>state,w,extra;_runner.exportP504PollState(state,scriptClock());for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);p516Extra(extra);const uint32 h[]={504,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),0};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(26);uint32 hash=2166136261U;auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)put(v);for(uint32 v:w)put(v);for(uint32 v:state)put(v);for(uint32 v:extra)put(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP504(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+45*27+607+118+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto get=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();Common::Array<uint32>w,state,extra;w.resize(1215);state.resize(607);extra.resize(118);for(uint32&v:w)v=get();for(uint32&v:state)v=get();for(uint32&v:extra)v=get();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=504||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]||!p504Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P504/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP504Sprites(w,parsed,state,extra,h[2]))return Common::kReadingFailed;ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);prepared.setPrograms(parsed.scripts,state[601]);prepared.setCometHandler(this);prepared.setP504PollSupport(true);if(!prepared.importP504PollState(state,h[2]))return Common::kReadingFailed;
 if(!loadPlace(504,false,true))return Common::kReadingFailed;if(!_runner.importP504PollState(state,h[2]))error("Validated P504 state could not be installed");_p504AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<45;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP503Scene(const Scene&s){
 if(s.mode||s.layers!=2||s.sprites.size()!=48||s.conditions.size()!=9||s.scripts.size()!=2||!s.mouseRects.empty()||!s.movies.empty()||s.consumed!=617311||s.trailing!=165284)return false;
 const uint frames[]={2,2,2,2,1,1,1,1,1,2,2,1,6,10,10,10,10,10,10,1,1,1,1,6,1,1,1,3,3,1,1,1,6,10,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
 for(uint i=0;i<48;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=34?12:i>=28&&i<=32?56-int(i):i>=14&&i<=18?14:-1))return false;return true;
}
static bool validP503State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]<1||s[300]>4||s[303]>15||s[306]<5||s[306]>9||s[324])return false;
 uint mask=0;for(uint i=3;i<=7;++i){if(s[300+3*i]>1)return false;mask|=s[300+3*i]<<(i-3);}if(mask==31)return false;
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<9)||s[301+3*i]!=(i<9?(i?20U:8U):0U))return false;return true;
}
static bool validP503Extra(const Common::Array<uint32>&w,const Common::Array<uint32>&s){
 if(w.size()!=118||!validP503State(s))return false;
 for(uint i=0;i<50;++i)if((i<23||i>32)&&(w[i]||w[50+i]))return false;
 for(int t=5;t<=9;++t){const uint p=t+18,q=37-t;const bool solved=s[300+3*(t-2)]!=0;
  if(solved){if(w[p]!=4||(w[q]!=1&&w[q]!=4)||int32(w[50+p])!=-int(q+1)||w[50+q]!=p+1)return false;}
  else if((w[p]!=0&&w[p]!=2&&w[p]!=3)||w[q]||w[50+p]||w[50+q])return false;
 }
 if(!((w[100]==0xffffffffU&&!w[101])||(w[100]==3&&w[101]==34)))return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;for(uint i=0;i<8;++i){empty&=!w[102+i]&&!w[110+i];configured&=w[102+i]==widths[i]&&w[110+i]==heights[i];}return empty||configured;
}
static bool validP503Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,const Common::Array<uint32>&extra,uint32 clock){
 if(w.size()!=48*27||!validP503Scene(original)||!validP503Extra(extra,state)||int32(clock-state[601])<0)return false;
 Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint speed=state[303],direction=state[300],target=state[306];for(uint i=4;i<=8;++i)expected.sprites[i].visible=target==i+1;for(uint i=19;i<=22;++i)expected.sprites[i].visible=direction==i-18;
 int digits=cometSpeed(speed);for(int i=18;i>=13;--i){expected.sprites[i].selectedFrame=digits%10;digits/=10;}
 expected.sprites[11].visible=speed>=1;for(uint i=34;i<48;++i)expected.sprites[i].visible=speed>=i-32;
 bool launched=false,low=false,orbit=false;
 for(int t=5;t<=9;++t){const uint p=t+18,q=37-t;launched|=extra[p]!=0;low|=extra[p]==2;orbit|=extra[p]==4;
  for(uint index:{p,q}){Sprite&s=expected.sprites[index];const uint at=index*27,kind=extra[index];
   if(w[at+1]>=spriteFrameCount(original,index)||((s.autoFrame||kind)&&int32(clock-w[at+8])<0)||(kind!=0&&kind!=1&&int32(clock-w[at+9])<0))return false;
   if(!kind){if(index==q&&(extra[p]==2||extra[p]==3)){s.autoFrame=true;s.frameData[0]=30;s.frameData[1]=1;s.frameData[2]=0;}if(s.autoFrame){s.selectedFrame=w[at+1];s.frameSince=w[at+8];}continue;}
   if(kind==2||kind==3){s.y=285;s.renderX=kind==2?340:197;s.renderY=kind==2?190:9;s.standardMotion=true;s.autoFrame=false;s.frameData[0]=s.moveData[0]=-1;s.selectedFrame=w[at+1];s.frameSince=w[at+8];s.moveSince=w[at+9];continue;}
   s.x=320;s.y=160;s.moveData[1]=t*25;s.moveData[2]=t*12;s.standardMotion=s.autoFrame=true;s.frameData[0]=30;s.frameData[1]=1;s.frameData[2]=0;s.selectedFrame=w[at+1];s.frameSince=w[at+8];
   if(kind==1){if(index!=q||w[at]||w[at+7]||w[at+9])return false;continue;}
   const int x=int32(w[at+4]),y=int32(w[at+5]),dx=int32(w[at+11]),dy=int32(w[at+12]);
   const int widths[]={60,110,39,50,28},heights[]={60,40,100,50,30};const int width=widths[t-5],height=heights[t-5];
   if(!width||!height||w[at]>1||w[at+14]>1||w[at+15]>1||x<320-t*25-width-2||x>MAX(320+t*25+2,545)||y<160-t*12-height-1||y>160+t*12+1||!((dx==0&&dy>=-1&&dy<=1)||(dy==0&&(dx==-2||dx==2)))||(!w[at]&&(dx||dy)))return false;
   s.visible=w[at];s.autoMove=true;s.moveData[0]=40;s.renderX=x;s.renderY=y;s.moveDX=dx;s.moveDY=dy;s.orbitSideX=w[at+14];s.orbitSideY=w[at+15];s.moveSince=w[at+9];
  }
  if(extra[p]==4&&w[p*27]+w[q*27]!=1)return false;
 }
 if(launched){Sprite&launch=expected.sprites[12];launch.visible=0;launch.frameData[0]=launch.moveData[0]=-1;}
 const uint at=33*27;const bool exploded=w[at+19]==0xffffffffU&&w[at+22]==0xffffffffU;if(low&&!exploded)return false;if(!launched&&exploded)return false;
 if(exploded){Sprite&e=expected.sprites[33];e.selectedFrame=9;e.renderX=320;e.renderY=160;e.frameData[0]=e.moveData[0]=-1;}
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}

static bool p503Assets(){return universeFileIdentity(ConfMan.getPath("path").join("PLACES/P503/MEGAFILE.HYP"),782595,231093171U);}
bool AstronomicaEngine::canSaveP503()const{
 if(_place!=503||!_p503AssetsValid||!_runner.scriptsIdle()||!validP503Scene(_scene)||_questionSaveBaseline.size()!=48||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;
 if(_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_ball.scenario||_ball.centerX||_ball.centerY||_ball.side!=2||_ball.period!=10||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_plotEvent||_plotTime||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w,extra;if(!_runner.exportPersistentState(state))return false;p516Extra(extra);for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP503Sprites(w,original,state,extra,scriptClock());
}
Common::Error AstronomicaEngine::saveP503(Common::WriteStream*stream){
 if(!canSaveP503())return Common::kWritingFailed;Common::Array<uint32>state,w,extra;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);p516Extra(extra);const uint32 h[]={503,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),0};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(25);uint32 hash=2166136261U;auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)put(v);for(uint32 v:w)put(v);for(uint32 v:state)put(v);for(uint32 v:extra)put(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP503(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+48*27+605+118+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto get=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();Common::Array<uint32>w,state,extra;w.resize(1296);state.resize(605);extra.resize(118);for(uint32&v:w)v=get();for(uint32&v:state)v=get();for(uint32&v:extra)v=get();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=503||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]||!p503Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P503/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP503Sprites(w,parsed,state,extra,h[2]))return Common::kReadingFailed;ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);if(!prepared.importPersistentState(state))return Common::kReadingFailed;
 if(!loadPlace(503,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P503 state could not be installed");_p503AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<48;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP502Scene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=35||s.conditions.size()!=4||s.scripts.size()!=2||!s.mouseRects.empty()||!s.movies.empty()||s.consumed!=586447||s.trailing!=83184)return false;
 const uint frames[]={2,2,2,2,2,2,2,1,6,10,10,10,10,10,10,2,2,2,2,12,10,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
 for(uint i=0;i<35;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=21?8:i>=10&&i<=14?10:-1))return false;return true;
}
static bool validP502State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]<1||s[300]>4||s[303]>15||s[306]!=10||s[309])return false;
 const uint widths[]={8,20,20,20};for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<4)||s[301+3*i]!=(i<4?widths[i]:0U))return false;return true;
}
static bool validP502Extra(const Common::Array<uint32>&w){
 if(w.size()!=118||(w[19]!=0&&w[19]!=2&&w[19]!=3))return false;
 for(uint i=0;i<100;++i)if(i!=19&&w[i])return false;
 if(w[19]==2?(w[100]!=3||w[101]!=21):(w[100]!=0xffffffffU||w[101]))return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;for(uint i=0;i<8;++i){empty&=!w[102+i]&&!w[110+i];configured&=w[102+i]==widths[i]&&w[110+i]==heights[i];}return empty||configured;
}
static bool validP502Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,const Common::Array<uint32>&extra,uint32 clock){
 if(w.size()!=35*27||!validP502Scene(original)||!validP502State(state)||!validP502Extra(extra)||int32(clock-state[601])<0)return false;
 Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint speed=state[303],direction=state[300];for(uint i=15;i<=18;++i)expected.sprites[i].selectedFrame=direction==i-14;
 int digits=cometSpeed(speed);for(int i=14;i>=9;--i){expected.sprites[i].selectedFrame=digits%10;digits/=10;}
 expected.sprites[7].visible=speed>=1;for(uint i=21;i<35;++i)expected.sprites[i].visible=speed>=i-19;
 if(extra[19]){Sprite&p=expected.sprites[19];p.y=310;p.renderX=extra[19]==2?340:199;p.renderY=extra[19]==2?190:10;p.selectedFrame=extra[19]==2?5:0;p.standardMotion=true;p.frameData[0]=p.moveData[0]=-1;if(int32(clock-w[19*27+9])<0)return false;p.moveSince=w[19*27+9];Sprite&launch=expected.sprites[8];launch.visible=0;launch.frameData[0]=launch.moveData[0]=-1;}
 // A high launch can retain an older low-failure explosion, independently.
 const uint at=20*27;const bool exploded=w[at+19]==0xffffffffU&&w[at+22]==0xffffffffU;
 if(extra[19]==2&&!exploded)return false;if(!extra[19]&&exploded)return false;
 if(exploded){Sprite&e=expected.sprites[20];e.selectedFrame=9;e.renderX=320;e.renderY=160;e.frameData[0]=e.moveData[0]=-1;}
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}
static bool p502Assets(){return universeFileIdentity(ConfMan.getPath("path").join("PLACES/P502/MEGAFILE.HYP"),669631,2443827672U);}
bool AstronomicaEngine::canSaveP502()const{
 if(_place!=502||!_p502AssetsValid||!_runner.scriptsIdle()||!validP502Scene(_scene)||_questionSaveBaseline.size()!=35||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;
 if(_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_ball.scenario||_ball.centerX||_ball.centerY||_ball.side!=2||_ball.period!=10||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_plotEvent||_plotTime||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w,extra;if(!_runner.exportPersistentState(state))return false;p516Extra(extra);for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP502Sprites(w,original,state,extra,scriptClock());
}
Common::Error AstronomicaEngine::saveP502(Common::WriteStream*stream){
 if(!canSaveP502())return Common::kWritingFailed;Common::Array<uint32>state,w,extra;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);p516Extra(extra);const uint32 h[]={502,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),0};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(24);uint32 hash=2166136261U;auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)put(v);for(uint32 v:w)put(v);for(uint32 v:state)put(v);for(uint32 v:extra)put(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP502(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+35*27+605+118+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto get=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();Common::Array<uint32>w,state,extra;w.resize(945);state.resize(605);extra.resize(118);for(uint32&v:w)v=get();for(uint32&v:state)v=get();for(uint32&v:extra)v=get();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=502||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]||!p502Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P502/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP502Sprites(w,parsed,state,extra,h[2]))return Common::kReadingFailed;ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);if(!prepared.importPersistentState(state))return Common::kReadingFailed;
 if(!loadPlace(502,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P502 state could not be installed");_p502AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<35;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP527Scene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=9||s.conditions.size()!=8||s.scripts.size()!=1||!s.mouseRects.empty()||s.movies.size()!=1||!s.movies[0].equalsIgnoreCase("FLATRING.MOV"))return false;
 for(uint i=0;i<9;++i)if(spriteFrameCount(s,i)!=2||s.sprites[i].clone!=-1)return false;return true;
}
static bool validP527State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]!=52||s[303]||s[306]||s[309]>4||s[312]!=1||s[315]>=15||s[318]>1||s[321]!=uint32(bool(s[315]&2))||(s[315]&&!s[318]))return false;
 const uint widths[]={52,3,16,8,1,4,0,0};
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<8)||s[301+3*i]!=(i<8?widths[i]:0U))return false;
 return !s[315]||s[309];
}
static bool validP527Extra(const Common::Array<uint32>&w){
 if(w.size()!=118||w[100]!=0xffffffffU||w[101])return false;
 for(uint i=0;i<100;++i)if(w[i])return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};
 bool empty=true,configured=true;for(uint i=0;i<8;++i){empty&=!w[102+i]&&!w[110+i];configured&=w[102+i]==widths[i]&&w[110+i]==heights[i];}return empty||configured;
}
static int p527RangeBit(uint start,uint end){const uint starts[]={1800,2568,900,0},lengths[]={599,959,899,899};for(uint i=0;i<4;++i)if(start==starts[i]&&end==starts[i]+lengths[i])return 1U<<i;return 0;}
static int p527FrameBit(int frame){return frame>=600&&frame<=799?1:frame>=801&&frame<=1079?2:frame>=300&&frame<=599?4:frame>=0&&frame<=299?8:0;}
static bool validP527Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&s,uint32 clock,int frame,uint start,uint end){
 if(w.size()!=9*27||!validP527Scene(original)||!validP527State(s)||int32(clock-s[601])<0||frame< -1)return false;
 if(s[315]==0){if(start||end||frame!=-1)return false;}else if(!(p527RangeBit(start,end)&s[315]))return false;
 if(frame!=-1&&!(p527FrameBit(frame)&s[315]))return false;
 Scene expected=original;for(uint i=0;i<9;++i)expected.sprites[i].selectedFrame=i<4&&s[309]==i+1;
 Common::Array<uint32>baseline;for(const Sprite&v:expected.sprites)p526SpriteWords(v,baseline);return baseline==w;
}
static bool p527Assets(){const Common::Path b=ConfMan.getPath("path").join("PLACES/P527");return universeFileIdentity(b.join("MEGAFILE.HYP"),348102,3684137004U)&&universeFileIdentity(b.join("FLATRING.MOV"),8387803,799535745U);}
bool AstronomicaEngine::canSaveP527()const{
 if(_place!=527||!_p527AssetsValid||!_movie||_moviePlaying||!_runner.scriptsIdle()||!validP527Scene(_scene)||_questionSaveBaseline.size()!=9||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;
 if(_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_ball.scenario||_ball.centerX||_ball.centerY||_ball.side!=2||_ball.period!=10||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_plotEvent||_plotTime||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;
 for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 if(_moviePresentedFrame==-1?_movieFrame.w!=0:(_movieFrame.w!=320||_movieFrame.h!=240||_movieX!=10||_movieY!=10))return false;
 Common::Array<uint32>s,w,extra;if(!_runner.exportPersistentState(s))return false;p516Extra(extra);if(!validP527Extra(extra))return false;
 for(const Sprite&v:_scene.sprites){if(v.dragEnabled||v.orbitMotion||v.planetMotion||v.planetPeriod!=-1)return false;p526SpriteWords(v,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP527Sprites(w,original,s,scriptClock(),_moviePresentedFrame,_movieSegmentStart,_universeSegmentEnd);
}
Common::Error AstronomicaEngine::saveP527(Common::WriteStream*stream){
 if(!canSaveP527())return Common::kWritingFailed;Common::Array<uint32>s,w,extra;_runner.exportPersistentState(s);for(const Sprite&v:_scene.sprites)p526SpriteWords(v,w);p516Extra(extra);
 const bool absent=_moviePresentedFrame<0;const uint32 h[]={527,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_moviePresentedFrame),absent?0U:uint32(_movieX),absent?0U:uint32(_movieY),_movieSegmentStart,_universeSegmentEnd,uint32(_comet.frame),uint32(_comet.previousFrame),0};
 stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(23);uint32 hash=2166136261U;auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)put(v);for(uint32 v:w)put(v);for(uint32 v:s)put(v);for(uint32 v:extra)put(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP527(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(16+9*27+605+118+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[16],hash=2166136261U;auto get=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();Common::Array<uint32>w,s,extra;w.resize(9*27);s.resize(605);extra.resize(118);for(uint32&v:w)v=get();for(uint32&v:s)v=get();for(uint32&v:extra)v=get();
 if(stream->readUint32LE()!=hash||stream->err()||h[0]!=527||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[13]<1||h[13]>12||h[14]>12||h[15]||(h[8]==0xffffffffU?(h[9]||h[10]):(h[9]!=10||h[10]!=10))||!validP527Extra(extra)||!p527Assets())return Common::kReadingFailed;
 const Common::Path folder=ConfMan.getPath("path").join("PLACES/P527");Common::File file;if(!file.open(Common::FSNode(folder.join("MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP527Sprites(w,parsed,s,h[2],int32(h[8]),h[11],h[12]))return Common::kReadingFailed;
 ScriptRunner runner;runner.loadLocalConditions(parsed.conditions);if(!runner.importPersistentState(s))return Common::kReadingFailed;
 Video::QuickTimeDecoder*prepared=new Video::QuickTimeDecoder();Common::File*movie=new Common::File();if(!movie->open(Common::FSNode(folder.join("FLATRING.MOV")))){delete movie;delete prepared;return Common::kReadingFailed;}
 if(!prepared->loadStream(movie)||!prepared->isSeekable()||prepared->getFrameCount()!=1105||prepared->getTimeScale()!=30||prepared->getWidth()!=320||prepared->getHeight()!=240){delete prepared;return Common::kReadingFailed;}
 Graphics::Surface residual;
 if(h[8]!=0xffffffffU){if(!prepared->seekToFrame(h[8])){delete prepared;return Common::kReadingFailed;}const Graphics::Surface*f=prepared->decodeNextFrame();if(!f||prepared->getCurFrame()!=int(h[8])){delete prepared;return Common::kReadingFailed;}Graphics::Surface*rgb=f->convertTo(_screen.format,prepared->getPalette());if(!rgb||rgb->w!=320||rgb->h!=240){if(rgb){rgb->free();delete rgb;}delete prepared;return Common::kReadingFailed;}residual.copyFrom(*rgb);rgb->free();delete rgb;}
 if(!loadPlace(527,false,true)){residual.free();delete prepared;return Common::kReadingFailed;}delete _movie;_movie=prepared;_movie->setVolume(ConfMan.getBool("astronomica_audio")?255:0);if(!_runner.importPersistentState(s))error("Validated P527 state could not be installed");_p527AssetsValid=true;
 _puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_moviePresentedFrame=int32(h[8]);_movieX=h[9];_movieY=h[10];_movieSegmentStart=h[11];_universeSegmentEnd=h[12];_moviePlaying=false;if(h[12])_movie->setEndTime(Audio::Timestamp(0,h[12],30));_comet.frame=h[13];_comet.previousFrame=h[14];
 for(uint i=0;i<9;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}if(residual.w)_movieFrame.copyFrom(residual);residual.free();redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP516State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]<1||s[300]>4||s[303]>15||s[306])return false;
 const uint widths[]={8,16,0};for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<3)||s[301+3*i]!=(i<3?widths[i]:0U))return false;return true;
}
static bool validP516Scene(const Scene&s){
 if(s.mode||s.layers!=2||s.sprites.size()!=37||s.conditions.size()!=3||s.scripts.size()!=2||!s.movies.empty()||!s.mouseRects.empty())return false;
 const uint frames[]={2,2,2,2,2,2,1,1,1,1,1,2,12,1,1,1,3,3,1,1,1,1,10,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
 for(uint i=0;i<37;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=23?7:i>=17&&i<=20?34-int(i):-1))return false;return true;
}
static bool validP516Extra(const Common::Array<uint32>&w){
 if(w.size()!=118||w[100]!=0xffffffffU||w[101])return false;
 for(uint i=0;i<50;++i){const int id=i+1;const uint kind=i>=13&&i<=20?4:0;const int partner=kind?(id<=17?35-id:id-35):0;if(w[i]!=kind||int32(w[50+i])!=partner)return false;}
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};for(uint i=0;i<8;++i)if(w[102+i]!=widths[i]||w[110+i]!=heights[i])return false;return true;
}
static bool validP516Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,uint32 clock){
 if(w.size()!=37*27||!validP516Scene(original)||!validP516State(state)||int32(clock-state[601])<0)return false;Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint direction=state[300],speed=state[303];for(uint i=7;i<11;++i)expected.sprites[i].visible=direction==i-6;expected.sprites[6].visible=speed>=1;for(uint i=23;i<37;++i)expected.sprites[i].visible=speed>=i-21;
 for(uint i=13;i<=20;++i){Sprite&s=expected.sprites[i];const uint at=i*27;const int id=i+1,radius=id<=17?18-id:id-17,a=radius*40+100,b=radius*12+50;
  const int x=int32(w[at+4]),y=int32(w[at+5]),dx=int32(w[at+11]),dy=int32(w[at+12]);
  if(w[at]>1||w[at+1]>=spriteFrameCount(original,i)||x<320-a-2||x>320+a+2||y<100-b-1||y>100+b+1||w[at+14]>1||w[at+15]>1||w[at+14]+w[at+15]>1||!((dx==0&&(dy>=-1&&dy<=1))||(dy==0&&(dx==-2||dx==2)))||(!w[at]&&(dx||dy))||int32(clock-w[at+9])<0)return false;
  s.x=320;s.y=100;s.renderX=x;s.renderY=y;s.visible=w[at];s.selectedFrame=w[at+1];s.standardMotion=s.autoMove=true;s.moveData[0]=10;s.moveData[1]=a;s.moveData[2]=b;s.moveDX=dx;s.moveDY=dy;s.orbitSideX=w[at+14];s.orbitSideY=w[at+15];s.moveSince=w[at+9];
  if(s.autoFrame){if(int32(clock-w[at+8])<0)return false;s.frameSince=w[at+8];}
 }
 for(uint i=13;i<=16;++i)if(w[i*27]+w[(33-i)*27]!=1)return false;
 Sprite&projectile=expected.sprites[12];const uint at=12*27;
 // These stopped subtypes are proved; do not normalize unproved opcode30
 // aborts that retain a nonzero delta from an ordinary active-flight history.
 if(w[at+19]==0xffffffffU&&w[at+22]==0xffffffffU){projectile.frameData[0]=projectile.moveData[0]=-1;
  if(w[at+10]==1){const int x=int32(w[at+4]),y=int32(w[at+5]);if(x< -78||x>676||y< -65||y>300||int32(clock-w[at+9])<0)return false;projectile.standardMotion=true;projectile.renderX=x;projectile.renderY=y;projectile.moveSince=w[at+9];}
 }
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}
static bool p516Assets(){return universeFileIdentity(ConfMan.getPath("path").join("PLACES/P516/MEGAFILE.HYP"),563403,3687920615U);}
void AstronomicaEngine::p516Extra(Common::Array<uint32>&w)const{w.clear();for(int v:_comet.kind)w.push_back(v);for(int v:_comet.partner)w.push_back(v);w.push_back(_comet.sound);w.push_back(_comet.explosion);for(int v:_jupiterWidths)w.push_back(v);for(int v:_jupiterHeights)w.push_back(v);}
bool AstronomicaEngine::canSaveP516()const{
 if(_place!=516||!_p516AssetsValid||!_runner.scriptsIdle()||!validP516Scene(_scene)||_questionSaveBaseline.size()!=37||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))return false;for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w,extra;if(!_runner.exportPersistentState(state)||!validP516State(state))return false;p516Extra(extra);if(!validP516Extra(extra))return false;for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP516Sprites(w,original,state,scriptClock());
}
Common::Error AstronomicaEngine::saveP516(Common::WriteStream*stream){
 if(!canSaveP516())return Common::kWritingFailed;Common::Array<uint32>state,w,extra;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);p516Extra(extra);const uint32 h[]={516,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),0};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(22);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);for(uint32 v:extra)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP516(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+37*27+605+118+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state,extra;w.resize(37*27);state.resize(605);extra.resize(118);for(uint32&v:w)v=read();for(uint32&v:state)v=read();for(uint32&v:extra)v=read();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=516||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]||!validP516State(state)||!validP516Extra(extra)||!p516Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P516/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP516Sprites(w,parsed,state,h[2]))return Common::kReadingFailed;
 for(uint i=13;i<=20;++i){const Frame*f=spriteFrameAt(parsed,i,0);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return Common::kReadingFailed;const bool ok=bmp->w==int(extra[102+i-13])&&bmp->h==int(extra[110+i-13]);bmp->free();delete bmp;if(!ok)return Common::kReadingFailed;}
 ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);if(!prepared.importPersistentState(state))return Common::kReadingFailed;
 if(!loadPlace(516,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P516 state could not be installed");_p516AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<37;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);for(uint i=0;i<50;++i){_comet.kind[i]=int32(extra[i]);_comet.partner[i]=int32(extra[50+i]);}_comet.sound=int32(extra[100]);_comet.explosion=int32(extra[101]);for(uint i=0;i<8;++i){_jupiterWidths[i]=extra[102+i];_jupiterHeights[i]=extra[110+i];}redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP511State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]>52||s[300]%4||s[303]||s[306]>15||s[309]<1||s[309]>4||s[312]!=1)return false;
 const uint mask=(s[309]==1?1:0)|(s[306]==15?2:0)|(s[300]==0?4:0);if(s[315]!=mask||mask>6)return false;
 const uint widths[]={52,3,16,8,1,3};for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<6)||s[301+3*i]!=(i<6?widths[i]:0U))return false;return true;
}
static bool validP511Scene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=35||s.conditions.size()!=6||s.scripts.size()!=5||!s.movies.empty()||!s.mouseRects.empty())return false;
 const uint frames[]={2,2,2,2,4,1,1,1,1,2,2,1,2,2,2,2,2,2,1,4,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
 for(uint i=0;i<35;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=21?12:-1))return false;return true;
}
static uint p511Cloud(uint cloud){return cloud<14?3:cloud<27?2:cloud<40?1:0;}
static int p511Image(const Common::String&name){for(uint i=0;i<4;++i)if(name.equalsIgnoreCase(Common::String::format("CLOUD%u",i)))return i;return -1;}
static bool validP511Sprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,uint image,uint32 clock){
 if(w.size()!=35*27||!validP511Scene(original)||!validP511State(state)||image!=p511Cloud(state[300])||int32(clock-state[601])<0)return false;
 Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint dial=state[306],type=state[309];Sprite&sky=expected.sprites[4];sky.x=sky.renderX=0;sky.y=sky.renderY=type==1?170:type==2?188:204;
 const int first=int32(w[4*27+16]),last=int32(w[4*27+17]);
 const bool range=last==first+1&&((dial<=3&&first==2)||(dial>=4&&dial<=7&&(first==1||first==2))||(dial==8&&first==1)||(dial>=9&&dial<=13&&(first==0||first==1))||(dial>=14&&first==0));if(!range)return false;sky.frameFirst=first;sky.frameLast=last;
 expected.sprites[5].visible=type<=2;expected.sprites[6].visible=type==1;
 expected.sprites[11].visible=dial>=1;for(uint i=21;i<35;++i)expected.sprites[i].visible=dial>=i-19;
 for(uint i=12;i<16;++i)expected.sprites[i].selectedFrame=type==i-11;
 expected.sprites[18].x=expected.sprites[18].renderX=477;expected.sprites[18].y=expected.sprites[18].renderY=411-state[300];
 // Explicit range updates retain the selected frame until the next real tick.
 for(uint i:{4U,19U,20U}){if(w[i*27+1]>=spriteFrameCount(original,i)||int32(clock-w[i*27+8])<0)return false;expected.sprites[i].selectedFrame=w[i*27+1];expected.sprites[i].frameSince=w[i*27+8];}
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}
static bool p511Assets(){
 const Common::Path base=ConfMan.getPath("path").join("PLACES/P511");
 return universeFileIdentity(base.join("MEGAFILE.HYP"),635643,153639794U)&&universeFileIdentity(base.join("CLOUD0"),61120,3545178943U)&&universeFileIdentity(base.join("CLOUD1"),61120,3525922351U)&&universeFileIdentity(base.join("CLOUD2"),61120,1646671861U)&&universeFileIdentity(base.join("CLOUD3"),61120,4221605925U);
}
bool AstronomicaEngine::canSaveP511()const{
 if(_place!=511||!_p511AssetsValid||!_runner.scriptsIdle()||!validP511Scene(_scene)||_questionSaveBaseline.size()!=35||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||p511Image(_displayedImageName)<0||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&(_lastSound!=_loopSound||!_loopEnabled)))return false;for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w;if(!_runner.exportPersistentState(state)||!validP511State(state))return false;for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP511Sprites(w,original,state,p511Image(_displayedImageName),scriptClock());
}
Common::Error AstronomicaEngine::saveP511(Common::WriteStream*stream){
 if(!canSaveP511())return Common::kWritingFailed;Common::Array<uint32>state,w;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);const uint32 h[]={511,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),uint32(p511Image(_displayedImageName))};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(21);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP511(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+35*27+605+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state;w.resize(35*27);state.resize(605);for(uint32&v:w)v=read();for(uint32&v:state)v=read();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=511||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]>3||!validP511State(state)||!p511Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P511/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP511Sprites(w,parsed,state,h[10],h[2]))return Common::kReadingFailed;
 // Preflight every original image and the configured runner before mutation.
 for(uint i=0;i<4;++i){Graphics::Surface*image=openBackgroundImage(Common::String::format("CLOUD%u",i),511);if(!image)return Common::kReadingFailed;const bool valid=image->w==315&&image->h==190;image->free();delete image;if(!valid)return Common::kReadingFailed;}
 ScriptRunner prepared;prepared.loadLocalConditions(parsed.conditions);if(!prepared.importPersistentState(state))return Common::kReadingFailed;
 if(!loadPlace(511,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P511 state could not be installed");_p511AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<35;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);if(!stageBackgroundImage(Common::String::format("CLOUD%u",h[10]),325,0))error("Preflighted P511 image disappeared");displayBackgroundImage();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validP521State(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s))return false;
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]||s[301+3*i])return false;return true;
}
static bool validP521Scene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=27||!s.conditions.empty()||s.scripts.size()!=1||s.scripts[0].size()!=1||!s.movies.empty()||!s.mouseRects.empty())return false;
 const uint frames[]={2,2,2,2,2,1,1,1,1,1,2,2,14,3,3,3,3,3,3,3,3,3,3,2,2,2,2};
 for(uint i=0;i<27;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=14&&i<=17?14:i>=19&&i<=22?19:-1))return false;return true;
}
static bool validP521Sprites(const Common::Array<uint32>&w,const Scene&original,uint image,uint32 clock){
 if(w.size()!=27*27||!validP521Scene(original)||image>1||(image&&w[10*27+19]!=0xffffffffU))return false;Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 Sprite&pose=expected.sprites[12];pose.x=pose.renderX=15;pose.y=pose.renderY=251;pose.selectedFrame=2;
 Sprite&always=expected.sprites[11];if(w[11*27+1]>1||int32(clock-w[11*27+8])<0)return false;always.selectedFrame=w[11*27+1];always.frameSince=w[11*27+8];
 Sprite&voice=expected.sprites[10];if(w[10*27+19]==0xffffffffU){if(w[10*27+1]>1||int32(clock-w[10*27+8])<0)return false;voice.frameData[0]=-1;voice.frameData[1]=1;voice.frameData[2]=0;voice.selectedFrame=w[10*27+1];voice.frameSince=w[10*27+8];}
 if(image){
  const int dx[]={2,-10,5,-3,4,-3,-2,2,3,1},dy[]={2,5,1,-7,-3,2,-1,3,-4,1};
  for(uint i=13;i<23;++i){Sprite&s=expected.sprites[i];const uint at=i*27;const int k=i-13,width=i<18?30:55,height=i<18?28:52;
   const int x=int32(w[at+4]),y=int32(w[at+5]);if(x<int(-width+MIN(dx[k],0))||x>640+MAX(dx[k],0)||y<int(-height+MIN(dy[k],0))||y>320+MAX(dy[k],0)||w[at+1]>2||int32(clock-w[at+8])<0||int32(clock-w[at+9])<0)return false;
   s.standardMotion=true;s.frameData[0]=-1;s.frameData[1]=1;s.frameData[2]=0;s.moveData[0]=-1;s.moveData[1]=dx[k];s.moveData[2]=dy[k];s.moveData[3]=2;s.moveData[4]=0;s.moveDX=dx[k];s.moveDY=dy[k];s.renderX=x;s.renderY=y;s.selectedFrame=w[at+1];s.frameSince=w[at+8];s.moveSince=w[at+9];
  }
 }
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}
static bool p521Assets(){
 const Common::Path base=ConfMan.getPath("path").join("PLACES/P521");return universeFileIdentity(base.join("MEGAFILE.HYP"),717441,1101702870U)&&universeFileIdentity(base.join("EARTH_B"),205878,0x5c98bffbU)&&universeFileIdentity(base.join("ROCKS_B"),205878,0x2f1f989dU);
}
static int p521Image(const Common::String&name){if(name.empty())return 0;return name.equalsIgnoreCase("EARTH_B")?1:-1;}
bool AstronomicaEngine::canSaveP521()const{
 if(_place!=521||!_p521AssetsValid||!_runner.scriptsIdle()||!validP521Scene(_scene)||_questionSaveBaseline.size()!=27||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||p521Image(_displayedImageName)<0||!_loopEnabled||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&(_lastSound!=_loopSound||!_loopEnabled)))return false;for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w;if(!_runner.exportPersistentState(state)||!validP521State(state))return false;for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validP521Sprites(w,original,p521Image(_displayedImageName),scriptClock());
}
Common::Error AstronomicaEngine::saveP521(Common::WriteStream*stream){
 if(!canSaveP521())return Common::kWritingFailed;Common::Array<uint32>state,w;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);const uint32 h[]={521,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),uint32(p521Image(_displayedImageName))};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(19);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP521(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(11+27*27+605+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[11],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state;w.resize(27*27);state.resize(605);for(uint32&v:w)v=read();for(uint32&v:state)v=read();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=521||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]!=1||h[7]>1||(h[7]&&h[4])||h[8]<1||h[8]>12||h[9]>12||h[10]>1||!validP521State(state)||!p521Assets())return Common::kReadingFailed;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P521/MEGAFILE.HYP"))))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validP521Sprites(w,parsed,h[10],h[2]))return Common::kReadingFailed;
 // Decode both immutable image resources before mutation, including future choice5.
 for(const char*name:{"EARTH_B","ROCKS_B"}){Common::File image;if(!image.open(Common::FSNode(ConfMan.getPath("path").join(Common::String::format("PLACES/P521/%s",name)))))return Common::kReadingFailed;Image::BitmapDecoder decoder;if(!decoder.loadStream(image)||!decoder.getSurface()||decoder.getSurface()->w!=640||decoder.getSurface()->h!=320)return Common::kReadingFailed;Graphics::Surface*converted=decoder.getSurface()->convertTo(_screen.format,decoder.getPalette().data(),decoder.getPalette().size());if(!converted)return Common::kReadingFailed;converted->free();delete converted;}
 if(!loadPlace(521,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P521 state could not be installed");_p521AssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=true;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<27;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);if(h[10]){if(!stageBackgroundImage("EARTH_b",0,0))error("Preflighted P521 image disappeared");displayBackgroundImage();}else redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static void planetSpriteWords(const Sprite&s,Common::Array<uint32>&w){p526SpriteWords(s,w);w.push_back(s.planetMotion);w.push_back(s.planetPeriod);}
static bool validPlanetState(const Common::Array<uint32>&s){
 if(!ScriptRunner::validPersistentState(s)||s[300]>15||s[303]>511||s[306]<1||s[306]>9||s[309]>8)return false;
 const uint widths[]={20,9,9,20};for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[302+3*i]!=uint32(i<4)||s[301+3*i]!=(i<4?widths[i]:0U))return false;return true;
}
static bool validPlanetScene(const Scene&s){
 if(s.mode||s.layers!=1||s.sprites.size()!=32||s.conditions.size()!=4||s.scripts.size()!=3||!s.movies.empty()||!s.mouseRects.empty())return false;
 const int raw[4][6]={{1,0,20,0,0,20},{1,1,9,0,0,511},{1,2,9,1,1,9},{1,3,20,0,0,20}};for(uint i=0;i<4;++i)for(uint j=0;j<6;++j)if(s.conditions[i].raw[j]!=raw[i][j])return false;
 const uint frames[]={2,2,2,2,2,2,1,2,1,3,3,11,11,3,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1};for(uint i=0;i<32;++i)if(spriteFrameCount(s,i)!=frames[i]||s.sprites[i].clone!=(i>=18?7:-1))return false;return true;
}
static bool validPlanetSprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,uint32 clock){
 if(w.size()!=32*29||!validPlanetScene(original)||!validPlanetState(state))return false;Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 const uint setting=state[300];expected.sprites[6].visible=setting>=1;for(uint i=18;i<32;++i)expected.sprites[i].visible=setting>=i-16;
 Sprite&launcher=expected.sprites[8];launcher.standardMotion=true;launcher.moveDX=0;launcher.renderX=int16(w[8*29+4]);launcher.moveDY=int16(w[8*29+12]);launcher.renderY=int16(w[8*29+5]);launcher.moveSince=w[8*29+9];
 if((launcher.renderX!=602&&launcher.renderX!=603)||int32(clock-launcher.moveSince)<0||launcher.renderY<8||launcher.renderY>236||(launcher.renderY&1)||(launcher.moveDY!=2&&launcher.moveDY!=-2)||(launcher.moveDY==2&&launcher.renderY<10)||(launcher.moveDY==-2&&launcher.renderY>234))return false;
 const uint widths[]={30,44,54,40,60,110,39,50,28};uint mask=0;const uint frameSince=w[9*29+8];if(int32(clock-frameSince)<0)return false;
 for(uint i=9;i<18;++i){Sprite&s=expected.sprites[i];const uint at=i*29,mode=w[at+27],id=i-8,category=w[at+22];const int period=int32(w[at+28]);
  if(mode>2||w[at+8]!=frameSince||w[at+1]>=spriteFrameCount(original,i))return false;s.frameSince=frameSince;s.selectedFrame=w[at+1];
  if((i==10||i==13||i==17)&&w[at+1]!=w[9*29+1])return false;if(i==12&&w[at+1]!=w[11*29+1])return false;
  if(mode){s.planetMotion=mode;s.planetPeriod=period;s.standardMotion=true;s.autoMove=w[at+7]!=0;s.visible=w[at]!=0;s.x=id;s.moveData[0]=category;s.renderX=int16(w[at+4]);s.renderY=int16(w[at+5]);s.moveDX=int16(w[at+11]);s.moveDY=int16(w[at+12]);s.moveSince=w[at+9];
   if(category>15||int32(clock-s.moveSince)<0)return false;
   if(mode==1){if(!s.visible||!s.autoMove||period!=10||s.moveDX||(s.moveDY!=2&&s.moveDY!=-2)||(s.renderX!=603-int(widths[i-9])&&s.renderX!=602-int(widths[i-9])))return false;mask|=1U<<(id-1);}
   else{if(!category||s.moveDY||(s.moveDX!=-2&&s.moveDX!=2)||s.renderX < -2||s.renderX > 642-int(widths[i-9]))return false;const bool correct=category+id==10||int(category)-int(id)==9;
    if(s.autoMove){if(period!=10||!s.visible)return false;mask|=1U<<(id-1);}else{if(period!=-1||s.visible!=int(correct))return false;if(correct)mask|=1U<<(id-1);}
   }
  }
 }
 // No popcount/count correlation: multiple old flights and exhausted-mask
 // reattachment are genuine original-control histories. Follow Y is retained
 // as native int16 state; old velocity and independent epochs forbid snapping.
 if(mask!=state[303]||w[(state[306]+8)*29+27]!=1)return false;
 Common::Array<uint32>baseline;for(const Sprite&s:expected.sprites)planetSpriteWords(s,baseline);return baseline==w;
}
bool AstronomicaEngine::canSavePlanets()const{
 if(_place!=518||!_planetAssetsValid||!_runner.scriptsIdle()||!validPlanetScene(_scene)||_questionSaveBaseline.size()!=32||_movie||_movieFrame.w||_pendingImage.w||!_displayedImageName.empty()||_comet.frame<1||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&(_lastSound!=_loopSound||!_loopEnabled)))return false;for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w;if(!_runner.exportPersistentState(state))return false;for(const Sprite&s:_scene.sprites){if(s.dragEnabled)return false;planetSpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validPlanetSprites(w,original,state,scriptClock());
}
Common::Error AstronomicaEngine::savePlanets(Common::WriteStream*stream){
 if(!canSavePlanets())return Common::kWritingFailed;Common::Array<uint32>state,w;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)planetSpriteWords(s,w);const uint32 h[]={518,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame)};stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(18);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadPlanets(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<(10+32*29+605+1)*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[10],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state;w.resize(32*29);state.resize(605);for(uint32&v:w)v=read();for(uint32&v:state)v=read();if(stream->readUint32LE()!=hash||stream->err()||h[0]!=518||(h[3]>537&&h[3]!=0xffffffffU)||(h[4]&&h[4]!=0xffffffffU)||h[5]>1||h[7]>1||(h[7]&&(h[4]||!h[5]))||h[8]<1||h[8]>12||h[9]>12)return Common::kReadingFailed;
 const Common::Path path=ConfMan.getPath("path").join("PLACES/P518/MEGAFILE.HYP");if(!universeFileIdentity(path,489731,0x838a2480U))return Common::kReadingFailed;Common::File file;if(!file.open(Common::FSNode(path)))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validPlanetScene(parsed)||!validPlanetSprites(w,parsed,state,h[2]))return Common::kReadingFailed;
 const int widths[]={38,30,44,54,40,60,110,39,50,28},heights[]={36,32,44,52,40,60,40,100,50,30};for(uint i=8;i<18;++i){Graphics::Surface*bmp=decodeSpriteBitmap(file,parsed.sprites[i].frames[0].image,_screen.format);if(!bmp)return Common::kReadingFailed;const bool ok=bmp->w==widths[i-8]&&bmp->h==heights[i-8];bmp->free();delete bmp;if(!ok)return Common::kReadingFailed;}
 if(!loadPlace(518,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P518 state could not be installed");_planetAssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=h[5]!=0;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<32;++i){p526RestoreSprite(_scene.sprites[i],&w[i*29]);_scene.sprites[i].planetMotion=w[i*29+27];_scene.sprites[i].planetPeriod=int32(w[i*29+28]);}redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validRendezvousState(const Common::Array<uint32> &s) {
 if (!ScriptRunner::validPersistentState(s) || s[300] || s[303]!=0xffffffffU || s[306]>1 || s[309]!=54 || s[312]!=1 || s[315]>15 || s[318] || s[321]) return false;
 const uint widths[]={20,19,2,52,1,16,16,1};
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1 || (s[3*i+1] && (i>=3 || s[3*i+1]!=6)) || s[302+3*i]!=uint32(i<8) || s[301+3*i]!=(i<8?widths[i]:0U))return false;
 return true;
}
static bool validRendezvousScene(const Scene &s) {
 if(s.mode || s.layers!=1 || s.sprites.size()!=20 || s.conditions.size()!=8 || s.scripts.size()!=2 || !s.movies.empty() || !s.mouseRects.empty())return false;
 const int raw[8][6]={{1,0,20,0,0,19},{1,1,19,-1,0,18},{1,2,2,0,0,2},{1,3,52,54,0,52},{1,4,1,1,1,1},{1,5,16,0,0,15},{1,6,16,0,0,15},{1,7,1,0,0,1}};
 for(uint i=0;i<8;++i)for(uint j=0;j<6;++j)if(s.conditions[i].raw[j]!=raw[i][j])return false;
 const uint counts[]={2,2,2,2,2,2,16,10,10,10,10,10,10,1,2,2,1,3,12,1};
 for(uint i=0;i<20;++i)if(spriteFrameCount(s,i)!=counts[i] || s.sprites[i].clone!=(i>=8&&i<=12?8:-1))return false;
 return true;
}
static bool rendezvousPhase(const Sprite &actual,const Scene &original,uint index,bool xOnly=false) {
 Scene replay=original;for(Sprite&s:replay.sprites)s.selectedFrame=0;
 const int mode=index==16?0:1;configureRendezvous(replay,mode,0);Sprite &s=replay.sprites[index];s.visible=1;if(index==18)s.selectedFrame=5;
 // Each original145-radius quadrant traverses monotone2-unit coordinates.
 // This bound includes the initial off-ellipse approach and repeated cycles.
 for(uint n=0;n<4096;++n){
  if(xOnly?s.renderX==actual.renderX:(s.renderX==actual.renderX&&s.renderY==actual.renderY&&s.moveDX==actual.moveDX&&s.moveDY==actual.moveDY&&s.orbitSideX==actual.orbitSideX&&s.orbitSideY==actual.orbitSideY&&s.selectedFrame==actual.selectedFrame))return true;
  advanceRendezvous(replay,index,index==16?52:56,index==16?54:56,(n+1)*100);
 }
 return false;
}
static bool validRendezvousSprites(const Common::Array<uint32>&w,const Scene&original,const Common::Array<uint32>&state,uint32 clock) {
 if(w.size()!=20*27 || !validRendezvousScene(original) || !validRendezvousState(state))return false;
 const bool launched=state[306]!=0;const uint speed=state[315];Scene expected=original;for(Sprite&s:expected.sprites)s.selectedFrame=0;
 expected.sprites[6].selectedFrame=speed;expected.sprites[7].selectedFrame=(20+speed)/10;expected.sprites[8].selectedFrame=speed%10;
 configureRendezvous(expected,0,speed);expected.sprites[16].visible=1;
 if(launched){configureRendezvous(expected,1,speed);expected.sprites[18].visible=1;Sprite &launch=expected.sprites[17];launch.x=launch.renderX=170;launch.y=launch.renderY=130;launch.selectedFrame=2;
  // Launch rewrites only the tens digit; a later speed click refreshes it.
  if(w[7*27+1]!=2 && w[7*27+1]!=(20+speed)/10)return false;expected.sprites[7].selectedFrame=w[7*27+1];
 }
 for(uint i=0;i<20;++i){Sprite&s=expected.sprites[i];const uint at=i*27;
  if(i==16 || (launched&&(i==13||i==18))){if(int32(clock-w[at+9])<0)return false;s.moveSince=w[at+9];s.renderX=int16(w[at+4]);s.renderY=int16(w[at+5]);s.moveDX=int16(w[at+11]);s.moveDY=int16(w[at+12]);s.orbitSideX=w[at+14];s.orbitSideY=w[at+15];if(i==18)s.selectedFrame=w[at+1];
   if(i==13){if(s.renderX!=406 || s.renderY<359 || s.renderY>412 || s.moveDX || s.moveDY!=1 || s.orbitSideX || s.orbitSideY)return false;}
   else if(!rendezvousPhase(s,original,i))return false;
  }
 }
 if(launched){Sprite &probe=expected.sprites[19];probe.renderX=int16(w[19*27+4]);probe.renderY=int16(w[19*27+5]);if(!(probe.renderX==272&&probe.renderY==4) && (probe.renderY!=probe.renderX+56 || !rendezvousPhase(probe,original,18,true)))return false;}
 Common::Array<uint32> baseline;for(const Sprite&s:expected.sprites)p526SpriteWords(s,baseline);return baseline==w;
}
bool AstronomicaEngine::canSaveRendezvous() const {
 if(_place!=514 || !_rendezvousAssetsValid || !_runner.scriptsIdle() || !validRendezvousScene(_scene) || _questionSaveBaseline.size()!=20 || _movie || _movieFrame.w || _pendingImage.w || !_displayedImageName.empty() || _comet.frame<1 || _comet.frame>12 || _comet.previousFrame<0 || _comet.previousFrame>12 || !ConfMan.getBool("astronomica_audio") || !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input"))return false;
 if((_loopSound!=-1&&_loopSound!=0)||(_mixer->isSoundHandleActive(_soundHandle)&&(_lastSound!=_loopSound||!_loopEnabled)))return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 Common::Array<uint32>state,w;if(!_runner.exportPersistentState(state))return false;for(const Sprite&s:_scene.sprites){if(s.dragEnabled||s.planetMotion||s.planetPeriod!=-1)return false;p526SpriteWords(s,w);}Scene original=_scene;original.sprites=_questionSaveBaseline;return validRendezvousSprites(w,original,state,scriptClock());
}
Common::Error AstronomicaEngine::saveRendezvous(Common::WriteStream *stream) {
 if(!canSaveRendezvous())return Common::kWritingFailed;Common::Array<uint32>state,w;_runner.exportPersistentState(state);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);
 const uint32 h[]={514,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame)};
 stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(17);uint32 hash=2166136261U;auto write=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:h)write(v);for(uint32 v:w)write(v);for(uint32 v:state)write(v);stream->writeUint32LE(hash);return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadRendezvous(Common::SeekableReadStream *stream) {
 if(stream->size()-stream->pos()<(10+20*27+605+1)*4 || !ConfMan.getBool("astronomica_audio") || !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 uint32 h[10],hash=2166136261U;auto read=[&](){uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=read();Common::Array<uint32>w,state;w.resize(20*27);state.resize(605);for(uint32&v:w)v=read();for(uint32&v:state)v=read();
 if(stream->readUint32LE()!=hash || stream->err() || h[0]!=514 || (h[3]>537&&h[3]!=0xffffffffU) || (h[4]&&h[4]!=0xffffffffU) || h[5]>1 || h[7]>1 || (h[7]&&(h[4]||!h[5])) || h[8]<1 || h[8]>12 || h[9]>12)return Common::kReadingFailed;
 const Common::Path path=ConfMan.getPath("path").join("PLACES/P514/MEGAFILE.HYP");if(!universeFileIdentity(path,586435,0x97d1b539U))return Common::kReadingFailed;Common::File file;if(!file.open(Common::FSNode(path)))return Common::kReadingFailed;Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!validRendezvousScene(parsed)||!validRendezvousSprites(w,parsed,state,h[2]))return Common::kReadingFailed;
 const uint ids[]={13,16,18,19};const int widths[]={18,52,56,15},heights[]={9,54,56,28};for(uint i=0;i<4;++i){Graphics::Surface*bmp=decodeSpriteBitmap(file,parsed.sprites[ids[i]].frames[0].image,_screen.format);if(!bmp)return Common::kReadingFailed;const bool ok=bmp->w==widths[i]&&bmp->h==heights[i];bmp->free();delete bmp;if(!ok)return Common::kReadingFailed;}
 if(!loadPlace(514,false,true))return Common::kReadingFailed;if(!_runner.importPersistentState(state))error("Validated P514 persistent state could not be installed");_rendezvousAssetsValid=true;_puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_loopSound=int32(h[4]);_loopEnabled=h[5]!=0;_lastSoundAt=h[6];_comet.frame=h[8];_comet.previousFrame=h[9];for(uint i=0;i<20;++i)p526RestoreSprite(_scene.sprites[i],&w[i*27]);redrawSprites();if(h[7])playSound(_loopSound,scriptClock(),true);return Common::kNoError;
}

static bool validProbeSaveState(const Common::Array<uint32> &s) {
 if (!ScriptRunner::validPersistentState(s) || s[300] < 1 || s[300] > 4 || s[303]) return false;
 for (uint i = 0; i < 100; ++i) {
  if (s[3*i+2] != 1 || s[302+3*i] != uint32(i < 2) || s[301+3*i] != (i < 2 ? 8U : 0U)) return false;
  // Global widths are retained metadata; negative widths cannot come from
  // the original declared nonnegative condition widths or initial zero.
  if (s[3*i+1] != 0 && (i >= 3 || s[3*i+1] != 6)) return false;
 }
 return true;
}
static bool validProbeSaveScene(const Scene &s) {
 if (s.mode || s.layers != 1 || s.sprites.size() != 18 || s.conditions.size() != 2 || s.scripts.size() != 11 || !s.movies.empty() || !s.mouseRects.empty()) return false;
 const int expected[2][6] = {{1,0,8,2,1,4},{1,1,8,0,0,8}};
 for (uint i = 0; i < 2; ++i) for (uint j = 0; j < 6; ++j) if (s.conditions[i].raw[j] != expected[i][j]) return false;
 const uint frames[] = {2,2,2,2,2,2,2,2,12,10,10,10,10,2,11,11,1,1};
 for (uint i = 0; i < 18; ++i) if (spriteFrameCount(s,i) != frames[i] || s.sprites[i].clone != (i >= 10 && i <= 12 ? 10 : -1)) return false;
 return true;
}
static bool probeDirection(uint32 dx, uint32 dy, uint32 sx, uint32 sy) {
 return (int32(dx) == 2 && !dy && !sx && !sy) || (int32(dx) == -2 && !dy && !sx && sy == 1) ||
        (!dx && int32(dy) == -1 && sx == 1 && !sy) || (!dx && int32(dy) == 1 && !sx && !sy);
}
static bool validProbeSaveSprites(const Common::Array<uint32> &w,const Scene &original,const Common::Array<uint32> &state,const ProbeMotion &motion,uint32 clock) {
 if (!validProbeSaveScene(original) || !validProbeSaveState(state) || w.size() != 18*27 || motion.year < 1991 || motion.year >= 2003 || motion.flying || motion.expired || motion.specialHit) return false;
 const int widths[] = {54,40,43},heights[] = {52,40,25};
 for (uint i = 0; i < 3; ++i) if (motion.widths[i] != widths[i] || motion.heights[i] != heights[i]) return false;
 Scene expected = original; for (Sprite &s : expected.sprites) s.selectedFrame = 0;
 for (uint i = 4; i < 8; ++i) expected.sprites[i].selectedFrame = state[300] == i-3;
 int year = motion.year; for (int i = 12; i >= 9; --i) { expected.sprites[i].selectedFrame = year%10; year /= 10; }
 expected.sprites[8].selectedFrame = w[8*27+1]; if (w[8*27+1] > 11) return false;
 ProbeMotion initial; for (uint i = 0; i < 3; ++i) { initial.widths[i] = widths[i]; initial.heights[i] = heights[i]; configureProbe(expected,initial,15+i); }
 expected.sprites[14].visible = expected.sprites[15].visible = 1;
 const uint32 moveEpoch = w[14*27+9],frameEpoch = w[14*27+8];
 if (int32(clock-moveEpoch) < 0 || int32(clock-frameEpoch) < 0 || w[14*27+1] > 10 || w[15*27+1] != w[14*27+1]) return false;
 for (uint i = 14; i <= 16; ++i) {
  if (w[i*27+9] != moveEpoch || !probeDirection(w[i*27+11],w[i*27+12],w[i*27+14],w[i*27+15])) return false;
  Sprite &s = expected.sprites[i]; s.moveSince = moveEpoch;
  s.renderX = int16(w[i*27+4]); s.renderY = int16(w[i*27+5]);
  s.moveDX = int16(w[i*27+11]); s.moveDY = int16(w[i*27+12]); s.orbitSideX = w[i*27+14]; s.orbitSideY = w[i*27+15];
  if (i < 16) { if (w[i*27+8] != frameEpoch) return false; s.frameSince = frameEpoch; s.selectedFrame = w[i*27+1]; }
 }
 // A failed flight resets its radii but commits the old computed point. Do
 // not force that hidden point onto the smaller orbit or onto Earth's point.
 const int px = int32(w[16*27+4]),py = int32(w[16*27+5]);
 if (px < 300-226-widths[2]-2 || px > 300+226+2 || py < 140-113-heights[2]-1 || py > 140+113+1) return false;
 Common::Array<uint32> baseline; for (const Sprite &s : expected.sprites) p526SpriteWords(s,baseline);
 if (baseline != w) { for(uint j=0;j<w.size();++j) if(baseline[j]!=w[j]) { debug("Probe baseline mismatch %u %d/%d",j,int32(w[j]),int32(baseline[j]));break; } return false; }
 // Validate all reachable Earth/Mars/calendar phases from the original setup,
 // including Mars's initial x40 approach and the initial unarmed partial year.
 // This is the native callback's finite calendar path, not an audit sample list.
 Scene world = original; for (Sprite &s : world.sprites) s.selectedFrame = 0;
 ProbeMotion m; for (uint i = 0; i < 3; ++i) { m.widths[i] = widths[i]; m.heights[i] = heights[i]; configureProbe(world,m,15+i); }
 world.sprites[14].visible = world.sprites[15].visible = 1; world.sprites[8].selectedFrame = 0;
 for (uint tick = 0; tick <= 20000 && !m.expired; ++tick) {
  bool same = m.year == motion.year && m.yearArmed == motion.yearArmed && world.sprites[8].selectedFrame == int(w[8*27+1]);
  for (uint i = 14; i <= 15; ++i) {
   const Sprite &s = world.sprites[i]; const uint at = i*27;
   same = same && s.renderX == int32(w[at+4]) && s.renderY == int32(w[at+5]) && s.moveDX == int32(w[at+11]) && s.moveDY == int32(w[at+12]) && s.orbitSideX == int32(w[at+14]) && s.orbitSideY == int32(w[at+15]);
  }
  if (same) return true;
  int32 idle = 0; advanceProbe(world,m,14,idle,(tick+1)*30); advanceProbe(world,m,15,idle,(tick+1)*30);
 }
 return false;
}
bool AstronomicaEngine::canSaveProbe() const {
 if (_place != 522 || !_probeAssetsValid || !validProbeSaveScene(_scene) || _questionSaveBaseline.size() != 18 || _movie || _movieFrame.w || _pendingImage.w || !_displayedImageName.empty() ||
     _probe.flying || _probe.expired || _probe.specialHit || _comet.frame < 1 || _comet.frame > 12 || _comet.previousFrame < 0 || _comet.previousFrame > 12 ||
     !ConfMan.getBool("astronomica_audio") || !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 Common::Array<uint32> state,words; uint32 since = 0; if (!_runner.exportProbePollState(state,since) || int32(scriptClock()-since) < 0) return false;
 for (const Sprite &s : _scene.sprites) { if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false; p526SpriteWords(s,words); }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validProbeSaveSprites(words,original,state,_probe,scriptClock());
}
Common::Error AstronomicaEngine::saveProbe(Common::WriteStream *stream) {
 if (!canSaveProbe()) return Common::kWritingFailed;
 Common::Array<uint32> state,words; uint32 since = 0; _runner.exportProbePollState(state,since); for (const Sprite &s : _scene.sprites) p526SpriteWords(s,words);
 const uint32 h[] = {522,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),
  since,uint32(_probe.year),uint32(_probe.yearArmed),uint32(_probe.specialHit),uint32(_probe.flying),uint32(_probe.expired),
  uint32(_probe.widths[0]),uint32(_probe.heights[0]),uint32(_probe.widths[1]),uint32(_probe.heights[1]),uint32(_probe.widths[2]),uint32(_probe.heights[2]),uint32(_comet.frame),uint32(_comet.previousFrame),0,0};
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(16); uint32 hash = 2166136261U;
 auto write = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : h) write(v); for (uint32 v : words) write(v); for (uint32 v : state) write(v); stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadProbe(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (24+18*27+605+1)*4 || !ConfMan.getBool("astronomica_audio") || !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 h[24],hash = 2166136261U; auto read = [&]() { uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : h) v = read(); Common::Array<uint32> words,state; words.resize(18*27); state.resize(605);
 for (uint32 &v : words) v = read(); for (uint32 &v : state) v = read();
 if (stream->readUint32LE() != hash || stream->err() || h[0] != 522 || (h[3] > 537 && h[3] != 0xffffffffU) || (h[4] && h[4] != 0xffffffffU) ||
     h[5] > 1 || h[7] > 1 || (h[7] && (h[4] || !h[5])) || int32(h[2]-h[8]) < 0 || h[10] > 1 || h[11] || h[12] || h[13] ||
     h[20] < 1 || h[20] > 12 || h[21] > 12 || h[22] || h[23]) return Common::kReadingFailed;
 const Common::Path path = ConfMan.getPath("path").join("PLACES/P522/MEGAFILE.HYP");
 if (!universeFileIdentity(path,483379,0x6015e215U)) return Common::kReadingFailed;
 Common::File file; if (!file.open(Common::FSNode(path))) return Common::kReadingFailed; Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validProbeSaveScene(parsed)) return Common::kReadingFailed;
 ProbeMotion motion; motion.year = int32(h[9]); motion.yearArmed = h[10] != 0;
 for (uint i = 0; i < 3; ++i) {
  Graphics::Surface *bmp = decodeSpriteBitmap(file,parsed.sprites[14+i].frames[0].image,_screen.format);
  if (!bmp) return Common::kReadingFailed; const bool match = h[14+i*2] == uint(bmp->w) && h[15+i*2] == uint(bmp->h);
  motion.widths[i] = bmp->w; motion.heights[i] = bmp->h; bmp->free(); delete bmp; if (!match) return Common::kReadingFailed;
 }
 if (!validProbeSaveSprites(words,parsed,state,motion,h[2])) return Common::kReadingFailed;
 // Validate the complete trusted binding against the parsed original program
 // before live mutation. No code, callback address or arbitrary job is imported.
 ScriptRunner prepared = _runner; prepared.clear(); prepared.loadLocalConditions(parsed.conditions); prepared.setPrograms(parsed.scripts,state[601]); prepared.setProbeHandler(this);
 if (!prepared.importProbePollState(state,h[8])) return Common::kReadingFailed;
 if (!loadPlace(522,false,true)) return Common::kReadingFailed;
 if (!_runner.importProbePollState(state,h[8])) error("Validated P522 poll binding could not be installed");
 _probe = motion; _probeAssetsValid = true;
 _puzzlesCompleted = h[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-h[2]; _previousPlace = int32(h[3]);
 _loopSound = int32(h[4]); _loopEnabled = h[5] != 0; _lastSoundAt = h[6]; _comet.frame = h[20]; _comet.previousFrame = h[21];
 for (uint i = 0; i < 18; ++i) p526RestoreSprite(_scene.sprites[i],&words[i*27]); redrawSprites();
 if (h[7]) playSound(_loopSound,scriptClock(),true); return Common::kNoError;
}

bool AstronomicaEngine::canSaveUniverse() const {
 if (_place != 529 || !_universeAssetsValid || !_movie || _moviePlaying || !_runner.scriptsIdle() || _pendingImage.w ||
     !_displayedImageName.empty() || !validUniverseScene(_scene) || _questionSaveBaseline.size() != 11 ||
     _comet.frame < 1 || _comet.frame > 12 || _comet.previousFrame < 0 || _comet.previousFrame > 12 ||
     !ConfMan.getBool("astronomica_audio") || !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 Common::Array<uint32> state,words; if (!_runner.exportPersistentState(state)) return false;
 for (const Sprite &s : _scene.sprites) { if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false; p526SpriteWords(s,words); }
 const bool absent = _moviePresentedFrame == -1;
 if (absent ? _movieFrame.w != 0 : (_movieFrame.w != 320 || _movieFrame.h != 240 || _movieX != 160 || _movieY != 40)) return false;
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validUniverseSprites(words,original,state,_moviePresentedFrame,_movieSegmentStart,_universeSegmentEnd);
}
Common::Error AstronomicaEngine::saveUniverse(Common::WriteStream *stream) {
 if (!canSaveUniverse()) return Common::kWritingFailed;
 const bool absent = _moviePresentedFrame < 0;
 const uint32 header[] = {529,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,
  uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_moviePresentedFrame),absent ? 0U : uint32(_movieX),absent ? 0U : uint32(_movieY),
  _movieSegmentStart,_universeSegmentEnd,uint32(_comet.frame),uint32(_comet.previousFrame),0};
 Common::Array<uint32> state,words; _runner.exportPersistentState(state); for (const Sprite &s : _scene.sprites) p526SpriteWords(s,words);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(15); uint32 hash = 2166136261U;
 auto write = [&](uint32 word) { stream->writeUint32LE(word); hash = (hash ^ word)*16777619U; };
 for (uint32 word : header) write(word); for (uint32 word : words) write(word); for (uint32 word : state) write(word);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadUniverse(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (16+11*27+605+1)*4 || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.getBool("astronomica_animation") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 h[16],hash = 2166136261U; auto read = [&]() { uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : h) v = read(); Common::Array<uint32> words,state; words.resize(11*27); state.resize(605);
 for (uint32 &v : words) v = read(); for (uint32 &v : state) v = read();
 if (stream->readUint32LE() != hash || stream->err() || h[0] != 529 || (h[3] > 537 && h[3] != 0xffffffffU) ||
     (h[4] && h[4] != 0xffffffffU) || h[5] > 1 || h[7] > 1 || (h[7] && (h[4] || !h[5])) ||
     h[13] < 1 || h[13] > 12 || h[14] > 12 || h[15] ||
     (h[8] == 0xffffffffU ? (h[9] || h[10]) : (h[9] != 160 || h[10] != 40))) return Common::kReadingFailed;
 const Common::Path folder = ConfMan.getPath("path").join("PLACES/P529");
 if (!universeFileIdentity(folder.join("MEGAFILE.HYP"),282102,0x7b986895U) ||
     !universeFileIdentity(folder.join("FUNIV.MOV"),1948518,0x7cd17aa3U)) return Common::kReadingFailed;
 Common::File file; if (!file.open(Common::FSNode(folder.join("MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validUniverseSprites(words,parsed,state,int32(h[8]),h[11],h[12])) return Common::kReadingFailed;
 Video::QuickTimeDecoder *prepared = new Video::QuickTimeDecoder(); Common::File *movie = new Common::File();
 if (!movie->open(Common::FSNode(folder.join("FUNIV.MOV")))) { delete movie; delete prepared; return Common::kReadingFailed; }
 if (!prepared->loadStream(movie) || !prepared->isSeekable() || prepared->getFrameCount() != 253 || prepared->getTimeScale() != 30 || prepared->getWidth() != 320 || prepared->getHeight() != 240) { delete prepared; return Common::kReadingFailed; }
 Graphics::Surface residual;
 if (h[8] != 0xffffffffU) {
  if (!prepared->seekToFrame(h[8])) { delete prepared; return Common::kReadingFailed; }
  const Graphics::Surface *decoded = prepared->decodeNextFrame();
  if (!decoded || prepared->getCurFrame() != int(h[8])) { delete prepared; return Common::kReadingFailed; }
  Graphics::Surface *rgb = decoded->convertTo(_screen.format,prepared->getPalette());
  if (!rgb || rgb->w != 320 || rgb->h != 240) { if (rgb) { rgb->free(); delete rgb; } delete prepared; return Common::kReadingFailed; }
  residual.copyFrom(*rgb); rgb->free(); delete rgb;
 }
 // loadPlace parses HYP and renders its embedded background before mutation.
 // As in older formats, host-side TOCTOU I/O changes are outside this guarantee.
 if (!loadPlace(529,false,true)) { residual.free(); delete prepared; return Common::kReadingFailed; }
 delete _movie; _movie = prepared; _movie->setVolume(ConfMan.getBool("astronomica_audio") ? 255 : 0);
 _runner.importPersistentState(state); _puzzlesCompleted = h[1];
 _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-h[2]; _previousPlace = int32(h[3]);
 _loopSound = int32(h[4]); _loopEnabled = h[5] != 0; _lastSoundAt = h[6];
 _moviePresentedFrame = int32(h[8]); _movieX = h[9]; _movieY = h[10]; _movieSegmentStart = h[11]; _universeSegmentEnd = h[12];
 _moviePlaying = false; if (h[12]) _movie->setEndTime(Audio::Timestamp(0,h[12],30));
 _comet.frame = h[13]; _comet.previousFrame = h[14];
 for (uint i = 0; i < 11; ++i) p526RestoreSprite(_scene.sprites[i],&words[i*27]);
 if (residual.w) _movieFrame.copyFrom(residual); residual.free(); redrawSprites();
 if (h[7]) playSound(_loopSound,scriptClock(),true); return Common::kNoError;
}

bool AstronomicaEngine::canSaveRocket() const {
 if (_place != 537 || _comet.frame < 1 || _comet.frame > 12 || _comet.previousFrame < 0 || _comet.previousFrame > 12 || !_runner.scriptsIdle() || _rocket.kind != RocketMotion::kStopped || _pendingImage.w || !_displayedImageName.empty() || _movie ||
     !validRocketScene(_scene) || _questionSaveBaseline.size() != 48 ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") || !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites; if (!_runner.exportPersistentState(state)) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) { if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false; p526SpriteWords(s,sprites); }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validRocketSprites(sprites,original,state,_rocket.delta,_rocket.since);
}
Common::Error AstronomicaEngine::saveRocket(Common::WriteStream *stream) {
 if (!canSaveRocket()) return Common::kWritingFailed;
 const uint32 header[] = {537,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,
  uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_rocket.delta),_rocket.since,uint32(_comet.frame),uint32(_comet.previousFrame),0,0,0,0};
 Common::Array<uint32> state,sprites; _runner.exportPersistentState(state); for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(14); uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v); for (uint32 v : sprites) word(v); for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadRocket(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kRocketWords+1)*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") || !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[16],hash = 2166136261U; auto word = [&]() { uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word(); Common::Array<uint32> sprites,state; sprites.resize(48*27); state.resize(ScriptRunner::kPersistentStateWords);
 for (uint32 &v : sprites) v = word(); for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validRocketState(state) || header[0] != 537 || (header[3] > 537 && header[3] != 0xffffffffU) ||
     (header[4] != 0 && header[4] != 0xffffffffU) || header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) ||
     header[10] < 1 || header[10] > 12 || header[11] > 12 || header[12] || header[13] || header[14] || header[15]) return Common::kReadingFailed;
 Common::File file; if (!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P537/MEGAFILE.HYP")))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file); if (!reader.read(parsed) || !validRocketSprites(sprites,parsed,state,header[8],header[9])) return Common::kReadingFailed;
 if (!loadPlace(537,false,true)) return Common::kReadingFailed;
 _runner.importPersistentState(state); _rocket.kind = RocketMotion::kStopped; _rocket.delta = header[8]; _rocket.since = header[9];
 _comet.frame = header[10]; _comet.previousFrame = header[11]; _puzzlesCompleted = header[1];
 _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2]; _previousPlace = int32(header[3]);
 _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 48; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]); redrawSprites();
 if (header[7]) playSound(_loopSound,scriptClock(),true); return Common::kNoError;
}

bool AstronomicaEngine::canSaveBuilder() const {
 if (_comet.frame < 1 || _comet.frame > 12 || _comet.previousFrame < 0 || _comet.previousFrame > 12) return false;
 if (!builderScene(_place) || !_runner.scriptsIdle() || _pendingImage.w || _movie || !validBuilderScene(_scene) || _questionSaveBaseline.size() != 60 || !_builderHistoryValid ||
     !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites;
 if (!_runner.exportPersistentState(state) || !validBuilderState(state) || builderImageId(_displayedImageName) < 0) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validBuilderSprites(sprites,original);
}
Common::Error AstronomicaEngine::saveBuilder(Common::WriteStream *stream) {
 if (!canSaveBuilder()) return Common::kWritingFailed;
 const uint32 header[] = {uint32(_place),_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(builderImageId(_displayedImageName)),uint32(_comet.frame),uint32(_comet.previousFrame),0};
 Common::Array<uint32> state,sprites; _runner.exportPersistentState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(13);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadBuilder(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < (kBuilderWords+1)*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 Common::Array<uint32> sprites,state; sprites.resize(60*27); state.resize(ScriptRunner::kPersistentStateWords);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validBuilderState(state) || !builderScene(header[0]) ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] > 2 || header[9] < 1 || header[9] > 12 || header[10] > 12 || header[11]) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::String::format("PLACES/P%u/MEGAFILE.HYP",header[0]))))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validBuilderSprites(sprites,parsed)) return Common::kReadingFailed;
 const Common::String name = header[8] == 1 ? "drydock" : header[8] == 2 ? "pad" : "";
 Graphics::Surface *picture = header[8] ? openBackgroundImage(name,header[0]) : nullptr;
 if (header[8] && (!picture || picture->w != 250 || picture->h != 330)) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 if (!loadPlace(header[0],false,true)) { if (picture) { picture->free(); delete picture; } return Common::kReadingFailed; }
 _runner.importPersistentState(state);
 _comet.frame = header[9]; _comet.previousFrame = header[10];
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < 60; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 if (picture) {
  _pendingImage.copyFrom(*picture); _pendingImageName = name; _pendingImageX = 0; _pendingImageY = 0;
  picture->free(); delete picture; displayBackgroundImage();
 } else redrawSprites();
 if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
bool AstronomicaEngine::canSaveVariant() const {
 const VariantSaveProfile *p = variantProfile(_place);
 if (!p || !_runner.variantIdle() || _pendingImage.w || !_displayedImageName.empty() || _movie || !validVariantScene(_scene,*p) ||
     _questionSaveBaseline.size() != p->sprites || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return false;
 if ((_loopSound != -1 && _loopSound != 0) || (_mixer->isSoundHandleActive(_soundHandle) && (_lastSound != _loopSound || !_loopEnabled))) return false;
 Common::Array<uint32> state,sprites;
 if (!_runner.exportVariantState(state) || !validVariantValues(state,*p)) return false;
 for (const HoverTarget &h : _hoverSprites) if (h.entered) return false;
 for (const HoverTarget &h : _hoverRects) if (h.entered) return false;
 for (const Sprite &s : _scene.sprites) {
  if (s.dragEnabled || s.planetMotion || s.planetPeriod != -1) return false;
  p526SpriteWords(s,sprites);
 }
 Scene original = _scene; original.sprites = _questionSaveBaseline;
 return validVariantSprites(sprites,original,*p);
}
Common::Error AstronomicaEngine::saveVariant(Common::WriteStream *stream) {
 if (!canSaveVariant()) return Common::kWritingFailed;
 const uint32 header[] = {uint32(_place),_puzzlesCompleted,scriptClock(),uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),
  _lastSoundAt,uint32(_mixer->isSoundHandleActive(_soundHandle)),0,0,0,0};
 Common::Array<uint32> state,sprites; _runner.exportVariantState(state);
 for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(10);
 uint32 hash = 2166136261U;
 auto word = [&](uint32 v) { stream->writeUint32LE(v); hash = (hash ^ v)*16777619U; };
 for (uint32 v : header) word(v);
 for (uint32 v : sprites) word(v);
 for (uint32 v : state) word(v);
 stream->writeUint32LE(hash); return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadVariant(Common::SeekableReadStream *stream) {
 if (stream->size()-stream->pos() < 12*4 || !ConfMan.hasKey("astronomica_audio") || !ConfMan.getBool("astronomica_audio") ||
     !ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") ||
     !ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return Common::kReadingFailed;
 uint32 header[12],hash = 2166136261U;
 auto word = [&]() { const uint32 v = stream->readUint32LE(); hash = (hash ^ v)*16777619U; return v; };
 for (uint32 &v : header) v = word();
 const VariantSaveProfile *p = variantProfile(header[0]);
 if (!p || stream->size()-stream->pos() < (p->sprites*27+ScriptRunner::kIdleStateWords+3)*4 ||
     (header[3] > 537 && header[3] != 0xffffffffU) || (header[4] != 0 && header[4] != 0xffffffffU) ||
     header[5] > 1 || header[7] > 1 || (header[7] && (header[4] != 0 || !header[5])) || header[8] || header[9] || header[10] || header[11]) return Common::kReadingFailed;
 Common::Array<uint32> sprites,state; sprites.resize(p->sprites*27); state.resize(ScriptRunner::kIdleStateWords+2);
 for (uint32 &v : sprites) v = word();
 for (uint32 &v : state) v = word();
 if (stream->readUint32LE() != hash || stream->err() || !validVariantValues(state,*p)) return Common::kReadingFailed;
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%u/MEGAFILE.HYP",p->place)))))) return Common::kReadingFailed;
 Scene parsed; ResourceReader reader(file);
 if (!reader.read(parsed) || !validVariantSprites(sprites,parsed,*p)) return Common::kReadingFailed;
 for (int id : {912,922}) {
  Audio::SeekableAudioStream *voice = openSound(id); if (!voice) return Common::kReadingFailed; delete voice;
 }
 if (!loadPlace(p->place,false,true)) return Common::kReadingFailed;
 if (!_runner.importVariantState(state)) return Common::kReadingFailed;
 _puzzlesCompleted = header[1]; _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-header[2];
 _previousPlace = int32(header[3]); _loopSound = int32(header[4]); _loopEnabled = header[5] != 0; _lastSoundAt = header[6];
 for (uint i = 0; i < p->sprites; ++i) p526RestoreSprite(_scene.sprites[i],&sprites[i*27]);
 redrawSprites(); if (header[7]) playSound(_loopSound,scriptClock(),true);
 return Common::kNoError;
}
void AstronomicaEngine::pauseEngineIntern(bool pause) {
 Engine::pauseEngineIntern(pause);
 if (pause != _clockPaused) {
  if (pause) _pauseStarted = _system->getMillis();
  else _pausedMillis += _system->getMillis()-_pauseStarted;
  _clockPaused = pause;
  if (_movie) _movie->pauseVideo(pause);
 }
}
bool AstronomicaEngine::canSaveGameStateCurrently(Common::U32String *msg) {
 const bool enabled = canSaveP510() || canSaveP501() || canSaveP504() || canSaveP503() || canSaveP502() || canSaveP527() || canSaveP516() || canSaveP511() || canSaveP509() || canSaveP521() || canSavePlanets() || canSaveRendezvous() || canSaveProbe() || canSaveUniverse() || canSaveRocket() || canSaveQuestion() || canSaveBuilder() || canSaveP517() || canSaveP513() || canSaveP519() || canSaveP524() || canSaveP526() || canSaveP528() || canSaveP530() || canSaveVariant() || (_place > 1 && _scene.mode == 1 && !_runner.variantRound() && !_runner.clicksBlocked() && !_runner.pendingCount());
 if (!enabled && msg) *msg = Common::U32String("Save after the current action finishes, in a supported exploration or puzzle screen.");
 return enabled;
}
bool AstronomicaEngine::canLoadGameStateCurrently(Common::U32String *msg) {
 const bool enabled = _screen.w && !_runner.clicksBlocked();
 if (!enabled && msg) *msg = Common::U32String("Wait for the current action to finish.");
 return enabled;
}
Common::Error AstronomicaEngine::saveGameStream(Common::WriteStream *stream, bool) {
 if (!canSaveGameStateCurrently()) return Common::kWritingFailed;
 if (questionProfile(_place)) return saveQuestion(stream);
 if (_place == 519) return saveP519(stream);
 if (_place == 524) return saveP524(stream);
 if (_place == 526) return saveP526(stream);
 if (_place == 528) return saveP528(stream);
 if (_place == 530) return saveP530(stream);
 if (_place == 537) return saveRocket(stream);
 if (_place == 510) return saveP510(stream);
 if (_place == 501) return saveP501(stream);
 if (_place == 504) return saveP504(stream);
 if (_place == 503) return saveP503(stream);
 if (_place == 502) return saveP502(stream);
 if (_place == 527) return saveP527(stream);
 if (_place == 516) return saveP516(stream);
 if (_place == 511) return saveP511(stream);
 if (_place == 509) return saveP509(stream);
 if (_place == 521) return saveP521(stream);
 if (_place == 518) return savePlanets(stream);
 if (_place == 514) return saveRendezvous(stream);
 if (_place == 522) return saveProbe(stream);
 if (_place == 529) return saveUniverse(stream);
 if (builderScene(_place)) return saveBuilder(stream);
 if (_place == 517) return saveP517(stream);
 if (_place == 513) return saveP513(stream);
 if (variantProfile(_place)) return saveVariant(stream);
 uint32 words[103]; words[102] = scriptClock(); words[0] = _place; words[1] = _puzzlesCompleted;
 for (int i = 0; i < 100; ++i) {
  int32 value = 0; if (!_runner.getValue(0,i,value)) return Common::kWritingFailed;
  words[i+2] = uint32(value);
 }
 // Original gamestat payload: place, completion count and 100 DWORD globals.
 // Native saves add a version and integrity check; ScummVM appends metadata.
 stream->writeUint32BE(MKTAG('A','S','V','M')); stream->writeUint32LE(2);
 uint32 hash = 2166136261U;
 for (uint32 word : words) { stream->writeUint32LE(word); hash = (hash ^ word)*16777619U; }
 stream->writeUint32LE(hash);
 return stream->err() ? Common::kWritingFailed : Common::kNoError;
}
Common::Error AstronomicaEngine::loadGameStream(Common::SeekableReadStream *stream) {
 if (!canLoadGameStateCurrently() || stream->size()-stream->pos() < 420) return Common::kReadingFailed;
 if (stream->readUint32BE() != MKTAG('A','S','V','M')) return Common::kReadingFailed;
 const uint32 version = stream->readUint32LE();
 if (version == 3 || version == 4) return loadQuestion(stream,version);
 if (version == 5) return loadP519(stream);
 if (version == 6) return loadP524(stream);
 if (version == 7) return loadP526(stream);
 if (version == 8) return loadP528(stream);
 if (version == 9) return loadP530(stream);
 if (version == 10) return loadVariant(stream);
 if (version == 14) return loadRocket(stream);
 if (version == 28) return loadP510(stream);
 if (version == 27) return loadP501(stream);
 if (version == 26) return loadP504(stream);
 if (version == 25) return loadP503(stream);
 if (version == 24) return loadP502(stream);
 if (version == 23) return loadP527(stream);
 if (version == 22) return loadP516(stream);
 if (version == 21) return loadP511(stream);
 if (version == 20) return loadP509(stream);
 if (version == 19) return loadP521(stream);
 if (version == 18) return loadPlanets(stream);
 if (version == 17) return loadRendezvous(stream);
 if (version == 16) return loadProbe(stream);
 if (version == 15) return loadUniverse(stream);
 if (version == 13) return loadBuilder(stream);
 if (version == 12) return loadP517(stream);
 if (version == 11) return loadP513(stream);
 if ((version != 1 && version != 2) || (version == 2 && stream->size()-stream->pos() < 416)) return Common::kReadingFailed;
 uint32 words[103] = {},hash = 2166136261U;
 for (uint i = 0; i < (version == 2 ? 103U : 102U); ++i) { words[i] = stream->readUint32LE(); hash = (hash ^ words[i])*16777619U; }
 // Version 1 never implemented the countdown and has no clock epoch.
 if (version == 1 && words[10] && (words[62] == 1 || words[62] == 2)) return Common::kReadingFailed;
 if (stream->readUint32LE() != hash || stream->err() || words[0] <= 1 || words[0] > 537) return Common::kReadingFailed;
 // Reject unsupported destinations before changing any live state.
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%u/MEGAFILE.HYP",words[0])));
 if (!file.open(Common::FSNode(path))) return Common::kReadingFailed;
 Scene destination; ResourceReader reader(file);
 if (!reader.read(destination) || destination.mode != 1) return Common::kReadingFailed;
 const ScriptRunner oldRunner = _runner;
 const uint oldCompleted = _puzzlesCompleted;
 const uint32 oldPausedMillis = _pausedMillis;
 // Restore the entire logical epoch, preserving the original nonzero clock
 // sentinel and unsigned wraparound. Time outside the game is not elapsed.
 if (version == 2) _pausedMillis = (_clockPaused ? _pauseStarted : _system->getMillis())-words[102];
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,int32(words[i+2]));
 _runner.resetVariantSequence();
 _puzzlesCompleted = words[1];
 if (!loadPlace(words[0])) { _runner = oldRunner; _puzzlesCompleted = oldCompleted; _pausedMillis = oldPausedMillis; return Common::kReadingFailed; }
 return Common::kNoError;
}
bool AstronomicaEngine::validateLegacyDestination(const LegacySaveState &state) const {
 const uint place = state.place;
 if (!((place >= 27 && place <= 422) || (place > 437 && place <= 537)) || state.hasUnknownClock()) return false;
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%u/MEGAFILE.HYP",place)));
 if (!Common::FSNode(path).exists() || !file.open(Common::FSNode(path))) return false;
 Scene destination; ResourceReader reader(file);
 return reader.read(destination) && destination.mode == 1;
}
void AstronomicaEngine::prepareLegacyResume() {
 if (_legacyChecked) return; _legacyChecked = true; _legacyAvailable = false;
 // The port reads only the selected game's directory, never a drive-root or
 // process working-directory fallback. No original save is modified.
 LegacySaveState candidate;
 const LegacyFileResult result = readLegacyDirectory(Common::FSNode(ConfMan.getPath("path")),candidate);
 if (result == kLegacyLoaded && validateLegacyDestination(candidate)) {
  _legacyState = candidate; _legacyAvailable = true;
 } else if (result != kLegacyMissing) warning("Astronomica: original GAMESTAT is invalid or cannot be restored without missing scene/clock state");
}
bool AstronomicaEngine::restoreLegacyState(const LegacySaveState &state) {
 if (!validateLegacyDestination(state)) return false;
 const ScriptRunner oldRunner = _runner; const uint oldCompleted = _puzzlesCompleted;
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,state.globals[i]);
 _runner.resetVariantSequence(); _puzzlesCompleted = state.completed;
 if (!loadPlace(state.place)) { _runner = oldRunner; _puzzlesCompleted = oldCompleted; return false; }
 return true;
}
AstronomicaEngine::~AstronomicaEngine() {
 closeMovie(); _pendingImage.free(); _mixer->stopHandle(_soundHandle);
}
void AstronomicaEngine::closeMovie() {
 if (_moviePlaying) debug("Astronomica movie closed while playing: %u frames, time %u, end %u",_movieFramesDrawn,_movie->getTime(),_movie->getEndTime().msecs());
 delete _movie; _movie = nullptr; _moviePlaying = false; _worldMovieCursorBottom = -1;
 _movieSegmentStart = 0; _universeSegmentEnd = 0; _universeAssetsValid = false; _plotEvent = 0; _plotTime = 0;
 _dangerEvent[0] = _dangerEvent[1] = 0; _dangerButtons = 0;
 _movieFrame.free(); _moviePresentedFrame = -1;
}
void AstronomicaEngine::configureMovie() {
 Common::Array<uint32> durations;
 // _load_place 9:2651-266f redirects P520's shared movie to P408.
 // P527 uses its ordinary per-scene directory (9:25fa-260f).
 const bool mentors = _place == 408 && _scene.layers == 1 && _scene.sprites.size() == 7;
 const bool advice = _place == 409 && _scene.layers == 1 && _scene.sprites.size() == 3;
 const bool shared = (_place == 520 || mentors || advice) && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("mentors.mov");
 const bool world29 = _place == 29 && _scene.mode == 1 && _scene.layers == 1 && _scene.sprites.size() == 3 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("FLAT29.MOV");
 const bool worldPanel = _scene.mode == 1 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("MOV") &&
  ((_place == 82 && _scene.layers == 1 && _scene.sprites.size() == 1) ||
   (_place == 222 && _scene.layers == 1 && _scene.sprites.size() == 2) ||
   (_place == 231 && _scene.layers == 0 && _scene.sprites.empty()));
 const bool world = world29 || worldPanel;
 const bool rings = _place == 527 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("flatring.mov");
 const bool solar = _place == 525 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("fsun.mov");
 const bool universe = _place == 529 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("funiv.mov");
 const bool weather = _place == 512 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("flatphen.mov");
 const bool plot = _place == 510 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("flatplot.mov") && _scene.layers == 1 && _scene.sprites.size() == 14;
 const bool danger = _place == 523 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("dangers.mov") && _scene.layers == 1 && _scene.sprites.size() == 44;
 const char *transitionMovie = _place == 426 ? "F23B.MOV" : _place == 427 ? "END_BOOM.MOV" :
  _place == 428 ? "F23A.MOV" : _place == 429 ? "F21G.MOV" :
  _place == 423 ? "F24.MOV" : _place == 424 ? "FFATE_1.MOV" :
  _place == 435 ? "FFATE_2.MOV" : _place == 436 ? "FFATE_3.MOV" : _place == 437 ? "FFATE_4.MOV" :
  _place == 2 ? "FLATOPEN.MOV" : _place == 4 ? "FLATOPN2.MOV" : _place == 0 ? "HQLOGO.MOV" : _place == 432 ? "RMC2.MOV" : _place == 433 ? "FX.MOV" : nullptr;
 const bool interlude = transitionMovie && ((_scene.layers == 0 && _scene.sprites.empty()) ||
  (_place == 433 && _scene.layers == 1 && _scene.sprites.size() == 2)) &&
  _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase(transitionMovie);
 if (world || shared || rings || solar || universe || weather || plot || danger || interlude) {
  Common::File *file = new Common::File();
  const Common::Path path = ConfMan.getPath("path").join(Common::Path(world ? Common::String::format("PLACES/P%d/%s",_place,world29 ? "FLAT29.MOV" : "MOV") : interlude ? Common::String::format("PLACES/P%d/%s",_place == 4 ? 2 : _place,transitionMovie) : danger ? "PLACES/P523/DANGERS.MOV" : plot ? "PLACES/P510/FLATPLOT.MOV" : shared ? "PLACES/P408/MENTORS.MOV" : solar ? "PLACES/P525/FSUN.MOV" : universe ? "PLACES/P529/FUNIV.MOV" : weather ? "PLACES/P512/FLATPHEN.MOV" : "PLACES/P527/FLATRING.MOV"));
  if (file->open(Common::FSNode(path))) {
   _movie = new Video::QuickTimeDecoder();
   if (_movie->loadStream(file) && _movie->isSeekable() && _movie->getWidth() <= 640 && _movie->getHeight() <= 480) {
    durations.push_back(_movie->getDuration().totalNumberOfFrames());
    // P523 starts playback before custom5 selects the first active segment.
    if (world || danger || interlude) _movie->setEndTime(_movie->getDuration());
    _movie->setVolume(ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio") ? 255 : 0);
    debug("Astronomica P%d movie: %ux%u, scale %u, duration %u",_place,_movie->getWidth(),_movie->getHeight(),_movie->getTimeScale(),durations[0]);
   } else closeMovie();
  } else delete file;
 }
 // Original P2 command50 changes a Win16 display palette. Both intro
 // movies are Cinepak RGB24, so native RGB rendering already keeps their
 // full colors. Admit this adaptation only with the original BMP present.
 bool nativePalette = false;
 if (_place == 2 && _movie && _movie->getPixelFormat().bytesPerPixel > 1 && _screen.format.bytesPerPixel > 1) {
  Graphics::Surface *palette = openBackgroundImage("OPEN2_B");
  if (palette) { nativePalette = true; palette->free(); delete palette; }
 }
 _runner.setNativePaletteSupport(nativePalette);
 _runner.setMovieTargets(durations);
 if (_place == 529) _universeAssetsValid = _movie && universeFileIdentity(ConfMan.getPath("path").join("PLACES/P529/MEGAFILE.HYP"),282102,0x7b986895U) && universeFileIdentity(ConfMan.getPath("path").join("PLACES/P529/FUNIV.MOV"),1948518,0x7cd17aa3U);
 _runner.setWorldMovieSupport(world && _movie && !durations.empty());
 _runner.setAdviceSupport(advice && shared && _movie && _movie->getTimeScale() == 30 && !durations.empty() && durations[0] >= 17536,_previousPlace);
 _runner.setMentorSupport(mentors && shared && _movie && _movie->getTimeScale() == 30 && !durations.empty() && durations[0] >= 67119,_previousPlace);
 _runner.setDangerSupport(danger && _movie && _movie->getTimeScale() == 30 && !durations.empty() && durations[0] >= 5681);
 _runner.setPlotSupport(plot && _movie && _movie->getTimeScale() == 30 && !durations.empty() && durations[0] >= 11340);
 _runner.setWeatherSupport(weather && _movie && !durations.empty() && _scene.layers == 1 && _scene.sprites.size() == 64);
}
void AstronomicaEngine::updateMovie() {
 if (!_movie || !_moviePlaying) return;
 if (_place == 523) {
  // Dispatch the earliest due slot first. Recompute after each callback:
  // it can replace either slot, seek the movie, stop it or change scene.
  for (int pass = 0; pass < 4 && _place == 523 && _moviePlaying; ++pass) {
   int slot = -1;
   for (int i = 0; i < 2; ++i)
    if (_dangerEvent[i] && uint64(_movie->getTime())*30 >= uint64(_dangerTime[i])*1000 &&
        (slot < 0 || _dangerTime[i] < _dangerTime[slot])) slot = i;
   if (slot < 0) break;
   const int event = _dangerEvent[slot]; _dangerEvent[slot] = 0; runDangerEvent(event);
  }
  if (!_movie || !_moviePlaying) return;
 }
 if (_place == 510 && _plotEvent && uint64(_movie->getTime()) * 30 >= uint64(_plotTime) * 1000) {
  const int event = _plotEvent; _plotEvent = 0;
  int32 choice = 0; _runner.getValue(1,4,choice);
  applyPlotStep(plotCallback(event,choice));
  if (!_movie || !_moviePlaying) return;
 }
 if (_movie->endOfVideo() || _movie->getTime() >= uint32(_movie->getEndTime().msecs())) { debug("Astronomica movie segment finished: %u frames drawn",_movieFramesDrawn); _movie->stop(); _moviePlaying = false; return; }
 if (!_movie->needsUpdate()) return;
 const Graphics::Surface *frame = _movie->decodeNextFrame();
 if (!frame) return;
 Graphics::Surface *rgb = frame->convertTo(_screen.format, _movie->getPalette());
 if (!rgb) return;
 _movieFrame.copyFrom(*rgb);
 _moviePresentedFrame = _movie->getCurFrame();
 rgb->free(); delete rgb; ++_movieFramesDrawn; presentScene();
}

void AstronomicaEngine::applyDangerStep(const DangerStep &step) {
 if (_place != 523 || !_movie) return;
 for (const DangerAction &a : step.actions) {
  switch (a.op) {
  case kDangerRange: {
   const bool playing = _moviePlaying;
   _movie->stop(); _moviePlaying = false; _movieFramesDrawn = 0; _movieSegmentStart = a.a;
   _movie->setEndTime(Audio::Timestamp(0,a.a+a.b,30));
   if (!_movie->seek(Audio::Timestamp(0,a.a,30))) { warning("Astronomica P523 seek failed"); return; }
   if (playing) { _movie->start(); _moviePlaying = true; }
   break;
  }
  case kDangerCallback: _dangerEvent[a.a] = a.b; _dangerTime[a.a] = a.c; break;
  case kDangerShow: _scene.sprites[a.a-1].visible = 1; break;
  case kDangerHide: _scene.sprites[a.a-1].visible = 0; break;
  case kDangerHideAll: for (int id = 9; id <= 37; ++id) _scene.sprites[id-1].visible = 0; break;
  case kDangerPlay: _movie->start(); _moviePlaying = true; break;
  case kDangerStop: _movie->stop(); _moviePlaying = false; break;
  case kDangerSuccess: onPuzzleSuccess(scriptClock()); break;
  }
 }
 if (step.destination) {
  if (step.destination == 524) _runner.defineValue(0,39,1);
  if (!changePlace(step.destination)) warning("Astronomica: cannot leave P523");
 } else redrawSprites();
}
void AstronomicaEngine::runDangerEvent(int event) {
 int32 solved = 0; _runner.getValue(0,39,solved);
 const DangerStep step = dangerCallback(event,_dangerChannels,_dangerButtons,solved != 0);
 applyDangerStep(step);
 _dangerButtons = 0;
}
void AstronomicaEngine::dangerCustom(int operation, int mode) {
 if (operation == 20) { for (int &value : _dangerChannels) value = 33; return; }
 if (operation == 4) { _dangerButtons |= mode ? 2 : 1; return; }
 if (operation == 1) {
  dangerAdjust(_dangerChannels,mode);
  const int xs[] = {121,244,362};
  for (int i = 0; i < 3; ++i) {
   _scene.sprites[i+1].renderX = xs[i];
   _scene.sprites[i+1].renderY = dangerControlY(_dangerChannels[i]);
  }
  redrawSprites(); return;
 }
 if (operation == 5) {
  DangerStep step;
  step.actions.push_back({kDangerRange,0,602});
  step.actions.push_back({kDangerCallback,0,1,600}); step.actions.push_back({kDangerCallback,1,13,510});
  for (int id : {5,6,1}) step.actions.push_back({kDangerHide,id});
  for (int id : {7,11,18}) step.actions.push_back({kDangerShow,id});
  applyDangerStep(step);
 }
}

void AstronomicaEngine::applyPlotStep(const PlotStep &step) {
 if (_place != 510 || !_movie) return;
 if (step.leave) {
  _plotEvent = 0;
  if (step.success) {
   int32 solved = 0; _runner.getValue(0,26,solved);
   if (!solved) onPuzzleSuccess(scriptClock());
   _runner.defineValue(0,26,1);
  }
  if (!changePlace(136)) warning("Astronomica: cannot leave P510");
  return;
 }
 if (step.x >= 0) {
  Sprite &marker = _scene.sprites[1];
  marker.renderX = step.x; marker.renderY = step.y;
 }
 if (step.start >= 0) {
  _movie->stop(); _moviePlaying = false;
  _movieSegmentStart = step.start; _movieFramesDrawn = 0;
  _movie->setEndTime(Audio::Timestamp(0,step.start+step.duration,30));
  if (!_movie->seek(Audio::Timestamp(0,step.start,30))) {
   warning("Astronomica: P510 movie seek failed"); _plotEvent = 0; return;
  }
  _plotEvent = step.event; _plotTime = step.time;
 }
 if (step.play) { _movie->start(); _moviePlaying = true; }
 redrawSprites();
}

static uint32 screenRGBHash(const Graphics::Surface &surface, int height = 456) {
 uint32 hash = 2166136261U;
 for (int y = 0; y < MIN(height,int(surface.h)); ++y) for (int x = 0; x < surface.w; ++x) {
  byte r,g,b; surface.format.colorToRGB(surface.getPixel(x,y),r,g,b);
  hash = (hash ^ r) * 16777619U; hash = (hash ^ g) * 16777619U; hash = (hash ^ b) * 16777619U;
 }
 return hash;
}
static Graphics::Surface *decodeSpriteBitmap(Common::SeekableReadStream &stream, const BitmapRef &ref, const Graphics::PixelFormat &format) {
 if (!ref.size || ref.size > 16 * 1024 * 1024 || uint64(ref.offset) + ref.size > uint64(stream.size())) return nullptr;
 if (ref.size >= 62 && stream.seek(ref.offset + 28) && stream.readUint16LE() == 1) {
  // ScummVM's generic BMP decoder in this build rejects 1-bit images.
  // Original masks use BITMAPINFOHEADER, a two-entry BGR palette and
  // MSB-first packed rows padded to four-byte boundaries.
  stream.seek(ref.offset + 10); const uint32 pixels = stream.readUint32LE();
  const uint32 headerSize = stream.readUint32LE();
  const int32 width = stream.readSint32LE(), height = stream.readSint32LE();
  const uint16 planes = stream.readUint16LE(), bits = stream.readUint16LE();
  const uint32 compression = stream.readUint32LE();
  if (headerSize != 40 || width <= 0 || width > 640 || !height || height < -480 || height > 480 || planes != 1 || bits != 1 || compression != 0 || pixels < 62) return nullptr;
  const uint32 rows = height < 0 ? -height : height, stride = ((width + 31) / 32) * 4;
  if (uint64(pixels) + uint64(rows) * stride > ref.size) return nullptr;
  stream.seek(ref.offset + 54);
  uint32 palette[2];
  for (int i = 0; i < 2; ++i) {
   const uint32 bgr = stream.readUint32LE();
   palette[i] = format.RGBToColor((bgr >> 16) & 255, (bgr >> 8) & 255, bgr & 255);
  }
  Graphics::Surface *mono = new Graphics::Surface(); mono->create(width, rows, format);
  stream.seek(ref.offset + pixels);
  byte packed[80];
  for (uint32 row = 0; row < rows; ++row) {
   if (stream.read(packed, stride) != stride) { mono->free(); delete mono; return nullptr; }
   const uint32 y = height < 0 ? row : rows - row - 1;
   for (int x = 0; x < width; ++x) mono->setPixel(x, y, palette[(packed[x / 8] >> (7 - x % 8)) & 1]);
  }
  return mono;
 }
 if (!stream.seek(ref.offset)) return nullptr;
 Common::SeekableReadStream *data = stream.readStream(ref.size);
 if (!data) return nullptr;
 Image::BitmapDecoder decoder;
 const bool ok = decoder.loadStream(*data); delete data;
 if (!ok || !decoder.getSurface() || decoder.getSurface()->w > 640 || decoder.getSurface()->h > 480) return nullptr;
 return decoder.getSurface()->convertTo(format, decoder.getPalette().data(), decoder.getPalette().size());
}
uint AstronomicaEngine::renderStaticSprites(Common::SeekableReadStream &stream, const Scene &scene, Graphics::Surface &target) {
 // SpriteWorld appends layers and sprites; draw in that same order.
 if (!supportsSpriteLayers(scene)) return 0;
 uint drawn = 0;
 for (int layer = 1; layer <= scene.layers; ++layer)
 for (uint i = 0; i < scene.sprites.size(); ++i) {
  const Sprite &s = scene.sprites[i];
  const Frame *frame = staticSpriteFrame(scene, i);
  if (!s.visible || s.layer != layer || !frame) continue;
  Graphics::Surface *src = decodeSpriteBitmap(stream, frame->image, target.format);
  Graphics::Surface *mask = decodeSpriteBitmap(stream, frame->mask, target.format);
  if (src && mask && (supportsComet(scene,502) || supportsComet(scene,503) || supportsComet(scene,504) || supportsJupiter(scene))) {
   // _SWUpdateSpriteWorld 6:06f4-0723 clips rectangle.bottom to moveBounds.bottom.
   const int height = MAX(0,MIN(int(src->h),int(int16(s.rect[1]))-s.renderY));
   src->h = height; mask->h = MIN(int(mask->h),height);
  }
  if (src && mask && compositeSprite(target, *src, *mask, s.renderX, s.renderY)) ++drawn;
  if (src) { src->free(); delete src; }
  if (mask) { mask->free(); delete mask; }
 }
 return drawn;
}
// Background renderer for the experimental resource explorer.
bool AstronomicaEngine::readImage(Common::SeekableReadStream &s, Graphics::Surface &target, bool control) {
 if (s.size() - s.pos() < 4) return false;
 const uint32 present = s.readUint32LE();
 if (!present) return true;
 if (present != 1 || s.size() - s.pos() < 4) return false;
 const uint32 embedded = s.readUint32LE();
 if (embedded != 1 || s.size() - s.pos() < 4) return false;
 const uint32 size = s.readUint32LE();
 if (size < 54 || size > uint64(s.size() - s.pos()) || size > 16 * 1024 * 1024) return false;
 Common::SeekableReadStream *bmp = s.readStream(size);
 if (!bmp) return false;
 Image::BitmapDecoder decoder;
 bool ok = decoder.loadStream(*bmp);
 delete bmp;
 if (!ok || !decoder.getSurface()) return false;
 const Graphics::Surface *src = decoder.getSurface();
 if (src->w > 640 || src->h > 480) return false;
 Graphics::Surface *rgb = src->convertTo(target.format, decoder.getPalette().data(), decoder.getPalette().size());
 if (!rgb) return false;
 const int y = control ? 480 - rgb->h : 0;
 for (int row = 0; row < rgb->h; ++row)
  memcpy(target.getBasePtr(0, y + row), rgb->getBasePtr(0, row), rgb->w * rgb->format.bytesPerPixel);
 rgb->free();
 delete rgb;
 return true;
}

bool AstronomicaEngine::changePlace(int place) {
 int32 globals[100] = {};
 for (int i = 0; i < 100; ++i) _runner.getValue(0,i,globals[i]);
 const PlaceTransition transition = resolvePlaceTransition(_place,place,globals);
 _runner.defineValue(0,57,transition.permit);
 const bool audio = ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio");
 // Denial voice starts before reloading the old scene in _do_place. Preserve
 // that foreground sound while the scene loader replaces its other state.
 const bool keepSound = audio && transition.immediateSound && playSound(transition.immediateSound,scriptClock());
 if (!loadPlace(transition.destination,keepSound)) {
  _runner.defineValue(0,57,globals[57]); return false;
 }
 if (audio && transition.failureVoice) playSound(911,scriptClock());
 return true;
}
bool AstronomicaEngine::loadPlace(int place, bool keepSound, bool restoring) {
 if (place < 0 || place > 537) return false;
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP", place)));
 if (!Common::FSNode(path).exists() || !file.open(Common::FSNode(path)) || file.size() < 4) return false;
 Scene parsed;
 ResourceReader reader(file);
 if (!reader.read(parsed)) return false;
 file.seek(0);
 const int32 mode = file.readSint32LE();
 if (mode != 0 && mode != 1 && mode != 3) return false;
 int32 nav[3] = {0, 0, 0};
 if (mode == 1) {
  if (file.size() - file.pos() < 12) return false;
  for (int i = 0; i < 3; ++i) nav[i] = file.readSint32LE();
 }
 Graphics::Surface candidate;
 candidate.create(640, 480, _screen.format);
 candidate.fillRect(Common::Rect(640, 480), 0);
 const bool ok = readImage(file, candidate, false) && readImage(file, candidate, true);
 if (!ok) { candidate.free(); return false; }
 closeMovie();
 _background.copyFrom(candidate);
 if (ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") && supportsSpriteLayers(parsed)) {
  // _SWAddFrame selects frames[0]; _CreateSpriteFromBmpMem sets range 0..n-1.
  for (uint i = 0; i < parsed.sprites.size(); ++i) {
   Sprite &s = parsed.sprites[i];
   // _load_place 9:2d34-2e5e configures serialized ordinary movement.
   if (s.autoMove && (s.moveData[3] == 1 || s.moveData[3] == 2) && s.moveData[4] == 0) {
    s.standardMotion = true; s.moveDX = int16(s.moveData[1]); s.moveDY = int16(s.moveData[2]);
   }
   if (s.clone == -1 && s.layer >= 1 && s.layer <= parsed.layers && !s.frames.empty()) s.selectedFrame = 0;
   // _SWCloneSprite 7:0349-0358 copies the source's current frame.
   // Sources have already been loaded; invalid forward references stay unset.
   else if (s.clone > 0 && uint(s.clone) <= i && spriteFrameCount(parsed,i))
    s.selectedFrame = parsed.sprites[s.clone - 1].selectedFrame;
  }
 }
 const uint spritesDrawn = renderStaticSprites(file, parsed, candidate);
 _screen.copyFrom(candidate);
 candidate.free();
 if (!keepSound) _mixer->stopHandle(_soundHandle);
 _pendingImage.free();
 _pendingImageName.clear(); _displayedImageName.clear();
 _p519LargeImage = _p519SmallImage = 0;
 _p528EarthImage = _p528MoonImage = _p528TallMoon = 0;
 _p528HistoryValid = true;
 _p530HistoryValid = true;
 _p513HistoryValid = true;
 _p517HistoryValid = true;
 _builderHistoryValid = true;
 _loopSound = -1; _loopEnabled = true; _lastSoundAt = 0;
 _scene = parsed;
 _questionSaveBaseline.clear(); if (place == 501 || place == 504 || place == 503 || place == 502 || place == 527 || place == 516 || place == 511 || place == 509 || place == 521 || place == 518 || place == 514 || place == 522 || place == 529 || place == 537 || questionProfile(place) || variantProfile(place) || builderScene(place) || place == 517 || place == 513 || place == 519 || place == 524 || place == 526 || place == 528 || place == 530) _questionSaveBaseline = _scene.sprites;
 _rocket = RocketMotion();
 _probe = ProbeMotion(); _probeAssetsValid = false;
 _p501AssetsValid=place==501&&validP501Scene(_scene)&&p501Assets();
 _runner.setP501ReadySupport(_p501AssetsValid);
 _p504AssetsValid=place==504&&validP504Scene(_scene)&&p504Assets();
 _runner.setP504PollSupport(_p504AssetsValid);
 _p503AssetsValid=place==503&&validP503Scene(_scene)&&p503Assets();
 _p502AssetsValid=place==502&&validP502Scene(_scene)&&p502Assets();
 _p527AssetsValid=place==527&&validP527Scene(_scene)&&p527Assets();
 _p516AssetsValid=place==516&&validP516Scene(_scene)&&p516Assets();
 _p511AssetsValid=place==511&&validP511Scene(_scene)&&p511Assets();
 _p509AssetsValid=place==509&&validP509Scene(_scene)&&p509Assets();
 _p521AssetsValid=place==521&&validP521Scene(_scene)&&p521Assets();
 _planetAssetsValid=place==518&&validPlanetScene(_scene)&&universeFileIdentity(ConfMan.getPath("path").join("PLACES/P518/MEGAFILE.HYP"),489731,0x838a2480U);
 _rendezvousAssetsValid = place == 514 && validRendezvousScene(_scene) && universeFileIdentity(ConfMan.getPath("path").join("PLACES/P514/MEGAFILE.HYP"),586435,0x97d1b539U);
 _ball = BallMotion();
 // The original orientation phase is process-global, unlike the sprite links.
 const int oldCometFrame = _comet.frame, oldCometPrevious = _comet.previousFrame;
 _comet = CometMotion(); _comet.frame = oldCometFrame; _comet.previousFrame = oldCometPrevious;
 _runner.loadLocalConditions(_scene.conditions);
 _runner.setP509PendingSupport(place==509&&_scene.sprites.size()==19&&_scene.conditions.size()==17&&universeFileIdentity(ConfMan.getPath("path").join("PLACES/P509/MEGAFILE.HYP"),713948,3651436523U));
 _runner.setGameStateHandler(this);
 _runner.setRocketSupport(place == 537 && supportsRocket(_scene) &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation"));
 Common::Array<uint> targets;
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  const Sprite &s = _scene.sprites[i];
  targets.push_back(supportsSpriteLayers(_scene) && s.layer >= 1 && s.layer <= _scene.layers ? spriteFrameCount(_scene,i) : 0);
 }
 _runner.setSpriteTargets(targets);
 _runner.setEclipseSupport(place == 528 && _scene.layers == 1 && _scene.sprites.size() == 9 && spriteFrameCount(_scene,8) == 1);
 _runner.setPlanetSupport(place == 518 && _scene.layers == 1 && _scene.sprites.size() == 32 && _scene.sprites[8].standardMotion);
 _runner.setOrbitHandler(place == 526 && _scene.layers == 1 && _scene.sprites.size() == 23 && spriteFrameCount(_scene,17) == 12 &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") ? this : nullptr);
 // P515 is absent from custom25's original dispatch table. Preserve its
 // no-op even if out-of-order controls reach the shared success branch.
 _runner.setNoopSuccess(place == 515 && _scene.layers == 1 && _scene.sprites.size() == 60);
 _runner.setResumeSupport(place == 524 && _scene.layers == 1 && _scene.sprites.size() == 32,_place == 408);
 _runner.setZodiacSupport(place == 507 && _scene.layers == 1 && _scene.sprites.size() == 30);
 _runner.setPhotonSupport(place == 513 && _scene.layers == 1 && _scene.sprites.size() == 32 &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation"));
 _runner.setBallHandler(place == 501 && _scene.layers == 1 && _scene.sprites.size() == 27 &&
  spriteFrameCount(_scene,24) == 6 && spriteFrameCount(_scene,25) == 12 &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") ? this : nullptr);
 _runner.setJupiterSupport(place == 516 && supportsJupiter(_scene));
 _runner.setCometHandler((supportsComet(_scene,place) || (place == 516 && supportsJupiter(_scene))) &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") ? this : nullptr);
 _runner.setProbeHandler(place == 522 && _scene.layers == 1 && _scene.sprites.size() == 18 &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") ? this : nullptr);
 _runner.setRendezvousHandler(place == 514 && _scene.layers == 1 && _scene.sprites.size() == 20 &&
  ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") ? this : nullptr);
 _runner.setPrograms(_scene.scripts, scriptClock());
 if (place == 1) _runner.resetGlobals();
 _previousPlace = _place;
 _place = place;
 configureSounds();
 configureImages();
 configureMovie();
 if (place == 1) prepareLegacyResume();
 _runner.setLegacyResumeSupport(place == 1 && _legacyAvailable);
 _runner.setHelpSupport((place == 1 || place == 408) && ensureHelpBook());
 configureHover();
 for (int i = 0; i < 3; ++i) _nav[i] = nav[i];
 presentScene();
 debug("Astronomica resource explorer: P%d; nav %d,%d,%d", place, nav[0], nav[1], nav[2]);
 if (spritesDrawn) debug("Astronomica static sprites: P%d, %u drawn", place, spritesDrawn);
 if (!restoring && ConfMan.hasKey("astronomica_entry_scripts") && ConfMan.getBool("astronomica_entry_scripts")) {
  // Reconstructed mode-0 audio lifecycle (_load_place 9:156b, 1c45,
  // 2f22). Other scene modes have separate global ambience rules.
  if (_scene.mode == 0 && ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
   Audio::SeekableAudioStream *music = openSound(0);
   if (music) { _loopSound = 0; delete music; }
   // Intro IDs are direct file IDs, not serialized command operands.
   // The original skips the intro on return from P408 (help).
   // With movies, 9:1c51-1c8f calls sndPlaySound on the same direct
   // intro file with flags 0 (synchronous). It does not skip the voice.
   if (_scene.introSound && _previousPlace != 408 && _runner.variantRound() <= 1 && playSound(_scene.introSoundId, scriptClock())) {
    debug("Astronomica P%d introduction: S%d.WAV", _place, _scene.introSoundId);
    while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {
     Common::Event event;
     while (_system->getEventManager()->pollEvent(event))
      if (event.type == Common::EVENT_QUIT) quitGame();
     _system->updateScreen();
     _system->delayMillis(5);
    }
   }
   _lastSoundAt = 0; // Original resets this after scene loading.
  }
  if (!shouldQuit()) queueEntryScripts();
 }
 return true;
}
Audio::SeekableAudioStream *AstronomicaEngine::openSound(int id) {
 if (id < 0 || id > 922) return nullptr;
 Common::File *file = new Common::File();
 const Common::Path path = ConfMan.getPath("path").join(Common::Path((id >= 900 ? Common::String::format("SOUNDS/S%d.WAV",id-900) : Common::String::format("PLACES/P%d/S%d.WAV", _place, id))));
 if (!Common::FSNode(path).exists() || !file->open(Common::FSNode(path))) { delete file; return nullptr; }
 return Audio::makeWAVStream(file, DisposeAfterUse::YES);
}
Graphics::Surface *AstronomicaEngine::openBackgroundImage(const Common::String &rawName, int place) {
 Common::String name = rawName; name.toUppercase();
 if (name.empty() || name == "." || name == "..") return nullptr;
 for (uint i = 0; i < name.size(); ++i)
  if (!((name[i] >= 'A' && name[i] <= 'Z') || (name[i] >= '0' && name[i] <= '9') || name[i] == '_' || name[i] == '-' || name[i] == '.')) return nullptr;
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/",place < 0 ? _place : place) + name));
 if (!file.open(Common::FSNode(path)) || file.size() < 54 || file.readUint16LE() != 0x4d42) return nullptr;
 // The shared decoder excludes monochrome external bitmaps.
 file.seek(28); if (file.readUint16LE() == 1) return nullptr;
 file.seek(0); Image::BitmapDecoder decoder;
 if (!decoder.loadStream(file) || !decoder.getSurface()) return nullptr;
 const Graphics::Surface *src = decoder.getSurface();
 if (src->w <= 0 || src->h <= 0 || src->w > 640 || src->h > 480) return nullptr;
 return src->convertTo(_screen.format,decoder.getPalette().data(),decoder.getPalette().size());
}
void AstronomicaEngine::configureImages() {
 Common::Array<Common::String> targets;
 if (_scene.layers == 1 || _scene.mode == 1 || _place == 425 || _place == 3) {
  Common::FSList files;
  const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d",_place)));
  Common::FSNode(path).getChildren(files,Common::FSNode::kListFilesOnly);
  for (uint i = 0; i < files.size(); ++i) {
   Common::String name = files[i].getName(); name.toUppercase();
   Graphics::Surface *surface = openBackgroundImage(name);
   if (surface) { targets.push_back(name); surface->free(); delete surface; }
  }
 }
 _runner.setImageTargets(targets);
}
bool AstronomicaEngine::stageBackgroundImage(const Common::String &name, int x, int y) {
 Graphics::Surface *src = openBackgroundImage(name);
 if (!src) return false;
 _pendingImage.copyFrom(*src); _pendingImageName = name; _pendingImageX = x; _pendingImageY = y;
 src->free(); delete src; return true;
}
void AstronomicaEngine::displayBackgroundImage() {
 if (_place == 530 && _pendingImage.w && (p530ImageId(_pendingImageName) <= 0 || _pendingImageX != 460 || _pendingImageY != 10 || _pendingImage.w != 172 || _pendingImage.h != 172)) _p530HistoryValid = false;
 if (builderScene(_place) && _pendingImage.w && (builderImageId(_pendingImageName) <= 0 || _pendingImageX || _pendingImageY || _pendingImage.w != 250 || _pendingImage.h != 330)) _builderHistoryValid = false;
 if (_place == 517 && _pendingImage.w && (p517ImageId(_pendingImageName) <= 0 || _pendingImageX || _pendingImageY || _pendingImage.w != 640 || _pendingImage.h != 320)) _p517HistoryValid = false;
 if (_place == 513 && _pendingImage.w && (p513ImageId(_pendingImageName,true) <= 0 || _pendingImageX != 177 || _pendingImageY != 22 || _pendingImage.w != 313 || _pendingImage.h != 320)) _p513HistoryValid = false;
 if (_place == 528 && _pendingImage.w) {
  const uint earth = p528ImageId(_pendingImageName,false), moon = p528ImageId(_pendingImageName,true);
  if (earth && _pendingImageX == 87 && _pendingImageY == 356 && _pendingImage.w == 171 && _pendingImage.h == 105) _p528EarthImage = earth;
  else if (moon && _pendingImageX == 401 && _pendingImageY == 369 && _pendingImage.w == 143 && _pendingImage.h == (p528Tall(moon) ? 81 : 80)) {
   _p528MoonImage = moon; if (p528Tall(moon)) _p528TallMoon = moon;
  } else { _p528HistoryValid = false; _p528EarthImage = _p528MoonImage = _p528TallMoon = 0xffffffffU; }
 }
 if (_place == 519 && _pendingImage.w) {
  const uint large = p519ImageId(_pendingImageName,true), small = p519ImageId(_pendingImageName,false);
  if (large && _pendingImageX == 258 && _pendingImageY == 356 && _pendingImage.w == 143 && _pendingImage.h == 108) {
   _p519LargeImage = large; _p519SmallImage = 0;
  } else if (small && _pendingImageX == 282 && _pendingImageY == 358 && _pendingImage.w == 99 && _pendingImage.h == 99) {
   _p519SmallImage = small;
  } else { _p519LargeImage = _p519SmallImage = 0; }
 }
 if (_pendingImage.w) _displayedImageName = _pendingImageName;
 // Opcode 49 calls _UpdateGame -> _SWUpdateSpriteWorld, a full-world
 // copy (6:069d-07c7). Unlike incremental sprite updates it overwrites
 // the previous movie image. A playing decoder can draw its next frame.
 _movieFrame.free(); _moviePresentedFrame = -1;
 // The loaded image is shared by script invocations until display or reload.
 for (int sy = 0; sy < _pendingImage.h; ++sy) for (int sx = 0; sx < _pendingImage.w; ++sx) {
  const int x = _pendingImageX+sx, y = _pendingImageY+sy;
  if (x >= 0 && x < _background.w && y >= 0 && y < _background.h)
   _background.setPixel(x,y,_pendingImage.getPixel(sx,sy));
 }
 // Original deletes the bitmap after copying. Do not retain a stale handle.
 _pendingImage.free(); _pendingImageName.clear(); redrawSprites();
}
void AstronomicaEngine::configureSounds() {
 Common::Array<bool> targets; targets.resize(923);
 for (uint i = 0; i < targets.size(); ++i) targets[i] = false;
 if (ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
  Common::FSList files;
  const Common::Path folder = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d", _place)));
  Common::FSNode(folder).getChildren(files, Common::FSNode::kListFilesOnly);
  for (uint i = 0; i < files.size(); ++i) {
   Common::String name = files[i].getName(); name.toUppercase();
   if (!name.hasPrefix("S") || !name.hasSuffix(".WAV")) continue;
   const int id = atoi(name.c_str() + 1);
   if (id < 0 || id >= 900 || name != Common::String::format("S%d.WAV", id)) continue;

   Common::File file;
   if (!file.open(files[i])) continue;
   int size, rate; byte flags; uint16 type;
   if (Audio::loadWAVFromStream(file, size, rate, flags, &type) && type == 1)
    targets[id] = true;
  }
  // Serialized operands are decremented by the original reader. Direct
  // IDs900..922 refer to SOUNDS/S0..S22 rather than a scene-local file.
  for (int id = 900; id <= 922; ++id) {
   Audio::SeekableAudioStream *sound = openSound(id);
   targets[id] = sound != nullptr; delete sound;
  }
 }
 _runner.setSoundTargets(targets);
 if (_place == 513) _runner.setSuccessHandler(this,_place); // Counter only; no global S12 dependency.
 if (ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) _runner.setSoundHandler(this);
 if (ScriptRunner::successGlobalForPlace(_place) >= 0 && ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
  Common::File successFile;
  const Common::Path successPath = ConfMan.getPath("path").join(Common::Path("SOUNDS/S12.WAV"));
  int size, rate; byte flags; uint16 type;
  if (successFile.open(Common::FSNode(successPath)) && Audio::loadWAVFromStream(successFile, size, rate, flags, &type) && type == 1)
   _runner.setSuccessHandler(this,_place);
  if (_place == 506 || (_place >= 531 && _place <= 535)) {
   Audio::SeekableAudioStream *voice = openSound(922);
   _runner.setVariantSupport(voice != nullptr); delete voice;
  }
 }

}
bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {
 Audio::SeekableAudioStream *stream = openSound(id);
 if (!stream) return false;
 // sndPlaySound is a single channel; a new sound replaces the old one.
 _mixer->stopHandle(_soundHandle);
 // Background loops follow ScummVM's Music control. Foreground sounds
 // retain the Effects control and replace the loop on this same handle.
 _mixer->playStream(looping ? Audio::Mixer::kMusicSoundType : Audio::Mixer::kSFXSoundType,
  &_soundHandle, looping ? Audio::makeLoopingAudioStream(stream, 0) : stream);
 if (!looping) _lastSoundAt = now;
 _lastSound = id; ++_soundsStarted;
 return true;
}
void AstronomicaEngine::resumeLoopAt(uint32 now) {
 // _playLoop 9:3c29 probes with SND_NOSTOP. A playing foreground sound
 // must finish before the loop can resume. Puzzle scenes also wait >5 s.
 if (_moviePlaying || _loopSound < 0 || !_loopEnabled || _mixer->isSoundHandleActive(_soundHandle)) return;
 if (_place >= 500 && _place <= 550 && uint32(now - _lastSoundAt) <= 5000) return;
 if (!playSound(_loopSound, now, true)) _loopSound = -1;
 else debug("Astronomica P%d loop: S%d.WAV", _place, _loopSound);
}
bool AstronomicaEngine::isBlockingSound(int id) const {
 // _playSound 9:3bb5-3be9 selects synchronous flags for these local files.
 return id == 912 || id == 922 || _moviePlaying || (_place == 505 && id >= 2 && id <= 10) || (_place == 512 && id == 14);
}
uint32 AstronomicaEngine::onBlockingSound(int id, uint32 now) {
 applyScriptActions(now);
 // _playSound 9:3b1a/3bda/3c14 pauses active QuickTime playback, waits
 // for the foreground sound, then resumes the remaining selection.
 const bool pauseMovie = _movie && _moviePlaying;
 if (pauseMovie) _movie->pauseVideo(true);
 const uint32 started = _system->getMillis();
 if (playSound(id,now)) {
  while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {
   Common::Event event;
   while (_system->getEventManager()->pollEvent(event))
    if (event.type == Common::EVENT_QUIT) quitGame();
   _system->updateScreen();
   _system->delayMillis(5);
  }
 }
 if (pauseMovie && _movie) _movie->pauseVideo(false);
 _lastBlockingSoundEnd = now + uint32(_system->getMillis() - started);
 return _lastBlockingSoundEnd;
}
uint32 AstronomicaEngine::onPuzzleSuccess(uint32 now) {
 if (_place == 513) { ++_puzzlesCompleted; _lastSuccessEnd = now; return now; }
 _lastSuccessEnd = onBlockingSound(912,now);
 // P530's 4:5a64 handler calls _playSound(912) directly rather than
 // _puzzle_successful. The voice is synchronous, but the counter stays.
 if (_place != 530) ++_puzzlesCompleted;
 return _lastSuccessEnd;
}
bool AstronomicaEngine::verifyAudio() {
 struct Reference { int id; uint samples; uint32 hash; };
 const Reference refs[] = { {1,127488,0x6f7731d2U}, {2,3627,0x1c898683U}, {5,19516,0x0ad041f8U} };
 bool ok = true;
 for (uint i = 0; i < ARRAYSIZE(refs); ++i) {
  Audio::SeekableAudioStream *stream = openSound(refs[i].id);
  if (!stream) return false;
  ok = stream->getRate() == 11025 && !stream->isStereo() && ok;
  int16 samples[1024]; uint count = 0; uint32 hash = 2166136261U;
  for (;;) {
   const int n = stream->readBuffer(samples, ARRAYSIZE(samples));
   if (n <= 0) break;
   count += n;
   for (int j = 0; j < n; ++j) {
    const uint16 v = uint16(samples[j]);
    hash = (hash ^ (v & 255)) * 16777619U;
    hash = (hash ^ (v >> 8)) * 16777619U;
   }
  }
  delete stream;
  debug("Astronomica audio samples: P510/S%d.WAV %u %08x", refs[i].id, count, hash);
  ok = count == refs[i].samples && hash == refs[i].hash && ok;
 }
 return ok;
}
void AstronomicaEngine::presentScene() {
 // Keep the decoded movie frame when a button or sprite redraws the scene.
 for (int y = 0; y < _movieFrame.h && y+_movieY < _screen.h; ++y)
  for (int x = 0; x < _movieFrame.w && x+_movieX < _screen.w; ++x)
   _screen.setPixel(x+_movieX,y+_movieY,_movieFrame.getPixel(x,y));
 // The original control panel and some committed pictures extend below
 // row456. Keep all480 composed rows during ordinary play.
 if (ConfMan.hasKey("astronomica_debug_overlay") && ConfMan.getBool("astronomica_debug_overlay")) {
  _screen.fillRect(Common::Rect(0, 456, 640, 480), 0);
  const Common::String label = Common::String::format("EXPERIMENTAL | P%d | simple hotspots | PgUp/PgDn: browse | Esc: exit", _place);
  FontMan.getFontByUsage(Graphics::FontManager::kGUIFont)->drawString(&_screen, label, 5, 462, 630, _screen.format.RGBToColor(255, 255, 255));
 }
 _system->copyRectToScreen(_screen.getPixels(), _screen.pitch, 0, 0, 640, 480);
 _system->updateScreen();
}
void AstronomicaEngine::redrawSprites() {
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP", _place)));
 if (!file.open(Common::FSNode(path))) { warning("Astronomica: cannot redraw P%d", _place); return; }
 _screen.copyFrom(_background);
 renderStaticSprites(file, _scene, _screen);
 presentScene();
}
bool AstronomicaEngine::demoVisibility(bool visible) {
 // Diagnostic demonstration: execute one original show/hide instruction,
 // without claiming that the timed VCR flashing script is implemented.
 if (_place != 29 || _scene.sprites.size() < 2) return false;
 for (uint s = 0; s < _scene.scripts.size(); ++s)
  for (uint i = 0; i < _scene.scripts[s].size(); ++i) {
   const Command &c = _scene.scripts[s][i];
   if (c.opcode == (visible ? 16 : 17) && c.args.size() == 1 && c.args[0] == 2) {
    Script one; one.push_back(c); return _runner.enqueue(one, scriptClock(), true);
   }
  }
 return false;
}
bool AstronomicaEngine::demoMovement(int x) {
 if (_place != 517) return false;
 for (uint s = 0; s < _scene.scripts.size(); ++s)
  for (uint i = 0; i < _scene.scripts[s].size(); ++i) {
   const Command &c = _scene.scripts[s][i];
   if (c.opcode == 7 && c.args.size() == 3 && c.args[0] == 7 && c.args[1] == x && c.args[2] == 361) {
    Script one; one.push_back(c); return _runner.enqueue(one, scriptClock(), true);
   }
  }
 return false;
}
bool AstronomicaEngine::demoOffset(int spriteId) {
 if (_place != 510) return false;
 for (uint s = 0; s < _scene.scripts.size(); ++s)
  for (uint i = 0; i < _scene.scripts[s].size(); ++i) {
   const Command &c = _scene.scripts[s][i];
   if (c.opcode == 47 && c.args.size() == 3 && c.args[0] == spriteId && c.args[1] == 0 && c.args[2] == 1) {
    Script one; one.push_back(c); return _runner.enqueue(one, scriptClock(), true);
   }
  }
 return false;
}
bool AstronomicaEngine::demoFrame(int frame) {
 if (_place != 510) return false;
 for (uint s = 0; s < _scene.sprites.size(); ++s)
  for (uint i = 0; i < _scene.sprites[s].click.size(); ++i) {
   const Command &c = _scene.sprites[s].click[i];
   if (c.opcode == 15 && c.args.size() == 2 && c.args[0] == 10 && c.args[1] == frame) {
    Script one; one.push_back(c); return _runner.enqueue(one, scriptClock(), true);
   }
  }
 return false;
}
void AstronomicaEngine::queueEntryScripts() {
 const uint accepted = _runner.enqueueStartup(_scene.scripts, scriptClock(), true);
 debug("Astronomica P%d entry scripts: %u queued, %u skipped", _place, accepted, _scene.scripts.size() - accepted);
 if (accepted < _scene.scripts.size())
  warning("Astronomica P%d entry behavior incomplete: unsupported scripts skipped", _place);
}
// _place_loop 9:0896/0cba: independent entered flags, sprite order then
// rectangle order. Pending commands run on the next loop, even during click lock.
void AstronomicaEngine::configureHover() {
 _hoverSprites.clear(); _hoverRects.clear();
 if (_place != 1 && _place != 505 && _place != 519 && _place != 526) return;
 if (!ConfMan.getBool("astronomica_sprite_input")) return;
 // These original scenes have neither special cursor interception nor dragging.
 for (uint i = 0; i < _scene.sprites.size(); ++i)
  if (_scene.sprites[i].cursor || _scene.sprites[i].dragEnabled) return;
 _hoverSprites.resize(_scene.sprites.size()); _hoverRects.resize(_scene.mouseRects.size());
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP",_place)));
 const bool opened = file.open(Common::FSNode(path));
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  const Sprite &sprite = _scene.sprites[i]; HoverTarget &target = _hoverSprites[i];
  if (sprite.mouseIn.empty() || sprite.mouseOut.empty() || !opened ||
      !supportsSpriteLayers(_scene) || sprite.layer != 1 || sprite.autoMove || sprite.autoFrame ||
      !_runner.canRun(sprite.mouseIn,true) || !_runner.canRun(sprite.mouseOut,true)) continue;
  const uint count = spriteFrameCount(_scene,i);
  bool valid = count != 0;
  // Cache only invariant bounds; do not decode bitmaps on every pointer sample.
  for (uint f = 0; f < count && valid; ++f) {
   const Frame *frame = spriteFrameAt(_scene,i,f);
   Graphics::Surface *bmp = frame ? decodeSpriteBitmap(file,frame->image,_screen.format) : nullptr;
   if (!bmp) { valid = false; break; }
   valid = !f || (target.width == bmp->w && target.height == bmp->h);
   target.width = bmp->w; target.height = bmp->h; bmp->free(); delete bmp;
  }
  target.ready = valid;
 }
 for (uint i = 0; i < _scene.mouseRects.size(); ++i) {
  const MouseRect &r = _scene.mouseRects[i];
  _hoverRects[i].ready = !r.mouseIn.empty() && !r.mouseOut.empty() &&
   _runner.canRun(r.mouseIn,true) && _runner.canRun(r.mouseOut,true);
 }
}
void AstronomicaEngine::hoverAtTime(int x, int y, uint32 now) {
 for (uint i = 0; i < _hoverSprites.size(); ++i) {
  HoverTarget &t = _hoverSprites[i]; const Sprite &s = _scene.sprites[i];
  if (!t.ready) continue;
  const bool inside = pointInSprite(s,t.width,t.height,x,y);
  if (inside != t.entered && _runner.enqueue(inside ? s.mouseIn : s.mouseOut,now,true)) t.entered = inside;
 }
 for (uint i = 0; i < _hoverRects.size(); ++i) {
  HoverTarget &t = _hoverRects[i]; const MouseRect &r = _scene.mouseRects[i];
  if (!t.ready) continue;
  const bool inside = x >= r.rect[0] && y >= r.rect[1] && x < r.rect[2] && y < r.rect[3];
  if (inside != t.entered && _runner.enqueue(inside ? r.mouseIn : r.mouseOut,now,true)) t.entered = inside;
 }
}
int AstronomicaEngine::spriteAt(int x, int y) {
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP", _place)));
 if (!file.open(Common::FSNode(path))) return -2;
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  const Sprite &s = _scene.sprites[i];
  if (!s.clickEnabled && !s.dragEnabled) continue;
  // Until their changing geometry is reconstructed, do not guess a hit.
  if (!supportsSpriteLayers(_scene) || s.layer != 1 || s.autoMove || s.autoFrame) return -2;
  const uint count = spriteFrameCount(_scene, i);
  if (!count) return -2;
  int width = -1, height = -1;
  // With no selected preview frame, accept only invariant frame dimensions.
  for (uint f = 0; f < count; ++f) {
   if (s.selectedFrame >= 0 && uint(s.selectedFrame) != f) continue;
   const Frame *frame = spriteFrameAt(_scene, i, f);
   Graphics::Surface *bmp = frame ? decodeSpriteBitmap(file, frame->image, _screen.format) : nullptr;
   if (!bmp) return -2;
   const bool mismatch = width >= 0 && (width != bmp->w || height != bmp->h);
   width = bmp->w; height = bmp->h; bmp->free(); delete bmp;
   if (mismatch) return -2;
  }
  if (width < 0) return -2;
  // Original hit test ignores visibility and mask pixels.
  if (pointInSprite(s, width, height, x, y)) return int(i);
 }
 return -1;
}
void AstronomicaEngine::clickAt(int x, int y) { clickAtTime(x,y,scriptClock()); }
void AstronomicaEngine::clickAtTime(int x, int y, uint32 now) {
 if (_runner.clicksBlocked()) return;
 // Original _do_mouse 9:11f7 stores the last click before hit dispatch.
 if (_place == 507) _runner.setZodiacRegion(astrologyRegion(x,y,444,165,122,30));
 if (!_scene.sprites.empty()) {
  if (!ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return;
  const int hit = spriteAt(x, y);
  if (hit == -2) { warning("Astronomica: sprite input geometry incomplete in P%d", _place); return; }
  if (hit >= 0) {
   const Sprite &s = _scene.sprites[hit];
   if (!s.clickEnabled || s.dragEnabled || (s.clickType != 0 && s.clickType != 2) || !_runner.canRun(s.click, true)) {
    warning("Astronomica: unsupported sprite click in P%d, sprite %d", _place, hit + 1);
    return;
   }
   if (s.clickType == 2) {
    // Original _button_click, initialized at 9:0071: frame 1 now, frame 0
    // after 500 ms. _do_mouse runs this before enqueueing the user script.
    Script pulse; Command frame; frame.opcode = 15;
    frame.args.push_back(hit + 1); frame.args.push_back(1); pulse.push_back(frame);
    frame.args[1] = 0; frame.delay = 500; pulse.push_back(frame);
    if (!_runner.start(pulse, now, true)) return;
    applyScriptActions(now);
   }
   _runner.enqueue(s.click, now, true);
   return; // A sprite always consumes the hit, even if its script is rejected.
  }
 }
 for (uint i = 0; i < _scene.mouseRects.size(); ++i) {
  const MouseRect &r = _scene.mouseRects[i];
  if (x >= r.rect[0] && y >= r.rect[1] && x < r.rect[2] && y < r.rect[3]) {
   if (!_runner.enqueue(r.click, now, ConfMan.hasKey("astronomica_sprite_input") && ConfMan.getBool("astronomica_sprite_input")) && !r.click.empty())
    warning("Astronomica: unsupported click script in P%d, rectangle %u", _place, i);
  }
 }
}
uint32 AstronomicaEngine::scriptClock() const {
 if (ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) return 0;
 return (_clockPaused ? _pauseStarted : _system->getMillis())-_pausedMillis;
}
void AstronomicaEngine::runScripts() { runScriptsAt(scriptClock()); }
void AstronomicaEngine::updateWorldAt(uint32 now) {
 int32 mode = 0,item = 0,stage = 0,started = 0;
 if (!_runner.getValue(0,60,mode) || !_runner.getValue(0,53,item) ||
     !_runner.getValue(0,62,stage) || !_runner.getValue(0,8,started)) return;
 const CountdownResult r = worldCountdown(mode,item,stage,uint32(started),now);
 _runner.defineValue(0,60,r.mode); _runner.defineValue(0,62,r.stage);
 if (r.sound) playSound(r.sound,now);
 if (r.destination) changePlace(r.destination);
}

bool AstronomicaEngine::onOrbitAnswer(int scenario, int choice, uint32 now) {
 applyScriptActions(now);
 return _place == 526 && orbitAnswer(scenario,_scene.sprites[17].selectedFrame,choice);
}
bool AstronomicaEngine::onRendezvous(int mode, int speed, uint32 now) {
 applyScriptActions(now);
 if (_place != 514 || _scene.sprites.size() != 20) return false;
 if (mode < 3) { configureRendezvous(_scene,mode,speed); return false; }
 Sprite &target = _scene.sprites[16], &ship = _scene.sprites[18], &probe = _scene.sprites[19];
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("PLACES/P514/MEGAFILE.HYP"))))) return false;
 const Frame *a = staticSpriteFrame(_scene,16), *b = staticSpriteFrame(_scene,19);
 Graphics::Surface *targetBmp = a ? decodeSpriteBitmap(file,a->image,_screen.format) : nullptr;
 Graphics::Surface *probeBmp = b ? decodeSpriteBitmap(file,b->image,_screen.format) : nullptr;
 if (!targetBmp || !probeBmp) {
  if (targetBmp) { targetBmp->free(); delete targetBmp; }
  if (probeBmp) { probeBmp->free(); delete probeBmp; }
  return false;
 }
 // 4:3736 passes the ship's RIGHT edge as the probe's y coordinate.
 // This unusual original argument order is intentional, not a typo.
 const Frame *shipFrame = staticSpriteFrame(_scene,18);
 Graphics::Surface *shipBmp = shipFrame ? decodeSpriteBitmap(file,shipFrame->image,_screen.format) : nullptr;
 if (!shipBmp) { targetBmp->free(); delete targetBmp; probeBmp->free(); delete probeBmp; return false; }
 probe.renderX = ship.renderX; probe.renderY = int16(ship.renderX+shipBmp->w);
 const int left = target.renderX, top = target.renderY, right = left+targetBmp->w, bottom = top+targetBmp->h;
 const int px[] = {left,right,left,right,(left+right)/2}, py[] = {top,top,bottom,bottom,(top+bottom)/2};
 bool hit = false;
 // The original moves sprite20 above, but tests sprite19 (bp-0x16=19).
 for (uint i = 0; i < 5; ++i) hit = pointInSprite(ship,shipBmp->w,shipBmp->h,px[i],py[i]) || hit;
 targetBmp->free(); delete targetBmp; probeBmp->free(); delete probeBmp; shipBmp->free(); delete shipBmp;
 if (hit) {
  ship.autoMove = _scene.sprites[13].autoMove = false;
  ship.moveData[0] = _scene.sprites[13].moveData[0] = -1;
 }
 return hit;
}
void AstronomicaEngine::runScriptsAt(uint32 now) {
 _runner.tick(now);
 applyScriptActions(now);
}
void AstronomicaEngine::applyScriptActions(uint32 now) {
 ScriptRunner::Action action;
 bool dirty = false;
 bool changePlace = false;
 int nextPlace = -1;
 while (_runner.popAction(action)) {
  if (action.opcode == 23 && (action.value == 1 || action.value == 4 || action.value == 5 || action.value == 20)) {
   if (_place == 523 && _movie) dangerCustom(action.value,action.x);
   continue;
  }
  if (action.opcode == 23 && action.value == 23) {
   if (_place == 510 && _movie) applyPlotStep(plotStart(action.x));
   continue;
  }
  if (action.opcode == 23 && action.value == 33) {
   if (_place == 1 && _legacyAvailable && restoreLegacyState(_legacyState)) return;
   warning("Astronomica: cannot resume original saved game"); continue;
  }
  if (action.opcode == 23 && action.value == 22) { openHelpBook(); continue; }
  if (action.opcode == 23 && action.value == 29) {
   // Original custom29 calls UpdateGame -> SWUpdateSpriteWorld:
   // rebuild the background and sprites, then copy them to the display.
   _movieFrame.free(); _moviePresentedFrame = -1; presentScene(); dirty = false; continue;
  }
  if (action.opcode == 4 && _movie) { _movie->stop(); _moviePlaying = false; continue; }
  if (action.opcode == 23 && action.value == 10) {
   if (_place == 513) dirty = startPhoton(_scene,action.x) || dirty;
   continue;
  }
  if (action.opcode == 23 && action.value == 24) {
   if (_place != 512 || !_movie) continue;
   if (action.x == 1) {
    // _ShowMovie also sends MCActionPlay at the preferred rate (17:0494).
    _mixer->stopHandle(_soundHandle); _movieX = 160; _movieY = 57;
    _movie->start(); _moviePlaying = true;
   } else if (action.x == 2) {
    _mixer->stopHandle(_soundHandle);
    if (_movie->endOfVideo() || _movie->getTime() >= uint32(_movie->getEndTime().msecs()))
     _movie->seek(Audio::Timestamp(0,_movieSegmentStart,_movie->getTimeScale()));
    _movie->start(); _moviePlaying = true;
   } else { updateMovie(); presentScene(); }
   continue;
  }
  if (action.opcode == 23 && action.value == 13) {
   if (_place == 526) dirty = startOrbit(_scene,action.x,action.y,action.motion[0]) || dirty;
   continue;
  }
  if (action.opcode == 23 && action.value == 12) {
   if (_place != 518 || action.y < 1 || action.y > 9) continue;
   Sprite &planet = _scene.sprites[action.y+8];
   if (action.x == 0) {
    Common::File file;
    const Frame *frame = staticSpriteFrame(_scene,action.y+8);
    if (!frame || !file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("PLACES/P518/MEGAFILE.HYP"))))) continue;
    Graphics::Surface *bmp = decodeSpriteBitmap(file,frame->image,_screen.format);
    if (!bmp) continue;
    const Sprite &launcher = _scene.sprites[8];
    planet.planetMotion = 1; planet.planetPeriod = int16(launcher.moveData[0]);
    planet.standardMotion = planet.autoMove = true;
    planet.moveDX = launcher.moveDX; planet.moveDY = launcher.moveDY;
    planet.renderX = int16(launcher.renderX-bmp->w); planet.renderY = launcher.renderY;
    planet.visible = 1; planet.moveData[0] = action.motion[0]; planet.x = action.y;
    bmp->free(); delete bmp;
   } else {
    planet.planetMotion = 2; planet.moveDX = -2; planet.moveDY = 0;
    planet.moveData[0] = action.motion[0];
   }
   dirty = true; continue;
  }
  if (action.opcode == 23 && action.value == 14) {
   int32 setting = 0;
   if (_place == 537 && _runner.getValue(1,0,setting) && startRocket(_scene,_rocket,setting)) dirty = true;
   continue;
  }
  if (action.opcode == 23 && action.value == 18) {
   dirty = positionEclipseMoon(_scene,action.x,action.y) || dirty;
   continue;
  }
  if (action.opcode == 50) {
   debug("Astronomica native RGB palette command: %s",action.text.c_str());
   continue;
  }
  if (action.opcode == 37 && _movie) {
   _movieSegmentStart = action.x;
   if (_place == 529 || _place == 527) _universeSegmentEnd = uint32(action.x)+uint32(action.y);
   const uint32 scale = _movie->getTimeScale();
   _movie->setEndTime(Audio::Timestamp(0,uint32(action.x)+uint32(action.y),scale));
   if (!_movie->seek(Audio::Timestamp(0,action.x,scale))) warning("Astronomica: movie segment seek failed");
   continue;
  }
  if (action.opcode == 36 && _movie) {
   if (!_movie->seek(Audio::Timestamp(0,action.x,_movie->getTimeScale()))) warning("Astronomica: movie time seek failed");
   continue;
  }
  if (action.opcode == 3 && _movie) {
   _mixer->stopHandle(_soundHandle);
   // QCMC action8 rewinds a completed positive-rate world movie before play.
   // Preserve the current time when playback is still inside the range.
   if (_runner.worldMovieSupport() && (_movie->endOfVideo() || _movie->getTime() >= uint32(_movie->getEndTime().msecs()))) {
    _movie->stop(); _moviePlaying = false;
    if (!_movie->seek(Audio::Timestamp(0,0,_movie->getTimeScale()))) { warning("Astronomica: movie replay seek failed"); continue; }
   }
   _movieX = action.x; _movieY = action.y; _movie->start(); _moviePlaying = true;
   // Original PlayMovie stores movie bottom+5; mouse update 9:1035
   // clamps the cursor below it until command35 clears DS:01d1.
   if (_runner.worldMovieSupport()) _worldMovieCursorBottom = MIN<int>(479,_movieY+_movie->getHeight()+5);
   debug("Astronomica P%d movie started at %d,%d",_place,_movieX,_movieY);
   continue;
  }
  if (action.opcode == 20) {
   if (!stageBackgroundImage(action.text,action.x,action.y)) warning("Astronomica: cannot draw image %s",action.text.c_str());
   continue;
  }
  if (action.opcode == 49) { displayBackgroundImage(); dirty = false; continue; }
  if (action.opcode == 21) {
   // _flash_white 18:1652-1729 fills the working image and front DC.
   // It does not overwrite the stored background or impose a timed pause.
   if (dirty) { redrawSprites(); dirty = false; }
   _screen.fillRect(Common::Rect(640,480),_screen.format.RGBToColor(255,255,255));
   _system->copyRectToScreen(_screen.getPixels(),_screen.pitch,0,0,640,480);
   _system->updateScreen();
   continue;
  }
  if (action.opcode == 25) {
   _loopEnabled = false; _mixer->stopHandle(_soundHandle); continue;
  }
  if (action.opcode == 26) { _loopEnabled = true; continue; }
  if (action.opcode == 27) {
   _mixer->stopHandle(_soundHandle); _loopSound = action.value; _lastSoundAt = 0;
   continue;
  }
  if (action.opcode == 10) {
   // _stop_sounds ignores its argument and calls sndPlaySound(NULL,1).
   _mixer->stopHandle(_soundHandle);
   continue;
  }
  if (action.opcode == 9) {
   if (!playSound(action.value, now)) warning("Astronomica: cannot play sound %d in P%d", action.value, _place);
   continue;
  }
  if (action.opcode == 48) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size())
    setSpriteFrameRange(_scene.sprites[action.value - 1], spriteFrameCount(_scene, action.value - 1), action.x, action.y);
   continue;
  }
  if (action.opcode == 15) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size() && action.x >= 0 &&
       uint(action.x) < spriteFrameCount(_scene,action.value-1)) {
    _scene.sprites[action.value - 1].selectedFrame = action.x; dirty = true;
   }
   continue;
  }
  if (action.opcode == 30) {
   // 15:0b2d-0bfd: disable frame/move timers and hide; keep frame/position.
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size()) {
    Sprite &stopped = _scene.sprites[action.value-1];
    stopped.frameData[0] = stopped.moveData[0] = -1;
    stopped.autoFrame = stopped.autoMove = false; stopped.visible = 0;
    if (_place == 537 && action.value == 34) _rocket.kind = RocketMotion::kStopped;
    dirty = true;
   }
   continue;
  }
  if (action.opcode == 19) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size()) {
    Sprite &animatedSprite = _scene.sprites[action.value-1];
    animatedSprite.frameData[0] = action.x; animatedSprite.frameData[1] = action.y; animatedSprite.frameData[2] = 0;
    animatedSprite.autoFrame = action.x >= 0;
    // _SWSetSpriteFrameTime does not reset the last-frame timestamp.
   }
   continue;
  }
  if (action.opcode == 18) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size()) {
    Sprite &moving = _scene.sprites[action.value-1];
    if (_place == 501 && action.value == 25) _ball = BallMotion();
    moving.moveData[0] = action.x; moving.moveData[1] = action.y;
    for (int i = 0; i < 3; ++i) moving.moveData[i+2] = action.motion[i];
    moving.moveDX = int16(action.y); moving.moveDY = int16(action.motion[0]);
    moving.standardMotion = true; moving.autoMove = action.x >= 0;
    // _SWSetSpriteMoveTime preserves the last movement timestamp.
   }
   continue;
  }
  if (action.opcode == 7 || action.opcode == 47) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size()) {
    if (action.opcode == 7) moveSprite(_scene.sprites[action.value - 1], action.x, action.y);
    else offsetSprite(_scene.sprites[action.value - 1], action.x, action.y);
    dirty = true;
   }
   continue;
  }
  if (action.opcode == 16 || action.opcode == 17) {
   if (action.value > 0 && uint(action.value) <= _scene.sprites.size()) {
    _scene.sprites[action.value - 1].visible = action.opcode == 16;
    dirty = true;
   }
   continue;
  }
  if (action.opcode == 35) { _worldMovieCursorBottom = -1; continue; }
  if (action.opcode == 6) { _runner.clear(); quitGame(); return; }
  nextPlace = action.opcode == 51 ? _previousPlace : action.value;
  changePlace = true;
 }
 if (dirty) redrawSprites();
 // Opcode5 writes c8c/c98, and _do_place reloads after command processing.
 // P515/P536 display their staged bitmap in the same pass after the request.
 if (changePlace && !this->changePlace(nextPlace)) warning("Astronomica: cannot enter scene P%d",nextPlace);
}
void AstronomicaEngine::queueBallCommand(int opcode, int value, int frame, int delay, uint32 now) {
 // _pend_command timestamps every generated command independently.
 Command c; c.opcode = opcode; c.delay = delay;
 if (opcode != 49) c.args.push_back(value);
 if (opcode == 15 || opcode == 20) c.args.push_back(frame);
 if (opcode == 20) c.text = "backorbi";
 if (opcode == 23) { c.args.push_back(frame); for (int i = 0; i < 4; ++i) c.args.push_back(0); }
 Script s; s.push_back(c);
 if (!_runner.enqueue(s,now,true)) warning("Astronomica P501 rejected generated command %d",opcode);
}
void AstronomicaEngine::cycleExplosion(int id, int x, int y, uint32 now) {
 Sprite &s = _scene.sprites[id-1]; s.visible = 1; s.renderX = int16(x); s.renderY = int16(y);
 const int count = spriteFrameCount(_scene,id-1);
 for (int frame = 0; frame <= count; ++frame) {
  Command c; c.opcode = frame < count ? 15 : 30; c.args.push_back(id);
  if (frame < count) c.args.push_back(frame);
  c.delay = frame*166; Script sequence; sequence.push_back(c); _runner.enqueue(sequence,now,true);
 }
}
void AstronomicaEngine::onComet(int mode, uint32 now) {
 if (_place == 516 && supportsJupiter(_scene)) {
  applyScriptActions(now); int32 direction = 0, speed = 0;
  _runner.getValue(1,0,direction); _runner.getValue(1,1,speed);
  configureJupiter(_scene,_comet,mode,direction,speed);
  if (!mode) {
   Common::File file; file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("PLACES/P516/MEGAFILE.HYP"))));
   for (int id = 14; id <= 21; ++id) {
    const Frame *frame = staticSpriteFrame(_scene,id-1);
    Graphics::Surface *bmp = file.isOpen() && frame ? decodeSpriteBitmap(file,frame->image,_screen.format) : nullptr;
    if (bmp) { _jupiterWidths[id-14] = bmp->w; _jupiterHeights[id-14] = bmp->h; bmp->free(); delete bmp; }
   }
  }
  redrawSprites(); return;
 }
 if (!supportsComet(_scene,_place)) return;
 applyScriptActions(now);
 int32 values[9] = {};
 const int count = _place == 502 ? 4 : 9;
 for (int i = 0; i < count; ++i) if (!_runner.getValue(1,i,values[i])) return;
 if (mode == 0) displayCometSpeed(_scene,values[2],values[1]);
 else {
  const int next = configureComet(_scene,_comet,values);
  for (int i = 0; i < count; ++i) _runner.defineValue(1,i,values[i]);
  if (next) {
   _runner.blockClicks();
   if (next == 504) playSound(2,now);
   if (next > 0) {
    Command c; c.opcode = 5; c.args.push_back(next); c.delay = 16667;
    Script s; s.push_back(c); _runner.enqueue(s,now,true);
   }
  }
 }
 redrawSprites();
}
void AstronomicaEngine::onBall(int mode, uint32 now) {
 if (_place != 501 || _scene.sprites.size() != 27) return;
 int32 scenario = 0, state = 0, misses = 0;
 _runner.getValue(1,0,scenario); _runner.getValue(1,1,state); _runner.getValue(1,2,misses);
 const int distance = _scene.sprites[24].renderX-_scene.sprites[25].x;
 auto queue = [&](int opcode, int value, int frame, int delay) { queueBallCommand(opcode,value,frame,delay,now); };
 if (mode == 0 && state == 1) {
  _runner.defineValue(1,1,2);
  if (distance > 40 && distance < 100) {
   playSound(8,now); _runner.defineValue(1,2,0);
   if (scenario == 1 || scenario == 4 || scenario == 5) startBall(_scene.sprites[24],_ball,scenario);
   if (scenario == 1) {
    queue(30,25,0,2000); queue(15,26,2,0); queue(15,26,0,6667);
   } else if (scenario == 5) {
    queue(30,25,0,5000); queue(15,26,2,0); queue(15,26,3,5000); queue(15,26,0,6000);
    const int delays[] = {833,1667,2500,3333,4167};
    for (int i = 0; i < 5; ++i) queue(15,25,4-i,delays[i]);
   } else if (scenario == 4) {
    queue(30,25,0,16000); queue(23,7,3,16000); queue(15,26,2,0);
   }
  } else {
   queue(30,25,0,500); playSound(11,now); queue(15,26,3,500); queue(15,26,0,2500);
   _runner.defineValue(1,1,0); onBall(4,now);
  }
 } else if (mode == 1 && state == 2) {
  _runner.defineValue(1,1,3);
  if (scenario == 4) {
   queue(30,25,0,0); _runner.defineValue(1,1,0);
   if (distance > -30 && distance < 60) {
    queue(15,26,9,500); queue(15,26,10,1000); queue(15,26,11,1500);
    _mixer->stopHandle(_soundHandle); playSound(6,now); _runner.defineValue(1,3,1);
   } else { queue(15,26,3,833); queue(15,26,0,2500); }
  }
 } else if (mode == 2 && state == 1) {
  _runner.defineValue(1,1,0); queue(30,25,0,0);
  if (misses != 2) playSound(11,now);
  onBall(4,now);
 } else if (mode == 3 && state == 2 && scenario == 4) {
  _runner.defineValue(1,1,0); queue(15,26,3,833); queue(15,26,0,2500);
 } else if (mode == 4) {
  if (misses != 2) _runner.defineValue(1,2,misses+1);
  else {
   for (int i = 0; i < 3; ++i) _runner.defineValue(1,i,0);
   playSound(12,now); queue(20,0,0,833); queue(49,0,0,833);
   queue(27,1,0,2500); queue(17,26,0,2500); queue(17,27,0,2500);
  }
 }
}
void AstronomicaEngine::onProbe(int mode, int id) {
 if (_place != 522) return;
 if (mode == 1) { launchProbe(_scene,_probe); return; }
 configureProbe(_scene,_probe,id);
 Common::File file;
 file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("PLACES/P522/MEGAFILE.HYP"))));
 const Frame *frame = staticSpriteFrame(_scene,id-1);
 Graphics::Surface *bmp = file.isOpen() && frame ? decodeSpriteBitmap(file,frame->image,_screen.format) : nullptr;
 if (bmp) { _probe.widths[id-15] = bmp->w; _probe.heights[id-15] = bmp->h; bmp->free(); delete bmp; }
 if (id == 17) _probeAssetsValid = validProbeSaveScene(_scene) && universeFileIdentity(ConfMan.getPath("path").join("PLACES/P522/MEGAFILE.HYP"),483379,0x6015e215U);
}
void AstronomicaEngine::animateSpritesAt(uint32 now) {
 if (!ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") || !supportsSpriteLayers(_scene)) return;
 bool dirty = false;
 Common::File motionFile;
 for (int layer = 1; layer <= _scene.layers; ++layer)
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  Sprite &s = _scene.sprites[i];
  if (s.layer != layer) continue;
  if (advanceSpriteFrame(s, spriteFrameCount(_scene,i), now) && s.visible) dirty = true;
  if (s.standardMotion && s.autoMove) {
   if (!motionFile.isOpen()) motionFile.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP",_place)))));
   const Frame *frame = staticSpriteFrame(_scene,i);
   Graphics::Surface *bmp = motionFile.isOpen() && frame ? decodeSpriteBitmap(motionFile,frame->image,_screen.format) : nullptr;
   if (bmp) {
    if (_place == 516 && i == 12) {
     const int x = int16(s.renderX+16)-48, y = int16(s.renderY+16)-48;
     const int result = advanceJupiter(_scene,_jupiterWidths,_jupiterHeights,bmp->w,bmp->h,now);
     dirty = result != 0 || dirty;
     if (result & 6) _runner.defineValue(1,2,1);
     for (int bit = 2; bit <= 4; bit *= 2) if (result & bit) { cycleExplosion(23,x,y,now); playSound(9,now); }
    } else if (_place == 516 && _comet.kind[i]) {
     dirty = advanceComet(_scene,_comet,i,bmp->w,bmp->h,0,now) || dirty;
    } else if (supportsComet(_scene,_place) && _comet.kind[i]) {
     int32 target = 0; _runner.getValue(1,2,target);
     dirty = advanceComet(_scene,_comet,i,bmp->w,bmp->h,target,now) || dirty;
     if (_comet.sound >= 0) playSound(_comet.sound,now);
     if (_comet.explosion) {
      const int id = _comet.explosion;
      Sprite &explosion = _scene.sprites[id-1];
      explosion.visible = 1; explosion.renderX = 320; explosion.renderY = 160;
      const int frames = spriteFrameCount(_scene,id-1);
      for (int frameIndex = 0; frameIndex <= frames; ++frameIndex) {
       Command c; c.opcode = frameIndex < frames ? 15 : 30; c.args.push_back(id);
       if (frameIndex < frames) c.args.push_back(frameIndex);
       c.delay = frameIndex*166; Script sequence; sequence.push_back(c); _runner.enqueue(sequence,now,true);
      }
     }
    } else if (_place == 501 && i == 24 && _ball.scenario) {
     const int result = advanceBall(s,_ball,bmp->w,bmp->h,now);
     dirty = result != 0 || dirty;
     if (result == 2) {
      queueBallCommand(15,26,4,0,now); queueBallCommand(15,26,5,833,now); queueBallCommand(15,26,6,1667,now);
     }
    } else if (_place == 513 && i == 31) {
     int32 setting = 0; _runner.getValue(1,0,setting);
     dirty = advancePhoton(_scene,setting,now) || dirty;
    } else if (_place == 518 && s.planetMotion) {
     const int result = advancePlanet(s,_scene.sprites[8],bmp->w,bmp->h,now);
     dirty = result != 0 || dirty;
     if (result >= 2) {
      playSound(result == 3 ? 10 : 9,now);
      if (result == 2 && s.x >= 1 && s.x <= 9) {
       int32 mask = 0;
       if (_runner.getValue(1,1,mask)) _runner.defineValue(1,1,int32(uint32(mask)-(1U << (s.x-1))));
      }
     }
    } else if (_place == 522 && i >= 14 && i <= 16) {
     int32 state = 0; _runner.getValue(1,1,state);
     dirty = advanceProbe(_scene,_probe,i,state,now) || dirty;
     _runner.defineValue(1,1,state);
    } else if (_place == 514) {
     const bool wasMoving = s.autoMove;
     dirty = advanceRendezvous(_scene,i,bmp->w,bmp->h,now) || dirty;
     if (i == 13 && wasMoving && !s.autoMove) {
      _runner.defineValue(1,7,1);
      Script exit; Command go; go.opcode = 5; go.args.push_back(388); go.delay = 1000; exit.push_back(go);
      _runner.enqueue(exit,now,true);
     }
    } else if (_place == 526 && s.orbitMotion) {
     int32 scenario = 0; _runner.getValue(1,2,scenario);
     dirty = advanceOrbit(_scene,i,bmp->w,bmp->h,scenario,now) || dirty;
    } else if (advanceSpriteMove(s,bmp->w,bmp->h,now) && s.visible) dirty = true;
    bmp->free(); delete bmp;
   }
  }
 }
 if (_place == 522 && _probe.expired) { debug("Probe audit expiry: %u %d %u",now,_probe.year,uint(_probe.expired)); changePlace(388); return; }
 if (_place == 537 && _rocket.kind != RocketMotion::kStopped) {
  int32 setting = 0;
  _runner.getValue(1,0,setting);
  const int result = advanceRocket(_scene,_rocket,setting,now);
  dirty = result != 0 || dirty;
  if (result == 3) {
   int32 completed = 0;
   if (_runner.getValue(0,36,completed) && !completed) onPuzzleSuccess(now);
   _runner.defineValue(0,36,1); // _fxm_move_rocket 3:1a61-1a80, game+0x9a.
  }
 }
 if (dirty) redrawSprites();
}
void AstronomicaEngine::stepPlace(int direction) {
 for (int id = _place + direction; id >= 0 && id <= 537; id += direction)
  if (changePlace(id)) return;
}
bool AstronomicaEngine::verifyContinuousMovies() {
 bool ok = true;
 ConfMan.setBool("astronomica_audio",true);
 ConfMan.setBool("astronomica_animation",true);
 ConfMan.setBool("astronomica_entry_scripts",false);
 const int requestedPlace = ConfMan.hasKey("astronomica_movie_place") ? ConfMan.getInt("astronomica_movie_place") : 0;
 const int moviePlaces[] = {512,525,527,529};
 for (int place : moviePlaces) {
  if (requestedPlace && place != requestedPlace) continue;
  ok = loadPlace(place) && ok;
  if (!_movie) return false;
  if (_scene.introSound) {
   Audio::SeekableAudioStream *intro = openSound(_scene.introSoundId);
   if (!intro) return false;
   const uint32 introMs = intro->getLength().msecs(); delete intro;
   const uint32 started = _system->getMillis();
   const uint soundCount = _soundsStarted;
   ConfMan.setBool("astronomica_entry_scripts",true);
   ok = loadPlace(place) && ok;
   ConfMan.setBool("astronomica_entry_scripts",false);
   const uint32 elapsed = _system->getMillis()-started;
   const bool introOK = _soundsStarted == soundCount+1 && _lastSound == _scene.introSoundId &&
    !_mixer->isSoundHandleActive(_soundHandle) && elapsed+250 >= introMs;
   ok = introOK && ok;
   debug("Astronomica movie-scene P%d introduction: %s (%u ms, expected at least %u)",place,introOK ? "PASS" : "FAIL",elapsed,introMs);
   _runner.clear();
  }
  const Script original = place == 525 ? _scene.mouseRects[0].click : _scene.scripts[place == 529 || place == 512 ? 2 : 0];
  Command originalPlay;
  for (uint i = 0; i < original.size(); ++i)
   if (original[i].opcode == 3 || (place == 512 && original[i].opcode == 23 && original[i].args[0] == 24 && original[i].args[1] == 1)) { originalPlay = original[i]; break; }
  if (originalPlay.opcode != 3 && originalPlay.opcode != 23) return false;
  uint segments = 0;
  for (uint i = 0; i < original.size(); ++i) {
   if (original[i].opcode != 37) continue;
   Script program;
   Command segment = original[i], play = originalPlay;
   segment.delay = play.delay = 0; program.push_back(segment); program.push_back(play);
   const uint32 expectedMs = uint32(uint64(segment.args[2])*1000/_movie->getTimeScale());
   const uint initialFrames = _movieFramesDrawn;
   const uint32 started = _system->getMillis();
   ok = _runner.start(program,scriptClock(),true) && ok; applyScriptActions(scriptClock());
   runScriptsAt(scriptClock());
   if (!_moviePlaying) return false;
   while (_moviePlaying && !shouldQuit() && uint32(_system->getMillis()-started) < expectedMs+5000) {
    Common::Event event;
    while (_eventMan->pollEvent(event)) if (event.type == Common::EVENT_QUIT) quitGame();
    updateMovie(); _system->updateScreen(); _system->delayMillis(5);
   }
   const uint32 elapsed = _system->getMillis()-started;
   const uint frames = _movieFramesDrawn-initialFrames;
   bool segmentOK = !_moviePlaying && !shouldQuit() && frames > 20 && elapsed+250 >= expectedMs && elapsed <= expectedMs+1500;
   // An ordinary sprite repaint retains the completed segment's pixels.
   redrawSprites();
   for (int y = 0; y < _movieFrame.h; ++y) for (int x = 0; x < _movieFrame.w; ++x)
    segmentOK = _screen.getPixel(x+_movieX,y+_movieY) == _movieFrame.getPixel(x,y) && segmentOK;
   if (place == 525) {
    segmentOK = stageBackgroundImage("sky_b",0,0) && segmentOK;
    displayBackgroundImage(); segmentOK = !_movieFrame.w && segmentOK;
   }
   ok = segmentOK && ok;
   debug("Astronomica continuous P%d segment %u: %s (%u frames, %u ms, expected %u)",place,segments,segmentOK ? "PASS" : "FAIL",frames,elapsed,expectedMs);
   ++segments;
  }
  ok = segments == uint(place == 512 ? 6 : 4) && ok;
 }
 debug("Astronomica continuous movie verification: %s (full original segments, no seek acceleration)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyVariantPuzzles() {
 const int places[] = {506,531,532,533,534,535};
 const int targets[6][5] = {{12,13,14,0,0},{10,11,12,14,0},{12,10,11,0,0},{9,10,11,0,0},{14,15,16,17,18},{9,10,11,0,0}};
 const int answers[6][5] = {{3,4,5,0,0},{1,2,3,5,0},{1,3,4,0,0},{1,2,3,0,0},{3,4,5,6,7},{1,2,3,0,0}};
 bool ok = true;
 for (uint route = 0; route < 7; ++route) {
  if (route < 6) _runner.resetGlobals();
  _runner.seedRandom(501+route);
  ok = loadPlace(places[route%6]) && _runner.variantRound() == 0 && ok;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto inGroup = [&]() { return _place == 506 || (_place >= 531 && _place <= 535); };
  auto settle = [&]() {
   for (uint pass = 0; pass < 3000 && inGroup() && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto clickSprite = [&](uint id) {
   if (!inGroup() || id < 1 || id > _scene.sprites.size()) return false;
   const Sprite &s = _scene.sprites[id-1];
   int hitX = -1, hitY = -1;
   // Find an exposed point within the original rectangle, then use the
   // ordinary input path. Answers above are independent original fixtures.
   for (int y = MAX(0,int(s.renderY)); y < 480 && hitX < 0; y += 8)
    for (int x = MAX(0,int(s.renderX)); x < 640; x += 8)
     if (spriteAt(x,y) == int(id)-1) { hitX = x; hitY = y; break; }
   if (hitX < 0) return false;
   clickAtTime(hitX,hitY,now); return settle();
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 2 && settle() && ok;
  uint seen = 0;
  for (uint stage = 0; stage < 4 && inGroup(); ++stage) {
   int variant = _place == 506 ? 0 : _place-530;
   if (stage) { ok = !(seen & (1U << variant)) && ok; seen |= 1U << variant; }
   ok = _runner.variantRound() == stage && ok;
   const int oldPlace = _place;
   if (route == 0 && stage == 0) {
    int32 mask = -1;
    ok = clickSprite(5) && clickSprite(12) && _runner.getValue(1,0,mask) && mask == 0 && ok;
   }
   for (uint item = 0; item < 5 && targets[variant][item] && _place == oldPlace; ++item) {
    ok = clickSprite(answers[variant][item]+4) && clickSprite(targets[variant][item]) && ok;
   }
   debug("Astronomica variant route %u stage %u: %s (P%d -> P%d, round %u)",route,stage,ok ? "PASS" : "FAIL",oldPlace,_place,_runner.variantRound());
  }
  int32 solved = -1;
  ok = _place == 519 && _runner.variantRound() == 0 && _runner.getValue(0,23,solved) && solved == 1 &&
   _puzzlesCompleted == completed+uint(route < 6) && _lastSound == 922 && ok;
 }
 _runner.resetGlobals(); ok = loadPlace(506) && ok;
 clickAtTime(24,417,0);
 for (uint32 now = 0; now < 5000 && _place == 506; now += 20) runScriptsAt(now);
 int32 solved = -1;
 ok = _place == 281 && _runner.getValue(0,23,solved) && solved == 0 && _runner.variantRound() == 0 && ok;
 debug("Astronomica variant puzzle verification: %s (six starting scenes, three nonrepeating variants, repeat success, unsolved exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP524Puzzle() {
 bool ok = true;
 const char *images[] = {"viewio","viewmars","viewmerc","viewmira","viewplut","viewtita","viewtrit","viewvenu","viewmoon"};
 for (int route = 0; route < 4; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(143+route);
  _runner.defineValue(0,29,1); // Original puzzle-entry prerequisite, including help return.
  if (route == 1) _runner.defineValue(0,40,1);
  if (!loadPlace(524)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto settle = [&]() {
   for (int tick = 0; tick < 6000 && _place == 524 && _runner.pendingCount(); ++tick) {
    runScriptsAt(now); animateSpritesAt(now); now += 20;
   }
   return _place != 524 || (!_runner.pendingCount() && !_runner.clicksBlocked());
  };
  auto press = [&](int index) {
   if (_place != 524) return false;
   const Sprite &s = _scene.sprites[index]; int x = s.renderX+10, y = s.renderY+10;
   if (spriteAt(x,y) != index) return false;
   clickAtTime(x,y,now); return settle();
  };
  auto checkImage = [&](int scenario) {
   Graphics::Surface *image = openBackgroundImage(images[scenario-1]);
   if (!image) return false;
   bool same = true;
   for (int y = 0; y < image->h; ++y) for (int x = 0; x < image->w; ++x)
    same = _background.getPixel(x,y) == image->getPixel(x,y) && same;
   image->free(); delete image; return same;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 5 && settle() && ok;
  uint seen = 0; int answers = 0;
  if (route == 3) ok = press(28) && ok;
  else while (_place == 524 && answers < 10) {
   int32 scenario = 0,mask = 0,errors = 0;
   if (!_runner.getValue(1,0,scenario) || scenario < 1 || scenario > 9) return false;
   ok = checkImage(scenario) && ok;
   if (route < 2) {
    ok = !(seen & (1U << (scenario-1))) && ok; seen |= 1U << (scenario-1);
    if (route == 0 && answers == 3) {
     _runner.getValue(1,1,mask); _runner.getValue(1,3,errors);
     ok = press(30) && _place == 408 && ok;
     if (spriteAt(33,426) != 0) return false;
     clickAtTime(33,426,now);
     for (int tick = 0; tick < 100 && _place == 408; ++tick) { runScriptsAt(now); now += 20; }
     if (_place != 524 || _runner.clicksBlocked()) return false;
     ok = _runner.enqueueStartup(_scene.scripts,now,true) == 5 && settle() && ok;
     int32 restored = -1;
     ok = _runner.getValue(1,0,restored) && restored == scenario &&
      _runner.getValue(1,1,restored) && restored == mask &&
      _runner.getValue(1,3,restored) && restored == errors && checkImage(scenario) && ok;
    }
   }
   ok = press(route == 2 ? 0 : scenario == 9 ? 0 : scenario) && ok;
   ++answers;
  }
  int32 solved = -1;
  ok = _place == 117 && _runner.getValue(0,40,solved) && solved == int(route < 2) &&
   _puzzlesCompleted == completed+uint(route == 0) && ok;
  if (route < 2) ok = answers == 9 && seen == 511 && ok;
  if (route == 2) ok = answers == 3 && ok;
  debug("Astronomica P524 route %d: %s (%d answers)",route,ok ? "PASS" : "FAIL",answers);
 }
 debug("Astronomica P524 interaction verification: %s (nine images/answers, help state restored, repeated success, three errors, voluntary exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyGameState() {
 struct Context : ScriptRunner::GameStateHandler {
  GameStateContext value = {31,true,false,0};
  GameStateContext gameStateContext() const override { return value; }
 } context;
 auto command = [](int key,int local,int mode,int selector) {
  Script script; Command c; c.opcode = 23;
  for (int arg : {26,key,local,mode,selector,0}) c.args.push_back(arg);
  script.push_back(c); return script;
 };
 uint32 hash = 2166136261U; uint cases = 0; bool ok = true;
 for (int key = 1; key <= 14; ++key) for (int local : {0,3,99})
  for (int mode = 0; mode <= 1; ++mode) for (int selector = 0; selector < 29; ++selector) {
   ScriptRunner runner; runner.setGameStateHandler(&context);
   for (int i = 0; i < 100; ++i) {
    runner.defineValue(0,i,0x12340000+i); runner.defineValue(1,i,0x45670000+i);
   }
   ok = runner.start(command(key,local,mode,selector),0,true) && ok;
   for (int scope : {1,0}) for (int i = 0; i < 100; ++i) {
    int32 value = 0; ok = runner.getValue(scope,i,value) && ok;
    hash = (hash ^ uint32(value))*16777619U;
   }
   ++cases;
  }
 ok = cases == 2436 && hash == 0xd253e90aU && ok;
 debug("Astronomica game state original comparison: %s (%u cases, %08x)",ok ? "PASS" : "FAIL",cases,hash);
 hash = 2166136261U;
 for (int resume : {0,1,2}) for (int help : {0,1})
  for (int bytes : {0,1649999,1650000,1650001,2399999,2400000,2400001}) {
   context.value = {31,resume != 0,help != 0,bytes};
   for (int key : {13,14}) {
    ScriptRunner runner; runner.setGameStateHandler(&context);
    ok = runner.start(command(key,0,0,0),0,true) && ok;
    int32 value = -1; ok = runner.getValue(1,0,value) && ok;
    hash = (hash ^ uint32(value))*16777619U;
   }
  }
 ok = hash == 0x662a3a5aU && ok;
 ScriptRunner invalid;
 ok = !invalid.start(command(1,0,0,0),0,true) &&
  !invalid.start(command(7,0,1,0),0,true) &&
  !invalid.start(command(7,-1,1,0),0,true) &&
  !invalid.start(command(7,100,1,0),0,true) && ok;
 debug("Astronomica game state boundary verification: %s (42 resume/memory cases, missing context/value and local bounds)",ok ? "PASS" : "FAIL");
 int32 saved[100] = {}; for (int i = 0; i < 100; ++i) _runner.getValue(0,i,saved[i]);
 const uint completed = _puzzlesCompleted;
 _runner.resetGlobals(); _puzzlesCompleted = 26;
 uint32 now = 0;
 auto settle = [&]() {
  for (int tick = 0; tick < 1500 && _runner.pendingCount(); ++tick) { runScriptsAt(now); now += 10; }
  return !_runner.pendingCount() && !_runner.clicksBlocked();
 };
 auto enter = [&](int place) {
  if (!loadPlace(place)) return false;
  now = 0;
  return _runner.enqueueStartup(_scene.scripts,0,true) == _scene.scripts.size() && settle();
 };
 auto press = [&](int x,int y) { clickAtTime(x,y,now); return settle(); };
 int32 value = 0;
 // Original cabinet control, then item pickup; revisit both to prove persistence.
 ok = enter(359) && press(268,162) && _runner.getValue(0,52,value) && value == 1 && ok;
 ok = enter(352) && press(210,282) && _runner.getValue(0,53,value) && value == 1 && ok;
 ok = enter(352) && _runner.getValue(1,1,value) && value == 1 && _scene.sprites[0].visible && ok;
 ok = enter(359) && _runner.getValue(1,1,value) && value == 1 && _scene.sprites[0].selectedFrame == 1 && ok;
 debug("Astronomica game state stage cabinet-item: %s (P%d, value %d, sound %d)",ok ? "PASS" : "FAIL",_place,value,_lastSound);
 // Unlocking the original world door writes global59 and starts P426.
 ok = enter(35) && press(200,150) && _place == 426 && _lastSound == 904 &&
  _runner.getValue(0,59,value) && value == 1 && ok;
 ok = enter(85) && _runner.getValue(1,0,value) && value == 1 && press(200,150) && _place == 423 && ok;
 debug("Astronomica game state stage world-door: %s (P%d, value %d, sound %d)",ok ? "PASS" : "FAIL",_place,value,_lastSound);
 // Completion counter affects the original gate; it is read at click time.
 _puzzlesCompleted = 24; ok = enter(98) && press(33,375) && _place == 98 && _lastSound == 2 && ok;
 _puzzlesCompleted = 25; _runner.defineValue(0,29,1);
 ok = press(33,375) && _place == 529 && _lastSound == 1 && ok;
 debug("Astronomica game state stage counter-gate: %s (P%d, value %d, sound %d)",ok ? "PASS" : "FAIL",_place,value,_lastSound);
 // The original hub reads eight independent puzzle-completion globals.
 const int flags[] = {20,24,34,30,37,32,27,38};
 for (int i = 0; i < 8; ++i) _runner.defineValue(0,flags[i],i%2);
 ok = enter(388) && ok;
 for (int i = 0; i < 8; ++i)
  ok = _runner.getValue(1,i+1,value) && value == i%2 && _scene.sprites[i+1].selectedFrame == i%2 && ok;
 debug("Astronomica game state stage hub-flags: %s (P%d, value %d, sound %d)",ok ? "PASS" : "FAIL",_place,value,_lastSound);
 // World keypad P407: wrong-key reset, then the original seven-key sequence.
 _runner.defineValue(0,55,0); ok = enter(407) && ok;
 auto rectPress = [&](int id) {
  const MouseRect &r = _scene.mouseRects[id];
  return press((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2);
 };
 ok = rectPress(0) && rectPress(8) && rectPress(9) && _runner.getValue(1,2,value) && value == 0 && ok;
 const int keys[] = {8,8,8,7,12,10,6};
 for (int key : keys) ok = rectPress(key) && ok;
 ok = _place == 407 && _runner.getValue(0,55,value) && value == 1 && ok;
 debug("Astronomica P407 keypad verification: %s (wrong-key reset, seven-key sequence, global55)",ok ? "PASS" : "FAIL");
 // P422 has a 27-second exit; exercise the sequence while that timer is live.
 _runner.defineValue(0,56,0); ok = loadPlace(422) && ok; now = 0;
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 2 && ok;
 for (; now < 100; now += 10) runScriptsAt(now);
 const int points[][2] = {{370,120},{470,78},{370,78},{470,162}};
 for (const auto &point : points) {
  clickAtTime(point[0],point[1],now);
  const uint32 end = now+1000;
  for (; now < end && _place == 422; now += 10) runScriptsAt(now);
 }
 for (int tick = 0; tick < 1500 && _place == 422; ++tick) { runScriptsAt(now); now += 10; }
 ok = _place == 183 && _runner.getValue(0,56,value) && value == 1 && now < 27000 && ok;
 debug("Astronomica P422 keypad verification: %s (four-key sequence before timed exit, global56)",ok ? "PASS" : "FAIL");
 // Credits update global61 through their formerly rejected first script.
 _runner.defineValue(0,61,0); ok = loadPlace(425) && ok;
 ok = _runner.start(_scene.scripts[0],0,true) && ok;
 now = 0; ok = settle() && _runner.getValue(0,61,value) && value == 1 && ok;
 debug("Astronomica game state stage credits: %s (global61 %d)",ok ? "PASS" : "FAIL",value);
 _puzzlesCompleted = completed;
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,saved[i]);
 ok = loadPlace(103) && ok;
 debug("Astronomica game state interaction verification: %s (cabinet, persistent item, world door, counter gate, hub flags, credit state)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyTransitions() {
 uint32 hash = 2166136261U; uint cases = 0;
 auto compare = [&](int previous, int requested, const int32 *globals) {
  const PlaceTransition r = resolvePlaceTransition(previous,requested,globals);
  for (int32 value : {int32(r.destination),r.permit,int32(r.failureVoice),int32(r.immediateSound)})
   hash = (hash ^ uint32(value))*16777619U;
  ++cases;
 };
 const int destinations[] = {-1,117,408,409,500,501,502,503,504,506,507,508,513,515,520,531,535,536,537,538,599,600};
 const int extra[] = {500,538,599,600,408,409,103};
 for (int index = 0; index < 44; ++index) {
  const int previous = index < 37 ? 501+index : extra[index-37];
  for (int destination : destinations) for (int pattern = -2; pattern < 47; ++pattern) {
   int32 globals[100];
   for (int i = 0; i < 100; ++i) globals[i] = pattern == -2 || i == pattern;
   compare(previous,destination,globals);
  }
 }
 const int pairs[][2] = {{307,414},{271,298},{284,289},{324,329},{101,110},{120,144},
  {177,182},{139,151},{160,168},{208,117},{387,117}};
 for (const auto &pair : pairs) for (int reverse = 0; reverse < 2; ++reverse)
  for (int permit = -1; permit <= 2; ++permit) {
   int32 globals[100] = {}; globals[57] = permit;
   compare(pair[reverse],pair[1-reverse],globals);
  }
 bool ok = hash == 0x03a3e23bU && cases == 47520;
 debug("Astronomica transition original comparison: %s (%u cases, %08x)",ok ? "PASS" : "FAIL",cases,hash);
 int32 savedGlobals[100] = {};
 for (int i = 0; i < 100; ++i) _runner.getValue(0,i,savedGlobals[i]);
 _runner.resetGlobals();
 for (int index = 0; index < 9; ++index) {
  const auto &pair = pairs[index];
  _runner.defineValue(0,57,0);
  ok = loadPlace(pair[0]) && changePlace(pair[1]) && _place == 429 && ok;
  _runner.defineValue(0,57,1);
  ok = loadPlace(pair[0]) && changePlace(pair[1]) && _place == pair[1] && ok;
  int32 permit = -1; ok = _runner.getValue(0,57,permit) && permit == 0 && ok;
 }
 ok = loadPlace(103) && changePlace(523) && _place == 103 && _lastSound == 910 && ok;
 ok = changePlace(513) && _place == 513 && ok;
 _runner.defineValue(0,29,1);
 ok = loadPlace(103) && changePlace(523) && _place == 523 && ok;
 ok = changePlace(117) && _place == 117 && _lastSound == 911 && ok;
 _runner.defineValue(0,39,1);
 ok = loadPlace(523) && ok;
 const uint before = _soundsStarted;
 ok = changePlace(117) && _soundsStarted == before && ok;
 ok = loadPlace(502) && ok;
 const uint beforeGroup = _soundsStarted;
 ok = changePlace(503) && _place == 503 && _soundsStarted == beforeGroup && ok;
 uint routes = 0;
 const int starts[] = {30,357,810,1200,1804}, lengths[] = {187,365,280,503,342};
 const int delays[] = {7500,13000,10000,17500,13000};
 for (uint seed = 0; seed < 100 && routes != 31; ++seed) {
  _runner.seedRandom(seed); ok = loadPlace(429) && _movie && ok;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  for (uint32 now = 0; now < 100; now += 10) runScriptsAt(now);
  int32 choice = 0;
  if (!_runner.getValue(1,0,choice) || choice < 1 || choice > 5 || !_movie) return false;
  const int index = choice-1; routes |= 1U << index;
  ok = _moviePlaying && _movieX == 200 && _movieY == 150 &&
   _movie->getEndTime() == Audio::Timestamp(0,starts[index]+lengths[index],30) && ok;
  updateMovie(); ok = _movieFramesDrawn > 0 && ok;
  for (uint32 now = 100; now < uint(delays[index])+300 && _place == 429; now += 10) runScriptsAt(now);
  ok = _place == 427 && _movie && ok;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  const uint beforeFrame = _movieFramesDrawn;
  runScriptsAt(0); updateMovie(); ok = _moviePlaying && _movieFramesDrawn > beforeFrame && ok;
  runScriptsAt(16999); ok = _place == 427 && ok;
  runScriptsAt(17000); ok = _place == 425 && ok;
 }
 ok = routes == 31 && ok;
 for (int place : {426,428}) {
  ok = loadPlace(place) && _movie && _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  const uint beforeFrame = _movieFramesDrawn;
  runScriptsAt(0); updateMovie(); ok = _moviePlaying && _movieFramesDrawn > beforeFrame && ok;
  const uint32 delay = place == 426 ? 12000 : 10000;
  runScriptsAt(delay-1); ok = _place == place && ok;
  runScriptsAt(delay); ok = _place == (place == 426 ? 32 : 423) && ok;
 }
 ok = loadPlace(425) && ok;
 // Original bookkeeping now runs alongside the seven image changes and exit.
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 9 && ok;
 for (int card = 2; card <= 8; ++card) {
  const uint32 now = (card-1)*17000;
  runScriptsAt(now); runScriptsAt(now);
  Graphics::Surface *expected = openBackgroundImage(Common::String::format("CRD%d",card));
  if (!expected) return false;
  ok = screenRGBHash(_background) == screenRGBHash(*expected) && ok;
  expected->free(); delete expected;
 }
 runScriptsAt(135999); ok = _place == 425 && ok;
 runScriptsAt(136000); ok = _place == 432 && ok;
 debug("Astronomica credits images verification: %s (seven timed images, bookkeeping and P432 exit)",ok ? "PASS" : "FAIL");
 debug("Astronomica denial interludes verification: %s (five segments, decoded frames, P429 to P427 to P425)",ok ? "PASS" : "FAIL");
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,savedGlobals[i]);
 ok = loadPlace(103) && ok;
 debug("Astronomica transition integration verification: %s (nine gates, permit consumption, prerequisite, entry exception, exit voices, continuation)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifySaves() {
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") >= 0) {
  int32 value = 0;
  if (_place != 103 || _puzzlesCompleted != 31 || !_runner.getValue(0,99,value) ||
      uint32(value) != (99U*0x01020304U ^ 0xa5a5a5a5U)) return false;
  debug("Astronomica startup save verification: PASS (scene, count and global99 restored before test setup)");
 }
 const uint oldCompleted = _puzzlesCompleted;
 _runner.resetGlobals();
 if (!loadPlace(103) || !canSaveGameStateCurrently()) return false;
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,int32(uint32(i)*0x01020304U ^ 0xa5a5a5a5U));
 _puzzlesCompleted = 31;
 Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
 bool ok = saveGameStream(&out).getCode() == Common::kNoError && out.size() == 424;
 auto restore = [&](const byte *data, uint size) {
  Common::MemoryReadStream input(data,size); return loadGameStream(&input).getCode() == Common::kNoError;
 };
 _runner.resetGlobals(); _puzzlesCompleted = 0; ok = loadPlace(117) && ok;
 ok = restore(out.getData(),out.size()) && _place == 103 && _puzzlesCompleted == 31 && ok;
 for (int i = 0; i < 100; ++i) {
  int32 value = 0; ok = _runner.getValue(0,i,value) && uint32(value) == (uint32(i)*0x01020304U ^ 0xa5a5a5a5U) && ok;
 }
 // Every truncated length and every one-byte payload corruption must fail
 // without changing the active scene or already restored progress.
 for (uint size = 0; size < out.size(); ++size) ok = !restore(out.getData(),size) && _place == 103 && _puzzlesCompleted == 31 && ok;
 Common::Array<byte> damaged; damaged.resize(out.size());
 for (uint offset = 0; offset < out.size(); ++offset) {
  memcpy(&damaged[0],out.getData(),out.size()); damaged[offset] ^= 1;
  ok = !restore(&damaged[0],damaged.size()) && _place == 103 && _puzzlesCompleted == 31 && ok;
 }
 // Version 1 inactive saves remain readable.
 Common::Array<byte> legacy; legacy.resize(420);
 memcpy(&legacy[0],out.getData(),416); WRITE_LE_UINT32(&legacy[4],1);
 uint32 legacyHash = 2166136261U;
 for (int i = 0; i < 102; ++i) legacyHash = (legacyHash ^ READ_LE_UINT32(&legacy[8+4*i]))*16777619U;
 WRITE_LE_UINT32(&legacy[416],legacyHash);
 ok = restore(&legacy[0],legacy.size()) && ok;
 // Valid checksum with an unsupported puzzle destination still fails.
 memcpy(&damaged[0],out.getData(),out.size()); WRITE_LE_UINT32(&damaged[8],523);
 uint32 hash = 2166136261U;
 for (int i = 0; i < 103; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+4*i]))*16777619U;
 WRITE_LE_UINT32(&damaged[420],hash);
 ok = !restore(&damaged[0],damaged.size()) && _place == 103 && ok;
 if (ConfMan.hasKey("astronomica_verify_save_files") && ConfMan.getBool("astronomica_verify_save_files")) {
  ok = saveGameState(1,"Astronomica regression").getCode() == Common::kNoError && ok;
  _runner.resetGlobals(); _puzzlesCompleted = 0; ok = loadPlace(117) && ok;
  ok = loadGameState(1).getCode() == Common::kNoError && _place == 103 && _puzzlesCompleted == 31 && ok;
  debug("Astronomica save file verification: %s (ScummVM slot and extended metadata)",ok ? "PASS" : "FAIL");
  Common::Event close; close.type = Common::EVENT_KEYDOWN; close.kbd.keycode = Common::KEYCODE_ESCAPE;
  _eventMan->pushEvent(close); openMainMenuDialog();
  ok = _place == 103 && !_clockPaused && ok;
  debug("Astronomica save menu verification: %s (open and close standard ScummVM menu)",ok ? "PASS" : "FAIL");
 }
 ok = loadPlace(523) && !canSaveGameStateCurrently() && ok;
 Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);
 ok = saveGameStream(&denied).getCode() == Common::kWritingFailed && denied.size() == 0 && ok;
 pauseEngineIntern(true); const uint32 paused = scriptClock();
 _system->delayMillis(25); ok = scriptClock() == paused && _movie && _movie->isPaused() && ok;
 pauseEngineIntern(false); ok = !_movie->isPaused() && scriptClock()-paused < 20 && ok;
 _puzzlesCompleted = oldCompleted; _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica save verification: %s (100 globals, count, 424 truncations, 424 corruptions, destination guard, pause)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP508Saves() {
 bool ok = true;
 auto fingerprint = [&]() {
  Common::Array<uint32> state; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  hash = (hash ^ _puzzlesCompleted)*16777619U;
  // Program epochs may differ after a later scene transition. All values,
  // metadata and the full RNG must match independently of wall-clock speed.
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  return (hash ^ screenRGBHash(_screen))*16777619U;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 2000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 50; }
  return !_runner.pendingCount() && !_runner.clicksBlocked();
 };
 auto answer = [&](bool wrong, uint32 &now) {
  int32 choice = 0; if (_place != 508 || !_runner.getValue(1,0,choice)) return false;
  const bool upper = (choice > 12) != wrong;
  clickAtTime(upper ? 223 : 222,upper ? 188 : 253,now);
  if (canSaveGameStateCurrently()) return false;
  return settle(now);
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 2) {
  int32 right = 0, wrong = 0;
  ok = canSaveQuestion() && _runner.getValue(1,4,right) && right == 1 && _runner.getValue(1,3,wrong) && wrong == 1;
  debug("Astronomica P508 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock();
  for (uint n = 0; n < 7 && ok; ++n) ok = answer(false,now) && ok;
  int32 solved = 0;
  ok = _place == 388 && _runner.getValue(0,24,solved) && solved == 1 && _puzzlesCompleted == 12 && ok;
  debug("Astronomica P508 startup save: %s (physical slot, seven remaining correct answers)",ok ? "PASS" : "FAIL");
  return ok;
 }
 struct Boundary { Common::Array<byte> bytes; uint32 hash, now; };
 uint restores = 0, continuations = 0;
 Common::Array<byte> fixture;
 for (uint seed : {1U,48879U,65535U}) for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(seed); _puzzlesCompleted = 11;
  if (!loadPlace(508)) return false;
  if (canSaveQuestion()) return false; // No first question has been displayed.
  uint32 now = scriptClock();
  if (_runner.enqueueStartup(_scene.scripts,now,true) != 3 || !settle(now)) return false;
  Common::Array<Boundary> boundaries;
  Common::Array<uint32> results, sounds, soundCounts;
  const uint count = route == 0 ? 8 : route == 1 ? 3 : 10;
  for (uint n = 0; n < count; ++n) {
   if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveQuestion()) return false;
   _mixer->stopHandle(_soundHandle); // Deterministic test boundary after speech.
   if (!canSaveQuestion()) { debug("P508 save boundary rejected: seed %u route %u answer %u",seed,route,n); return false; }
   _pausedMillis = _system->getMillis()-now;
   Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
   if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 12+4*kP508StateWords) return false;
   Boundary boundary; boundary.bytes.resize(out.size()); memcpy(&boundary.bytes[0],out.getData(),out.size());
   boundary.hash = fingerprint(); boundary.now = now; boundaries.push_back(boundary);
   if (seed == 48879 && route == 2 && n == 2) {
    fixture = boundary.bytes;
    if (ConfMan.hasKey("astronomica_verify_save_files") && ConfMan.getBool("astronomica_verify_save_files")) {
     if (saveGameState(2,"P508 continuation regression").getCode() != Common::kNoError) return false;
     debug("Astronomica P508 slot fingerprint: %08x",fingerprint());
    }
   }
   const uint before = _soundsStarted;
   if (!answer(route == 1 || (route == 2 && (n == 1 || n == 4)),now)) return false;
   results.push_back(fingerprint()); sounds.push_back(_lastSound); soundCounts.push_back(_soundsStarted-before);
  }
  int32 solved = 0;
  if (_place != 388 || !_runner.getValue(0,24,solved) || solved != (route == 1 ? 0 : 1) || _puzzlesCompleted != (route == 1 ? 11U : 12U)) return false;
  for (uint start = 0; start < boundaries.size(); ++start) {
   _mixer->stopHandle(_soundHandle);
   if (!loadPlace(117)) return false;
   _runner.seedRandom(99); _runner.defineValue(0,24,123);
   const uint beforeLoad = _soundsStarted;
   // Exercise the production skip-entry path even with automatic entry on.
   ConfMan.setBool("astronomica_entry_scripts",true);
   const bool restored = restore(boundaries[start].bytes);
   ConfMan.setBool("astronomica_entry_scripts",false);
   if (!restored || _soundsStarted != beforeLoad || fingerprint() != boundaries[start].hash || !canSaveQuestion()) return false;
   ++restores; now = boundaries[start].now;
   Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);
   if (saveGameStream(&again).getCode() != Common::kNoError || again.size() != boundaries[start].bytes.size()) return false;
   // Clock naturally advances; every other serialized field stays identical.
   for (uint offset = 8; offset < again.size()-4; ++offset)
    if ((offset < 16 || offset >= 20) && again.getData()[offset] != boundaries[start].bytes[offset]) return false;
   for (uint n = start; n < count; ++n) {
    const uint before = _soundsStarted;
    if (!answer(route == 1 || (route == 2 && (n == 1 || n == 4)),now)) return false;
    if (fingerprint() != results[n] || uint32(_lastSound) != sounds[n] || _soundsStarted-before != soundCounts[n]) return false;
    ++continuations;
   }
  }
 }
 if (fixture.empty() || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1;
  if (restore(damaged) || fingerprint() != unchanged) return false;
  damaged[offset] ^= 1;
 }
 // Valid checksum cannot bypass state bounds or known/width metadata checks.
 for (uint word : {0U,3U,4U,5U,6U,7U,9U,310U,311U,312U,319U,322U,325U,612U}) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+word*4],0x80000000U);
  uint32 hash = 2166136261U;
  for (uint n = 0; n < kP508StateWords; ++n) hash = (hash ^ READ_LE_UINT32(&damaged[8+n*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) return false;
 }
 if (!restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveQuestion()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || _lastSound != 0 || !_mixer->isSoundHandleActive(_soundHandle)) return false;
 _mixer->stopHandle(_soundHandle);
 if (!playSound(1,scriptClock()) || canSaveQuestion()) return false;
 _mixer->stopHandle(_soundHandle);
 _scene.sprites[4].x++; if (canSaveQuestion()) return false; _scene.sprites[4].x--;
 if (!stageBackgroundImage("logy1",67,354) || canSaveQuestion()) return false;
 _pendingImage.free(); _pendingImageName.clear();
 debug("Astronomica P508 saves: PASS (%u boundaries, %u continuation steps, %u truncations, %u corruptions, 14 invalid states, music and foreground guards)",restores,continuations,fixture.size(),fixture.size());
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyP505Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  hash = (hash ^ _puzzlesCompleted)*16777619U;
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  for (const HoverTarget &hover : _hoverSprites) hash = (hash ^ uint32(hover.entered))*16777619U;
  for (const HoverTarget &hover : _hoverRects) hash = (hash ^ uint32(hover.entered))*16777619U;
  return (hash ^ screenRGBHash(_screen))*16777619U;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 3000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 50; }
  return _runner.idle();
 };
 auto answer = [&](bool wrong, uint32 &now) {
  const int correct[] = {9,4,1,8,7,3,5,6}; int32 choice = 0;
  if (_place != 505 || !_runner.getValue(1,0,choice) || choice < 1 || choice > 8) return false;
  hoverAtTime(-100,-100,now); if (!settle(now)) return false;
  const MouseRect &rect = _scene.mouseRects[wrong ? 2 : correct[choice-1]];
  clickAtTime((rect.rect[0]+rect.rect[2])/2,(rect.rect[1]+rect.rect[3])/2,now);
  if (canSaveGameStateCurrently()) return false;
  return settle(now);
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 3) {
  int32 errors = 0;
  bool ok = _place == 505 && canSaveQuestion() && _runner.getValue(1,2,errors) && errors == 1;
  debug("Astronomica P505 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock();
  for (uint n = 0; n < 6 && ok; ++n) ok = answer(false,now) && ok;
  int32 solved = 0;
  ok = _place == 520 && _runner.getValue(0,22,solved) && solved == 1 && _puzzlesCompleted == 8 && ok;
  debug("Astronomica P505 startup save: %s (physical slot, six remaining answers)",ok ? "PASS" : "FAIL");
  return ok;
 }
 struct Boundary { Common::Array<byte> bytes; uint32 before, after, now, sounds, lastSound; int x, y; bool wrong; };
 uint restored = 0, hoverChecks = 0; Common::Array<byte> fixture;
 for (uint seed : {1U,48879U}) for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(seed); _puzzlesCompleted = 7;
  if (!loadPlace(505) || canSaveQuestion()) return false;
  uint32 now = scriptClock();
  if (_runner.enqueueStartup(_scene.scripts,now,true) != 3 || !settle(now)) return false;
  Common::Array<Boundary> boundaries;
  const uint count = route == 1 ? 3 : 8;
  for (uint n = 0; n < count; ++n) {
   Boundary b; b.wrong = route == 1 || (route == 2 && (n == 1 || n == 4));
   if (n & 1) {
    const Sprite &sprite = _scene.sprites[2*(n%4)]; b.x = sprite.x+1; b.y = sprite.y+1;
   } else {
    const MouseRect &rect = _scene.mouseRects[(n+route)%10]; b.x = (rect.rect[0]+rect.rect[2])/2; b.y = (rect.rect[1]+rect.rect[3])/2;
   }
   hoverAtTime(b.x,b.y,now); if (!settle(now)) return false;
   if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveQuestion()) return false;
   _mixer->stopHandle(_soundHandle);
   if (!canSaveQuestion()) { debug("P505 save boundary rejected: seed %u route %u answer %u",seed,route,n); return false; }
   _pausedMillis = _system->getMillis()-now; b.now = now; b.before = fingerprint();
   Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
   if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 2472) return false;
   b.bytes.resize(out.size()); memcpy(&b.bytes[0],out.getData(),out.size());
   if (seed == 48879 && route == 2 && n == 2) {
    fixture = b.bytes;
    if (ConfMan.hasKey("astronomica_verify_save_files") && ConfMan.getBool("astronomica_verify_save_files")) {
     if (saveGameState(3,"P505 continuation regression").getCode() != Common::kNoError) return false;
     debug("Astronomica P505 slot fingerprint: %08x",fingerprint());
    }
   }
   const uint sounds = _soundsStarted;
   if (!answer(b.wrong,now)) return false;
   b.after = fingerprint(); b.sounds = _soundsStarted-sounds; b.lastSound = uint32(_lastSound);
   boundaries.push_back(b);
  }
  int32 solved = 0;
  if (_place != (route == 1 ? 321 : 520) || !_runner.getValue(0,22,solved) || solved != (route == 1 ? 0 : 1) || _puzzlesCompleted != (route == 1 ? 7U : 8U)) return false;
  // Every edge of both complete routes is replayed from its own snapshot,
  // comparing the successor to the uninterrupted route, including hover exit.
  for (const Boundary &b : boundaries) {
   if (!loadPlace(117)) return false;
   _runner.seedRandom(77); _runner.defineValue(0,22,123);
   const uint sounds = _soundsStarted;
   ConfMan.setBool("astronomica_entry_scripts",true);
   const bool loaded = restore(b.bytes);
   ConfMan.setBool("astronomica_entry_scripts",false);
   if (!loaded || !canSaveQuestion() || _soundsStarted != sounds || fingerprint() != b.before) {
    debug("P505 restore mismatch: seed %u route %u, loaded %d, before %08x actual %08x",seed,route,loaded,b.before,fingerprint()); return false;
   }
   now = b.now;
   // Remaining on the already-entered target must neither replay speech nor
   // enqueue a duplicate enter event after a load.
   hoverAtTime(b.x,b.y,now);
   if (!_runner.idle() || _soundsStarted != sounds || fingerprint() != b.before) return false;
   ++hoverChecks;
   Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);
   if (saveGameStream(&again).getCode() != Common::kNoError || again.size() != b.bytes.size()) return false;
   for (uint offset = 8; offset < again.size()-4; ++offset)
    if ((offset < 16 || offset >= 20) && again.getData()[offset] != b.bytes[offset]) return false;
   if (!answer(b.wrong,now) || fingerprint() != b.after || _soundsStarted-sounds != b.sounds || uint32(_lastSound) != b.lastSound) {
    debug("P505 continuation mismatch: seed %u route %u",seed,route); return false;
   }
   ++restored;
  }
  debug("Astronomica P505 save route: PASS (seed %u, route %u, %u boundaries)",seed,route,boundaries.size());
 }
 if (fixture.empty() || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1;
  if (restore(damaged) || fingerprint() != unchanged) return false;
  damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,6,7,9,310,311,312,313,316,319,612,613,614};
 for (uint word : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+word*4],0x80000000U);
  uint32 hash = 2166136261U;
  for (uint n = 0; n < kP508StateWords+2; ++n) hash = (hash ^ READ_LE_UINT32(&damaged[8+n*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) return false;
 }
 if (!restore(fixture)) return false;
 _scene.sprites[0].selectedFrame = 1;
 if (canSaveQuestion()) return false;
 _scene.sprites[0].selectedFrame = 0;
 if (!stageBackgroundImage("apollo",254,362) || canSaveQuestion()) return false;
 _pendingImage.free(); _pendingImageName.clear();
 debug("Astronomica P505 saves: PASS (%u boundaries and successor comparisons, %u hover resumptions, 2472 truncations, 2472 corruptions, 16 invalid states)",restored,hoverChecks);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyP519Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) { hash = (hash ^ uint32(s.selectedFrame))*16777619U; hash = (hash ^ uint32(s.visible))*16777619U; }
  for (const HoverTarget &h : _hoverRects) hash = (hash ^ uint32(h.entered))*16777619U;
  for (uint32 value : {_puzzlesCompleted,_p519LargeImage,_p519SmallImage,screenRGBHash(_background),screenRGBHash(_screen)}) hash = (hash ^ value)*16777619U;
  return hash;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 4000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 50; }
  // Stop only after checking that active foreground audio excludes saving.
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP519()) return false;
  _mixer->stopHandle(_soundHandle);
  return _runner.idle();
 };
 auto execute = [&](int index, uint32 &now) {
  if (index < 0) return true;
  int x = 24, y = 417;
  if (index < 10) { const MouseRect &r = _scene.mouseRects[index]; x = (r.rect[0]+r.rect[2])/2; y = (r.rect[1]+r.rect[3])/2; }
  clickAtTime(x,y,now);
  if (canSaveP519()) return false;
  return settle(now);
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 4) {
  debug("Astronomica P519 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); bool ok = canSaveP519() && execute(3,now);
  const uint detectors[] = {9,7,5,6,8}, targets[] = {1,3,4,0,2};
  for (uint i = 0; i < 5 && ok; ++i) ok = execute(detectors[i],now) && execute(targets[i],now);
  int32 solved = 0; ok = ok && _place == 281 && _runner.getValue(0,35,solved) && solved == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P519 startup save: %s (physical slot, wrong Sun then five pairings)",ok ? "PASS" : "FAIL");
  return ok;
 }
 uint32 now = 0; uint boundaries = 0, compositions = 0; Common::Array<byte> fixture;
 auto start = [&]() {
  _runner.resetGlobals(); _runner.seedRandom(519); _puzzlesCompleted = 10;
  if (!loadPlace(519) || canSaveP519()) return false;
  now = scriptClock(); return _runner.enqueueStartup(_scene.scripts,now,true) == 3 && settle(now) && canSaveP519();
 };
 auto roundTrip = [&](int action, bool physical) {
  if (action >= 0 && action < 10) {
   const MouseRect &r = _scene.mouseRects[action];
   hoverAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);
   if (!settle(now)) return false;
  }
  if (!canSaveP519()) { debug("P519 boundary rejected: %u",boundaries); return false; }
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 2584) return false;
  Common::Array<byte> bytes; bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size());
  const uint32 before = fingerprint(), savedNow = now;
  if (physical) {
   fixture = bytes;
   if (saveGameState(4,"P519 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P519 slot fingerprint: %08x",before);
  }
  const uint soundBefore = _soundsStarted;
  if (!execute(action,now)) return false;
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundBefore; const int last = _lastSound;
  if (!loadPlace(117)) return false;
  _runner.seedRandom(77); _runner.defineValue(0,35,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true);
  const bool loaded = restore(bytes);
  ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP519() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("P519 restore mismatch: boundary %u loaded %d before %08x actual %08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  if (action >= 0 && action < 10) {
   const MouseRect &r = _scene.mouseRects[action]; hoverAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);
   if (!_runner.idle() || fingerprint() != before || _soundsStarted != loadSounds) return false;
  }
  Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);
  if (saveGameStream(&again).getCode() != Common::kNoError || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again.getData()[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action >= 0 && _lastSound != last)) {
   debug("P519 continuation mismatch: boundary %u action %d",boundaries,action); return false;
  }
  ++boundaries; return true;
 };
 // All 25 original detector/target pairs, including errors and flash paths.
 for (uint detector = 5; detector < 10; ++detector) for (uint target = 0; target < 5; ++target) {
  if (!start() || !roundTrip(detector,false) || !roundTrip(target,detector == 6 && target == 3)) return false;
 }
 debug("Astronomica P519 save pair matrix: PASS (25 pairs, 50 boundaries)");
 // Complete both solve orders and retain higher selected frames between pairs.
 for (uint route = 0; route < 2; ++route) {
  if (!start()) return false;
  const uint detectors[] = {9,7,5,6,8}, targets[] = {1,3,4,0,2};
  for (uint i = 0; i < 5; ++i) {
   const uint pair = route ? 4-i : i;
   if (!roundTrip(detectors[pair],false) || !roundTrip(targets[pair],false)) return false;
  }
  int32 solved = 0;
  if (_place != 281 || !_runner.getValue(0,35,solved) || solved != 1 || _puzzlesCompleted != 11) return false;
 }
 if (!start() || !roundTrip(7,false) || !roundTrip(3,false) || !roundTrip(3,false) || !roundTrip(10,false) || _place != 281 || _puzzlesCompleted != 10) return false;
 debug("Astronomica P519 save solve routes: PASS (two orders, repeated target, unsolved exit)");
 // Native reconstruction of every supported two-image composition. This is
 // resource composition coverage, separate from the reachable routes above.
 for (uint large = 1; large <= 5; ++large) for (uint small = 0; small <= 5; ++small) {
  if (!start() || !stageBackgroundImage(kP519Large[large],258,356)) return false;
  displayBackgroundImage();
  if (small) { if (!stageBackgroundImage(kP519Small[small],282,358)) return false; displayBackgroundImage(); }
  if (!roundTrip(-1,false)) return false;
  ++compositions;
 }
 if (fixture.empty() || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1;
  if (restore(damaged) || fingerprint() != unchanged) return false;
  damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,6,8,9,10,11,12,13,39,340,341,342,346,361,642};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U;
  for (uint i = 0; i < kP519Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) return false;
 }
 if (!restore(fixture)) return false;
 _scene.sprites[0].selectedFrame = 1; if (canSaveP519()) return false; _scene.sprites[0].selectedFrame = 0;
 if (!stageBackgroundImage("asun",258,356) || canSaveP519()) return false;
 _pendingImage.free(); _pendingImageName.clear();
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP519()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P519 saves: PASS (%u boundaries, %u compositions, 2584 truncations, 2584 corruptions, 18 invalid states, music and foreground guards)",boundaries,compositions);
 _runner.resetGlobals(); return loadPlace(103);
}

bool AstronomicaEngine::verifyP524Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) { hash = (hash ^ uint32(s.selectedFrame))*16777619U; hash = (hash ^ uint32(s.visible))*16777619U; }
  if (_place == 524) {
   const Sprite &a = _scene.sprites[31];
   for (uint32 word : {uint32(a.autoFrame),a.frameSince,uint32(a.frameData[0]),uint32(a.frameData[1]),uint32(a.moveData[0])}) hash = (hash ^ word)*16777619U;
  }
  for (uint32 word : {_puzzlesCompleted,screenRGBHash(_background),screenRGBHash(_screen)}) hash = (hash ^ word)*16777619U;
  return hash;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 6000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 20; }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP524()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle();
 };
 auto execute = [&](int index, uint32 &now) {
  if (index < 0) return true;
  if (_place != 524) return false;
  const Sprite &s = _scene.sprites[index]; const int x = s.renderX+10, y = s.renderY+10;
  if (spriteAt(x,y) != index) return false;
  clickAtTime(x,y,now);
  if (canSaveP524() || !settle(now)) return false;
  if (index == 30 && _place == 408) {
   if (spriteAt(33,426) != 0) return false;
   clickAtTime(33,426,now);
   if (!settle(now) || _place != 524 || _runner.enqueueStartup(_scene.scripts,now,true) != 5 || !settle(now)) return false;
  }
  return true;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto choice = [&]() { int32 value = 0; _runner.getValue(1,0,value); return value; };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 5) {
  debug("Astronomica P524 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); bool ok = canSaveP524() && choice() == 7 && execute(30,now);
  for (uint n = 0; n < 9 && ok && _place == 524; ++n) ok = execute(choice() == 9 ? 0 : choice(),now);
  int32 solved = 0; ok = ok && _place == 117 && _runner.getValue(0,40,solved) && solved == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P524 startup save: %s (Triton, mentor return and completion)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, animations = 0; Common::Array<byte> fixture;
 auto start = [&](uint seed, bool solved) {
  _runner.resetGlobals(); _runner.seedRandom(seed); _runner.defineValue(0,29,1); _runner.defineValue(0,40,solved); _puzzlesCompleted = 10;
  if (!loadPlace(524) || canSaveP524()) return false;
  now = scriptClock();
  if (_runner.enqueueStartup(_scene.scripts,now,true) != 5 || !settle(now)) return false;
  if (!canSaveP524()) {
   Common::Array<uint32> state; _runner.exportIdleState(state);
   debug("P524 start rejected: locals %u %u %u %u %u %u animation %d %d %d",state[300],state[303],state[306],state[309],state[312],state[315],_scene.sprites[31].autoFrame,_scene.sprites[31].frameData[0],_scene.sprites[31].moveData[0]); return false;
  }
  return true;
 };
 auto roundTrip = [&](int action, bool physical) {
  if (!canSaveP524()) { debug("P524 boundary rejected: %u choice %d",boundaries,choice()); return false; }
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 2612) return false;
  Common::Array<byte> bytes; bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size());
  const uint32 before = fingerprint(), savedNow = now;
  if (physical) {
   fixture = bytes;
   if (saveGameState(5,"P524 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P524 slot fingerprint: %08x",before);
  }
  const uint soundBefore = _soundsStarted;
  if (!execute(action,now)) { debug("P524 action failed: %d",action); return false; }
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundBefore; const int last = _lastSound;
  if (!loadPlace(117)) return false;
  _runner.seedRandom(77); _runner.defineValue(0,40,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true);
  const bool loaded = restore(bytes);
  ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP524() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("P524 restore mismatch: boundary %u loaded %d before %08x actual %08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);
  if (saveGameStream(&again).getCode() != Common::kNoError || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again.getData()[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action >= 0 && _lastSound != last)) {
   debug("P524 continuation mismatch: boundary %u action %d",boundaries,action); return false;
  }
  ++boundaries; return true;
 };
 for (uint route = 0; route < 4; ++route) {
  if (!start(143+route,route == 1)) return false;
  uint seen = 0, answers = 0;
  if (route == 3) { if (!roundTrip(28,false)) return false; }
  else while (_place == 524 && answers < 10) {
   const int current = choice();
   if (current < 1 || current > 9 || (seen & (1U << (current-1)))) return false;
   seen |= 1U << (current-1);
   if (current == 9 && answers != 8) return false;
   if (route == 0 && current == 7) {
    if (!roundTrip(30,true) || !roundTrip(-1,false)) return false;
   }
   if (!roundTrip(route == 2 ? 0 : current == 9 ? 0 : current,false)) return false;
   ++answers;
  }
  int32 solved = -1;
  if (_place != 117 || !_runner.getValue(0,40,solved) || solved != int(route < 2) ||
      _puzzlesCompleted != 10+uint(route == 0) || (route < 2 && (answers != 9 || seen != 511)) || (route == 2 && answers != 3)) return false;
 }
 debug("Astronomica P524 save routes: PASS (Moon last, two solve routes, three errors, voluntary exit and mentor return)");
 if (fixture.empty()) return false;
 // Probe all animation frames and exact timer boundaries, including uint32 wrap.
 for (uint frame = 0; frame < 8; ++frame) for (uint32 epoch : {1000U,0xffffff80U}) for (uint32 gap : {199U,200U,2200U}) {
  if (!restore(fixture)) return false;
  Sprite &a = _scene.sprites[31]; a.selectedFrame = frame; a.frameSince = epoch; now = epoch+gap;
  redrawSprites();
  if (!roundTrip(-1,false)) return false;
  animateSpritesAt(now);
  if (_scene.sprites[31].selectedFrame != int(gap < 200 ? frame : (frame+1)%8) ||
      _scene.sprites[31].frameSince != (gap < 200 ? epoch : now)) return false;
  ++animations;
 }
 if (!loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1;
  if (restore(damaged) || fingerprint() != unchanged) return false;
  damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,5,6,8,9,11,12,13,14,15,46,347,348,349,350,353,356,359,362,649};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U;
  for (uint i = 0; i < kP524Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) return false;
 }
 if (!restore(fixture)) return false;
 _scene.sprites[0].selectedFrame = 1; if (canSaveP524()) return false; _scene.sprites[0].selectedFrame = 0;
 if (!stageBackgroundImage("viewtrit",0,0) || canSaveP524()) return false;
 _pendingImage.free(); _pendingImageName.clear(); _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP524()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P524 saves: PASS (%u boundaries, %u animation cases, 2612 truncations, 2612 corruptions, 21 invalid states, music and foreground guards)",boundaries,animations);
 _runner.resetGlobals(); return loadPlace(103);
}

bool AstronomicaEngine::verifyRocketSaves() {
 uint boundaries = 0, histories = 0, dormant = 0, busy = 0, invalid = 0; uint32 now = 0;
 Common::Array<byte> fixture;
 auto fingerprint = [&](uint32 clock = 0, bool departure = false) {
  uint32 hash = 2166136261U; auto add = [&](uint32 v) { hash = (hash ^ v)*16777619U; };
  add(_place); add(_puzzlesCompleted); add(_comet.frame); add(_comet.previousFrame);
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return uint32(0);
  for (uint i = 0; i < state.size(); ++i) if (i != 601) add(state[i]);
  if (_place == 537) { add(_rocket.kind); add(_rocket.delta); add(_rocket.since); }
  for (const Sprite &s : _scene.sprites) {
   Common::Array<uint32> words; p526SpriteWords(s,words);
   if (departure && s.autoFrame) words[8] = clock-words[8];
   if (departure && s.autoMove) words[9] = clock-words[9];
   for (uint32 v : words) add(v);
  }
  add(screenRGBHash(_background,480)); add(screenRGBHash(_screen,480)); return hash;
 };
 auto settle = [&]() {
  for (uint n = 0; n < 20000 && _place == 537 && (!_runner.scriptsIdle() || _rocket.kind != RocketMotion::kStopped); ++n) {
   if (canSaveRocket()) return false; ++busy;
   runScriptsAt(now); animateSpritesAt(now); now += 10;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveRocket()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.scriptsIdle();
 };
 auto press = [&](uint id) {
  if (!id) return true;
  if (_place != 537 || id > 48) return false;
  const Sprite &s = _scene.sprites[id-1]; if (spriteAt(s.x+1,s.y+1) != int(id)-1) return false;
  clickAtTime(s.x+1,s.y+1,now);
  if (canSaveRocket()) return false; return settle();
 };
 auto start = [&](bool suspended = false, int solved = 0) {
  if (suspended) { if (loadGameState(99).getCode() != Common::kNoError) return false; }
  else _runner.resetGlobals();
  _runner.defineValue(0,36,solved); _puzzlesCompleted = 10; _comet.frame = 3; _comet.previousFrame = 4;
  if (!loadPlace(537)) return false;
  now = 1000; if (_runner.enqueueStartup(_scene.scripts,now,true) != 1 || !settle()) return false;
  return canSaveRocket();
 };
 auto bytes = [&](Common::Array<byte> &result) {
  // Freeze the test clock while serializing; keep the byte comparison exact.
  const bool paused = _clockPaused; const uint32 pauseStarted = _pauseStarted;
  _clockPaused = true; _pauseStarted = now; _pausedMillis = 0;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  const bool ok = saveGameStream(&out).getCode() == Common::kNoError && out.size() == 7680;
  _clockPaused = paused; _pauseStarted = pauseStarted;
  _pausedMillis = (paused ? pauseStarted : _system->getMillis())-now;
  if (!ok) return false;
  result.resize(out.size()); memcpy(&result[0],out.getData(),out.size()); return true;
 };
 auto restore = [&](const Common::Array<byte> &data) {
  const bool paused = _clockPaused; const uint32 oldStart = _pauseStarted,oldOffset = _pausedMillis;
  _clockPaused = true; _pauseStarted = 0x23450000U;
  Common::MemoryReadStream in(&data[0],data.size()); const bool loaded = loadGameStream(&in).getCode() == Common::kNoError;
  const uint32 restoredClock = scriptClock(); const bool clockOK = loaded ? data.size() >= 20 && restoredClock == READ_LE_UINT32(&data[16]) : _pausedMillis == oldOffset;
  _clockPaused = paused; _pauseStarted = oldStart; _pausedMillis = loaded ? (paused ? oldStart : _system->getMillis())-restoredClock : oldOffset;
  if (!clockOK) debug("Rocket restored/rejected clock invariant: FAIL");
  return loaded ? clockOK : !clockOK;
 };
 auto roundTrip = [&](uint action, bool physical = false) {
  if (!canSaveRocket()) { debug("Rocket save eligibility failed: boundary%u action%u P%d delta%d since%u",boundaries,action,_place,_rocket.delta,_rocket.since); return false; }
  Common::Array<byte> saved; if (!bytes(saved)) return false;
  const uint32 before = fingerprint(), savedNow = now; Common::Array<uint32> state; _runner.exportPersistentState(state);
  histories += _rocket.delta != 0; dormant += state[603] != 0;
  if (physical) { fixture = saved; if (saveGameState(13,"Rocket continuation regression").getCode() != Common::kNoError) return false; debug("Astronomica rocket slot fingerprint: %08x",before); }
  const uint soundsBefore = _soundsStarted; if (!press(action)) return false;
  const bool departure = _place != 537; const uint32 after = fingerprint(now,departure), sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!loadPlace(117)) return false; _runner.seedRandom(77); _runner.defineValue(0,36,0x12345678);
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(saved); ConfMan.setBool("astronomica_entry_scripts",false);
  now = savedNow; Common::Array<byte> again;
  if (!loaded || !canSaveRocket() || fingerprint() != before || !bytes(again) || again != saved) { debug("Rocket save restore mismatch: boundary%u action%u loaded%d eligible%d before%08x actual%08x bytes%u/%u",boundaries,action,loaded,canSaveRocket(),before,fingerprint(),uint(saved.size()),uint(again.size())); for (uint i = 0; i < MIN(saved.size(),again.size()); ++i) if (saved[i] != again[i]) { debug("Rocket payload difference: offset%u expected%u actual%u",i,uint(saved[i]),uint(again[i])); break; } return false; }
  const uint actualSoundsBefore = _soundsStarted; if (!press(action)) return false;
  if (fingerprint(now,departure) != after || _soundsStarted-actualSoundsBefore != sounds || _lastSound != last) {
   debug("Rocket continuation mismatch: boundary%u action%u expected%08x actual%08x clock%u",boundaries,action,after,fingerprint(now,departure),now); return false;
  }
  if (!restore(saved)) return false; now = savedNow; ++boundaries; return true;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 13) {
  debug("Astronomica rocket slot fingerprint: %08x",fingerprint()); now = scriptClock();
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return false; const uint32 mask = state[604];
  int32 selection = -1; bool ok = canSaveRocket() && _rocket.delta == 10 && _comet.frame == 3 && _comet.previousFrame == 4 && state[603] == 2 &&
   _runner.getValue(1,0,selection) && selection == 11;
  ok = ok && press(33); int32 solved = 0;
  ok = ok && _place == 321 && _runner.getValue(0,36,solved) && solved == 1 && _puzzlesCompleted == 11 && _runner.exportPersistentState(state) && state[603] == 2 && state[604] == mask;
  debug("Astronomica rocket startup save: %s (prior fast failure, selector11, dormant round2, first success)",ok ? "PASS" : "FAIL"); return ok;
 }
 // Exercise all controls at every initial selector, with both count histories.
 for (int solved = 0; solved <= 1; ++solved) for (int setting = 0; setting < 16; ++setting) {
  if (!start(false,solved)) return false;
  for (int value = 1; value <= setting; ++value) if (!press(6)) return false;
  for (uint action : {0U,5U,6U,33U,1U,4U}) if (!roundTrip(action)) return false;
 }
 // Old digits/gauges must remain independent of all subsequent selector values.
 for (int setting : {1,3,5,7,9,13}) {
  if (!start(true)) return false;
  for (int value = 1; value <= setting; ++value) if (!press(6)) return false;
  if (!press(33) || _place != 537) return false;
  for (int value = setting; value > 0; --value) if (!press(5)) return false;
  for (int value = 0; value < 16; ++value) {
   for (uint action : {0U,5U,6U,33U}) if (!roundTrip(action)) return false;
   if (value < 15 && !press(6)) return false;
  }
 }
 // Build a real old-readout fixture, then choose the successful selector.
 if (!start(true)) return false;
 for (int value = 1; value <= 13; ++value) if (!press(6)) return false;
 if (!press(33) || !press(5) || !press(5) || !roundTrip(33,true)) return false;
 // The ambient sample may restart, but no entry narration is replayed.
 _loopSound = 0; _loopEnabled = true; playSound(0,now,true); Common::Array<byte> music; if (!bytes(music) || !loadPlace(117)) return false;
 uint sounds = _soundsStarted; if (!restore(music) || _soundsStarted != sounds+1 || _lastSound != 0 || !_loopEnabled) return false;
 _mixer->stopHandle(_soundHandle);
 // Every truncation/corruption and checksummed invalid field rejects atomically.
 auto atomic = [&]() {
  uint32 hash = fingerprint(); auto add = [&](uint32 v) { hash = (hash ^ v)*16777619U; };
  for (uint32 v : {uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),
       uint32(_rocket.kind),uint32(_rocket.delta),_rocket.since,_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie != nullptr)}) add(v);
  Common::Array<uint32> state; _runner.exportPersistentState(state); for (uint32 v : state) add(v);
  for (char c : _pendingImageName) add(byte(c)); add(0); for (char c : _displayedImageName) add(byte(c));
  add(screenRGBHash(_pendingImage,480)); return hash;
 };
 if (fixture.empty() || !loadPlace(117)) return false; const uint32 unchanged = atomic();
 for (uint length = 0; length < fixture.size(); ++length) { Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || atomic() != unchanged) return false; }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) { damaged[offset] ^= 0x40; if (restore(damaged) || atomic() != unchanged) return false; damaged[offset] ^= 0x40; }
 const uint invalidWords[] = {0,3,4,5,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,
  16+6*27,16+8*27+1,16+8*27+19,16+8*27+20,16+29*27+5,16+33*27+4,16+34*27,16+48*27+300,16+48*27+301,16+48*27+302,16+48*27+604};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x7fffffffU); uint32 hash = 2166136261U;
  for (uint i = 8; i < damaged.size()-4; i += 4) hash = (hash ^ READ_LE_UINT32(&damaged[i]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || atomic() != unchanged) { debug("Rocket invalid field accepted: %u",index); return false; } ++invalid;
 }
 debug("Astronomica rocket saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u busy rejections, 7680 truncations, 7680 corruptions, %u invalid states, Music restart)",boundaries,histories,dormant,busy,invalid);
 _runner.resetGlobals(); return loadPlace(103);
}

bool AstronomicaEngine::verifyRocketBoundaries() {
 uint boundaries = 0, rejected = 0, failures = 0; uint32 now = 0;
 auto candidate = [&]() { return _place == 537 && _runner.scriptsIdle() && _rocket.kind == RocketMotion::kStopped && !_pendingImage.w && !_movie; };
 auto settle = [&]() {
  for (uint tick = 0; tick < 6000 && (!candidate()); ++tick) { runScriptsAt(now); animateSpritesAt(now); now += 20; if (_place != 537) return _runner.scriptsIdle(); }
  return candidate();
 };
 auto record = [&](int route, int control) {
  if (!candidate()) return false;
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return false;
  debug("Rocket audit boundary: %d %d %u %u %d %u %u %u %u",route,control,now,state[300],_rocket.delta,_rocket.since,state[603],state[604],uint(_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound));
  for (uint i = 0; i < _scene.sprites.size(); ++i) {
   Common::Array<uint32> words; p526SpriteWords(_scene.sprites[i],words);
   Common::String line = Common::String::format("Rocket audit sprite: %u",i);
   for (uint32 value : words) line += Common::String::format(" %d",int32(value));
   debug("%s",line.c_str());
  }
  ++boundaries; return true;
 };
 auto click = [&](uint id) {
  const Sprite &s = _scene.sprites[id];
  if (spriteAt(s.x+1,s.y+1) != int(id)) return false;
  clickAtTime(s.x+1,s.y+1,now);
  if (candidate()) return false;
  ++rejected; return settle();
 };
 for (int route = 0; route <= 16; ++route) {
  _runner.resetGlobals(); if (!loadPlace(537)) return false;
  now = 0; if (_runner.enqueueStartup(_scene.scripts,now,true) != 1 || !settle() || !record(route,-1)) return false;
  if (!route) {
   if (!click(4) || !record(route,4)) return false;
   for (int value = 1; value <= 15; ++value) if (!click(5) || !record(route,5)) return false;
   if (!click(5) || !record(route,5)) return false;
   for (int value = 14; value >= 0; --value) if (!click(4) || !record(route,4)) return false;
  } else {
   const int setting = route-1;
   for (int value = 1; value <= setting; ++value) if (!click(5)) return false;
   if (!record(route,5) || !click(32)) return false;
   if (setting == 11 || setting == 12) { if (_place != 321) return false; }
   else {
    if (!record(route,32)) return false; ++failures;
    for (int value = setting+1; value <= 15; ++value) if (!click(5) || !record(route,5)) return false;
    for (int value = 14; value >= 0; --value) if (!click(4) || !record(route,4)) return false;
   }
  }
 }
 debug("Astronomica rocket boundary verification: PASS (%u boundaries, %u busy rejections, %u failed-return routes, all16 selectors)",boundaries,rejected,failures);
 _runner.resetGlobals(); return loadPlace(103);
}

bool AstronomicaEngine::verifyBuilderSaves() {
 const uint32 seeds[] = {1,32,64,1,1,64};
 const int parts[5][11] = {{48,54,58,60,59,52,0},{46,47,53,58,57,56,45,44,50,0},
  {48,54,58,60,49,52,0},{48,54,58,45,43,51,0},{46,47,53,58,57,56,55,45,43,51,0}};
 auto fingerprint = [&](uint32 comparisonClock = 0, bool freshScene = false) {
  Common::Array<uint32> state,sprites; if (!_runner.exportPersistentState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i < state.size(); ++i) if (i != 601) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) {
   const uint index = sprites.size(); p526SpriteWords(s,sprites);
   // A newly loaded destination starts its own animation after real speech.
   // Compare its active frame's age; saved builder epochs stay byte-exact.
   if (freshScene && s.autoFrame) sprites[index+8] = comparisonClock-s.frameSince;
  }
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {uint32(_comet.frame),uint32(_comet.previousFrame),_puzzlesCompleted,uint32(_previousPlace),uint32(_builderHistoryValid),screenRGBHash(_background,480),screenRGBHash(_screen,480),
       uint32(_loopSound),uint32(_loopEnabled),builderScene(_place) ? _lastSoundAt : uint32(0)}) hash = (hash ^ v)*16777619U;
  hash = (hash ^ uint32(_pendingImage.w))*16777619U;
  if (_pendingImage.w) {
   for (uint32 v : {uint32(_pendingImage.h),uint32(_pendingImageX),uint32(_pendingImageY)}) hash = (hash ^ v)*16777619U;
   for (char c : _pendingImageName) hash = (hash ^ byte(c))*16777619U;
   hash = (hash ^ screenRGBHash(_pendingImage,_pendingImage.h))*16777619U;
  }
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 8960) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 20000 && builderScene(_place) && _runner.pendingCount(); ++n) {
   if (canSaveBuilder()) return false;
   runScriptsAt(now); animateSpritesAt(now); now += 10;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveBuilder()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.scriptsIdle();
 };
 auto press = [&](uint id, uint32 &now) {
  if (!id) return true;
  if (!builderScene(_place) || id > 60) return false;
  const Sprite &s = _scene.sprites[id-1]; int hitX = -1, hitY = -1;
  for (int y = MAX(0,int(s.renderY)); y < 480 && hitX < 0; y += 4)
   for (int x = MAX(0,int(s.renderX)); x < 640; x += 4)
    if (spriteAt(x,y) == int(id)-1) { hitX = x; hitY = y; break; }
  if (hitX < 0) { debug("Builder save hit unavailable: P%d control%u",_place,id); return false; }
  clickAtTime(hitX,hitY,now); return settle(now);
 };
 auto execute = [&](uint action, uint32 &now) {
  if (action == 61) return press(5,now) && press(6,now);
  return press(action,now);
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 12) {
  debug("Astronomica builder slot fingerprint: %08x",fingerprint());
  Common::Array<uint32> state; int32 scenario = 0; uint32 now = scriptClock();
  bool ok = _comet.frame == 3 && _comet.previousFrame == 4 && _place == 536 && canSaveBuilder() && _runner.exportPersistentState(state) && state[603] == 2 &&
   _runner.getValue(1,1,scenario) && scenario == 5;
  const uint32 mask = ok ? state[604] : 0;
  for (uint i = 3; ok && parts[4][i]; ++i) ok = execute(parts[4][i],now);
  ok = ok && execute(7,now) && execute(8,now);
  int32 solved = 0;
  ok = ok && _place == 510 && _runner.getValue(0,31,solved) && solved == 1 && _puzzlesCompleted == 11 &&
   _runner.exportPersistentState(state) && state[603] == 2 && state[604] == mask;
  debug("Astronomica builder startup save: %s (P536 design5, partial parts, dormant round2 and first count)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, matrices = 0, seen515 = 0, seen536 = 0, noPicture = 0, dormant = 0, freshTimerChecks = 0;
 Common::Array<byte> fixture;
 auto roundTrip = [&](uint control, bool physical = false) {
  if (!canSaveBuilder()) {
   Common::Array<uint32> state; _runner.exportPersistentState(state);
   debug("Builder save boundary rejected: P%d control%u boundary%u idle%d history%d image%d state%d",_place,control,boundaries,_runner.scriptsIdle(),_builderHistoryValid,builderImageId(_displayedImageName),validBuilderState(state));
   for (uint i = 0; i < _scene.sprites.size(); ++i) {
    const Sprite &s = _scene.sprites[i]; debug("Builder sprite%u visible%d frame%d stored%d,%d render%d,%d",i,s.visible,s.selectedFrame,s.x,s.y,s.renderX,s.renderY);
   }
   return false;
  }
  const int savedPlace = _place;
  Common::Array<byte> bytes; if (!snapshot(bytes,now)) return false;
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return false;
  if (_displayedImageName.empty()) ++noPicture;
  if (state[603]) {
   Common::Array<uint32> legacy; if (_runner.idle() || _runner.exportIdleState(legacy)) return false;
   ++dormant;
  }
  if (_place == 515) seen515 |= 1U << state[303]; else seen536 |= 1U << state[303];
  const uint32 before = fingerprint(),savedNow = now;
  if (physical) {
   fixture = bytes;
   if (saveGameState(12,"Builder continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica builder slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(control,now)) return false;
  const bool freshScene = _place != savedPlace;
  if (freshScene) for (const Sprite &s : _scene.sprites) if (s.autoFrame) ++freshTimerChecks;
  const uint32 after = fingerprint(now,freshScene); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  Common::Array<uint32> expectedState,expectedSprites; _runner.exportPersistentState(expectedState);
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,expectedSprites);
  const uint32 expectedNow = now,expectedSuccessEnd = _lastSuccessEnd,expectedBlockingEnd = _lastBlockingSoundEnd;
  if (!after || !loadPlace(117)) return false;
  _runner.resetVariantSequence(); _runner.seedRandom(888); _runner.defineValue(0,31,123);
  _comet.frame = 2; _comet.previousFrame = 3;
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveBuilder() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("Builder restore mismatch: %u loaded%d expected%08x actual%08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  Common::Array<byte> again; if (!snapshot(again,now) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  if (!execute(control,now) || fingerprint(now,_place != savedPlace) != after || _soundsStarted-loadSounds != sounds || (control && _lastSound != last)) {
   debug("Builder continuation mismatch: %u control%u expected%08x actual%08x, clock%u/%u successEnd%u/%u blockingEnd%u/%u",boundaries,control,after,fingerprint(now,_place != savedPlace),expectedNow,now,expectedSuccessEnd,_lastSuccessEnd,expectedBlockingEnd,_lastBlockingSoundEnd);
   Common::Array<uint32> actualState,actualSprites; _runner.exportPersistentState(actualState);
   for (const Sprite &s : _scene.sprites) p526SpriteWords(s,actualSprites);
   for (uint i = 0; i < MIN(expectedState.size(),actualState.size()); ++i)
    if (expectedState[i] != actualState[i]) debug("Builder successor state%u: %u/%u",i,expectedState[i],actualState[i]);
   for (uint i = 0; i < MIN(expectedSprites.size(),actualSprites.size()); ++i)
    if (expectedSprites[i] != actualSprites[i]) debug("Builder successor sprite%u field%u: %u/%u",i/27+1,i%27,expectedSprites[i],actualSprites[i]);
   return false;
  }
  ++boundaries; return true;
 };
 auto matrix = [&]() {
  Common::Array<byte> entry; if (!snapshot(entry,now)) return false;
  for (uint control = 1; control <= 14; ++control) {
   if (!roundTrip(control) || !restore(entry)) return false;
   now = scriptClock(); ++matrices;
  }
  return true;
 };
 auto value = [&](int id, int expected) { int32 actual = -1; return _runner.getValue(1,id,actual) && actual == expected; };
 for (uint route = 0; route < ARRAYSIZE(seeds); ++route) {
  _runner.resetVariantSequence();
  if (route == 1 || route == 4) {
   if (loadGameState(99).getCode() != Common::kNoError || _runner.variantRound() != 2) return false;
  }
  _runner.resetGlobals(); _runner.seedRandom(seeds[route]); _puzzlesCompleted = 10;
  if (route == 3) _runner.defineValue(0,31,1);
  const int phases[6][2] = {{4,0},{3,4},{12,1},{7,8},{4,3},{1,12}};
  _comet.frame = phases[route][0]; _comet.previousFrame = phases[route][1];
  if (!loadPlace(515)) return false;
  now = scriptClock();
  if (_runner.enqueueStartup(_scene.scripts,now,true) != 7 || !settle(now) || !roundTrip(0) || !matrix()) return false;
  // Cap is intentionally allowed before choosing, while size remains6.
  Common::Array<byte> initial; if (!snapshot(initial,now) || !roundTrip(13) || !value(5,1) || !value(4,6) || !restore(initial)) return false;
  now = scriptClock();
  const bool alternate = route >= 4;
  if (alternate && (!roundTrip(8) || !value(0,7))) return false;
  for (int phase = 0; phase < (alternate ? 1 : 2); ++phase) {
   if (phase && (_runner.enqueueStartup(_scene.scripts,now,true) != 7 || !settle(now) || !roundTrip(0) || !matrix())) return false;
   if (!roundTrip(61) || !value(2,2)) return false;
   int32 scenario = 0,required = 0;
   if (!_runner.getValue(1,1,scenario) || scenario < 1 || scenario > 5 || !_runner.getValue(1,3,required)) return false;
   if ((phase || alternate ? scenario < 4 : scenario > 3) || !roundTrip(9) || !matrix()) return false;
   if (!roundTrip(13) || !value(2,2) || !roundTrip(14) || !value(5,0)) return false;
   for (int stage = 1; stage < required-1; ++stage) if (!roundTrip(11)) return false;
   if (!roundTrip(13) || !value(2,3) || !matrix()) return false;
   for (uint part = 0; parts[scenario-1][part]; ++part) {
    if (!roundTrip(parts[scenario-1][part])) return false;
    if (route == 1 && phase == 1 && part == 2 && !roundTrip(0,true)) return false;
   }
   for (int flag = 7; flag <= 12; ++flag) if (!value(flag,1)) return false;
   if (!roundTrip(7) || !value(2,4) || !roundTrip(8) || _place != (phase || alternate ? 510 : 536)) return false;
  }
  int32 solved = 0;
  if (!_runner.getValue(0,31,solved) || solved != int(!alternate) || _puzzlesCompleted != 10+uint(route < 3)) return false;
  if ((route == 1 || route == 4) && _runner.variantRound() != 2) return false;
 }
 if (fixture.empty() || seen515 != 0x3f || (seen536 & 0x34) != 0x34 || !noPicture || !dormant || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,22,23,25,26,27,28,30,31,32,33,34,35,36,37,38,
  12+42*27+2,12+42*27+3,12+42*27+4,12+42*27+5,1634,1932,1933,1934,1935,1936,1937,1938,1941,1944,1947,1972,1973,2234,2235,2236};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kBuilderWords; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("Builder invalid field accepted: %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveBuilder() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveBuilder() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[4].selectedFrame = 1; if (canSaveBuilder()) return false; _scene.sprites[4].selectedFrame = 0;
 _pendingImage.create(1,1,_screen.format); if (canSaveBuilder()) return false; _pendingImage.free();
 if (!stageBackgroundImage("pad",1,0)) return false;
 displayBackgroundImage(); if (canSaveBuilder() || _builderHistoryValid || !restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveBuilder()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 const uint musicSounds = _soundsStarted; Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !canSaveBuilder() || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0 || _soundsStarted != musicSounds+1) return false;
 if (!playSound(1,scriptClock()) || canSaveBuilder()) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica builder saves: PASS (%u boundaries, six routes, %u control matrix cases, 8960 truncations, 8960 corruptions, %u invalid states, %u no-picture and %u dormant-sequence boundaries, %u fresh-scene timer comparisons, Music restart, comet phase and P515 no-op)",boundaries,matrices,uint(ARRAYSIZE(invalidWords)),noPicture,dormant,freshTimerChecks);
 _runner.resetGlobals(); _runner.resetVariantSequence(); return loadPlace(103);
}

bool AstronomicaEngine::verifyP517Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state,sprites; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i < state.size(); ++i) if (i != 601) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),uint32(_p517HistoryValid),screenRGBHash(_background,480),screenRGBHash(_screen,480),
       uint32(_loopSound),uint32(_loopEnabled),_place == 517 ? _lastSoundAt : uint32(0)}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 3660) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto execute = [&](int action, uint32 &now) {
  if (_place != 517) return false;
  if (action == 0) { now += 301; animateSpritesAt(now); return true; }
  const int x[] = {0,319,319,24}, y[] = {0,420,369,417}, expected[] = {-1,4,5,1};
  if (action < 1 || action > 3 || spriteAt(x[action],y[action]) != expected[action]) return false;
  clickAtTime(x[action],y[action],now);
  for (uint pass = 0; pass < 10000 && _place == 517 && _runner.pendingCount(); ++pass) {
   if (canSaveP517()) return false;
   runScriptsAt(now); animateSpritesAt(now); now += 10;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP517()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle();
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 11) {
  debug("Astronomica P517 slot fingerprint: %08x",fingerprint());
  int32 setting = 0; uint32 now = scriptClock();
  bool ok = canSaveP517() && _runner.getValue(1,1,setting) && setting == 12 && _scene.sprites[9].autoFrame;
  for (uint pass = 0; pass < 3 && ok && _place == 517; ++pass) ok = execute(2,now);
  int32 solved = 0; ok = ok && _place == 512 && _runner.getValue(0,33,solved) && solved == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P517 startup save: %s (setting12, active/stopped phases, first completion count)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, animationCases = 0, settingMask = 0; Common::Array<byte> fixture;
 auto roundTrip = [&](int action, bool physical) {
  if (!canSaveP517()) {
   Common::Array<uint32> state; _runner.exportIdleState(state);
   debug("P517 save boundary rejected: %u idle%d scene%d history%d picture%d",boundaries,_runner.idle(),validP517Scene(_scene),_p517HistoryValid,p517ImageId(_displayedImageName));
   for (uint i = 0; i < _scene.sprites.size(); ++i) {
    const Sprite &s = _scene.sprites[i]; debug("P517 sprite%u visible%d frame%d auto%d stored%d,%d render%d,%d data%d,%d,%d move%d",i,s.visible,s.selectedFrame,s.autoFrame,s.x,s.y,s.renderX,s.renderY,s.frameData[0],s.frameData[1],s.frameData[2],s.moveData[0]);
   }
   return false;
  }
  Common::Array<byte> bytes; if (!snapshot(bytes,now)) return false;
  int32 setting = 0; if (!_runner.getValue(1,1,setting) || setting < 1 || setting > 14) return false;
  settingMask |= 1U << (setting-1);
  const uint32 before = fingerprint(), savedNow = now;
  if (physical) {
   fixture = bytes;
   if (saveGameState(11,"P517 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P517 slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(action,now)) return false;
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!after || !loadPlace(117)) return false;
  _runner.seedRandom(999); _runner.defineValue(0,33,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP517() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("P517 restore mismatch: %u loaded%d expected%08x actual%08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  Common::Array<byte> again; if (!snapshot(again,now) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action && _lastSound != last)) {
   debug("P517 continuation mismatch: %u action%d expected%08x actual%08x",boundaries,action,after,fingerprint()); return false;
  }
  ++boundaries; return true;
 };
 auto matrix = [&]() {
  Common::Array<byte> entry; if (!snapshot(entry,now)) return false;
  // Exercise each loaded phase and the exact next-frame boundary. Inactive
  // cycles keep their old frames and timer parameters through each restore.
  for (uint phase = 0; phase < 4; ++phase) for (uint age : {0U,99U,100U,299U,300U}) {
   if (!restore(entry)) return false;
   now = scriptClock();
   int32 level = 0; if (!_runner.getValue(1,0,level)) return false;
   if (level > 1) {
    Sprite &s = _scene.sprites[level+6]; const uint period = s.frameData[0];
    for (uint n = 0; n <= phase; ++n) { now = MAX(now,s.frameSince)+period; animateSpritesAt(now); }
    now = s.frameSince+age; animateSpritesAt(now);
   }
   for (int action = 0; action < 4; ++action) {
    Common::Array<byte> point; if (!snapshot(point,now) || !roundTrip(action,false) || !restore(point)) return false;
    now = scriptClock(); ++animationCases;
   }
  }
  if (!restore(entry)) return false; now = scriptClock(); return true;
 };
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(100+route); _puzzlesCompleted = 10;
  if (route == 1) _runner.defineValue(0,33,1);
  if (route == 2 && !loadPlace(509)) return false; // Retain original unknown locals14/16.
  if (!loadPlace(517) || _runner.enqueueStartup(_scene.scripts,0,true) != 2) return false;
  now = 0;
  for (uint n = 0; n < 10000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 10; }
  _mixer->stopHandle(_soundHandle);
  if (!_runner.idle()) return false;
  if (route == 2) {
   Common::Array<uint32> entry; if (!_runner.exportIdleState(entry) || entry[342] != 1 || entry[343] || entry[344] || entry[348] != 2 || entry[349] || entry[350]) return false;
   if (!roundTrip(3,false) || _place != 157 || _puzzlesCompleted != 10) return false;
   continue;
  }
  for (int setting = 3; setting >= 1; --setting) if (!roundTrip(1,false)) return false;
  if (!roundTrip(1,false)) return false; // Original minimum clamp.
  for (int setting = 1; setting <= 14; ++setting) {
   int32 actual = 0; if (!_runner.getValue(1,1,actual) || actual != setting || !matrix()) return false;
   if (!route && setting == 12 && !roundTrip(0,true)) return false;
   if (!roundTrip(2,false)) return false;
  }
  int32 solved = 0;
  if (_place != 512 || !_runner.getValue(0,33,solved) || solved != 1 || _puzzlesCompleted != 10+uint(!route)) return false;
 }
 if (fixture.empty() || settingMask != 0x3fff || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,18,19,22,25,28,30,31,33,34,174,175,176,177,201,202,203,204,228,229,234,235,238,241,244,309+300,309+301,309+302,309+303,309+304,309+305,309+307,309+308,911};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kP517Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("P517 invalid field accepted: %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveP517() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveP517() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[4].selectedFrame = 1; if (canSaveP517()) return false; _scene.sprites[4].selectedFrame = 0;
 _pendingImage.create(1,1,_screen.format); if (canSaveP517()) return false; _pendingImage.free();
 if (!stageBackgroundImage("aurback1",1,0)) return false;
 displayBackgroundImage(); if (canSaveP517() || _p517HistoryValid || !restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP517()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 const uint musicSounds = _soundsStarted;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !canSaveP517() ||
     !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0 || _soundsStarted != musicSounds+1) return false;
 if (!playSound(1,scriptClock()) || canSaveP517()) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P517 saves: PASS (%u boundaries, three routes, fourteen settings, %u animation cases, 3660 truncations, 3660 corruptions, %u invalid states, initial/repeated success, Music restart and guards)",boundaries,animationCases,uint(ARRAYSIZE(invalidWords)));
 _runner.resetGlobals(); return loadPlace(103);
}

bool AstronomicaEngine::verifyP513Saves() {
 const int answers[] = {7,2,2,2,8,1,8,7,6,2,5,9,4,5};
 const int digits[9][3] = {{0,0,5},{0,1,1},{0,0,4},{0,3,0},{0,0,2},{1,0,0},{0,0,4},{0,5,0},{0,1,5}};
 const int results[] = {12,13,14,14,15,15,16,16,17};
 auto fingerprint = [&]() {
  Common::Array<uint32> state,sprites; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i < state.size(); ++i) if (i != 601) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),uint32(_p513HistoryValid),screenRGBHash(_background,480),screenRGBHash(_screen,480),
       uint32(_loopSound),uint32(_loopEnabled),_place == 513 ? _lastSoundAt : uint32(0)}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 5928) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto execute = [&](int action, uint32 &now) {
  if (!action) return true;
  if (_place != 513) return false;
  const int x[] = {0,24,281,281,335,335},y[] = {0,417,362,418,369,411},expected[] = {-1,1,6,7,4,5};
  if (action < 1 || action > 5) return false;
  if (spriteAt(x[action],y[action]) != expected[action]) { debug("P513 save hit mismatch: action%d got%d expected%d",action,spriteAt(x[action],y[action]),expected[action]); return false; }
  clickAtTime(x[action],y[action],now);
  for (uint pass = 0; pass < 10000 && _place == 513 && _runner.pendingCount(); ++pass) {
   if (canSaveP513()) return false;
   runScriptsAt(now); animateSpritesAt(now); now += 10;
  }
  if (_place == 513 && _scene.sprites[31].autoMove) {
   _mixer->stopHandle(_soundHandle);
   if (canSaveP513()) return false; // Still moving with no foreground audio.
   for (uint pass = 0; pass < 400 && _scene.sprites[31].autoMove; ++pass) { animateSpritesAt(now); now += 10; }
   if (_scene.sprites[31].autoMove || _scene.sprites[31].visible) return false;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP513()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle();
 };
 auto directSelect = [&](int desired, uint32 &now) {
  for (uint n = 0; n < 10; ++n) {
   int32 setting = 0; if (!_runner.getValue(1,0,setting)) return false;
   if (setting == desired) return true;
   if (!execute(setting < desired ? 2 : 3,now)) return false;
  }
  return false;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 10) {
  debug("Astronomica P513 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); int32 right = 0; bool ok = canSaveP513() && _runner.getValue(1,5,right) && right == 2 && _scene.sprites[31].standardMotion;
  for (uint n = 0; n < 7 && ok && _place == 513; ++n) {
   int32 scenario = 0; ok = _runner.getValue(1,1,scenario) && scenario >= 1 && scenario <= 14;
   ok = ok && directSelect(answers[scenario-1],now) && execute(4,now);
  }
  int32 solved = 0; ok = ok && _place == 197 && _runner.getValue(0,29,solved) && solved == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P513 startup save: %s (two correct, retained stopped photon/digits, RNG and silent first completion)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, scenarios = 0, settings = 0, launches = 0, answerCases = 0; Common::Array<byte> fixture, questions[14];
 auto roundTrip = [&](int action, bool physical) {
  if (!canSaveP513()) {
   Common::Array<uint32> state; _runner.exportIdleState(state);
   debug("P513 save boundary rejected: %u idle%d scene%d history%d picture%d",boundaries,_runner.idle(),validP513Scene(_scene),_p513HistoryValid,p513ImageId(_displayedImageName));
   if (state.size() == ScriptRunner::kIdleStateWords) debug("P513 locals: %u,%u,%u,%u,%u,%u valid%d",state[300],state[303],state[306],state[309],state[312],state[315],validP513State(state));
   for (uint i = 0; i < _scene.sprites.size(); ++i) {
    const Sprite &s = _scene.sprites[i]; debug("P513 sprite%u visible%d frame%d auto%d,%d standard%d stored%d,%d render%d,%d periods%d,%d",i,s.visible,s.selectedFrame,s.autoFrame,s.autoMove,s.standardMotion,s.x,s.y,s.renderX,s.renderY,s.frameData[0],s.moveData[0]);
   }
   return false;
  }
  Common::Array<byte> bytes; if (!snapshot(bytes,now)) return false;
  int32 current = 0; if (!_runner.getValue(1,1,current) || current < 1 || current > 14) return false;
  if (questions[current-1].empty()) questions[current-1] = bytes;
  const uint32 before = fingerprint(),savedNow = now;
  if (physical) {
   fixture = bytes;
   if (saveGameState(10,"P513 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P513 slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(action,now)) return false;
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!after || !loadPlace(117)) return false;
  _runner.seedRandom(88); _runner.defineValue(0,29,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP513() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("P513 restore mismatch: %u loaded%d expected%08x actual%08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  Common::Array<byte> again; if (!snapshot(again,now) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action && _lastSound != last)) {
   debug("P513 continuation mismatch: %u action%d expected%08x actual%08x",boundaries,action,after,fingerprint()); return false;
  }
  ++boundaries; return true;
 };
 auto select = [&](int desired) {
  for (uint n = 0; n < 10; ++n) {
   int32 setting = 0; if (!_runner.getValue(1,0,setting)) return false;
   if (setting == desired) return true;
   if (!roundTrip(setting < desired ? 2 : 3,false)) return false;
  }
  return false;
 };
 for (uint route = 0; route < 5; ++route) {
  _runner.resetGlobals(); _runner.resetVariantSequence(); _runner.seedRandom(113+route); _runner.defineValue(0,29,route == 2); _puzzlesCompleted = 10;
  if (!loadPlace(509) || !loadPlace(513)) return false;
  now = scriptClock(); if (_runner.enqueueStartup(_scene.scripts,now,true) != 4) return false;
  for (uint n = 0; n < 10000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 10; }
  _mixer->stopHandle(_soundHandle);
  if (!roundTrip(0,false)) return false;
  if (route == 4) { if (!roundTrip(1,false)) return false; }
  else {
   if (!route) {
    if (!roundTrip(3,false)) return false;
    for (uint level = 1; level <= 9; ++level) {
     if (!select(level) || !roundTrip(5,false)) return false;
     const uint speed = 10-level, ticks = (266+speed-1)/speed;
     if (_scene.sprites[31].renderX != int(177+ticks*speed) || !_scene.sprites[results[level-1]-1].visible) return false;
     for (uint d = 0; d < 3; ++d) if (_scene.sprites[d+8].selectedFrame != digits[level-1][d]) return false;
     settings |= 1U << (level-1); ++launches;
    }
    if (!roundTrip(2,false)) return false;
   }
   uint seen = 0, attempts = 0;
   for (; attempts < 15 && _place == 513; ++attempts) {
    int32 scenario = 0; if (!_runner.getValue(1,1,scenario) || scenario < 1 || scenario > 14 || (seen & (1U << (scenario-1)))) return false;
    seen |= 1U << (scenario-1); scenarios |= seen;
    const bool correct = route == 0 || route == 2 || (route == 1 && attempts < 6);
    int setting = answers[scenario-1]; if (!correct) setting = setting == 9 ? 8 : setting+1;
    if (!select(setting)) return false;
    if (!route && attempts == 2 && !roundTrip(0,true)) return false;
    if (!roundTrip(4,false)) return false;
   }
   if (attempts != (route == 1 ? 14U : route == 3 ? 10U : 7U) || (route == 1 && seen != 0x3fff)) return false;
  }
  int32 solved = 0;
  if (_place != 197 || !_runner.getValue(0,29,solved) || solved != int(route < 3) || _puzzlesCompleted != 10+uint(route < 2)) return false;
 }
 if (fixture.empty() || scenarios != 0x3fff || settings != 0x1ff || launches != 9) return false;
 // Each question fixture comes from a real route above. Exhaust all nine
 // ordinary knob settings and compare the restored answer's successor.
 for (uint scenario = 1; scenario <= 14; ++scenario) for (uint setting = 1; setting <= 9; ++setting) {
  if (questions[scenario-1].empty() || !restore(questions[scenario-1])) return false;
  int32 oldMask = 0, oldRight = 0, oldWrong = 0, oldSolved = 0;
  if (!_runner.getValue(1,2,oldMask) || !_runner.getValue(1,4,oldWrong) || !_runner.getValue(1,5,oldRight) || !_runner.getValue(0,29,oldSolved)) return false;
  const uint oldCount = _puzzlesCompleted;
  const bool expectedAccepted = int(setting) == answers[scenario-1];
  const bool expectedWin = oldMask == 0x3fff || oldRight+int(expectedAccepted) == 7;
  const bool expectedExit = expectedWin || oldWrong+int(!expectedAccepted) == 10;
  now = scriptClock(); if (!select(setting)) return false;
  const uint oldSounds = _soundsStarted;
  if (!roundTrip(4,false)) return false;
  int32 solved = 0;
  if (_place != (expectedExit ? 197 : 513) || !_runner.getValue(0,29,solved) ||
      solved != (oldSolved || expectedWin) || _puzzlesCompleted != oldCount+uint(expectedWin && !oldSolved)) return false;
  const int expectedSound = expectedWin ? 16 : expectedAccepted ? 13 : int(setting) < answers[scenario-1] ? 10 : 11;
  // roundTrip performs the answer twice. P513's original success is silent
  // apart from the explicit reply/departure WAVs; custom25 must not add S12.
  if (_lastSound != expectedSound || _soundsStarted-oldSounds != 2U*(2U+uint(expectedWin))) return false;
  if (_place == 513) {
   int32 accepted = 0; const int expected = answers[scenario-1];
   if (!_runner.getValue(1,3,accepted) || accepted != int(setting == uint(expected))) return false;
   if (!accepted && _lastSound != (int(setting) < expected ? 10 : 11)) return false;
  }
  ++answerCases;
 }
 // The knob can change after its200ms input lock while a slow photon is
 // still moving. Velocity retains the launch setting; digits use the live
 // setting when the original callback stops the photon.
 for (uint initial : {7U,9U}) {
  if (!restore(fixture)) return false;
  now = scriptClock(); if (!select(initial)) return false;
  clickAtTime(335,411,now);
  for (uint n = 0; n < 10000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 10; }
  _mixer->stopHandle(_soundHandle);
  if (!_scene.sprites[31].autoMove || canSaveP513() || !execute(initial < 8 ? 2 : 3,now)) return false;
  const uint speed = 10-initial;
  if (_scene.sprites[31].renderX != int(177+((266+speed-1)/speed)*speed)) return false;
  for (uint d = 0; d < 3; ++d) if (_scene.sprites[d+8].selectedFrame != digits[7][d]) return false;
  if (!roundTrip(0,false) || !select(1) || !roundTrip(0,false)) return false;
  for (uint d = 0; d < 3; ++d) if (_scene.sprites[d+8].selectedFrame != digits[7][d]) return false;
 }
 if (!loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,18,19,22,25,28,30,31,33,34,853,856,859,868,871,1176,1177,1178,1179,1182,1185,1188,1191,1195,1196,1478};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kP513Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("P513 invalid field accepted: %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveP513() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveP513() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[0].selectedFrame = 1; if (canSaveP513()) return false; _scene.sprites[0].selectedFrame = 0;
 _pendingImage.create(1,1,_screen.format); if (canSaveP513()) return false; _pendingImage.free();
 if (!stageBackgroundImage("cube1",176,22)) return false;
 displayBackgroundImage(); if (canSaveP513() || _p513HistoryValid || !restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP513()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0) return false;
 if (!playSound(1,scriptClock()) || canSaveP513()) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P513 saves: PASS (%u boundaries, five routes, fourteen scenarios, nine stopped photon results, %u answer continuations, two live-setting changes, 5928 truncations, 5928 corruptions, 37 invalid states, initial/repeated silent success and guards)",boundaries,answerCases);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifySaveEntryHistory() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state,sprites; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint32 v : state) hash = (hash ^ v)*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),screenRGBHash(_background,480),screenRGBHash(_screen,480),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto capture = [&](Common::Array<byte> &bytes) {
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto checksum = [](Common::Array<byte> &bytes) {
  uint32 hash = 2166136261U; for (uint i = 8; i < bytes.size()-4; i += 4) hash = (hash ^ READ_LE_UINT32(&bytes[i]))*16777619U;
  WRITE_LE_UINT32(&bytes[bytes.size()-4],hash);
 };
 struct Destination { uint place,version,stateOffset; };
 const Destination destinations[] = {{524,6,47},{526,7,633},{528,8,255},{530,9,795}};
 uint entries = 0, extremes = 0, invalid = 0;
 for (const Destination &d : destinations) {
  _runner.resetGlobals(); _runner.resetVariantSequence(); _runner.defineValue(0,29,1); _runner.seedRandom(123);
  if (!loadPlace(509) || !loadPlace(d.place)) return false;
  uint32 now = scriptClock();
  if (d.place == 524 || d.place == 530) {
   if (_runner.enqueueStartup(_scene.scripts,now,true) != _scene.scripts.size()) return false;
   for (uint n = 0; n < 10000 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 20; }
  }
  _mixer->stopHandle(_soundHandle);
  Common::Array<uint32> state;
  if (!_runner.exportIdleState(state) || state[342] != 1 || state[343] || state[344] || state[348] != 2 || state[349] || state[350]) return false;
  if (!canSaveGameStateCurrently()) { debug("Astronomica save entry history rejected: P509 -> P%u (unknown locals14=1,16=2)",d.place); return false; }
  Common::Array<byte> bytes,again; if (!capture(bytes) || READ_LE_UINT32(&bytes[4]) != d.version) return false;
  const uint32 before = fingerprint();
  if (!loadPlace(117) || !restore(bytes) || fingerprint() != before || !capture(again) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  ++entries;
  for (uint32 value : {1U,0x80000000U,0xffffffffU}) {
   Common::Array<byte> changed = bytes; WRITE_LE_UINT32(&changed[8+(d.stateOffset+342)*4],value); checksum(changed);
   if (!restore(changed) || !canSaveGameStateCurrently() || !capture(again)) return false;
   for (uint i = 8; i < changed.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != changed[i]) return false;
   ++extremes;
  }
  const uint32 unchanged = fingerprint();
  for (uint field : {343U,344U}) {
   Common::Array<byte> changed = bytes; WRITE_LE_UINT32(&changed[8+(d.stateOffset+field)*4],1); checksum(changed);
   if (restore(changed) || fingerprint() != unchanged) return false;
   ++invalid;
  }
 }
 debug("Astronomica save entry history: PASS (%u original P509 entries, %u inert-value round trips, %u metadata rejections, v6-v9 layouts unchanged)",entries,extremes,invalid);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyVariantSaves() {
 const uint places[] = {506,531,532,533,534,535};
 const int targets[6][5] = {{12,13,14,0,0},{10,11,12,14,0},{12,10,11,0,0},{9,10,11,0,0},{14,15,16,17,18},{9,10,11,0,0}};
 const int answers[6][5] = {{3,4,5,0,0},{1,2,3,5,0},{1,3,4,0,0},{1,2,3,0,0},{3,4,5,6,7},{1,2,3,0,0}};
 auto fingerprint = [&]() {
  ScriptRunner copy = _runner; copy.setVariantSupport(true);
  Common::Array<uint32> state,sprites; if (!copy.exportVariantState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i < state.size(); ++i) if (i != 601) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),screenRGBHash(_background,480),screenRGBHash(_screen,480),
       uint32(_loopSound),uint32(_loopEnabled),variantProfile(_place) ? _lastSoundAt : uint32(0)}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  const VariantSaveProfile *p = variantProfile(_place); if (!p) return false;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 8+4*(12+p->sprites*27+606)) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 10000 && variantProfile(_place) && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 20; }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveVariant()) return false;
  _mixer->stopHandle(_soundHandle);
  ScriptRunner copy = _runner; copy.setVariantSupport(true); return copy.variantIdle();
 };
 auto execute = [&](int id, uint32 &now) {
  if (!id) return true;
  const VariantSaveProfile *p = variantProfile(_place); if (!p) return false;
  int hitX = -1,hitY = -1;
  if (id < 0) { hitX = 24; hitY = 417; }
  else {
   if (uint(id) > _scene.sprites.size()) return false;
   const Sprite &s = _scene.sprites[id-1];
   for (int y = MAX(0,int(s.renderY)); y < 480 && hitX < 0; y += 4)
    for (int x = MAX(0,int(s.renderX)); x < 640; x += 4)
     if (spriteAt(x,y) == id-1) { hitX = x; hitY = y; break; }
  }
  if (hitX < 0) { debug("Variant save missing hit: P%d sprite%d",_place,id); return false; }
  clickAtTime(hitX,hitY,now); return settle(now);
 };
 auto finish = [&](uint32 &now) {
  for (uint stage = 0; stage < 4 && variantProfile(_place); ++stage) {
   const int oldPlace = _place, variant = _place == 506 ? 0 : _place-530;
   for (uint item = 0; item < 5 && targets[variant][item] && _place == oldPlace; ++item)
    if (!execute(answers[variant][item]+4,now) || !execute(targets[variant][item],now)) return false;
  }
  int32 solved = 0; return _place == 519 && !_runner.variantRound() && _runner.getValue(0,23,solved) && solved == 1 && _lastSound == 922;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 9) {
  debug("Astronomica variant slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); int32 mask = 0; bool ok = canSaveVariant() && _runner.variantRound() == 2 && _runner.getValue(1,0,mask) && mask != 0;
  ok = ok && finish(now) && _puzzlesCompleted == 11;
  debug("Astronomica variant startup save: %s (partial solution, process statics, remaining nonrepeating rounds and first completion count)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, transitions = 0, routes = 0, initialRepeats = 0, coverage[4] = {};
 Common::Array<byte> fixture, sceneFixtures[6];
 auto roundTrip = [&](int action, bool physical) {
  if (!canSaveVariant()) { debug("Variant save boundary rejected: %u P%d round%u",boundaries,_place,_runner.variantRound()); return false; }
  Common::Array<byte> bytes; if (!snapshot(bytes,now)) return false;
  const uint32 before = fingerprint(),savedNow = now, savedRound = _runner.variantRound(); const int savedPlace = _place;
  const int variant = _place == 506 ? 0 : _place-530;
  if (sceneFixtures[variant].empty()) sceneFixtures[variant] = bytes;
  if (physical) {
   fixture = bytes;
   if (saveGameState(9,"Variant continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica variant slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(action,now)) return false;
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!after || !loadPlace(117)) return false;
  _runner.resetVariantSequence(); _runner.seedRandom(99); _runner.defineValue(0,23,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveVariant() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("Variant restore mismatch: %u loaded%d expected%08x actual%08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  Common::Array<byte> again; if (!snapshot(again,now) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action && _lastSound != last)) {
   debug("Variant continuation mismatch: %u P%d action%d expected%08x actual%08x",boundaries,savedPlace,action,after,fingerprint()); return false;
  }
  if (_place != savedPlace || _runner.variantRound() != savedRound) ++transitions;
  if (!savedRound && _runner.variantRound() == 1 && _place == savedPlace) ++initialRepeats;
  ++boundaries; return true;
 };
 for (uint route = 0; route < 48; ++route) {
  _runner.resetGlobals(); _runner.resetVariantSequence(); _runner.seedRandom(uint16(0x1234U ^ route*0x9e37U));
  _runner.defineValue(0,23,route > 0); _puzzlesCompleted = 10;
  // Retain deliberately unknown data from the previous scene as real loads do.
  _runner.defineValue(1,80,0x12345678); if (!loadPlace(places[route%6])) return false;
  now = scriptClock(); if (_runner.enqueueStartup(_scene.scripts,now,true) != 2 || !settle(now)) return false;
  uint seen = 0;
  for (uint stage = 0; stage < 4 && variantProfile(_place); ++stage) {
   const int variant = _place == 506 ? 0 : _place-530, oldPlace = _place;
   if (_runner.variantRound() != stage) return false;
   Common::Array<uint32> legacy;
   if (stage && (_runner.idle() || _runner.exportIdleState(legacy))) return false;
   coverage[stage] |= 1U << variant;
   if (stage) { if (seen & (1U << variant)) return false; seen |= 1U << variant; }
   if (!roundTrip(0,false)) return false;
   const VariantSaveProfile *p = variantProfile(_place);
   for (uint choice = 1; choice <= p->choices; ++choice) {
    if (!roundTrip(choice+4,false)) return false;
    int32 selected = 0; if (!_runner.getValue(1,1,selected) || selected != int(choice)) return false;
    for (uint i = 0; i < p->choices; ++i) if (_scene.sprites[4+i].selectedFrame != int(i+1 == choice)) return false;
   }
   // A wrong choice on the first target must not set its completion bit.
   const int wrong = answers[variant][0] == 1 ? 2 : 1;
   if (!roundTrip(wrong+4,false) || !roundTrip(targets[variant][0],false)) return false;
   int32 mask = -1; if (!_runner.getValue(1,0,mask) || mask) return false;
   for (uint item = 0; item < p->answers && _place == oldPlace && _runner.variantRound() == stage; ++item) {
    if (!roundTrip(answers[variant][item]+4,false) || !roundTrip(targets[variant][item],false)) return false;
    if (_place == oldPlace && _runner.variantRound() == stage) {
     if (!_runner.getValue(1,0,mask) || mask != int((1U << (item+1))-1)) return false;
     const bool physical = route == 0 && stage == 2 && item == 0;
     if (!roundTrip(0,physical) || !roundTrip(targets[variant][item],false)) return false;
     if (!_runner.getValue(1,0,mask) || mask != int((1U << (item+1))-1)) return false;
    }
   }
   if (_place == oldPlace && _runner.variantRound() == stage) return false;
  }
  int32 solved = 0;
  if (_place != 519 || _runner.variantRound() || !_runner.getValue(0,23,solved) || solved != 1 || _puzzlesCompleted != 10+uint(route == 0) || _lastSound != 922) return false;
  ++routes;
  if (routes >= 12 && initialRepeats && coverage[0] == 63 && coverage[1] == 63 && coverage[2] == 63 && coverage[3] == 63) break;
 }
 if (fixture.empty() || !initialRepeats || coverage[0] != 63 || coverage[1] != 63 || coverage[2] != 63 || coverage[3] != 63) return false;
 // Each scene has its own payload size. Reject every truncation and every
 // single-byte corruption before changing even process-static state.
 uint truncations = 0, corruptions = 0, invalid = 0;
 if (!loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint variant = 0; variant < 6; ++variant) {
  const Common::Array<byte> &bytes = sceneFixtures[variant]; if (bytes.empty()) return false;
  for (uint length = 0; length < bytes.size(); ++length) {
   Common::MemoryReadStream in(&bytes[0],length);
   if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
   ++truncations;
  }
  Common::Array<byte> damaged = bytes;
  for (uint offset = 0; offset < damaged.size(); ++offset) {
   damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1; ++corruptions;
  }
  const uint state = 12+variantProfile(places[variant])->sprites*27;
  const uint badWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,18,19,22,25,28,30,31,33,34,state+300,state+301,state+302,state+303,state+306,state+309,state+602,state+603,state+604};
  for (uint index : badWords) {
   damaged = bytes; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
   uint32 hash = 2166136261U; for (uint i = 8; i < damaged.size()-4; i += 4) hash = (hash ^ READ_LE_UINT32(&damaged[i]))*16777619U;
   WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
   if (restore(damaged) || fingerprint() != unchanged) { debug("Variant invalid field accepted: %u word%u",places[variant],index); return false; }
   ++invalid;
  }
  for (uint wrongRound : {0U,1U}) {
   damaged = bytes;
   WRITE_LE_UINT32(&damaged[8+(state+603)*4],wrongRound);
   WRITE_LE_UINT32(&damaged[8+(state+604)*4],1-wrongRound);
   uint32 hash = 2166136261U; for (uint i = 8; i < damaged.size()-4; i += 4) hash = (hash ^ READ_LE_UINT32(&damaged[i]))*16777619U;
   WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
   if (restore(damaged) || fingerprint() != unchanged) return false;
   ++invalid;
  }
 }
 if (!restore(fixture)) return false;
 now = scriptClock(); if (!roundTrip(-1,false) || _place != 281 || _runner.variantRound() != 2) return false;
 // The original statics persist on voluntary exit, including a later reentry.
 if (!loadPlace(506) || !settle(now) || !roundTrip(0,false) || _runner.variantRound() != 2) return false;
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveVariant() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveVariant() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[0].selectedFrame = 1; if (canSaveVariant()) return false; _scene.sprites[0].selectedFrame = 0;
 _pendingImage.create(1,1,_screen.format); if (canSaveVariant()) return false; _pendingImage.free();
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveVariant()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0) return false;
 if (!playSound(1,scriptClock()) || canSaveVariant()) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica variant saves: PASS (%u boundaries, %u routes, %u transitions, %u initial repeats, six scenes at all four stages, %u truncations, %u corruptions, %u invalid states, exit/reentry and music guards)",boundaries,routes,transitions,initialRepeats,truncations,corruptions,invalid);
 _runner.resetVariantSequence(); _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyP530Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state,sprites; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  // A departure's generic failure voice uses the fresh scene's real clock.
  // Its epoch is not a P530 continuation field. Before-action serialization
  // equality below still verifies the saved P530 sound epoch exactly.
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),uint32(_p530HistoryValid),screenRGBHash(_background,480),screenRGBHash(_screen,480),
       uint32(_loopSound),uint32(_loopEnabled),_place == 530 ? _lastSoundAt : uint32(0)}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 5604) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 10000 && _place == 530 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 10; }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP530()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle();
 };
 auto execute = [&](int action, uint32 &now) {
  if (action == 12) return true;
  if (_place != 530) return false;
  int x = 0,y = 0,expected = -1;
  if (!action) { x = 20; y = 443; expected = 1; }
  else if (action == 1) { x = 542; y = 333; expected = 4; }
  else if (action == 2) { x = 143; y = 354; }
  else if (action == 3) { x = 392; y = 189; expected = 21; }
  else if (action == 4) { x = 308; y = 395; }
  else if (action == 5) { x = 223; y = 80; expected = 22; }
  else if (action <= 10) { const int xs[] = {569,533,492,448,404},ys[] = {374,395,409,420,429}; x = xs[action-6]; y = ys[action-6]; expected = action+1; }
  else { int32 scenario = 0; _runner.getValue(1,9,scenario); const bool upper = scenario == 1 || scenario == 5; x = upper ? 245 : 424; y = upper ? 33 : 216; expected = upper ? 19 : 20; }
  if (spriteAt(x,y) != expected) { debug("P530 save hit mismatch action %d: expected %d got %d",action,expected,spriteAt(x,y)); return false; }
  clickAtTime(x,y,now); if (canSaveP530()) return false;
  return settle(now);
 };
 const int answers[] = {2,4,5,1,4};
 auto finish = [&](uint32 &now) {
  for (uint n = 0; n < 3 && _place == 530; ++n) {
   int32 a = 0,b = 0,scenario = 0;
   _runner.getValue(1,7,a); _runner.getValue(1,8,b); _runner.getValue(1,9,scenario);
   if (!a && (!execute(2,now) || !execute(3,now))) return false;
   if (!b && (!execute(4,now) || !execute(5,now))) return false;
   if (!execute(answers[scenario-1]+5,now) || !execute(11,now)) return false;
   if (_place == 530 && !execute(1,now)) return false;
  }
  int32 solved = 0; return _place == 228 && _runner.getValue(0,46,solved) && solved == 1 && _puzzlesCompleted == 10;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 8) {
  debug("Astronomica P530 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); int32 round = 0,a = 0,b = 0,detector = 0;
  const bool partial = _runner.getValue(1,13,round) && round == 2 && _runner.getValue(1,7,a) && a == 1 &&
   _runner.getValue(1,8,b) && !b && _runner.getValue(1,10,detector) && !detector && !_displayedImageName.empty();
  const bool ok = canSaveP530() && partial && finish(now);
  debug("Astronomica P530 startup save: %s (partial components, prior-round picture, remaining random round and unchanged counter)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, routes = 0, pictures = 0, seen[3] = {}; Common::Array<byte> fixture;
 auto roundTrip = [&](int action, bool physical = false) {
  if (!canSaveP530()) { debug("P530 save admission failed at boundary %u",boundaries); return false; }
  Common::Array<byte> bytes; if (!snapshot(bytes,now)) return false;
  const uint32 before = fingerprint(), savedNow = now;
  if (physical) {
   fixture = bytes; if (saveGameState(8,"P530 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P530 slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(action,now)) return false;
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  Common::Array<uint32> expectedState; _runner.exportIdleState(expectedState);
  const uint32 expectedBackground = screenRGBHash(_background,480), expectedScreen = screenRGBHash(_screen,480);
  if (_place == 530) { const int image = p530ImageId(_displayedImageName); if (image > 0) pictures |= 1U << (image-1); }
  if (!loadPlace(117)) return false;
  _runner.seedRandom(88); _runner.defineValue(0,46,123); const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP530() || fingerprint() != before || _soundsStarted != loadSounds) { debug("P530 restore mismatch boundary %u",boundaries); return false; }
  Common::Array<byte> again; if (!snapshot(again,savedNow) || again.size() != bytes.size()) return false;
  for (uint i = 8; i < again.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != bytes[i]) return false;
  now = savedNow;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || _lastSound != last) {
   debug("P530 continuation mismatch boundary %u action %d hashes %08x/%08x sounds %u/%u last %d/%d pixels %08x/%08x %08x/%08x",boundaries,action,after,fingerprint(),sounds,_soundsStarted-loadSounds,last,_lastSound,expectedBackground,screenRGBHash(_background,480),expectedScreen,screenRGBHash(_screen,480));
   Common::Array<uint32> actualState; _runner.exportIdleState(actualState);
   for (uint i = 0; i < MIN(expectedState.size(),actualState.size()); ++i) if (expectedState[i] != actualState[i]) debug("P530 successor word %u expected %u actual %u",i,expectedState[i],actualState[i]);
   return false;
  }
  ++boundaries; return true;
 };
 for (uint seed = 0; seed < 32; ++seed) {
  _runner.resetGlobals(); _runner.seedRandom(0x1234567U ^ (seed*0x9e3779b9U)); _runner.defineValue(0,46,seed >= 2); _puzzlesCompleted = 10;
  if (!loadPlace(530)) return false;
  now = scriptClock(); if (_runner.enqueueStartup(_scene.scripts,now,true) != 11 || !settle(now)) return false;
  for (uint round = 1; round <= 3; ++round) {
   int32 scenario = 0,count = 0; _runner.getValue(1,9,scenario); _runner.getValue(1,13,count);
   if (scenario < 1 || scenario > 5 || count != int32(round)) return false;
   seen[round-1] |= 1U << (scenario-1);
   if (!roundTrip(12)) return false;
   const int orders[6][3] = {{0,1,2},{1,0,2},{0,2,1},{1,2,0},{2,0,1},{2,1,0}};
   const int lastBAnswers[] = {2,1,5,4,4}; int wrong = 1;
   while (wrong == answers[scenario-1] || wrong == lastBAnswers[scenario-1]) ++wrong;
   for (int component : orders[seed%6]) {
    if (!component) { if (!roundTrip(2) || !roundTrip(3) || (seed == 0 && round == 2 && !roundTrip(12,true))) return false; }
    else if (component == 1) { if (!roundTrip(4) || !roundTrip(5)) return false; }
    else if (!roundTrip(wrong+5) || !roundTrip(11)) return false;
   }
   const int answer = answers[scenario-1];
   for (int choice = 1; choice <= 5; ++choice) if (choice != answer && (!roundTrip(choice+5) || !roundTrip(11))) return false;
   if (!roundTrip(answer+5) || !roundTrip(11)) return false;
   if (round < 3) {
    if (!roundTrip(answer+5) || !roundTrip(11) || !roundTrip(1)) return false;
   }
  }
  int32 solved = 0; if (_place != 228 || !_runner.getValue(0,46,solved) || solved != 1 || _puzzlesCompleted != 10) { debug("P530 route completion failed seed %u P%d solved %d count %u",seed,_place,solved,_puzzlesCompleted); return false; }
  ++routes;
  if (seed >= 7 && seen[0] == 31 && seen[1] == 31 && seen[2] == 31 && pictures == 0x1ffffffU) break;
 }
 debug("P530 save coverage: routes %u rounds %x/%x/%x pictures %x fixture %u",routes,seen[0],seen[1],seen[2],pictures,uint(fixture.size()));
 if (seen[0] != 31 || seen[1] != 31 || seen[2] != 31 || pictures != 0x1ffffffU || fixture.empty()) return false;
 if (!restore(fixture)) return false; now = scriptClock(); if (!roundTrip(0)) return false;
 if (!loadPlace(117)) return false; const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) { Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false; }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) { damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1; }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,16,18,19,22,25,28,30,31,33,34,1095,1096,1097,1122,1125,1128,1131,1134,1397};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kP530Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("P530 invalid word accepted %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveP530() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveP530() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[0].selectedFrame = 1; if (canSaveP530() || !restore(fixture)) return false;
 moveSprite(_scene.sprites[23],466,295); if (canSaveP530() || !restore(fixture)) return false;
 if (!stageBackgroundImage(kP530Images[1],460,10) || canSaveP530()) return false;
 _pendingImage.free(); _pendingImageName.clear();
 if (!stageBackgroundImage(kP530Images[1],0,0)) return false; displayBackgroundImage(); if (canSaveP530() || !restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP530()) return false;
 Common::Array<byte> ambient; if (!snapshot(ambient,scriptClock()) || !restore(ambient) || !_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType)) return false;
 _mixer->stopHandle(_soundHandle); if (!playSound(1,scriptClock()) || canSaveP530()) return false; _mixer->stopHandle(_soundHandle);
 debug("Astronomica P530 saves: PASS (%u round trips, %u solve routes, five scenarios at each round, 25 pictures, 5604 truncations, 5604 corruptions, 31 invalid states, partial components/RNG/music guards)",boundaries,routes);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyP528Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state,sprites; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),_p528EarthImage,_p528MoonImage,_p528TallMoon,uint32(_p528HistoryValid),
       screenRGBHash(_background,480),screenRGBHash(_screen,480),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto snapshot = [&](Common::Array<byte> &bytes, uint32 now) {
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 3444) return false;
  bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size()); return true;
 };
 auto execute = [&](int button, uint32 &now) {
  if (_place != 528) return false;
  const int x = button ? 299 : 24, y = !button ? 417 : button == 4 ? 369 : button == 5 ? 404 : 439;
  if (spriteAt(x,y) != (button ? button : 1)) return false;
  clickAtTime(x,y,now); if (canSaveP528()) return false;
  for (uint n = 0; n < 10000 && _place == 528 && _runner.pendingCount(); ++n) { runScriptsAt(now); animateSpritesAt(now); now += 20; }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP528()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle();
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 7) {
  debug("Astronomica P528 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); int32 flag = 0;
  bool ok = canSaveP528() && _p528MoonImage == 12 && _p528TallMoon == 1 && _runner.getValue(1,3,flag) && flag == 1;
  ok = execute(5,now) && execute(6,now) && ok;
  ok = ok && _place == 526 && _runner.getValue(0,44,flag) && flag == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P528 startup save: %s (retained moon row, partial eclipse and completion)",ok ? "PASS" : "FAIL"); return ok;
 }
 _runner.resetGlobals(); _runner.seedRandom(528); _runner.defineValue(0,44,1); _puzzlesCompleted = 10;
 if (!loadPlace(528) || !canSaveP528()) { debug("P528 initial admission failed"); return false; }
 struct Node { Common::Array<byte> bytes; uint32 now; Common::String key; };
 Common::Array<Node> nodes;
 auto key = [&]() {
  int32 p = 0,q = 0,a = 0,b = 0; _runner.getValue(1,0,p); _runner.getValue(1,1,q); _runner.getValue(1,3,a); _runner.getValue(1,4,b);
  return Common::String::format("%d,%d,%d,%d,%u,%u",p,q,a,b,_p528MoonImage,_p528TallMoon);
 };
 auto enqueue = [&](uint32 now) {
  const Common::String value = key(); for (const Node &n : nodes) if (n.key == value) return true;
  Node n; n.now = now; n.key = value; if (!snapshot(n.bytes,now)) return false; nodes.push_back(n); return true;
 };
 if (!enqueue(scriptClock())) return false;
 uint boundaries = 0, completions = 0, exits = 0; Common::Array<byte> fixture;
 for (uint index = 0; index < nodes.size(); ++index) {
  const Node node = nodes[index];
  for (int action : {4,5,6,0}) {
   if (!restore(node.bytes) || !canSaveP528()) return false;
   uint32 now = node.now; const uint32 before = fingerprint();
   if (fixture.empty() && _p528MoonImage == 12 && _p528TallMoon == 1 && node.key.hasPrefix("0,0,1,0,")) {
    _runner.defineValue(0,44,0);
    if (!snapshot(fixture,now) || saveGameState(7,"P528 continuation regression").getCode() != Common::kNoError) return false;
    debug("Astronomica P528 slot fingerprint: %08x",fingerprint());
    _runner.defineValue(0,44,1);
   }
   const uint soundsBefore = _soundsStarted;
   if (!execute(action,now)) { debug("P528 action failed at %s/%d",node.key.c_str(),action); return false; }
   const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
   const Common::String nextKey = _place == 528 ? key() : Common::String("-");
   debug("Astronomica P528 save edge: %s / %d -> P%d %s",node.key.c_str(),action,_place,nextKey.c_str());
   if (_place == 528) { if (!canSaveP528() || !enqueue(now)) return false; }
   else if (action) { if (_place != 526) return false; ++completions; }
   else { if (_place != 268) return false; ++exits; }
   if (!loadPlace(117)) return false;
   _runner.seedRandom(88); _runner.defineValue(0,44,123); const uint loadSounds = _soundsStarted;
   ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(node.bytes); ConfMan.setBool("astronomica_entry_scripts",false);
   if (!loaded || !canSaveP528() || fingerprint() != before || _soundsStarted != loadSounds) { debug("P528 restore failed at %s/%d",node.key.c_str(),action); return false; }
   Common::Array<byte> again; if (!snapshot(again,node.now) || again.size() != node.bytes.size()) return false;
   for (uint i = 8; i < again.size()-4; ++i) if ((i < 16 || i >= 20) && again[i] != node.bytes[i]) return false;
   now = node.now;
   if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || _lastSound != last) {
    debug("P528 continuation failed at %s/%d",node.key.c_str(),action); return false;
   }
   ++boundaries;
  }
 }
 if (nodes.size() != 160 || boundaries != 640 || completions != 6 || exits != 160 || fixture.empty()) return false;
 if (!loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,14,16,18,19,22,25,28,30,31,33,34,555,556,557,558,561,564,567,857};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kP528Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("P528 invalid word accepted %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 for (const char *option : {"astronomica_audio","astronomica_animation","astronomica_sprite_input"}) {
  ConfMan.setBool(option,false); if (canSaveP528() || restore(fixture)) return false;
  ConfMan.removeKey(option,ConfMan.getActiveDomainName()); if (canSaveP528() || restore(fixture)) return false;
  ConfMan.setBool(option,true);
 }
 _scene.sprites[4].selectedFrame = 1; if (canSaveP528()) return false;
 if (!restore(fixture) || !stageBackgroundImage("ge_s1",87,356) || canSaveP528()) return false;
 _pendingImage.free(); _pendingImageName.clear();
 if (!stageBackgroundImage("ge_s1",0,0)) return false;
 displayBackgroundImage(); if (canSaveP528() || !restore(fixture)) return false;
 _p528TallMoon = 11; if (canSaveP528() || !restore(fixture)) return false;
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP528()) return false;
 Common::Array<byte> ambient; if (!snapshot(ambient,scriptClock()) || !restore(ambient) || !_mixer->isSoundHandleActive(_soundHandle) || !_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType)) return false;
 _mixer->stopHandle(_soundHandle);
 if (!playSound(1,scriptClock()) || canSaveP528()) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P528 saves: PASS (%u reachable states, %u round trips, %u completion edges, %u exits, 3444 truncations, 3444 corruptions, 30 invalid states, music/foreground guards)",uint(nodes.size()),boundaries,completions,exits);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyAudioChannels() {
 const Audio::Mixer::SoundType music = Audio::Mixer::kMusicSoundType, effects = Audio::Mixer::kSFXSoundType;
 const int oldMusicVolume = _mixer->getVolumeForSoundType(music), oldEffectsVolume = _mixer->getVolumeForSoundType(effects);
 const bool oldMusicMute = _mixer->isSoundTypeMuted(music), oldEffectsMute = _mixer->isSoundTypeMuted(effects);
 _mixer->setVolumeForSoundType(music,0); _mixer->muteSoundType(music,true);
 _mixer->setVolumeForSoundType(effects,Audio::Mixer::kMaxMixerVolume); _mixer->muteSoundType(effects,false);
 uint loops = 0, foregrounds = 0; bool ok = true;
 for (int place : {505,508,519,524,526,528}) {
  if (!loadPlace(place)) { ok = false; break; }
  _mixer->stopHandle(_soundHandle);
  const bool loopOK = playSound(0,scriptClock(),true) && _mixer->isSoundHandleActive(_soundHandle) &&
   _mixer->hasActiveChannelOfType(music) && !_mixer->hasActiveChannelOfType(effects) &&
   _mixer->isSoundTypeMuted(music) && _mixer->getVolumeForSoundType(music) == 0;
  loops += loopOK;
  const bool foregroundOK = playSound(1,scriptClock()) && _mixer->isSoundHandleActive(_soundHandle) &&
   _mixer->hasActiveChannelOfType(effects) && !_mixer->hasActiveChannelOfType(music) &&
   !_mixer->isSoundTypeMuted(effects) && _mixer->getVolumeForSoundType(effects) == Audio::Mixer::kMaxMixerVolume &&
   _mixer->isSoundTypeMuted(music) && _mixer->getVolumeForSoundType(music) == 0;
  foregrounds += foregroundOK; ok = loopOK && foregroundOK && ok;
  debug("Astronomica P%d audio channels: music %s, foreground %s",place,loopOK ? "PASS" : "FAIL",foregroundOK ? "PASS" : "FAIL");
  _mixer->stopHandle(_soundHandle);
 }
 _mixer->setVolumeForSoundType(music,oldMusicVolume); _mixer->muteSoundType(music,oldMusicMute);
 _mixer->setVolumeForSoundType(effects,oldEffectsVolume); _mixer->muteSoundType(effects,oldEffectsMute);
 const bool restored = _mixer->getVolumeForSoundType(music) == oldMusicVolume && _mixer->isSoundTypeMuted(music) == oldMusicMute &&
  _mixer->getVolumeForSoundType(effects) == oldEffectsVolume && _mixer->isSoundTypeMuted(effects) == oldEffectsMute;
 ok = ok && loops == 6 && foregrounds == 6 && restored;
 debug("Astronomica audio channel verification: %s (%u muted music loops, %u foreground replacements, controls %s)",ok ? "PASS" : "FAIL",loops,foregrounds,restored ? "restored" : "FAIL");
 _runner.resetGlobals(); return loadPlace(103) && ok;
}
bool AstronomicaEngine::verifyPresentation() {
 const bool hadOverlay = ConfMan.hasKey("astronomica_debug_overlay");
 const bool oldOverlay = hadOverlay && ConfMan.getBool("astronomica_debug_overlay");
 ConfMan.setBool("astronomica_debug_overlay",false);
 uint scenes = 0, originalPixels = 0; bool ok = true;
 for (int place : {0,1,29,103,425,505,508,519,524,526,528,537}) {
  if (!loadPlace(place)) return false;
  Common::File file;
  if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::String::format("PLACES/P%d/MEGAFILE.HYP",place))))) return false;
  Graphics::Surface expected; expected.copyFrom(_background);
  renderStaticSprites(file,_scene,expected);
  presentScene(); presentScene();
  uint mismatches = 0;
  for (int y = 0; y < 480; ++y) for (int x = 0; x < 640; ++x) if (_screen.getPixel(x,y) != expected.getPixel(x,y)) {
   if (!mismatches) debug("Presentation mismatch P%d at %d,%d: actual %08x expected %08x",place,x,y,_screen.getPixel(x,y),expected.getPixel(x,y));
   ++mismatches;
  }
  ok = !mismatches && ok;
  expected.free(); ++scenes;
 }
 if (!loadPlace(528)) return false;
 Graphics::Surface *original = openBackgroundImage("ge_s1",528);
 if (!original || original->w != 171 || original->h != 105) { if (original) { original->free(); delete original; } return false; }
 if (!stageBackgroundImage("ge_s1",87,356)) { original->free(); delete original; return false; }
 displayBackgroundImage();
 for (int y = 100; y < 105; ++y) for (int x = 0; x < 171; ++x) {
  ok = _screen.getPixel(87+x,356+y) == original->getPixel(x,y) && ok; ++originalPixels;
 }
 const uint32 normal = screenRGBHash(_screen,480);
 ConfMan.setBool("astronomica_debug_overlay",true); presentScene();
 const bool debugVisible = screenRGBHash(_screen,480) != normal;
 ConfMan.setBool("astronomica_debug_overlay",false); redrawSprites();
 const bool recovered = screenRGBHash(_screen,480) == normal;
 debug("Presentation strip checks: visible %d recovered %d",debugVisible,recovered);
 original->free(); delete original;
 if (hadOverlay) ConfMan.setBool("astronomica_debug_overlay",oldOverlay);
 else ConfMan.removeKey("astronomica_debug_overlay",ConfMan.getActiveDomainName());
 ok = ok && scenes == 12 && originalPixels == 855 && debugVisible && recovered;
 debug("Astronomica full-height presentation: %s (%u scenes, %u original P528 pixels, optional strip and recovery)",ok ? "PASS" : "FAIL",scenes,originalPixels);
 _runner.resetGlobals(); return loadPlace(103) && ok;
}
bool AstronomicaEngine::verifyP526Saves() {
 auto fingerprint = [&]() {
  Common::Array<uint32> state; if (!_runner.exportIdleState(state)) return uint32(0);
  uint32 hash = (2166136261U ^ uint32(_place))*16777619U;
  // The successor can enter another scene after synchronous audio. Its
  // fresh program epoch follows real playback time rather than simulated
  // test time. Restore equality still checks every serialized word below.
  for (uint i = 0; i <= 600; ++i) hash = (hash ^ state[i])*16777619U;
  Common::Array<uint32> sprites;
  for (const Sprite &s : _scene.sprites) p526SpriteWords(s,sprites);
  for (uint32 v : sprites) hash = (hash ^ v)*16777619U;
  for (const HoverTarget &h : _hoverRects) hash = (hash ^ uint32(h.entered))*16777619U;
  for (uint32 v : {_puzzlesCompleted,uint32(_previousPlace),screenRGBHash(_background),screenRGBHash(_screen)}) hash = (hash ^ v)*16777619U;
  return hash;
 };
 auto settle = [&](uint32 &now) {
  for (uint n = 0; n < 10000 && (_runner.pendingCount() || (_place == 526 && _scene.sprites[19].autoMove)); ++n) {
   runScriptsAt(now); animateSpritesAt(now); now += 10;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound && canSaveP526()) return false;
  _mixer->stopHandle(_soundHandle); return _runner.idle() && (_place != 526 || !_scene.sprites[19].autoMove);
 };
 auto execute = [&](int action, uint32 &now) {
  if (action == -2) { animateSpritesAt(now); return true; }
  if (action < 0) return true;
  if (_place != 526) return false;
  int x = action == 6 ? 250 : 24, y = action == 6 ? 380 : 417;
  if (action < 6) { const MouseRect &r = _scene.mouseRects[action]; x = (r.rect[0]+r.rect[2])/2; y = (r.rect[1]+r.rect[3])/2; }
  clickAtTime(x,y,now);
  if (canSaveP526()) return false;
  return settle(now);
 };
 auto restore = [&](const Common::Array<byte> &bytes) {
  Common::MemoryReadStream in(&bytes[0],bytes.size()); return loadGameStream(&in).getCode() == Common::kNoError;
 };
 auto answer = [&](bool correct) {
  int32 scenario = 0; _runner.getValue(1,2,scenario);
  int choice = 1; while (choice <= 6 && orbitAnswer(scenario,_scene.sprites[17].selectedFrame,choice) != correct) ++choice;
  return choice <= 6 ? choice-1 : -1;
 };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 6) {
  debug("Astronomica P526 slot fingerprint: %08x",fingerprint());
  uint32 now = scriptClock(); bool ok = canSaveP526();
  for (uint n = 0; n < 6 && ok && _place == 526; ++n) {
   const int choice = answer(true); ok = choice >= 0 && execute(choice,now);
   if (ok && _place == 526) ok = execute(6,now);
  }
  int32 solved = 0; ok = ok && _place == 268 && _runner.getValue(0,42,solved) && solved == 1 && _puzzlesCompleted == 11;
  debug("Astronomica P526 startup save: %s (stopped orbit, all remaining answers)",ok ? "PASS" : "FAIL"); return ok;
 }
 uint32 now = 0; uint boundaries = 0, animations = 0, answerCases = 0; Common::Array<byte> fixture, initialFixture, scenarios[6];
 auto start = [&](uint seed, bool solved) {
  _runner.resetGlobals(); _runner.seedRandom(seed); _runner.defineValue(0,42,solved); _puzzlesCompleted = 10;
  if (!loadPlace(526)) return false;
  now = scriptClock();
  if (!canSaveP526()) { debug("P526 initial save rejected"); return false; }
  return true;
 };
 auto roundTrip = [&](int action, bool physical) {
  if (action >= 0 && action < 6) {
   const MouseRect &r = _scene.mouseRects[action]; hoverAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);
   if (!settle(now)) return false;
  }
  if (!canSaveP526()) { debug("P526 boundary rejected: %u",boundaries); return false; }
  _pausedMillis = _system->getMillis()-now;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  if (saveGameStream(&out).getCode() != Common::kNoError || out.size() != 4956) return false;
  Common::Array<byte> bytes; bytes.resize(out.size()); memcpy(&bytes[0],out.getData(),out.size());
  const uint32 before = fingerprint(), savedNow = now;
  if (initialFixture.empty()) initialFixture = bytes;
  if (action >= 0 && action < 6) {
   int32 scenario = 0, phase = 0; _runner.getValue(1,2,scenario); _runner.getValue(1,3,phase);
   if (!phase && scenario >= 1 && scenario <= 6 && scenarios[scenario-1].empty()) scenarios[scenario-1] = bytes;
  }
  if (physical) {
   fixture = bytes;
   if (saveGameState(6,"P526 continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica P526 slot fingerprint: %08x",before);
  }
  const uint soundsBefore = _soundsStarted;
  if (!execute(action,now)) { debug("P526 action failed: %u %d",boundaries,action); return false; }
  const uint32 after = fingerprint(); const uint sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!loadPlace(117)) return false;
  _runner.seedRandom(88); _runner.defineValue(0,42,123);
  const uint loadSounds = _soundsStarted;
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(bytes); ConfMan.setBool("astronomica_entry_scripts",false);
  if (!loaded || !canSaveP526() || fingerprint() != before || _soundsStarted != loadSounds) {
   debug("P526 restore mismatch: %u loaded %d before %08x actual %08x",boundaries,loaded,before,fingerprint()); return false;
  }
  now = savedNow;
  if (action >= 0 && action < 6) {
   const MouseRect &r = _scene.mouseRects[action]; hoverAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);
   if (!_runner.idle() || fingerprint() != before || _soundsStarted != loadSounds) return false;
  }
  Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);
  if (saveGameStream(&again).getCode() != Common::kNoError || again.size() != bytes.size()) return false;
  for (uint i = 8; i < bytes.size()-4; ++i) if ((i < 16 || i >= 20) && again.getData()[i] != bytes[i]) return false;
  if (!execute(action,now) || fingerprint() != after || _soundsStarted-loadSounds != sounds || (action >= 0 && _lastSound != last)) {
   debug("P526 continuation mismatch: %u action %d",boundaries,action); return false;
  }
  ++boundaries; return true;
 };
 for (uint route = 0; route < 4; ++route) {
  if (!start(111+route,route == 1)) return false;
  uint seen = 0, answers = 0;
  if (!roundTrip(-1,false)) return false;
  if (route == 3) { if (!roundTrip(7,false)) return false; }
  else for (uint n = 0; n < 6 && _place == 526; ++n) {
   if (!roundTrip(6,false)) return false;
   int32 scenario = 0; _runner.getValue(1,2,scenario); seen |= 1U << (scenario-1);
   if (route == 0 && n == 0 && !roundTrip(-1,true)) return false;
   const int choice = answer(route != 2);
   if (choice < 0 || !roundTrip(choice,false)) return false;
   ++answers;
  }
  int32 solved = -1;
  if (_place != 268 || !_runner.getValue(0,42,solved) || solved != int(route < 2) || _puzzlesCompleted != 10+uint(route == 0) ||
      (route < 2 && (seen != 63 || answers != 6)) || (route == 2 && answers != 4)) return false;
 }
 debug("Astronomica P526 save routes: PASS (six scenarios, two solve routes, four errors, voluntary exit and hover continuity)");
 // Separate synthetic phase/answer matrix: the six scene states come from
 // real routes; each loaded phase frame is varied explicitly. This is not
 // a claim that all twelve frames occur naturally at every orbital stop.
 for (uint scenario = 0; scenario < 6; ++scenario) for (uint frame = 0; frame < 12; ++frame) for (uint choice = 0; choice < 6; ++choice) {
  if (scenarios[scenario].empty() || !restore(scenarios[scenario])) return false;
  // Route tests above check first success/counting and the real victory
  // voice. Use the original already-solved branch for this phase matrix
  // instead of waiting for that same synchronous voice another 144 times.
  _runner.defineValue(0,42,1);
  _scene.sprites[17].selectedFrame = frame; now = scriptClock(); redrawSprites();
  if (!roundTrip(choice,false)) return false;
  ++answerCases;
 }
 debug("Astronomica P526 save answer matrix: PASS (%u synthetic phase/answer continuations)",answerCases);
 // Compare actual first post-load animation updates, including hidden sprites.
 for (uint i : {17U,19U,21U}) for (uint frame = 0; frame < 12; ++frame)
  for (uint32 epoch : {1000U,0xfffffff0U}) for (uint32 extra : {0U,1U,1000U}) {
   if (!restore(initialFixture)) return false;
   const uint32 period = i == 17 ? 100 : 30;
   _scene.sprites[i].selectedFrame = frame; _scene.sprites[i].frameSince = epoch;
   now = epoch+period-1+extra; redrawSprites();
   if (!roundTrip(-2,false)) return false;
   if (_scene.sprites[i].selectedFrame != int(extra ? (frame+1)%12 : frame) ||
       _scene.sprites[i].frameSince != (extra ? now : epoch)) return false;
   ++animations;
  }
 if (fixture.empty() || !loadPlace(117)) return false;
 const uint32 unchanged = fingerprint();
 for (uint length = 0; length < fixture.size(); ++length) {
  Common::MemoryReadStream in(&fixture[0],length);
  if (loadGameStream(&in).getCode() == Common::kNoError || fingerprint() != unchanged) return false;
 }
 Common::Array<byte> damaged = fixture;
 for (uint offset = 0; offset < damaged.size(); ++offset) {
  damaged[offset] ^= 1; if (restore(damaged) || fingerprint() != unchanged) return false; damaged[offset] ^= 1;
 }
 const uint invalidWords[] = {0,3,4,5,7,8,9,10,11,12,13,16,18,19,22,25,28,30,31,33,34,633+300,633+301,633+302,1235};
 for (uint index : invalidWords) {
  damaged = fixture; WRITE_LE_UINT32(&damaged[8+index*4],0x80000000U);
  uint32 hash = 2166136261U; for (uint i = 0; i < kP526Words; ++i) hash = (hash ^ READ_LE_UINT32(&damaged[8+i*4]))*16777619U;
  WRITE_LE_UINT32(&damaged[damaged.size()-4],hash);
  if (restore(damaged) || fingerprint() != unchanged) { debug("P526 invalid word accepted: %u",index); return false; }
 }
 if (!restore(fixture)) return false;
 ConfMan.setBool("astronomica_animation",false);
 if (canSaveP526() || restore(fixture)) return false;
 ConfMan.removeKey("astronomica_animation",ConfMan.getActiveDomainName());
 if (canSaveP526() || restore(fixture)) return false;
 ConfMan.setBool("astronomica_animation",true);
 ConfMan.setBool("astronomica_sprite_input",false);
 if (canSaveP526() || restore(fixture)) return false;
 ConfMan.removeKey("astronomica_sprite_input",ConfMan.getActiveDomainName());
 if (canSaveP526() || restore(fixture)) return false;
 ConfMan.setBool("astronomica_sprite_input",true);
 _scene.sprites[4].selectedFrame = 1; if (canSaveP526()) return false; _scene.sprites[4].selectedFrame = 0;
 _scene.sprites[19].autoMove = true; if (canSaveP526()) return false; _scene.sprites[19].autoMove = false;
 if (!stageBackgroundImage("s1",90,361) || canSaveP526()) return false;
 _pendingImage.free(); _pendingImageName.clear(); _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,scriptClock(),true) || !canSaveP526()) return false;
 Common::MemoryWriteStreamDynamic music(DisposeAfterUse::YES);
 if (saveGameStream(&music).getCode() != Common::kNoError) return false;
 Common::MemoryReadStream musicIn(music.getData(),music.size());
 if (loadGameStream(&musicIn).getCode() != Common::kNoError || !_mixer->isSoundHandleActive(_soundHandle) || _lastSound != 0) return false;
 _mixer->stopHandle(_soundHandle);
 debug("Astronomica P526 saves: PASS (%u boundaries, %u animation cases, %u answer cases, 4956 truncations, 4956 corruptions, 25 invalid states, motion/music/foreground guards)",boundaries,animations,answerCases);
 _runner.resetGlobals(); return loadPlace(103);
}
bool AstronomicaEngine::verifyLegacySaves() {
 const bool oldChecked = _legacyChecked, oldAvailable = _legacyAvailable;
 const LegacySaveState oldLegacy = _legacyState; const uint oldCompleted = _puzzlesCompleted;
 bool ok = true;
 auto parse = [](const Common::String &text, LegacySaveState &state) {
  Common::MemoryReadStream stream((const byte *)text.c_str(),text.size()); return readLegacySave(stream,state);
 };
 auto hash = [](const LegacySaveState &state) {
  uint32 h = (2166136261U ^ state.place)*16777619U; h = (h ^ state.completed)*16777619U;
  for (int32 value : state.globals) h = (h ^ uint32(value))*16777619U; return h;
 };
 // Expected words were obtained by executing the original writer/reader.
 struct Original { uint place, completed; uint32 hash; };
 const Original originals[] = {{117,12,0xd96ac188U},{523,31,0xb7b0beebU},{524,40,0xc7df18fdU},{523,0,0x637eb45aU},{1,0,0xc0379758U}};
 for (const Original &original : originals) for (const char *separator : {"\n","\r\n"," \t"}) {
  Common::String text = Common::String::format("%u%s%u%s",original.place,separator,original.completed,separator);
  for (uint i = 0; i < 100; ++i) text += Common::String::format("%d%s",int32(i*0x01020304U ^ 0xa5a5a5a5U),separator);
  LegacySaveState state; ok = parse(text,state) && hash(state) == original.hash && ok;
 }
 debug("Astronomica legacy original payloads: %s",ok ? "PASS" : "FAIL");
 LegacySaveState initial; initial.place = 103; initial.completed = 7; initial.globals[99] = 1234;
 Common::String valid = "103\n7\n";
 for (uint i = 0; i < 100; ++i) valid += Common::String::format("%d\n",initial.globals[i]);
 // Truncation at each token boundary cannot silently produce partial state.
 uint boundary = 0;
 for (uint count = 0; count < 102; ++count) {
  LegacySaveState state = initial;
  ok = !parse(valid.substr(0,boundary),state) && hash(state) == hash(initial) && ok;
  while (boundary < valid.size() && valid[boundary++] != '\n') {}
 }
 for (const char *bad : {"","-","+","2147483648","-2147483649","12x","0x10","1e2"}) {
  LegacySaveState state = initial;
  ok = !parse(Common::String(bad)+valid.substr(3),state) && hash(state) == hash(initial) && ok;
 }
 for (const Common::String &bad : {valid+"0",valid+"garbage",Common::String(8193,'0')}) {
  LegacySaveState state = initial; ok = !parse(bad,state) && hash(state) == hash(initial) && ok;
 }
 LegacySaveState extremes;
 Common::String signedText = "+103\v+7\f";
 for (uint i = 0; i < 100; ++i) signedText += (i%2 ? "-2147483648 " : "+2147483647 ");
 ok = parse(signedText,extremes) && extremes.globals[0] == 2147483647 && uint32(extremes.globals[1]) == 0x80000000U && ok;
 if (ConfMan.hasKey("astronomica_verify_legacy_directory")) {
  const Common::Path fixturePath = ConfMan.getPath("astronomica_verify_legacy_directory");
  const Common::FSNode fixtureDirectory(fixturePath); LegacySaveState fileState;
  ok = readLegacyDirectory(fixtureDirectory,fileState) == kLegacyLoaded && hash(fileState) == hash(initial) && ok;
  fileState = initial;
  ok = readLegacyDirectory(fixtureDirectory.getChild("missing"),fileState) == kLegacyMissing && hash(fileState) == hash(initial) && ok;
  ok = readLegacyDirectory(fixtureDirectory.getChild("invalid"),fileState) == kLegacyInvalid && hash(fileState) == hash(initial) && ok;
  // Exercise the actual startup discovery against a dedicated fixture tree.
  const Common::Path gamePath = ConfMan.getPath("path");
  ConfMan.setPath("path",fixturePath); _legacyChecked = false; _legacyAvailable = false;
  prepareLegacyResume();
  ok = _legacyChecked && _legacyAvailable && hash(_legacyState) == hash(initial) && gameStateContext().resume && ok;
  ConfMan.setPath("path",gamePath);
  _legacyChecked = oldChecked; _legacyAvailable = oldAvailable; _legacyState = oldLegacy;
 }
 debug("Astronomica legacy parser checks: %s",ok ? "PASS" : "FAIL");
 _runner.resetGlobals(); ok = loadPlace(117) && ok;
 _runner.defineValue(0,99,5678); _puzzlesCompleted = 9;
 for (uint destination : {0U,1U,26U,408U,409U,423U,437U,523U,538U,0xffffffffU}) {
  LegacySaveState unsupported = initial; unsupported.place = destination;
  ok = !restoreLegacyState(unsupported) && _place == 117 && _puzzlesCompleted == 9 && ok;
  int32 value = 0; ok = _runner.getValue(0,99,value) && value == 5678 && ok;
 }
 for (int mode : {1,2}) {
  LegacySaveState active = initial; active.globals[8] = 100; active.globals[60] = mode;
  ok = !restoreLegacyState(active) && _place == 117 && _puzzlesCompleted == 9 && ok;
 }
 ok = restoreLegacyState(initial) && _place == 103 && _puzzlesCompleted == 7 && !_runner.clicksBlocked() && ok;
 for (uint i = 0; i < 100; ++i) { int32 value = 0; ok = _runner.getValue(0,i,value) && value == initial.globals[i] && ok; }
 // Import can subsequently be saved and restored as a normal ScummVM slot.
 Common::MemoryWriteStreamDynamic native(DisposeAfterUse::YES);
 ok = saveGameStream(&native).getCode() == Common::kNoError && native.size() == 424 && ok;
 ok = loadPlace(117) && ok;
 Common::MemoryReadStream nativeInput(native.getData(),native.size());
 ok = loadGameStream(&nativeInput).getCode() == Common::kNoError && _place == 103 && _puzzlesCompleted == 7 && ok;
 debug("Astronomica legacy state checks: %s",ok ? "PASS" : "FAIL");
 // Original P1 flow: Start with a saved game opens the original choice;
 // its second button dispatches custom33 after its sound/delay.
 _legacyChecked = true; _legacyAvailable = true; _legacyState = initial;
 ok = loadPlace(1) && ok; _runner.enqueueStartup(_scene.scripts,0,true);
 for (uint32 now = 0; now <= 500; now += 10) runScriptsAt(now);
 int32 resume = 0; ok = _runner.getValue(1,1,resume) && resume == 1 && ok;
 const Sprite &start = _scene.sprites[2]; clickAtTime(start.renderX+10,start.renderY+10,510);
 for (uint32 now = 510; now <= 1500; now += 10) runScriptsAt(now);
 ok = _place == 1 && !_runner.clicksBlocked() && ok;
 const Sprite &button = _scene.sprites[1];
 ok = spriteAt(button.renderX+10,button.renderY+10) == 1 && _runner.canRun(button.click,true) && ok;
 clickAtTime(button.renderX+10,button.renderY+10,1510);
 for (uint32 now = 1510; now <= 5000 && _place == 1; now += 10) runScriptsAt(now);
 ok = _place == 103 && _puzzlesCompleted == 7 && !_runner.clicksBlocked() && !_runner.pendingCount() && ok;
 Script command; Command c; c.opcode = 23; for (int arg : {33,0,0,0,0,0}) c.args.push_back(arg); command.push_back(c);
 ok = !_runner.canRun(command,true) && ok;
 _legacyAvailable = false; ok = loadPlace(1) && !_runner.canRun(command,true) && ok;
 _legacyAvailable = true; ok = loadPlace(1) && _runner.canRun(command,true) && ok;
 command[0].args[1] = 1; ok = !_runner.canRun(command,true) && ok;
 _legacyChecked = oldChecked; _legacyAvailable = oldAvailable; _legacyState = oldLegacy;
 _puzzlesCompleted = oldCompleted; _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica legacy save verification: %s (15 original payloads, 102 token truncations, signed bounds, inactive import, native resave, original menu control, rejected active clocks/destinations)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyHelp() {
 bool ok = ensureHelpBook();
 debug("Astronomica help decoded: %u articles, %u records, %08x, %u keywords, %u references",
  _helpBook.articles.size(),_helpBook.recordCount,_helpBook.recordHash,_helpBook.keywordCount,_helpBook.referenceCount);
 ok = _helpBook.articles.size() == 782 && _helpBook.recordCount == 2117 &&
  _helpBook.recordHash == 0x2cab83c0U && _helpBook.keywordCount == 812 && _helpBook.referenceCount == 2008 && ok;
 debug("Astronomica help format: %u records, %u commands, %08x",_helpBook.formatRecords,_helpBook.formatCommands,_helpBook.formatHash);
 ok = _helpBook.formatRecords == 1335 && _helpBook.formatCommands == 11455 && _helpBook.formatHash == 0xb5265663U && ok;
 struct SearchCase { const char *query; uint count; uint32 hash; };
 const SearchCase cases[] = {{"",781,0x1f4fa2cfU},{"a.u.",1,0xc40bf6ccU},{"moon",24,0xeaecb450U},
  {"MERCURY",9,0x134d50bfU},{"xyz-no-such-article",0,0x811c9dc5U}};
 for (const SearchCase &c : cases) {
  const Common::Array<uint> results = _helpBook.search(c.query); uint32 hash = 2166136261U;
  for (uint index : results) hash = (hash ^ index)*16777619U;
  ok = results.size() == c.count && hash == c.hash && ok;
  debug("Astronomica help search '%s': %u, %08x",c.query,results.size(),hash);
 }
 if (!ok) return false;
 if (ConfMan.hasKey("astronomica_verify_help_ui")) {
  PauseToken paused = pauseEngine();
  const bool ui = verifyHelpBookUI(_helpBook,ConfMan.getPath("astronomica_verify_help_ui"));
  debug("Astronomica help UI capture: %s",ui ? "PASS" : "FAIL"); ok = ui && ok;
 }
 Common::File file;
 if (!file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("HELP/ASTRONOM.HLP"))))) return false;
 Common::Array<byte> bytes; bytes.resize(uint(file.size())); if (file.read(&bytes[0],bytes.size()) != bytes.size()) return false;
 // Reject invalid image types in every original bitmap stream. Failed loads
 // must preserve both the text and every image in the previously loaded book.
 const uint imageTypeOffsets[] = {0x53942,0x55fa8,0x589c8,0x5b515,0x631aa,0x67cde,0x687bf,0x6aef4,0x70bda,0x72b54,0x74e1c,0x79937,0x7dfc6,0x85ac7,0x88021,0x8aa2c,0x8df2a,0x91efa,0x944b6,0x96bb4,0x991c5,0xa139f,0xa5d40,0xaab33,0xae1bb,0xaf5a8,0xb4640,0xbc6c2,0xbf6aa,0xc286a,0xc52b4};
 bool imageOK = verifyHelpImages(_helpBook);
 for (uint offset : imageTypeOffsets) {
  const byte before = bytes[offset]; bytes[offset] = 0xff;
  Common::MemoryReadStream damaged(&bytes[0],bytes.size());
  imageOK = !_helpBook.load(damaged) && verifyHelpImages(_helpBook) && imageOK; bytes[offset] = before;
 }
 struct ImageDamage { uint offset; byte value; };
 const ImageDamage imageDamage[] = {{0x53943,0xff},{0x53944,0x0},{0x53948,0x0},{0x53949,0x0},{0x5394a,0x0},{0x5394c,0x0},{0x53951,0x0},{0x53955,0xff},{0x53935,0xff},{0x53936,0xff}};
 for (const ImageDamage &damage : imageDamage) {
  const byte before = bytes[damage.offset]; bytes[damage.offset] = damage.value;
  Common::MemoryReadStream damaged(&bytes[0],bytes.size());
  const bool rejected = !_helpBook.load(damaged); bytes[damage.offset] = before;
  imageOK = rejected && verifyHelpImages(_helpBook) && imageOK;
  debug("Astronomica help image header %x: %s",damage.offset,rejected ? "PASS" : "FAIL");
 }
 debug("Astronomica help images verification: %s (31 palettes/pixels, 31 original article associations, 31 corrupt image streams, 10 header/extent corruptions)",imageOK ? "PASS" : "FAIL");
 ok = imageOK && ok;
 const uint lengths[] = {0,1,4,8,12,15,16,32,256,65536,uint(bytes.size()-1)};
 for (uint length : lengths) {
  Common::MemoryReadStream shortFile(&bytes[0],length);
  ok = !_helpBook.load(shortFile) && _helpBook.recordHash == 0x2cab83c0U && ok;
 }
 // Corrupt an LZ back-reference, file size, directory and linked topic record.
 const uint corruptOffsets[] = {0,4,12,0x2c07,0x2c2f,0x0d6d,0x3086+12+1};
 for (uint offset : corruptOffsets) {
  const byte before = bytes[offset]; bytes[offset] ^= 0xff;
  Common::MemoryReadStream damaged(&bytes[0],bytes.size());
  const bool accepted = _helpBook.load(damaged); bytes[offset] = before;
  ok = !accepted && _helpBook.recordHash == 0x2cab83c0U && ok;
  debug("Astronomica help corruption %x: %s",offset,accepted ? "FAIL" : "PASS");
 }
 // Original menu and mentor controls must enqueue custom22, open a real
 // ScummVM modal window and return without changing the scene or globals.
 for (int place : {1,408}) {
  if (!loadPlace(place)) return false;
  if (place == 1) {
   ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
   for (uint32 now = 0; now <= 500; now += 10) runScriptsAt(now);
  }
  const int index = place == 1 ? 4 : 6;
  const Sprite &button = _scene.sprites[index];
  const int x = button.renderX+10, y = button.renderY+10;
  const uint before = _helpOpened;
  ok = spriteAt(x,y) == index && _runner.canRun(button.click,true) && ok;
  // Escape is consumed by the actual modal dialog, not by the script runner.
  Common::Event close; close.type = Common::EVENT_KEYDOWN; close.kbd.keycode = Common::KEYCODE_ESCAPE;
  _eventMan->pushEvent(close);
  clickAtTime(x,y,510);
  for (uint32 now = 510; now <= 2500; now += 10) runScriptsAt(now);
  ok = _helpOpened == before+1 && _place == place && !_clockPaused && !_runner.clicksBlocked() && ok;
  if (place == 408) ok = !_moviePlaying && ok;
  debug("Astronomica P%d help control: %s, opens %u/%u, scene %d, paused %d, blocked %d",place,ok ? "PASS" : "FAIL",_helpOpened,before+1,_place,int(_clockPaused),int(_runner.clicksBlocked()));
 }
 // Do not accept Windows-help commands in unrelated scenes or other modes.
 Script command; Command c; c.opcode = 23;
 for (int value : {22,1,0,0,0,0}) c.args.push_back(value); command.push_back(c);
 ok = loadPlace(103) && !_runner.canRun(command,true) && ok;
 ok = loadPlace(1) && _runner.canRun(command,true) && ok; command[0].args[1] = 2;
 ok = !_runner.canRun(command,true) && ok;
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica help verification: %s (2117 records, 781 readable articles, 812 keywords, search, corruption, native controls)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::ensureHelpBook() {
 if (!_helpAttempted) {
  _helpAttempted = true; Common::File file;
  if (file.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path("HELP/ASTRONOM.HLP")))))
   if (!_helpBook.load(file)) warning("Astronomica: cannot decode reference book");
 }
 return !_helpBook.articles.empty();
}
void AstronomicaEngine::openHelpBook() {
 if ((_place != 1 && _place != 408) || !ensureHelpBook()) return;
 _mixer->stopHandle(_soundHandle);
 if (_place == 408 && _movie) {
  // Custom22 stops the mentor movie before transferring to Windows help.
  _movie->stop(); _moviePlaying = false;
 }
 ++_helpOpened;
 {
  PauseToken paused = pauseEngine();
  showHelpBook(_helpBook);
 }
 // ScummVM's modal viewer replaces WinHelp; restore the current scene on close.
 presentScene();
}
bool AstronomicaEngine::verifyHover() {
 bool ok = true; uint targets = 0, sounds = 0, dispatchCases = 0;
 auto pump = [&]() { for (int i = 0; i < 32; ++i) runScriptsAt(0); };
 const int places[] = {1,505,519,526};
 const int counts[] = {2,14,10,6};
 for (uint placeIndex = 0; placeIndex < ARRAYSIZE(places); ++placeIndex) {
  const int place = places[placeIndex];
  if (!loadPlace(place)) return false;
  uint ready = 0;
  for (const auto &t : _hoverSprites) ready += t.ready;
  for (const auto &t : _hoverRects) ready += t.ready;
  ok = ready == uint(counts[placeIndex]) && ok;
  debug("Astronomica hover P%d ready %u/%d",place,ready,counts[placeIndex]);
  const uint spriteCount = _scene.sprites.size(), rectCount = _scene.mouseRects.size();
  for (uint n = 0; n < spriteCount+rectCount; ++n) {
   if (!loadPlace(place)) return false;
   const bool sprite = n < spriteCount; const uint index = sprite ? n : n-spriteCount;
   HoverTarget &t = sprite ? _hoverSprites[index] : _hoverRects[index];
   if (!t.ready) continue;
   if (place == 526) _runner.defineValue(1,3,0); // Settled selection phase after entry.
   const Script &in = sprite ? _scene.sprites[index].mouseIn : _scene.mouseRects[index].mouseIn;
   int shown = -1, sound = -1;
   for (const auto &c : in) {
    if (c.opcode == 16) shown = c.args[0]-1;
    if (c.opcode == 9) sound = c.args[0]-1;
   }
   if (shown < 0 || uint(shown) >= spriteCount) return false;
   const int x = sprite ? _scene.sprites[index].renderX+t.width/2 : _scene.mouseRects[index].rect[0]+1;
   const int y = sprite ? _scene.sprites[index].renderY+t.height/2 : _scene.mouseRects[index].rect[1]+1;
   _scene.sprites[shown].visible = 0;
   const uint before = _soundsStarted;
   // Hidden hit sprites still receive hover; queued scripts do not execute inline.
   if (sprite) _scene.sprites[index].visible = 0;
   hoverAtTime(x,y,0);
   ok = t.entered && !_scene.sprites[shown].visible && ok;
   const uint queued = _runner.pendingCount();
   hoverAtTime(x,y,0); ok = _runner.pendingCount() == queued && ok;
   pump(); ok = _scene.sprites[shown].visible && ok;
   if (sound >= 0) {
    ok = _lastSound == sound && _soundsStarted == before+1 && !isBlockingSound(sound) && ok; ++sounds;
   }
   const uint after = _soundsStarted;
   hoverAtTime(x,y,0); pump(); ok = _soundsStarted == after && ok;
   hoverAtTime(-100,-100,0); pump(); ok = !t.entered && !_scene.sprites[shown].visible && ok;
   hoverAtTime(-100,-100,0); ok = _runner.pendingCount() == 0 && ok;
   debug("Hover target P%d %s %u shown %d sound %d: %s",place,sprite ? "sprite" : "rect",index,shown,sound,ok ? "PASS" : "FAIL");
   ++targets;
  }
 }
 debug("Hover target group: %s",ok ? "PASS" : "FAIL");
 // Original P505 buttons 0 and 2 overlap at(105,376). Both events run
 // in sprite order; the second asynchronous sound replaces the first.
 if (!loadPlace(505)) return false;
 const uint overlapSounds = _soundsStarted;
 hoverAtTime(105,376,0); ok = _hoverSprites[0].entered && _hoverSprites[2].entered && ok;
 pump(); ok = _scene.sprites[1].visible && _scene.sprites[3].visible &&
  _soundsStarted == overlapSounds+2 && _lastSound == 12 && ok;
 hoverAtTime(105,376,0); pump(); ok = _soundsStarted == overlapSounds+2 && ok;
 hoverAtTime(-100,-100,0); pump(); ok = !_scene.sprites[1].visible && !_scene.sprites[3].visible && ok;
 debug("Hover original overlap and sound order: %s",ok ? "PASS" : "FAIL");
 // Conditional hover is still tracked when its script branch does nothing.
 for (int place : {1,526}) {
  if (!loadPlace(place)) return false;
  _runner.defineValue(1,place == 1 ? 0 : 3,1);
  const int index = place == 1 ? 4 : 0;
  const int shown = 5;
  _scene.sprites[shown].visible = 0;
  const int x = place == 1 ? _scene.sprites[index].renderX+1 : _scene.mouseRects[index].rect[0]+1;
  const int y = place == 1 ? _scene.sprites[index].renderY+1 : _scene.mouseRects[index].rect[1]+1;
  hoverAtTime(x,y,0); pump(); ok = !_scene.sprites[shown].visible && ok;
  _runner.defineValue(1,place == 1 ? 0 : 3,0);
  hoverAtTime(x,y,0); pump(); ok = !_scene.sprites[shown].visible && ok;
  hoverAtTime(-100,-100,0); pump(); hoverAtTime(x,y,0); pump();
  ok = _scene.sprites[shown].visible && ok;
 }
 debug("Hover conditions group: %s",ok ? "PASS" : "FAIL");
 // Native dispatch compared with the 256 original state/hit cases. Geometry
 // is controlled here; the preceding 32 checks use original scene geometry.
 for (int kind = 0; kind < 2; ++kind) {
  for (uint states = 0; states < 8; ++states) for (uint hits = 0; hits < 8; ++hits) {
   if (!loadPlace(kind ? 519 : 505)) return false;
   for (auto &t : _hoverSprites) t.ready = false;
   for (auto &t : _hoverRects) t.ready = false;
   uint expected = 0;
   for (uint i = 0; i < 3; ++i) {
    HoverTarget &t = kind ? _hoverRects[i] : _hoverSprites[i*2];
    t.ready = true; t.entered = (states & (1U<<i)) != 0;
    const bool hit = (hits & (1U<<i)) != 0;
    expected += hit != t.entered;
    if (kind) {
     int32 *r = _scene.mouseRects[i].rect;
     r[0] = hit ? 0 : 200; r[1] = 0; r[2] = r[0]+100; r[3] = 100;
    } else {
     _scene.sprites[i*2].renderX = hit ? 0 : 200;
     _scene.sprites[i*2].renderY = 0;
    }
   }
   // Original ordinary hover does not test the global click lock.
   Script lock; Command c; c.opcode = 28; c.args.push_back(-1); c.delay = -1; lock.push_back(c);
   ok = _runner.start(lock,0,true) && _runner.clicksBlocked() && ok;
   hoverAtTime(1,1,0); ok = _runner.pendingCount() == expected && ok; ++dispatchCases;
   for (uint i = 0; i < 3; ++i)
    ok = (kind ? _hoverRects[i].entered : _hoverSprites[i*2].entered) == ((hits & (1U<<i)) != 0) && ok;
   hoverAtTime(1,1,0); ok = _runner.pendingCount() == expected && ok; ++dispatchCases;
  }
 }
 debug("Hover dispatch group: %s",ok ? "PASS" : "FAIL");
 // Leaving a scene clears entered flags and queued hover scripts.
 ok = loadPlace(505) && ok; hoverAtTime(_scene.sprites[0].renderX+1,_scene.sprites[0].renderY+1,0);
 ok = _runner.pendingCount() > 0 && loadPlace(103) && _hoverSprites.empty() && _hoverRects.empty() && !_runner.pendingCount() && ok;
 ok = loadPlace(505) && !_hoverSprites[0].entered && ok;
 ok = targets == 32 && sounds == 4 && dispatchCases == 256 && ok;
 debug("Astronomica hover verification: %s; %u targets, %u sounds, %u dispatch cases",ok ? "PASS" : "FAIL",targets,sounds,dispatchCases);
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 return ok;
}
bool AstronomicaEngine::verifyWorldMovie29() {
 bool ok = true;
 ConfMan.setBool("astronomica_sprite_input",true);
 const auto pump = [&](uint32 now) { for (int pass = 0; pass < 32; ++pass) runScriptsAt(now); };
 for (int first = 0; first < 2; ++first) {
  if (!loadPlace(29) || !_movie) return false;
  const auto click = [&](int id, uint32 now) {
   const MouseRect &r = _scene.mouseRects[id];
   clickAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);
   pump(now);
  };
  ok = _runner.canRun(_scene.mouseRects[0].click,true) && _runner.canRun(_scene.mouseRects[1].click,true) && ok;
  click(first,0);
  ok = !_moviePlaying && _runner.clicksBlocked() && ok;
  pump(149); ok = _runner.clicksBlocked() && ok;
  pump(150); ok = !_runner.clicksBlocked() && ok;
  // Repeating just one control cannot start the movie.
  click(first,200); pump(350); ok = !_moviePlaying && ok;
  click(1-first,400);
  int32 a = 0,b = 0; _runner.getValue(1,1,a); _runner.getValue(1,2,b);
  ok = a == 2 && b == 2 && _moviePlaying && _runner.clicksBlocked() &&
   _movieX == 213 && _movieY == 22 && _worldMovieCursorBottom == 22+_movie->getHeight()+5 && ok;
  updateMovie(); ok = _movieFrame.w > 0 && ok;
  for (int part = 1; part < 4; ++part) {
   const uint before = _movieFramesDrawn;
   ok = _movie->seek(Audio::Timestamp(0,_movie->getDuration().totalNumberOfFrames()*part/4,_movie->getTimeScale())) && ok;
   updateMovie(); ok = _movieFramesDrawn > before && ok;
  }
  // Keep the real movie decoded, but test script boundaries independently.
  pump(65399); ok = _movieFrame.w > 0 && _runner.clicksBlocked() && ok;
  pump(65400); ok = _movieFrame.w == 0 && _worldMovieCursorBottom == -1 && _runner.clicksBlocked() && ok;
  pump(65549); ok = _runner.clicksBlocked() && ok;
  pump(65550); ok = !_runner.clicksBlocked() && ok;
  _movie->seek(_movie->getEndTime()); updateMovie(); ok = !_moviePlaying && ok;
  click(0,66000); pump(66150); click(1,66200); pump(66350);
  ok = !_moviePlaying && !_runner.clicksBlocked() && ok;
  debug("Astronomica P29 control order %d: %s",first,ok ? "PASS" : "FAIL");
 }
 if (!loadPlace(29)) return false;
 Script redraw; Command c; c.opcode = 23;
 for (int value : {29,0,0,0,0,0}) c.args.push_back(value);
 redraw.push_back(c);
 _runner.setWorldMovieSupport(false); ok = !_runner.canRun(redraw,true) && ok;
 ok = loadPlace(103) && _worldMovieCursorBottom == -1 && ok;
 debug("Astronomica P29 movie verification: %s (both control orders, duplicate clicks, frame decode, redraw, lock deadlines, no replay, context guard)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyWorldMovies(bool continuous) {
 bool ok = true;
 ConfMan.setBool("astronomica_sprite_input",true);
 ConfMan.setBool("astronomica_animation",true);
 const auto pump = [&](uint32 now) { for (int pass = 0; pass < 32; ++pass) runScriptsAt(now); };
 const auto click = [&](uint id,uint32 now) {
  const MouseRect &r = _scene.mouseRects[id];
  clickAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now); pump(now);
 };
 for (int place : {82,222,231}) {
  if (!loadPlace(place) || !_movie) return false;
  const uint32 duration = place == 231 ? 16000 : 10000;
  click(1,0); pump(150); ok = !_moviePlaying && !_runner.clicksBlocked() && ok;
  click(0,200); pump(350); click(0,400); pump(550);
  int32 armed = -1; _runner.getValue(1,1,armed); ok = armed == 0 && ok;
  click(0,600); pump(750); click(1,800);
  ok = _moviePlaying && _runner.clicksBlocked() && _worldMovieCursorBottom >= 0 && ok;
  const int x = place == 82 ? 327 : place == 222 ? 241 : 296;
  const int y = place == 82 ? 240 : place == 222 ? 182 : 109;
  ok = _movieX == x && _movieY == y && ok;
  for (int part = 0; part < 4; ++part) {
   const uint before = _movieFramesDrawn;
   ok = _movie->seek(Audio::Timestamp(0,_movie->getDuration().totalNumberOfFrames()*part/4,_movie->getTimeScale())) && ok;
   updateMovie(); ok = _movieFramesDrawn > before && ok;
  }
  _movie->seek(_movie->getEndTime()); updateMovie(); ok = !_moviePlaying && ok;
  pump(800+duration-1); ok = _runner.clicksBlocked() && _worldMovieCursorBottom >= 0 && ok;
  pump(800+duration); ok = _runner.clicksBlocked() && _worldMovieCursorBottom == -1 && ok;
  if (place == 231) ok = _movieFrame.w == 0 && ok;
  pump(800+duration+149); ok = _runner.clicksBlocked() && ok;
  pump(800+duration+150); ok = !_runner.clicksBlocked() && ok;
  if (place == 222) {
   _runner.getValue(1,1,armed); ok = armed == 2 && ok;
   click(2,12000); ok = _moviePlaying && _movie->getTime() < 100 && ok;
   const uint before = _movieFramesDrawn; updateMovie(); ok = _movieFramesDrawn > before && ok;
   _movie->seek(_movie->getEndTime()); updateMovie();
   pump(21999); ok = _runner.clicksBlocked() && ok;
   pump(22000); pump(22150); _runner.getValue(1,1,armed);
   ok = armed == 0 && !_runner.clicksBlocked() && ok;
   click(2,23000); pump(23150); ok = !_moviePlaying && ok;
   // The controller keeps an in-range position. A forced rewind on every
   // play would break this second, distinct original-controller case.
   const uint32 middle = _movie->getDuration().totalNumberOfFrames()/2;
   ok = _movie->seek(Audio::Timestamp(0,middle,_movie->getTimeScale())) && ok;
   _runner.defineValue(1,1,2); click(2,24000);
   const uint32 middleMs = Audio::Timestamp(0,middle,_movie->getTimeScale()).msecs();
   ok = _moviePlaying && _movie->getTime() >= middleMs && _movie->getTime() < middleMs+100 && ok;
   _movie->seek(_movie->getEndTime()); updateMovie(); pump(34000); pump(34150);
   // Original sprite0 independently shows/animates sprite1 for two seconds.
   const Sprite &button = _scene.sprites[0];
   const int bx = button.renderX+1, by = button.renderY+1;
   ok = spriteAt(bx,by) == 0 && ok;
   clickAtTime(bx,by,35000); pump(35000);
   ok = _scene.sprites[1].visible && _scene.sprites[1].autoFrame && _runner.clicksBlocked() && ok;
   const int oldFrame = _scene.sprites[1].selectedFrame;
   animateSpritesAt(35150); ok = _scene.sprites[1].selectedFrame != oldFrame && ok; pump(36999); ok = _scene.sprites[1].autoFrame && ok;
   pump(37000); ok = !_scene.sprites[1].autoFrame && _runner.clicksBlocked() && ok;
   pump(37150); ok = !_runner.clicksBlocked() && ok;
   click(5,38000); ok = _place == 407 && ok;
  }
  debug("Astronomica P%d world movie controls: %s",place,ok ? "PASS" : "FAIL");
 }
 if (continuous) for (int place : {29,82,222,231}) {
  if (!loadPlace(place) || !_movie) return false;
  click(0,0); pump(150); click(1,200);
  const uint before = _movieFramesDrawn; const uint32 started = _system->getMillis();
  while ((_moviePlaying || _runner.clicksBlocked()) && _system->getMillis()-started < 90000) {
   pump(200+_system->getMillis()-started); updateMovie(); _system->delayMillis(5);
  }
  const bool passed = !_moviePlaying && !_runner.clicksBlocked() && _movieFramesDrawn-before > 10;
  ok = passed && ok;
  debug("Astronomica P%d world movie continuous: %s (%u frames, %u ms)",place,passed ? "PASS" : "FAIL",_movieFramesDrawn-before,_system->getMillis()-started);
 }
 ok = loadPlace(103) && !_runner.worldMovieSupport() && _worldMovieCursorBottom == -1 && ok;
 debug("Astronomica world movies verification: %s",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyIntro() {
 bool ok = true; _runner.resetGlobals();
 if (!loadPlace(1)) return false;
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
 for (uint32 now = 0; now <= 500; now += 10) runScriptsAt(now);
 ConfMan.setBool("astronomica_sprite_input",true);
 const Sprite &start = _scene.sprites[2];
 ok = spriteAt(start.renderX+10,start.renderY+10) == 2 && ok;
 clickAtTime(start.renderX+10,start.renderY+10,510);
 for (uint32 now = 510; now < 5000 && _place == 1; now += 10) runScriptsAt(now);
 ok = _place == 2 && !_runner.clicksBlocked() && ok;
 debug("Astronomica new-game menu verification: %s",ok ? "PASS" : "FAIL");
 for (int place : {2,4}) {
  if (!loadPlace(place) || !_movie || _scene.scripts.size() != 1) return false;
  ok = _movie->getPixelFormat().bytesPerPixel > 1 && ok;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
  uint frames = _movieFramesDrawn; updateMovie();
  ok = _moviePlaying && _movieX == 120 && _movieY == 140 && _movieFramesDrawn > frames && ok;
  // Decode throughout the source movie, including both sides of P2's
  // palette command, without replacing the embedded RGB colors.
  const uint32 duration = _movie->getEndTime().msecs();
  for (uint part = 1; part < 5; ++part) {
   ok = _movie->seek(Audio::Timestamp(duration*part/5)) && ok;
   frames = _movieFramesDrawn; updateMovie(); ok = _movieFramesDrawn > frames && ok;
  }
  if (place == 2) {
   Script palette; Command command; command.opcode = 50; command.text = "missing.bmp"; palette.push_back(command);
   ok = !_runner.canRun(palette,true) && ok;
   runScriptsAt(168999); ok = _place == 2 && ok;
   runScriptsAt(169000); ok = _place == 2 && _moviePlaying && ok;
   runScriptsAt(207999); ok = _place == 2 && ok;
   runScriptsAt(208000); ok = _place == 3 && ok;
  } else {
   runScriptsAt(69999); ok = _place == 4 && ok;
   runScriptsAt(70000); ok = _place == 27 && ok;
  }
  debug("Astronomica intro P%d timing: %s",place,ok ? "PASS" : "FAIL");
 }
 // The nine original P3 cards bridge the two movie sequences.
 ok = loadPlace(3) && _runner.enqueueStartup(_scene.scripts,0,true) == 10 && ok;
 for (int card = 2; card <= 10; ++card) {
  const uint32 now = (card-1)*6500;
  runScriptsAt(now); runScriptsAt(now);
  Graphics::Surface *expected = openBackgroundImage(Common::String::format("OPEN%d_B",card));
  if (!expected) return false;
  ok = screenRGBHash(_background) == screenRGBHash(*expected) && ok;
  expected->free(); delete expected;
 }
 runScriptsAt(68499); ok = _place == 3 && ok;
 runScriptsAt(68500); ok = _place == 4 && ok;
 ok = loadPlace(3) && ok; clickAtTime(10,10,0); runScriptsAt(0); ok = _place == 4 && ok;
 debug("Astronomica intro cards verification: %s (nine images, timed and clicked exit)",ok ? "PASS" : "FAIL");
 // A palette command from any other scene fails before any effect.
 ok = loadPlace(103) && ok;
 Script palette; Command command; command.opcode = 50; command.text = "OPEN2_B"; palette.push_back(command);
 ok = !_runner.canRun(palette,true) && ok;
 debug("Astronomica intro verification: %s (two RGB movies, P4 directory redirect, palette adaptation, original delays)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyLogo(bool actualExit) {
 bool ok = true;
 for (int flag : {0,2,1}) {
  _runner.resetGlobals(); _runner.defineValue(0,61,flag);
  if (!loadPlace(0) || !_movie || _scene.scripts.size() != 1) return false;
  Script invalid = _scene.scripts[0]; Command extra; extra.opcode = 32;
  extra.args.push_back(0); extra.args.push_back(61); extra.args.push_back(4); invalid.push_back(extra);
  ok = !_runner.canRun(invalid,true) && ok;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
  const uint frames = _movieFramesDrawn; updateMovie();
  ok = _moviePlaying && _movieX == 160 && _movieY == 120 && _movieFramesDrawn > frames && ok;
  int32 state = -1; ok = _runner.getValue(0,61,state) && state == (flag == 2 ? 0 : flag) && ok;
  runScriptsAt(19999); ok = _place == 0 && !shouldQuit() && ok;
  if (flag == 1 && !actualExit) {
   _runner.tick(20000); ScriptRunner::Action action; uint quits = 0;
   while (_runner.popAction(action)) { ok = action.opcode == 6 && ok; if (action.opcode == 6) ++quits; }
   ok = quits == 1 && !_runner.pendingCount() && ok;
  } else {
   runScriptsAt(20000);
   ok = (flag == 1 ? shouldQuit() : _place == 1 && !shouldQuit()) && ok;
  }
 }
 if (!actualExit) { _runner.resetGlobals(); ok = loadPlace(103) && ok; }
 debug("Astronomica logo verification: %s (flags 0/2 return to menu, flag1 quit, 20-second boundary, trailing-effect guard)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyPostCredits() {
 _runner.resetGlobals();
 bool ok = loadPlace(432) && _movie;
 if (!ok) return false;
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
 for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
 uint frames = _movieFramesDrawn; updateMovie();
 ok = _moviePlaying && _movieX == 160 && _movieY == 120 && _movieFramesDrawn > frames && ok;
 runScriptsAt(9999); ok = _place == 432 && ok;
 runScriptsAt(10000); ok = _place == 433 && _movie && ok;
 if (!ok) return false;
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
 for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
 frames = _movieFramesDrawn; updateMovie();
 ok = _moviePlaying && _movieX == 160 && _movieY == 110 && _movieFramesDrawn > frames && ok;
 const int y0 = _scene.sprites[0].renderY, y1 = _scene.sprites[1].renderY;
 runScriptsAt(6999); ok = !_scene.sprites[0].autoMove && !_scene.sprites[1].autoMove && ok;
 for (uint32 now = 7000; now <= 8000; now += 25) { runScriptsAt(now); animateSpritesAt(now); }
 ok = _scene.sprites[0].renderY > y0 && _scene.sprites[1].renderY < y1 && ok;
 for (uint32 now = 8025; now < 17000; now += 25) { runScriptsAt(now); animateSpritesAt(now); }
 ok = _place == 433 && !_scene.sprites[0].autoFrame && !_scene.sprites[1].autoFrame && _scene.sprites[0].moveDY == 0 && _scene.sprites[1].moveDY == 0 && ok;
 runScriptsAt(17000); ok = _place == 0 && ok;
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 for (int place : {432,433}) {
  if (!loadPlace(place) || !_movie) return false;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
  const uint continuousFrames = _movieFramesDrawn; const uint32 began = _system->getMillis();
  while (_moviePlaying && _system->getMillis()-began < 25000) { updateMovie(); _system->delayMillis(5); }
  const bool ended = !_moviePlaying && _movieFramesDrawn-continuousFrames > 40;
  ok = ended && ok;
  debug("Astronomica post-credits P%d continuous: %s (%u frames)",place,ended ? "PASS" : "FAIL",_movieFramesDrawn-continuousFrames);
 }
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica post-credits verification: %s (two movies, timed sprite motion, P432 to P433 to P0)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyEndings() {
 _runner.resetGlobals(); bool ok = true; uint routes = 0;
 const int destinations[] = {424,435,436,437};
 for (uint seed = 0; seed < 100 && routes != 15; ++seed) {
  _runner.seedRandom(seed); if (!loadPlace(423) || !_movie) return false;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  for (int pass = 0; pass < 32; ++pass) runScriptsAt(0);
  int32 choice = 0; if (!_runner.getValue(1,0,choice) || choice < 1 || choice > 4) return false;
  if (routes & (1U << (choice-1))) continue;
  routes |= 1U << (choice-1);
  const uint frames = _movieFramesDrawn; updateMovie();
  ok = _moviePlaying && _movieX == 120 && _movieY == 140 && _movieFramesDrawn > frames && ok;
  runScriptsAt(22999); ok = _place == 423 && ok;
  runScriptsAt(23000); ok = _place == destinations[choice-1] && _movie && ok;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
  const uint finalFrames = _movieFramesDrawn; runScriptsAt(0); updateMovie();
  ok = _moviePlaying && _movieX == 120 && _movieY == 140 && _movieFramesDrawn > finalFrames && ok;
  // Decode throughout each actual final movie, not just its first frame.
  const uint32 duration = _movie->getDuration().msecs();
  for (uint part = 1; part < 5; ++part) {
   ok = _movie->seek(Audio::Timestamp(duration*part/5)) && ok;
   const uint before = _movieFramesDrawn; updateMovie(); ok = _movieFramesDrawn > before && ok;
  }
  runScriptsAt(72999); ok = _place == destinations[choice-1] && ok;
  runScriptsAt(73000); ok = _place == 425 && ok;
  debug("Astronomica ending choice %d: %s (film P%d to credits)",choice,ok ? "PASS" : "FAIL",destinations[choice-1]);
 }
 ok = routes == 15 && ok;
 // Continuously decode the common lead-in through its natural movie end.
 ok = loadPlace(423) && _movie && ok;
 ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && ok;
 runScriptsAt(0); const uint before = _movieFramesDrawn; const uint32 began = _system->getMillis();
 while (_moviePlaying && _system->getMillis()-began < 50000) { updateMovie(); _system->delayMillis(5); }
 const uint frames = _movieFramesDrawn-before;
 const bool continuous = !_moviePlaying && frames > 100 && _system->getMillis()-began > 15000;
 ok = continuous && ok;
 debug("Astronomica ending continuous playback: %s (%u frames, wall %u ms, movie %u ms, end %u ms)",continuous ? "PASS" : "FAIL",frames,_system->getMillis()-began,_movie->getTime(),uint32(_movie->getEndTime().msecs()));
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica endings interaction verification: %s (four original choices, five movies, timed credit transitions)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyAdvice() {
 const uint oldCompleted = _puzzlesCompleted;
 uint32 hash = 2166136261U; uint cases = 0;
 auto fold = [&](uint32 v) { hash = (hash ^ v)*16777619U; };
 const int counts[] = {0,1,2,8,9,21,22,25,26,27};
 const int flags[][2] = {{0,0},{1,0},{0,1},{1,1},{2,2}};
 for (int previous : {103,208}) for (int count : counts) for (int solved = 0; solved < 3; ++solved)
  for (int stage = 0; stage < 4; ++stage) for (const auto &flag : flags) for (int branch = 0; branch < 29; ++branch) {
   int draws[3] = {branch < 13 ? 0 : 1,branch < 13 ? branch+1 : (branch-13)/4+1,(branch-13)%4+1}, used = 0;
   const AdviceResult r = chooseAdvice(previous,count,solved,stage,flag[0],flag[1],[&](int low,int high) { const int v = draws[used++]; return v; });
   fold(r.side); fold(r.stage); fold(r.flag55); fold(r.flag56); fold(r.clip.start); fold(r.clip.duration); fold(used); ++cases;
  }
 bool ok = hash == 0xbcb8ca85U && cases == 34800;
 debug("Astronomica advice original comparison: %s (%u cases, %08x)",ok ? "PASS" : "FAIL",cases,hash);
 hash = 2166136261U; cases = 0;
 for (int solved = 0; solved < 3; ++solved) for (uint32 previous : {0U,1U,0xffffffffU})
  for (int flag = 0; flag < 3; ++flag) for (uint32 now : {0U,1U,0x12345678U,0xffffffffU}) {
   const bool start = adviceStartsClock(solved,previous);
   fold(start ? now : previous); fold(start ? 1 : flag); fold(start ? 1 : 0); ++cases;
  }
 ok = hash == 0xbf6ea917U && cases == 108 && ok;
 debug("Astronomica advice clock comparison: %s (%u cases, %08x)",hash == 0xbf6ea917U ? "PASS" : "FAIL",cases,hash);
 hash = 2166136261U; cases = 0;
 const uint32 ages[] = {0,3999,4000,4001,59999,60000,60001,119999,120000,120001,179999,180000,180001,239999,240000,240001,269999,270000,270001,294999,295000,295001,299999,300000,300001,0xffffffffU};
 for (int mode = 0; mode < 5; ++mode) for (int item = 0; item < 3; ++item) for (int stage = 0; stage < 9; ++stage)
  for (uint32 started : {0U,1U,0xfffffff0U}) for (uint32 age : ages) {
   const CountdownResult r = worldCountdown(mode,item,stage,started,started+age);
   fold(r.mode); fold(r.stage); fold(r.destination ? r.destination : 103); fold(r.destination ? 1 : 0); fold(r.sound); ++cases;
  }
 ok = hash == 0x0ae350b7U && cases == 10530 && ok;
 debug("Astronomica countdown original comparison: %s (%u cases, %08x)",hash == 0x0ae350b7U ? "PASS" : "FAIL",cases,hash);
 auto value = [&](int scope,int index) { int32 v = -1; _runner.getValue(scope,index,v); return v; };
 auto click = [&](int sprite,uint32 now) {
  const Sprite &button = _scene.sprites[sprite];
  const int x = button.renderX+10, y = button.renderY+10;
  if (spriteAt(x,y) != sprite) return false;
  clickAtTime(x,y,now); return true;
 };
 // Actual MEGAFILE scripts: priorities, both speaker positions, repeat click,
 // permission, delayed return and clock-start sentinel.
 for (int scenario = 0; scenario < 8; ++scenario) {
  _runner.resetGlobals(); _puzzlesCompleted = scenario == 2 ? 9 : scenario == 3 ? 22 : scenario == 4 ? 26 : 0;
  _runner.defineValue(0,6,scenario == 3 ? 1 : scenario == 4 ? 2 : 0);
  _runner.defineValue(0,45,scenario == 0 ? 1 : 0);
  _runner.defineValue(0,55,scenario == 6 ? 1 : 0); _runner.defineValue(0,56,scenario == 5 ? 1 : 0);
  const int previous = scenario == 1 ? 208 : 103;
  if (!loadPlace(previous) || !loadPlace(409) || !_movie) return false;
  ok = click(1,100) && ok;
  for (uint32 now = 100; now <= 1100; now += 10) runScriptsAt(now);
  const int side = value(1,0);
  ok = _moviePlaying && _movieX == (side ? 143 : 343) && _movieY == 113 && value(0,57) == 1 && value(1,1) == 1 && !_runner.clicksBlocked() && ok;
  if (scenario == 5) ok = side == 1 && value(0,56) == 0 && ok;
  if (scenario == 6) ok = side == 1 && value(0,55) == 0 && ok;
  if (scenario >= 2 && scenario <= 4) ok = value(0,6) == scenario-1 && ok;
  const uint frames = _movieFramesDrawn; updateMovie(); ok = _movieFramesDrawn > frames && ok;
  ok = click(1,1200) && ok;
  for (uint32 now = 1200; now <= 2200; now += 10) runScriptsAt(now);
  ok = !_moviePlaying && value(1,0) == 2 && !_runner.clicksBlocked() && ok;
  ok = click(0,2300) && ok; runScriptsAt(2300); runScriptsAt(3049);
  ok = _place == 409 && ok; runScriptsAt(3050);
  ok = _place == previous && value(0,8) == (scenario == 0 ? 2300 : 0) && value(0,60) == (scenario == 0 ? 1 : 0) && ok;
  debug("Astronomica advice scenario %d: %s",scenario,ok ? "PASS" : "FAIL");
 }
 // A continuous original advice segment must stop at its selected end.
 _runner.resetGlobals(); _runner.defineValue(0,45,1);
 ok = loadPlace(103) && loadPlace(409) && click(1,0) && ok;
 for (uint32 now = 0; now < 1000 && !_moviePlaying; now += 10) runScriptsAt(now);
 const AdviceResult clip = chooseAdvice(103,0,1,0,0,0,[](int low,int) { return low; });
 ok = _moviePlaying && _movie->getEndTime() == Audio::Timestamp(0,clip.clip.start+clip.clip.duration,30) && ok;
 const uint framesBefore = _movieFramesDrawn; const uint32 began = _system->getMillis();
 while (_moviePlaying && _system->getMillis()-began < 20000) { updateMovie(); _system->delayMillis(5); }
 const uint played = _movieFramesDrawn-framesBefore;
 const bool continuous = !_moviePlaying && played > 100 && _system->getMillis()-began >= 14000;
 ok = continuous && ok;
 debug("Astronomica advice continuous playback: %s (%u frames, natural segment end)",continuous ? "PASS" : "FAIL",played);
 // Start once, even after revisiting; consume the permission at an actual gate.
 _runner.resetGlobals(); _runner.defineValue(0,45,1); _runner.defineValue(0,8,123);
 ok = loadPlace(103) && loadPlace(409) && click(0,100) && ok;
 runScriptsAt(100); runScriptsAt(850); ok = value(0,8) == 123 && value(0,60) == 0 && ok;
 _runner.defineValue(0,57,1); ok = loadPlace(101) && changePlace(110) && _place == 110 && value(0,57) == 0 && ok;
 // Production timer dispatch: all seven original WAVs then P427.
 _runner.resetGlobals(); ok = loadPlace(103) && ok;
 _runner.defineValue(0,8,1); _runner.defineValue(0,60,1);
 const uint32 thresholds[] = {4000,60000,120000,180000,240000,270000,295000};
 for (int stage = 0; stage < 7; ++stage) {
  updateWorldAt(1+thresholds[stage]); ok = value(0,62) == stage && ok;
  updateWorldAt(2+thresholds[stage]); ok = value(0,62) == stage+1 && _lastSound == 913+stage && ok;
 }
 updateWorldAt(300001); ok = _place == 103 && ok;
 updateWorldAt(300002); ok = _place == 427 && value(0,60) == 3 && ok;
 // Save and restore an active clock after deliberately changing its epoch.
 // Test while paused as the F5 load dialog does, and across uint32 wrap.
 const bool deterministic = ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify");
 ConfMan.setBool("astronomica_verify",false);
 for (uint32 now : {10000U,5U}) {
  _runner.resetGlobals(); ok = loadPlace(103) && ok;
  pauseEngineIntern(true); _pausedMillis = _pauseStarted-now;
  _runner.defineValue(0,60,1); _runner.defineValue(0,8,int32(now-5000));
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  ok = saveGameStream(&out).getCode() == Common::kNoError && ok;
  _pausedMillis -= 900000;
  Common::MemoryReadStream input(out.getData(),out.size());
  ok = loadGameStream(&input).getCode() == Common::kNoError && scriptClock() == now && uint32(value(0,8)) == now-5000 && ok;
  updateWorldAt(scriptClock()); ok = value(0,62) == 1 && _place == 103 && ok;
  pauseEngineIntern(false);
 }
 ConfMan.setBool("astronomica_verify",deterministic);
 _puzzlesCompleted = oldCompleted; _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica advice/countdown interaction verification: %s (clips, return, permit, seven WAVs, expiry, saved clock and wrap)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyMentors() {
 _runner.defineValue(0,29,1); // Help returns pass the original puzzle-entry gate.
 uint32 hash = 2166136261U;
 for (int mentor = 1; mentor <= 5; ++mentor) for (int previous = 500; previous < 538; ++previous)
  for (int variant = 0; variant < 10; ++variant) {
   const MentorClip clip = mentorClip(mentor,previous,variant);
   hash = (hash ^ uint32(clip.start))*16777619U;
   hash = (hash ^ uint32(clip.duration))*16777619U;
  }
 bool ok = hash == 0x3fc5282bU;
 debug("Astronomica mentors original comparison: %s (1900 cases; undefined P524 ranges fail closed)",ok ? "PASS" : "FAIL");
 uint decoded = 0;
 // Exercise original click scripts for every supported source scene and P524
 // variant, including unavailable hints and switching mentor during playback.
 for (int previous = 501; previous < 538; ++previous) {
  if (!loadPlace(previous) || !loadPlace(408) || !_movie) return false;
  uint32 now = 0;
  for (int variant = 0; variant < (previous == 524 ? 10 : 1); ++variant) {
   _runner.defineValue(0,10,variant);
   for (int mentor = 1; mentor <= 5; ++mentor) {
    const Sprite &button = _scene.sprites[mentor];
    const int x = button.renderX+10, y = button.renderY+10;
    if (spriteAt(x,y) != mentor || !_runner.canRun(button.click,true)) return false;
    const MentorClip clip = mentorClip(mentor,previous,variant);
    clickAtTime(x,y,now);
    for (int tick = 0; tick < 500; ++tick) { runScriptsAt(now); now += 20; }
    int32 unavailable = -1;
    ok = _runner.getValue(1,0,unavailable) && unavailable == int(!clip.duration) && !_runner.clicksBlocked() && ok;
    if (clip.duration) {
     ok = _moviePlaying && _movieX == 400 && _movieY == 30 &&
      _movie->getEndTime() == Audio::Timestamp(0,clip.start+clip.duration,30) && ok;
     const uint frames = _movieFramesDrawn; updateMovie();
     ok = _movieFramesDrawn > frames && _movieFrame.w > 0 && ok; ++decoded;
    } else ok = _lastSound == 2 && ok;
   }
  }
  clickAtTime(33,426,now); runScriptsAt(now); runScriptsAt(now+749);
  ok = _place == 408 && ok; runScriptsAt(now+750);
  ok = _place == previous && !_runner.clicksBlocked() && ok;
  debug("Astronomica mentors source P%d: %s (returned P%d)",previous,ok ? "PASS" : "FAIL",_place);
 }
 if (!loadPlace(523) || !loadPlace(408) || !_movie) return false;
 const Sprite &button = _scene.sprites[1];
 clickAtTime(button.renderX+10,button.renderY+10,0);
 for (uint32 now = 0; now < 2000 && !_moviePlaying; now += 10) runScriptsAt(now);
 const uint beforeFrames = _movieFramesDrawn;
 const uint32 started = _system->getMillis();
 while (_moviePlaying && _system->getMillis()-started < 12000) { updateMovie(); _system->delayMillis(5); }
 const uint continuousFrames = _movieFramesDrawn-beforeFrames;
 ok = !_moviePlaying && continuousFrames > 30 && _system->getMillis()-started >= 8000 && ok;
 debug("Astronomica mentor continuous playback: %s (%u frames, natural segment end)",ok ? "PASS" : "FAIL",continuousFrames);
 debug("Astronomica mentors interaction verification: %s (%u decoded selections, no-hint speech, timed return)",ok ? "PASS" : "FAIL",decoded);
 return ok;
}
bool AstronomicaEngine::verifyP523Puzzle() {
 _runner.defineValue(0,29,1); // Legitimate entry state for help/return.
 uint32 hash = 2166136261U;
 const int levels[] = {0,19,20,29,30,39,40,59,60,74,75,99};
 auto fold = [&](int value) { hash = (hash ^ uint32(value))*16777619U; };
 for (int event = 1; event <= 19; ++event)
  for (int a : levels) for (int b : levels) for (int c : levels)
   for (int buttons = 0; buttons < 4; ++buttons) for (int solved = 0; solved < 2; ++solved) {
    const int channels[] = {a,b,c}; const DangerStep step = dangerCallback(event,channels,buttons,solved);
    fold(step.actions.size());
    for (const DangerAction &action : step.actions) { fold(action.op); fold(action.a); fold(action.b); fold(action.c); }
    fold(step.destination);
   }
 bool ok = hash == 0xf8ea0405U; // Original instructions, with the explicit event8 repair.
 debug("Astronomica P523 callback comparison: %s (262656 cases, explicit event8 ABI repair, %08x)",ok ? "PASS" : "FAIL",hash);
 hash = 2166136261U;
 Common::Array<byte> seen; seen.resize(1000000); memset(&seen[0],0,seen.size());
 Common::Array<uint32> states; states.push_back(333333); seen[333333] = 1;
 uint edges = 0;
 for (uint index = 0; index < states.size(); ++index) {
  const int original[] = {int(states[index]/10000),int(states[index]/100%100),int(states[index]%100)};
  for (int button = 1; button <= 6; ++button) {
   int channels[] = {original[0],original[1],original[2]}; dangerAdjust(channels,button);
   for (int value : original) fold(value); fold(button); for (int value : channels) fold(value);
   const uint32 state = channels[0]*10000+channels[1]*100+channels[2]; ++edges;
   if (state >= seen.size()) return false;
   if (!seen[state]) { seen[state] = 1; states.push_back(state); }
  }
 }
 const bool spreadOK = states.size() == 5899 && edges == 35394 && hash == 0x40e80615U;
 debug("Astronomica P523 controls comparison: %s (%u states, %u transitions, %08x)",spreadOK ? "PASS" : "FAIL",states.size(),edges,hash);
 ok = spreadOK && ok;
 hash = 2166136261U;
 for (int value = 0; value < 100; ++value) for (int x : {121,244,362}) { fold(x); fold(dangerControlY(value)); }
 const bool positionOK = hash == 0x742cfb9dU;
 debug("Astronomica P523 position comparison: %s (100 exact x87 cases)",positionOK ? "PASS" : "FAIL");
 ok = positionOK && ok;
 const bool continuous = ConfMan.hasKey("astronomica_p523_continuous") && ConfMan.getBool("astronomica_p523_continuous");
 const int decisions[] = {1,4,6,8,10};
 for (int route = 0; route < (continuous ? 1 : 10); ++route) {
  if (!loadPlace(523) || !_movie) return false;
  _runner.defineValue(0,39,route == 1); const uint completed = _puzzlesCompleted;
  uint32 now = scriptClock();
  auto wait = [&](uint ms) {
   const uint32 end = now+ms;
   while (now < end) {
    runScriptsAt(now);
    if (continuous) { updateMovie(); animateSpritesAt(now); _system->delayMillis(5); now = scriptClock(); }
    else now += 10;
   }
  };
  auto press = [&](int id) {
   const Sprite &button = _scene.sprites[id-1]; const int x = button.renderX+1,y = button.renderY+1;
   if (_runner.clicksBlocked() || spriteAt(x,y) != id-1 || !_runner.canRun(button.click,true)) {
    debug("P523 button %d: blocked %d hit %d ready %d",id,int(_runner.clicksBlocked()),spriteAt(x,y),int(_runner.canRun(button.click,true)));return false;
   }
   clickAtTime(x,y,now);wait(350);return true;
  };
  bool good = _runner.enqueueStartup(_scene.scripts,now,true) == 1; wait(200);
  good = _moviePlaying && _dangerEvent[0] == 1 && _dangerEvent[1] == 13 && good;
  good = _dangerChannels[0] == 33 && _dangerChannels[1] == 33 && _dangerChannels[2] == 33 && good;
  if (route == 9) good = press(41) && _dangerChannels[2] > 33 && press(5) && _dangerButtons == 1 && good;
  if (route >= 8) { good = press(route == 8 ? 42 : 43) && good; wait(10000); }
  uint callbacks = 0, frames = 0; int answered = 0, prepared = 0;
  const uint32 started = _system->getMillis();
  while (route < 8 && _place == 523 && _moviePlaying && callbacks < 30 && _system->getMillis()-started < 240000) {
   int slot = _dangerEvent[0] ? 0 : 1;
   if (_dangerEvent[1] && (! _dangerEvent[0] || _dangerTime[1] < _dangerTime[0])) slot = 1;
   const int event = _dangerEvent[slot]; if (!event) break;
   bool decision = false; for (int e : decisions) decision = decision || event == e;
   const int prepareEvent = continuous ? _dangerEvent[0] : event;
   bool prepareDecision = false; for (int e : decisions) prepareDecision = prepareDecision || prepareEvent == e;
   if (prepareDecision && prepared != prepareEvent) {
    // Adjust while the long movie segment runs; answer after the secondary
    // callback opens the response window. Continuous input uses real delays.
    auto acceptable = [&]() { return prepareEvent == 1 ? _dangerChannels[2] >= 75 : prepareEvent == 4 || prepareEvent == 10 ? _dangerChannels[1] >= 75 : prepareEvent == 6 ? _dangerChannels[0] >= 40 && _dangerChannels[1] >= 20 : _dangerChannels[2] >= 30; };
    const int control = prepareEvent == 1 || prepareEvent == 8 ? 6 : prepareEvent == 6 ? 4 : 5;
    for (int i = 0; i < 12 && !acceptable(); ++i) good = press(35+control) && good;
    good = acceptable() && good;
    prepared = prepareEvent;
   }
   if (decision && answered != event) {
    const bool fail = route >= 2 && route <= 6 && event == decisions[route-2];
    if (!fail) { good = press(route == 0 ? 6 : 5) && good; if (route == 7) good = press(6) && good; }
    answered = event;
   }
   if (continuous) {
    const uint before = _movieFramesDrawn;
    updateMovie(); if (_movie && _movieFramesDrawn > before) frames += _movieFramesDrawn-before;
    now = scriptClock(); runScriptsAt(now); animateSpritesAt(now); _system->delayMillis(5);
   } else {
    good = _movie->seek(Audio::Timestamp(0,_dangerTime[slot]+1,30)) && good; updateMovie();
   }
   if (_place != 523 || _dangerEvent[slot] != event) ++callbacks;
  }
  int32 solved = 0; _runner.getValue(0,39,solved);
  const bool victory = route < 2 || route == 7;
  good = _place == (victory ? 524 : route == 9 ? 408 : 117) && solved == int(victory) &&
   _puzzlesCompleted == completed+(victory && route != 1 ? 1 : 0) && !_dangerEvent[0] && !_dangerEvent[1] && good;
  if (route == 9 && _place == 408) {
   // P408's original return button reloads the previous place. P523's
   // entry program runs custom20 (reset channels), then custom5 (new movie).
   good = spriteAt(33,426) == 0 && good;
   clickAtTime(33,426,now); wait(2000);
   good = _place == 523 && _previousPlace == 408 && _movie && !_runner.clicksBlocked() && good;
   if (_place == 523 && _movie) {
    good = _runner.enqueueStartup(_scene.scripts,now,true) == 1 && good; wait(200);
    good = _moviePlaying && _dangerEvent[0] == 1 && _dangerTime[0] == 600 &&
     _dangerEvent[1] == 13 && _dangerTime[1] == 510 && _dangerButtons == 0 &&
     _dangerChannels[0] == 33 && _dangerChannels[1] == 33 && _dangerChannels[2] == 33 && good;
    good = press(41) && _dangerChannels[2] > 33 && good;
    good = press(42) && good; wait(10000);
    good = _place == 117 && !_movie && !_dangerEvent[0] && !_dangerEvent[1] &&
     _runner.getValue(0,39,solved) && solved == 0 && _puzzlesCompleted == completed && good;
   }
   debug("Astronomica P523 help return: %s (fresh movie callbacks, reset controls, interactive exit)",good ? "PASS" : "FAIL");
  }
  if (continuous) good = frames > 100 && _system->getMillis()-started > 60000 && good;
  debug("Astronomica P523 route %d: %s (P%d, %u callbacks, solved %d, %u frames)",route,good ? "PASS" : "FAIL",_place,callbacks,solved,frames);
  ok = good && ok;
 }
 debug("Astronomica P523 interaction verification: %s",ok ? "PASS" : "FAIL");
 return ok;
}


// Diagnostic in-memory packet:24 header words,607 runner,378 sprites,
//118Comet/Jupiter,5Ball and checksum. No ASVM format or save capability.
static const uint kP510Header=24,kP510Runner=24,kP510Sprite=631,kP510Extra=1009,kP510Ball=1127,kP510Words=1133;
static uint32 p510PacketHash(const Common::Array<uint32>&w){uint32 h=2166136261U;for(uint i=0;i+1<w.size();++i)h=(h^w[i])*16777619U;return h;}
static bool p510Private(const Common::Array<uint32>&w){
 for(uint i=0;i<100;++i)if(w[kP510Extra+i])return false;
 if(w[kP510Extra+100]!=0xffffffffU||w[kP510Extra+101])return false;
 const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;
 for(uint i=0;i<8;++i){empty&=!w[kP510Extra+102+i]&&!w[kP510Extra+110+i];configured&=w[kP510Extra+102+i]==widths[i]&&w[kP510Extra+110+i]==heights[i];}
 return (empty||configured)&&!w[kP510Ball]&&!w[kP510Ball+1]&&!w[kP510Ball+2]&&w[kP510Ball+3]==2&&w[kP510Ball+4]==10;
}
static bool p510Tuple(const Common::Array<uint32>&w){
 auto matches=[&](const PlotStep&s){return s.start>=0&&uint32(s.start)==w[13]&&uint32(s.start+s.duration)==w[14]&&uint32(s.event)==w[15]&&uint32(s.time)==w[16];};
 for(int mode=1;mode<=3;++mode)if(matches(plotStart(mode)))return true;
 for(int event=20;event<=54;++event)for(int choice=1;choice<=5;++choice)if(matches(plotCallback(event,choice)))return true;return false;
}
static bool p510Marker(int32 x,int32 y){
 for(int mode=1;mode<=3;++mode){const PlotStep s=plotStart(mode);if(x==s.x&&y==s.y)return true;}
 for(int event=20;event<=54;++event)for(int choice=1;choice<=5;++choice){const PlotStep s=plotCallback(event,choice);if(s.x>=0&&x==s.x&&y==s.y)return true;}return false;
}
AstronomicaEngine::P510Prepared::~P510Prepared(){clearOwned();}
void AstronomicaEngine::P510Prepared::clearOwned(){delete decoder;decoder=nullptr;background.free();displayed.free();composed.free();scene=Scene();runner=ScriptRunner();packet.clear();ready=false;}
bool AstronomicaEngine::P510Prepared::empty()const{return !ready&&!decoder&&!background.getPixels()&&!displayed.getPixels()&&!composed.getPixels()&&scene.sprites.empty()&&scene.scripts.empty()&&scene.mouseRects.empty()&&scene.conditions.empty()&&scene.movies.empty()&&!runner.pendingCount()&&packet.empty();}
bool AstronomicaEngine::captureP510Packet(Common::Array<uint32>&words,uint32 now)const{
 if(_movie&&(!_movie->isPlaying()||_movie->isPaused()!=_clockPaused||_movie->getRate()!=Common::Rational(1,1)))return false;
 if(_place!=510||!_movie||!_moviePlaying||_loopEnabled||(_loopSound!=-1&&_loopSound!=0)||_mixer->isSoundHandleActive(_soundHandle)||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty())return false;
 if(!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return false;
 if(_scene.sprites.size()!=14||_rocket.kind!=RocketMotion::kStopped||_rocket.delta||_rocket.since||_probe.year!=1991||_probe.yearArmed||_probe.specialHit||_probe.flying||_probe.expired||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_worldMovieCursorBottom!=-1)return false;
 for(uint i=0;i<3;++i)if(_probe.widths[i]||_probe.heights[i])return false;
 for(const HoverTarget&h:_hoverSprites)if(h.entered)return false;for(const HoverTarget&h:_hoverRects)if(h.entered)return false;
 for(const Sprite&s:_scene.sprites)if(s.dragEnabled||s.orbitMotion||s.planetMotion||s.planetPeriod!=-1)return false;
 if(!_hoverSprites.empty()||!_hoverRects.empty()||_nav[0]||_nav[1]||_nav[2]||_universeSegmentEnd||_universeAssetsValid||!_questionSaveBaseline.empty())return false;
 if(_p519LargeImage||_p519SmallImage||_p528EarthImage||_p528MoonImage||_p528TallMoon||!_p528HistoryValid||!_p530HistoryValid||!_p513HistoryValid||!_p517HistoryValid||!_builderHistoryValid)return false;
 if(_probeAssetsValid||_rendezvousAssetsValid||_p501AssetsValid||_p502AssetsValid||_p503AssetsValid||_p504AssetsValid||_p527AssetsValid||_p516AssetsValid||_p511AssetsValid||_p509AssetsValid||_p521AssetsValid||_planetAssetsValid)return false;
 Common::Array<uint32>runner;if(!_runner.exportP510ActiveState(runner,now))return false;
 const uint32 mediaMs=_movie->getTime();const int currentFrame=_movie->getCurFrame(),soughtFrame=int(mediaMs/100)-1;if(currentFrame<soughtFrame||currentFrame>soughtFrame+1)return false;
 const uint32 header[]={510,_puzzlesCompleted,now,uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,0,uint32(_comet.frame),uint32(_comet.previousFrame),mediaMs,uint32(currentFrame),uint32(_moviePresentedFrame),_movieSegmentStart,uint32(_movie->getEndTime().convertToFramerate(30).totalNumberOfFrames()),uint32(_plotEvent),_plotTime,uint32(_moviePlaying),uint32(_movieX),uint32(_movieY),uint32(_movie->getVolume()),uint32(_lastSound),_lastBlockingSoundEnd,_lastSuccessEnd};
 Common::Array<uint32>w;for(uint32 v:header)w.push_back(v);for(uint32 v:runner)w.push_back(v);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,w);Common::Array<uint32>extra;p516Extra(extra);for(uint32 v:extra)w.push_back(v);for(int32 v:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})w.push_back(uint32(v));w.push_back(0);if(w.size()!=kP510Words)return false;w.back()=p510PacketHash(w);if(!p510Private(w))return false;words=w;return true;
}
class P510PreparedDecoder final : public Video::QuickTimeDecoder { public: void startPrepared(bool paused){
 const uint32 media=getTime();if(paused)pauseVideo(true);start();
 if(paused){if(ConfMan.hasKey("astronomica_verify_p510_clock_delay")&&ConfMan.getBool("astronomica_verify_p510_clock_delay"))g_system->delayMillis(2);
 resetPauseStartTime();_startTime=int32(uint32(_startTime)+getTime()-media);
 const uint32 actual=getTime();if(actual!=media)debug("P510 PAUSE ANCHOR DIFFERENCE saved%u actual%u delta%d start%u",media,actual,int32(actual-media),uint32(_startTime));
 }
} };
bool AstronomicaEngine::prepareP510Packet(const Common::Array<uint32>&w,P510Prepared&out){
 if(!out.empty())return false;
 if(w.size()!=kP510Words||w.back()!=p510PacketHash(w)||w[0]!=510||(w[3]>537&&w[3]!=0xffffffffU)||(w[4]!=0xffffffffU&&w[4]!=0)||w[5]||w[7]||w[8]<1||w[8]>12||w[9]>12||w[10]>=378000||(w[11]>=3780&&w[11]!=0xffffffffU)||(w[12]>=3780&&w[12]!=0xffffffffU)||w[17]!=1||w[18]!=261||w[19]!=33||w[20]>255||(w[21]>922&&w[21]!=0xffffffffU)||!p510Private(w)||!p510Tuple(w))return (debug("P510 preflight rejection line%d",__LINE__),false);
 if(uint64(w[10])*30>=uint64(w[14])*1000)return (debug("P510 preflight rejection line%d",__LINE__),false);
 if(uint64(w[10])<uint64(w[13])*1000/30)return false;
 if(!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P510/MEGAFILE.HYP"),439846,910364267U)||!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P510/FLATPLOT.MOV"),24246078,3073739601U))return (debug("P510 preflight rejection line%d",__LINE__),false);
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P510/MEGAFILE.HYP"))))return (debug("P510 preflight rejection line%d",__LINE__),false);ResourceReader reader(file);if(!reader.read(out.scene)||out.scene.mode||out.scene.layers!=1||out.scene.sprites.size()!=14||out.scene.conditions.size()!=7||out.scene.scripts.size()!=4||out.scene.consumed!=439846||out.scene.trailing||out.scene.commandCount!=79)return (debug("P510 preflight rejection line%d",__LINE__),false);
 Common::Array<uint32>runner;for(uint i=0;i<607;++i)runner.push_back(w[kP510Runner+i]);out.runner.loadLocalConditions(out.scene.conditions);out.runner.setPrograms(out.scene.scripts,runner[601]);out.runner.setPlotSupport(true);if(!out.runner.importP510ActiveState(runner,w[2]))return (debug("P510 preflight rejection line%d",__LINE__),false);
 // Compare untouched fields against freshly parsed originals. Independent
 // countdown sprites each use their own original state and full saved record.
 for(uint i=0;i<14;++i){Sprite expected=out.scene.sprites[i];expected.selectedFrame=0;const uint at=kP510Sprite+i*27;const uint frames=spriteFrameCount(out.scene,i);if(!frames||w[at+1]>=frames)return (debug("P510 preflight rejection line%d",__LINE__),false);expected.selectedFrame=w[at+1];
  if(i==1){if(w[at]||!p510Marker(int32(w[at+4]),int32(w[at+5]))||int32(w[2]-w[at+8])<0)return (debug("P510 preflight rejection line%d",__LINE__),false);expected.visible=0;expected.renderX=int16(w[at+4]);expected.renderY=int16(w[at+5]);expected.frameSince=w[at+8];}
  if(i==7||i==8){const int32 increments=52-int32(runner[303]);expected.y=int32(uint32(expected.y)+uint32(increments));expected.renderY=int16(int32(expected.renderY)+increments);}
  Common::Array<uint32>baseline;p526SpriteWords(expected,baseline);for(uint j=0;j<27;++j)if(w[at+j]!=baseline[j])return (debug("P510 preflight rejection line%d",__LINE__),false);
  p526RestoreSprite(out.scene.sprites[i],&w[at]);
 }
 file.seek(0);if(file.readSint32LE()!=0)return (debug("P510 preflight rejection line%d",__LINE__),false);out.background.create(640,480,_screen.format);out.background.fillRect(Common::Rect(640,480),0);if(!readImage(file,out.background,false)||!readImage(file,out.background,true))return (debug("P510 preflight rejection line%d",__LINE__),false);
 auto open=[&](){Common::File*f=new Common::File();if(!f->open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P510/FLATPLOT.MOV")))){delete f;return (Video::QuickTimeDecoder*)nullptr;}Video::QuickTimeDecoder*d=new P510PreparedDecoder();if(!d->loadStream(f)){delete d;return (Video::QuickTimeDecoder*)nullptr;}return d;};
 if(w[12]!=0xffffffffU){Video::QuickTimeDecoder*display=open();if(!display)return (debug("P510 preflight rejection line%d",__LINE__),false);bool ok=display->seekToFrame(w[12]);const Graphics::Surface*frame=ok?display->decodeNextFrame():nullptr;Graphics::Surface*rgb=frame?frame->convertTo(_screen.format,display->getPalette()):nullptr;if(!rgb){delete display;return (debug("P510 preflight rejection line%d",__LINE__),false);}out.displayed.copyFrom(*rgb);rgb->free();delete rgb;delete display;}
 out.decoder=open();if(!out.decoder||out.decoder->getFrameCount()!=3780||out.decoder->getWidth()!=320||out.decoder->getHeight()!=240||out.decoder->getTimeScale()!=30)return (debug("P510 preflight rejection line%d",__LINE__),false);
 out.decoder->setEndTime(Audio::Timestamp(0,w[14],30));out.decoder->setVolume(w[20]);if(!out.decoder->seek(Audio::Timestamp(w[10])))return (debug("P510 preflight rejection line%d",__LINE__),false);const int sought=out.decoder->getCurFrame(),current=int32(w[11]);if(current<sought||current>sought+1)return (debug("P510 preflight rejection line%d",__LINE__),false);if(current>sought&&!out.decoder->decodeNextFrame())return (debug("P510 preflight rejection line%d",__LINE__),false);
 if(out.decoder->isPlaying()||out.decoder->getTime()!=w[10]||out.decoder->getCurFrame()!=current)return false;
 if(!bindP510Prepared(out))return false;
 out.composed.copyFrom(out.background);const uint drawn=renderStaticSprites(file,out.scene,out.composed);if(drawn!=13)return false;
 if(out.displayed.w)out.composed.copyRectToSurface(out.displayed.getPixels(),out.displayed.pitch,w[18],w[19],out.displayed.w,out.displayed.h);
 out.packet=w;out.ready=true;return true;
}
bool AstronomicaEngine::testP510Combined(uint32 now){
 static uint calls=0,accepted=0,rejected=0;Common::Array<uint32>w;if(!captureP510Packet(w,now)){++rejected;debug("P510 combined boundary excluded: calls%u rejected%u",++calls,rejected);return true;}
 auto surfaceHash=[](const Graphics::Surface&s){uint32 h=2166136261U;for(int y=0;y<s.h;++y)for(int x=0;x<s.w*s.format.bytesPerPixel;++x)h=(h^*((const byte*)s.getBasePtr(0,y)+x))*16777619U;return h;};
 auto live=[&](){uint32 h=_runner.probeDiagnosticHash(true);auto add=[&](uint32 v){h=(h^v)*16777619U;};for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,_pausedMillis,_pauseStarted,uint32(_clockPaused),uint32(_plotEvent),_plotTime,_movieSegmentStart,uint32(_moviePresentedFrame),uint32(_moviePlaying),uint32(_movieX),uint32(_movieY),_soundsStarted,uint32(_lastSound),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,_lastBlockingSoundEnd,_lastSuccessEnd,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_movie&&_movie->isPlaying()),uint32(_movie&&_movie->isPaused()),uint32(_movie?_movie->getVolume():0),uint32(_comet.frame),uint32(_comet.previousFrame),uint32(_rocket.kind),uint32(_rocket.delta),_rocket.since,uint32(_probe.year),uint32(_probe.flying)})add(v);Common::Array<uint32>extra;p516Extra(extra);for(uint32 v:extra)add(v);for(const Sprite&s:_scene.sprites){Common::Array<uint32>b;p526SpriteWords(s,b);for(uint32 v:b)add(v);}for(int32 v:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})add(uint32(v));for(const Common::String*name:{&_pendingImageName,&_displayedImageName})for(char c:*name)add(byte(c));for(const Graphics::Surface*image:{&_screen,&_background,&_movieFrame,&_pendingImage}){add(image->w);add(image->h);add(surfaceHash(*image));}return h;};
 const uint32 before=live();Video::QuickTimeDecoder*const liveDecoder=_movie;const void*screenPixels=_screen.getPixels(),*moviePixels=_movieFrame.getPixels(),*backgroundPixels=_background.getPixels(),*pendingPixels=_pendingImage.getPixels();
 auto unchanged=[&](){return live()==before&&_movie==liveDecoder&&_screen.getPixels()==screenPixels&&_movieFrame.getPixels()==moviePixels&&_background.getPixels()==backgroundPixels&&_pendingImage.getPixels()==pendingPixels;};
 {Common::String header;for(uint i=0;i<24;++i)header+=Common::String::format("%u,",w[i]);debug("P510 combined header %s private%d tuple%d",header.c_str(),p510Private(w),p510Tuple(w));}
 P510Prepared prepared;if(!prepareP510Packet(w,prepared)){debug("P510 combined valid packet rejected at clock%u",now);return (debug("P510 preflight rejection line%d",__LINE__),false);}
 if(!unchanged()||surfaceHash(prepared.background)!=surfaceHash(_background)||surfaceHash(prepared.displayed)!=surfaceHash(_movieFrame)||prepared.decoder->isPlaying())return (debug("P510 preflight rejection line%d",__LINE__),false);
 Common::Array<uint32>again;if(!prepared.runner.exportP510ActiveState(again,now))return (debug("P510 preflight rejection line%d",__LINE__),false);for(uint i=0;i<607;++i)if(again[i]!=w[kP510Runner+i])return (debug("P510 preflight rejection line%d",__LINE__),false);
 // Exhaustive shape/checksum tests run once. Prepared objects remain stopped;
 // elapsed wall/audio time is allowed but clock origins and live data cannot change.
 if(!accepted){for(uint size=0;size<kP510Words;++size){Common::Array<uint32>bad=w;bad.resize(size);P510Prepared candidate;if(prepareP510Packet(bad,candidate))return (debug("P510 preflight rejection line%d",__LINE__),false);}for(uint i=0;i<kP510Words;++i){Common::Array<uint32>bad=w;bad[i]^=1;P510Prepared candidate;if(prepareP510Packet(bad,candidate))return (debug("P510 preflight rejection line%d",__LINE__),false);}if(!unchanged())return (debug("P510 preflight rejection line%d",__LINE__),false);}
 const uint offsets[]={0,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,kP510Runner+303,kP510Runner+304,kP510Runner+605,kP510Sprite+27+4,kP510Sprite+27+8,kP510Sprite+7*27+3,kP510Sprite+8*27+3,kP510Extra,kP510Extra+100,kP510Extra+102,kP510Ball+3};
 for(uint offset:offsets){Common::Array<uint32>bad=w;bad[offset]=offset==kP510Runner+303?52U:offset==kP510Sprite+27+8?now+1:0xfffffffeU;bad.back()=p510PacketHash(bad);P510Prepared candidate;if(prepareP510Packet(bad,candidate)||!unchanged())return (debug("P510 preflight rejection line%d",__LINE__),false);}
 if(w[13]){Common::Array<uint32>bad=w;bad[10]=uint32(uint64(w[13])*1000/30)-1;bad.back()=p510PacketHash(bad);P510Prepared candidate;if(prepareP510Packet(bad,candidate)||!unchanged())return false;debug("P510 segment lower-bound rejection: PASS (start%u,time%u)",w[13],bad[10]);}
 ++accepted;++calls;debug("P510 combined preflight: PASS (accepted%u,calls%u,rejected%u,1133words,29invalidfields,stopped owned decoders)",accepted,calls,rejected);return true;
}

// Isolated actual-engine commit milestone. No ASVM file format or public save.
template<class T>static void p510SwapValue(T&a,T&b){T value=a;a=b;b=value;}
static void p510SwapSurface(Graphics::Surface&a,Graphics::Surface&b){Graphics::Surface value=a;a=b;b=value;}
static void p510SwapScene(Scene&a,Scene&b){
 p510SwapValue(a.mode,b.mode);p510SwapValue(a.layers,b.layers);p510SwapValue(a.introSound,b.introSound);p510SwapValue(a.introSoundId,b.introSoundId);
 for(uint i=0;i<3;++i)p510SwapValue(a.nav[i],b.nav[i]);p510SwapValue(a.background,b.background);p510SwapValue(a.control,b.control);
 a.sprites.swap(b.sprites);a.scripts.swap(b.scripts);a.mouseRects.swap(b.mouseRects);a.conditions.swap(b.conditions);a.movies.swap(b.movies);
 p510SwapValue(a.consumed,b.consumed);p510SwapValue(a.trailing,b.trailing);p510SwapValue(a.bitmapCount,b.bitmapCount);p510SwapValue(a.commandCount,b.commandCount);
}
bool AstronomicaEngine::bindP510Prepared(P510Prepared&out){
 // Build normal P510 capabilities in the fresh recipient. No commands tick.
 Common::Array<uint>sprites;for(uint i=0;i<out.scene.sprites.size();++i)sprites.push_back(spriteFrameCount(out.scene,i));out.runner.setSpriteTargets(sprites);
 Common::Array<uint32>movies;movies.push_back(out.decoder->getDuration().totalNumberOfFrames());out.runner.setMovieTargets(movies);
 Common::Array<Common::String>images;out.runner.setImageTargets(images);
 Common::Array<bool>sounds;sounds.resize(923);for(uint i=0;i<sounds.size();++i)sounds[i]=false;
 auto wav=[&](const Common::Path&path){Common::File file;if(!file.open(Common::FSNode(path)))return false;int size,rate;byte flags;uint16 type;return Audio::loadWAVFromStream(file,size,rate,flags,&type)&&type==1;};
 Common::FSList files;Common::FSNode(ConfMan.getPath("path").join("PLACES/P510")).getChildren(files,Common::FSNode::kListFilesOnly);
 for(const Common::FSNode&file:files){Common::String name=file.getName();name.toUppercase();if(!name.hasPrefix("S")||!name.hasSuffix(".WAV"))continue;const int id=atoi(name.c_str()+1);if(id>=0&&id<900&&name==Common::String::format("S%d.WAV",id))sounds[id]=wav(file.getPath());}
 for(uint id=900;id<=922;++id)sounds[id]=wav(ConfMan.getPath("path").join(Common::Path(Common::String::format("SOUNDS/S%d.WAV",id-900))));
 if(!sounds[912]||!sounds[300])return false;for(uint id=0;id<=10;++id)if(!sounds[id])return false;out.runner.setSoundTargets(sounds);out.runner.setGameStateHandler(this);out.runner.setSoundHandler(this);out.runner.setSuccessHandler(this,510);
 if(!out.runner.p510Capabilities(this,this,this,out.scene))return false;
 for(const Script&program:out.scene.scripts)if(!out.runner.canRun(program,true))return false;
 for(const Sprite&sprite:out.scene.sprites)for(const Script*program:{&sprite.click,&sprite.drag,&sprite.mouseIn,&sprite.mouseOut})if(!program->empty()&&!out.runner.canRun(*program,true))return false;return true;
}
void AstronomicaEngine::commitP510Prepared(P510Prepared&out){
 assert(out.ready&&out.decoder&&!out.decoder->isPlaying());
 const Common::Array<uint32>&w=out.packet;
 // Commit starts here. Every file/codec/target/composition operation is done.
 // Array/surface swaps transfer ownership without generic Scene/runner copies.
 _mixer->stopHandle(_soundHandle);if(_movie)_movie->stop();delete _movie;_movie=out.decoder;out.decoder=nullptr;
 p510SwapScene(_scene,out.scene);_runner.swapP510PreparedRunner(out.runner);
 p510SwapSurface(_background,out.background);p510SwapSurface(_movieFrame,out.displayed);p510SwapSurface(_screen,out.composed);
 _place=510;_previousPlace=int32(w[3]);_puzzlesCompleted=w[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-w[2];
 _loopSound=int32(w[4]);_loopEnabled=w[5]!=0;_lastSoundAt=w[6];_lastSound=int32(w[21]);_lastBlockingSoundEnd=w[22];_lastSuccessEnd=w[23];
 _comet.frame=w[8];_comet.previousFrame=w[9];for(uint i=0;i<50;++i){_comet.kind[i]=int32(w[kP510Extra+i]);_comet.partner[i]=int32(w[kP510Extra+50+i]);}_comet.sound=int32(w[kP510Extra+100]);_comet.explosion=int32(w[kP510Extra+101]);
 for(uint i=0;i<8;++i){_jupiterWidths[i]=w[kP510Extra+102+i];_jupiterHeights[i]=w[kP510Extra+110+i];}
 _ball.scenario=int32(w[kP510Ball]);_ball.centerX=int32(w[kP510Ball+1]);_ball.centerY=int32(w[kP510Ball+2]);_ball.side=int32(w[kP510Ball+3]);_ball.period=int32(w[kP510Ball+4]);
 _rocket=RocketMotion();_probe=ProbeMotion();_plotEvent=int32(w[15]);_plotTime=w[16];_movieSegmentStart=w[13];_moviePresentedFrame=int32(w[12]);_movieX=w[18];_movieY=w[19];_movieFramesDrawn=0;
 _dangerEvent[0]=_dangerEvent[1]=0;_dangerButtons=0; // inactive channels/times retain recipient convention
 _worldMovieCursorBottom=-1;_universeSegmentEnd=0;_universeAssetsValid=false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_pendingImageX=_pendingImageY=0;
 _hoverSprites.clear();_hoverRects.clear();_nav[0]=_nav[1]=_nav[2]=0;_questionSaveBaseline.clear();
 _p519LargeImage=_p519SmallImage=_p528EarthImage=_p528MoonImage=_p528TallMoon=0;
 _p528HistoryValid=_p530HistoryValid=_p513HistoryValid=_p517HistoryValid=_builderHistoryValid=true;
 _probeAssetsValid=_rendezvousAssetsValid=_p501AssetsValid=_p502AssetsValid=_p503AssetsValid=_p504AssetsValid=_p527AssetsValid=_p516AssetsValid=_p511AssetsValid=_p509AssetsValid=_p521AssetsValid=_planetAssetsValid=false;
 // _soundsStarted, help/legacy caches, user volumes and inactive danger
 // channels/times are recipient process state, not manufactured sound starts.
 out.clearOwned();if(!out.empty())error("P510 ownership release FAIL");debug("P510 ownership release: PASS (empty holder)");++_p510InstallCommits;
 static_cast<P510PreparedDecoder*>(_movie)->startPrepared(_clockPaused);_moviePlaying=true;++_p510InstallStarts;presentScene();
}
bool AstronomicaEngine::installP510Packet(const Common::Array<uint32>&words){
 // Receiver Engine pause ownership is retained; prepared tracks stay stopped.
 P510Prepared prepared;if(!prepareP510Packet(words,prepared))return false;commitP510Prepared(prepared);return true;
}
uint32 AstronomicaEngine::p510WholeLiveHash()const{
 uint32 h=_runner.p510CompleteHash();auto add=[&](uint32 value){h=(h^value)*16777619U;};
 for(uint32 value:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,_pausedMillis,_pauseStarted,uint32(_clockPaused),uint32(_plotEvent),_plotTime,_movieSegmentStart,uint32(_moviePresentedFrame),uint32(_moviePlaying),uint32(_movieX),uint32(_movieY),_movieFramesDrawn,_soundsStarted,uint32(_lastSound),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,_lastBlockingSoundEnd,_lastSuccessEnd,uint32(_mixer->isSoundHandleActive(_soundHandle)),uint32(_comet.frame),uint32(_comet.previousFrame),uint32(_rocket.kind),uint32(_rocket.delta),_rocket.since,uint32(_probe.year),uint32(_probe.yearArmed),uint32(_probe.specialHit),uint32(_probe.flying),uint32(_probe.expired),uint32(_dangerButtons),uint32(_worldMovieCursorBottom),_universeSegmentEnd,uint32(_universeAssetsValid),uint32(_probeAssetsValid),uint32(_rendezvousAssetsValid),uint32(_p501AssetsValid),uint32(_p502AssetsValid),uint32(_p503AssetsValid),uint32(_p504AssetsValid),uint32(_p527AssetsValid),uint32(_p516AssetsValid),uint32(_p511AssetsValid),uint32(_p509AssetsValid),uint32(_p521AssetsValid),uint32(_planetAssetsValid),_p519LargeImage,_p519SmallImage,_p528EarthImage,_p528MoonImage,_p528TallMoon,uint32(_p528HistoryValid),uint32(_p530HistoryValid),uint32(_p513HistoryValid),uint32(_p517HistoryValid),uint32(_builderHistoryValid),uint32(_pendingImageX),uint32(_pendingImageY),uint32(_legacyChecked),uint32(_legacyAvailable),uint32(_helpAttempted),_helpOpened,_p510InstallCommits,_p510InstallStarts})add(value);
 for(uint i=0;i<3;++i){add(_probe.widths[i]);add(_probe.heights[i]);add(_dangerChannels[i]);add(_nav[i]);}for(uint i=0;i<2;++i){add(_dangerEvent[i]);add(_dangerTime[i]);}
 for(Audio::Mixer::SoundType type:{Audio::Mixer::kMusicSoundType,Audio::Mixer::kSFXSoundType,Audio::Mixer::kPlainSoundType}){add(_mixer->getVolumeForSoundType(type));add(_mixer->isSoundTypeMuted(type));}
 Common::Array<uint32>extra;p516Extra(extra);for(uint32 v:extra)add(v);for(int32 v:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})add(v);
 auto sprite=[&](const Sprite&s){Common::Array<uint32>values;p526SpriteWords(s,values);for(uint32 v:values)add(v);add(s.dragEnabled);add(s.planetMotion);add(s.planetPeriod);};for(const Sprite&s:_scene.sprites)sprite(s);for(const Sprite&s:_questionSaveBaseline)sprite(s);
 for(const Common::Array<HoverTarget>*targets:{&_hoverSprites,&_hoverRects}){add(targets->size());for(const HoverTarget&t:*targets){add(t.width);add(t.height);add(t.ready);add(t.entered);}}
 for(const Common::String*name:{&_pendingImageName,&_displayedImageName}){add(name->size());for(char c:*name)add(byte(c));}
 for(const Graphics::Surface*image:{&_screen,&_background,&_movieFrame,&_pendingImage}){uint64 ptr=uint64(reinterpret_cast<uintptr_t>(image->getPixels()));add(uint32(ptr));add(uint32(ptr>>32));add(image->w);add(image->h);for(int y=0;y<image->h;++y)for(int x=0;x<image->w*image->format.bytesPerPixel;++x)add(*((const byte*)image->getBasePtr(0,y)+x));}
 uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_movie));add(uint32(ptr));add(uint32(ptr>>32));if(_movie){add(_movie->isPlaying());add(_movie->isPaused());add(_movie->getRate().getNumerator());add(_movie->getRate().getDenominator());add(_movie->getCurFrame());add(_movie->getVolume());add(_movie->getEndTime().msecs());}return h;
}
bool AstronomicaEngine::canSaveP510()const{Common::Array<uint32>words;return captureP510Packet(words,scriptClock());}
Common::Error AstronomicaEngine::saveP510(Common::WriteStream*stream){
 Common::Array<uint32>words;if(!captureP510Packet(words,scriptClock()))return Common::kWritingFailed;
 P510Prepared validation;if(!prepareP510Packet(words,validation))return Common::kWritingFailed;
 stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(28);for(uint32 word:words)stream->writeUint32LE(word);
 return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP510(Common::SeekableReadStream*stream){
 if(stream->size()-stream->pos()<kP510Words*4||!ConfMan.getBool("astronomica_audio")||!ConfMan.getBool("astronomica_animation")||!ConfMan.getBool("astronomica_sprite_input"))return Common::kReadingFailed;
 Common::Array<uint32>words;words.resize(kP510Words);for(uint32&word:words)word=stream->readUint32LE();
 if(stream->err()||!installP510Packet(words))return Common::kReadingFailed;return Common::kNoError;
}
bool AstronomicaEngine::testP510FileSave(uint32 now){
 static uint boundaries=0;Common::Array<uint32>original;if(!captureP510Packet(original,now))return true;
 // The route driver uses synthetic script ticks with a native media clock.
 // Rebase its script epoch before entering the real Engine GUI pause path.
 _pausedMillis=_system->getMillis()-now;PauseToken pause=pauseEngine();
 Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(!canSaveGameStateCurrently()||saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=4540)return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
 Common::Array<byte>fixture;fixture.resize(out.size());memcpy(&fixture[0],out.getData(),out.size());
 auto restore=[&](const Common::Array<byte>&data){Common::MemoryReadStream input(&data[0],data.size());return loadGameStream(&input).getCode()==Common::kNoError;};
 if(!restore(fixture)||!_clockPaused||!_movie->isPaused())return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
 Common::MemoryWriteStreamDynamic again(DisposeAfterUse::YES);const Common::Error againError=saveGameStream(&again);
 if(againError.getCode()!=Common::kNoError||again.size()!=fixture.size()||(again.size()==fixture.size()&&memcmp(again.getData(),&fixture[0],fixture.size()))){
  uint difference=0;while(difference<MIN<uint>(again.size(),fixture.size())&&again.getData()[difference]==fixture[difference])++difference;
  debug("P510 BYTE DIFFERENCE boundary%u error%d saved%u again%u firstbyte%u word%d clock%u media%u",boundaries,int(againError.getCode()),uint(fixture.size()),uint(again.size()),difference,int(difference<8?-1:(difference-8)/4),scriptClock(),_movie?_movie->getTime():0);
  if(again.size()==fixture.size())for(uint byte=8;byte+4<=fixture.size();byte+=4)if(READ_LE_UINT32(&fixture[byte])!=READ_LE_UINT32(again.getData()+byte))debug("P510 BYTE WORD %u saved%u again%u",(byte-8)/4,READ_LE_UINT32(&fixture[byte]),READ_LE_UINT32(again.getData()+byte));
  return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
 }

 if(!boundaries){
  const uint32 unchanged=p510WholeLiveHash(),clock=scriptClock(),media=_movie->getTime();const Video::QuickTimeDecoder*decoder=_movie;const void*display=_movieFrame.getPixels();
  auto unchangedState=[&](){return p510WholeLiveHash()==unchanged&&scriptClock()==clock&&_movie->getTime()==media&&_movie==decoder&&_movieFrame.getPixels()==display;};
  auto reject=[&](const Common::Array<byte>&data){Common::MemoryReadStream input(&data[0],data.size());return loadGameStream(&input).getCode()!=Common::kNoError&&unchangedState();};
  for(uint length=0;length<fixture.size();++length){Common::MemoryReadStream input(length?&fixture[0]:nullptr,length);if(loadGameStream(&input).getCode()==Common::kNoError||!unchangedState())return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);}
  for(uint index=0;index<fixture.size();++index){Common::Array<byte>bad=fixture;bad[index]^=1;if(!reject(bad))return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);}
  uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);uint32 hash=2166136261U;for(uint at=8;at<bad.size()-4;at+=4)hash=(hash^READ_LE_UINT32(&bad[at]))*16777619U;WRITE_LE_UINT32(&bad[bad.size()-4],hash);++invalid;const bool ok=reject(bad);if(!ok)debug("P510 ASVM28 invalid field%u value%u unexpectedly accepted",index,value);return ok;};
  for(uint index:{0U,3U,4U,5U,7U,8U,9U,10U,11U,12U,13U,14U,15U,17U,18U,19U,20U,21U})if(!badWord(index,0xfffffffeU))return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
  if(!badWord(kP510Runner+303,52)||!badWord(kP510Runner+606,clock+1)||!badWord(kP510Sprite+1,9999)||!badWord(kP510Extra+102,1234)||!badWord(kP510Ball+3,99))return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
  if(saveGameState(27,"P510 native paused continuation").getCode()!=Common::kNoError||!unchangedState())return (debug("P510 FILE TEST RETURN line%d boundary%u now%u script%u media%u paused%d",__LINE__,boundaries,now,scriptClock(),_movie?_movie->getTime():0,int(_clockPaused)),false);
  debug("P510 ASVM28 malformed atomic: PASS (4540 truncations,4540 single-byte flips,%u checksummed invalid fields,paused live decoder unchanged)",invalid);
  debug("P510 ASVM28 physical slot27: PASS (saved inside actual Engine pause token)");
 }
 ++boundaries;debug("P510 ASVM28 byte roundtrip: PASS (boundary%u,4540bytes,paused source/recipient,607runner,14sprites)",boundaries);return true;
}
bool AstronomicaEngine::testP510FreshFile(){
 if(_place!=510||!_movie||_runner.executedCount()||!_runner.p510Capabilities(this,this,this,_scene)||_movie->isPaused()||!_movie->isPlaying())return false;
 const uint completed=_puzzlesCompleted;int32 before=0;if(!_runner.getValue(0,26,before))return false;uint32 now=scriptClock();
 const Sprite&button=_scene.sprites[13];const int x=button.renderX+10,y=button.renderY+10;if(spriteAt(x,y)!=13||!_runner.canRun(button.click,true))return false;clickAtTime(x,y,now);
 for(uint tick=0;tick<30;++tick){runScriptsAt(now);now+=10;}
 uint transitions=0;while(_place==510&&_plotEvent&&transitions<40){if(!_movie->seek(Audio::Timestamp(0,_plotTime+1,30)))return false;const int event=_plotEvent;updateMovie();runScriptsAt(now);now+=10;if(_plotEvent!=event||_place!=510)++transitions;}
 int32 solved=0;const bool ok=_place==136&&!_plotEvent&&_runner.getValue(0,26,solved)&&solved==1&&_puzzlesCompleted==completed+uint(!before)&&transitions>=9;
 debug("P510 ASVM28 fresh physical continuation: %s (slot27,%u original callbacks,P%d,solved%d,no startup replay)",ok?"PASS":"FAIL",transitions,_place,solved);return ok;
}

bool AstronomicaEngine::testP510LiveInstall(uint32 now){
 static_assert(!std::is_copy_constructible<P510Prepared>::value,"Prepared holder must not copy");static_assert(!std::is_move_constructible<P510Prepared>::value,"Prepared holder transfer is explicit");
 static uint accepted=0,excluded=0,cross=0;Common::Array<uint32>words;if(!captureP510Packet(words,now)){++excluded;return true;}
 auto check=[&](const char*label){if(_place!=510||!_movie||!_moviePlaying||!_movie->isPlaying()||_movie->isPaused()!=_clockPaused||_movie->getRate()!=Common::Rational(1,1)||!_runner.p510Capabilities(this,this,this,_scene)||!_hoverSprites.empty()||!_hoverRects.empty()||_nav[0]||_nav[1]||_nav[2]||_worldMovieCursorBottom!=-1||_dangerEvent[0]||_dangerEvent[1]||_dangerButtons||_mixer->isSoundHandleActive(_soundHandle))return false;
  Common::Array<uint32>state;if(!_runner.exportP510ActiveState(state,words[2]))return false;for(uint i=0;i<607;++i)if(state[i]!=words[kP510Runner+i])return false;for(uint i=0;i<14;++i){Common::Array<uint32>v;p526SpriteWords(_scene.sprites[i],v);for(uint j=0;j<27;++j)if(v[j]!=words[kP510Sprite+i*27+j])return false;}
  if(_movie->getCurFrame()!=int32(words[11])||_moviePresentedFrame!=int32(words[12])||_plotEvent!=int32(words[15])||_plotTime!=words[16]||_runner.executedCount()!=0)return false;
  for(uint id=10;id<=14;++id)if(!_runner.canRun(_scene.sprites[id-1].click,true))return false;
  hoverAtTime(0,0,scriptClock());debug("P510 install capability future: PASS (%s,5actual buttons ready,nav0,hoverempty,startup not replayed)",label);return true;};
 auto restore=[&](const char*label){const uint starts=_p510InstallStarts,commits=_p510InstallCommits,sounds=_soundsStarted;const int music=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType),effects=_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType);const bool musicMute=_mixer->isSoundTypeMuted(Audio::Mixer::kMusicSoundType),effectsMute=_mixer->isSoundTypeMuted(Audio::Mixer::kSFXSoundType);
  if(!installP510Packet(words)||_p510InstallStarts!=starts+1||_p510InstallCommits!=commits+1||_soundsStarted!=sounds||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=music||_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType)!=effects||_mixer->isSoundTypeMuted(Audio::Mixer::kMusicSoundType)!=musicMute||_mixer->isSoundTypeMuted(Audio::Mixer::kSFXSoundType)!=effectsMute||!check(label))return false;return true;};
 auto reject=[&](){const uint32 before=p510WholeLiveHash();const Audio::SoundHandle sound=_soundHandle;Common::Array<uint32>bad=words;bad[kP510Runner+303]=52;bad.back()=p510PacketHash(bad);if(installP510Packet(bad)||p510WholeLiveHash()!=before||!(_soundHandle==sound))return false;return true;};
 // Deliberate holder reuse is rejected before mutation; explicit transfer
 // leaves holder empty. The new decoder remains stopped until commit.
 {P510Prepared prepared;if(!prepareP510Packet(words,prepared)||!prepared.ready||prepared.decoder->isPlaying())return false;Video::QuickTimeDecoder*const pointer=prepared.decoder;const uint32 before=p510WholeLiveHash();if(prepareP510Packet(words,prepared)||prepared.decoder!=pointer||p510WholeLiveHash()!=before)return false;}
 if(!cross){
  for(uint destination:{519U,526U,117U}){if(!loadPlace(destination))return false;if((destination==519||destination==526)&&_hoverSprites.size()<=14)return false;if(destination==117&&!_nav[0]&&!_nav[1]&&!_nav[2])return false;const uint hover=_hoverSprites.size();if(!reject()||!restore("cross-scene"))return false;debug("P510 cross-scene install: PASS (P%u,oldhover%u,actual mouse future)",destination,hover);++cross;}
  if(loadGameState(98).getCode()!=Common::kNoError||!_ball.scenario||!_jupiterWidths[0])return false;if(!reject()||!restore("P501 retained state"))return false;debug("P510 cross-scene install: PASS (P501,nondefaultBall/Jupiter destination)");++cross;
  if(!loadPlace(516))return false;uint32 cacheNow=scriptClock();_runner.enqueueStartup(_scene.scripts,cacheNow,true);for(uint tick=0;tick<1000&&!_runner.scriptsIdle();++tick){runScriptsAt(cacheNow);cacheNow+=10;}if(!_runner.scriptsIdle()||!_jupiterWidths[0]||!reject()||!restore("P516 cache"))return false;debug("P510 cross-scene install: PASS (P516,native configured cache)");++cross;
  if(!loadPlace(523))return false;uint32 dangerNow=scriptClock();_runner.enqueueStartup(_scene.scripts,dangerNow,true);for(uint tick=0;tick<100;++tick){runScriptsAt(dangerNow);dangerNow+=10;}if(!_dangerEvent[0]&&!_dangerEvent[1])return false;const int channels[]={_dangerChannels[0],_dangerChannels[1],_dangerChannels[2]};const uint32 times[]={_dangerTime[0],_dangerTime[1]};if(!reject()||!restore("P523 pending events"))return false;for(uint i=0;i<3;++i)if(_dangerChannels[i]!=channels[i])return false;for(uint i=0;i<2;++i)if(_dangerTime[i]!=times[i])return false;debug("P510 cross-scene install: PASS (P523,pending cleared,inactive channels/times retained)");++cross;
  if(!loadPlace(117)||!playSound(922,scriptClock())||!_mixer->isSoundHandleActive(_soundHandle))return false;const uint32 before=p510WholeLiveHash();if(!reject()||p510WholeLiveHash()!=before||!_mixer->isSoundHandleActive(_soundHandle)||!restore("foreground destination"))return false;debug("P510 cross-scene install: PASS (foreground922 retained on rejection,stopped at commit)");++cross;
  // Actual nested Engine tokens model GMM plus its child dialog. Neither
  // installation nor an inner dialog release owns the outer pause.
  {PauseToken outer=pauseEngine();PauseToken inner=pauseEngine();
   if(!_clockPaused||!_movie->isPaused()||!reject()||!restore("nested GUI pause"))return false;
   const uint32 frozenClock=scriptClock(),frozenMedia=_movie->getTime();const int frozenFrame=_movie->getCurFrame();
   _system->delayMillis(40);if(scriptClock()!=frozenClock||_movie->getTime()!=frozenMedia||_movie->getCurFrame()!=frozenFrame)return false;
   Common::Array<uint32>pausedWords;if(!captureP510Packet(pausedWords,scriptClock()))return false;
   inner.clear();if(!_clockPaused||!_movie->isPaused()||scriptClock()!=frozenClock||_movie->getTime()!=frozenMedia)return false;
   outer.clear();if(_clockPaused||_movie->isPaused())return false;
   _system->delayMillis(40);if(scriptClock()-frozenClock<30||_movie->getTime()<frozenMedia)return false;
   debug("P510 nested Engine pause install: PASS (two real tokens,paused capture,frozen40ms,inner retains,outer resumes)");
  }
  if(!restore("unpaused after GUI pause"))return false;
 }
 if(!reject()||!restore("same scene"))return false;++accepted;
 debug("P510 live install: PASS (accepted%u,excluded%u,cross%u,starts%u,commits%u,owned transfer)",accepted,excluded,cross,_p510InstallStarts,_p510InstallCommits);return true;
}

bool AstronomicaEngine::verifyP510OrdinaryEntry(){
 ConfMan.setBool("astronomica_entry_scripts",true);_runner.resetGlobals();
 const uint before=_soundsStarted;if(!loadPlace(510)||!_movie)return false;
 debug("P510 ordinary loaded: loop%d enabled%d lastSound%d active%d starts%u queued%u",_loopSound,int(_loopEnabled),_lastSound,int(_mixer->isSoundHandleActive(_soundHandle)),_soundsStarted-before,_runner.pendingCount());
 if(_loopSound!=0||_lastSound!=300||_mixer->isSoundHandleActive(_soundHandle)||_soundsStarted!=before+1)return false;
 const uint32 start=_system->getMillis();bool ready=false;uint32 now=scriptClock();Common::Array<uint32>packet;
 while(_system->getMillis()-start<45000&&_place==510){now=scriptClock();runScriptsAt(now);animateSpritesAt(now);resumeLoopAt(now);updateMovie();
  if(captureP510Packet(packet,now)){ready=true;break;}_system->delayMillis(10);
 }
 if(!ready||packet[4]!=0||packet[5]||packet[7]||packet[kP510Runner+303]<1||packet[kP510Runner+303]>51||!canSaveGameStateCurrently())return false;
 debug("P510 ordinary ready: PASS (loop0 disabled,inactive,count%u,clock%u,media%u,one original startup)",packet[kP510Runner+303],now,_movie->getTime());
 if(!testP510FileSave(now)||_loopSound!=0||_loopEnabled||_mixer->isSoundHandleActive(_soundHandle))return false;
 debug("P510 ordinary paused ASVM28 save: PASS (literal loop0 preserved,4540bytes,physical slot27)");
 return testP510FreshFile();
}

bool AstronomicaEngine::verifyP510Puzzle() {
 // File and nested-pause diagnostics require the real script clock.
 // Restore the general-suite clock convention on every return path.
 struct VerifyClockScope {
  bool wasEnabled;
  VerifyClockScope() : wasEnabled(ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) {
   if (wasEnabled) ConfMan.setBool("astronomica_verify",false);
  }
  ~VerifyClockScope() { if (wasEnabled) ConfMan.setBool("astronomica_verify",true); }
 } verifyClockScope;
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==27)return testP510FreshFile();
 if(ConfMan.hasKey("astronomica_verify_p510_ordinary_entry")&&ConfMan.getBool("astronomica_verify_p510_ordinary_entry"))return verifyP510OrdinaryEntry();
 bool combinedOK=true;
 uint ordinarySnapshots=0,foregroundSnapshots=0;
 auto boundary=[&](uint32 now){if(_place!=510||!_movie)return;Common::Array<uint32>state,sprites,extra,ball;_runner.p510AuditExportState(state);for(const Sprite&sprite:_scene.sprites)p526SpriteWords(sprite,sprites);p516Extra(extra);for(int32 v:{_ball.scenario,_ball.centerX,_ball.centerY,_ball.side,_ball.period})ball.push_back(uint32(v));
  auto words=[&](const char*name,const Common::Array<uint32>&values){Common::String line;for(uint32 v:values)line+=Common::String::format("%u,",v);debug("P510WORDS %u %s %s",ordinarySnapshots,name,line.c_str());};
  bool foreground=_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound;foregroundSnapshots+=foreground;
  debug("P510BOUNDARY row=%u now=%u movie_ms=%u cur=%d presented=%d next_ms=%u end_ms=%u start=%u event=%d deadline=%u foreground=%u sound=%d loop=%d pending_image=%u frame_w=%u frame_h=%u rocket=%d probe_year=%d probe_flying=%u",ordinarySnapshots,now,_movie->getTime(),_movie->getCurFrame(),_moviePresentedFrame,_movie->getTimeToNextFrame(),uint32(_movie->getEndTime().msecs()),_movieSegmentStart,_plotEvent,_plotTime,uint(foreground),_lastSound,_loopSound,uint(_pendingImage.w||!_pendingImageName.empty()),_movieFrame.w,_movieFrame.h,int(_rocket.kind),_probe.year,uint(_probe.flying));
  {Common::Array<uint32>snapshot;const bool eligible=_runner.exportP510ActiveState(snapshot,now);if(eligible&&!_runner.testP510ActiveState(now))error("P510 runner preflight FAIL");if(!testP510FileSave(now)){combinedOK=false;debug("P510 ASVM28 byte test FAIL");}if(!testP510LiveInstall(now)){combinedOK=false;debug("P510 live install case rejected row%u",ordinarySnapshots);}if(!testP510Combined(now)){combinedOK=false;debug("P510 combined case rejected row%u",ordinarySnapshots);}debug("P510RUNNER row=%u eligible=%u result=PASS",ordinarySnapshots,uint(eligible));}
  _runner.p510AuditPending("ordinary",now);words("runner",state);words("sprites",sprites);words("extra",extra);words("ball",ball);++ordinarySnapshots;
 };

 auto observe=[&](const char*tag,uint32 now){
  _runner.p510AuditPending(tag,now);int32 choice=0;_runner.getValue(1,4,choice);
  uint32 pixels=2166136261U;for(int y=0;y<_movieFrame.h;++y)for(int x=0;x<_movieFrame.w*_movieFrame.format.bytesPerPixel;++x)pixels=(pixels^*((const byte*)_movieFrame.getBasePtr(0,y)+x))*16777619U;
  debug("P510ACTIVE %s now=%u movie_ms=%u cur=%d presented=%d next_ms=%u end_ms=%u start=%u event=%d deadline=%u playing=%u decoder_playing=%u paused=%u choice=%d pixels=%08x",tag,now,_movie?_movie->getTime():0,_movie?_movie->getCurFrame():-1,_moviePresentedFrame,_movie?_movie->getTimeToNextFrame():0,_movie?uint32(_movie->getEndTime().msecs()):0,_movieSegmentStart,_plotEvent,_plotTime,uint(_moviePlaying),uint(_movie&&_movie->isPlaying()),uint(_movie&&_movie->isPaused()),choice,pixels);
 };

 uint32 hash = 2166136261U;
 const int events[] = {20,21,22,23,24,25,26,27,28,29,30,31,32,40,41,42,43,44,46,47,48,49,50,51,52,53,54};
 for (int event : events) for (int choice = -1; choice <= 6; ++choice) for (int solved = 0; solved < 2; ++solved) {
  const PlotStep s = plotCallback(event,choice);
  const int fields[] = {s.x,s.y,s.start,s.duration,s.event,s.time,int(s.play),int(s.leave),int(s.success)};
  for (int field : fields) hash = (hash ^ uint32(field))*16777619U;
 }
 bool ok = hash == 0x33d6e7a1U;
 debug("Astronomica P510 original callback comparison: %s (432 cases, %08x)",ok ? "PASS" : "FAIL",hash);

 if(!loadPlace(510)||!_movie)return false;uint32 pollNow=scriptClock();_runner.enqueueStartup(_scene.scripts,pollNow,true);
 for(uint delta:{0U,500U,2749U,2750U,2751U,5499U,5500U,5501U}){runScriptsAt(pollNow+delta);observe("countdown",pollNow+delta);}
 const bool continuous = ConfMan.hasKey("astronomica_p510_continuous") && ConfMan.getBool("astronomica_p510_continuous");
 for (int route = 0; route < (continuous ? 1 : 8); ++route) {

  if(route==2){if(!loadPlace(516))return false;uint32 cacheNow=scriptClock();_runner.enqueueStartup(_scene.scripts,cacheNow,true);for(uint tick=0;tick<1000&&!_runner.scriptsIdle();++tick){runScriptsAt(cacheNow);cacheNow+=10;}if(!_runner.scriptsIdle()||!_jupiterWidths[0]){debug("P510 prior P516 cache FAIL");return false;}debug("P510 prior P516 cache PASS");}
  if(route==3){if(loadGameState(99).getCode()!=Common::kNoError)return false;_comet.frame=3;_comet.previousFrame=4;debug("P510 inherited variant fixture loaded");}
  if (!loadPlace(510) || !_movie) return false;
  bool good = _movie->getTimeScale() == 30 && _scene.sprites.size() == 14;
  _runner.defineValue(0,26,route == 3);
  const uint completed = _puzzlesCompleted;
  // Seed the original random operation to cover each of the three starts.
  uint16 seed = 0; const int mode = route%3+1;
  for (; seed < 1000; ++seed) {
   _runner.seedRandom(seed); if ((uint32(_runner.random15())*3)/32768+1 == uint32(mode)) break;
  }
  _runner.seedRandom(seed);
  uint32 now = scriptClock();
  const uint queued = _runner.enqueueStartup(_scene.scripts,now,true);
  auto wait = [&](uint duration) { const uint32 end = now+duration; while (now < end) { runScriptsAt(now); now += 10; } };
  good = queued == 4 && good; wait(500); observe("startup",now);boundary(now);
  int32 actualMode = 0; _runner.getValue(1,0,actualMode);
  debug("P510 startup: %u queued, mode %d, event %d, playing %d",queued,actualMode,_plotEvent,int(_moviePlaying));
  good = actualMode == mode && _plotEvent == 19+mode && _moviePlaying && _movieX == 261 && _movieY == 33 && good;
  good = _scene.sprites[1].renderX == plotStart(mode).x && _scene.sprites[1].renderY == plotStart(mode).y && good;
  uint transitions = 0, frames = 0;
  auto press = [&](int id) {
   const Sprite &button = _scene.sprites[id-1]; const int x = button.renderX+10, y = button.renderY+10;
   if (_runner.clicksBlocked() || spriteAt(x,y) != id-1 || !_runner.canRun(button.click,true)) return false;
   observe("before-button",now);clickAtTime(x,y,now); wait(300); observe("after-button",now);boundary(now);return true;
  };
  // Routes0..3 win (both branch directions and repeated victory),4..5
  // fail with the middle button,6 exits,7 expires the original countdown.
  const int choice = route == 4 || route == 5 ? 3 : route == 1 ? 1 : 5;

  if(route<3){for(int pick=1;pick<=5;++pick){good=press(9+pick)&&good;debug("P510CHOICE mode=%d pick=%d",mode,pick);}
   good=press(7)&&good;debug("P510HINT pending mode=%d",mode);observe("hint-pending",now);boundary(now);wait(10010);debug("P510HINT drained mode=%d",mode);observe("hint-drained",now);boundary(now);}
  good = press(9+choice) && good;
  if (route == 6) { good = press(4) && good; wait(1000); }
  if (route == 7) {
   for (int i = 0; i < 450 && _place == 510; ++i) { now += 3000; runScriptsAt(now); }
  }
  uint32 lastSnapshot=0;const uint32 started = _system->getMillis();
  while (route < 6 && _place == 510 && _plotEvent && transitions < 40 && _system->getMillis()-started < 180000) {
   const int event = _plotEvent;
   if (continuous) {
    const uint before = _movieFramesDrawn;
    updateMovie(); if (_movie && _movieFramesDrawn > before) frames += _movieFramesDrawn-before;
    now = scriptClock(); runScriptsAt(now); animateSpritesAt(now); if(_system->getMillis()-lastSnapshot>=1000){observe("ordinary",now);boundary(now);lastSnapshot=_system->getMillis();}_system->delayMillis(5);
   } else {
    // Accelerated route checks use the real decoder; continuous playback
    // is independently checked without seeks by the dedicated option.
    observe("before-seek",now);good = _movie->seek(Audio::Timestamp(0,_plotTime+1,30)) && good;observe("after-seek-before-update",now);
    updateMovie();observe("after-update",now);boundary(now);
   }
   if (_plotEvent != event || _place != 510) ++transitions;
  }
  int32 solved = 0; _runner.getValue(0,26,solved);
  const bool victory = route < 4;
  good = _place == 136 && !_plotEvent && solved == int(victory) &&
   _puzzlesCompleted == completed + (victory && route != 3 ? 1 : 0) && good;
  if (continuous) good = transitions >= 9 && frames > 100 && _system->getMillis()-started > 60000 && good;
  debug("Astronomica P510 route %d: %s (mode %d, %u transitions, P%d, %d solved, %u frames)",route,good ? "PASS" : "FAIL",mode,transitions,_place,solved,frames);
  ok = good && ok;
 }
 debug("P510 continuous boundary audit: %s (%u ordinary snapshots, %u foreground snapshots)",ok&&ordinarySnapshots>30?"PASS":"FAIL",ordinarySnapshots,foregroundSnapshots);ok=ok&&ordinarySnapshots>30;ok=ok&&combinedOK;debug("Astronomica P510 interaction verification: %s",ok ? "PASS" : "FAIL");
 return ok;
}

bool AstronomicaEngine::verifyP527Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,histories=0,dormant=0,ordinary=0,busy=0,successors=0,futures=0,absences=0,mismatches=0;uint masks=0,selectors=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto hashSurface=[&](const Graphics::Surface&s){return screenRGBHash(s,480);};
 auto fingerprint=[&](bool departure=false){uint32 h=departure?2166136261U:_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};if(departure){Common::Array<uint32>state;if(!_runner.exportPersistentState(state))return uint32(0);for(uint i=0;i<state.size();++i)if(i!=601)add(state[i]);}for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame),uint32(_moviePresentedFrame),_movieSegmentStart,_universeSegmentEnd})add(v);Common::Array<uint32>w;p516Extra(w);for(uint32 v:w)add(v);for(const Sprite&s:_scene.sprites){w.clear();p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}add(hashSurface(_screen));add(hashSurface(_background));add(hashSurface(_movieFrame));return h;};
 auto snapshot=[&](Common::Array<byte>&d){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=3940)return false;d.resize(out.size());memcpy(&d[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&d){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&d[0],d.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&d[16]))return false;now=scriptClock();sync();return true;};
 auto quiet=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP527())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;};
 bool noFrame=false;
 auto settle=[&](){for(uint pass=0;pass<10000&&_place==527&&(!_runner.scriptsIdle()||_moviePlaying);++pass){if(canSaveP527())return false;++busy;sync();runScriptsAt(now);animateSpritesAt(now);if(_moviePlaying){if(!noFrame){const uint before=_movieFramesDrawn;updateMovie();if(_movieFramesDrawn<=before||!_movieFrame.w)return false;}if(!_movie->seek(_movie->getEndTime()))return false;updateMovie();if(_moviePlaying)return false;}now+=20;}sync();return _place!=527||_runner.scriptsIdle();};
 auto press=[&](uint id){if(_place!=527||id<1||id>9||_runner.clicksBlocked())return false;const Sprite&s=_scene.sprites[id-1];const int x=s.renderX+14,y=s.renderY+13;if(spriteAt(x,y)!=int(id-1))return false;clickAtTime(x,y,now);return settle()&&quiet();};
 auto roundtrip=[&](){if(!quiet())return false;Common::Array<byte>d,again;if(!snapshot(d)){debug("P527 snapshot rejected boundary%u clock%u",boundaries,now);return false;}const uint32 before=fingerprint(),saved=now;now+=1000;sync();runScriptsAt(now);animateSpritesAt(now);const uint32 after=fingerprint(),ended=now;if(!loadPlace(117)||!restore(d)||fingerprint()!=before||!snapshot(again)||again!=d)return false;now+=1000;sync();runScriptsAt(now);animateSpritesAt(now);if(now!=ended||fingerprint()!=after)return false;++successors;Common::Array<uint32>s;_runner.exportPersistentState(s);++boundaries;histories+=_moviePresentedFrame>=0;absences+=_moviePresentedFrame<0;dormant+=s[603]!=0;ordinary+=!s[603];masks|=1U<<s[315];selectors|=1U<<s[309];const int bit=s[309]?1U<<(s[309]-1):0;mismatches+=_moviePresentedFrame>=0&&p527FrameBit(_moviePresentedFrame)!=bit;return true;};
 auto startup=[&](){sync();if(!loadPlace(527)||_runner.enqueueStartup(_scene.scripts,now,true)!=1||!settle())return false;return quiet();};
 auto exitOutcome=[&](bool solved){int32 before=0;_runner.getValue(0,43,before);const uint completed=_puzzlesCompleted;if(!press(6)){debug("P527 exit press failed P%d",_place);return false;}int32 actual=0;const bool ok=_place==174&&_runner.getValue(0,43,actual)&&actual==int(solved)&&_puzzlesCompleted==completed+uint(solved&&!before);if(!ok)debug("P527 exit outcome failed P%d solved%d/%d count%u/%u",_place,actual,solved,_puzzlesCompleted,completed+uint(solved&&!before));return ok;};
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==22){now=scriptClock();sync();debug("Astronomica P527 slot fingerprint: %08x",fingerprint());Common::Array<byte>d;const bool ok=canSaveP527()&&snapshot(d)&&roundtrip()&&restore(d)&&exitOutcome(true);debug("Astronomica P527 startup save: %s (slot22, retained movie and sticky early completion)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();sync();if(!startup()||!roundtrip())return false;
 // Decode the complete original sample stream, then compare every random seek.
 auto compareMovie=[&](){Video::QuickTimeDecoder sequential,reconstructed;const Common::Path path=ConfMan.getPath("path").join("PLACES/P527/FLATRING.MOV");Common::File*a=new Common::File();Common::File*b=new Common::File();if(!a->open(Common::FSNode(path))||!b->open(Common::FSNode(path))){delete a;delete b;return false;}if(!sequential.loadStream(a)){delete b;return false;}if(!reconstructed.loadStream(b))return false;
  if(sequential.getFrameCount()!=1105||reconstructed.getFrameCount()!=1105||sequential.getWidth()!=320||sequential.getHeight()!=240||reconstructed.getWidth()!=320||reconstructed.getHeight()!=240)return false;
  for(uint i=0;i<1105;++i){const Graphics::Surface*x=sequential.decodeNextFrame();if(!x||sequential.getCurFrame()!=int(i)||!reconstructed.seekToFrame(i))return false;const Graphics::Surface*y=reconstructed.decodeNextFrame();if(!y||reconstructed.getCurFrame()!=int(i))return false;Graphics::Surface*rgbX=x->convertTo(_screen.format,sequential.getPalette());Graphics::Surface*rgbY=y->convertTo(_screen.format,reconstructed.getPalette());bool same=rgbX&&rgbY&&rgbX->w==320&&rgbX->h==240&&rgbY->w==320&&rgbY->h==240&&rgbX->format==rgbY->format;
   if(same)for(int row=0;row<240;++row)if(memcmp(rgbX->getBasePtr(0,row),rgbY->getBasePtr(0,row),320*rgbX->format.bytesPerPixel)){same=false;break;}if(rgbX){rgbX->free();delete rgbX;}if(rgbY){rgbY->free();delete rgbY;}if(!same){debug("P527 seek mismatch sample%u",i);return false;}}
  return true;};if(!compareMovie())return false;
 debug("Astronomica P527 original movie audit: PASS (1105 sequential and seek pixel comparisons)");
 for(uint mask=0;mask<15;++mask){now=0;_runner.resetGlobals();if(!startup()||!roundtrip())return false;for(uint choice=1;choice<=4;++choice)if(mask&(1U<<(choice-1))){if(!press(choice)||!press(9)||_place!=527||!roundtrip())return false;}for(uint choice=1;choice<=4;++choice)if(!press(choice)||!roundtrip())return false;}
 // A new range may end before its first sample is presented: preserve absence.
 now=0;_runner.resetGlobals();if(!startup()||!press(1))return false;noFrame=true;if(!press(9)||_moviePresentedFrame!=-1||!roundtrip())return false;noFrame=false;
 // Retain a previous segment even when a later range produces no sample.
 if(!press(3)||!press(9)||!press(4))return false;const int residual=_moviePresentedFrame;const uint32 picture=hashSurface(_movieFrame);noFrame=true;if(!press(9)||_moviePresentedFrame!=residual||hashSurface(_movieFrame)!=picture||!roundtrip())return false;noFrame=false;
 // Restore dormant family state and a deliberately unknown local value verbatim.
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();if(!startup()||!press(2)||!press(9)||!press(4)||!roundtrip())return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&d){uint32 h=2166136261U;for(uint j=8;j<d.size()-4;j+=4)h=(h^READ_LE_UINT32(&d[j]))*16777619U;WRITE_LE_UINT32(&d[d.size()-4],h);};
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(16+243+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP527())return false;const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP527()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}if(_mixer->isSoundHandleActive(_soundHandle)||_system->getMillis()==voiceStart||!roundtrip())return false;debug("Astronomica P527 natural voice end: PASS (no stopHandle)");
 now=0;sync();ConfMan.setBool("astronomica_entry_scripts",true);const bool entered=loadPlace(527);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||!quiet()||_loopSound!=0)return false;now=5001;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP527())return false;
 const int musicBefore=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,musicBefore);debug("Astronomica P527 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // Atomic rejection includes live foreground audio, movie decoder and surfaces.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP527())return false;_mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageName="P527-atomic";_pendingImageX=19;_pendingImageY=23;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie->getCurFrame()),_movie->getTime(),uint32(_moviePlaying),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);add(hashSurface(_pendingImage));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels(),*decoder=_movie;auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels&&_movie==decoder;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels||_movie!=decoder)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P527 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint i:{0U,3U,4U,5U,7U,8U,9U,10U,11U,12U,13U,14U,15U})if(!badWord(i,0xfffffffeU))return false;
 for(uint i=0;i<9;++i)if(!badWord(16+i*27+1,2)||!badWord(16+i*27+4,65538)||!badWord(16+i*27+18,2))return false;
 for(uint i:{2U,300U,303U,306U,309U,312U,315U,318U,321U,301U,302U,602U,603U,604U})if(!badWord(16+243+i,0xffffffffU))return false;
 for(uint i:{0U,50U,100U,101U,102U,110U})if(!badWord(16+243+605+i,123456))return false;
 _pendingImage.free();_pendingImageName.clear();_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP527())return false;debug("Astronomica P527 rejection verification: PASS (3940 truncations, 3940 corruptions, %u invalid states, extended atomic state)",invalid);
 // First and repeated early completion follow actual original controls.
 for(uint repeat=0;repeat<2;++repeat){if(!restore(fixture)||!roundtrip()||!restore(fixture)){debug("P527 early future setup failed repeat%u",repeat);return false;}Common::Array<byte>branch;if(!snapshot(branch)||!exitOutcome(true))return false;const uint32 expected=fingerprint(true),ended=now,successEnd=_lastSuccessEnd;Common::Array<uint32>expectedState;_runner.exportPersistentState(expectedState);if(!restore(branch)||!exitOutcome(true))return false;const bool clockOK=repeat?now==ended:(now-_lastSuccessEnd>=520&&now-_lastSuccessEnd<540&&ended-successEnd>=520&&ended-successEnd<540);if(!clockOK||fingerprint(true)!=expected){debug("P527 early future mismatch repeat%u clock%u/%u successEnd%u/%u hash%08x/%08x",repeat,ended,now,successEnd,_lastSuccessEnd,expected,fingerprint(true));Common::Array<uint32>actualState;_runner.exportPersistentState(actualState);for(uint i=0;i<MIN(expectedState.size(),actualState.size());++i)if(expectedState[i]!=actualState[i])debug("P527 future runner%u: %u/%u",i,expectedState[i],actualState[i]);return false;}debug("Astronomica P527 early future repeat%u: PASS (clock%u, successEnd%u, departure loadedAt normalized)",repeat,now,_lastSuccessEnd);++futures;++successors;if(!repeat){now=0;sync();if(!startup()||!press(2)||!press(9)||!quiet()||!snapshot(fixture))return false;}}
 // Unsolved exit and natural full-mask completion are separate native routes.
 now=0;_runner.resetGlobals();if(!startup()||!press(1)||!press(9)||!roundtrip()||!exitOutcome(false))return false;++futures;
 for(uint repeat=0;repeat<2;++repeat){now=0;if(!repeat)_runner.resetGlobals();if(!startup())return false;const uint completed=_puzzlesCompleted;for(uint choice:{1U,3U,4U,2U})if(!press(choice)||!press(9))return false;int32 solved=0;if(_place!=174||!_runner.getValue(0,43,solved)||solved!=1||_puzzlesCompleted!=completed+uint(!repeat))return false;++futures;}
 // Save a fresh-process continuation with retained group2 and selector4.
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_comet.frame=3;_comet.previousFrame=4;now=0;if(!startup()||!press(2)||!press(9)||!press(4)||!quiet()||saveGameState(22,"P527 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P527 slot fingerprint: %08x",fingerprint());if(!exitOutcome(true))return false;
 if(masks!=32767||selectors!=31||!histories||!dormant||!ordinary||!absences||!mismatches)return false;
 debug("Astronomica P527 history coverage: PASS (%u absent boundaries, %u selector-image mismatches, %u successor checks, %u future outcome checks, 15 masks, 5 selector states)",absences,mismatches,successors,futures);
 debug("Astronomica P527 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP516Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,busy=0,histories=0,dormant=0,ordinary=0,motion=0,handoffs=0,animations=0,successors=0,futures=0,timerCases=0,controlMask=0,directionMask=0,speedMask=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto advance=[&](uint duration){for(uint n=0;n<duration&&_place==516;n+=10)tick();};
 auto settle=[&](){for(uint n=0;n<5000&&_place==516&&!_runner.scriptsIdle();++n){if(canSaveP516())return false;++busy;tick();}return _place==516&&_runner.scriptsIdle();};
 auto fingerprint=[&](){uint32 h=_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);Common::Array<uint32>extra;p516Extra(extra);for(uint32 v:extra)add(v);for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=6944)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&data[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP516())return false;_mixer->stopHandle(_soundHandle);}Common::Array<byte>data,again;if(!snapshot(data)){debug("P516 snapshot rejected boundary%u clock%u",boundaries,now);return false;}const uint32 before=fingerprint(),saved=now;advance(2000);const uint32 after=fingerprint(),ended=now;if(!loadPlace(117)||!restore(data)||now!=saved||fingerprint()!=before||!snapshot(again)||again!=data){debug("P516 restore mismatch boundary%u",boundaries);return false;}advance(2000);if(now!=ended||fingerprint()!=after){debug("P516 successor mismatch boundary%u",boundaries);return false;}Common::Array<uint32>state;_runner.exportPersistentState(state);++boundaries;++successors;const bool retained=_scene.sprites[12].standardMotion;histories+=retained||state[303]!=0;motion+=retained;bool front=false;for(uint i=13;i<=16;++i)front|=_scene.sprites[i].visible!=0;handoffs+=front;animations+=_scene.sprites[16].autoFrame&&_scene.sprites[17].autoFrame;dormant+=state[603]!=0;ordinary+=!state[603];directionMask|=1U<<(state[300]-1);speedMask|=1U<<state[303];return true;};
 auto press=[&](uint id){if(_place!=516||id<1||id>37||_runner.clicksBlocked())return false;const Sprite&s=_scene.sprites[id-1];const int x=s.renderX+10,y=s.renderY+10;if(spriteAt(x,y)!=int(id-1))return false;clickAtTime(x,y,now);if(!settle())return false;if(id>=5&&id<=11&&id!=7)controlMask|=1U<<id;return true;};

 auto quietVoice=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP516())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;};
 auto startup=[&](){sync();return loadPlace(516)&&_runner.enqueueStartup(_scene.scripts,now,true)==2&&settle();};
 auto step=[&](uint duration){sync();runScriptsAt(now);animateSpritesAt(now);now+=duration;sync();};
 auto future=[&](){int32 beforeSolved=0;_runner.getValue(0,32,beforeSolved);const uint completed=_puzzlesCompleted;if(spriteAt(464,408)!=11)return false;clickAtTime(464,408,now);
  for(uint pass=0;pass<2000&&_place==516;++pass){if(canSaveP516())return false;++busy;int32 flag=0;_runner.getValue(1,2,flag);step(flag?1000:10);}
  int32 solved=0;return _place==388&&_runner.getValue(0,32,solved)&&solved==1&&_puzzlesCompleted==completed+uint(!beforeSolved);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==21){now=scriptClock();sync();debug("Astronomica P516 slot fingerprint: %08x",fingerprint());Common::Array<byte>incoming;const bool ok=canSaveP516()&&snapshot(incoming)&&roundtrip()&&restore(incoming)&&future();debug("Astronomica P516 startup save: %s (slot21, stopped projectile and original paired orbits)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();sync();if(!startup()||!roundtrip())return false;
 for(uint pass=0;pass<2000;++pass){if(!canSaveP516())return false;tick();}debug("Astronomica P516 orbit-cycle guard: PASS (2000 native ticks, all eight configured orbits)");
 for(uint id=8;id<=11;++id)if(!press(id)||!roundtrip())return false;
 for(uint n=0;n<15;++n)if(!press(6)||!roundtrip())return false;
 if(!press(6)||!roundtrip())return false;for(uint n=0;n<15;++n)if(!press(5)||!roundtrip())return false;if(!press(5)||!roundtrip())return false;
 // Fresh original UI phase delayed1000ms gives a wrong-target stopped return.
 now=0;sync();if(!startup()||!press(9)||!press(6))return false;advance(1000);if(!press(12)||!_scene.sprites[12].standardMotion||_scene.sprites[12].visible||_scene.sprites[12].autoMove||!roundtrip())return false;

 if(!press(5)||!roundtrip()||!press(12)||!roundtrip())return false;
 // Genuine old-rectangle boundary miss, direction1/speed1, not speed0 NOOP.
 now=0;sync();if(!startup()||!press(8)||!press(6)||!press(12))return false;advance(7000);if(_scene.sprites[12].visible||_scene.sprites[12].autoMove||!roundtrip())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();if(!startup()||!roundtrip())return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&data){uint32 hash=2166136261U;for(uint j=8;j<data.size()-4;j+=4)hash=(hash^READ_LE_UINT32(&data[j]))*16777619U;WRITE_LE_UINT32(&data[data.size()-4],hash);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint kind:{13U,20U,16U,17U}){const uint period=kind==13||kind==20?10:80;for(uint age:{0U,1U,period-1,period,period+1}){
  Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);for(uint i=13;i<=20;++i){const uint at=8+(11+i*27+9)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}for(uint i:{13U,16U,17U,20U}){const uint at=8+(11+i*27+8)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}const uint at=8+(11+999+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);WRITE_LE_UINT32(&timed[8+(11+kind*27+(period==10?9:8))*4],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;
 }}
 if(!restore(fixture))return false;debug("Astronomica P516 timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+999+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP516())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP516()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSaveP516()||!roundtrip())return false;debug("Astronomica P516 natural voice end: PASS (%u ms, no stopHandle)",waited);
 // Obtain the ambient binding through the actual original scene entry.
 now=0;ConfMan.setBool("astronomica_entry_scripts",true);sync();const bool entered=loadPlace(516);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||_loopSound!=0||!_loopEnabled)return false;
 if(_mixer->isSoundHandleActive(_soundHandle)){if(canSaveP516())return false;++busy;_mixer->stopHandle(_soundHandle);}
 const uint32 ambientEpoch=_lastSoundAt;now=ambientEpoch+4999;sync();resumeLoopAt(now);if(_mixer->isSoundHandleActive(_soundHandle))return false;
 ++now;sync();resumeLoopAt(now);if(_mixer->isSoundHandleActive(_soundHandle))return false;
 ++now;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP516())return false;
 debug("Astronomica P516 ambient deadline: PASS (3 cases, original entry)");
 const int musicBefore=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);
 Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;
 _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,musicBefore);debug("Astronomica P516 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP516())return false;Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="P516-atomic-image";_displayedImageName="P516-atomic-display";
 _movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_movieFrame.w),uint32(_movieFrame.h),uint32(_p516AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P516 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(index,index==3?538U:index==4?1U:0xffffffffU))return false;
 for(uint i=0;i<37;++i)if(!badWord(11+i*27+18,2))return false;
 for(uint i:{2U,301U,302U,300U,303U,306U,307U,308U,602U,603U,604U})if(!badWord(11+999+i,0xffffffffU))return false;
 for(uint i=13;i<=20;++i)if(!badWord(11+i*27+9,now+1)||!badWord(11+i*27+4,65538)||!badWord(11+i*27+11,65538)||!badWord(11+i*27+22,11))return false;
 for(uint i:{13U,16U,17U,20U})if(!badWord(11+i*27+8,now+1)||!badWord(11+i*27+1,4))return false;
 for(uint i:{13U,63U,100U,101U,102U,110U})if(!badWord(11+999+605+i,123456))return false;
 if(!badWord(11+999+601,now+1)||!badWord(11+12*27+7,1)||!badWord(11+12*27+11,1)||!badWord(11+12*27+12,1)||!badWord(11+22*27,1)||!badWord(11+22*27+1,9)||!badWord(11+13*27+14,2)||!badWord(11+13*27,2))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP516())return false;debug("Astronomica P516 rejection verification: PASS (6944 truncations, 6944 corruptions, %u invalid states, extended atomic state)",invalid);


 // Known successful launch phase comes from real original UI, not local setters.
 now=0;sync();if(!startup()||!press(9)||!press(6)||!quietVoice())return false;Common::Array<byte>successFixture;if(!snapshot(successFixture)){debug("P516 success fixture save rejected clock%u",now);return false;}
 for(uint mode=0;mode<2;++mode){if(!restore(successFixture)||!roundtrip()||!restore(successFixture))return false;Common::Array<byte>branch;if(!snapshot(branch)||!future())return false;const uint32 expected=fingerprint(),expectedClock=now;
  if(!restore(branch)||!future()||now!=expectedClock||fingerprint()!=expected){debug("P516 future mismatch mode%u clock%u/%u hash%08x/%08x",mode,expectedClock,now,expected,fingerprint());return false;}++futures;++successors;
  // The actual first outcome creates global32=1; reenter original controls for repeat.
  if(mode==0){now=0;sync();if(!startup()||!press(9)||!press(6)||!quietVoice()||!snapshot(successFixture))return false;}
 }
 // Fresh-process fixture is an unsolved original launch phase, preserving dormant state.
 _runner.resetGlobals();now=0;sync();if(!startup()||!press(9)||!press(6)||!quietVoice()||saveGameState(21,"P516 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P516 slot fingerprint: %08x",fingerprint());if(!future())return false;
 uint choices=0,directions=0,speeds=0;for(uint i=0;i<32;++i)choices+=(controlMask>>i)&1U;for(uint i=0;i<4;++i)directions+=(directionMask>>i)&1U;for(uint i=0;i<16;++i)speeds+=(speedMask>>i)&1U;if(choices!=6||directions!=4||speeds!=16||!motion||!handoffs)return false;
 debug("Astronomica P516 controls coverage: PASS (%u direction settings, %u speed settings)",directions,speeds);
 debug("Astronomica P516 history coverage: PASS (%u choice controls, %u retained-motion boundaries, %u handoff boundaries, %u animation boundaries, %u successor checks, %u future outcome checks)",choices,motion,handoffs,animations,successors,futures);
 debug("Astronomica P516 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP516Puzzle() {
 bool ok = verifyJupiterMotion();
 debug("Astronomica P516 original motion comparison: %s (eight sprites, 20 seconds)",ok ? "PASS" : "FAIL");
 const bool setupOK = verifyJupiterSetup();
 debug("Astronomica P516 original setup comparison: %s (128 configurations)",setupOK ? "PASS" : "FAIL");
 ok = setupOK && ok;
 const bool collisionOK = verifyJupiterCollision();
 debug("Astronomica P516 collision verification: %s (64 original fixtures and four USER rectangle boundaries)",collisionOK ? "PASS" : "FAIL");
 ok = collisionOK && ok;
 const uint32 rgb888[] = {0x0781fc19U,0xeb2035e0U,0x21ca9a99U};
 const uint32 rgb565[] = {0x23191a12U,0x98c6efd5U,0xac7b70bcU};
 bool graphicsOK = true;
 for (int variant = 0; variant < 3; ++variant) {
  if (!loadPlace(516)) return false;
  if (variant) for (int id = 14; id <= 21; ++id) {
   Sprite &s = _scene.sprites[id-1]; s.visible = 1; s.renderX = 300; s.renderY = variant == 1 ? 150 : 310;
  }
  redrawSprites();
  const uint32 actual = screenRGBHash(_screen), expected = _screen.format.bytesPerPixel == 2 ? rgb565[variant] : rgb888[variant];
  if (actual != expected) debug("P516 composition %d: %08x expected %08x",variant,actual,expected);
  graphicsOK = actual == expected && graphicsOK;
 }
 if (!loadPlace(516)) return false;
 onComet(0,0); animateSpritesAt(79);
 const int animated[] = {14,17,18,21};
 for (int id : animated) graphicsOK = _scene.sprites[id-1].selectedFrame == 0 && _scene.sprites[id-1].frameSince == 0 && graphicsOK;
 animateSpritesAt(80);
 for (int id : animated) graphicsOK = _scene.sprites[id-1].selectedFrame == (id == 17 || id == 18 ? 1 : 0) && _scene.sprites[id-1].frameSince == 80 && graphicsOK;
 debug("Astronomica P516 graphics verification: %s (three original compositions and 80ms animation on both layers)",graphicsOK ? "PASS" : "FAIL");
 ok = graphicsOK && ok;
 _runner.resetGlobals(); int winningDirection = 0, winningSpeed = 0;
 for (int route = 0; route < 4; ++route) {
  bool passed = false;
  for (int trial = 0; trial < 1 && !passed; ++trial) {
   const int direction = route == 3 ? 1 : route == 0 ? 2 : winningDirection;
   const int speed = route == 0 || route == 3 ? 1 : route == 1 ? winningSpeed : 0;
   if (!loadPlace(516)) return false;
   uint32 now = 0; const uint completed = _puzzlesCompleted;
   _runner.defineValue(0,32,route == 1);
   auto step = [&]() { runScriptsAt(now); animateSpritesAt(now); now += 10; };
   auto wait = [&](uint duration) { const uint32 end = now+duration; while (now < end) step(); };
   auto press = [&](int id) {
    const Sprite &s = _scene.sprites[id-1]; const int x = s.renderX+10, y = s.renderY+10;
    if (_runner.clicksBlocked() || spriteAt(x,y) != id-1 || !_runner.canRun(s.click,true)) {
     debug("P516 button %d blocked %d hit %d ready %d",id,int(_runner.clicksBlocked()),spriteAt(x,y),int(_runner.canRun(s.click,true))); return false;
    }
    clickAtTime(x,y,now); step(); wait(300); return true;
   };
   const uint queued = _runner.enqueueStartup(_scene.scripts,0,true);
   bool good = queued == 2; if (!good) debug("P516 startup queued %u",queued); step();
   good = press(7+direction) && good;
   for (int n = 0; n < speed; ++n) good = press(6) && good;
   good = press(12) && good; wait(14000);
   int32 solved = 0; _runner.getValue(0,32,solved);
   if (route >= 2) { good = _place == 516 && !solved && !_runner.clicksBlocked() && !_scene.sprites[12].visible && !_scene.sprites[22].visible && _lastSound == 10 && good; good = press(2) && good; wait(1000); passed = good && _place == 388; }
   else passed = good && _place == 388 && solved == 1 && _puzzlesCompleted == completed+uint(route == 0);
   if (passed && route == 0) { winningDirection = direction; winningSpeed = speed; }
   if (!good) { debug("Astronomica P516 input failure: route %d trial %d",route,trial); break; }
  }
  debug("Astronomica P516 route %d: %s (direction %d, speed %d)",route,passed ? "PASS" : "FAIL",winningDirection,winningSpeed);
  ok = passed && ok;
  if (!winningDirection) break;
 }
 debug("Astronomica P516 interaction verification: %s",ok ? "PASS" : "FAIL"); return ok;
}
bool AstronomicaEngine::verifyP502Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,prelaunch=0,low=0,high=0,changed=0,explosions=0,caches=0,histories=0,dormant=0,ordinary=0,busy=0,successors=0,futures=0;uint dirs=0,speeds=0,failedCombinations=0,timerCases=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto advance=[&](uint duration){for(uint i=0;i<duration;i+=10)tick();};
 auto value=[&](int id){int32 v=-1;_runner.getValue(1,id,v);return v;};
 auto fingerprint=[&](bool departure=false){uint32 h=departure?2166136261U:_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};if(departure){Common::Array<uint32>s;if(!_runner.exportPersistentState(s))return uint32(0);for(uint i=0;i<s.size();++i)if(i!=601)add(s[i]);}for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);Common::Array<uint32>w;p516Extra(w);for(uint32 v:w)add(v);for(const Sprite&s:_scene.sprites){w.clear();p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto quiet=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP502())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;};
 auto settle=[&](){for(uint i=0;i<6000&&!_runner.scriptsIdle();++i){if(_place==502&&canSaveP502())return false;++busy;tick();}return _runner.scriptsIdle();};
 auto press=[&](uint id){if(id<1||id>_scene.sprites.size()||_runner.clicksBlocked())return false;const int origin=_place;const Sprite&s=_scene.sprites[id-1];if(spriteAt(s.renderX+15,s.renderY+10)!=int(id-1)||!_runner.canRun(s.click,true))return false;clickAtTime(s.renderX+15,s.renderY+10,now);if(origin==502)return settle()&&quiet();advance(300);return true;};
 auto speed=[&](int target){for(uint i=0;i<16&&value(1)!=target;++i){const int down=_place==502?6:_place==503?10:9;if(!press(down+uint(value(1)<target)))return false;}return value(1)==target;};
 auto entry=[&](){now=0;sync();return loadPlace(502)&&_runner.enqueueStartup(_scene.scripts,now,true)==2&&settle()&&quiet();};
 auto snapshot=[&](Common::Array<byte>&d){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=6728)return false;d.resize(out.size());memcpy(&d[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&d){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&d[0],d.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&d[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(!quiet())return false;Common::Array<byte>d,again;if(!snapshot(d)){debug("P502 snapshot rejected boundary%u clock%u kind%d sound%d explosion%d",boundaries,now,_comet.kind[19],_comet.sound,_comet.explosion);return false;}const uint32 before=fingerprint(),clock=now;advance(1000);const uint32 expected=fingerprint(),ended=now;if(!loadPlace(117)||!restore(d)||now!=clock||fingerprint()!=before||!snapshot(again)||again!=d){debug("P502 restore mismatch boundary%u",boundaries);return false;}advance(1000);if(now!=ended||fingerprint()!=expected)return false;Common::Array<uint32>s;_runner.exportPersistentState(s);++boundaries;++successors;prelaunch+=!_comet.kind[19];low+=_comet.kind[19]==2;high+=_comet.kind[19]==3;histories+=_comet.kind[19]!=0;explosions+=_scene.sprites[20].selectedFrame==9;caches+=_jupiterWidths[0]!=0;dormant+=s[603]!=0;ordinary+=!s[603];dirs|=1U<<(s[300]-1);speeds|=1U<<s[303];return true;};
 auto failure=[&](){if(!press(9)||_place!=502)return false;for(uint i=0;i<4000&&(_scene.sprites[19].autoMove||!_runner.scriptsIdle());++i){if(canSaveP502())return false;++busy;tick();}return _place==502&&!_scene.sprites[19].visible&&!_scene.sprites[19].autoMove&&_runner.scriptsIdle()&&quiet();};
 auto fullFuture=[&](){int32 before=0;_runner.getValue(0,21,before);const uint completed=_puzzlesCompleted;if(!press(16)||!speed(13)||_place!=502)return false;const Sprite&launch=_scene.sprites[8];if(spriteAt(launch.renderX+15,launch.renderY+10)!=8)return false;clickAtTime(launch.renderX+15,launch.renderY+10,now);bool armed=false;
  for(uint i=0;i<4000&&_place==502;++i){if(canSaveP502())return false;++busy;if(value(3)==1&&_runner.clicksBlocked())armed=true;tick();}if(_place!=503||!armed)return false;
  for(int place=503;place<=504;++place){if(_place!=place||_runner.enqueueStartup(_scene.scripts,now,true)!=_scene.scripts.size())return false;advance(400);if(_place!=place||_runner.clicksBlocked())return false;const int first=place==503?5:1,last=place==503?9:4;for(int target=first;target<=last;++target){if(!press(5+target-first)||!press((place==503?20:19)+(target==9?1:target<=4?target:target-4)-1)||!speed(11-target)||!press(place==503?13:12))return false;advance(target==last?30000:6500);}if(_place!=(place==503?504:527))return false;}
  int32 solved=0;return _place==527&&_runner.getValue(0,21,solved)&&solved==1&&_puzzlesCompleted==completed+uint(!before);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==23){now=scriptClock();sync();debug("Astronomica P502 slot fingerprint: %08x",fingerprint());Common::Array<byte>d;const bool ok=canSaveP502()&&snapshot(d)&&roundtrip()&&restore(d)&&fullFuture();debug("Astronomica P502 startup save: %s (slot23, failed projectile and dormant state)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();if(!entry()||!roundtrip())return false;
 // Every real direction/speed combination is selected;62 launch into failures.
 for(uint direction=1;direction<=4;++direction)for(uint setting=0;setting<16;++setting){if(!entry()||!press(15+direction)||!speed(setting)||!roundtrip())return false;if(setting==13&&(direction==1||direction==4))continue;if(!failure()||!roundtrip())return false;++failedCombinations;if(!press(direction==4?16:19)||!speed((setting+3)%16)||!roundtrip())return false;++changed;}
 // Explicit low -> high -> low without reloading retains an earlier explosion.
 if(!entry()||!press(16)||!speed(0)||!failure()||!roundtrip()||!speed(15)||!failure()||_comet.kind[19]!=3||_scene.sprites[20].selectedFrame!=9||!roundtrip()||!speed(0)||!failure()||!roundtrip())return false;
 // The actual P516 entry populates cache geometry; preserve it into P502 saves.
 now=0;sync();if(!loadPlace(516)||_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;if(!entry()||!press(17)||!speed(13)||!failure()||!press(19)||!speed(3)||!roundtrip()||!_jupiterWidths[0]||_comet.frame!=3||_comet.previousFrame!=4)return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&d){uint32 h=2166136261U;for(uint j=8;j<d.size()-4;j+=4)h=(h^READ_LE_UINT32(&d[j]))*16777619U;WRITE_LE_UINT32(&d[d.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);for(uint32 clock:{originalClock,0xfffffff0U})for(uint age:{0U,1U,1000U}){Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);const uint at=8+(11+945+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);WRITE_LE_UINT32(&timed[8+(11+19*27+9)*4],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;}if(!restore(fixture))return false;debug("Astronomica P502 timer epochs: PASS (%u inactive epoch and uint32 wrap cases)",timerCases);
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+945+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP502())return false;const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP502()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}if(_mixer->isSoundHandleActive(_soundHandle)||_system->getMillis()==voiceStart||!roundtrip())return false;debug("Astronomica P502 natural voice end: PASS (no stopHandle)");
 now=0;sync();ConfMan.setBool("astronomica_entry_scripts",true);const bool entered=loadPlace(502);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||!quiet()||_loopSound!=0)return false;now=5001;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP502())return false;const int volume=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,volume);debug("Astronomica P502 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // A valid current live state makes partial malformed loads detectable.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP502())return false;_mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageName="P502-atomic";_pendingImageX=19;_pendingImageY=23;_movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_p502AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P502 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint i:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(i,0xfffffffeU))return false;for(uint i=0;i<35;++i)if(!badWord(11+i*27+18,2))return false;for(uint i:{2U,300U,303U,306U,309U,301U,302U,602U,603U,604U})if(!badWord(11+945+i,0xffffffffU))return false;for(uint i:{0U,19U,50U,69U,100U,101U,102U,110U})if(!badWord(11+945+605+i,123456))return false;
 for(uint i:{1U,3U,4U,5U,7U,10U,11U,12U,19U,22U})if(!badWord(11+19*27+i,123456))return false;if(!badWord(11+945+601,now+1)||!badWord(11+19*27+9,now+1)||!badWord(11+20*27+1,8)||!badWord(11+8*27,1))return false;
 _pendingImage.free();_pendingImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP502())return false;debug("Astronomica P502 rejection verification: PASS (6728 truncations, 6728 corruptions, %u invalid states, extended atomic state)",invalid);
 // First and repeated success preserve the entire downstream comet puzzle route.
 for(uint repeat=0;repeat<2;++repeat){if(!restore(fixture)||!roundtrip()||!restore(fixture))return false;Common::Array<byte>branch;if(!snapshot(branch)||!fullFuture()){debug("P502 full future failed repeat%u P%d",repeat,_place);return false;}const uint32 expected=fingerprint(true);if(!restore(branch)||!fullFuture()||fingerprint(true)!=expected){debug("P502 future continuation mismatch repeat%u",repeat);return false;}++futures;++successors;if(!repeat){if(!entry()||!press(17)||!speed(13)||!failure()||!press(19)||!speed(3)||!quiet()||!snapshot(fixture))return false;}}
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_comet.frame=3;_comet.previousFrame=4;if(!entry()||!press(17)||!speed(13)||!failure()||!press(19)||!speed(3)||!quiet()||saveGameState(23,"P502 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P502 slot fingerprint: %08x",fingerprint());if(!fullFuture())return false;
 if(dirs!=15||speeds!=65535||failedCombinations!=62||!prelaunch||!low||!high||!changed||!explosions||!caches||!dormant||!ordinary)return false;
 debug("Astronomica P502 controls coverage: PASS (4 direction settings, 16 speed settings, %u failed launch combinations)",failedCombinations);
 debug("Astronomica P502 history coverage: PASS (%u prelaunch boundaries, %u low failure boundaries, %u high failure boundaries, %u changed control histories, %u retained explosion boundaries, %u private cache boundaries, %u successor checks, %u future outcome checks)",prelaunch,low,high,changed,explosions,caches,successors,futures);
 debug("Astronomica P502 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP503Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,prelaunch=0,low=0,high=0,changed=0,explosions=0,caches=0,histories=0,dormant=0,ordinary=0,busy=0,successors=0,futures=0;uint dirs=0,speeds=0,failedCombinations=0,timerCases=0,partial=0,handoffs=0,excluded=0,properMasks=0,firstKind4=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto advance=[&](uint duration){for(uint i=0;i<duration;i+=10)tick();};
 auto value=[&](int id){int32 v=-1;_runner.getValue(1,id,v);return v;};
 auto fingerprint=[&](bool departure=false){uint32 h=departure?2166136261U:_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};if(departure){Common::Array<uint32>s;if(!_runner.exportPersistentState(s))return uint32(0);for(uint i=0;i<s.size();++i)if(i!=601)add(s[i]);}for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);Common::Array<uint32>w;p516Extra(w);for(uint32 v:w)add(v);for(const Sprite&s:_scene.sprites){w.clear();p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto quiet=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP503())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;};
 auto settle=[&](){for(uint i=0;i<6000&&!_runner.scriptsIdle();++i){if(_place==503&&canSaveP503())return false;++busy;tick();}return _runner.scriptsIdle();};
 auto press=[&](uint id){if(id<1||id>_scene.sprites.size()||_runner.clicksBlocked())return false;const int origin=_place;const Sprite&s=_scene.sprites[id-1];if(spriteAt(s.renderX+15,s.renderY+10)!=int(id-1)||!_runner.canRun(s.click,true))return false;clickAtTime(s.renderX+15,s.renderY+10,now);advance(300);if(origin==503&&_place==503)return settle()&&quiet();return true;};
 auto speed=[&](int target){for(uint i=0;i<16&&value(1)!=target;++i){const int down=_place==502?6:_place==503?10:9;if(!press(down+uint(value(1)<target)))return false;}return value(1)==target;};
 auto entry=[&](){now=0;sync();return loadPlace(503)&&_runner.enqueueStartup(_scene.scripts,now,true)==_scene.scripts.size()&&settle()&&quiet();};
 auto snapshot=[&](Common::Array<byte>&d){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=8132)return false;d.resize(out.size());memcpy(&d[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&d){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&d[0],d.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&d[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(!quiet())return false;Common::Array<byte>d,again;if(!snapshot(d)){debug("P503 snapshot rejected boundary%u clock%u",boundaries,now);return false;}const uint32 before=fingerprint(),clock=now;advance(1000);const uint32 expected=fingerprint(),ended=now;if(!loadPlace(117)||!restore(d)||now!=clock||fingerprint()!=before||!snapshot(again)||again!=d){debug("P503 restore mismatch boundary%u",boundaries);return false;}advance(1000);if(now!=ended||fingerprint()!=expected){debug("P503 successor mismatch boundary%u",boundaries);return false;}Common::Array<uint32>state;_runner.exportPersistentState(state);++boundaries;++successors;bool history=false,hasOrbit=false;for(int target=5;target<=9;++target){const int kind=_comet.kind[target+18];low+=kind==2;high+=kind==3;history|=kind!=0;hasOrbit|=kind==4;}prelaunch+=!history;histories+=history;partial+=hasOrbit;explosions+=_scene.sprites[33].selectedFrame==9;caches+=_jupiterWidths[0]!=0;dormant+=state[603]!=0;ordinary+=!state[603];dirs|=1U<<(state[300]-1);speeds|=1U<<state[303];return true;};
 auto launch=[&](uint duration){if(!press(13))return false;advance(duration);return _place==503&&settle()&&quiet();};
 auto fullFuture=[&](){int32 before=0;_runner.getValue(0,21,before);const uint completed=_puzzlesCompleted;
  for(int place=503;place<=504;++place){if(_place!=place)return false;if(place==504){if(_runner.enqueueStartup(_scene.scripts,now,true)!=_scene.scripts.size())return false;advance(400);}const int first=place==503?5:1,last=place==503?9:4;for(int target=first;target<=last;++target){if(place==503&&value(target-2))continue;if(!press(5+target-first)||!press((place==503?20:19)+(target==9?1:target<=4?target:target-4)-1)||!speed(11-target)||!press(place==503?13:12))return false;advance(target==last?30000:6500);}if(_place!=(place==503?504:527))return false;}
  int32 solved=0;return _place==527&&_runner.getValue(0,21,solved)&&solved==1&&_puzzlesCompleted==completed+uint(!before);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==24){now=scriptClock();sync();debug("Astronomica P503 slot fingerprint: %08x",fingerprint());Common::Array<byte>d;const bool ok=canSaveP503()&&snapshot(d)&&roundtrip()&&restore(d)&&fullFuture();debug("Astronomica P503 startup save: %s (slot24, failed projectile and dormant state)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();if(!entry()||!roundtrip())return false;
 // First kind4 retains side bits1/1 and its inactive kind1 partner.
 for(uint target=5;target<=9;++target){if(!entry()||!press(target)||!press(19+(target==9?1:target-4))||!speed(11-target)){debug("P503 first kind4 setup failed target%u",target);return false;}const Sprite&button=_scene.sprites[12];clickAtTime(button.renderX+15,button.renderY+10,now);for(uint i=0;i<2000&&_comet.kind[target+18]!=4;++i){sync();runScriptsAt(now);animateSpritesAt(now);now+=200;sync();}const Sprite&primary=_scene.sprites[target+18];debug("P503 first kind4 target%u clock%u primary%d partner%d sides%d/%d delta%d/%d pending%u blocked%d",target,now,_comet.kind[target+18],_comet.kind[37-target],primary.orbitSideX,primary.orbitSideY,primary.moveDX,primary.moveDY,_runner.pendingCount(),int(_runner.clicksBlocked()));if(_comet.kind[target+18]!=4||_comet.kind[37-target]!=1||primary.orbitSideX!=1||primary.orbitSideY!=1||primary.moveDX||primary.moveDY||!roundtrip())return false;++firstKind4;}

 for(uint target=5;target<=9;++target)for(uint direction=1;direction<=4;++direction)for(uint setting=0;setting<16;++setting){if(!entry()||!press(target)||!press(19+direction)||!speed(setting)||!roundtrip()||!launch(6500)||!roundtrip())return false;const bool good=setting==11-target&&(target==9||direction==target-4);failedCombinations+=!good;if(!press(target==9?5:9)||!press(direction==4?20:23)||!speed((setting+3)%16)||!roundtrip())return false;++changed;}
 // All30 proper nonempty masks through actual original UI control launches.
 for(uint mask=1;mask<31;++mask){if(!entry())return false;for(uint target=5;target<=9;++target)if(mask&(1U<<(target-5))){if(!press(target)||!press(19+(target==9?1:target-4))||!speed(11-target)||!launch(6500))return false;}if(!roundtrip())return false;++properMasks;}
 debug("Astronomica P503 accepted masks: PASS (%u proper solved masks, %u first kind4 transitions)",properMasks,firstKind4);
 // Four genuine accumulated solutions and both layer handoffs.
 if(!entry())return false;for(uint target=5;target<=8;++target){if(!press(target)||!press(19+target-4)||!speed(11-target)||!launch(6500)||!roundtrip())return false;}
 for(uint i=0;i<1200;++i){bool visible[10];for(uint j=0;j<10;++j)visible[j]=_scene.sprites[23+j].visible;advance(100);bool changedVisibility=false;for(uint j=0;j<10;++j)changedVisibility|=visible[j]!=bool(_scene.sprites[23+j].visible);if(changedVisibility){++handoffs;if(!roundtrip())return false;}}
 if(!press(9)||!speed(0)||!launch(6500)||!roundtrip()||!speed(15)||!launch(6500)||!roundtrip()||!speed(0)||!launch(6500)||!roundtrip())return false;
 // Excluded solved->failed routes remain rejected, with full state left literal.
 for(uint target=5;target<=9;++target){if(!entry()||!press(target)||!press(19+(target==9?1:target-4))||!speed(11-target)||!launch(6500)||!roundtrip()||!speed(0)||!launch(6500)||canSaveP503())return false;++excluded;}
 now=0;sync();if(!loadPlace(516)||_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;if(!entry()||!press(5)||!press(20)||!speed(6)||!launch(6500)||!press(9)||!speed(0)||!launch(6500))return false;_comet.frame=3;_comet.previousFrame=4;if(!roundtrip()||!_jupiterWidths[0]||_comet.frame!=3||_comet.previousFrame!=4)return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&d){uint32 h=2166136261U;for(uint j=8;j<d.size()-4;j+=4)h=(h^READ_LE_UINT32(&d[j]))*16777619U;WRITE_LE_UINT32(&d[d.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);for(uint32 clock:{originalClock,0xfffffff0U})for(uint age:{0U,1U,1000U}){Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);for(uint i=23;i<=32;++i)for(uint field:{8U,9U}){const uint offset=8+(11+i*27+field)*4;const uint32 old=READ_LE_UINT32(&timed[offset]);if(old)WRITE_LE_UINT32(&timed[offset],old+delta);}const uint at=8+(11+1296+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);WRITE_LE_UINT32(&timed[8+(11+27*27+9)*4],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;}if(!restore(fixture))return false;
 // Before/at/after the actual30ms frame and40ms movement periods, with independent epochs.
 for(uint wrap=0;wrap<2;++wrap)for(uint period:{30U,40U})for(uint age:{period-1,period,period+1}){Common::Array<byte>timed=fixture;const uint32 clock=wrap?0xfffffff0U:originalClock,delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);WRITE_LE_UINT32(&timed[8+(11+1296+601)*4],READ_LE_UINT32(&timed[8+(11+1296+601)*4])+delta);for(uint i=23;i<=32;++i)for(uint field:{8U,9U}){const uint offset=8+(11+i*27+field)*4;const uint32 old=READ_LE_UINT32(&timed[offset]);if(old)WRITE_LE_UINT32(&timed[offset],old+delta);}for(uint index:{23U,32U})WRITE_LE_UINT32(&timed[8+(11+index*27+(period==30?8:9))*4],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;}
 if(!restore(fixture))return false;debug("Astronomica P503 timer epochs: PASS (%u independent frame movement and uint32 wrap cases)",timerCases);
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+1296+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP503())return false;const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP503()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}if(_mixer->isSoundHandleActive(_soundHandle)||_system->getMillis()==voiceStart||!roundtrip())return false;debug("Astronomica P503 natural voice end: PASS (no stopHandle)");
 now=0;sync();ConfMan.setBool("astronomica_entry_scripts",true);const bool entered=loadPlace(503);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||!quiet()||_loopSound!=0)return false;now=5001;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP503())return false;const int volume=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,volume);debug("Astronomica P503 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // A valid current live state makes partial malformed loads detectable.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP503())return false;_mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageName="P503-atomic";_pendingImageX=19;_pendingImageY=23;_movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_p503AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P503 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint i:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(i,0xfffffffeU))return false;for(uint i=0;i<48;++i)if(!badWord(11+i*27+18,2))return false;for(uint i:{2U,300U,303U,306U,309U,301U,302U,602U,603U,604U})if(!badWord(11+1296+i,0xffffffffU))return false;for(uint i:{0U,23U,50U,73U,100U,101U,102U,110U})if(!badWord(11+1296+605+i,123456))return false;
 for(uint i:{1U,3U,4U,5U,7U,10U,11U,12U,19U,22U})if(!badWord(11+27*27+i,123456))return false;if(!badWord(11+1296+601,now+1)||!badWord(11+27*27+9,now+1)||!badWord(11+33*27+1,8)||!badWord(11+12*27,1))return false;
 _pendingImage.free();_pendingImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP503())return false;debug("Astronomica P503 rejection verification: PASS (8132 truncations, 8132 corruptions, %u invalid states, extended atomic state)",invalid);
 // First and repeated true downstream game outcomes from partial state.
 for(uint repeat=0;repeat<2;++repeat){if(!restore(fixture)||!roundtrip()||!restore(fixture))return false;Common::Array<byte>branch;if(!snapshot(branch)||!fullFuture())return false;const uint32 expected=fingerprint(true);if(!restore(branch)||!fullFuture()||fingerprint(true)!=expected)return false;++futures;++successors;if(!repeat){if(!entry()||!press(5)||!press(20)||!speed(6)||!launch(6500)||!quiet()||!snapshot(fixture))return false;}}
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();if(!entry()||!press(5)||!press(20)||!speed(6)||!launch(6500))return false;_comet.frame=3;_comet.previousFrame=4;if(!roundtrip()||saveGameState(24,"P503 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P503 slot fingerprint: %08x",fingerprint());if(!fullFuture())return false;
 if(dirs!=15||speeds!=65535||failedCombinations!=312||!prelaunch||!low||!high||!changed||!partial||!handoffs||excluded!=5||!explosions||!caches||!dormant||!ordinary)return false;
 debug("Astronomica P503 controls coverage: PASS (5 target settings, 4 direction settings, 16 speed settings, %u failed launch combinations)",failedCombinations);
 debug("Astronomica P503 orbit coverage: PASS (%u partial boundaries, %u handoffs, %u excluded solved failure histories)",partial,handoffs,excluded);
 debug("Astronomica P503 history coverage: PASS (%u prelaunch boundaries, %u low failure boundaries, %u high failure boundaries, %u changed control histories, %u retained explosion boundaries, %u private cache boundaries, %u successor checks, %u future outcome checks)",prelaunch,low,high,changed,explosions,caches,successors,futures);
 debug("Astronomica P503 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP504Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,prelaunch=0,low=0,high=0,changed=0,explosions=0,caches=0,histories=0,dormant=0,ordinary=0,busy=0,successors=0,futures=0;uint dirs=0,speeds=0,failedCombinations=0,timerCases=0,partial=0,handoffs=0,excluded=0,properMasks=0,firstKind4=0,pollCases=0,rejectedPoll=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto advance=[&](uint duration){for(uint i=0;i<duration;i+=10)tick();};
 auto value=[&](int id){int32 v=-1;_runner.getValue(1,id,v);return v;};
 auto fingerprint=[&](bool departure=false){uint32 h=departure?2166136261U:_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};if(departure){Common::Array<uint32>s;if(!_runner.exportPersistentState(s))return uint32(0);for(uint i=0;i<s.size();++i)if(i!=601)add(s[i]);}for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);Common::Array<uint32>w;p516Extra(w);for(uint32 v:w)add(v);for(const Sprite&s:_scene.sprites){w.clear();p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto quiet=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP504())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;};
 auto pollState=[&](Common::Array<uint32>&state){return _runner.exportP504PollState(state,now);};
 auto settle=[&](){if(_place!=504){for(uint i=0;i<6000&&!_runner.scriptsIdle();++i)tick();return _runner.scriptsIdle();}Common::Array<uint32>state;for(uint i=0;i<6000&&!pollState(state);++i){if(_place==504&&canSaveP504())return false;++busy;tick();}return pollState(state);};
 auto press=[&](uint id){if(id<1||id>_scene.sprites.size()||_runner.clicksBlocked())return false;const int origin=_place;const Sprite&s=_scene.sprites[id-1];if(spriteAt(s.renderX+15,s.renderY+10)!=int(id-1)||!_runner.canRun(s.click,true))return false;clickAtTime(s.renderX+15,s.renderY+10,now);advance(300);if(origin==504&&_place==504){if(id==12||value(7)||value(8))return quiet();return settle()&&quiet();}return true;};
 auto speed=[&](int target){for(uint i=0;i<16&&value(1)!=target;++i){const int down=9;if(!press(down+uint(value(1)<target)))return false;}return value(1)==target;};
 auto entry=[&](){now=0;sync();return loadPlace(504)&&_runner.enqueueStartup(_scene.scripts,now,true)==_scene.scripts.size()&&settle()&&quiet();};
 auto snapshot=[&](Common::Array<byte>&d){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=7816)return false;d.resize(out.size());memcpy(&d[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&d){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&d[0],d.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&d[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(!settle()||!quiet())return false;Common::Array<byte>d,again;if(!snapshot(d)){debug("P504 snapshot rejected boundary%u clock%u",boundaries,now);return false;}const uint32 before=fingerprint(),clock=now;advance(1000);const uint32 expected=fingerprint(),ended=now;if(!loadPlace(117)||!restore(d)||now!=clock||fingerprint()!=before||!snapshot(again)||again!=d){debug("P504 restore mismatch boundary%u",boundaries);return false;}advance(1000);if(now!=ended||fingerprint()!=expected){debug("P504 successor mismatch boundary%u",boundaries);return false;}Common::Array<uint32>state;if(!settle()||!quiet()||!pollState(state))return false;++boundaries;++successors;bool history=false,hasOrbit=false;for(int target=1;target<=4;++target){const int kind=_comet.kind[target+21];low+=kind==2;high+=kind==3;history|=kind!=0;hasOrbit|=kind==4;}prelaunch+=!history;histories+=history;partial+=hasOrbit;explosions+=_scene.sprites[30].selectedFrame==9;caches+=_jupiterWidths[0]!=0;dormant+=state[603]!=0;ordinary+=!state[603];dirs|=1U<<(state[300]-1);speeds|=1U<<state[303];return true;};
 auto launch=[&](uint duration){if(!press(12))return false;advance(duration);return _place==504&&settle()&&quiet();};
 auto fullFuture=[&](){int32 before=0;_runner.getValue(0,21,before);const uint completed=_puzzlesCompleted;if(_place!=504)return false;for(uint target=1;target<=4;++target){if(value(target+2))continue;if(!press(target+4)||!press(18+target)||!speed(11-target)||!press(12))return false;advance(target==4?30000:6500);}int32 solved=0;const bool known=_runner.getValue(0,21,solved);debug("P504 full future outcome P%d before%d known%d solved%d completed%u expected%u clock%u",_place,before,int(known),solved,_puzzlesCompleted,completed+uint(!before),now);return _place==527&&known&&solved==1&&_puzzlesCompleted==completed+uint(!before);};
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==25){now=scriptClock();sync();debug("Astronomica P504 slot fingerprint: %08x",fingerprint());Common::Array<byte>d;const bool ok=canSaveP504()&&snapshot(d)&&roundtrip()&&restore(d)&&fullFuture();debug("Astronomica P504 startup save: %s (slot25, failed projectile and dormant state)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();if(!entry()||!roundtrip())return false;
 // First kind4 retains side bits1/1 and its inactive kind1 partner.
 for(uint target=1;target<=4;++target){if(!entry()||!press(target+4)||!press(18+target)||!speed(11-target)){debug("P504 first kind4 setup failed target%u",target);return false;}const Sprite&button=_scene.sprites[11];clickAtTime(button.renderX+15,button.renderY+10,now);for(uint i=0;i<2000&&_comet.kind[target+21]!=4;++i){sync();runScriptsAt(now);animateSpritesAt(now);now+=200;sync();}const Sprite&primary=_scene.sprites[target+21];debug("P504 first kind4 target%u clock%u primary%d partner%d sides%d/%d delta%d/%d pending%u blocked%d",target,now,_comet.kind[target+21],_comet.kind[30-target],primary.orbitSideX,primary.orbitSideY,primary.moveDX,primary.moveDY,_runner.pendingCount(),int(_runner.clicksBlocked()));if(_comet.kind[target+21]!=4||_comet.kind[30-target]!=1||primary.orbitSideX!=1||primary.orbitSideY!=1||primary.moveDX||primary.moveDY||!roundtrip())return false;++firstKind4;}

 for(uint target=1;target<=4;++target)for(uint direction=1;direction<=4;++direction)for(uint setting=0;setting<16;++setting){if(!entry()||!press(target+4)||!press(18+direction)||!speed(setting)||!roundtrip()||!launch(6500)||!roundtrip())return false;const bool good=setting==11-target&&(direction==target);failedCombinations+=!good;if(!press(target==4?5:8)||!press(direction==4?19:22)||!speed((setting+3)%16)||!roundtrip())return false;++changed;}
 // All30 proper nonempty masks through actual original UI control launches.
 for(uint mask=1;mask<15;++mask){if(!entry())return false;for(uint target=1;target<=4;++target)if(mask&(1U<<(target-1))){if(!press(target+4)||!press(18+target)||!speed(11-target)||!launch(6500))return false;}if(!roundtrip())return false;++properMasks;}
 debug("Astronomica P504 accepted masks: PASS (%u proper solved masks, %u first kind4 transitions)",properMasks,firstKind4);
 // Four genuine accumulated solutions and both layer handoffs.
 if(!entry())return false;for(uint target=1;target<=3;++target){if(!press(target+4)||!press(18+target)||!speed(11-target)||!launch(6500)||!roundtrip())return false;}
 for(uint i=0;i<1200;++i){bool visible[8];for(uint j=0;j<8;++j)visible[j]=_scene.sprites[22+j].visible;advance(100);bool changedVisibility=false;for(uint j=0;j<8;++j)changedVisibility|=visible[j]!=bool(_scene.sprites[22+j].visible);if(changedVisibility){++handoffs;if(!roundtrip())return false;}}
 if(!press(8)||!speed(0)||!launch(6500)||!roundtrip()||!speed(15)||!launch(6500)||!roundtrip()||!speed(0)||!launch(6500)||!roundtrip())return false;
 // Excluded solved->failed routes remain rejected, with full state left literal.
 for(uint target=1;target<=4;++target){if(!entry()||!press(target+4)||!press(18+target)||!speed(11-target)||!launch(6500)||!roundtrip()||!speed(0)||!launch(6500)||canSaveP504())return false;++excluded;}
 now=0;sync();if(!loadPlace(516)||_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;if(!entry()||!press(5)||!press(19)||!speed(10)||!launch(6500)||!press(8)||!speed(0)||!launch(6500))return false;_comet.frame=3;_comet.previousFrame=4;if(!roundtrip()||!_jupiterWidths[0]||_comet.frame!=3||_comet.previousFrame!=4)return false;
 Common::Array<byte>pollFixture;if(!snapshot(pollFixture))return false;
 for(uint pendingIndex:{0U,10U})for(uint32 origin:{1000U,0xfffffe00U})for(uint age:{0U,1U,199U,200U,201U,1000U}){if(!entry())return false;Common::Array<uint32>state;if(!pollState(state))return false;state[601]=origin;state[605]=pendingIndex;state[606]=pendingIndex?origin+200:origin;const uint32 clock=state[606]+age;_runner.clear();if(!_runner.importP504PollState(state,clock))return false;now=clock;sync();for(Sprite&sprite:_scene.sprites)if(sprite.autoFrame)sprite.frameSince=origin;if(!quiet()||!roundtrip())return false;++pollCases;}
 if(!restore(pollFixture))return false;for(uint i=0;i<100;++i){Common::Array<uint32>state,queue;_runner.auditP509Snapshot(state,queue);Common::Array<uint32>exported;if(!pollState(exported)&&_runner.pendingCount()==1&&!_runner.clicksBlocked()){if(canSaveP504())return false;++rejectedPoll;}tick();}if(!rejectedPoll||!restore(pollFixture))return false;debug("Astronomica P504 poll coverage: PASS (%u timer cases, %u excluded poll phases)",pollCases,rejectedPoll);
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&d){uint32 h=2166136261U;for(uint j=8;j<d.size()-4;j+=4)h=(h^READ_LE_UINT32(&d[j]))*16777619U;WRITE_LE_UINT32(&d[d.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);for(uint32 clock:{originalClock,0xfffffff0U})for(uint age:{0U,1U,1000U}){Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);for(uint i=22;i<=29;++i)for(uint field:{8U,9U}){const uint offset=8+(11+i*27+field)*4;const uint32 old=READ_LE_UINT32(&timed[offset]);if(old)WRITE_LE_UINT32(&timed[offset],old+delta);}const uint at=8+(11+1215+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);WRITE_LE_UINT32(&timed[8+(11+25*27+9)*4],clock-age);WRITE_LE_UINT32(&timed[8+(11+1215+606)*4],READ_LE_UINT32(&timed[8+(11+1215+606)*4])+delta);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;}if(!restore(fixture))return false;
 // Before/at/after the actual30ms frame and40ms movement periods, with independent epochs.
 for(uint wrap=0;wrap<2;++wrap)for(uint period:{30U,40U})for(uint age:{period-1,period,period+1}){Common::Array<byte>timed=fixture;const uint32 clock=wrap?0xfffffff0U:originalClock,delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);WRITE_LE_UINT32(&timed[8+(11+1215+601)*4],READ_LE_UINT32(&timed[8+(11+1215+601)*4])+delta);for(uint i=22;i<=29;++i)for(uint field:{8U,9U}){const uint offset=8+(11+i*27+field)*4;const uint32 old=READ_LE_UINT32(&timed[offset]);if(old)WRITE_LE_UINT32(&timed[offset],old+delta);}for(uint index:{22U,29U})WRITE_LE_UINT32(&timed[8+(11+index*27+(period==30?8:9))*4],clock-age);WRITE_LE_UINT32(&timed[8+(11+1215+606)*4],READ_LE_UINT32(&timed[8+(11+1215+606)*4])+delta);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;}
 if(!restore(fixture))return false;debug("Astronomica P504 timer epochs: PASS (%u independent frame movement and uint32 wrap cases)",timerCases);
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+1215+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP504())return false;const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP504()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}if(_mixer->isSoundHandleActive(_soundHandle)||_system->getMillis()==voiceStart||!roundtrip())return false;debug("Astronomica P504 natural voice end: PASS (no stopHandle)");
 now=0;sync();ConfMan.setBool("astronomica_entry_scripts",true);const bool entered=loadPlace(504);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||!quiet()||_loopSound!=0)return false;now=5001;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP504())return false;const int volume=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,volume);debug("Astronomica P504 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // A valid current live state makes partial malformed loads detectable.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP504())return false;_mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageName="P504-atomic";_pendingImageX=19;_pendingImageY=23;_movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_p504AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P504 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint i:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(i,0xfffffffeU))return false;for(uint i=0;i<45;++i)if(!badWord(11+i*27+18,2))return false;for(uint i:{2U,300U,303U,306U,309U,301U,302U,602U,603U,604U})if(!badWord(11+1215+i,0xffffffffU))return false;for(uint i:{0U,22U,50U,72U,100U,101U,102U,110U})if(!badWord(11+1215+607+i,123456))return false;
 for(uint i:{1U,3U,4U,5U,7U,10U,11U,12U,19U,22U})if(!badWord(11+25*27+i,123456))return false;if(!badWord(11+1215+601,now+1)||!badWord(11+25*27+9,now+1)||!badWord(11+30*27+1,8)||!badWord(11+11*27,1))return false;
 if(!badWord(11+1215+605,3)||!badWord(11+1215+606,now+1))return false;
 _pendingImage.free();_pendingImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP504())return false;debug("Astronomica P504 rejection verification: PASS (7816 truncations, 7816 corruptions, %u invalid states, extended atomic state)",invalid);
 // First and repeated true downstream game outcomes from partial state.
 for(uint repeat=0;repeat<2;++repeat){if(!restore(fixture)||!roundtrip()||!restore(fixture))return false;Common::Array<byte>branch;if(!snapshot(branch)||!fullFuture()){debug("P504 first future branch failed repeat%u",repeat);return false;}const uint32 expected=fingerprint(true);if(!restore(branch)||!fullFuture()||fingerprint(true)!=expected){debug("P504 restored future branch failed repeat%u expectedhash%08x actual%08x",repeat,expected,fingerprint(true));return false;}++futures;++successors;if(!repeat){if(!entry()||!press(5)||!press(19)||!speed(10)||!launch(6500)||!quiet()||!snapshot(fixture))return false;}}
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();if(!entry()||!press(5)||!press(19)||!speed(10)||!launch(6500))return false;_comet.frame=3;_comet.previousFrame=4;if(!roundtrip()||saveGameState(25,"P504 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P504 slot fingerprint: %08x",fingerprint());if(!fullFuture())return false;
 if(pollCases!=24||!rejectedPoll||dirs!=15||speeds!=65535||failedCombinations!=252||!prelaunch||!low||!high||!changed||!partial||!handoffs||excluded!=4||!explosions||!caches||!dormant||!ordinary)return false;
 debug("Astronomica P504 controls coverage: PASS (4 target settings, 4 direction settings, 16 speed settings, %u failed launch combinations)",failedCombinations);
 debug("Astronomica P504 orbit coverage: PASS (%u partial boundaries, %u handoffs, %u excluded solved failure histories)",partial,handoffs,excluded);
 debug("Astronomica P504 history coverage: PASS (%u prelaunch boundaries, %u low failure boundaries, %u high failure boundaries, %u changed control histories, %u retained explosion boundaries, %u private cache boundaries, %u successor checks, %u future outcome checks)",prelaunch,low,high,changed,explosions,caches,successors,futures);
 debug("Astronomica P504 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyCometPuzzles() {
 bool ok = verifyCometMotion(), setup = verifyCometSetup();
 debug("Astronomica comet original motion comparison: %s (30 trajectories)",ok ? "PASS" : "FAIL");
 debug("Astronomica comet original setup comparison: %s (1920 display/launch states)",setup ? "PASS" : "FAIL");
 ok = setup && ok;
 const uint32 rgb888[] = {0x356fce2aU,0xce864829U,0x356fce2aU,0x29a134a6U,0x976e2a18U,0xc4e27e01U,0xefd07d69U,0xccc2599cU,0xac1d0a70U};
 const uint32 rgb565[] = {0x58ce30a4U,0xbc1112abU,0x58ce30a4U,0xd7d344b6U,0xaeb8a9fcU,0x7e5b15e7U,0xdf4366d3U,0x29d47ba4U,0xccd6d989U};
 bool graphicsOK = true;
 for (int place = 502; place <= 504; ++place) for (int variant = 0; variant < 3; ++variant) {
  if (!loadPlace(place)) return false;
  if (variant) for (uint i = 0; i < _scene.sprites.size(); ++i) {
   if ((place == 502 && i == 19) || (place == 503 && i >= 23 && i <= 32) || (place == 504 && i >= 22 && i <= 29)) {
    Sprite &s = _scene.sprites[i]; s.visible = 1; s.renderX = 300; s.renderY = variant == 1 ? 150 : 310;
   }
  }
  redrawSprites(); const uint32 actual = screenRGBHash(_screen);
  const int index = (place-502)*3+variant;
  const uint32 expected = _screen.format.bytesPerPixel == 2 ? rgb565[index] : rgb888[index];
  if (actual != expected) debug("Comet P%d composition %d: %08x expected %08x",place,variant,actual,expected);
  graphicsOK = actual == expected && graphicsOK;
 }
 debug("Astronomica comet original composition comparison: %s (nine layer/clone/bottom-bound images)",graphicsOK ? "PASS" : "FAIL");
 ok = graphicsOK && ok;
 _runner.resetGlobals();
 uint32 now = 0;
 auto value = [&](int id) { int32 v = -1; _runner.getValue(1,id,v); return v; };
 auto step = [&]() { runScriptsAt(now); animateSpritesAt(now); now += 10; };
 auto wait = [&](uint duration) { const uint32 end = now+duration; while (now < end) step(); };
 auto press = [&](int id) {
  if (id < 1 || uint(id) > _scene.sprites.size()) return false;
  const Sprite &s = _scene.sprites[id-1]; const int x = s.renderX+15, y = s.renderY+10;
  if (_runner.clicksBlocked() || spriteAt(x,y) != id-1 || !_runner.canRun(s.click,true)) {
   debug("Comet P%d rejected button %d, blocked %d, hit %d, ready %d",_place,id,int(_runner.clicksBlocked()),spriteAt(x,y),int(_runner.canRun(s.click,true))); return false;
  }
  clickAtTime(x,y,now); step(); wait(200); return true;
 };
 auto speed = [&](int level) {
  for (int n = 0; n < 16 && value(1) != level; ++n) {
   const int down = _place == 502 ? 6 : _place == 503 ? 10 : 9;
   if (!press(down+(value(1) < level))) return false;
  }
  return value(1) == level;
 };
 auto entry = [&]() { return _runner.enqueueStartup(_scene.scripts,now,true) == _scene.scripts.size(); };
 for (int route = 0; route < 2; ++route) {
  _runner.defineValue(0,21,route); const uint completed = _puzzlesCompleted;
  bool good = loadPlace(route ? 503 : 502) && entry();
  for (int place = route ? 503 : 502; place <= 504 && good; ++place) {
   if (_place != place) { good = false; break; }
   const int first = place == 502 ? 10 : place == 503 ? 5 : 1;
   const int last = place == 502 ? 10 : place == 503 ? 9 : 4;
   for (int target = first; target <= last && good; ++target) {
    if (place != 502) good = press(5+target-first) && value(2) == target && good;
    const int direction = target == 9 || target == 10 ? 1 : target <= 4 ? target : target-4;
    good = press((place == 502 ? 16 : place == 503 ? 20 : 19)+direction-1) && good;
    good = speed(target == 10 ? 13 : 11-target) && good;
    good = press(place == 502 ? 9 : place == 503 ? 13 : 12) && good;
    wait(target == last ? 30000 : 6500);
    if (target != last) {
     const int id = target+(target <= 4 ? 22 : 19), partner = (target <= 4 ? 53 : 57)-id;
     good = _place == place && value(target <= 4 ? target+2 : target-2) == 1 &&
      (_scene.sprites[id-1].visible || _scene.sprites[partner-1].visible) && !_runner.clicksBlocked() && good;
    }
   }
   const int expected = place == 504 ? 527 : place+1;
   good = _place == expected && good;
   debug("Astronomica comet route %d P%d transition: %s (P%d)",route,place,good ? "PASS" : "FAIL",_place);
   if (place < 504 && good) good = entry();
  }
  int32 solved = 0;
  good = _place == 527 && _runner.getValue(0,21,solved) && solved == 1 && _puzzlesCompleted == completed+uint(route == 0) && good;
  debug("Astronomica comet complete route %d: %s",route,good ? "PASS" : "FAIL"); ok = good && ok;
 }
 for (int place = 502; place <= 504; ++place) {
  bool good = loadPlace(place) && entry();
  const int target = value(2), id = target == 10 ? 20 : target+(target <= 4 ? 22 : 19);
  const int launch = place == 502 ? 9 : place == 503 ? 13 : 12;
  for (int failure = 0; failure < 3; ++failure) {
   good = speed(failure == 0 ? 0 : failure == 1 ? 15 : target == 10 ? 13 : 11-target) && good;
   if (failure == 2) good = press((place == 502 ? 16 : place == 503 ? 20 : 19)+1) && good;
   good = press(launch) && good; wait(6500);
   good = _place == place && !_scene.sprites[id-1].visible && !_scene.sprites[id-1].autoMove && !_runner.clicksBlocked() && good;
  }
  good = press(2) && good; wait(1000); good = _place == 174 && good;
  debug("Astronomica comet P%d failure/exit route: %s",place,good ? "PASS" : "FAIL"); ok = good && ok;
 }
 debug("Astronomica comet interaction verification: %s (P502-P504 transitions, repeated success, low/high speed, wrong direction, exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP501Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,histories=0,dormant=0,ordinary=0,busy=0,successors=0,futures=0,worlds=0,backgrounds=0,historyChecks=0,strikeChecks=0,pollCases=0,inputChecks=0,pauseChecks=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};auto advance=[&](uint duration){const uint32 start=now;while(_place==501&&uint32(now-start)<duration)tick();};
 auto value=[&](int id){int32 v=-1;_runner.getValue(1,id,v);return v;};auto quiet=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}++busy;_mixer->stopHandle(_soundHandle);}return true;};
 auto poll=[&](Common::Array<uint32>&state){return _runner.exportP501ReadyState(state,now);};auto settle=[&](){Common::Array<uint32>state;for(uint i=0;i<10000&&_place==501;++i){if(poll(state)&&!_scene.sprites[24].autoMove&&!_pendingImage.w)return quiet();if(canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}++busy;tick();}{debug("P501 test failure line%d",__LINE__);return false;}};
 auto press=[&](uint id){if(_place!=501||id>=27||_runner.clicksBlocked()){debug("P501 test failure line%d",__LINE__);return false;}const Sprite&sprite=_scene.sprites[id];const int x=sprite.x+2,y=sprite.y+2;if(spriteAt(x,y)!=int(id)||!_runner.canRun(sprite.click,true)){debug("P501 test failure line%d",__LINE__);return false;}clickAtTime(x,y,now);tick();return true;};
 const uint buttons[]={0,10,7,8,11,9};auto select=[&](uint world){if(world<1||world>5||!press(buttons[world])){debug("P501 test failure line%d",__LINE__);return false;}advance(1200);return value(0)==int(world)&&settle();};auto entry=[&](){now=0;sync();return loadPlace(501)&&_runner.enqueueStartup(_scene.scripts,now,true)==1&&settle();};
 auto fingerprint=[&](bool departure=false){uint32 hash=departure?2166136261U:_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){hash=(hash^v)*16777619U;};if(departure){Common::Array<uint32>state;if(!_runner.exportPersistentState(state))return uint32(0);for(uint i=0;i<state.size();++i)if(i!=601)add(state[i]);}for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame),uint32(_ball.scenario),uint32(_ball.centerX),uint32(_ball.centerY),uint32(_ball.side),uint32(_ball.period)})add(v);Common::Array<uint32>extra;p516Extra(extra);for(uint32 v:extra)add(v);for(const Sprite&sprite:_scene.sprites){Common::Array<uint32>words;p526SpriteWords(sprite,words);for(uint32 v:words)add(v);}for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return hash;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=5896){debug("P501 snapshot rejected boundary%u clock%u world%d pitch%d ball%d bg%s",boundaries,now,value(0),value(1),_ball.scenario,_displayedImageName.c_str());{debug("P501 test failure line%d",__LINE__);return false;}}data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&data[16])){debug("P501 test failure line%d",__LINE__);return false;}now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(!settle()){debug("P501 test failure line%d",__LINE__);return false;}Common::Array<byte>saved,again;if(!snapshot(saved)){debug("P501 test failure line%d",__LINE__);return false;}const uint32 before=fingerprint(),clock=now;advance(1000);const uint32 expected=fingerprint(),ended=now;if(!loadPlace(117)||!restore(saved)||now!=clock||fingerprint()!=before||!snapshot(again)||again!=saved){debug("P501 restore mismatch boundary%u",boundaries);{debug("P501 test failure line%d",__LINE__);return false;}}advance(1000);if(now!=ended||fingerprint()!=expected){debug("P501 future tick mismatch boundary%u",boundaries);{debug("P501 test failure line%d",__LINE__);return false;}}if(!settle()){debug("P501 test failure line%d",__LINE__);return false;}Common::Array<uint32>state;if(!poll(state)){debug("P501 test failure line%d",__LINE__);return false;}++boundaries;++successors;histories+=_ball.scenario!=0;dormant+=state[603]!=0;ordinary+=!state[603];worlds|=1U<<state[300];backgrounds|=1U<<p501ImageId(_displayedImageName);return true;};
 auto pitchHit=[&](int distance,bool direct=false){if(!press(4)){debug("P501 test failure line%d",__LINE__);return false;}bool window=false;for(uint i=0;i<1000&&_place==501;++i){if(value(1)==1&&_scene.sprites[24].autoMove&&_scene.sprites[24].renderX-_scene.sprites[25].x<=distance){window=true;break;}if(canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}++busy;tick();}if(!window){debug("P501 test failure line%d",__LINE__);return false;}if(direct)onBall(0,now);else if(!press(5)){debug("P501 test failure line%d",__LINE__);return false;}advance(100);return true;};
 auto fullFuture=[&](){int32 before=0;_runner.getValue(0,20,before);const uint completed=_puzzlesCompleted;if(!select(4)||!pitchHit(75)||value(1)!=2||_ball.scenario!=4){debug("P501 test failure line%d",__LINE__);return false;}bool returned=false;for(uint i=0;i<2000&&_place==501;++i){if(_ball.side==0&&_scene.sprites[24].renderX>=100){returned=true;break;}if(canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}++busy;tick();}if(!returned||!press(6)){debug("P501 test failure line%d",__LINE__);return false;}advance(18000);int32 solved=0;const bool known=_runner.getValue(0,20,solved);debug("P501 future outcome P%d solved%d completed%u expected%u",_place,solved,_puzzlesCompleted,completed+uint(!before));return _place==388&&known&&solved==1&&_puzzlesCompleted==completed+uint(!before);};
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==26){now=scriptClock();sync();debug("Astronomica P501 slot fingerprint: %08x",fingerprint());const bool ok=canSaveP501()&&roundtrip()&&fullFuture();debug("Astronomica P501 startup save: %s (slot26, retained ready history)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();if(!entry()||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}for(uint world=1;world<=5;++world)if(!select(world)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}
debug("P501 phase: selected all worlds");
 // Actual regular hit histories, including selection during Vesta's5000ms pause.
 for(uint hitWorld:{1U,5U,4U}){if(!entry()||!select(hitWorld)||!pitchHit(75)||value(1)!=2){debug("P501 test failure line%d",__LINE__);return false;}if(hitWorld==4){bool paused=false;for(uint i=0;i<2000;++i){tick();if(_ball.period==5000){paused=true;break;}}if(!paused){debug("P501 test failure line%d",__LINE__);return false;}++pauseChecks;}for(uint world=1;world<=5;++world){if(!select(world)){debug("P501 test failure line%d",__LINE__);return false;}advance(22000);if(!settle()||!roundtrip()||_ball.scenario!=int(hitWorld)){debug("P501 test failure line%d",__LINE__);return false;}++historyChecks;}}
debug("P501 phase: cross-world histories complete");
 if(!entry()||!select(2)||!press(4)){debug("P501 test failure line%d",__LINE__);return false;}advance(14000);if(!settle()||!roundtrip()||!select(3)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}
debug("P501 phase: crush history complete");
 // Real strikes0/1/2 and third-strike reset preserve BACKORBI as a separate identity.
 if(!entry()||!select(4)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}for(uint attempt=0;attempt<3;++attempt){if(!pitchHit(1000)||value(1)!=0){debug("P501 test failure line%d",__LINE__);return false;}advance(8500);if(!settle()||value(2)!=int(attempt==2?0:attempt+1)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}++strikeChecks;}if(value(0)||_displayedImageName!="backorbi"){debug("P501 test failure line%d",__LINE__);return false;}
debug("P501 phase: strike histories complete");
 // Strict original hit window through actual pitch movement.
 for(int distance:{40,41,99,100}){if(!entry()||!select(4)||!roundtrip()||!pitchHit(distance,true)||value(1)!=(distance>40&&distance<100?2:0)){debug("P501 test failure line%d",__LINE__);return false;}++inputChecks;advance(22000);if(!select(4)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}}
debug("P501 phase: hit windows complete");
 // Catch boundaries exercise the real callback after restoring the same ready state.
 Common::Array<byte>ready;if(!snapshot(ready)){debug("P501 test failure line%d",__LINE__);return false;}for(int distance:{-30,-29,59,60}){if(!restore(ready)){debug("P501 test failure line%d",__LINE__);return false;}_runner.defineValue(1,1,2);_scene.sprites[24].renderX=_scene.sprites[25].x+distance;onBall(1,now);if(value(3)!=int(distance> -30&&distance<60)){debug("P501 test failure line%d",__LINE__);return false;}++inputChecks;}if(!restore(ready)){debug("P501 test failure line%d",__LINE__);return false;}
debug("P501 phase: catch windows complete");
 // Populate actual dormant Jupiter cache, then retain variant/global/Comet history.
 now=0;sync();if(!loadPlace(516)||_runner.enqueueStartup(_scene.scripts,now,true)!=2){debug("P501 test failure line%d",__LINE__);return false;}for(uint i=0;i<1000&&!_runner.scriptsIdle();++i)tick();if(!_runner.scriptsIdle()||loadGameState(99).getCode()!=Common::kNoError){debug("P501 test failure line%d",__LINE__);return false;}_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;if(!entry()||!select(4)||!pitchHit(75)){debug("P501 test failure line%d",__LINE__);return false;}while(_ball.period!=5000)tick();if(!select(5)){debug("P501 test failure line%d",__LINE__);return false;}advance(22000);_comet.frame=3;_comet.previousFrame=4;if(!roundtrip()||_ball.period!=5000||!_jupiterWidths[0]){debug("P501 test failure line%d",__LINE__);return false;}
 Common::Array<byte>fixture;if(!snapshot(fixture)){debug("P501 test failure line%d",__LINE__);return false;}auto checksum=[&](Common::Array<byte>&data){uint32 hash=2166136261U;for(uint at=8;at<data.size()-4;at+=4)hash=(hash^READ_LE_UINT32(&data[at]))*16777619U;WRITE_LE_UINT32(&data[data.size()-4],hash);};
 for(uint index:{0U,7U})for(uint32 origin:{1000U,0xfffffe00U})for(uint age:{0U,1U,199U,200U,201U,1000U}){if(!entry()){debug("P501 test failure line%d",__LINE__);return false;}Common::Array<uint32>state;if(!poll(state)){debug("P501 test failure line%d",__LINE__);return false;}state[601]=origin;state[605]=index;state[606]=index?origin+200:origin;const uint32 clock=state[606]+age;_runner.clear();if(!_runner.importP501ReadyState(state,clock)){debug("P501 test failure line%d",__LINE__);return false;}now=clock;sync();if(!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}++pollCases;}if(!restore(fixture)){debug("P501 test failure line%d",__LINE__);return false;}
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP501()&&_mixer->isSoundHandleActive(_soundHandle)){debug("P501 test failure line%d",__LINE__);return false;}++busy;_system->delayMillis(10);}if(_mixer->isSoundHandleActive(_soundHandle)||!roundtrip()){debug("P501 test failure line%d",__LINE__);return false;}debug("Astronomica P501 natural voice end: PASS (no stopHandle)");
 const int musicVolume=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);if(!playSound(_loopSound,now,true)||!canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117)){debug("P501 test failure line%d",__LINE__);return false;}const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music){debug("P501 test failure line%d",__LINE__);return false;}_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,musicVolume);_mixer->stopHandle(_soundHandle);if(!restore(fixture)){debug("P501 test failure line%d",__LINE__);return false;}debug("Astronomica P501 Music restart: PASS (one ambient start, Music volume unchanged)");
 // A valid current live state makes partial malformed loads detectable.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}_mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageName="P501-atomic";_pendingImageX=19;_pendingImageY=23;_movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_p501AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels){debug("P501 test failure line%d",__LINE__);return false;}}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad)){debug("P501 test failure line%d",__LINE__);return false;}}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P501 invalid accepted field%u value%u",index,value);{debug("P501 test failure line%d",__LINE__);return false;}}++invalid;return true;};
 for(uint i:{0U,3U,4U,5U,7U,8U,9U,10U,11U})if(!badWord(i,0xfffffffeU)){debug("P501 test failure line%d",__LINE__);return false;}for(uint i=0;i<27;++i)if(!badWord(12+i*27+18,2)){debug("P501 test failure line%d",__LINE__);return false;}for(uint i:{2U,300U,303U,306U,309U,312U,301U,302U,602U,603U,604U})if(!badWord(12+729+i,0xffffffffU)){debug("P501 test failure line%d",__LINE__);return false;}if(!badWord(12+729+605,6)||!badWord(12+729+606,now+1)){debug("P501 test failure line%d",__LINE__);return false;}for(uint i:{0U,50U,100U,101U,102U,110U})if(!badWord(12+729+607+i,123456)){debug("P501 test failure line%d",__LINE__);return false;}for(uint i:{0U,1U,2U,3U,4U})if(!badWord(12+729+607+118+i,123456)){debug("P501 test failure line%d",__LINE__);return false;}for(uint i:{1U,2U,4U,7U,8U,9U,10U,11U,12U,19U,22U})if(!badWord(12+24*27+i,123456)){debug("P501 test failure line%d",__LINE__);return false;}
 if(!badWord(12+729+300,6)){debug("P501 test failure line%d",__LINE__);return false;}
 _pendingImage.free();_pendingImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP501()){debug("P501 test failure line%d",__LINE__);return false;}debug("Astronomica P501 rejection verification: PASS (5896 truncations, 5896 corruptions, %u invalid states, extended atomic state)",invalid);

 for(uint repeat=0;repeat<2;++repeat){if(!restore(fixture)||!roundtrip()||!restore(fixture)){debug("P501 test failure line%d",__LINE__);return false;}_runner.defineValue(0,20,repeat);Common::Array<byte>branch;if(!snapshot(branch)||!fullFuture()){debug("P501 test failure line%d",__LINE__);return false;}const uint32 expected=fingerprint(true);if(!restore(branch)||!fullFuture()||fingerprint(true)!=expected){debug("P501 test failure line%d",__LINE__);return false;}++futures;++successors;}
 if(!restore(fixture)){debug("P501 test failure line%d",__LINE__);return false;}const uint32 beforeExit=_puzzlesCompleted;if(!press(1)){debug("P501 test failure line%d",__LINE__);return false;}advance(3000);int32 solved=0;if(_place!=388||!_runner.getValue(0,20,solved)||solved||_puzzlesCompleted!=beforeExit){debug("P501 test failure line%d",__LINE__);return false;}++futures;
 if(!restore(fixture)||saveGameState(26,"P501 continuation regression").getCode()!=Common::kNoError){debug("P501 test failure line%d",__LINE__);return false;}debug("Astronomica P501 slot fingerprint: %08x",fingerprint());if(!fullFuture()){debug("P501 test failure line%d",__LINE__);return false;}
 if(worlds!=63||backgrounds!=127||historyChecks!=15||strikeChecks!=3||pollCases!=24||inputChecks!=8||pauseChecks!=1||!histories||!dormant||!ordinary){debug("P501 test failure line%d",__LINE__);return false;}
 debug("Astronomica P501 ready coverage: PASS (6 world states, 7 background identities, %u cross-world histories, %u strike histories, %u input windows, %u Vesta pauses, %u poll timer cases)",historyChecks,strikeChecks,inputChecks,pauseChecks,pollCases);
 debug("Astronomica P501 future coverage: PASS (%u successor checks, %u outcome checks)",successors,futures);
 debug("Astronomica P501 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP501Puzzle() {
 bool ok = verifyBallMotion();
 debug("Astronomica P501 original motion verification: %s (nine original trajectories and timer boundaries)",ok ? "PASS" : "FAIL");
 if (!loadPlace(501)) return false;
 uint32 stateHash = 2166136261U;
 const int distances[] = {-31,-30,-29,0,40,41,59,60,99,100};
 for (int mode = 0; mode < 5; ++mode) for (int scenario = 0; scenario < 6; ++scenario)
  for (int state = 0; state < 4; ++state) for (int misses = 0; misses < 3; ++misses)
   for (uint distance = 0; distance < ARRAYSIZE(distances); ++distance) {
    _runner.clear(); _ball = BallMotion(); _lastSound = -1;
    _runner.defineValue(1,0,scenario); _runner.defineValue(1,1,state);
    _runner.defineValue(1,2,misses); _runner.defineValue(1,3,0);
    _scene.sprites[25].x = 157; _scene.sprites[24].renderX = 157+distances[distance]; _scene.sprites[24].renderY = 182;
    onBall(mode,0);
    int32 values[7] = {}; for (int i = 0; i < 4; ++i) _runner.getValue(1,i,values[i]);
    values[4] = _runner.pendingCount(); values[5] = _lastSound; values[6] = _ball.scenario;
    for (uint i = 0; i < ARRAYSIZE(values); ++i) for (int byte = 0; byte < 4; ++byte)
     stateHash = (stateHash ^ ((uint32(values[i]) >> (8*byte)) & 255))*16777619U;
   }
 const bool statesOK = stateHash == 0x63b6a619U;
 debug("Astronomica P501 original state comparison: %s (3600 transitions, generated command counts, sounds and callback selection; %08x)",statesOK ? "PASS" : "FAIL",stateHash);
 ok = statesOK && ok;
 _runner.clear(); _runner.resetGlobals();
 for (int route = 0; route < 11; ++route) {
  if (!loadPlace(501)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0; bool good = true;
  _runner.defineValue(0,20,route == 1);
  auto step = [&]() { runScriptsAt(now); animateSpritesAt(now); now += 10; };
  auto wait = [&](uint duration) { const uint32 until = now+duration; while (_place == 501 && now < until) step(); };
  auto value = [&](int id) { int32 v = -1; _runner.getValue(1,id,v); return v; };
  auto press = [&](int index) {
   if (_place != 501) return false;
   const int x = _scene.sprites[index].x+2, y = _scene.sprites[index].y+2;
   if (_runner.clicksBlocked() || spriteAt(x,y) != index) { debug("P501 rejected click %d blocked %d actual %d",index,int(_runner.clicksBlocked()),spriteAt(x,y)); return false; }
   if (!_runner.canRun(_scene.sprites[index].click,true)) return false;
   clickAtTime(x,y,now); step(); return true;
  };
  good = _runner.enqueueStartup(_scene.scripts,0,true) == 1;
  const int scenario = route == 6 ? 1 : route == 7 ? 5 : route == 8 ? 3 : route == 9 ? 2 : 4;
  const int buttons[] = {0,10,7,8,11,9};
  good = press(buttons[scenario]) && good; wait(1200);
  good = value(0) == scenario && good;
  if (route == 10) { good = press(1) && good; wait(2000); }
  else if (route == 4 || route == 5) {
   for (int attempt = 0; attempt < 3; ++attempt) {
    good = press(4) && good;
    if (route == 5) {
     for (int tick = 0; tick < 400 && value(1) != 1; ++tick) step();
     good = press(5) && good;
    }
    wait(8500);
    good = value(2) == (attempt == 2 ? 0 : attempt+1) && good;
   }
   good = value(0) == 0 && value(1) == 0 && !_scene.sprites[25].visible && !_scene.sprites[26].visible && _loopSound == 0 && good;
  } else {
   good = press(4) && good;
   if (scenario == 2 || scenario == 3) {
    wait(14000); good = value(3) == 0 && !_scene.sprites[24].visible && good;
   } else {
    bool window = false;
    for (int tick = 0; tick < 500 && _place == 501; ++tick) {
     if (value(1) == 1 && _scene.sprites[24].autoMove && _scene.sprites[24].renderX-_scene.sprites[25].x <= 75) { window = true; break; }
     step();
    }
    good = window && press(5) && good; wait(100);
    good = value(1) == 2 && _ball.scenario == scenario && value(2) == 0 && good;
    if (route < 2) {
     bool returned = false;
     for (int tick = 0; tick < 1600 && _place == 501; ++tick) {
      if (_ball.side == 0 && _scene.sprites[24].renderX >= 100) { returned = true; break; }
      step();
     }
     good = returned && press(6) && good; wait(18000);
     int32 solved = 0; good = _place == 388 && _runner.getValue(0,20,solved) && solved == 1 && _puzzlesCompleted == completed+uint(route == 0) && good;
    } else if (route == 2) {
     good = press(6) && good; wait(3000); good = value(1) == 0 && value(3) == 0 && !_scene.sprites[24].visible && good;
    } else {
     wait(20000); good = value(3) == 0 && !_scene.sprites[24].visible && good;
     if (route == 3) good = value(1) == 0 && good;
    }
   }
  }
  if (route >= 2 && route != 10) { good = press(1) && good; wait(2000); }
  good = _place == 388 && good;
  debug("Astronomica P501 route %d: %s",route,good ? "PASS" : "FAIL"); ok = good && ok;
 }
 debug("Astronomica P501 interaction verification: %s (five worlds, hit/catch, success/repeat, missed hits, serve/return timeouts, voluntary exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyProbeSaves() {
 ConfMan.setBool("astronomica_verify",false);
 uint32 now = 0; uint boundaries=0,ordinary=0,dormant=0,failed=0,calendar=0,busy=0;
 auto sync = [&]() { _clockPaused=true; _pauseStarted=now; _pausedMillis=0; };
 auto tick = [&]() { sync(); runScriptsAt(now); animateSpritesAt(now); now+=30; sync(); };
 auto settle = [&]() { for(uint i=0;i<40;++i) tick(); Common::Array<uint32> st; uint32 since; for(uint i=0;i<4 && !_runner.exportProbePollState(st,since);++i) tick(); if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}_mixer->stopHandle(_soundHandle);} return _place==522; };
 auto snapshot = [&](Common::Array<byte> &data) { sync(); Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES); if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=4472) {debug("Probe test rejected line %d",__LINE__);return false;} data.resize(out.size()); memcpy(&data[0],out.getData(),out.size()); return true; };
 auto restore = [&](const Common::Array<byte> &data) { _pauseStarted=0x23450000U; Common::MemoryReadStream in(&data[0],data.size()); const bool ok=loadGameStream(&in).getCode()==Common::kNoError; if(ok&&scriptClock()!=READ_LE_UINT32(&data[16])) {debug("Probe test rejected line %d",__LINE__);return false;} if(ok) now=scriptClock(); sync(); return ok; };
 auto fingerprint = [&]() { uint32 hash=2166136261U; auto add=[&](uint32 v){hash=(hash^v)*16777619U;}; add(_place);add(_previousPlace);add(_puzzlesCompleted);add(_comet.frame);add(_comet.previousFrame); add(_runner.probeDiagnosticHash(false));for(const Sprite &s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);} add(_probe.year);add(_probe.yearArmed);add(_probe.specialHit);add(_probe.flying);add(_probe.expired);for(int i=0;i<3;++i){add(_probe.widths[i]);add(_probe.heights[i]);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return hash; };
 auto roundtrip = [&](uint duration) { Common::Array<uint32> ready;uint32 poll;if(!_runner.exportProbePollState(ready,poll)){if(canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}runScriptsAt(now);} Common::Array<byte> saved,again;sync();if(!snapshot(saved)){debug("Probe rejected at %u year%d month%d pending%u assets%d",now,_probe.year,_scene.sprites[8].selectedFrame,_runner.pendingCount(),_probeAssetsValid);{debug("Probe test rejected line %d",__LINE__);return false;}}const uint32 before=fingerprint(),savedNow=now;for(uint t=0;t<duration;t+=30)tick();if(!_runner.exportProbePollState(ready,poll))runScriptsAt(now);const uint32 after=fingerprint(),afterNow=now;if(!loadPlace(117)||!restore(saved)||now!=savedNow||fingerprint()!=before||!snapshot(again)||again!=saved){debug("Probe test rejected line %d",__LINE__);return false;}for(uint t=0;t<duration;t+=30)tick();if(!_runner.exportProbePollState(ready,poll))runScriptsAt(now);if(now!=afterNow||fingerprint()!=after){debug("Probe test rejected line %d",__LINE__);return false;}Common::Array<uint32> st;uint32 since;_runner.exportProbePollState(st,since);++boundaries;ordinary+=!st[603];dormant+=st[603]!=0;return true; };
 auto press=[&](int x,int y,int index){sync();if(spriteAt(x,y)!=index||_runner.clicksBlocked()){debug("Probe test rejected line %d",__LINE__);return false;}clickAtTime(x,y,now);return settle();};
 auto continuation=[&]() { for(uint i=0;i<4500&&_place==522;++i){if(_probe.year==1992&&_scene.sprites[8].selectedFrame==8)break;tick();}if(_probe.year!=1992||!press(452,394,13)){debug("Probe test rejected line %d",__LINE__);return false;}for(uint i=0;i<1800&&_place==522;++i)tick();int32 solved=-1;return _place==388&&_runner.getValue(0,38,solved)&&solved==1;};
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==15){now=scriptClock();sync();debug("Astronomica probe slot fingerprint: %08x",fingerprint());const bool ok=canSaveProbe()&&roundtrip(240)&&continuation();debug("Astronomica probe startup save: %s (slot15, failed return and natural next success)",ok?"PASS":"FAIL");return ok;}
 for(uint route=0;route<2;++route){if(route==1&&loadGameState(99).getCode()!=Common::kNoError){debug("Probe test rejected line %d",__LINE__);return false;}_runner.resetGlobals();now=0;sync();if(!loadPlace(522)){debug("Probe test rejected line %d",__LINE__);return false;}if(_runner.enqueueStartup(_scene.scripts,now,true)!=11||!settle()){debug("Probe test rejected line %d",__LINE__);return false;}
 if(!_runner.verifyProbePollSnapshots()){debug("Probe test rejected line %d",__LINE__);return false;}
 if(!roundtrip(240)){debug("Probe test rejected line %d",__LINE__);return false;}
 const int buttons[4][2]={{306,398},{332,377},{360,377},{385,397}};
 for(int c=0;c<4;++c)if(!press(buttons[c][0],buttons[c][1],c+4)||!roundtrip(240)){debug("Probe test rejected line %d",__LINE__);return false;}
 for(uint t=0;t<4500&&_place==522;++t){const int yr=_probe.year,month=_scene.sprites[8].selectedFrame;tick();if(_probe.year!=yr||_scene.sprites[8].selectedFrame!=month){if(!roundtrip(240)){debug("Probe test rejected line %d",__LINE__);return false;}++calendar;}if(_probe.year==1991&&_scene.sprites[8].selectedFrame==8)break;}
 if(!press(452,394,13)||!_probe.flying||canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}++busy;
 for(uint t=0;t<1200&&_probe.flying;++t){tick();if(_probe.flying){if(canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}++busy;}}
 if(_probe.flying||!settle()||!roundtrip(240)){debug("Probe test rejected line %d",__LINE__);return false;}++failed;
 }

 Common::Array<byte> fixture;
 if (!snapshot(fixture)) {debug("Probe test rejected line %d",__LINE__);return false;}

 const uint32 originalClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint32 age:{0U,1U,199U,200U,201U,210U,1000U}){
  Common::Array<byte> timed=fixture;const uint32 delta=clock-originalClock;
  WRITE_LE_UINT32(&timed[16],clock);WRITE_LE_UINT32(&timed[8+8*4],clock-age);
  for(uint i=14;i<=16;++i){const uint at=8+(24+i*27+9)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);if(i<16){const uint f=8+(24+i*27+8)*4;WRITE_LE_UINT32(&timed[f],READ_LE_UINT32(&timed[f])+delta);}}
  const uint loadAt=8+(24+486+601)*4;WRITE_LE_UINT32(&timed[loadAt],READ_LE_UINT32(&timed[loadAt])+delta);
  uint32 checksum=2166136261U;for(uint at=8;at<timed.size()-4;at+=4)checksum=(checksum^READ_LE_UINT32(&timed[at]))*16777619U;WRITE_LE_UINT32(&timed[timed.size()-4],checksum);
  if(!restore(timed)||!roundtrip(240))return false;
 }
 if(!restore(fixture))return false;
 debug("Astronomica probe caller poll epochs: PASS (14 original/wrap save and successor cases)");

 // A real original foreground voice must finish naturally.
 if (!playSound(1,now) || !_mixer->isSoundHandleActive(_soundHandle) || canSaveProbe()) {debug("Probe test rejected line %d",__LINE__);return false;}
 const uint32 voiceStart=_system->getMillis();
 while (_mixer->isSoundHandleActive(_soundHandle) && _system->getMillis()-voiceStart<120000) { if(canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}_system->delayMillis(10); }
 const uint32 voiceWait=_system->getMillis()-voiceStart;
 if(_mixer->isSoundHandleActive(_soundHandle)||!voiceWait||!canSaveProbe()||!roundtrip(240)){debug("Probe test rejected line %d",__LINE__);return false;}
 debug("Astronomica probe natural voice end: PASS (%u ms, no stopHandle)",voiceWait);
 _loopSound=0;_loopEnabled=true;
 if(!playSound(0,now,true)||!_mixer->isSoundHandleActive(_soundHandle)||!canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}
 Common::Array<byte> music;if(!snapshot(music)||!loadPlace(117)){debug("Probe test rejected line %d",__LINE__);return false;}const uint sounds=_soundsStarted;
 if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)){debug("Probe test rejected line %d",__LINE__);return false;}
 Common::Array<byte> again;if(!snapshot(again)||again!=music){debug("Probe test rejected line %d",__LINE__);return false;}
 debug("Astronomica probe Music restart: PASS (one ambient start)");
 _mixer->stopHandle(_soundHandle);if(!restore(fixture)){debug("Probe test rejected line %d",__LINE__);return false;}
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}
 Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size()){debug("Probe test rejected line %d",__LINE__);return false;}
 _mixer->pauseHandle(_soundHandle,true);
 _pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="probe-atomic-image";_displayedImageName="probe-atomic-display";
 auto atomic=[&](){uint32 h=fingerprint();h=(h^_runner.probeDiagnosticHash(true))*16777619U;auto add=[&](uint32 v){h=(h^v)*16777619U;};for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_probeAssetsValid),uint32(_runner.pendingCount()),uint32(_runner.clicksBlocked()),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle)})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));return h;};
 const uint32 unchanged=atomic();const void *pendingPixels=_pendingImage.getPixels();
 auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels){debug("Probe test rejected line %d",__LINE__);return false;}return true;};
 for(uint i=0;i<fixture.size();++i){Common::Array<byte> bad;bad.resize(i);if(i)memcpy(&bad[0],&fixture[0],i);Common::MemoryReadStream in(i?&bad[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels){debug("Probe test rejected line %d",__LINE__);return false;}}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte> bad=fixture;bad[i]^=1;if(!reject(bad)){debug("Probe test rejected line %d",__LINE__);return false;}}
 uint invalid=0;auto invalidWord=[&](uint index,uint32 value){Common::Array<byte> bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);uint32 h=2166136261U;for(uint at=8;at<bad.size()-4;at+=4)h=(h^READ_LE_UINT32(&bad[at]))*16777619U;WRITE_LE_UINT32(&bad[bad.size()-4],h);if(!reject(bad)){debug("Probe test rejected line %d",__LINE__);return false;}++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,9U,10U,11U,12U,13U,14U,15U,16U,17U,18U,19U,20U,21U,22U,23U})if(!invalidWord(index,index==3?538U:index==4?1U:0xffffffffU)){debug("Probe test rejected line %d",__LINE__);return false;}
 for(uint i=0;i<18;++i)if(!invalidWord(24+i*27+18,2)){debug("Probe test rejected line %d",__LINE__);return false;}
 if(!invalidWord(24+14*27+11,65538)||!invalidWord(24+14*27+9,now+1)||!invalidWord(24+486+301,6)||!invalidWord(24+486+303,1)||!invalidWord(24+486+10,1)){debug("Probe test rejected line %d",__LINE__);return false;}
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_mixer->stopHandle(_soundHandle);
 if(!restore(fixture)||!canSaveProbe()){debug("Probe test rejected line %d",__LINE__);return false;}
 debug("Astronomica probe rejection verification: PASS (4472 truncations, 4472 corruptions, %u invalid states, extended atomic state)",invalid);


 if(!restore(fixture)||!_runner.defineValue(0,38,1)||!roundtrip(240))return false;
 const uint completedBeforeRepeat=_puzzlesCompleted;if(!continuation()||_puzzlesCompleted!=completedBeforeRepeat)return false;
 if(!restore(fixture)||!roundtrip(240))return false;
 const uint completedBeforeExpiry=_puzzlesCompleted;for(uint i=0;i<5000&&_place==522;++i)tick();int32 expiredSolved=-1;if(_place!=388||!_runner.getValue(0,38,expiredSolved)||expiredSolved||_puzzlesCompleted!=completedBeforeExpiry)return false;
 if(!restore(fixture))return false;
 debug("Astronomica probe future outcomes: PASS (restored repeat success and natural year2003 expiry)");

 if(saveGameState(15,"Probe continuation regression").getCode()!=Common::kNoError){debug("Probe test rejected line %d",__LINE__);return false;}debug("Astronomica probe slot fingerprint: %08x",fingerprint());
 if(!continuation()){debug("Probe test rejected line %d",__LINE__);return false;}
 debug("Astronomica probe saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u failed return boundaries, %u calendar edges, %u poll timing cases, %u flight rejections)",boundaries,failed,dormant,ordinary,failed,calendar,14U,busy);
 return true;
}

bool AstronomicaEngine::verifyProbeBoundaries() {
 uint observations = 0;
 bool ok = verifyProbeMotion();
 debug("Astronomica P522 original motion verification: %s (4128 calendar steps, six original launches, timer boundaries)",ok ? "PASS" : "FAIL");
 if (!ok) return false;
 for (int route = 0; route < 4; ++route) {
  _runner.resetGlobals(); if (route == 1) _runner.defineValue(0,38,1);
  if (!loadPlace(522)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto record = [&](const char *tag) {
   if (_place != 522 || _scene.sprites.size() != 18) return;
   int32 selector = -1,state = -1; _runner.getValue(1,0,selector); _runner.getValue(1,1,state);
   debug("Probe audit boundary: %u %d %s %u %d %d %d %d %u %u %u %u %d %d %d %d %d %d %u %u %u %u %u %u %08x %08x",
    observations,route,tag,now,_place,selector,state,_probe.year,uint(_probe.yearArmed),uint(_probe.specialHit),uint(_probe.flying),uint(_probe.expired),
    _probe.widths[0],_probe.heights[0],_probe.widths[1],_probe.heights[1],_probe.widths[2],_probe.heights[2],
    _runner.pendingCount(),uint(_runner.idle()),uint(_runner.scriptsIdle()),uint(_runner.clicksBlocked()),
    uint(_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound),_puzzlesCompleted,screenRGBHash(_screen,480),screenRGBHash(_background,480));
   for (uint i = 0; i < 18; ++i) {
    Common::Array<uint32> words; p526SpriteWords(_scene.sprites[i],words);
    Common::String line = Common::String::format("Probe audit sprite: %u %u %u",observations,i,words.size());
    for (uint32 word : words) line += Common::String::format(" %d",int32(word));
    debug("%s",line.c_str());
   }
   ++observations;
  };
  record("before-startup");

  auto step = [&]() {
   const int year = _probe.year; const bool armed = _probe.yearArmed,flying = _probe.flying,special = _probe.specialHit;
   int32 before = -1; _runner.getValue(1,1,before);
   runScriptsAt(now); animateSpritesAt(now); now += 30;
   if (_place != 522) { debug("Probe audit departure: %d %u %d %u",route,now,_place,_puzzlesCompleted); return; }
   int32 after = -1; _runner.getValue(1,1,after);
   if (now <= 360) record("startup-tick");
   else if (year != _probe.year || armed != _probe.yearArmed) record("calendar-edge");
   else if (flying != _probe.flying || special != _probe.specialHit || before != after) record("flight-transition");
  };
  auto wait = [&](uint duration) { const uint32 until = now+duration; while (_place == 522 && now < until) step(); };
  auto press = [&](int x, int y, int index) {
   if (_place != 522 || _runner.clicksBlocked() || spriteAt(x,y) != index) { debug("P522 rejected test click %d,%d expected %d actual %d blocked %d",x,y,index,spriteAt(x,y),int(_runner.clicksBlocked())); return false; }
   clickAtTime(x,y,now); wait(600); record("after-control"); return true;
  };
  auto window = [&](int year, int month) {
   for (int tick = 0; tick < 4500 && _place == 522; ++tick) {
    if (_probe.year == year && _scene.sprites[8].selectedFrame == month && !_runner.clicksBlocked()) { record("launch-window"); return true; }
    step();
   }
   return false;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 11 && ok; wait(600); record("after-startup");
  if (!_runner.verifyProbePollSnapshots()) return false;
  int32 value = -1;
  ok = _runner.getValue(1,0,value) && value == 2 && _probe.widths[0] == 54 && _probe.widths[1] == 40 && _probe.widths[2] == 43 && ok;
  const int buttons[4][2] = {{306,398},{332,377},{360,377},{385,397}};
  for (int choice = 1; choice <= 4; ++choice) {
   ok = press(buttons[choice-1][0],buttons[choice-1][1],choice+3) && _runner.getValue(1,0,value) && value == choice && ok;
   for (int button = 0; button < 4; ++button) ok = _scene.sprites[button+4].selectedFrame == int(button == choice-1) && ok;
  }
  if (route == 3) ok = press(24,417,1) && ok;
  else if (route == 2) wait(150000);
  else {
   if (route == 0) {
    ok = window(1991,8) && press(452,394,13) && ok;
    for (int tick = 0; tick < 1000 && _place == 522; ++tick) {
     _runner.getValue(1,1,value); if (value == 0) break; step();
    }
    ok = _place == 522 && value == 0 && !_scene.sprites[16].visible && !_probe.flying && ok; record("failed-return");
   }
   ok = window(route == 0 ? 1992 : 1994,route == 0 ? 8 : 10) && press(452,394,13) && ok;
   for (int tick = 0; tick < 1800 && _place == 522; ++tick) step();
  }
  ok = _place == 388 && _runner.getValue(0,38,value) && value == int(route < 2) &&
   _puzzlesCompleted == completed+uint(route == 0) && ok;
  debug("Astronomica P522 route %d: %s",route,ok ? "PASS" : "FAIL");
 }
 debug("Astronomica P522 interaction verification: %s (four controls, failed launch/recovery, success/repeat, year2003 timeout, voluntary exit)",ok ? "PASS" : "FAIL");
 debug("Astronomica probe boundary audit: %s (%u observations, four native routes; no save support)",ok ? "PASS" : "FAIL",observations);
 return ok;
}

bool AstronomicaEngine::verifyP522Puzzle() {
 bool ok = verifyProbeMotion();
 debug("Astronomica P522 original motion verification: %s (4128 calendar steps, six original launches, timer boundaries)",ok ? "PASS" : "FAIL");
 if (!ok) return false;
 for (int route = 0; route < 4; ++route) {
  _runner.resetGlobals(); if (route == 1) _runner.defineValue(0,38,1);
  if (!loadPlace(522)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto step = [&]() { runScriptsAt(now); animateSpritesAt(now); now += 30; };
  auto wait = [&](uint duration) { const uint32 until = now+duration; while (_place == 522 && now < until) step(); };
  auto press = [&](int x, int y, int index) {
   if (_place != 522 || _runner.clicksBlocked() || spriteAt(x,y) != index) { debug("P522 rejected test click %d,%d expected %d actual %d blocked %d",x,y,index,spriteAt(x,y),int(_runner.clicksBlocked())); return false; }
   clickAtTime(x,y,now); wait(600); return true;
  };
  auto window = [&](int year, int month) {
   for (int tick = 0; tick < 4500 && _place == 522; ++tick) {
    if (_probe.year == year && _scene.sprites[8].selectedFrame == month && !_runner.clicksBlocked()) return true;
    step();
   }
   return false;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 11 && ok; wait(600);
  int32 value = -1;
  ok = _runner.getValue(1,0,value) && value == 2 && _probe.widths[0] == 54 && _probe.widths[1] == 40 && _probe.widths[2] == 43 && ok;
  const int buttons[4][2] = {{306,398},{332,377},{360,377},{385,397}};
  for (int choice = 1; choice <= 4; ++choice) {
   ok = press(buttons[choice-1][0],buttons[choice-1][1],choice+3) && _runner.getValue(1,0,value) && value == choice && ok;
   for (int button = 0; button < 4; ++button) ok = _scene.sprites[button+4].selectedFrame == int(button == choice-1) && ok;
  }
  if (route == 3) ok = press(24,417,1) && ok;
  else if (route == 2) wait(150000);
  else {
   if (route == 0) {
    ok = window(1991,8) && press(452,394,13) && ok;
    for (int tick = 0; tick < 1000 && _place == 522; ++tick) {
     _runner.getValue(1,1,value); if (value == 0) break; step();
    }
    ok = _place == 522 && value == 0 && !_scene.sprites[16].visible && !_probe.flying && ok;
   }
   ok = window(route == 0 ? 1992 : 1994,route == 0 ? 8 : 10) && press(452,394,13) && ok;
   for (int tick = 0; tick < 1800 && _place == 522; ++tick) step();
  }
  ok = _place == 388 && _runner.getValue(0,38,value) && value == int(route < 2) &&
   _puzzlesCompleted == completed+uint(route == 0) && ok;
  debug("Astronomica P522 route %d: %s",route,ok ? "PASS" : "FAIL");
 }
 debug("Astronomica P522 interaction verification: %s (four controls, failed launch/recovery, success/repeat, year2003 timeout, voluntary exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP507Wheel() {
 uint32 hash = 2166136261U;
 for (int y = 35; y <= 295; ++y) for (int x = 314; x <= 574; ++x)
  hash = (hash ^ uint32(astrologyRegion(x,y,444,165,122,30)))*16777619U;
 bool ok = hash == 0xdf3f8b45U;
 const int points[12][2] = {{465,88},{501,108},{521,144},{521,186},{501,222},{465,242},
  {423,242},{387,222},{367,186},{367,144},{387,108},{423,88}};
 const char *names[] = {"sag","scorp","libra","virgo","leo","can","gem","taurus","aries","pisces","aquar","cap"};
 _runner.resetGlobals();
 for (uint route = 0; route < 2; ++route) {
  if (!loadPlace(507)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 5000 && _place == 507 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 10;
   }
   return _place != 507 || (!_runner.pendingCount() && !_runner.clicksBlocked());
  };
  auto check = [&](int region, bool highlighted) {
   int32 value = -1;
   if (!_runner.getValue(1,0,value) || value != region) return false;
   for (int s = 18; s <= 29; ++s) if (bool(_scene.sprites[s-1].visible) != (highlighted && s == 17+region)) return false;
   Graphics::Surface *caption = openBackgroundImage(names[region-1]);
   if (!caption) return false;
   bool match = !_pendingImage.getPixels();
   for (int y = 0; y < caption->h; ++y) for (int x = 0; x < caption->w; ++x)
    match = caption->getPixel(x,y) == _background.getPixel(65+x,354+y) && match;
   caption->free(); delete caption; return match;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 2 && settle() && ok;
  for (int s = 6; s <= 17; ++s) ok = _scene.sprites[s-1].selectedFrame == 0 && ok;
  for (int region = 1; region <= 12; ++region) {
   const uint sounds = _soundsStarted;
   ok = spriteAt(points[region-1][0],points[region-1][1]) == -1 && ok;
   clickAtTime(points[region-1][0],points[region-1][1],now);
   ok = settle() && check(region,true) && _lastSound == 6 && _soundsStarted == sounds+1 && ok;
  }
  for (int invalid = 0; invalid < 3; ++invalid) {
   const uint sounds = _soundsStarted;
   clickAtTime(invalid == 0 ? 444 : invalid == 1 ? 473 : 323,invalid == 2 ? 51 : 165,now);
   ok = settle() && check(12,false) && _soundsStarted == sounds && ok;
  }
  clickAtTime(474,165,now); runScriptsAt(now); now += 10;
  ok = _runner.clicksBlocked() && ok;
  clickAtTime(423,88,now); // A blocked click must not replace the original mouse position.
  ok = settle() && check(3,true) && ok;
  for (int toggle = 1; toggle >= 0; --toggle) {
   int32 value = -1; clickAtTime(184,228,now);
   ok = settle() && _runner.getValue(1,1,value) && value == toggle && _scene.sprites[29].visible == toggle && ok;
  }
  clickAtTime(route == 0 ? 546 : 24,route == 0 ? 271 : 417,now);
  int32 solved = -1;
  ok = settle() && _place == (route == 0 ? 508 : 388) && _puzzlesCompleted == completed &&
   _runner.getValue(0,24,solved) && solved == 0 && ok;
 }
 debug("Astronomica P507 interaction verification: %s (68121 original regions, twelve captions/highlights, annulus edges, blocked input, toggle, both exits)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP513Puzzle() {
 uint32 hash = 2166136261U;
 for (int scenario = 1; scenario <= 14; ++scenario) for (int setting = 1; setting <= 9; ++setting) {
  const int sound = ScriptRunner::photonAnswer(setting,scenario);
  hash = (hash ^ uint32(sound == -1))*16777619U;
  hash = (hash ^ uint32(sound < 0 ? 255 : sound))*16777619U;
 }
 bool ok = hash == 0xa8180d31U && verifyPhotonMotion();
 debug("Astronomica P513 original comparison: %s (126 answers, nine photon trajectories)",ok ? "PASS" : "FAIL");
 const int answer[] = {7,2,2,2,8,1,8,7,6,2,5,9,4,5};
 const int digits[9][3] = {{0,0,5},{0,1,1},{0,0,4},{0,3,0},{0,0,2},{1,0,0},{0,0,4},{0,5,0},{0,1,5}};
 const int result[] = {12,13,14,14,15,15,16,16,17};
 uint allScenarios = 0;
 for (uint route = 0; route < 5; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(113+route);
  if (route == 2) _runner.defineValue(0,29,1);
  if (!loadPlace(513)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 5000 && _place == 513 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 10;
   }
   return _place != 513 || (!_runner.pendingCount() && !_runner.clicksBlocked());
  };
  auto press = [&](int x, int y, int index) {
   if (_place != 513 || spriteAt(x,y) != index) return false;
   clickAtTime(x,y,now); return settle();
  };
  auto select = [&](int desired) {
   int32 setting = 0;
   for (int i = 0; i < 10; ++i) {
    if (!_runner.getValue(1,0,setting)) return false;
    if (setting == desired) return true;
    if (!press(281,setting < desired ? 362 : 418,setting < desired ? 6 : 7)) return false;
   }
   return false;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 4 && settle() && ok;
  if (route == 4) ok = press(24,417,1) && ok;
  else {
   if (route == 0) {
    int32 setting = -1;
    ok = press(281,418,7) && _runner.getValue(1,0,setting) && setting == 1 && ok;
    for (int level = 1; level <= 9; ++level) {
     ok = select(level) && press(335,411,5) && ok;
     for (uint pass = 0; pass < 400 && _scene.sprites[31].autoMove; ++pass) { animateSpritesAt(now); now += 10; }
     ok = !_scene.sprites[31].visible && !_scene.sprites[31].autoMove && _scene.sprites[result[level-1]-1].visible && ok;
     for (int d = 0; d < 3; ++d) ok = _scene.sprites[d+8].selectedFrame == digits[level-1][d] && ok;
    }
    ok = press(281,362,6) && _runner.getValue(1,0,setting) && setting == 9 && ok;
   }
   uint seen = 0; int attempts = 0;
   while (_place == 513 && attempts < 15) {
    int32 scenario = 0;
    if (!_runner.getValue(1,1,scenario) || scenario < 1 || scenario > 14) return false;
    ok = !(seen & (1U << (scenario-1))) && ok; seen |= 1U << (scenario-1); allScenarios |= seen;
    const bool correct = route == 0 || route == 2 || (route == 1 && attempts < 6);
    int setting = answer[scenario-1];
    if (!correct) setting = setting == 9 ? 8 : setting+1;
    ok = select(setting) && press(335,369,4) && ok;
    if (!correct && _place == 513) ok = _lastSound == ScriptRunner::photonAnswer(setting,scenario) && ok;
    ++attempts;
   }
   ok = attempts == (route == 1 ? 14 : route == 3 ? 10 : 7) && ok;
   if (route == 1) ok = seen == 0x3fff && ok;
   debug("Astronomica P513 route %u attempts %d: %s",route,attempts,ok ? "PASS" : "FAIL");
  }
  int32 solved = -1;
  ok = _place == 197 && _runner.getValue(0,29,solved) && solved == int(route < 3) &&
   _puzzlesCompleted == completed+uint(route < 2) && ok;
 }
 ok = allScenarios == 0x3fff && ok;
 if (!loadPlace(513)) return false;
 const uint sounds = _soundsStarted, completed = _puzzlesCompleted;
 ok = onPuzzleSuccess(1234) == 1234 && _soundsStarted == sounds && _puzzlesCompleted == completed+1 && ok;
 debug("Astronomica P513 interaction verification: %s (fourteen scenarios, seven correct/all selected/ten errors, nine animations, limits, repeated success, silent counter, unsolved exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyRendezvousSaves() {
 ConfMan.setBool("astronomica_verify",false);
 uint32 now=0;uint boundaries=0,prelaunch=0,launched=0,ordinary=0,dormant=0,histories=0,busy=0,failed=0,successors=0,futures=0,settingsMask=0,timerCases=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto settle=[&](){
  for(uint n=0;n<3000&&_place==514&&!_runner.scriptsIdle();++n){if(canSaveRendezvous())return false;++busy;tick();}
  if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(_place==514){if(canSaveRendezvous())return false;++busy;}_mixer->stopHandle(_soundHandle);}
  return _place!=514||_runner.scriptsIdle();
 };
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=4632)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());const bool ok=loadGameStream(&in).getCode()==Common::kNoError;if(ok&&scriptClock()!=READ_LE_UINT32(&data[16]))return false;if(ok)now=scriptClock();sync();return ok;};
 auto fingerprint=[&](bool destination=false){uint32 h=2166136261U;auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_place);add(_previousPlace);add(_puzzlesCompleted);add(_comet.frame);add(_comet.previousFrame);if(destination){Common::Array<uint32>state;if(!_runner.exportPersistentState(state))return uint32(0);for(uint i=0;i<state.size();++i)if(i!=601)add(state[i]);}else add(_runner.probeDiagnosticHash(false));for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto roundtrip=[&](uint duration){
  Common::Array<byte>saved,again;if(!snapshot(saved)){debug("Rendezvous snapshot rejected: %u launched%u speed%u",now,uint(_scene.sprites[18].autoMove),uint(_scene.sprites[6].selectedFrame));return false;}
  const uint32 before=fingerprint(),savedNow=now;for(uint t=0;t<duration;t+=10)tick();const uint32 after=fingerprint(),afterNow=now;
  if(!loadPlace(117)||!restore(saved)||now!=savedNow||fingerprint()!=before||!snapshot(again)||again!=saved){debug("Rendezvous restored state mismatch");return false;}
  for(uint t=0;t<duration;t+=10)tick();if(now!=afterNow||fingerprint()!=after){debug("Rendezvous successor mismatch");return false;}
  Common::Array<uint32>state;_runner.exportPersistentState(state);++boundaries;++successors;prelaunch+=!state[306];launched+=state[306]!=0;ordinary+=!state[603];dormant+=state[603]!=0;settingsMask|=1U<<state[315];histories+=_scene.sprites[19].renderX!=272||_scene.sprites[19].renderY!=4;return true;
 };
 auto press=[&](int x,int y,int index){sync();if(spriteAt(x,y)!=index||_runner.clicksBlocked())return false;clickAtTime(x,y,now);return settle();};
 auto select=[&](int desired){for(uint n=0;n<20;++n){int32 speed=-1;if(!_runner.getValue(1,5,speed))return false;if(speed==desired)return true;if(!press(speed<desired?310:234,416,speed<desired?5:4))return false;}return false;};
 auto overlapping=[&](){const Sprite&t=_scene.sprites[16],&s=_scene.sprites[18];return t.renderX<=s.renderX+56&&t.renderX+52>=s.renderX&&t.renderY<=s.renderY+56&&t.renderY+54>=s.renderY;};
 auto future=[&](uint mode){
  const uint completed=_puzzlesCompleted;if(mode==3){if(!press(24,417,1))return false;}
  else{if(!select(mode==0?5:mode==1?8:15))return false;
   for(uint n=0;n<15000&&_place==514;++n){if(mode<2&&_runner.scriptsIdle()&&overlapping()){if(!press(495,372,14))return false;}else tick();}
  }
  int32 solved=-1;return _place==388&&_runner.getValue(0,30,solved)&&solved==int(mode<2)&&_puzzlesCompleted==completed+uint(mode==0);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==16){
  now=scriptClock();sync();debug("Astronomica rendezvous slot fingerprint: %08x",fingerprint());
  const bool ok=canSaveRendezvous()&&roundtrip(130)&&future(0);debug("Astronomica rendezvous startup save: %s (slot16, failed docking and native next success)",ok?"PASS":"FAIL");return ok;
 }
 // Ordinary route is independent of the physical dormant fixture.
 _runner.resetGlobals();now=0;sync();if(!loadPlace(514)||_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle()||!roundtrip(130))return false;
 for(uint speed=1;speed<=15;++speed)if(!press(310,416,5)||!roundtrip(130))return false;
 if(!press(310,416,5)||!roundtrip(130)||!press(120,395,15)||!roundtrip(130))return false;
 for(uint speed=0;speed<15;++speed)if(!press(234,416,4)||!roundtrip(130))return false;
 // Rebuild the same original scene while retaining dormant variant/comet data.
 if(loadGameState(99).getCode()!=Common::kNoError)return false;
 _runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(77);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;
 now=1000;sync();if(!loadPlace(514)||_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle()||!roundtrip(130)||!press(120,395,15)||!roundtrip(130))return false;
 for(uint speed=1;speed<=15;++speed)if(!press(310,416,5)||!roundtrip(130))return false;
 if(!select(0)||!roundtrip(130))return false;
 // Choose a genuinely disjoint original position for the failed docking attempt.
 for(uint n=0;n<3000&&overlapping();++n)tick();
 if(overlapping()||!press(495,372,14)||_place!=514||!roundtrip(130))return false;++failed;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 // Active timer epochs are independent of orbit phase and selected speed.
 const uint32 savedClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{savedClock,0xfffffff0U})for(uint sprite:{13U,16U,18U}){
  const uint32 period=READ_LE_UINT32(&fixture[8+(10+sprite*27+22)*4]);
  for(uint32 age:{0U,1U,period-1,period,period+1}){
   Common::Array<byte>timed=fixture;const uint32 delta=clock-savedClock;WRITE_LE_UINT32(&timed[16],clock);
   for(uint i:{13U,16U,18U}){const uint at=8+(10+i*27+9)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}
   WRITE_LE_UINT32(&timed[8+(10+sprite*27+9)*4],clock-age);const uint at=8+(10+540+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);
   uint32 hash=2166136261U;for(uint j=8;j<timed.size()-4;j+=4)hash=(hash^READ_LE_UINT32(&timed[j]))*16777619U;WRITE_LE_UINT32(&timed[timed.size()-4],hash);
   if(!restore(timed)||!roundtrip(130))return false;++timerCases;
  }
 }
 if(!restore(fixture))return false;debug("Astronomica rendezvous timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 // A real foreground original narration finishes naturally, without stopHandle.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveRendezvous())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveRendezvous())return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSaveRendezvous()||!roundtrip(130))return false;
 debug("Astronomica rendezvous natural voice end: PASS (%u ms, no stopHandle)",waited);
 _loopSound=0;_loopEnabled=true;if(!playSound(0,now,true)||!_mixer->isSoundHandleActive(_soundHandle)||!canSaveRendezvous())return false;
 Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;
 if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||!snapshot(again)||again!=music)return false;
 debug("Astronomica rendezvous Music restart: PASS (one ambient start)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // Nonzero sentinels and paused native audio strengthen atomic rejection checks.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveRendezvous())return false;
 Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="rendezvous-atomic-image";_displayedImageName="rendezvous-atomic-display";
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));
  for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_rendezvousAssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);
  for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));return h;};
 const uint32 unchanged=atomic();const void*pixels=_pendingImage.getPixels();
 auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);uint32 hash=2166136261U;for(uint at=8;at<bad.size()-4;at+=4)hash=(hash^READ_LE_UINT32(&bad[at]))*16777619U;WRITE_LE_UINT32(&bad[bad.size()-4],hash);if(!reject(bad))return false;++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,8U,9U})if(!badWord(index,index==3?538U:index==4?1U:0xffffffffU))return false;
 for(uint i=0;i<20;++i)if(!badWord(10+i*27+18,2))return false;
 for(uint i=0;i<8;++i)if(!badWord(10+540+301+3*i,100))return false;
 for(uint i:{13U,16U,18U})if(!badWord(10+i*27+9,now+1))return false;
 if(!badWord(10+16*27+11,65538)||!badWord(10+540+315,16)||!badWord(10+540+318,1)||!badWord(10+540+321,1)||!badWord(10+540+303,0)||!badWord(10+540+309,52)||!badWord(10+540+2,0)||!badWord(10+19*27+5,0)||!badWord(10+17*27+2,270))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveRendezvous())return false;
 debug("Astronomica rendezvous rejection verification: PASS (4632 truncations, 4632 corruptions, %u invalid states, extended atomic state)",invalid);
 for(uint mode=0;mode<4;++mode){
  if(!restore(fixture))return false;if(mode==1)_runner.defineValue(0,30,1);if(!roundtrip(130))return false;Common::Array<byte>branch;if(!snapshot(branch))return false;
  if(!future(mode))return false;const uint32 expected=fingerprint(mode==0),expectedClock=now,expectedEnd=_lastSuccessEnd,expectedBlock=_lastBlockingSoundEnd,expectedScreen=screenRGBHash(_screen,480),expectedBackground=screenRGBHash(_background,480);Common::Array<uint32>expectedState,expectedSprites;_runner.exportPersistentState(expectedState);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,expectedSprites);
  if(!restore(branch)||!future(mode)||(mode?now!=expectedClock:(now-_lastSuccessEnd<3010||now-_lastSuccessEnd>=3020||expectedClock-expectedEnd<3010||expectedClock-expectedEnd>=3020))||fingerprint(mode==0)!=expected){debug("Rendezvous future outcome mismatch mode%u clock%u/%u successEnd%u/%u blockingEnd%u/%u hash%08x/%08x screen%08x/%08x bg%08x/%08x",mode,expectedClock,now,expectedEnd,_lastSuccessEnd,expectedBlock,_lastBlockingSoundEnd,expected,fingerprint(mode==0),expectedScreen,screenRGBHash(_screen,480),expectedBackground,screenRGBHash(_background,480));Common::Array<uint32>actualState,actualSprites;_runner.exportPersistentState(actualState);for(const Sprite&s:_scene.sprites)p526SpriteWords(s,actualSprites);for(uint i=0;i<MIN(expectedState.size(),actualState.size());++i)if(expectedState[i]!=actualState[i])debug("Rendezvous future runner%u: %u/%u",i,expectedState[i],actualState[i]);for(uint i=0;i<MIN(expectedSprites.size(),actualSprites.size());++i)if(expectedSprites[i]!=actualSprites[i])debug("Rendezvous future sprite%u field%u: %u/%u",i/27+1,i%27,expectedSprites[i],actualSprites[i]);return false;}++futures;++successors;
 }
 if(!restore(fixture)||saveGameState(16,"Rendezvous continuation regression").getCode()!=Common::kNoError)return false;
 debug("Astronomica rendezvous slot fingerprint: %08x",fingerprint());if(!future(0))return false;
 uint settings=0;for(uint i=0;i<16;++i)settings+=(settingsMask>>i)&1U;
 debug("Astronomica rendezvous motion coverage: PASS (%u prelaunch boundaries, %u launched boundaries, %u failed docking boundaries, %u speed settings, %u successor checks, %u future outcome checks)",prelaunch,launched,failed,settings,successors,futures);
 debug("Astronomica rendezvous saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP514Puzzle() {
 bool ok = verifyRendezvousMotion();
 debug("Astronomica P514 original motion verification: %s (two 1000-step x86 trajectories)",ok ? "PASS" : "FAIL");
 _runner.resetGlobals(); if (!loadPlace(514)) return false;
 uint32 collisionHash = 2166136261U;
 const int shipX[] = {150,200,295,400}, dx[] = {-53,-52,-37,-26,-1,0,56,57}, dy[] = {-55,-54,-27,-1,0,56,57};
 for (uint a = 0; a < ARRAYSIZE(shipX); ++a) for (uint b = 0; b < ARRAYSIZE(dx); ++b) for (uint c = 0; c < ARRAYSIZE(dy); ++c) {
  _scene.sprites[16].renderX = shipX[a]+dx[b]; _scene.sprites[16].renderY = 50+dy[c];
  _scene.sprites[18].renderX = shipX[a]; _scene.sprites[18].renderY = 50;
  collisionHash = (collisionHash ^ uint32(onRendezvous(3,0,0)))*16777619U;
 }
 ok = collisionHash == 0x1fc8c7fdU && ok;
 // Successful custom16 discards other pending commands while preserving
 // its own delayed continuation. Failed docking must keep those commands.
 for (int hit = 0; hit < 2; ++hit) {
  if (!loadPlace(514)) return false;
  _scene.sprites[16].renderX = hit ? 200 : 400; _scene.sprites[16].renderY = 50;
  _scene.sprites[18].renderX = 200; _scene.sprites[18].renderY = 50;
  Command dock; dock.opcode = 23; dock.args.push_back(16); dock.args.push_back(3);
  for (int i = 0; i < 4; ++i) dock.args.push_back(0);
  Command marker; marker.opcode = 32; marker.args.push_back(1); marker.args.push_back(0); marker.args.push_back(99); marker.delay = 500;
  Script docking; docking.push_back(dock); Command continuation = marker; continuation.args[1] = 1; continuation.args[2] = 7;
  continuation.delay = 100; docking.push_back(continuation);
  Script other; other.push_back(marker);
  ok = _runner.enqueue(docking,0,true) && _runner.enqueue(other,0,true) && ok;
  runScriptsAt(0); runScriptsAt(100); runScriptsAt(500);
  int32 v = -1; ok = _runner.getValue(1,0,v) && v == (hit ? 0 : 99) && ok;
  ok = _runner.getValue(1,1,v) && v == 7 && _runner.getValue(1,6,v) && v == hit && ok;
 }
 for (uint route = 0; route < 5; ++route) {
  _runner.resetGlobals(); if (route == 2) _runner.defineValue(0,30,1);
  if (!loadPlace(514)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 3000 && _place == 514 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 10;
   }
   return _place != 514 || (!_runner.pendingCount() && !_runner.clicksBlocked());
  };
  auto press = [&](int x, int y, int index) {
   if (_place != 514 || spriteAt(x,y) != index) return false;
   clickAtTime(x,y,now); return settle();
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 2 && settle() && ok;
  if (route == 4) ok = press(24,417,1) && _place == 388 && ok;
  else {
   ok = press(234,416,4) && ok;
   int32 setting = -1; ok = _runner.getValue(1,5,setting) && setting == 0 && ok;
   ok = press(120,395,15) && ok;
   const int speed = route == 0 ? 5 : route == 1 ? 8 : 15;
   for (int i = 0; i < speed; ++i) ok = press(310,416,5) && ok;
   if (speed == 15) { ok = press(310,416,5) && _runner.getValue(1,5,setting) && setting == 15 && ok; }
   ok = _scene.sprites[18].moveData[0] == 100-4*speed && _scene.sprites[13].moveData[0] == 1000-40*speed && ok;
   // An early attempt must not synthesize success. Later attempts use
   // ordinary input while the original movement continues on the clock.
   if (route < 3) {
    ok = press(495,372,14) && ok;
    int32 docked = -1; ok = _place == 514 && _runner.getValue(1,6,docked) && docked == 0 && ok;
   }
   const uint32 end = now+65000;
   while (_place == 514 && now < end) {
    if (route < 3 && !_runner.clicksBlocked() && !_runner.pendingCount()) {
     const Sprite &target = _scene.sprites[16], &ship = _scene.sprites[18];
     // Test a candidate when the two original rectangles overlap.
     const int x = ship.renderX, y = ship.renderY;
     if (target.renderX <= x+56 && target.renderX+52 >= x && target.renderY <= y+56 && target.renderY+54 >= y) {
      ok = press(495,372,14) && ok; continue;
     }
    }
    runScriptsAt(now); animateSpritesAt(now); now += 10;
   }
  }
  int32 solved = -1;
  ok = _place == 388 && _runner.getValue(0,30,solved) && solved == int(route < 3) &&
   _puzzlesCompleted == completed+uint(route < 2) && ok;
  debug("Astronomica P514 route %u: %s (P%d, solved %d)",route,ok ? "PASS" : "FAIL",_place,solved);
 }
 debug("Astronomica P514 interaction verification: %s (224 original collision cases, queue cancellation, three speeds, clamped controls, docking, fuel exhaustion, unsolved exit, repeated success)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyBuilderPuzzle() {
 bool ok = true; uint seen = 0;
 const uint32 seeds[] = {1,32,64,1,1,64};
 const int parts[5][11] = {{48,54,58,60,59,52,0},{46,47,53,58,57,56,45,44,50,0},
  {48,54,58,60,49,52,0},{48,54,58,45,43,51,0},{46,47,53,58,57,56,55,45,43,51,0}};
 for (uint route = 0; route < ARRAYSIZE(seeds); ++route) {
  const bool alternate = route >= 4;
  _runner.resetGlobals(); _runner.seedRandom(seeds[route]);
  if (route == 3) _runner.defineValue(0,31,1);
  if (!loadPlace(515)) return false;
  const uint completed = _puzzlesCompleted; uint32 now = 0;
  auto inGroup = [&]() { return _place == 515 || _place == 536; };
  auto settle = [&]() {
   for (uint pass = 0; pass < 5000 && inGroup() && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 50;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto boundary = [&](uint control) {
   if (!ConfMan.hasKey("astronomica_verify_builder_boundaries") || !ConfMan.getBool("astronomica_verify_builder_boundaries") || !inGroup()) return;
   Common::Array<uint32> state;
   if (!_runner.exportIdleState(state)) { debug("Builder audit nonidle: %u %u",route,control); return; }
   Common::String values;
   for (uint i = 0; i < 13; ++i) values += Common::String::format(" %d",int32(state[300+i*3]));
   debug("Builder audit boundary: %u %d %u %u%s",route,_place,control,now,values.c_str());
   for (uint i = 0; i < _scene.sprites.size(); ++i) {
    Common::Array<uint32> words; p526SpriteWords(_scene.sprites[i],words); values.clear();
    for (uint32 word : words) values += Common::String::format(" %d",int32(word));
    debug("Builder audit sprite: %u%s",i,values.c_str());
   }
   debug("Builder audit image: %s",_displayedImageName.c_str());
  };
  auto value = [&](int id, int expected) { int32 v = -1; return _runner.getValue(1,id,v) && v == expected; };
  auto press = [&](uint id) {
   if (!inGroup() || id < 1 || id > _scene.sprites.size()) return false;
   const Sprite &s = _scene.sprites[id-1]; int hitX = -1, hitY = -1;
   for (int y = MAX(0,int(s.renderY)); y < 480 && hitX < 0; y += 4)
    for (int x = MAX(0,int(s.renderX)); x < 640; x += 4)
     if (spriteAt(x,y) == int(id)-1) { hitX = x; hitY = y; break; }
   if (hitX < 0) { warning("Builder no exposed sprite %u",id); return false; }
   clickAtTime(hitX,hitY,now); const bool result = settle(); if (result) boundary(id); return result;
  };
  ok = _runner.enqueueStartup(_scene.scripts,now,true) == 7 && settle() && ok;
  boundary(0);
  if (alternate) ok = press(8) && value(0,7) && ok;
  for (int phase = 0; phase < (alternate ? 1 : 2) && inGroup(); ++phase) {
   if (phase) ok = _runner.enqueueStartup(_scene.scripts,now,true) == 7 && settle() && ok;
   if (phase) boundary(0);
   ok = press(5) && press(6) && value(2,2) && ok;
   int32 scenario = 0, required = 0;
   if (!_runner.getValue(1,1,scenario) || scenario < 1 || scenario > 5 ||
       !_runner.getValue(1,3,required)) return false;
   seen |= 1U << scenario;
   ok = (phase || alternate ? scenario >= 4 : scenario <= 3) && press(9) && ok;
   // Try an undersized rocket, remove its cap, then complete the same build.
   ok = press(13) && value(2,2) && press(14) && value(5,0) && ok;
   for (int stage = 1; stage < required-1; ++stage) ok = press(11) && ok;
   ok = press(13) && value(2,3) && ok;
   for (uint part = 0; parts[scenario-1][part]; ++part) ok = press(parts[scenario-1][part]) && ok;
   for (int flag = 7; flag <= 12; ++flag) ok = value(flag,1) && ok;
   ok = press(7) && value(2,4) && press(8) && ok;
   ok = _place == (phase || alternate ? 510 : 536) && ok;
   debug("Astronomica builder route %u phase %d: %s (scenario %d, P%d)",route,phase,ok ? "PASS" : "FAIL",scenario,_place);
  }
  int32 solved = 0;
  ok = _place == 510 && _runner.getValue(0,31,solved) && solved == int(!alternate) &&
   _puzzlesCompleted == completed+uint(route < 3) && ok;
 }
 ok = seen == 0x3e && ok;
 debug("Astronomica P515/P536 interaction verification: %s (five designs, original clicks, wrong size/recovery, two phases, repeated success, early Launch and P515 no-op success)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP512Puzzle() {
 uint32 hash = 2166136261U;
 for (int scenario = 1; scenario <= 6; ++scenario)
  for (int a = 0; a < 16; ++a) for (int b = 0; b < 16; ++b) for (int c = 0; c < 16; ++c) {
   const int sound = ScriptRunner::weatherAnswer(scenario,a,b,c);
   hash = (hash ^ uint32(sound == -1))*16777619U;
   hash = (hash ^ uint32(sound < 0 ? 255 : sound))*16777619U;
  }
 bool ok = hash == 0x685e2531U; // Original x86, probe_p512_weather.py.
 const int plus[] = {280,391,501}, minus[] = {204,315,425};
 const int requirements[6][3] = {{8,8,15},{15,8,8},{15,8,8},{15,8,8},{8,15,8},{8,15,15}};
 const uint32 starts[] = {0,150,1272,1456,1642,1834};
 for (int route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(137+route);
  if (route == 1) _runner.defineValue(0,28,1);
  if (!loadPlace(512) || !_movie) return false;
  Script invalidSeek; Command assign; assign.opcode = 32; assign.delay = -1;
  assign.args.push_back(1); assign.args.push_back(0); assign.args.push_back(9); invalidSeek.push_back(assign);
  Command seek; seek.opcode = 36; seek.delay = -1; seek.args.push_back(0);
  seek.args.push_back(_movie->getDuration().totalNumberOfFrames()); invalidSeek.push_back(seek);
  int32 untouched = -1;
  ok = !_runner.start(invalidSeek,0,true) && _runner.getValue(1,0,untouched) && untouched == 0 && ok;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 4000 && _place == 512; ++pass) {
    if (!_runner.pendingCount()) break;
    runScriptsAt(now); updateMovie(); now += 50;
   }
   return _place != 512 || (!_runner.pendingCount() && !_runner.clicksBlocked());
  };
  auto press = [&](int x, int y) { clickAtTime(x,y,now); return settle(); };
  auto select = [&](int local, int target) {
   int32 current = -1;
   for (uint pass = 0; pass <= 16; ++pass) {
    if (!_runner.getValue(1,local,current)) return false;
    if (current == target) return true;
    if (!press(current < target ? plus[local] : minus[local],417)) return false;
   }
   return false;
  };
  const uint frames = _movieFramesDrawn;
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 6 && settle() && ok;
  ok = _movieFramesDrawn > frames && _movieX == 160 && _movieY == 57 && ok;
  if (route == 2) {
   ok = press(24,417) && _place == 174 && ok;
  } else {
   uint seen = 0;
   for (int round = 0; round < 6 && _place == 512; ++round) {
    int32 scenario = 0, accepted = -1;
    if (!_runner.getValue(1,4,scenario) || scenario < 1 || scenario > 6) return false;
    ok = !(seen & (1U << scenario)) && _movieSegmentStart == starts[scenario-1] && ok;
    seen |= 1U << scenario;
    if (round == 0 && route == 0) {
     // The default zero settings are wrong for every scenario. The
     // rejected attempt must keep the same selection and not advance it.
     ok = press(537,374) && _runner.getValue(1,5,accepted) && accepted == 0 &&
      _lastSound == ScriptRunner::weatherAnswer(scenario,0,0,0) && ok;
     int32 unchanged = 0; ok = _runner.getValue(1,4,unchanged) && unchanged == scenario && ok;
     ok = press(minus[0],417) && _runner.getValue(1,0,unchanged) && unchanged == 0 && ok;
    }
    for (int local = 0; local < 3; ++local)
     ok = select(local,requirements[scenario-1][local] == 15 ? 15 : route == 0 ? 0 : 8) && ok;
    ok = press(537,374) && ok;
    debug("Astronomica P512 route %d round %d: %s (scenario %d, P%d)",route,round,ok ? "PASS" : "FAIL",scenario,_place);
   }
   ok = seen == 0x7e && _place == 157 && ok;
  }
  int32 solved = -1;
  ok = _runner.getValue(0,28,solved) && solved == int(route < 2) && _puzzlesCompleted == completed+uint(route == 0) && ok;
 }
 Script invalidContext; Command custom; custom.opcode = 23; custom.args.push_back(24);
 for (int i = 0; i < 5; ++i) custom.args.push_back(0);
 invalidContext.push_back(custom);
 ok = loadPlace(526) && !_runner.canRun(invalidContext,true) && ok;
 debug("Astronomica P512 interaction verification: %s (24576 original answers, six scenarios, three controls, wrong/recovery, repeated success, unsolved exit, seek/context rejection)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP526Puzzle() {
 auto boundary = [&](uint route, const char *phase, uint32 now) {
  if (!ConfMan.hasKey("astronomica_verify_p526_boundaries") || !ConfMan.getBool("astronomica_verify_p526_boundaries") || _place != 526) return;
  Common::Array<uint32> state;
  if (!_runner.exportIdleState(state)) { debug("P526 audit nonidle: %u %s",route,phase); return; }
  Common::String values;
  auto word = [&](int32 value) { values += Common::String::format(" %d",value); };
  for (uint i = 0; i < 7; ++i) word(state[300+i*3]);
  debug("P526 audit boundary: %u %s %u%s",route,phase,now,values.c_str());
  for (uint i = 0; i < _scene.sprites.size(); ++i) {
   const Sprite &s = _scene.sprites[i]; values.clear();
   for (int32 value : {s.visible,s.selectedFrame,s.x,s.y,int32(s.renderX),int32(s.renderY),int32(s.autoFrame),int32(s.autoMove),
        int32(s.frameSince),int32(s.moveSince),int32(s.standardMotion),int32(s.moveDX),int32(s.moveDY),int32(s.orbitMotion),
        s.orbitSideX,s.orbitSideY,s.frameFirst,s.frameLast,int32(s.clickEnabled)}) word(value);
   for (int32 value : s.frameData) word(value);
   for (int32 value : s.moveData) word(value);
   debug("P526 audit sprite: %u%s",i,values.c_str());
  }
  debug("P526 audit image: %s",_displayedImageName.c_str());
 };
 bool ok = verifyOrbitMotion();
 debug("Astronomica P526 original motion comparison: %s (24 complete x86 trajectories)",ok ? "PASS" : "FAIL");
 // A queued frame change must be visible to custom13 before the next
 // script condition executes. This is a command-order test, not a route.
 if (!loadPlace(526)) return false;
 Script ordered;
 auto command = [&](int opcode, std::initializer_list<int> args) {
  Command c; c.opcode = opcode; c.delay = -1;
  for (int v : args) c.args.push_back(v);
  ordered.push_back(c);
 };
 command(32,{1,2,1}); command(32,{1,3,6}); command(15,{18,4});
 command(23,{13,1,0,0,0,0}); command(31,{1,4,1,0,0,0}); command(32,{1,5,2});
 int32 observed = -1;
 ok = _runner.start(ordered,0,true) && _runner.getValue(1,5,observed) && observed == 2 && ok;
 ConfMan.setBool("astronomica_animation",false);
 ok = loadPlace(526) && !_runner.canRun(ordered,true) && ok;
 ConfMan.setBool("astronomica_animation",true);
 ok = loadPlace(528) && !_runner.canRun(ordered,true) && ok;
 const int choiceXY[6][2] = {{465,425},{465,380},{500,380},{530,430},{390,380},{430,425}};
 for (int route = 0; route < 4; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(111+route);
  if (route == 1) _runner.defineValue(0,42,1);
  if (!loadPlace(526) || _scene.sprites.size() != 23) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  boundary(route,"entry",now);
  auto settle = [&](bool moving) {
   for (uint pass = 0; pass < 4000 && _place == 526; ++pass) {
    if (!_runner.pendingCount() && (!moving || !_scene.sprites[19].autoMove)) break;
    runScriptsAt(now); animateSpritesAt(now); now += 10;
   }
   return _place != 526 || (!_runner.pendingCount() && !_runner.clicksBlocked() && (!moving || !_scene.sprites[19].autoMove));
  };
  if (route == 3) {
   clickAtTime(24,417,now); ok = settle(false) && _place == 268 && ok;
  } else {
   uint seen = 0;
   for (int round = 0; round < 6 && _place == 526; ++round) {
    clickAtTime(250,380,now); ok = settle(true) && ok;
    boundary(route,"stopped",now);
    int32 scenario = 0, active = 0;
    if (_place != 526 || !_runner.getValue(1,2,scenario) || scenario < 1 || scenario > 6) return false;
    ok = !(seen & (1U << scenario)) && _runner.getValue(1,6,active) && active == 1 && ok;
    seen |= 1U << scenario;
    const int phase = _scene.sprites[17].selectedFrame;
    int answer = 1;
    const bool correct = route != 2;
    while (answer <= 6 && orbitAnswer(scenario,phase,answer) != correct) ++answer;
    if (answer > 6) return false;
    clickAtTime(choiceXY[answer-1][0],choiceXY[answer-1][1],now);
    ok = settle(false) && ok;
    boundary(route,"answered",now);
    int32 accepted = -1, errors = -1;
    if (_place == 526) {
     ok = _runner.getValue(1,4,accepted) && accepted == int(correct) && _runner.getValue(1,5,errors) && errors == (correct ? 0 : round+1) && ok;
     ok = _lastSound == (correct ? 13 : 14) && ok;
    }
    debug("Astronomica P526 route %d round %d: %s (scenario %d, phase %d, choice %d, P%d)",route,round,ok ? "PASS" : "FAIL",scenario,phase,answer,_place);
   }
   ok = _place == 268 && (route == 2 || seen == 0x7e) && ok;
  }
  int32 solved = -1;
  ok = _runner.getValue(0,42,solved) && solved == int(route < 2) && _puzzlesCompleted == completed+uint(route == 0) && ok;
 }
 debug("Astronomica P526 interaction verification: %s (six scenarios, repeat success, four wrong answers, unsolved exit, synchronous answer/context rejection)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyPlanetSaves() {
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint records=0,boundaries=0,histories=0,dormant=0,ordinary=0,busy=0,followB=0,releasedB=0,failedArr=0,correctArr=0,settingsMask=0,successors=0,futures=0,exhausted=0,timerCases=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();uint active=0;for(uint i=9;i<18;++i)if(_scene.sprites[i].planetMotion==2&&_scene.sprites[i].autoMove)active|=1U<<i;runScriptsAt(now);animateSpritesAt(now);if(_place==518)for(uint i=9;i<18;++i)if((active&(1U<<i))&&!_scene.sprites[i].autoMove){if(_scene.sprites[i].visible)++correctArr;else ++failedArr;}now+=10;sync();};
 auto settle=[&](bool flight=false){for(uint n=0;n<3000&&_place==518;++n){bool moving=false;if(flight)for(uint i=9;i<18;++i)moving=moving||(_scene.sprites[i].planetMotion==2&&_scene.sprites[i].autoMove);if(_runner.scriptsIdle()&&!moving)break;if(!_runner.scriptsIdle()){if(canSavePlanets())return false;++busy;}tick();}return _place==518&&_runner.scriptsIdle();};
 auto press=[&](uint index,bool flight=false){const int x=index==4?183:index==5?259:374,y=index==7?399:420;sync();if(spriteAt(x,y)!=int(index)||_runner.clicksBlocked())return false;clickAtTime(x,y,now);const bool ok=settle(flight);return _place!=518||ok;};
 auto select=[&](int desired){for(uint n=0;n<20;++n){int32 v=-1;if(!_runner.getValue(1,0,v))return false;if(v==desired)return true;if(!press(v<desired?5:4))return false;}return false;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=6184)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());const bool ok=loadGameStream(&in).getCode()==Common::kNoError;if(ok&&scriptClock()!=READ_LE_UINT32(&data[16]))return false;if(ok)now=scriptClock();sync();return ok;};
 auto fingerprint=[&](bool destination=false){uint32 hash=2166136261U;auto add=[&](uint32 v){hash=(hash^v)*16777619U;};add(_place);add(_previousPlace);add(_puzzlesCompleted);add(_comet.frame);add(_comet.previousFrame);if(destination){Common::Array<uint32>state;if(!_runner.exportPersistentState(state))return uint32(0);for(uint i=0;i<state.size();++i)if(i!=601)add(state[i]);}else add(_runner.probeDiagnosticHash(false));for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;planetSpriteWords(s,w);for(uint32 v:w)add(v);}add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return hash;};
 auto roundtrip=[&](uint duration=130){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSavePlanets())return false;++busy;_mixer->stopHandle(_soundHandle);}Common::Array<byte>data,again;if(!snapshot(data)){debug("Planet snapshot rejection at%u",now);return false;}const uint32 before=fingerprint(),savedNow=now;for(uint n=0;n<duration;n+=10)tick();const uint32 after=fingerprint(),afterNow=now;if(!loadPlace(117)||!restore(data)||now!=savedNow||fingerprint()!=before||!snapshot(again)||again!=data)return false;for(uint n=0;n<duration;n+=10)tick();if(now!=afterNow||fingerprint()!=after)return false;Common::Array<uint32>state;_runner.exportPersistentState(state);bool f=false,r=false,h=false;for(const Sprite&s:_scene.sprites){f=f||s.planetMotion==1;r=r||(s.planetMotion==2&&s.autoMove);h=h||s.planetMotion==2;}++boundaries;++successors;histories+=h;dormant+=state[603]!=0;ordinary+=!state[603];followB+=f;releasedB+=r;settingsMask|=1U<<state[300];return true;};
 auto record=[&](const char*tag){Common::Array<uint32>state;if(!_runner.exportPersistentState(state))return false;uint modes[3]={},active=0;for(const Sprite&s:_scene.sprites){if(s.planetMotion>=0&&s.planetMotion<3)++modes[s.planetMotion];active+=s.planetMotion==2&&s.autoMove;}debug("Planet audit header: %u %s clock%u setting%u mask%u selected%u count%u rng%u releasedActive%u modes%u,%u,%u screen%08x background%08x",records,tag,now,state[300],state[303],state[306],state[309],state[600],active,modes[0],modes[1],modes[2],screenRGBHash(_screen,480),screenRGBHash(_background,480));for(uint i=0;i<32;++i){Common::Array<uint32>words;p526SpriteWords(_scene.sprites[i],words);words.push_back(_scene.sprites[i].planetMotion);words.push_back(_scene.sprites[i].planetPeriod);Common::String line=Common::String::format("Planet audit sprite: %u %u",records,i);for(uint32 v:words)line+=Common::String::format(" %d",int32(v));debug("%s",line.c_str());}++records;return roundtrip();};

 auto future=[&](uint mode){const uint completed=_puzzlesCompleted;if(mode==2){clickAtTime(24,417,now);settle();}
  else for(uint n=0;n<10&&_place==518;++n){int32 id=0;_runner.getValue(1,2,id);const int setting=mode==1&&id<=6?id+9:10-id;if(!select(setting)||!press(7,true))return false;}
  int32 solved=-1;return _place==388&&_runner.scriptsIdle()&&_runner.getValue(0,34,solved)&&solved==int(mode<2)&&_puzzlesCompleted==completed+uint(mode==0);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==17){now=scriptClock();sync();debug("Astronomica planet slot fingerprint: %08x",fingerprint());const bool ok=canSavePlanets()&&roundtrip()&&future(0);debug("Astronomica planet startup save: %s (slot17, exhausted-mask and wrong-history continuation)",ok?"PASS":"FAIL");return ok;}

 _runner.resetGlobals();_runner.seedRandom(101);sync();if(!loadPlace(518)||_runner.enqueueStartup(_scene.scripts,now,true)!=3||!settle()||!record("startup-follow"))return false;

 for(uint setting=1;setting<=15;++setting)if(!select(setting)||!roundtrip())return false;
 if(!press(5)||!roundtrip()||!select(0)||!press(4)||!roundtrip())return false;
 Common::Array<uint32>zeroBefore,zeroAfter;_runner.exportPersistentState(zeroBefore);if(!press(7)||!roundtrip())return false;_runner.exportPersistentState(zeroAfter);if(zeroBefore[600]!=zeroAfter[600]||zeroAfter[309])return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();
 if(!loadPlace(518)||_runner.enqueueStartup(_scene.scripts,now,true)!=3||!settle()||!record("dormant-startup-follow"))return false;

 for(uint n=0;n<7;++n){int32 id=0;if(!_runner.getValue(1,2,id)||!select(10-id)||!press(7,true))return false;}
 if(!record("seven-correct"))return false;int32 a=0,b=0,mask=0,count=0;_runner.getValue(1,2,a);
 if(!select(a==6?14:15)||!press(7)||!record("first-wrong-still-released"))return false;_runner.getValue(1,1,mask);_runner.getValue(1,2,b);_runner.getValue(1,3,count);
 if(mask!=511||count!=7||b==a||_scene.sprites[a+8].planetMotion!=2||!_scene.sprites[a+8].autoMove)return false;
 Common::Array<uint32>before;_runner.exportPersistentState(before);
 if(!select(b==6?14:15)||!press(7)||!record("exhausted-mask-reattached-current"))return false;
 Common::Array<uint32>after;_runner.exportPersistentState(after);
 if(after[303]!=511||after[306]!=uint(b)||after[309]!=7||after[600]==before[600]||_scene.sprites[b+8].planetMotion!=1)return false;
 ++exhausted;for(uint n=0;n<1000;++n)tick();if(!record("old-wrong-arrived-hidden"))return false;

 Common::Array<byte>fixture;if(!snapshot(fixture))return false;const uint32 originalClock=READ_LE_UINT32(&fixture[16]);
 const uint current=READ_LE_UINT32(&fixture[8+(10+928+306)*4])+8;
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint kind:{0U,1U,2U}){const uint period=kind==2?50:10;
  for(uint32 age:{0U,1U,period-1,period,period+1}){Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);
   for(uint i=8;i<18;++i){if(i==8||READ_LE_UINT32(&timed[8+(10+i*29+27)*4])){const uint at=8+(10+i*29+9)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}if(i>=9){const uint at=8+(10+i*29+8)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}}
   if(kind==2){for(uint i=9;i<18;++i)WRITE_LE_UINT32(&timed[8+(10+i*29+8)*4],clock-age);}else WRITE_LE_UINT32(&timed[8+(10+(kind?current:8)*29+9)*4],clock-age);
   const uint at=8+(10+928+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);uint32 hash=2166136261U;for(uint j=8;j<timed.size()-4;j+=4)hash=(hash^READ_LE_UINT32(&timed[j]))*16777619U;WRITE_LE_UINT32(&timed[timed.size()-4],hash);
   if(!restore(timed)||!roundtrip())return false;++timerCases;
  }
 }
 if(!restore(fixture))return false;debug("Astronomica planet timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 // A real foreground original narration finishes naturally, without stopHandle.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSavePlanets())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSavePlanets())return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSavePlanets()||!roundtrip(130))return false;
 debug("Astronomica planet natural voice end: PASS (%u ms, no stopHandle)",waited);
 _loopSound=0;_loopEnabled=true;if(!playSound(0,now,true)||!_mixer->isSoundHandleActive(_soundHandle)||!canSavePlanets())return false;
 Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;
 if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||!snapshot(again)||again!=music)return false;
 debug("Astronomica planet Music restart: PASS (one ambient start)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 // Nonzero sentinels and paused native audio strengthen atomic rejection checks.
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSavePlanets())return false;
 Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="planet-atomic-image";_displayedImageName="planet-atomic-display";
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));
  for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_planetAssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);
  for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));return h;};
 const uint32 unchanged=atomic();const void*pixels=_pendingImage.getPixels();
 auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);uint32 hash=2166136261U;for(uint at=8;at<bad.size()-4;at+=4)hash=(hash^READ_LE_UINT32(&bad[at]))*16777619U;WRITE_LE_UINT32(&bad[bad.size()-4],hash);if(!reject(bad))return false;++invalid;return true;};

 for(uint index:{0U,3U,4U,5U,7U,8U,9U})if(!badWord(index,index==3?538U:index==4?1U:0xffffffffU))return false;
 for(uint i=0;i<32;++i)if(!badWord(10+i*29+18,2))return false;
 for(uint i=0;i<4;++i)if(!badWord(10+928+301+3*i,100))return false;
 if(!badWord(10+928+300,16)||!badWord(10+928+303,512)||!badWord(10+928+306,0)||!badWord(10+928+309,9)||!badWord(10+928+2,0)||!badWord(10+8*29+9,now+1)||!badWord(10+9*29+8,now+1)||!badWord(10+8*29+11,65536)||!badWord(10+8*29+27,1)||!badWord(10+8*29+28,10)||!badWord(10+9*29+27,3)||!badWord(10+9*29+28,0))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSavePlanets())return false;
 debug("Astronomica planet rejection verification: PASS (6184 truncations, 6184 corruptions, %u invalid states, extended atomic state)",invalid);


 // Original count8 branch draws again even when selector0 releases nothing.
 if(!restore(fixture))return false;int32 zeroId=0;_runner.getValue(1,2,zeroId);if(!select(10-zeroId)||!press(7,true)||!select(0))return false;
 Common::Array<uint32>eightBefore,eightAfter;if(!_runner.exportPersistentState(eightBefore)||eightBefore[309]!=8||eightBefore[303]!=511||!press(7)||!_runner.exportPersistentState(eightAfter))return false;
 if(eightAfter[309]!=8||eightAfter[303]!=511||eightAfter[306]!=eightBefore[306]||eightAfter[600]==eightBefore[600]||_scene.sprites[eightAfter[306]+8].planetMotion!=1||!roundtrip())return false;++exhausted;
 debug("Astronomica planet count8 zero-setting: PASS (delayed exhausted-mask RNG draw, unchanged count/selection, native follow, roundtrip)");

 for(uint mode=0;mode<3;++mode){if(!restore(fixture))return false;if(mode==1)_runner.defineValue(0,34,1);if(!roundtrip())return false;Common::Array<byte>branch;if(!snapshot(branch)||!future(mode))return false;const uint32 expected=fingerprint(mode==0),expectedClock=now,expectedEnd=_lastSuccessEnd;if(!expected)return false;
  if(!restore(branch)||!future(mode)||(mode?now!=expectedClock:(now-_lastSuccessEnd<2010||now-_lastSuccessEnd>=2020||expectedClock-expectedEnd<2010||expectedClock-expectedEnd>=2020))||fingerprint(mode==0)!=expected){debug("Planet future mismatch mode%u clock%u/%u end%u/%u hash%08x/%08x",mode,expectedClock,now,expectedEnd,_lastSuccessEnd,expected,fingerprint(mode==0));return false;}++futures;++successors;
 }
 if(!restore(fixture)||saveGameState(17,"Planet continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica planet slot fingerprint: %08x",fingerprint());if(!future(0))return false;
 uint settings=0;for(uint i=0;i<16;++i)settings+=(settingsMask>>i)&1U;
 debug("Astronomica planet motion coverage: PASS (%u follow boundaries, %u released boundaries, %u failed arrivals, %u correct arrivals, %u speed settings, %u successor checks, %u future outcome checks, %u exhausted mask checks)",followB,releasedB,failedArr,correctArr,settings,successors,futures,exhausted);
 debug("Astronomica planet saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);
 return true;
}
bool AstronomicaEngine::verifyP518Puzzle() {
 bool ok = true;
 for (int route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(101+route); ok = loadPlace(518) && ok;
  if (_scene.sprites.size() != 32) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0; bool wrongSound = false; uint correctSounds = 0; uint lastStarted = _soundsStarted;
  auto settle = [&](bool flight) {
   for (uint pass = 0; pass < 1600 && _place == 518; ++pass) {
    bool moving = false;
    if (flight) for (uint id = 9; id < 18; ++id) moving = moving || (_scene.sprites[id].planetMotion == 2 && _scene.sprites[id].autoMove);
    if (!_runner.pendingCount() && !moving) break;
    runScriptsAt(now); animateSpritesAt(now); now += 10;
    if (_soundsStarted != lastStarted) {
     if (_lastSound == 9) wrongSound = true;
     if (_lastSound == 10) ++correctSounds;
     lastStarted = _soundsStarted;
    }
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto press = [&](int button, bool flight = false) {
   const int x = button == 4 ? 183 : button == 5 ? 259 : 374;
   const int y = button == 7 ? 399 : 420;
   const bool hit = spriteAt(x,y) == button;
   clickAtTime(x,y,now); return settle(flight) && hit;
  };
  auto select = [&](int target) {
   int32 value = -1;
   for (uint pass = 0; pass < 20; ++pass) {
    if (!_runner.getValue(1,0,value)) return false;
    if (value == target) return true;
    if (!press(value < target ? 5 : 4)) return false;
   }
   return false;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && settle(false) && ok;
  int32 planet = 0, count = -1, mask = 0;
  ok = press(4) && press(7) && _runner.getValue(1,3,count) && count == 0 && ok;
  if (route == 2) {
   clickAtTime(24,417,now); ok = settle(false) && _place == 388 && ok;
  } else {
   if (route == 0) {
    _runner.getValue(1,2,planet);
    const int wrong = planet == 9 ? 2 : 1;
    ok = select(wrong) && press(7,true) && wrongSound && ok;
    ok = _runner.getValue(1,3,count) && count == 0 && _runner.getValue(1,1,mask) && !(mask & (1 << (planet-1))) && ok;
   } else {
    ok = select(15) && press(5) && _runner.getValue(1,0,count) && count == 15 && ok;
   }
   uint seen = 0;
   for (int round = 0; round < 9 && _place == 518; ++round) {
    if (!_runner.getValue(1,2,planet) || planet < 1 || planet > 9) return false;
    ok = !(seen & (1U << planet)) && ok; seen |= 1U << planet;
    const int target = route == 1 && planet <= 6 ? planet+9 : 10-planet;
    ok = select(target) && press(7,true) && ok;
    if (_place == 518) ok = _runner.getValue(1,3,count) && count == round+1 && ok;
   }
   ok = seen == 0x3fe && correctSounds == 9 && _place == 388 && ok;
  }
  int32 solved = -1;
  ok = _runner.getValue(0,34,solved) && solved == int(route < 2) && _puzzlesCompleted == completed+uint(route < 2) && ok;
  debug("Astronomica P518 route %d: %s (P%d, global34=%d, correct sounds=%u)",route,ok ? "PASS" : "FAIL",_place,solved,correctSounds);
 }
 debug("Astronomica P518 interaction verification: %s (nine planets, both directions, wrong answer recovery, zero/bounds, unsolved exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP511Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,busy=0,histories=0,dormant=0,ordinary=0,images=0,frames=0,animations=0,successors=0,futures=0,timerCases=0,controlMask=0,dialMask=0,cloudMask=0,typeMask=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto settle=[&](){for(uint n=0;n<18000&&!_runner.scriptsIdle();++n){if(_place==511){if(canSaveP511())return false;++busy;}tick();}return _runner.scriptsIdle();};
 auto fingerprint=[&](){uint32 h=_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=6256)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&data[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP511())return false;_mixer->stopHandle(_soundHandle);}Common::Array<byte>data,again;if(!snapshot(data)){debug("P511 snapshot rejected boundary%u clock%u image%s",boundaries,now,_displayedImageName.c_str());return false;}const uint32 before=fingerprint(),saved=now;for(uint n=0;n<60;++n)tick();const uint32 after=fingerprint(),ended=now;if(!loadPlace(117)||!restore(data)||now!=saved||fingerprint()!=before||!snapshot(again)||again!=data){debug("P511 restore mismatch boundary%u",boundaries);return false;}for(uint n=0;n<60;++n)tick();if(now!=ended||fingerprint()!=after){debug("P511 successor mismatch boundary%u",boundaries);return false;}Common::Array<uint32>state;_runner.exportPersistentState(state);++boundaries;++successors;histories+=state[300]!=52||state[306]!=0||state[309]!=4;dormant+=state[603]!=0;ordinary+=!state[603];images+=!_displayedImageName.empty();const int savedSelected=int32(READ_LE_UINT32(&data[8+(11+4*27+1)*4])),savedFirst=int32(READ_LE_UINT32(&data[8+(11+4*27+16)*4])),savedLast=int32(READ_LE_UINT32(&data[8+(11+4*27+17)*4]));frames+=savedSelected<savedFirst||savedSelected>savedLast;animations+=_scene.sprites[4].autoFrame&&_scene.sprites[19].autoFrame&&_scene.sprites[20].autoFrame;dialMask|=1U<<state[306];cloudMask|=1U<<(state[300]/4);typeMask|=1U<<(state[309]-1);return true;};
 auto press=[&](uint index,int x,int y){if(_place!=511||_runner.clicksBlocked()||spriteAt(x,y)!=int(index))return false;clickAtTime(x,y,now);if(!settle()||_place!=511)return false;controlMask|=1U<<index;return true;};

 auto value=[&](uint index){int32 v=-1;_runner.getValue(1,index,v);return v;};
 auto up=[&](){return press(10,376,430);};auto down=[&](){return press(9,300,430);};auto cloudDown=[&](){return press(16,440,443);};auto cloudUp=[&](){return press(17,534,443);};
 auto startup=[&](){sync();return loadPlace(511)&&_runner.enqueueStartup(_scene.scripts,now,true)==5&&settle()&&_place==511;};
 auto future=[&](uint mode){const uint completed=_puzzlesCompleted;
  if(mode==3)return cloudUp()&&down()&&press(13,151,380)&&up()&&_puzzlesCompleted==completed;
  if(mode<2){if(!up()||spriteAt(125,400)!=12)return false;clickAtTime(125,400,now);}
  else {if(spriteAt(24,417)!=1)return false;clickAtTime(24,417,now);}
  // Outcome scheduler sampled at an explicit coarse interval, while exact
  // full clocks/state601 and destination surfaces remain compared below.
  for(uint n=0;n<120&&_place==511;++n){if(canSaveP511())return false;++busy;sync();runScriptsAt(now);animateSpritesAt(now);now+=1000;sync();}
  int32 solved=-1;return _place==388&&_runner.getValue(0,27,solved)&&solved==int(mode<2)&&_puzzlesCompleted==completed+uint(mode==0);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==20){now=scriptClock();sync();debug("Astronomica P511 slot fingerprint: %08x",fingerprint());const bool ok=canSaveP511()&&roundtrip()&&future(0);debug("Astronomica P511 startup save: %s (slot20, retained CLOUD and animation range)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();if(!startup()||!roundtrip())return false;
 for(uint n=0;n<15;++n)if(!up()||!roundtrip())return false;
 if(!up()||!roundtrip())return false;
 for(uint n=0;n<15;++n)if(!down()||!roundtrip())return false;
 if(!down()||!roundtrip())return false;
 for(uint n=0;n<13;++n)if(!cloudDown()||!roundtrip())return false;
 if(!cloudDown()||!roundtrip()||!cloudUp()||!roundtrip()||!cloudDown()||!roundtrip())return false;
 for(uint n=0;n<13;++n)if(!cloudUp()||!roundtrip())return false;
 if(!cloudUp()||!roundtrip())return false;
 for(const auto&point:{Common::Point(125,400),Common::Point(151,380),Common::Point(179,380),Common::Point(204,400)}){const uint index=point.x==125?12:point.x==151?13:point.x==179?14:15;if(!press(index,point.x,point.y)||!roundtrip())return false;}
 // Ordinary mask1/3/5/6 via original controls; do not manufacture locals.
 if(!startup()||!press(12,125,400)||value(5)!=1||!roundtrip())return false;
 for(uint n=0;n<15;++n)if(!up())return false;if(value(5)!=3||!roundtrip())return false;
 if(!startup()||!press(12,125,400))return false;for(uint n=0;n<13;++n)if(!cloudDown())return false;if(value(5)!=5||!roundtrip())return false;
 if(!startup())return false;for(uint n=0;n<15;++n)if(!up())return false;for(uint n=0;n<13;++n)if(!cloudDown())return false;if(value(5)!=6||!roundtrip())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();
 if(!startup()||!roundtrip())return false;
 for(uint n=0;n<14;++n)if(!up())return false;for(uint n=0;n<13;++n)if(!cloudDown())return false;if(!roundtrip())return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&data){uint32 h=2166136261U;for(uint j=8;j<data.size()-4;j+=4)h=(h^READ_LE_UINT32(&data[j]))*16777619U;WRITE_LE_UINT32(&data[data.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint kind:{4U,19U,20U}){const uint period=kind==19?400:500;for(uint age:{0U,1U,period-1,period,period+1}){
  Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);for(uint i:{4U,19U,20U}){const uint at=8+(11+i*27+8)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}const uint loaded=8+(11+945+601)*4;WRITE_LE_UINT32(&timed[loaded],READ_LE_UINT32(&timed[loaded])+delta);WRITE_LE_UINT32(&timed[8+(11+kind*27+8)*4],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;
 }}
 if(!restore(fixture))return false;debug("Astronomica P511 timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+945+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP511())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP511()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSaveP511()||!roundtrip())return false;debug("Astronomica P511 natural voice end: PASS (%u ms, no stopHandle)",waited);
 // Obtain the ambient binding through the actual original scene entry.
 ConfMan.setBool("astronomica_entry_scripts",true);sync();const bool entered=loadPlace(511);ConfMan.setBool("astronomica_entry_scripts",false);if(!entered||!settle()||_loopSound!=0||!_loopEnabled)return false;
 if(_mixer->isSoundHandleActive(_soundHandle)){if(canSaveP511())return false;++busy;_mixer->stopHandle(_soundHandle);}
 const uint32 ambientEpoch=_lastSoundAt;now=ambientEpoch+4999;sync();resumeLoopAt(now);if(_mixer->isSoundHandleActive(_soundHandle))return false;
 ++now;sync();resumeLoopAt(now);if(_mixer->isSoundHandleActive(_soundHandle))return false;
 ++now;sync();resumeLoopAt(now);if(!_mixer->isSoundHandleActive(_soundHandle)||_lastSound!=0||!canSaveP511())return false;
 debug("Astronomica P511 ambient deadline: PASS (3 cases, original entry)");
 const int musicBefore=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);
 Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77||!snapshot(again)||again!=music)return false;
 _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,musicBefore);debug("Astronomica P511 Music restart: PASS (one ambient start, Music volume unchanged)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP511())return false;Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="P511-atomic-image";_displayedImageName="P511-atomic-display";
 _movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_movieFrame.w),uint32(_movieFrame.h),uint32(_p511AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P511 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(index,index==3?538U:index==4?1U:0xffffffffU))return false;
 for(uint i=0;i<35;++i)if(!badWord(11+i*27+18,2))return false;
 for(uint i:{2U,301U,302U,300U,303U,306U,309U,312U,315U,602U,603U,604U})if(!badWord(11+945+i,0xffffffffU))return false;
 for(uint i:{4U,19U,20U})if(!badWord(11+i*27+8,now+1)||!badWord(11+i*27+1,4)||!badWord(11+i*27+19,499))return false;
 if(!badWord(11+945+601,now+1)||!badWord(11+4*27+16,4)||!badWord(11+4*27+17,4)||!badWord(11+18*27+3,65538)||!badWord(11+18*27+5,65538)||!badWord(11+33*27,0)||!badWord(11+34*27,1))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP511())return false;debug("Astronomica P511 rejection verification: PASS (6256 truncations, 6256 corruptions, %u invalid states, extended atomic state)",invalid);

 for(uint mode=0;mode<4;++mode){if(!restore(fixture))return false;_runner.defineValue(0,27,mode==1?1:0);if(!roundtrip())return false;Common::Array<byte>branch;if(!snapshot(branch)||!future(mode))return false;const uint32 expected=fingerprint(),expectedClock=now;
  if(!restore(branch)||!future(mode)||now!=expectedClock||fingerprint()!=expected){debug("P511 future mismatch mode%u clock%u/%u hash%08x/%08x",mode,expectedClock,now,expected,fingerprint());return false;}++futures;++successors;
 }
 if(!restore(fixture)||saveGameState(20,"P511 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P511 slot fingerprint: %08x",fingerprint());if(!future(0))return false;
 uint controls=0,dials=0,clouds=0,types=0;for(uint i=0;i<32;++i)controls+=(controlMask>>i)&1U;for(uint i=0;i<16;++i)dials+=(dialMask>>i)&1U;for(uint i=0;i<14;++i)clouds+=(cloudMask>>i)&1U;for(uint i=0;i<4;++i)types+=(typeMask>>i)&1U;
 if(dials!=16||clouds!=14||types!=4||!frames){debug("P511 coverage failed dials%u clouds%u types%u retainedFrames%u",dials,clouds,types,frames);return false;}
 debug("Astronomica P511 controls coverage: PASS (%u dial settings, %u cloud settings, %u type settings)",dials,clouds,types);
 debug("Astronomica P511 history coverage: PASS (%u choice controls, %u retained-image boundaries, %u frame-history boundaries, %u animation boundaries, %u successor checks, %u future outcome checks)",controls,images,frames,animations,successors,futures);
 debug("Astronomica P511 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP509Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,histories=0,dormant=0,ordinary=0,busy=0,choiceMask=0,images=0,targetHistories=0,animations=0,successors=0,futures=0,timerCases=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto step=[&](uint duration){sync();runScriptsAt(now);animateSpritesAt(now);now+=duration;sync();};
 auto tick=[&](){step(10);};
 auto advance=[&](uint duration){for(uint n=0;n<duration&&_place==509;n+=10)tick();};
 auto eligible=[&](){Common::Array<uint32>state;for(uint n=0;n<3000&&_place==509;++n){if(_runner.exportP509PendingState(state,now)){if(_mixer->isSoundHandleActive(_soundHandle)){if(canSaveP509())return false;++busy;_mixer->stopHandle(_soundHandle);}return true;}if(canSaveP509())return false;++busy;tick();}return false;};
 auto fingerprint=[&](){uint32 h=_runner.probeDiagnosticHash(false);auto add=[&](uint32 v){h=(h^v)*16777619U;};for(uint32 v:{uint32(_place),uint32(_previousPlace),_puzzlesCompleted,uint32(_comet.frame),uint32(_comet.previousFrame)})add(v);for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return h;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=4540)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());if(loadGameStream(&in).getCode()!=Common::kNoError||scriptClock()!=READ_LE_UINT32(&data[16]))return false;now=scriptClock();sync();return true;};
 auto roundtrip=[&](uint duration=2000){if(!eligible())return false;Common::Array<byte>data,again;if(!snapshot(data)){debug("P509 snapshot rejected clock%u image%s",now,_displayedImageName.c_str());return false;}const uint32 before=fingerprint(),saved=now;advance(duration);const uint32 after=fingerprint(),ended=now;
  if(!loadPlace(117)||!restore(data)||now!=saved||fingerprint()!=before||!snapshot(again)||again!=data){debug("P509 roundtrip restore/bytes FAIL boundary%u",boundaries);return false;}advance(duration);if(now!=ended||fingerprint()!=after){debug("P509 successor FAIL boundary%u clock%u/%u hash%08x/%08x",boundaries,now,ended,fingerprint(),after);return false;}
  Common::Array<uint32>state;Common::Array<uint32>queue;_runner.auditP509Snapshot(state,queue);bool partial=false;for(uint i=1;i<=5;++i)partial=partial||state[300+3*i]==0;++boundaries;++successors;histories+=partial||state[339]!=0;targetHistories+=partial;dormant+=state[603]!=0;ordinary+=!state[603];images+=!_displayedImageName.empty();animations+=_scene.sprites[10].autoFrame&&_scene.sprites[10].autoMove;return true;};
 auto choose=[&](uint option){const int xs[]={83,166,257,338,408,490};if(_place!=509||_runner.clicksBlocked()||option<1||option>6)return false;const uint index=option+3;int x=xs[option-1],y=365;if(spriteAt(x,y)!=int(index)){x=_scene.sprites[index].renderX+44;y=_scene.sprites[index].renderY+53;}if(spriteAt(x,y)!=int(index))return false;clickAtTime(x,y,now);advance(1000);if(_runner.clicksBlocked())return false;choiceMask|=1U<<(option-1);return true;};
 auto target=[&](uint id){if(_place!=509||_runner.clicksBlocked())return false;const MouseRect&r=_scene.mouseRects[id];const int x=(r.rect[0]+r.rect[2])/2,y=(r.rect[1]+r.rect[3])/2;if(spriteAt(x,y)!=-1)return false;clickAtTime(x,y,now);advance(2000);return _place==509&&!_runner.clicksBlocked();};
 auto sky1=[&](){const uint order[]={0,1,2,4,3,5},options[]={2,1,1,2,1,3};for(uint i=0;i<6;++i)if(!choose(options[i])||!target(order[i])||!roundtrip())return false;int32 phase=0;return _runner.getValue(1,16,phase)&&phase==1;};
 auto future=[&](uint mode){const uint completed=_puzzlesCompleted;if(mode<2){if(!choose(1)||!target(3)||!choose(3)||!target(5))return false;}
  else if(mode==2){if(!choose(6))return false;for(uint i=0;i<3;++i)if(!target(3))return false;int32 phase=0;if(!_runner.getValue(1,16,phase)||phase!=2||!choose(3))return false;for(uint i=0;i<3;++i)if(!target(0))return false;}
  else clickAtTime(24,417,now);
  // Explicit coarse controlled caller schedule after queued outcome work.
  // Full destination clocks/state are still compared exactly, never normalized.
  for(uint n=0;n<120&&_place==509;++n)step(1000);
  int32 solved=-1;return _place==304&&_runner.getValue(0,25,solved)&&solved==int(mode<2)&&_puzzlesCompleted==completed+uint(mode==0);
 };
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==19){now=scriptClock();sync();debug("Astronomica P509 slot fingerprint: %08x",fingerprint());const bool ok=canSaveP509()&&roundtrip()&&future(0);debug("Astronomica P509 startup save: %s (slot19, trusted narrator and sky1 targets)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();sync();if(!loadPlace(509)||_runner.enqueueStartup(_scene.scripts,now,true)!=6)return false;advance(4000);if(!roundtrip())return false;
 for(uint option=1;option<=6;++option)if(!choose(option)||!roundtrip())return false;if(!sky1())return false;
 if(!choose(6))return false;for(uint i=0;i<3;++i)if(!target(3)||!roundtrip())return false;int32 phase=0;if(!_runner.getValue(1,16,phase)||phase!=2)return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();
 if(!loadPlace(509)||_runner.enqueueStartup(_scene.scripts,now,true)!=6)return false;advance(4000);if(!roundtrip()||!sky1()||!eligible())return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&data){uint32 h=2166136261U;for(uint j=8;j<data.size()-4;j+=4)h=(h^READ_LE_UINT32(&data[j]))*16777619U;WRITE_LE_UINT32(&data[data.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint kind:{0U,1U,2U}){const uint period=kind==0?150:kind==1?200:800;for(uint age:{0U,1U,period-1,period,period+1}){
  Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);for(uint field:{8U,9U}){const uint at=8+(11+10*27+field)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}for(uint field:{601U,607U}){const uint at=8+(11+513+field)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}const uint at=kind<2?8+(11+10*27+(kind==0?8:9))*4:8+(11+513+607)*4;WRITE_LE_UINT32(&timed[at],clock-age);checksum(timed);if(!restore(timed)||!roundtrip())return false;++timerCases;
 }}
 if(!restore(fixture))return false;debug("Astronomica P509 timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 // Unknown historical values remain data, while their original metadata stays unknown.
 Common::Array<byte>unknown=fixture;WRITE_LE_UINT32(&unknown[8+(11+513+450)*4],0x80000000U);checksum(unknown);if(!restore(unknown)||!roundtrip()||!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP509())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP509()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSaveP509()||!roundtrip())return false;debug("Astronomica P509 natural voice end: PASS (%u ms, no stopHandle)",waited);
 if(!eligible()||_loopEnabled||_mixer->isSoundHandleActive(_soundHandle))return false;const int musicBefore=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType);_mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);
 Common::Array<byte>music;if(!snapshot(music))return false;const uint soundsBefore=_soundsStarted;if(!loadPlace(117)||!restore(music)||_loopEnabled||_mixer->isSoundHandleActive(_soundHandle)||_soundsStarted!=soundsBefore||_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)!=77)return false;
 _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,musicBefore);debug("Astronomica P509 Music state: PASS (Music volume unchanged, disabled ambient stays stopped, zero ambient starts)");if(!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP509())return false;Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="P509-atomic-image";_displayedImageName="P509-atomic-display";
 _movieFrame.create(7,4,_screen.format);_movieFrame.fillRect(Common::Rect(7,4),_screen.format.RGBToColor(41,73,97));_moviePresentedFrame=17;
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),uint32(_movieFrame.w),uint32(_movieFrame.h),uint32(_p509AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));add(screenRGBHash(_movieFrame,480));return h;};
 const uint32 unchanged=atomic();const void*pendingPixels=_pendingImage.getPixels(),*moviePixels=_movieFrame.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pendingPixels&&_movieFrame.getPixels()==moviePixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pendingPixels||_movieFrame.getPixels()!=moviePixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P509 invalid accepted field%u value%u",index,value);return false;}++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(index,index==3?538U:index==4||index==5||index==7?1U:0xffffffffU))return false;
 for(uint i=0;i<19;++i)if(!badWord(11+i*27+18,2))return false;
 for(uint i:{2U,301U,302U,321U,339U,342U,345U,348U,602U,603U,604U,605U,606U})if(!badWord(11+513+i,0xffffffffU))return false;
 for(uint index:{0U,4U,24U})if(!badWord(11+513+606,index))return false;
 if(!badWord(11+513+601,now+1)||!badWord(11+513+607,now+1)||!badWord(11+10*27+8,now+1)||!badWord(11+10*27+9,now+1)||!badWord(11+10*27+4,447)||!badWord(11+10*27+4,590)||!badWord(11+10*27+5,uint32(-2))||!badWord(11+10*27+5,67)||!badWord(11+10*27+11,65538)||!badWord(11+10*27+12,65537)||!badWord(11+10*27,1)||!badWord(11+10*27+19,400)||!badWord(11+10*27+22,201))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_movieFrame.free();_moviePresentedFrame=-1;_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP509())return false;debug("Astronomica P509 rejection verification: PASS (4540 truncations, 4540 corruptions, %u invalid states, extended atomic state)",invalid);
 for(uint mode=0;mode<4;++mode){if(!restore(fixture))return false;_runner.defineValue(0,25,mode==1?1:0);if(!roundtrip()||!eligible())return false;Common::Array<byte>branch;if(!snapshot(branch)||!future(mode))return false;const uint32 expected=fingerprint(),expectedClock=now;
  if(!restore(branch)||!future(mode)||now!=expectedClock||fingerprint()!=expected){debug("P509 future mismatch mode%u clock%u/%u hash%08x/%08x",mode,expectedClock,now,expected,fingerprint());return false;}++futures;++successors;
 }
 if(!restore(fixture)||saveGameState(19,"P509 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P509 slot fingerprint: %08x",fingerprint());if(!future(0))return false;
 uint choices=0;for(uint i=0;i<6;++i)choices+=(choiceMask>>i)&1U;
 debug("Astronomica P509 history coverage: PASS (%u choice controls, %u retained-image boundaries, %u target-history boundaries, %u animation boundaries, %u successor checks, %u future outcome checks)",choices,images,targetHistories,animations,successors,futures);
 debug("Astronomica P509 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP509BoundaryAudit(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint records=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=1;sync();};
 auto advance=[&](uint duration){const uint32 end=now+duration;while(now<end&&_place==509)tick();};
 auto record=[&](const char*tag){Common::Array<uint32>state,queue;_runner.auditP509Snapshot(state,queue);if(state.size()!=605)return false;
  debug("P509 audit header: %u %s now%u place%d pending%u scriptsIdle%d blocked%d loadedAt%u lastTrue%u image=%s pendingImage=%s screen%08x background%08x",records,tag,now,_place,_runner.pendingCount(),int(_runner.scriptsIdle()),int(_runner.clicksBlocked()),state[601],state[602],_displayedImageName.c_str(),_pendingImageName.c_str(),screenRGBHash(_screen,480),screenRGBHash(_background,480));
  Common::String line;for(uint32 v:state)line+=Common::String::format(" %u",v);debug("P509 audit values605:%s",line.c_str());line.clear();for(uint32 v:queue)line+=Common::String::format(" %u",v);debug("P509 audit queue(program,index,since,opcode,delay):%s",line.c_str());
  if(_place==509)for(uint i=0;i<19;++i){Common::Array<uint32>w;p526SpriteWords(_scene.sprites[i],w);line.clear();for(uint32 v:w)line+=Common::String::format(" %u",v);const Frame*f=spriteFrameAt(_scene,i,_scene.sprites[i].selectedFrame);debug("P509 audit sprite %u:%s",i+1,line.c_str());if(i==10&&f){Common::File original;if(!original.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P509/MEGAFILE.HYP"))))return false;Graphics::Surface*bmp=decodeSpriteBitmap(original,f->image,_screen.format);if(!bmp)return false;debug("P509 audit hidden mover: frame%d width%d height%d moveDX%d moveDY%d visible%d",_scene.sprites[i].selectedFrame,bmp->w,bmp->h,_scene.sprites[i].moveDX,_scene.sprites[i].moveDY,int(_scene.sprites[i].visible));bmp->free();delete bmp;}}
  ++records;return true;};
 auto choose=[&](uint option){const int xs[]={83,166,257,338,408,490};if(_place!=509||_runner.clicksBlocked()||spriteAt(xs[option-1],365)!=int(option+3))return false;clickAtTime(xs[option-1],365,now);advance(1000);return !_runner.clicksBlocked();};
 auto target=[&](uint id){const MouseRect&r=_scene.mouseRects[id];clickAtTime((r.rect[0]+r.rect[2])/2,(r.rect[1]+r.rect[3])/2,now);advance(2000);return _place==509&&!_runner.clicksBlocked();};
 _runner.resetGlobals();sync();if(!loadPlace(509)||_runner.enqueueStartup(_scene.scripts,now,true)!=6||!record("startup"))return false;
 advance(3499);if(!record("entry-before3500"))return false;advance(1);if(!record("entry-at3500-beforetick"))return false;tick();if(!record("entry-after3500"))return false;advance(500);if(!record("ordinary-sky2"))return false;
 bool found=false;Common::Array<uint32>state,q;for(uint n=0;n<10000;++n){_runner.auditP509Snapshot(state,q);if(q.size()==5&&q[0]==5&&q[1]==24&&int32(now-q[2])<799){found=true;break;}tick();}if(!found)return false;
 const uint32 since=q[2];advance(since+799-now);if(!record("narrator800-before"))return false;advance(1);tick();if(!record("narrator800-at-aftertick"))return false;tick();if(!record("narrator800-nextpass"))return false;runScriptsAt(now);animateSpritesAt(now);if(!record("narrator800-sametime-pass1"))return false;runScriptsAt(now);animateSpritesAt(now);if(!record("narrator800-sametime-pass2"))return false;advance(800);if(!record("narrator1600-plus"))return false;
 for(uint option:{1U,6U,6U,4U})if(!choose(option)||!record("selected-control"))return false;
 const uint order[]={0,1,2,4,3,5},options[]={2,1,1,2,1,3};for(uint i=0;i<6;++i)if(!choose(options[i])||!target(order[i])||!record("remove-sky2-target"))return false;
 int32 phase=0;if(!_runner.getValue(1,16,phase)||phase!=1||!record("ordinary-sky1"))return false;
 if(!choose(6))return false;for(uint i=0;i<3;++i)if(!target(3)||!record("wrong-in-sky1"))return false;
 if(!_runner.getValue(1,16,phase)||phase!=2||!record("reset-sky2-history"))return false;
 if(!choose(3))return false;for(uint i=0;i<3;++i)if(!target(0)||!record("wrong-in-reset-sky2"))return false;
 if(!_runner.getValue(1,16,phase)||phase!=3||!record("sky3-exit-queued"))return false;
 advance(12000);if(_place!=304||!record("failure-exit304"))return false;
 debug("Astronomica P509 boundary audit: PASS (%u records, NATIVE_BOUNDARY_AUDIT_ONLY, no serializer or save support)",records);
 _runner.resetGlobals();now=1000;sync();if(!loadPlace(509)||_runner.enqueueStartup(_scene.scripts,now,true)!=6)return false;advance(5000);
 Common::Array<uint32>kernelState;bool eligible=false;for(uint n=0;n<10000;++n){if(_runner.exportP509PendingState(kernelState,now)){eligible=true;break;}tick();}if(!eligible)return false;
 const ScriptRunner source=_runner;if(!loadPlace(509,false,true)||!_runner.scriptsIdle()||!source.verifyP509PendingSnapshots(_runner,now))return false;
 debug("Astronomica P509 foundation verification: PASS (STAGED_PENDING_KERNEL_ONLY, no serializer/loader/save support)");return true;
}
bool AstronomicaEngine::verifyP521Saves(){
 ConfMan.setBool("astronomica_verify",false);uint32 now=0;uint boundaries=0,histories=0,dormant=0,ordinary=0,busy=0,controls=0,images=0,fragments=0,animations=0,successors=0,futures=0,timerCases=0;
 auto sync=[&](){_clockPaused=true;_pauseStarted=now;_pausedMillis=0;};
 auto tick=[&](){sync();runScriptsAt(now);animateSpritesAt(now);now+=10;sync();};
 auto settle=[&](){for(uint n=0;n<18000&&!_runner.scriptsIdle();++n){if(_place==521){if(canSaveP521())return false;++busy;}tick();}return _runner.scriptsIdle();};
 const int buttons[]={103,180,270,370,475};
 auto press=[&](uint choice){sync();if(_place!=521||choice<1||choice>5||spriteAt(buttons[choice-1],361)!=int(choice-1))return false;clickAtTime(buttons[choice-1],361,now);return settle()&&_place==521;};
 auto snapshot=[&](Common::Array<byte>&data){sync();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError||out.size()!=5392)return false;data.resize(out.size());memcpy(&data[0],out.getData(),out.size());return true;};
 auto restore=[&](const Common::Array<byte>&data){_pauseStarted=0x23450000U;Common::MemoryReadStream in(&data[0],data.size());const bool ok=loadGameStream(&in).getCode()==Common::kNoError;if(ok&&scriptClock()!=READ_LE_UINT32(&data[16]))return false;if(ok)now=scriptClock();sync();return ok;};
 auto fingerprint=[&](){uint32 hash=2166136261U;auto add=[&](uint32 v){hash=(hash^v)*16777619U;};add(_place);add(_previousPlace);add(_puzzlesCompleted);add(_comet.frame);add(_comet.previousFrame);add(_runner.probeDiagnosticHash(false));for(const Sprite&s:_scene.sprites){Common::Array<uint32>w;p526SpriteWords(s,w);for(uint32 v:w)add(v);add(s.planetMotion);add(s.planetPeriod);}for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_screen,480));add(screenRGBHash(_background,480));return hash;};
 auto roundtrip=[&](uint duration=430){if(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound){if(canSaveP521())return false;++busy;_mixer->stopHandle(_soundHandle);}Common::Array<byte>data,again;if(!snapshot(data)){debug("P521 snapshot rejected clock%u image%s",now,_displayedImageName.c_str());return false;}const uint32 before=fingerprint(),savedNow=now;for(uint n=0;n<duration;n+=10)tick();const uint32 after=fingerprint(),afterNow=now;if(!loadPlace(117)||!restore(data)||now!=savedNow||fingerprint()!=before||!snapshot(again)||again!=data)return false;for(uint n=0;n<duration;n+=10)tick();if(now!=afterNow||fingerprint()!=after)return false;Common::Array<uint32>state;_runner.exportPersistentState(state);++boundaries;++successors;histories+=!_displayedImageName.empty()||_scene.sprites[10].frameData[0]==-1;dormant+=state[603]!=0;ordinary+=!state[603];images+=!_displayedImageName.empty();fragments+=_scene.sprites[13].standardMotion;animations+=_scene.sprites[11].autoFrame;return true;};
 auto future=[&](uint mode){const uint completed=_puzzlesCompleted;if(mode==3)return press(5)&&p521Image(_displayedImageName)==1&&_puzzlesCompleted==completed;if(mode<2){if(!press(3))return false;int32 solved=0;if(!_runner.getValue(0,37,solved)||solved!=1||_puzzlesCompleted!=completed+uint(mode==0))return false;}
  clickAtTime(24,417,now);if(!settle()||_place!=388)return false;return true;};
 if(ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")==18){now=scriptClock();sync();debug("Astronomica P521 slot fingerprint: %08x",fingerprint());const bool ok=canSaveP521()&&roundtrip()&&future(0);debug("Astronomica P521 startup save: %s (slot18, retained image and hidden fragments)",ok?"PASS":"FAIL");return ok;}
 _runner.resetGlobals();sync();if(!loadPlace(521)||_runner.enqueueStartup(_scene.scripts,now,true)!=1||!settle()||!roundtrip())return false;
 for(uint choice=1;choice<=5;++choice){if(!press(choice)||!roundtrip())return false;++controls;}
 for(uint choice:{5U,1U,3U,4U,5U})if(!press(choice)||!roundtrip())return false;
 if(loadGameState(99).getCode()!=Common::kNoError)return false;_runner.resetGlobals();_runner.defineValue(1,50,1234);_runner.seedRandom(101);_puzzlesCompleted=10;_comet.frame=3;_comet.previousFrame=4;now=1000;sync();
 if(!loadPlace(521)||_runner.enqueueStartup(_scene.scripts,now,true)!=1||!settle()||!roundtrip())return false;
 for(uint choice:{5U,5U,2U,4U,1U})if(!press(choice)||!roundtrip())return false;
 Common::Array<byte>fixture;if(!snapshot(fixture))return false;
 auto checksum=[&](Common::Array<byte>&data){uint32 h=2166136261U;for(uint j=8;j<data.size()-4;j+=4)h=(h^READ_LE_UINT32(&data[j]))*16777619U;WRITE_LE_UINT32(&data[data.size()-4],h);};
 const uint originalClock=READ_LE_UINT32(&fixture[16]);
 for(uint32 clock:{originalClock,0xfffffff0U})for(uint32 age:{0U,1U,399U,400U,401U}){
  Common::Array<byte>timed=fixture;const uint32 delta=clock-originalClock;WRITE_LE_UINT32(&timed[16],clock);
  for(uint i=0;i<27;++i)for(uint field:{8U,9U}){const uint at=8+(11+i*27+field)*4;if(READ_LE_UINT32(&timed[at]))WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);}
  WRITE_LE_UINT32(&timed[8+(11+11*27+8)*4],clock-age);const uint at=8+(11+729+601)*4;WRITE_LE_UINT32(&timed[at],READ_LE_UINT32(&timed[at])+delta);checksum(timed);
  if(!restore(timed)||!roundtrip(430))return false;++timerCases;
 }
 if(!restore(fixture))return false;debug("Astronomica P521 timer epochs: PASS (%u native save/successor cases, before/at/after periods and uint32 wrap)",timerCases);
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP521())return false;
 const uint32 voiceStart=_system->getMillis();while(_mixer->isSoundHandleActive(_soundHandle)&&_system->getMillis()-voiceStart<120000){if(canSaveP521()&&_mixer->isSoundHandleActive(_soundHandle))return false;++busy;_system->delayMillis(10);}
 const uint32 waited=_system->getMillis()-voiceStart;debug("P521 natural postwait waited%u active%d eligible%d clock%u/%u loop%d/%d last%d idle%d",waited,int(_mixer->isSoundHandleActive(_soundHandle)),int(canSaveP521()),now,scriptClock(),_loopSound,int(_loopEnabled),_lastSound,int(_runner.scriptsIdle()));if(_mixer->isSoundHandleActive(_soundHandle)||!waited||!canSaveP521()||!roundtrip())return false;debug("Astronomica P521 natural voice end: PASS (%u ms, no stopHandle)",waited);
 _loopSound=0;_loopEnabled=true;if(!playSound(0,now,true)||!_mixer->isSoundHandleActive(_soundHandle)||!canSaveP521())return false;
 Common::Array<byte>music,again;if(!snapshot(music)||!loadPlace(117))return false;const uint sounds=_soundsStarted;if(!restore(music)||_soundsStarted!=sounds+1||_lastSound!=0||!_mixer->isSoundHandleActive(_soundHandle)||!snapshot(again)||again!=music)return false;
 debug("Astronomica P521 Music restart: PASS (one ambient start)");_mixer->stopHandle(_soundHandle);if(!restore(fixture))return false;
 if(!playSound(1,now)||!_mixer->isSoundHandleActive(_soundHandle)||canSaveP521())return false;Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);if(saveGameStream(&denied).getCode()!=Common::kWritingFailed||denied.size())return false;
 _mixer->pauseHandle(_soundHandle,true);_pendingImage.create(5,3,_screen.format);_pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));_pendingImageX=19;_pendingImageY=23;_pendingImageName="P521-atomic-image";_displayedImageName="P521-atomic-display";
 auto atomic=[&](){uint32 h=fingerprint();auto add=[&](uint32 v){h=(h^v)*16777619U;};add(_runner.probeDiagnosticHash(true));for(uint32 v:{uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,_pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),uint32(_movie!=nullptr),uint32(_moviePlaying),uint32(_p521AssetsValid),uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))})add(v);for(char c:_pendingImageName)add(byte(c));for(char c:_displayedImageName)add(byte(c));add(screenRGBHash(_pendingImage,480));return h;};
 const uint32 unchanged=atomic();const void*pixels=_pendingImage.getPixels();auto reject=[&](const Common::Array<byte>&bad){Common::MemoryReadStream in(&bad[0],bad.size());return loadGameStream(&in).getCode()!=Common::kNoError&&atomic()==unchanged&&_pendingImage.getPixels()==pixels;};
 for(uint i=0;i<fixture.size();++i){Common::MemoryReadStream in(i?&fixture[0]:nullptr,i);if(loadGameStream(&in).getCode()==Common::kNoError||atomic()!=unchanged||_pendingImage.getPixels()!=pixels)return false;}
 for(uint i=0;i<fixture.size();++i){Common::Array<byte>bad=fixture;bad[i]^=1;if(!reject(bad))return false;}
 uint invalid=0;auto badWord=[&](uint index,uint32 value){Common::Array<byte>bad=fixture;WRITE_LE_UINT32(&bad[8+index*4],value);checksum(bad);if(!reject(bad)){debug("P521 invalid accepted index%u value%u",index,value);return false;}++invalid;return true;};
 for(uint index:{0U,3U,4U,5U,7U,8U,9U,10U})if(!badWord(index,index==3?538U:index==4?1U:0xffffffffU))return false;
 for(uint i=0;i<27;++i)if(!badWord(11+i*27+18,2))return false;
 for(uint i=0;i<10;++i)if(!badWord(11+(i+13)*27+4,65538U))return false;
 if(!badWord(11+729+2,0)||!badWord(11+729+301,8)||!badWord(11+729+302,1)||!badWord(11+11*27+8,now+1)||!badWord(11+10*27+19,0)||!badWord(11+13*27+23,65538U)||!badWord(11+13*27+6,1)||!badWord(11+13*27+7,1)||!badWord(11+13*27+19,150)||!badWord(11+13*27+22,50))return false;
 _pendingImage.free();_pendingImageName.clear();_displayedImageName.clear();_mixer->stopHandle(_soundHandle);if(!restore(fixture)||!canSaveP521())return false;debug("Astronomica P521 rejection verification: PASS (5392 truncations, 5392 corruptions, %u invalid states, extended atomic state)",invalid);
 for(uint mode=0;mode<4;++mode){if(!restore(fixture))return false;_runner.defineValue(0,37,mode==1?1:0);if(!roundtrip())return false;Common::Array<byte>branch;if(!snapshot(branch)||!future(mode))return false;const uint32 expected=fingerprint(),expectedClock=now,expectedEnd=_lastSuccessEnd;
  if(!restore(branch)||!future(mode)||now!=expectedClock||fingerprint()!=expected){debug("P521 future mismatch mode%u clock%u/%u end%u/%u hash%08x/%08x",mode,expectedClock,now,expectedEnd,_lastSuccessEnd,expected,fingerprint());return false;}++futures;++successors;
 }
 if(!restore(fixture)||saveGameState(18,"P521 continuation regression").getCode()!=Common::kNoError)return false;debug("Astronomica P521 slot fingerprint: %08x",fingerprint());if(!future(0))return false;
 debug("Astronomica P521 history coverage: PASS (%u choice controls, %u retained-image boundaries, %u fragment-history boundaries, %u animation boundaries, %u successor checks, %u future outcome checks)",controls,images,fragments,animations,successors,futures);
 debug("Astronomica P521 saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u ordinary boundaries, %u busy rejections)",boundaries,histories,dormant,ordinary,busy);return true;
}

bool AstronomicaEngine::verifyP521Puzzle() {
 bool ok = true;
 const int buttons[] = {103,180,270,370,475};
 for (int route = 0; route < 5; ++route) {
  _runner.resetGlobals(); ok = loadPlace(521) && ok;
  if (_scene.sprites.size() != 27) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0; bool sawMotion = false, sawFrames = false;
  auto settle = [&]() {
   for (uint pass = 0; pass < 1800 && _place == 521 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 50;
    if (_place == 521) for (uint id = 13; id < 23; ++id) {
     const Sprite &s = _scene.sprites[id];
     if (s.standardMotion && s.autoMove && (s.renderX != int16(s.x) || s.renderY != int16(s.y))) sawMotion = true;
     if (s.standardMotion && s.autoFrame && s.selectedFrame != 0) sawFrames = true;
    }
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && settle() && ok;
  ok = spriteAt(buttons[route],361) == route && ok;
  clickAtTime(buttons[route],361,now); ok = settle() && ok;
  int32 solved = -1;
  ok = _place == 521 && _runner.getValue(0,37,solved) && solved == int(route == 2) &&
   _puzzlesCompleted == completed+uint(route == 2) && ok;
  if (route == 4) {
   ok = sawMotion && sawFrames && ok;
   for (uint id = 13; id < 23; ++id) ok = !_scene.sprites[id].autoMove && !_scene.sprites[id].autoFrame && !_scene.sprites[id].visible && ok;
   ok = _scene.sprites[5].visible && _scene.sprites[11].visible && _scene.sprites[12].visible && ok;
  }
  clickAtTime(24,417,now); ok = settle() && _place == 388 && ok;
  debug("Astronomica P521 choice %d: %s (global37=%d, motion=%d, frames=%d)",route+1,ok ? "PASS" : "FAIL",solved,int(sawMotion),int(sawFrames));
 }
 debug("Astronomica P521 interaction verification: %s (five original controls, success, ten moving/animated fragments, stop and exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyEclipsePuzzle() {
 bool ok = true;
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); ok = loadPlace(528) && ok;
  if (_scene.sprites.size() != 9) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 4000 && _place == 528 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto press = [&](int button) {
   const int y = button == 4 ? 369 : button == 5 ? 404 : 439;
   const bool hit = _place == 528 && spriteAt(299,y) == button;
   clickAtTime(299,y,now); return settle() && hit;
  };
  int32 value = -1;
  if (route == 0) {
   ok = press(6) && _lastSound == 10 && _runner.getValue(1,2,value) && value == 0 && ok;
   uint32 hash = 2166136261U;
   for (int phase = 0; phase < 12; ++phase) {
    ok = press(4) && _runner.getValue(1,0,value) && value == phase && ok;
    ok = _scene.sprites[7].selectedFrame == 11-phase && ok;
    for (int quadrant = 3; quadrant >= 0; --quadrant) {
     ok = press(5) && _runner.getValue(1,1,value) && value == quadrant && ok;
     const Sprite &moon = _scene.sprites[8];
     ok = moon.x == 447 && moon.y == 48 && moon.selectedFrame == 0 && ok;
     const uint16 coordinates[] = {uint16(moon.renderX),uint16(moon.renderY)};
     for (uint i = 0; i < 2; ++i) for (uint byteIndex = 0; byteIndex < 2; ++byteIndex)
      hash = (hash ^ ((coordinates[i] >> (8*byteIndex)) & 255)) * 16777619U;
    }
   }
   // Independent hash extracted from 48 call sites in ASTRO.EXE.
   ok = hash == 0x51a72785U && ok;
   debug("Astronomica P528 position verification: %s (48 original coordinates, hash %08x)",ok ? "PASS" : "FAIL",hash);
  }
  if (route < 2) {
   const int target = route == 0 ? 0 : 6;
   for (int steps = 0; steps < 12; ++steps) {
    _runner.getValue(1,0,value); if (value == target) break;
    ok = press(4) && ok;
   }
   for (int i = 0; i < 3; ++i) ok = press(5) && ok; // 0 -> 3 -> 2 -> 1
   ok = press(6) && _lastSound == (route == 0 ? 8 : 9) && ok;
   ok = _runner.getValue(1,route == 0 ? 3 : 4,value) && value == 1 && ok;
   ok = _runner.getValue(1,2,value) && value == 0 && ok;
   // Repeating the same valid alignment does not complete both eclipses.
   ok = press(6) && _runner.getValue(1,2,value) && value == 0 && ok;
   ok = press(5) && press(5) && press(6) && ok; // 1 -> 0 -> 3
  } else {
   clickAtTime(24,417,now); ok = settle() && ok;
  }
  ok = _place == (route < 2 ? 526 : 268) && _runner.getValue(0,44,value) && value == int(route < 2) &&
   _puzzlesCompleted == completed+uint(route < 2) && ok;
  debug("Astronomica P528 route %u: %s (P%d, global44=%d)",route,ok ? "PASS" : "FAIL",_place,value);
 }
 Script custom; Command command; command.opcode = 23;
 command.args.push_back(18); for (int i = 0; i < 5; ++i) command.args.push_back(0); custom.push_back(command);
 ok = loadPlace(517) && !_runner.canRun(custom,true) && ok;
 custom[0].args[1] = 2; ok = !ScriptRunner::supports(custom,true) && ok;
 debug("Astronomica P528 interaction verification: %s (both eclipse orders, wrong/repeated alignment, solved/unsolved exits, context rejection)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyP530Puzzle() {
 bool ok = true;
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); _runner.seedRandom(100+route);
  ok = loadPlace(530) && ok;
  if (_scene.sprites.size() != 29 || _scene.scripts.size() != 11) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 4000 && _place == 530 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto click = [&](int x, int y, int expectedSprite) {
   if (_place != 530) return false;
   const bool hit = spriteAt(x,y) == expectedSprite;
   clickAtTime(x,y,now); return settle() && hit;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 11 && settle() && ok;
  uint seen = 0;
  const int answers[] = {2,4,5,1,4};
  const int x[] = {569,533,492,448,404}, y[] = {374,395,409,420,429};
  for (int round = 1; round <= 3 && route < 2 && _place == 530; ++round) {
   int32 scenario = 0, count = 0, value = 0;
   if (!_runner.getValue(1,9,scenario) || scenario < 1 || scenario > 5) return false;
   ok = _runner.getValue(1,13,count) && count == round && !(seen & (1U << scenario)) && ok;
   seen |= 1U << scenario;
   // Two independent components may be placed in either order. The
   // detector is placed last, so its original handler checks the answer.
   for (uint component = 0; component < 2; ++component) {
    const bool first = (component == 0) != (route == 1);
    if (first) { ok = click(143,354,-1) && ok; ok = click(392,189,21) && ok; }
    else { ok = click(308,395,-1) && ok; ok = click(223,80,22) && ok; }
   }
   ok = _runner.getValue(1,7,value) && value == 1 && ok;
   ok = _runner.getValue(1,8,value) && value == 1 && ok;
   const bool upper = scenario == 1 || scenario == 5;
   const int answer = answers[scenario-1];
   if (route == 0 && round == 1) {
    const int wrong = answer == 5 ? 1 : answer+1;
    ok = click(x[wrong-1],y[wrong-1],wrong+6) && ok;
    ok = click(upper ? 245 : 424,upper ? 33 : 216,upper ? 19 : 20) && ok;
    ok = _lastSound == 8 && _runner.getValue(1,12,value) && value == 0 && ok;
   }
   ok = click(x[answer-1],y[answer-1],answer+6) && ok;
   ok = click(upper ? 245 : 424,upper ? 33 : 216,upper ? 19 : 20) && ok;
   if (_place == 530 && round < 3) {
    ok = _runner.getValue(1,12,value) && value == 1 && ok;
    ok = click(542,333,4) && ok;
   }
  }
  if (route == 2) ok = click(20,443,1) && ok;
  int32 solved = -1;
  ok = _place == 228 && _runner.getValue(0,46,solved) && solved == int(route < 2) &&
   _puzzlesCompleted == completed && ok;
  if (route < 2) ok = _lastSound == 912 && ok;
  debug("Astronomica P530 route %u: %s (P%d, global46=%d, counter unchanged)",route,ok ? "PASS" : "FAIL",_place,solved);
 }
 // A repeated completion must not play the voice a second time.
 ok = loadPlace(530) && ok; _runner.defineValue(0,46,1);
 const uint sounds = _soundsStarted, completed = _puzzlesCompleted;
 Script repeat;
 for (uint i = 0; i < _scene.scripts[0].size(); ++i)
  if (_scene.scripts[0][i].opcode == 23) { Command c = _scene.scripts[0][i]; c.delay = 0; repeat.push_back(c); break; }
 ok = _runner.start(repeat,0,true) && _soundsStarted == sounds && _puzzlesCompleted == completed && ok;
 debug("Astronomica P530 interaction verification: %s (three randomized rounds, both component orders, wrong answer, unsolved exit, special success)",ok ? "PASS" : "FAIL");
 return ok;
}
// Prepared audit only: integrate declaration/caller after reviewing checkpoint.
// Does not implement saving. Movie completion is deliberately TEST-SKIPPED:
// decode a real frame, capture its index, then seek to end without decoding it.
// Foreground audio is observed, never cut to manufacture an eligible boundary.
bool AstronomicaEngine::verifyUniverseSaves() {
 uint boundaries = 0, histories = 0, dormant = 0, busy = 0, invalid = 0, ordinary = 0, naturalVoice = 0; uint32 now = 0;
 Common::Array<byte> fixture;
 bool skipMovieFrame = false, allowRejectedBoundary = false;
 auto fingerprint = [&](bool departure = false) {
  uint32 hash = 2166136261U; auto add = [&](uint32 v) { hash = (hash ^ v)*16777619U; };
  add(_place); add(_previousPlace); add(_puzzlesCompleted); add(_comet.frame); add(_comet.previousFrame);
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return uint32(0);
  for (uint i = 0; i < state.size(); ++i) if (i != 601) add(state[i]);
  for (const Sprite &s : _scene.sprites) { Common::Array<uint32> w; p526SpriteWords(s,w);
   if (departure && s.autoFrame) w[8] = now-w[8]; if (departure && s.autoMove) w[9] = now-w[9];
   for (uint32 v : w) add(v);
  }
  add(screenRGBHash(_background,480)); add(screenRGBHash(_screen,480));
  add(_movieFrame.w); add(_movieFrame.h); if (_movieFrame.w) add(screenRGBHash(_movieFrame,_movieFrame.h));
  if (_place == 529) { add(_moviePresentedFrame); add(_movieFrame.w ? _movieX : 0); add(_movieFrame.w ? _movieY : 0); add(_movieSegmentStart); add(_universeSegmentEnd); }
  return hash;
 };
 auto snapshot = [&](Common::Array<byte> &data) {
  const bool paused = _clockPaused; const uint32 oldStart = _pauseStarted;
  _clockPaused = true; _pauseStarted = now; _pausedMillis = 0;
  Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
  const bool ok = saveGameStream(&out).getCode() == Common::kNoError && out.size() == 3684;
  _clockPaused = paused; _pauseStarted = oldStart; _pausedMillis = (paused ? oldStart : _system->getMillis())-now;
  if (!ok) return false; data.resize(out.size()); memcpy(&data[0],out.getData(),out.size()); return true;
 };
 auto restore = [&](const Common::Array<byte> &data) {
  const bool paused = _clockPaused; const uint32 oldStart = _pauseStarted,oldOffset = _pausedMillis;
  _clockPaused = true; _pauseStarted = 0x23450000U;
  Common::MemoryReadStream in(&data[0],data.size()); const bool loaded = loadGameStream(&in).getCode() == Common::kNoError;
  const uint32 actual = scriptClock(); const bool clockOK = loaded ? actual == READ_LE_UINT32(&data[16]) : _pausedMillis == oldOffset;
  _clockPaused = paused; _pauseStarted = oldStart; _pausedMillis = loaded ? (paused ? oldStart : _system->getMillis())-actual : oldOffset;
  if (!clockOK) debug("Universe immediate restored/rejected clock invariant: FAIL");
  return loaded && clockOK;
 };
 auto settle = [&]() {
  for (uint n = 0; n < 10000 && _place == 529 && (!_runner.scriptsIdle() || _moviePlaying); ++n) {
   if (canSaveUniverse()) return false; ++busy;
   runScriptsAt(now); animateSpritesAt(now);
   if (_place == 529 && _moviePlaying) {
    const uint before = _movieFramesDrawn;
    if (!skipMovieFrame) updateMovie();
    if (!skipMovieFrame && (_movieFramesDrawn <= before || !_movieFrame.w || _moviePresentedFrame != _movie->getCurFrame())) return false;
    const uint32 image = screenRGBHash(_movieFrame,480); const int presented = _moviePresentedFrame;
    if (!_movie->seek(_movie->getEndTime())) return false; updateMovie();
    if (_moviePlaying || _moviePresentedFrame != presented || screenRGBHash(_movieFrame,480) != image || (skipMovieFrame && _movieFramesDrawn != before)) return false;
   }
   now += 20;
  }
  if (_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound) {
   if (_place == 529 && canSaveUniverse()) return false; ++busy;
   // Diagnostic simulation of completed speech only after guard rejection.
   _mixer->stopHandle(_soundHandle);
  }
  return _runner.scriptsIdle() && (_place != 529 || canSaveUniverse() || allowRejectedBoundary);
 };
 auto press = [&](uint id) {
  if (_place != 529 || !id || id > 7) return false;
  const Sprite &s = _scene.sprites[id-1]; int hx = -1,hy = -1;
  for (int y = MAX(0,int(s.renderY)); y < MIN(480,int(s.renderY)+48) && hx < 0; ++y)
   for (int x = MAX(0,int(s.renderX)); x < MIN(640,int(s.renderX)+96); ++x)
    if (spriteAt(x,y) == int(id)-1) { hx=x; hy=y; break; }
  if (hx < 0) return false; clickAtTime(hx,hy,now); if (canSaveUniverse()) return false; return settle();
 };
 auto step = [&](uint action) {
  Common::Array<byte> saved,again; if (!canSaveUniverse() || !snapshot(saved)) { debug("Universe snapshot rejected: P%d action%u clock%u",_place,action,now); return false; }
  const uint32 before = fingerprint(), savedNow = now; Common::Array<uint32> state; _runner.exportPersistentState(state);
  histories += _moviePresentedFrame >= 0; dormant += state[603] != 0; ordinary += state[603] == 0;
  const uint soundsBefore = _soundsStarted; if (!press(action)) return false;
  const bool departed = _place != 529; const uint32 after = fingerprint(departed),afterNow = now,sounds = _soundsStarted-soundsBefore; const int last = _lastSound;
  if (!loadPlace(117)) return false; _runner.seedRandom(77); _runner.defineValue(0,45,1234);
  ConfMan.setBool("astronomica_entry_scripts",true); const bool loaded = restore(saved); ConfMan.setBool("astronomica_entry_scripts",false);
  now = savedNow;
  if (!loaded || !canSaveUniverse() || fingerprint() != before || !snapshot(again) || again != saved) { debug("Universe restore mismatch: boundary%u action%u loaded%d canSave%d before%08x after%08x",boundaries,action,loaded,canSaveUniverse(),before,fingerprint()); return false; }
  const uint soundsRestored = _soundsStarted; if (!press(action)) return false;
  if (now != afterNow || fingerprint(departed) != after || _soundsStarted-soundsRestored != sounds || _lastSound != last) { debug("Universe successor mismatch: boundary%u action%u expected%08x actual%08x time%u/%u",boundaries,action,after,fingerprint(departed),afterNow,now); return false; }
  ++boundaries; return true;
 };
 auto select = [&](int target) {
  for (uint n = 0; n < 16; ++n) { int32 v = -1; if (!_runner.getValue(1,0,v)) return false; if (v == target) return true; if (!step(v < target ? 7 : 6)) return false; }
  int32 v = -1; return _runner.getValue(1,0,v) && v == target;
 };
 auto outcome = [&](int setting) { return select(setting) && step(5); };
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") == 14) {
  now = scriptClock(); Common::Array<uint32> state; _runner.exportPersistentState(state);
  debug("Astronomica universe slot fingerprint: %08x",fingerprint());
  bool ok = canSaveUniverse() && state[603] == 2 && state[309] == 12 && _comet.frame == 3 && _comet.previousFrame == 4;
  ok = ok && outcome(13) && outcome(9) && _place == 98 && _puzzlesCompleted == 11;
  Common::Array<uint32> after; _runner.exportPersistentState(after);
  ok = ok && after[603] == 2 && after[604] == state[604];
  debug("Astronomica universe startup save: %s (slot14, dormant round2, prior movie/readout, full-mask completion)",ok ? "PASS" : "FAIL"); return ok;
 }
 // Original controls with a first update delayed beyond the segment end.
 // Compare both absence and a retained older group's frame before/after fix.
 _runner.resetVariantSequence(); _runner.resetGlobals(); _puzzlesCompleted = 10; _comet.frame = 3; _comet.previousFrame = 4;
 if (!loadPlace(529)) return false; now = 1000;
 if (_runner.enqueueStartup(_scene.scripts,now,true) != 3 || !settle() || !press(7)) return false;
 skipMovieFrame = true; allowRejectedBoundary = true;
 if (!press(5) || _moviePresentedFrame != -1 || _movieFrame.w) return false;
 const bool firstAbsentEligible = canSaveUniverse();
 debug("Universe zero-frame first absent eligibility: %u (mask must be4, last attempted1029..1261)",uint(firstAbsentEligible));
 if (firstAbsentEligible && (!step(7) || !step(6))) return false;
 skipMovieFrame = false;
 if (!press(5) || _moviePresentedFrame < 215 || _moviePresentedFrame > 252) return false;
 const int olderFrame = _moviePresentedFrame; const uint32 olderHash = screenRGBHash(_movieFrame,480);
 for (uint setting = 2; setting <= 6; ++setting) if (!press(7)) return false;
 skipMovieFrame = true;
 if (!press(5) || _moviePresentedFrame != olderFrame || screenRGBHash(_movieFrame,480) != olderHash) return false;
 const bool priorResidualEligible = canSaveUniverse();
 debug("Universe zero-frame prior residual eligibility: %u (mask must be12, digits015, older group1 frame%d, attempted720..946)",uint(priorResidualEligible),olderFrame);
 if (!firstAbsentEligible || !priorResidualEligible) { debug("Universe zero-frame settled boundary coverage: FAIL (first%d prior%d)",firstAbsentEligible,priorResidualEligible); return false; }
 if (!step(7) || !step(6)) return false;
 skipMovieFrame = false; allowRejectedBoundary = false;
 debug("Astronomica universe zero-frame history: PASS (first absent and prior-group residual, roundtrip and successor)");
 for (uint route = 0; route < 3; ++route) {
  if (loadGameState(99).getCode() != Common::kNoError) return false;
  _runner.resetGlobals(); _puzzlesCompleted = 10; _comet.frame = 3; _comet.previousFrame = 4;
  if (!loadPlace(529)) return false; now = 1000;
  if (_runner.enqueueStartup(_scene.scripts,now,true) != 3 || !settle()) return false;
  if (route == 0) {
   if (!step(1) || !step(3) || !step(4) || !step(6) || !step(5) || !select(15) || !step(7) ||
       !outcome(1) || !step(5) || !select(15) || !select(0) || !step(5) || !outcome(6) || !step(5) || !select(0)) return false;
   if (!snapshot(fixture) || saveGameState(14,"Universe continuation regression").getCode() != Common::kNoError) return false;
   debug("Astronomica universe slot fingerprint: %08x",fingerprint());
   if (!outcome(13) || !step(5) || !outcome(9)) return false;
  } else if (route == 1) { if (!outcome(6) || !step(5) || !select(0) || !step(2)) return false; }
  else { if (!outcome(1) || !step(5) || !select(15) || !select(0) || !step(2)) return false; }
  int32 solved = -1, unlocked = -1;
  if (_place != 98 || _puzzlesCompleted != 10+uint(route != 2) || !_runner.getValue(0,45,solved) || solved != int(route != 2) || !_runner.getValue(0,60,unlocked) || unlocked != int(route != 2)) return false;
 }
 // Ordinary state comes from a reset, never from a dormant physical fixture.
 _runner.resetVariantSequence(); _runner.resetGlobals(); _puzzlesCompleted = 10;
 if (!loadPlace(529)) return false; now = 1000;
 if (_runner.enqueueStartup(_scene.scripts,now,true) != 3 || !settle()) return false;
 Common::Array<uint32> ordinaryState; if (!_runner.exportPersistentState(ordinaryState) || ordinaryState[603] || ordinaryState[604]) return false;
 // Let one actual native voice finish naturally; do not stopHandle in this case.
 if (!playSound(1,now) || !_mixer->isSoundHandleActive(_soundHandle) || canSaveUniverse()) return false;
 Common::MemoryWriteStreamDynamic denied(DisposeAfterUse::YES);
 if (saveGameStream(&denied).getCode() != Common::kWritingFailed || denied.size()) return false;
 const uint32 voiceStarted = _system->getMillis();
 while (_mixer->isSoundHandleActive(_soundHandle) && _system->getMillis()-voiceStarted < 120000) {
  if (canSaveUniverse()) return false; ++busy; _system->delayMillis(10);
 }
 const uint32 waited = _system->getMillis()-voiceStarted; now += waited;
 if (_mixer->isSoundHandleActive(_soundHandle) || !waited || !canSaveUniverse()) return false;
 ++naturalVoice;
 debug("Astronomica universe natural voice end: PASS (%u ms, ordinary round0, no stopHandle)",waited);
 if (!step(6) || !select(15) || !step(7) || !outcome(13) || !step(5) || !select(0) || !step(2) || _place != 98 || _puzzlesCompleted != 10) return false;
 if (fixture.size() != 3684 || !restore(fixture)) return false; now = READ_LE_UINT32(&fixture[16]);
 // Ambient restart must start exactly one loop, without replaying narration.
 _loopSound = 0; _loopEnabled = true;
 if (!playSound(0,now,true) || !_mixer->isSoundHandleActive(_soundHandle) || !canSaveUniverse()) return false;
 Common::Array<byte> music; if (!snapshot(music) || !loadPlace(117)) return false;
 const uint sounds = _soundsStarted;
 if (!restore(music) || !canSaveUniverse() || _soundsStarted != sounds+1 || _lastSound != 0 || !_loopEnabled || !_mixer->isSoundHandleActive(_soundHandle)) return false;
 Common::Array<byte> musicAgain; if (!snapshot(musicAgain) || musicAgain != music) return false;
 debug("Astronomica universe Music restart: PASS (one ambient start, no entry narration)");
 _mixer->stopHandle(_soundHandle);
 if (!restore(fixture)) return false; now = READ_LE_UINT32(&fixture[16]);
 // Populate image/audio sentinels so rejection checks observe more than zero
 // defaults. Pause only the mixer handle and script clock for stable sampling.
 if (!playSound(1,now) || !_mixer->isSoundHandleActive(_soundHandle) || canSaveUniverse()) return false;
 Common::MemoryWriteStreamDynamic foregroundDenied(DisposeAfterUse::YES);
 if (saveGameStream(&foregroundDenied).getCode() != Common::kWritingFailed || foregroundDenied.size()) return false;
 _mixer->pauseHandle(_soundHandle,true);
 _pendingImage.create(5,3,_screen.format); _pendingImage.fillRect(Common::Rect(5,3),_screen.format.RGBToColor(17,33,65));
 _pendingImageX = 19; _pendingImageY = 23; _pendingImageName = "universe-atomic-image-sentinel"; _displayedImageName = "universe-atomic-display-sentinel";
 const bool oldPaused = _clockPaused; const uint32 oldPauseStarted = _pauseStarted,oldOffset = _pausedMillis;
 _clockPaused = true; _pauseStarted = 0x34560000U;
 auto atomic = [&]() {
  uint32 hash = fingerprint(); auto add = [&](uint32 v) { hash = (hash ^ v)*16777619U; };
  for (uint32 v : {uint32(_previousPlace),uint32(_loopSound),uint32(_loopEnabled),_lastSoundAt,uint32(_lastSound),_soundsStarted,
       _pausedMillis,_pauseStarted,uint32(_clockPaused),scriptClock(),_lastSuccessEnd,_lastBlockingSoundEnd,
       uint32(_pendingImageX),uint32(_pendingImageY),uint32(_pendingImage.w),uint32(_pendingImage.h),
       uint32(_movie != nullptr),uint32(_moviePlaying),uint32(_moviePresentedFrame),_movieFramesDrawn,_movieSegmentStart,_universeSegmentEnd,uint32(_universeAssetsValid),
       uint32(_movieX),uint32(_movieY),uint32(_worldMovieCursorBottom),uint32(_runner.pendingCount()),uint32(_runner.clicksBlocked()),uint32(_runner.scriptsIdle()),uint32(_runner.idle()),
       uint32(_mixer->isSoundHandleActive(_soundHandle)),_mixer->getSoundElapsedTime(_soundHandle),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)),uint32(_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType))}) add(v);
  Common::Array<uint32> state; if (!_runner.exportPersistentState(state)) return uint32(0); for (uint32 v : state) add(v);
  for (char c : _pendingImageName) add(byte(c)); add(0); for (char c : _displayedImageName) add(byte(c));
  add(screenRGBHash(_pendingImage,480));
  if (_movie) { add(_movie->getCurFrame()); add(_movie->getTime()); add(_movie->getEndTime().msecs()); add(_movie->isPlaying()); add(_movie->isPaused()); add(_movie->getVolume()); }
  return hash;
 };
 const uint32 unchanged = atomic(); Video::QuickTimeDecoder *const savedMovie = _movie; const void *const pendingPixels = _pendingImage.getPixels();
 auto unchangedAll = [&]() { return atomic() == unchanged && _movie == savedMovie && _pendingImage.getPixels() == pendingPixels; };
 for (uint length = 0; length < fixture.size(); ++length) { Common::MemoryReadStream in(&fixture[0],length); if (loadGameStream(&in).getCode() == Common::kNoError || !unchangedAll()) { debug("Universe atomic truncation mismatch: %u",length); return false; } }
 for (uint at = 0; at < fixture.size(); ++at) { Common::Array<byte> bad = fixture; bad[at] ^= 0x80; Common::MemoryReadStream in(&bad[0],bad.size()); if (loadGameStream(&in).getCode() == Common::kNoError || !unchangedAll()) { debug("Universe atomic corruption mismatch: %u",at); return false; } }
 auto badWord = [&](uint word, uint32 v) {
  Common::Array<byte> bad = fixture; WRITE_LE_UINT32(&bad[8+4*word],v); uint32 hash = 2166136261U;
  for (uint at = 8; at < bad.size()-4; at += 4) hash = (hash ^ READ_LE_UINT32(&bad[at]))*16777619U;
  WRITE_LE_UINT32(&bad[bad.size()-4],hash); Common::MemoryReadStream in(&bad[0],bad.size());
  if (loadGameStream(&in).getCode() == Common::kNoError || !unchangedAll()) { debug("Universe atomic invalid-field mismatch: %u",word); return false; } ++invalid; return true;
 };
 const uint32 invalidWords[][2] = {{0,528},{3,538},{4,2},{5,2},{7,2},{8,253},{8,214},{9,159},{10,41},{11,360},{12,945},{13,0},{14,13},{15,1},
       {16+7*27+1,16},{16+9*27+2,445},{16+10*27+1,9},{16+8*27+6,1},{16+9*27+8,0},{16+8*27+19,20},
       {16+297+300,16},{16+297+303,0},{16+297+306,0},{16+297+309,15},{16+297+603,4}};
 for (const auto &entry : invalidWords) if (!badWord(entry[0],entry[1])) return false;
 _clockPaused = oldPaused; _pauseStarted = oldPauseStarted; _pausedMillis = oldOffset;
 _mixer->pauseHandle(_soundHandle,false); _mixer->stopHandle(_soundHandle);
 _pendingImage.free(); _pendingImageName.clear(); _displayedImageName.clear();
 if (!restore(fixture) || !canSaveUniverse()) return false;
 debug("Astronomica universe extra guards: PASS (%u ordinary boundaries, %u natural voice ends, Music restart, foreground rejection, extended atomic state)",ordinary,naturalVoice);
 debug("Astronomica universe saves: PASS (%u boundaries, %u history boundaries, %u dormant boundaries, %u busy rejections, 3684 truncations, 3684 corruptions, %u invalid states, test-skipped movies)",boundaries,histories,dormant,busy,invalid);
 return true;
}


bool AstronomicaEngine::verifyUniverseBoundaries() {
 uint boundaries = 0, movies = 0, seekChanges = 0, foreground = 0, repeated = 0;
 uint32 selectors = 0, controls = 0, now = 0;
 int auditLastPresented = -1;
 auto value = [&](uint index) { int32 v = -1; return _runner.getValue(1,index,v) ? v : int32(-1); };
 auto movieHash = [&]() { return _movieFrame.w ? screenRGBHash(_movieFrame,_movieFrame.h) : uint32(0); };
 auto candidate = [&]() {
  if (_place != 529 || _scene.sprites.size() != 11 || !_movie || _moviePlaying ||
      !_runner.scriptsIdle() || _pendingImage.w) return false;
  for (uint i = 0; i < 11; ++i)
   if (_scene.sprites[i].autoFrame || _scene.sprites[i].autoMove) return false;
  return true;
 };
 debug("Universe audit schema: header boundary route control clock selector local1 local2 mask completed previousPlace scriptsIdle pending clicksBlocked foreground moviePlaying moviePresent frameWidth frameHeight movieX movieY frameHash screen480Hash background480Hash decoderCurFrame observedPresentedFrame framesDrawn segmentStart movieTimeMs endTimeMs lastSound loopSound loopEnabled lastSoundAt successEnd blockingEnd");
 debug("Universe audit schema: persistent boundary wordCount words[605]; sprite boundary zeroBasedId wordCount words[27]");
 debug("Universe audit schema: test-skipped-movie route clock segmentStart endTimeMs decodedFrame decoderAfterSeek frameHash retainedHash framesDrawn");
 // Actual original frames, decoded by ScummVM; no playback/audio start.
 // Compare each sought sample against uninterrupted sequential decoding in
 // the exact native screen pixel format, including all VFR long-held samples.
 {
  Video::QuickTimeDecoder sequential, sought;
  auto open = [&](Video::QuickTimeDecoder &decoder) {
   Common::File *file = new Common::File();
   const Common::Path path = ConfMan.getPath("path").join(Common::Path("PLACES/P529/FUNIV.MOV"));
   if (!file->open(Common::FSNode(path))) { delete file; return false; }
   if (!decoder.loadStream(file)) return false;
   decoder.setVolume(0);
   return decoder.isSeekable() && decoder.getFrameCount() == 253 &&
    decoder.getTimeScale() == 30 && decoder.getWidth() == 320 && decoder.getHeight() == 240;
  };
  if (!open(sequential) || !open(sought)) return false;
  for (uint i = 0; i < 253; ++i) {
   const Graphics::Surface *a = sequential.decodeNextFrame();
   if (!a || sequential.getCurFrame() != int(i) || !sought.seekToFrame(i)) return false;
   const Graphics::Surface *b = sought.decodeNextFrame();
   if (!b || sought.getCurFrame() != int(i)) return false;
   Graphics::Surface *ar = a->convertTo(_screen.format,sequential.getPalette());
   Graphics::Surface *br = b->convertTo(_screen.format,sought.getPalette());
   if (!ar || !br) { if (ar) { ar->free(); delete ar; } if (br) { br->free(); delete br; } return false; }
   bool same = ar->w == br->w && ar->h == br->h;
   for (int y = 0; same && y < ar->h; ++y)
    same = !memcmp(ar->getBasePtr(0,y),br->getBasePtr(0,y),ar->w*ar->format.bytesPerPixel);
   debug("Universe audit original-sample: %u %08x %08x %u",i,screenRGBHash(*ar,ar->h),screenRGBHash(*br,br->h),uint(same));
   ar->free(); delete ar; br->free(); delete br;
   if (!same) return false;
  }
  debug("Astronomica universe original-frame reconstruction: PASS (253 sequential versus seekToFrame native pixel comparisons; stopped decoders)");
 }
 auto record = [&](uint route, int control) {
  if (!candidate()) return false;
  Common::Array<uint32> state;
  if (!_runner.exportPersistentState(state) || state.size() != 605) return false;
  const int32 setting = value(0);
  if (setting < 0 || setting > 15 || _scene.sprites[7].selectedFrame != setting) return false;
  const bool sound = _mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound;
  if (sound) ++foreground;
  selectors |= 1U << uint(setting);
  presentScene();
  debug("Universe audit header: %u %u %d %u %d %d %d %d %u %d %u %u %u %u %u %u %d %d %d %d %08x %08x %08x %d %d %u %u %u %u %d %d %u %u %u %u",
   boundaries,route,control,now,setting,value(1),value(2),value(3),_puzzlesCompleted,_previousPlace,
   uint(_runner.scriptsIdle()),_runner.pendingCount(),uint(_runner.clicksBlocked()),uint(sound),
   uint(_moviePlaying),uint(_movieFrame.w != 0),_movieFrame.w,_movieFrame.h,_movieX,_movieY,
   movieHash(),screenRGBHash(_screen,480),screenRGBHash(_background,480),_movie->getCurFrame(),auditLastPresented,
   _movieFramesDrawn,_movieSegmentStart,_movie->getTime(),uint32(_movie->getEndTime().msecs()),
   _lastSound,_loopSound,uint(_loopEnabled),_lastSoundAt,_lastSuccessEnd,_lastBlockingSoundEnd);
  Common::String persistent = Common::String::format("Universe audit persistent: %u %u",boundaries,state.size());
  for (uint32 word : state) persistent += Common::String::format(" %u",word);
  debug("%s",persistent.c_str());
  for (uint i = 0; i < 11; ++i) {
   Common::Array<uint32> words; p526SpriteWords(_scene.sprites[i],words);
   if (words.size() != 27) return false;
   Common::String line = Common::String::format("Universe audit sprite: %u %u %u",boundaries,i,words.size());
   for (uint32 word : words) line += Common::String::format(" %d",int32(word));
   debug("%s",line.c_str());
  }
  ++boundaries;
  return true;
 };
 auto settle = [&](uint route) {
  for (uint pass = 0; pass < 4000 && _place == 529 &&
       (_runner.pendingCount() || _moviePlaying); ++pass) {
   runScriptsAt(now); animateSpritesAt(now);
   if (_place != 529) break;
   if (_moviePlaying) {
    if (!_movie) return false;
    const uint frames = _movieFramesDrawn;
    updateMovie();
    if (!_moviePlaying || _movieFramesDrawn <= frames || !_movieFrame.w) return false;
    auditLastPresented = _movie->getCurFrame();
    const uint32 beforeHash = movieHash();
    const int width = _movieFrame.w, height = _movieFrame.h;
    const uint32 end = uint32(_movie->getEndTime().msecs());
    if (!_movie->seek(_movie->getEndTime())) return false;
    const int afterSeek = _movie->getCurFrame();
    updateMovie();
    if (_moviePlaying || _movieFrame.w != width || _movieFrame.h != height || movieHash() != beforeHash) return false;
    if (afterSeek != auditLastPresented) ++seekChanges;
    ++movies;
    debug("Universe audit test-skipped-movie: %u %u %u %u %d %d %08x %08x %u",
     route,now,_movieSegmentStart,end,auditLastPresented,afterSeek,beforeHash,movieHash(),_movieFramesDrawn);
   }
   now += 20;
  }
  return _place == 529 ? candidate() : _runner.scriptsIdle();
 };
 auto press = [&](uint route, uint id, bool capture = true) {
  if (_place != 529 || !id || id > 7) return false;
  const Sprite &s = _scene.sprites[id-1];
  int hitX = -1, hitY = -1;
  for (int y = MAX(0,int(s.renderY)); y < MIN(480,int(s.renderY)+48) && hitX < 0; ++y)
   for (int x = MAX(0,int(s.renderX)); x < MIN(640,int(s.renderX)+96); ++x)
    if (spriteAt(x,y) == int(id)-1) { hitX = x; hitY = y; break; }
  if (hitX < 0) return false;
  controls |= 1U << (id-1);
  clickAtTime(hitX,hitY,now);
  if (!settle(route)) return false;
  return !capture || _place != 529 || record(route,int(id));
 };
 auto select = [&](uint route, int target) {
  if (target < 0 || target > 15) return false;
  for (uint guard = 0; guard < 16 && value(0) != target; ++guard) {
   const int32 old = value(0), expected = old+(old < target ? 1 : -1);
   if (!press(route,old < target ? 7 : 6) || value(0) != expected) return false;
  }
  return value(0) == target;
 };
 auto outcome = [&](uint route, int setting, int mask, bool repeat) {
  if (!select(route,setting)) return false;
  const uint32 beforeCompleted = _puzzlesCompleted;
  if (!press(route,5)) return false;
  if (_place == 529) {
   if (value(3) != mask || _scene.sprites[8].selectedFrame != 0 ||
       _scene.sprites[9].selectedFrame != (setting >= 6 && setting <= 8 ? 1 : 0) ||
       _scene.sprites[10].selectedFrame != (setting >= 13 ? 2 : 5)) return false;
   if (repeat) {
    if (!press(route,5) || value(3) != mask || _puzzlesCompleted != beforeCompleted) return false;
    ++repeated;
   }
  }
  return true;
 };
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals();
  if (!loadPlace(529) || !_movie || _scene.sprites.size() != 11) return false;
  now = 0; auditLastPresented = -1;
  const uint completed = _puzzlesCompleted;
  if (_runner.enqueueStartup(_scene.scripts,0,true) != 3 || !settle(route) || !record(route,0)) return false;
  if (route == 0) {
   // Every original control, both clamps, every selector and no-outcome0.
   if (!press(route,1) || !press(route,3) || !press(route,4) ||
       !press(route,6) || value(0) != 0 || !press(route,5) || movies != 0 ||
       !select(route,15) || !press(route,7) || value(0) != 15) return false;
   if (!outcome(route,1,4,true)) return false;
   // Traverse all selectors again with retained prior result/movie state.
   if (!select(route,15) || !select(route,0) || !press(route,5) || value(3) != 4 ||
       !outcome(route,6,12,true) || value(2) != 1 ||
       !outcome(route,13,14,true) || !outcome(route,9,15,false)) return false;
  } else if (route == 1) {
   // Early success: local2 set by group6..8 although mask only8.
   if (!outcome(route,6,8,true) || value(2) != 1 || !select(route,0) ||
       value(3) != 8 || !press(route,2)) return false;
  } else {
   // Repeated unsuccessful outcome, all selector histories, unsolved exit.
   if (!outcome(route,1,4,true) || value(2) != 0 || !select(route,15) ||
       !select(route,0) || value(3) != 4 || !press(route,2)) return false;
  }
  const int global = ScriptRunner::successGlobalForPlace(529);
  int32 solved = -1, unlocked = -1;
  if (_place != 98 || !_runner.getValue(0,global,solved) || solved != int(route != 2) ||
      !_runner.getValue(0,60,unlocked) || unlocked != int(route != 2) ||
      _puzzlesCompleted != completed+uint(route != 2)) return false;
  debug("Universe audit destination: %u %u %d %d %d %d %u",route,now,_place,global,solved,unlocked,_puzzlesCompleted);
 }
 if (boundaries <= 50 || selectors != 0xffffU || controls != 0x7fU || repeated != 5 || !movies) return false;
 debug("Astronomica universe boundary verification: PASS (%u boundaries, %u test-skipped movies, %u decoder-index changes, %u foreground boundaries, %u repeated outcomes, all16 selectors, all7 controls, three routes; independent boundary/frame audit)",
  boundaries,movies,seekChanges,foreground,repeated);
 _runner.resetGlobals();
 return loadPlace(103);
}


bool AstronomicaEngine::verifyUniversePuzzle() {
 bool ok = true;
 uint movies = 0;
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); ok = loadPlace(529) && ok;
  if (!_movie || _scene.sprites.size() != 11) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 4000 && _place == 529 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now);
    if (_moviePlaying) {
     const uint frames = _movieFramesDrawn; updateMovie();
     ok = _movieFramesDrawn > frames && ok; ++movies;
     _movie->seek(_movie->getEndTime()); updateMovie(); ok = !_moviePlaying && ok;
    }
    now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto select = [&](int target) {
   int32 current = -1;
   ok = _runner.getValue(1,0,current) && ok;
   while (current != target && _place == 529) {
    const int direction = current < target ? 1 : -1;
    const int x = direction > 0 ? 216 : 120;
    ok = spriteAt(x,428) == (direction > 0 ? 6 : 5) && ok;
    clickAtTime(x,428,now); ok = settle() && ok;
    const int32 expected = current+direction;
    if (!_runner.getValue(1,0,current) || current != expected) return false;
    ok = _scene.sprites[7].selectedFrame == current && ok;
   }
   return current == target;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && settle() && ok;
  int32 value = -1;
  if (route == 0) {
   clickAtTime(120,428,now); ok = settle() && _runner.getValue(1,0,value) && value == 0 && ok;
   clickAtTime(282,398,now); ok = settle() && movies == 0 && ok;
   ok = select(15) && ok;
   clickAtTime(216,428,now); ok = settle() && _runner.getValue(1,0,value) && value == 15 && ok;
  }
  const int settings[] = {1,6,13,9};
  const int flags[] = {4,12,14,15};
  const int targets = route == 0 ? 4 : 1;
  for (int i = 0; i < targets && _place == 529; ++i) {
   const int setting = route == 1 ? 6 : settings[i];
   ok = select(setting) && ok;
   ok = spriteAt(282,398) == 4 && ok;
   clickAtTime(282,398,now); ok = settle() && ok;
   if (_place == 529) {
    ok = _runner.getValue(1,3,value) && value == (route == 1 ? 8 : flags[i]) && ok;
    ok = !_scene.sprites[8].autoFrame && !_scene.sprites[9].autoFrame && !_scene.sprites[10].autoFrame && ok;
    ok = _scene.sprites[8].selectedFrame == 0 && _scene.sprites[9].selectedFrame == (setting == 6 ? 1 : 0) &&
     _scene.sprites[10].selectedFrame == (setting == 13 ? 2 : 5) && ok;
   }
  }
  if (route != 0) { clickAtTime(24,417,now); ok = settle() && ok; }
  const int global = ScriptRunner::successGlobalForPlace(529);
  ok = _place == 98 && _runner.getValue(0,global,value) && value == int(route != 2) &&
   _puzzlesCompleted == completed+uint(route != 2) && ok;
  debug("Astronomica P529 route %u: %s (P%d, global%d=%d)",route,ok ? "PASS" : "FAIL",_place,global,value);
  ok = _runner.getValue(0,60,value) && value == int(route != 2) && ok;
 }
 ok = movies == 6 && ok;
 // Isolated repeat-success check: the extra unlock must be restored even
 // when global45 already suppresses the sound/counter increment.
 ok = loadPlace(529) && ok;
 _runner.defineValue(0,45,1); _runner.defineValue(0,60,0);
 const uint beforeRepeat = _puzzlesCompleted;
 Script repeat;
 for (uint i = 0; i < _scene.scripts[1].size(); ++i)
  if (_scene.scripts[1][i].opcode == 23) { Command c = _scene.scripts[1][i]; c.delay = 0; repeat.push_back(c); break; }
 int32 unlocked = 0;
 ok = _runner.start(repeat,0,true) && _runner.getValue(0,60,unlocked) && unlocked == 1 &&
  _puzzlesCompleted == beforeRepeat && ok;
 debug("Astronomica P529 interaction verification: %s (all four outcomes, zero/maximum bounds, animation stop, full and early success, unsolved exit)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifySolarPuzzle() {
 bool ok = true;
 const int expected[][3] = {{291,131,5},{286,125,4},{281,112,3},{282,115,3},{277,110,2},{270,94,1},{263,82,0}};
 uint segmentsDecoded = 0;
 for (uint route = 0; route < 2; ++route) {
  _runner.resetGlobals(); ok = loadPlace(525) && ok;
  if (!_movie || _scene.sprites.size() != 22 || _scene.mouseRects.size() != 1) return false;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 6000 && _place == 525 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now);
    if (_moviePlaying) {
     const uint frames = _movieFramesDrawn;
     updateMovie();
     ok = _movieFramesDrawn > frames && _movieFrame.w > 0 && ok;
     ++segmentsDecoded;
     // Route verification only: decode the selected start, then seek its
     // end. Continuous playback has a separate development check.
     _movie->seek(_movie->getEndTime()); updateMovie();
     ok = !_moviePlaying && ok;
    }
    now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 5 && settle() && ok;
  int32 value = -1;
  ok = _runner.getValue(1,1,value) && value == 0 && ok;
  const int iterations = route == 0 ? 7 : 2;
  for (int experiment = 1; experiment <= iterations && _place == 525; ++experiment) {
   const int choice = route == 0 ? experiment : 1;
   for (int step = 1; step <= choice; ++step) {
    ok = spriteAt(110,385) == 21 && ok;
    clickAtTime(110,385,now); ok = settle() && ok;
    ok = _runner.getValue(1,1,value) && value == step && ok;
    const Sprite &indicator = _scene.sprites[20];
    ok = indicator.renderX == expected[step-1][0] && indicator.renderY == expected[step-1][1] &&
     indicator.selectedFrame == expected[step-1][2] && ok;
   }
   if (choice == 7) {
    clickAtTime(110,385,now); ok = settle() && _runner.getValue(1,1,value) && value == 7 && ok;
   }
   ok = spriteAt(358,422) == -1 && ok;
   clickAtTime(358,422,now); ok = settle() && ok;
   if (_place == 525) {
    ok = _runner.getValue(1,choice+1,value) && value == 1 && ok;
    ok = _runner.getValue(1,1,value) && value == 0 && ok;
    // Every video branch ends with an explicit sky_b image update.
    if (choice == 4 || choice == 5 || choice == 7) ok = !_movieFrame.w && ok;
   }
  }
  if (route == 1) { clickAtTime(24,417,now); ok = settle() && ok; }
  const int global = ScriptRunner::successGlobalForPlace(525);
  ok = _place == (route == 0 ? 509 : 304) && _runner.getValue(0,global,value) &&
   value == int(route == 0) && _puzzlesCompleted == completed+uint(route == 0) && ok;
  debug("Astronomica P525 route %u: %s (P%d, global%d=%d)",route,ok ? "PASS" : "FAIL",_place,global,value);
 }
 ok = segmentsDecoded == 4 && ok;
 debug("Astronomica P525 interaction verification: %s (seven experiments, selector bounds, repeated experiment, four decoded segments, solved/unsolved exits)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyMoveFrameCommand() {
 bool ok = loadPlace(525);
 if (!ok || _scene.sprites.size() != 22) return false;
 const int expected[][3] = {{291,131,5},{286,125,4},{281,112,3},{282,115,3},{277,110,2},{270,94,1},{263,82,0}};
 uint count = 0;
 const Script original = _scene.sprites[21].click;
 for (uint i = 0; i < original.size(); ++i) {
  if (original[i].opcode != 24) continue;
  Command command = original[i]; command.delay = 0;
  if (count >= ARRAYSIZE(expected) || command.args.size() != 4 || command.args[0] != 21) return false;
  Sprite &target = _scene.sprites[20];
  target.frameSince = 123;
  const bool visible = target.visible, frames = target.autoFrame, moves = target.autoMove;
  Script program; program.push_back(command);
  ok = _runner.start(program,0,true) && ok; applyScriptActions(0);
  ok = target.x == expected[count][0] && target.y == expected[count][1] &&
   target.renderX == expected[count][0] && target.renderY == expected[count][1] &&
   target.selectedFrame == expected[count][2] && target.frameSince == 123 &&
   bool(target.visible) == visible && target.autoFrame == frames && target.autoMove == moves && ok;
  program[0].args[3] = spriteFrameCount(_scene,20);
  ok = !_runner.canRun(program,true) && ok;
  program[0].args[3] = -1; ok = !_runner.canRun(program,true) && ok;
  program[0].args[3] = 0; program[0].args[0] = 999; ok = !_runner.canRun(program,true) && ok;
  ++count;
 }
 ok = count == ARRAYSIZE(expected) && ok;
 debug("Astronomica move/frame command verification: %s (seven original P525 commands, stored/render positions, frames, timer/visibility preservation, invalid targets)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifyAuroraPuzzle() {
 bool ok = true;
 _runner.resetGlobals();
 const uint completed = _puzzlesCompleted;
 ok = loadPlace(517) && _runner.enqueueStartup(_scene.scripts,0,true) == 2 && ok;
 uint32 now = 0;
 auto settle = [&]() {
  for (uint pass = 0; pass < 2000 && _place == 517 && _runner.pendingCount(); ++pass) {
   runScriptsAt(now); animateSpritesAt(now); now += 20;
  }
  return !_runner.pendingCount() && !_runner.clicksBlocked();
 };
 const int levels[] = {4,3,2,1,2,3,4,3,2,1,2,3,4,3};
 const int markerX[] = {72,87,98,114,131,140,158,174,185,201,216,225,244,261};
 const int markerY[] = {368,390,413,429,411,388,370,386,408,425,408,386,368,384};
 const int gaugeX[] = {447,477,507,536};
 auto check = [&](int value) {
  int32 actual = 0, level = 0;
  bool valid = _place == 517 && _runner.getValue(1,1,actual) && actual == value &&
   _runner.getValue(1,0,level) && level == levels[value-1];
  valid = valid && _scene.sprites[7].renderX == markerX[value-1] &&
   _scene.sprites[7].renderY == markerY[value-1] && _scene.sprites[6].renderX == gaugeX[levels[value-1]-1];
  for (uint index = 8; index < 11; ++index) {
   const bool active = levels[value-1] == int(index)-6;
   valid = bool(_scene.sprites[index].visible) == active && _scene.sprites[index].autoFrame == active && valid;
  }
  return valid;
 };
 ok = settle() && check(4) && ok;
 for (int value = 3; value >= 1; --value) { clickAtTime(319,420,now); ok = settle() && check(value) && ok; }
 clickAtTime(319,420,now); ok = settle() && check(1) && ok;
 for (int value = 2; value <= 14; ++value) {
  clickAtTime(319,369,now); ok = settle() && check(value) && ok;
  if (value == 3) {
   Sprite &animated = _scene.sprites[8];
   const int frame = animated.selectedFrame;
   const uint32 since = animated.frameSince;
   ok = !advanceSpriteFrame(animated,4,since+99) && advanceSpriteFrame(animated,4,since+100) &&
    animated.selectedFrame == (frame+1)%4 && ok;
   now = MAX(now,animated.frameSince);
  }
 }
 clickAtTime(319,369,now); settle();
 int32 solved = -1;
 ok = _place == 512 && _runner.getValue(0,33,solved) && solved == 1 && _puzzlesCompleted == completed+1 && ok;
 debug("Astronomica P517 complete route: %s (14 settings, clamped minimum, animation timing, P512, global33=%d)",ok ? "PASS" : "FAIL",solved);
 _runner.resetGlobals(); ok = loadPlace(517) && ok;
 clickAtTime(24,417,now); settle();
 ok = _place == 157 && _runner.getValue(0,33,solved) && solved == 0 && ok;
 debug("Astronomica P517 interaction verification: %s (original initial state, both controls, solved and unsolved exits)",ok ? "PASS" : "FAIL");
 return ok;
}
bool AstronomicaEngine::verifySpectrumPuzzle() {
 bool ok = true;
 // Check the actual flash pixels and restoration separately from route logic.
 ok = loadPlace(519) && ok;
 const uint32 before = screenRGBHash(_screen);
 Command flash; flash.opcode = 21; Script white; white.push_back(flash);
 ok = _runner.start(white,0,true) && ok; applyScriptActions(0);
 const uint32 whitePixel = _screen.format.RGBToColor(255,255,255);
 for (int y = 0; y < 480; ++y) for (int x = 0; x < 640; ++x)
  ok = _screen.getPixel(x,y) == whitePixel && ok;
 redrawSprites(); ok = screenRGBHash(_screen) == before && ok;
 for (uint route = 0; route < 3; ++route) {
  _runner.resetGlobals(); ok = loadPlace(519) && ok;
  const uint completed = _puzzlesCompleted;
  uint32 now = 0;
  auto settle = [&]() {
   for (uint pass = 0; pass < 3000 && _place == 519 && _runner.pendingCount(); ++pass) {
    runScriptsAt(now); animateSpritesAt(now); now += 20;
   }
   return !_runner.pendingCount() && !_runner.clicksBlocked();
  };
  auto clickRect = [&](uint index) {
   const MouseRect &rect = _scene.mouseRects[index];
   const int x = (rect.rect[0]+rect.rect[2])/2, y = (rect.rect[1]+rect.rect[3])/2;
   ok = spriteAt(x,y) == -1 && ok;
   clickAtTime(x,y,now); ok = settle() && ok;
  };
  ok = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && settle() && ok;
  // Wrong pairing: low-frequency detector aimed at the Sun flashes white.
  clickRect(6); clickRect(3);
  int32 solved = -1;
  for (int id = 2; id <= 6; ++id) ok = _runner.getValue(1,id,solved) && solved == 0 && ok;
  if (route < 2) {
   const uint detector[] = {9,7,5,6,8};
   const uint target[] = {1,3,4,0,2};
   for (uint step = 0; step < 5 && _place == 519; ++step) {
    const uint pair = route == 0 ? step : 4-step;
    clickRect(detector[pair]); clickRect(target[pair]);
    if (_place == 519) ok = _runner.getValue(1,pair+2,solved) && solved == 1 && ok;
   }
  } else {
   clickAtTime(24,417,now); ok = settle() && ok;
  }
  ok = _place == 281 && _runner.getValue(0,35,solved) && solved == int(route < 2) &&
   _puzzlesCompleted == completed+uint(route < 2) && ok;
  debug("Astronomica P519 route %u: %s (P%d, global35=%d)",route,ok ? "PASS" : "FAIL",_place,solved);
 }
 debug("Astronomica P519 interaction verification: %s (five original pairings, two orders, wrong Sun pairing, flash and unsolved exit)",ok ? "PASS" : "FAIL");
 return ok;
}
Common::Error AstronomicaEngine::run() {
 Graphics::PixelFormat format = _system->getSupportedFormats().front();
 initGraphics(640, 480, &format);
 if (_system->getScreenFormat().bytesPerPixel < 2)
  return Common::Error(Common::kUnsupportedColorMode);
 _screen.create(640, 480, _system->getScreenFormat());
 // Supply a visible engine cursor; the backend hides the OS cursor in-game.
 CursorMan.setDefaultArrowCursor();
 CursorMan.showMouse(true);
 _runner.seedRandom(uint16(Common::RandomSource::generateNewSeed()));
 // _CreateGame allocates the original game structure with calloc.
 _runner.resetGlobals();
 const int startPlace = ConfMan.hasKey("astronomica_start_place") ? ConfMan.getInt("astronomica_start_place") : 1;
 if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }
 if (ConfMan.hasKey("save_slot") && ConfMan.getInt("save_slot") >= 0) {
  const Common::Error result = loadGameState(ConfMan.getInt("save_slot"));
  if (result.getCode() != Common::kNoError) { _background.free(); _screen.free(); return result; }
 }
 if (ConfMan.hasKey("astronomica_verify_legacy") && ConfMan.getBool("astronomica_verify_legacy")) {
  ConfMan.setBool("astronomica_verify",true); ConfMan.setBool("astronomica_sprite_input",true);
  ConfMan.setBool("astronomica_entry_scripts",false); ConfMan.setBool("astronomica_audio",true);
  const bool ok = verifyLegacySaves();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Legacy save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_help") && ConfMan.getBool("astronomica_verify_help")) {
  ConfMan.setBool("astronomica_verify",true); ConfMan.setBool("astronomica_sprite_input",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyHelp();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Help verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_hover") && ConfMan.getBool("astronomica_verify_hover")) {
  ConfMan.setBool("astronomica_verify",true); ConfMan.setBool("astronomica_sprite_input",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyHover();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Hover verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_world29") && ConfMan.getBool("astronomica_verify_world29")) {
  ConfMan.setBool("astronomica_verify",true); ConfMan.setBool("astronomica_sprite_input",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyWorldMovie29() && verifyWorldMovies(true);
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P29 movie verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_intro") && ConfMan.getBool("astronomica_verify_intro")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyIntro();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Intro verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_logo") && ConfMan.getBool("astronomica_verify_logo")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyLogo(true);
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Logo verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_postcredits") && ConfMan.getBool("astronomica_verify_postcredits")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyPostCredits();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Post-credits verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_endings") && ConfMan.getBool("astronomica_verify_endings")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyEndings();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Endings verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_advice") && ConfMan.getBool("astronomica_verify_advice")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyAdvice();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Advice verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_game_state") && ConfMan.getBool("astronomica_verify_game_state")) {
  ConfMan.setBool("astronomica_verify",true);
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyGameState();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Game state verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_transitions") && ConfMan.getBool("astronomica_verify_transitions")) {
  ConfMan.setBool("astronomica_verify",true); // Deterministic scene-entry clock for boundary assertions.
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyTransitions();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Transition verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_audio_channels") && ConfMan.getBool("astronomica_verify_audio_channels")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyAudioChannels();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Audio channel verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_rocket_saves") && ConfMan.getBool("astronomica_verify_rocket_saves")) {
  const bool ok = verifyRocketSaves(); debug("Astronomica rocket save verification: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Rocket save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_probe_saves") && ConfMan.getBool("astronomica_verify_probe_saves")) { ConfMan.setBool("astronomica_verify",true); const bool ok=verifyProbeSaves(); debug("Astronomica probe save verification: %s",ok ? "PASS" : "FAIL"); return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Probe save verification failed"); }
 if (ConfMan.hasKey("astronomica_verify_probe_boundaries") && ConfMan.getBool("astronomica_verify_probe_boundaries")) {
  ConfMan.setBool("astronomica_verify",true);
  const bool ok = verifyProbeBoundaries();
  debug("Astronomica probe boundary result: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Probe boundary audit failed");
 }
 if (ConfMan.hasKey("astronomica_verify_universe_saves") && ConfMan.getBool("astronomica_verify_universe_saves")) {
  ConfMan.setBool("astronomica_verify",true);
  const bool ok = verifyUniverseSaves();
  debug("Astronomica universe save verification: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Universe save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_universe_boundaries") && ConfMan.getBool("astronomica_verify_universe_boundaries")) {
  ConfMan.setBool("astronomica_verify",true);
  const bool ok = verifyUniverseBoundaries();
  debug("Astronomica universe boundary result: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Universe boundary audit failed");
 }
 if (ConfMan.hasKey("astronomica_verify_rocket_boundaries") && ConfMan.getBool("astronomica_verify_rocket_boundaries")) {
  const bool ok = verifyRocketBoundaries();
  debug("Astronomica rocket boundary result: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Rocket boundary audit failed");
 }
 if (ConfMan.hasKey("astronomica_verify_rocket_original") && ConfMan.getBool("astronomica_verify_rocket_original")) {
  uint32 hash = 0; bool ok = verifyRocketOriginalCallbacks(hash);
  debug("Astronomica P537 original callback comparison: %s (96 fixtures, 14592 steps, %08x)",ok ? "PASS" : "FAIL",hash);
  if (ok && ConfMan.hasKey("astronomica_capture_rocket_readouts") && ConfMan.getBool("astronomica_capture_rocket_readouts")) {
   debug("Astronomica P537 readout pixel format: %u %u %u %u",uint(_screen.format.bytesPerPixel),uint(_screen.format.rBits()),uint(_screen.format.gBits()),uint(_screen.format.bBits()));
   for (int setting : {1,7,11,13}) {
    ok = loadPlace(537,false,true) && ok;
    _runner.defineValue(1,0,setting); uint32 now = scriptClock();
    ok = _runner.enqueueStartup(_scene.scripts,now,true) == 1 && ok;
    for (uint tick = 0; tick < 1000 && _runner.pendingCount(); ++tick) { runScriptsAt(now); now += 10; }
    ok = !_runner.pendingCount() && startRocket(_scene,_rocket,setting) && ok;
    for (uint tick = 1; tick <= 300 && _rocket.kind != RocketMotion::kStopped; ++tick) advanceRocket(_scene,_rocket,setting,tick*10);
    ok = _rocket.kind == RocketMotion::kStopped && ok; redrawSprites();
    Common::DumpFile out;
    ok = out.open(ConfMan.getPath("savepath").join(Common::String::format("rocket-readout-%d.bmp",setting))) && Image::writeBMP(out,_screen) && ok;
   }
   debug("Astronomica P537 readout captures: %s (four original-resource scenes)",ok ? "PASS" : "FAIL");
  }
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Rocket original comparison failed");
 }
 if (ConfMan.hasKey("astronomica_verify_builder_saves") && ConfMan.getBool("astronomica_verify_builder_saves")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyBuilderSaves();
  debug("Astronomica builder save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Builder save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p517_saves") && ConfMan.getBool("astronomica_verify_p517_saves")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP517Saves();
  debug("Astronomica P517 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P517 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p513_saves") && ConfMan.getBool("astronomica_verify_p513_saves")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP513Saves();
  debug("Astronomica P513 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P513 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_save_history") && ConfMan.getBool("astronomica_verify_save_history")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifySaveEntryHistory();
  debug("Astronomica save entry history verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Save entry history verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_variant_saves") && ConfMan.getBool("astronomica_verify_variant_saves")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyVariantSaves();
  debug("Astronomica variant save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Variant save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p530_saves") && ConfMan.getBool("astronomica_verify_p530_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP530Saves();
  debug("Astronomica P530 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P530 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p528_saves") && ConfMan.getBool("astronomica_verify_p528_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP528Saves();
  debug("Astronomica P528 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P528 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_presentation") && ConfMan.getBool("astronomica_verify_presentation")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyPresentation();
  debug("Astronomica presentation verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Presentation verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p526_saves") && ConfMan.getBool("astronomica_verify_p526_saves")) {
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP526Saves();
  debug("Astronomica P526 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P526 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p524_saves") && ConfMan.getBool("astronomica_verify_p524_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP524Saves();
  debug("Astronomica P524 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P524 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p519_saves") && ConfMan.getBool("astronomica_verify_p519_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP519Saves();
  debug("Astronomica P519 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P519 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p505_saves") && ConfMan.getBool("astronomica_verify_p505_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP505Saves();
  debug("Astronomica P505 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P505 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p508_saves") && ConfMan.getBool("astronomica_verify_p508_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP508Saves();
  debug("Astronomica P508 save verification: %s",ok ? "PASS" : "FAIL");
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P508 save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_saves") && ConfMan.getBool("astronomica_verify_saves")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifySaves();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Save verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_movies") && ConfMan.getBool("astronomica_verify_movies")) {
  const bool movieOK = verifyContinuousMovies();
  _background.free(); _screen.free(); quitGame();
  return movieOK ? Common::kNoError : Common::Error(Common::kReadingFailed,"Continuous movie verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p524") && ConfMan.getBool("astronomica_verify_p524")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP524Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P524 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_comet") && ConfMan.getBool("astronomica_verify_comet")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyCometPuzzles();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Comet verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_mentors") && ConfMan.getBool("astronomica_verify_mentors")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyMentors();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Mentors verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p523") && ConfMan.getBool("astronomica_verify_p523")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP523Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P523 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p510") && ConfMan.getBool("astronomica_verify_p510")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP510Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P510 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p516") && ConfMan.getBool("astronomica_verify_p516")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP516Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P516 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p501") && ConfMan.getBool("astronomica_verify_p501")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP501Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P501 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p522") && ConfMan.getBool("astronomica_verify_p522")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP522Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P522 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p507") && ConfMan.getBool("astronomica_verify_p507")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP507Wheel();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P507 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p513") && ConfMan.getBool("astronomica_verify_p513")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP513Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P513 verification failed");
 }
 if(ConfMan.hasKey("astronomica_verify_p501_saves")&&ConfMan.getBool("astronomica_verify_p501_saves")){const bool ok=verifyP501Saves();debug("Astronomica P501 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P501 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p504_saves")&&ConfMan.getBool("astronomica_verify_p504_saves")){const bool ok=verifyP504Saves();debug("Astronomica P504 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P504 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p503_saves")&&ConfMan.getBool("astronomica_verify_p503_saves")){const bool ok=verifyP503Saves();debug("Astronomica P503 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P503 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p502_saves")&&ConfMan.getBool("astronomica_verify_p502_saves")){const bool ok=verifyP502Saves();debug("Astronomica P502 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P502 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p527_saves")&&ConfMan.getBool("astronomica_verify_p527_saves")){const bool ok=verifyP527Saves();debug("Astronomica P527 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P527 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p516_saves")&&ConfMan.getBool("astronomica_verify_p516_saves")){const bool ok=verifyP516Saves();debug("Astronomica P516 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P516 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p511_saves")&&ConfMan.getBool("astronomica_verify_p511_saves")){const bool ok=verifyP511Saves();debug("Astronomica P511 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P511 save verification failed");}
 if(ConfMan.hasKey("astronomica_verify_p509_saves")&&ConfMan.getBool("astronomica_verify_p509_saves")){const bool ok=verifyP509Saves();debug("Astronomica P509 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P509 save verification failed");}
 if(ConfMan.hasKey("astronomica_audit_p509_boundaries")&&ConfMan.getBool("astronomica_audit_p509_boundaries")){const bool ok=verifyP509BoundaryAudit();debug("Astronomica P509 boundary verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P509 boundary audit failed");}
 if(ConfMan.hasKey("astronomica_verify_p521_saves")&&ConfMan.getBool("astronomica_verify_p521_saves")){const bool ok=verifyP521Saves();debug("Astronomica P521 save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P521 audit failed");}
 if(ConfMan.hasKey("astronomica_verify_planet_saves")&&ConfMan.getBool("astronomica_verify_planet_saves")){const bool ok=verifyPlanetSaves();debug("Astronomica planet save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Planet audit failed");}
 if (ConfMan.hasKey("astronomica_verify_rendezvous_saves") && ConfMan.getBool("astronomica_verify_rendezvous_saves")) {const bool ok=verifyRendezvousSaves();debug("Astronomica rendezvous save verification: %s",ok?"PASS":"FAIL");return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Rendezvous save verification failed");}
 if (ConfMan.hasKey("astronomica_verify_p514") && ConfMan.getBool("astronomica_verify_p514")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP514Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P514 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_builder") && ConfMan.getBool("astronomica_verify_builder")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyBuilderPuzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Builder verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p512") && ConfMan.getBool("astronomica_verify_p512")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP512Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P512 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_p526") && ConfMan.getBool("astronomica_verify_p526")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyP526Puzzle();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P526 verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify_variants") && ConfMan.getBool("astronomica_verify_variants")) {
  ConfMan.setBool("astronomica_audio",true); ConfMan.setBool("astronomica_animation",true);
  ConfMan.setBool("astronomica_sprite_input",true); ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyVariantPuzzles();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Variant verification failed");
 }
 if (ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) {
  bool scriptsOK = verifyScriptRunner() && verifyConditions() && verifySpriteComposition();
  const bool cursorInitiallyVisible = CursorMan.isVisible();
  int loaded = 0; uint32 bitmaps = 0, commands = 0, tails = 0;
  for (int id = 0; id <= 537; ++id) if (loadPlace(id)) { ++loaded; bitmaps += _scene.bitmapCount; commands += _scene.commandCount; if (_scene.trailing) ++tails; }
  const bool cursorOK = cursorInitiallyVisible && CursorMan.isVisible();
  debug("Astronomica cursor verification: %s (visible after initialization and scene reloads)",cursorOK ? "PASS" : "FAIL");
  scriptsOK = cursorOK && scriptsOK;
  debug("Astronomica parser verification: %u bitmaps, %u commands, %u trailing payloads", bitmaps, commands, tails);
  debug("Astronomica verification: %d scene prefixes rendered", loaded);
  bool spriteOK = loadPlace(29);
  Common::DumpFile spriteDump;
  spriteDump.open(Common::Path("astronomica-P29.rgb"));
  debug("Astronomica sprite pixel format: %u bytes, %u/%u/%u bits", _screen.format.bytesPerPixel, _screen.format.rBits(), _screen.format.gBits(), _screen.format.bBits());
  uint32 rgbHash = 2166136261U;
  for (int y = 0; y < 456; ++y) for (int x = 0; x < 640; ++x) {
   byte r, g, b; _screen.format.colorToRGB(_screen.getPixel(x,y), r, g, b);
   if (spriteDump.isOpen()) { spriteDump.writeByte(r); spriteDump.writeByte(g); spriteDump.writeByte(b); }
   rgbHash = (rgbHash ^ r) * 16777619U;
   rgbHash = (rgbHash ^ g) * 16777619U;
   rgbHash = (rgbHash ^ b) * 16777619U;
  }
  spriteDump.close();
  // Reference colors quantized to the actual backend format before hashing.
  const bool rgb565 = _screen.format.rBits() == 5 && _screen.format.gBits() == 6 && _screen.format.bBits() == 5;
  const bool rgb888 = _screen.format.rBits() == 8 && _screen.format.gBits() == 8 && _screen.format.bBits() == 8;
  spriteOK = spriteOK && ((rgb565 && rgbHash == 0x97802e24U) || (rgb888 && rgbHash == 0xca004a3bU));
  debug("Astronomica sprite verification: %s (P29 RGB hash %08x)", spriteOK ? "PASS" : "FAIL", rgbHash);
  bool visibilityOK = demoVisibility(false) && _scene.sprites[1].visible == 1;
  runScripts();
  visibilityOK = _scene.sprites[1].visible == 0 && screenRGBHash(_screen) == (rgb565 ? 0xf46c822eU : 0xa8aa76a9U) && visibilityOK;
  visibilityOK = demoVisibility(true) && visibilityOK;
  runScripts();
  visibilityOK = _scene.sprites[1].visible == 1 && screenRGBHash(_screen) == rgbHash && visibilityOK;
  // A later invalid sprite must reject the preceding state change too.
  Script invalid; Command set; set.opcode = 32; set.args.push_back(1); set.args.push_back(0); set.args.push_back(9);
  invalid.push_back(set); Command hide; hide.opcode = 17; hide.args.push_back(99); invalid.push_back(hide);
  int32 localBefore = 0, localAfter = 0;
  visibilityOK = _runner.getValue(1, 0, localBefore) && !_runner.enqueue(invalid, 0) && _runner.getValue(1, 0, localAfter) && localBefore == localAfter && visibilityOK;
  debug("Astronomica visibility verification: %s (original P29 hide/show, background restored, invalid target rejected)", visibilityOK ? "PASS" : "FAIL");
  scriptsOK = scriptsOK && visibilityOK;
  bool movementOK = loadPlace(517) && _scene.sprites.size() >= 7;
  if (movementOK) {
  const uint32 initialMoveHash = rgb565 ? 0x2239ec62U : 0x402586efU;
  const uint32 movedHash = rgb565 ? 0xc411be61U : 0xcb1d5ec4U;
  movementOK = screenRGBHash(_screen) == initialMoveHash && movementOK;
  movementOK = demoMovement(477) && movementOK;
  movementOK = _scene.sprites[6].x == 447 && movementOK;
  runScripts();
  movementOK = _scene.sprites[6].x == 477 && _scene.sprites[6].y == 361 && screenRGBHash(_screen) == movedHash && movementOK;
  movementOK = demoMovement(447) && movementOK;
  runScripts();
  movementOK = screenRGBHash(_screen) == initialMoveHash && movementOK;
  debug("Astronomica movement verification: %s (original P517 move/restore, independent RGB reference)", movementOK ? "PASS" : "FAIL");
  }
  scriptsOK = scriptsOK && movementOK;
  bool offsetOK = loadPlace(510) && _scene.sprites.size() >= 9;
  if (offsetOK) {
   const uint32 expected565[] = {0xa3902005U, 0x457e9af5U, 0xb9c36ac5U};
   const uint32 expected888[] = {0x3579528cU, 0x5d523333U, 0xaa7ebad4U};
   offsetOK = screenRGBHash(_screen) == (rgb565 ? expected565[0] : expected888[0]);
   for (int i = 1; i <= 2; ++i) {
    offsetOK = demoOffset() && _scene.sprites[7].y == 359 + i && offsetOK;
    runScripts();
    offsetOK = _scene.sprites[7].y == 360 + i && screenRGBHash(_screen) == (rgb565 ? expected565[i] : expected888[i]) && offsetOK;
   }
   // Original chain now supports both source and clone. Each zero-delay
   // successor must execute in the next queue pass, independently.
   Script mixed;
   for (uint s = 0; s < _scene.scripts.size(); ++s)
    for (uint i = 0; i < _scene.scripts[s].size(); ++i) {
     const Command &c = _scene.scripts[s][i];
     if (c.opcode == 47 && c.args.size() == 3 && (c.args[0] == 8 || c.args[0] == 9)) mixed.push_back(c);
    }
   offsetOK = mixed.size() == 2 && _runner.enqueue(mixed, 0) && _scene.sprites[7].y == 362 && offsetOK;
   runScripts();
   offsetOK = _scene.sprites[7].y == 363 && _scene.sprites[8].y == 361 && _runner.pendingCount() == 1 && screenRGBHash(_screen) == (rgb565 ? 0x725673d5U : 0x517ce2a3U) && offsetOK;
   runScripts();
   offsetOK = _scene.sprites[7].y == 363 && _scene.sprites[8].y == 362 && !_runner.pendingCount() && screenRGBHash(_screen) == (rgb565 ? 0xfdea7131U : 0x9af3fbc8U) && offsetOK;
  }
  debug("Astronomica offset verification: %s (P510 source/clone independence, five RGB references)", offsetOK ? "PASS" : "FAIL");
  scriptsOK = scriptsOK && offsetOK;
  bool frameOK = loadPlace(510) && _scene.sprites.size() >= 10;
  if (frameOK) {
   const int sequence[] = {0,1,0};
   for (int i = 0; i < 3; ++i) {
    const int previous = _scene.sprites[9].selectedFrame;
    frameOK = demoFrame(sequence[i]) && _scene.sprites[9].selectedFrame == previous && frameOK;
    runScripts();
    const uint32 expected = sequence[i] == 0 ? (rgb565 ? 0xa3902005U : 0x3579528cU) : (rgb565 ? 0x518eade8U : 0xf9c9f648U);
    frameOK = _scene.sprites[9].selectedFrame == sequence[i] && screenRGBHash(_screen) == expected && frameOK;
   }
   Command bad; bad.opcode = 15; bad.args.push_back(10); bad.args.push_back(2);
   Script invalidFrame; invalidFrame.push_back(bad);
   const int oldFrame = _scene.sprites[9].selectedFrame;
   const uint32 oldPixels = screenRGBHash(_screen);
   frameOK = _runner.enqueue(invalidFrame,0) && frameOK;
   runScriptsAt(0); runScriptsAt(1);
   frameOK = !_runner.pendingCount() && _scene.sprites[9].selectedFrame == oldFrame &&
    screenRGBHash(_screen) == oldPixels && frameOK;
   invalidFrame[0].args[1] = -1;
   frameOK = !_runner.enqueue(invalidFrame,0) && frameOK;
  }
  debug("Astronomica frame verification: %s (original P510 frames 0/1/0, RGB references, invalid indices)", frameOK ? "PASS" : "FAIL");
  scriptsOK = scriptsOK && frameOK;
  scriptsOK = scriptsOK && spriteOK;
  ConfMan.setBool("astronomica_entry_scripts", true);
  bool conditionsOK = loadPlace(505) && _scene.scripts.size() > 2 && _runner.pendingCount() == 2;
  ConfMan.setBool("astronomica_entry_scripts", false);
  _runner.clear();
  int32 state = -1;
  if (conditionsOK) {
   conditionsOK = _runner.getValue(1, 1, state) && state == 0;
   uint before = _runner.executedCount();
   conditionsOK = _runner.start(_scene.scripts[2], 0) && conditionsOK;
   conditionsOK = _runner.executedCount() - before == 1 && conditionsOK;
   _runner.defineValue(1, 1, 255);
   before = _runner.executedCount();
   conditionsOK = _runner.start(_scene.scripts[2], 0) && conditionsOK;
   conditionsOK = _runner.executedCount() - before == 3 && conditionsOK;
   _runner.loadLocalConditions(_scene.conditions);
 _runner.setGameStateHandler(this);
   before = _runner.executedCount();
   const uint queued = _runner.enqueueStartup(_scene.scripts, 0);
   conditionsOK = queued == 2 && _runner.pendingCount() == 2 && _runner.executedCount() == before && conditionsOK;
   _runner.tick(0);
   conditionsOK = _runner.executedCount() - before == 2 && !_runner.pendingCount() && conditionsOK;
  }
  conditionsOK = loadPlace(530) && conditionsOK;
  if (_scene.scripts.size() > 9) {
   conditionsOK = _runner.getValue(1, 5, state) && state == 1 && conditionsOK;
   conditionsOK = _runner.start(_scene.scripts[9], 0) && conditionsOK;
   const int resetIds[] = {0, 2, 3, 4, 5, 6, 7, 8, 10};
   for (uint i = 0; i < ARRAYSIZE(resetIds); ++i)
    conditionsOK = _runner.getValue(1, resetIds[i], state) && state == 0 && conditionsOK;
   conditionsOK = _runner.getValue(1, 9, state) && state == 1 && conditionsOK;
  } else conditionsOK = false;
  debug("Astronomica conditions verification: %s (P505 true/false, P530 reset)", conditionsOK ? "PASS" : "FAIL");
  ConfMan.setBool("astronomica_sprite_input", true);
  bool mouseOK = loadPlace(510) && spriteAt(227,384) == 9 && spriteAt(256,411) == 9;
  mouseOK = spriteAt(257,411) != 9 && spriteAt(226,384) != 9 && mouseOK;
  // An earlier, invisible sprite with an unsupported click still consumes
  // the hit. Never fall through to another sprite or a rectangle behind it.
  const Sprite savedFirst = _scene.sprites[0];
  _scene.sprites[0] = _scene.sprites[9];
  _scene.sprites[0].visible = 0;
  _scene.sprites[0].click[0].opcode = 999;
  mouseOK = spriteAt(227,384) == 0 && mouseOK;
  clickAt(227,384);
  mouseOK = !_runner.pendingCount() && !_runner.clicksBlocked() && mouseOK;
  _scene.sprites[0] = savedFirst;
  const uint beforeClick = _runner.executedCount();
  clickAt(227,384);
  mouseOK = _runner.pendingCount() == 1 && _runner.executedCount() == beforeClick && mouseOK;
  runScriptsAt(0); // lock, then queue the frame changes
  const uint pendingLocked = _runner.pendingCount();
  clickAt(253,363);
  mouseOK = _runner.clicksBlocked() && _runner.pendingCount() == pendingLocked && mouseOK;
  runScriptsAt(0); runScriptsAt(0); // frames, then local state
  int32 button = 0;
  mouseOK = _scene.sprites[9].selectedFrame == 1 && _runner.getValue(1,4,button) && button == 1 && mouseOK;
  for (uint i = 10; i < 14; ++i) mouseOK = _scene.sprites[i].selectedFrame == 0 && mouseOK;
  mouseOK = screenRGBHash(_screen) == (rgb565 ? 0xfb10a99bU : 0x3f2d859fU) && mouseOK;
  runScriptsAt(149); mouseOK = _runner.clicksBlocked() && mouseOK;
  runScriptsAt(150); mouseOK = !_runner.clicksBlocked() && !_runner.pendingCount() && mouseOK;
  clickAt(253,363); runScriptsAt(0); runScriptsAt(0); runScriptsAt(0);
  mouseOK = _scene.sprites[9].selectedFrame == 0 && _scene.sprites[10].selectedFrame == 1 && _runner.getValue(1,4,button) && button == 2 && mouseOK;
  mouseOK = screenRGBHash(_screen) == (rgb565 ? 0x966034ffU : 0x655cfed9U) && mouseOK;
  mouseOK = loadPlace(103) && !_runner.clicksBlocked() && !_runner.pendingCount() && mouseOK;
  ConfMan.setBool("astronomica_sprite_input", false);
  debug("Astronomica mouse verification: %s (P510 original button scripts, inclusive bounds, 149/150 ms lock, scene reset)", mouseOK ? "PASS" : "FAIL");
  scriptsOK = mouseOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  bool animationOK = loadPlace(510) && _scene.sprites[1].selectedFrame == 0;
  clickAt(100,380); runScriptsAt(0); runScriptsAt(0);
  animationOK = _scene.sprites[1].visible && _scene.sprites[6].selectedFrame == 1 && _runner.clicksBlocked() && animationOK;
  animateSpritesAt(399);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  animateSpritesAt(400); runScriptsAt(400);
  animationOK = _scene.sprites[1].selectedFrame == 1 && !_runner.clicksBlocked() && animationOK;
  const uint32 animationFrameOneHash = screenRGBHash(_screen);
  runScriptsAt(499); animationOK = _scene.sprites[6].selectedFrame == 1 && animationOK;
  runScriptsAt(500); animationOK = _scene.sprites[6].selectedFrame == 0 && animationOK;
  animateSpritesAt(800);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  const uint32 animationFrameZeroHash = screenRGBHash(_screen);
  animationOK = animationFrameZeroHash == (rgb565 ? 0xbddce235U : 0x74ec5203U) && animationFrameOneHash == (rgb565 ? 0xdb506b77U : 0xcbf46977U) && animationOK;
  animateSpritesAt(2400);
  animationOK = _scene.sprites[1].selectedFrame == 1 && animationOK;
  runScriptsAt(10399); animationOK = _scene.sprites[1].visible && animationOK;
  runScriptsAt(10400); animationOK = !_scene.sprites[1].visible && !_runner.pendingCount() && animationOK;
  animateSpritesAt(10400);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  debug("Astronomica animation verification: %s (P510 original indicator click, hidden advancement, no catch-up; RGB %08x/%08x)", animationOK ? "PASS" : "FAIL", animationFrameZeroHash, animationFrameOneHash);
  scriptsOK = animationOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  bool audioOK = loadPlace(510) && verifyAudio();
  const uint soundCountBefore = _soundsStarted;
  clickAt(30,375); // Original type-2 button: pulse, sound S3, unlock.
  audioOK = _soundsStarted == soundCountBefore && audioOK;
  runScriptsAt(0); runScriptsAt(0);
  audioOK = _soundsStarted == soundCountBefore + 1 && _lastSound == 2 && _mixer->isSoundHandleActive(_soundHandle) && audioOK;
  runScriptsAt(150); runScriptsAt(500);
  clickAt(600,375); runScriptsAt(0); runScriptsAt(0);
  audioOK = _lastSound == 5 && _soundsStarted == soundCountBefore + 2 && audioOK;
  runScriptsAt(149); audioOK = _runner.clicksBlocked() && audioOK;
  runScriptsAt(150); runScriptsAt(1449);
  audioOK = _lastSound == 5 && audioOK;
  runScriptsAt(1450);
  audioOK = _lastSound == 1 && _soundsStarted == soundCountBefore + 3 && audioOK;
  Script missing; Command sound; sound.opcode = 9; sound.args.push_back(899); missing.push_back(sound);
  audioOK = !_runner.canRun(missing, true) && audioOK;
  audioOK = loadPlace(103) && !_mixer->isSoundHandleActive(_soundHandle) && audioOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  debug("Astronomica audio verification: %s (P510 PCM, original clicks S3/S6/S2, replacement, missing target, scene stop)", audioOK ? "PASS" : "FAIL");
  scriptsOK = audioOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  ConfMan.setBool("astronomica_animation", true);
  bool transitionOK = loadPlace(510);
  _runner.defineValue(0,95,1234);
  const uint beforeExitSound = _soundsStarted;
  clickAt(35,430); // Original sprite 4: S4, new_place(136,500), unlock(150).
  transitionOK = _runner.pendingCount() == 2 && _place == 510 && transitionOK;
  runScriptsAt(0); runScriptsAt(0);
  transitionOK = _lastSound == 3 && _soundsStarted == beforeExitSound + 1 && _runner.clicksBlocked() && transitionOK;
  runScriptsAt(499);
  transitionOK = _place == 510 && _runner.clicksBlocked() && transitionOK;
  runScriptsAt(500);
  int32 preserved = 0;
  transitionOK = _place == 136 && _previousPlace == 510 && !_runner.pendingCount() && !_runner.clicksBlocked() && _lastSound == 911 && _soundsStarted == beforeExitSound + 2 && _runner.getValue(0,95,preserved) && preserved == 1234 && transitionOK;
  const uint32 arrivedHash = screenRGBHash(_screen);
  const uint afterArrival = _runner.executedCount();
  runScriptsAt(650);
  transitionOK = _place == 136 && _runner.executedCount() == afterArrival && screenRGBHash(_screen) == arrivedHash && transitionOK;
  transitionOK = loadPlace(510) && transitionOK;
  clickAt(600,430); // Original sprite 6: S5, new_place(408,700).
  runScriptsAt(0);
  transitionOK = _lastSound == 4 && _place == 510 && transitionOK;
  runScriptsAt(699); transitionOK = _place == 510 && transitionOK;
  runScriptsAt(700);
  transitionOK = _place == 408 && _previousPlace == 510 && !_runner.pendingCount() && transitionOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  ConfMan.setBool("astronomica_animation", false);
  debug("Astronomica transition verification: %s (original P510 exits, 499/500 and 699/700 ms, queued tail discarded, globals preserved)", transitionOK ? "PASS" : "FAIL");
  scriptsOK = transitionOK && scriptsOK;
  bool bitsOK = loadPlace(511) && _scene.scripts.size() > 3;
  _runner.defineValue(1,5,6); _runner.defineValue(0,5,123);
  uint bitOperations = 0;
  if (bitsOK) for (uint i = 0; i < _scene.scripts[3].size(); ++i) {
   const Command &c = _scene.scripts[3][i];
   if (c.opcode != 33) continue;
   Script one; one.push_back(c);
   bitsOK = _runner.enqueue(one,0) && bitsOK;
   runScriptsAt(0);
   int32 value;
   bitsOK = _runner.getValue(1,5,value) && value == (bitOperations == 0 ? 7 : 6) && bitsOK;
   ++bitOperations;
  }
  int32 globalBits;
  bitsOK = bitOperations == 4 && _runner.getValue(0,5,globalBits) && globalBits == 123 && bitsOK;
  debug("Astronomica bit verification: %s (original P511 commands: 6/7/6/6/6, unrelated bits and global preserved)", bitsOK ? "PASS" : "FAIL");
  scriptsOK = bitsOK && scriptsOK;
  bool randomOK = loadPlace(510);
  Script randomCommand;
  for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 40) randomCommand.push_back(_scene.scripts[0][i]);
  _runner.seedRandom(1);
  const int expectedVariants[] = {1,1,2,1,2,1,2,1,3,3,1,2};
  randomOK = randomCommand.size() == 1 && randomOK;
  for (uint i = 0; i < ARRAYSIZE(expectedVariants); ++i) {
   randomOK = _runner.enqueue(randomCommand,0) && randomOK;
   runScriptsAt(0); int32 variant;
   randomOK = _runner.getValue(1,0,variant) && variant == expectedVariants[i] && randomOK;
  }
  _runner.seedRandom(1);
  randomOK = _runner.random15() == 346 && loadPlace(136) && _runner.random15() == 130 && randomOK;
  debug("Astronomica random verification: %s (original P510 range 1..3, 12 seeded draws, state survives scene load)", randomOK ? "PASS" : "FAIL");
  scriptsOK = randomOK && scriptsOK;
  bool bagOK = loadPlace(505);
  Script bagCommand;
  for (uint j = 0; j < _scene.scripts.size(); ++j)
   for (uint i = 0; i < _scene.scripts[j].size(); ++i)
    if (_scene.scripts[j][i].opcode == 39) bagCommand.push_back(_scene.scripts[j][i]);
  bagOK = bagCommand.size() == 1 && bagOK;
  _runner.seedRandom(1);
  uint seenVariants = 0;
  const int bagOrder[] = {1,2,5,3,6,4,8,7};
  for (uint i = 0; i < 8; ++i) {
   bagOK = _runner.enqueue(bagCommand,0) && bagOK;
   runScriptsAt(0);
   int32 variant = 0, used = 0;
   bagOK = _runner.getValue(1,0,variant) && _runner.getValue(1,1,used) && variant == bagOrder[i] && bagOK;
   if (variant >= 1 && variant <= 8) {
    bagOK = !(seenVariants & (1U << (variant-1))) && bagOK;
    seenVariants |= 1U << (variant-1);
   }
   bagOK = uint32(used) == seenVariants && bagOK;
  }
  int32 lastVariant = 0, afterExhaustion = 0;
  _runner.getValue(1,0,lastVariant);
  bagOK = _runner.enqueue(bagCommand,0) && bagOK; runScriptsAt(0);
  bagOK = seenVariants == 255 && _runner.getValue(1,0,afterExhaustion) && afterExhaustion == lastVariant && _runner.random15() == 31126 && bagOK;
  debug("Astronomica variant bag verification: %s (original P505, eight distinct variants, exhausted mask preserves result and consumes draw)", bagOK ? "PASS" : "FAIL");
  scriptsOK = bagOK && scriptsOK;
  bool stopOK = loadPlace(501);
  Script originalStop;
  if (stopOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 10) originalStop.push_back(_scene.scripts[0][i]);
  ConfMan.setBool("astronomica_audio", true);
  stopOK = loadPlace(510) && originalStop.size() == 1 && stopOK;
  stopOK = playSound(1) && _mixer->isSoundHandleActive(_soundHandle) && stopOK;
  stopOK = _runner.enqueue(originalStop,0,true) && stopOK;
  runScriptsAt(3499);
  stopOK = _mixer->isSoundHandleActive(_soundHandle) && _runner.pendingCount() == 1 && stopOK;
  runScriptsAt(3500);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && !_runner.pendingCount() && stopOK;
  // Repeated stops are harmless. A following unknown opcode rejects the whole chain.
  stopOK = _runner.enqueue(originalStop,0,true) && stopOK;
  runScriptsAt(3500);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && playSound(1) && stopOK;
  Script invalidStop = originalStop; Command unsupported; unsupported.opcode = 999; invalidStop.push_back(unsupported);
  stopOK = !_runner.start(invalidStop,0,true) && _mixer->isSoundHandleActive(_soundHandle) && stopOK;
  // Parameter is not used as a channel id in the original implementation.
  Script parameter = originalStop; parameter[0].args[0] = 123; parameter[0].delay = 0;
  stopOK = _runner.enqueue(parameter,0) && stopOK;
  runScriptsAt(0);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && stopOK;
  ConfMan.setBool("astronomica_audio", false);
  debug("Astronomica stop verification: %s (original P501 command on P510 sound, 3499/3500 ms, repeated stop, atomic rejection)", stopOK ? "PASS" : "FAIL");
  scriptsOK = stopOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", true);
  bool rangeOK = loadPlace(511);
  Script originalRanges;
  if (rangeOK) for (uint i = 0; i < _scene.scripts[1].size(); ++i)
   if (_scene.scripts[1][i].opcode == 48) originalRanges.push_back(_scene.scripts[1][i]);
  rangeOK = originalRanges.size() == 4 && rangeOK;
  const uint32 rangeRGB[] = {0x413b4b5aU,0xc720b91eU,0xb9bea763U,0xb86c6b60U};
  const uint32 range565[] = {0x9b3c70e5U,0x606fe3c8U,0x4f281904U,0xffbd8bbbU};
  for (uint i = 0; i < originalRanges.size(); ++i) {
   Sprite &indicator = _scene.sprites[4];
   indicator.selectedFrame = 0; indicator.frameSince = 100;
   Script oneRange; oneRange.push_back(originalRanges[i]);
   rangeOK = _runner.enqueue(oneRange,100,true) && rangeOK; runScriptsAt(100);
   rangeOK = indicator.selectedFrame == 0 && indicator.frameSince == 100 &&
    indicator.frameFirst == originalRanges[i].args[1] && indicator.frameLast == originalRanges[i].args[2] && rangeOK;
   rangeOK = !advanceSpriteFrame(indicator,4,599) && rangeOK;
   // Only advance this indicator, keeping other scene sprites at their initial frames.
   for (uint tick = 1; tick <= 4; ++tick) {
    const int expected = i == 0 ? (tick % 2 ? 1 : 0) : i == 1 ? (tick % 2 ? 1 : 2) : (tick % 2 ? 3 : 2);
    rangeOK = advanceSpriteFrame(indicator,4,100 + tick * 500) && indicator.selectedFrame == expected && rangeOK;
    redrawSprites();
    rangeOK = screenRGBHash(_screen) == (rgb565 ? range565[expected] : rangeRGB[expected]) && rangeOK;
   }
  }
  if (!originalRanges.empty()) {
   Sprite &indicator = _scene.sprites[4];
   Script clamped; clamped.push_back(originalRanges[0]);
   clamped[0].args[1] = -50; clamped[0].args[2] = 99999;
   rangeOK = _runner.enqueue(clamped,0,true) && rangeOK; runScriptsAt(0);
   rangeOK = indicator.frameFirst == 0 && indicator.frameLast == 3 && rangeOK;
   const uint32 since = indicator.frameSince; const int frame = indicator.selectedFrame;
   Script badRange = clamped; badRange[0].args[1] = 3; badRange[0].args[2] = 1;
   rangeOK = !_runner.start(badRange,0,true) && rangeOK;
   Script atomicRange = clamped; Command unknownRange; unknownRange.opcode = 999; atomicRange.push_back(unknownRange);
   atomicRange[0].args[2] = 0;
   rangeOK = !_runner.start(atomicRange,0,true) && indicator.frameFirst == 0 && indicator.frameLast == 3 &&
    indicator.frameSince == since && indicator.selectedFrame == frame && rangeOK;
   badRange[0].args[0] = 9999;
   rangeOK = !_runner.start(badRange,0,true) && rangeOK;
  }
  debug("Astronomica range verification: %s (four original P511 commands, 500 ms, preserved frame/time, four independent RGB references, clamps, atomic rejection)", rangeOK ? "PASS" : "FAIL");
  scriptsOK = rangeOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
  // Isolated original loop controls; no assumption that the full puzzle runs.
  ConfMan.setBool("astronomica_audio", true);
  bool loopOK = loadPlace(509);
  Script disableLoop, enableLoop, chooseLoop;
  if (loopOK) {
   for (uint i = 0; i < _scene.scripts[2].size(); ++i)
    if (_scene.scripts[2][i].opcode == 25 && disableLoop.empty()) disableLoop.push_back(_scene.scripts[2][i]);
   for (uint i = 0; i < _scene.scripts[4].size(); ++i)
    if (_scene.scripts[4][i].opcode == 26) enableLoop.push_back(_scene.scripts[4][i]);
  }
  loopOK = loadPlace(511) && loopOK;
  if (loopOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 27) chooseLoop.push_back(_scene.scripts[0][i]);
  loopOK = chooseLoop.size() == 1 && disableLoop.size() == 1 && enableLoop.size() == 1 && loopOK;
  Audio::SeekableAudioStream *loopSource = openSound(11);
  loopOK = loopSource && loopOK;
  if (loopSource) {
   Audio::AudioStream *repeating = Audio::makeLoopingAudioStream(loopSource,0);
   int16 repeated[56541];
   loopOK = repeating->readBuffer(repeated,56541) == 56541 && !repeating->endOfData() && loopOK;
   uint32 pcmHash = 2166136261U;
   for (uint i = 0; i < 28252; ++i) {
    pcmHash = (pcmHash ^ (uint16(repeated[i]) & 255)) * 16777619U;
    pcmHash = (pcmHash ^ (uint16(repeated[i]) >> 8)) * 16777619U;
    loopOK = repeated[i] == repeated[i+28252] && loopOK;
   }
   for (uint i = 0; i < 37; ++i) loopOK = repeated[i] == repeated[i+56504] && loopOK;
   loopOK = pcmHash == 0x0d45829aU && loopOK;
   delete repeating;
  }
  loopOK = _runner.enqueue(chooseLoop,0,true) && loopOK; runScriptsAt(0);
  const uint beforeLoop = _soundsStarted;
  resumeLoopAt(5000);
  loopOK = _soundsStarted == beforeLoop && !_mixer->isSoundHandleActive(_soundHandle) && loopOK;
  resumeLoopAt(5001);
  loopOK = _soundsStarted == beforeLoop+1 && _lastSound == 11 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  resumeLoopAt(9000);
  loopOK = _soundsStarted == beforeLoop+1 && loopOK;
  Script foreground; Command fg; fg.opcode = 9; fg.args.push_back(3); foreground.push_back(fg);
  loopOK = _runner.enqueue(foreground,6000) && loopOK; runScriptsAt(6000);
  resumeLoopAt(11001); // Long foreground sound is still active despite elapsed logical time.
  loopOK = _lastSound == 2 && _soundsStarted == beforeLoop+2 && _lastSoundAt == 6000 && loopOK;
  _mixer->stopHandle(_soundHandle); // Simulate foreground completion without a wall-clock wait.
  resumeLoopAt(11000);
  loopOK = _soundsStarted == beforeLoop+2 && loopOK;
  resumeLoopAt(11001);
  loopOK = _soundsStarted == beforeLoop+3 && _lastSound == 11 && loopOK;
  loopOK = _runner.enqueue(disableLoop,12000,true) && loopOK; runScriptsAt(12000); resumeLoopAt(20000);
  loopOK = !_loopEnabled && !_mixer->isSoundHandleActive(_soundHandle) && _soundsStarted == beforeLoop+3 && loopOK;
  loopOK = _runner.enqueue(enableLoop,20000,true) && loopOK; runScriptsAt(20000); resumeLoopAt(20000);
  loopOK = _loopEnabled && _soundsStarted == beforeLoop+4 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  Script badLoop = chooseLoop; badLoop[0].args[0] = 899;
  loopOK = !_runner.enqueue(badLoop,0,true) && _loopSound == 11 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  loopOK = loadPlace(103) && loopOK; resumeLoopAt(30000);
  loopOK = _loopSound == -1 && !_mixer->isSoundHandleActive(_soundHandle) && loopOK;
  debug("Astronomica loop verification: %s (original P511/P509 controls, serialized 12 -> S11 PCM wrap, 5000/5001 ms, foreground priority, disable/enable, scene cleanup)", loopOK ? "PASS" : "FAIL");
  scriptsOK = loopOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_audio", true);
  bool successOK = loadPlace(511);
  Script originalSuccess;
  if (successOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 23) originalSuccess.push_back(_scene.scripts[0][i]);
  successOK = originalSuccess.size() == 1 && successOK;
  _runner.defineValue(0,27,0);
  const uint32 initialCompleted = _puzzlesCompleted;
  const uint successSounds = _soundsStarted;
  Script invalidSuccess = originalSuccess; Command unrecognizedSuccess; unrecognizedSuccess.opcode = 999;
  invalidSuccess.push_back(unrecognizedSuccess);
  successOK = !_runner.start(invalidSuccess,0,true) && _puzzlesCompleted == initialCompleted && successOK;
  successOK = _runner.start(originalSuccess,100,true) && successOK;
  int32 completionFlag = 0;
  successOK = _runner.getValue(0,27,completionFlag) && completionFlag == 1 && _puzzlesCompleted == initialCompleted+1 &&
   _soundsStarted == successSounds+1 && _lastSound == 912 && !_mixer->isSoundHandleActive(_soundHandle) && _lastSuccessEnd > 100 && successOK;
  successOK = _runner.start(originalSuccess,200,true) && _puzzlesCompleted == initialCompleted+1 && _soundsStarted == successSounds+1 && successOK;
  _runner.defineValue(0,27,-2);
  successOK = _runner.start(originalSuccess,300,true) && _runner.getValue(0,27,completionFlag) && completionFlag == 1 &&
   _puzzlesCompleted == initialCompleted+1 && _soundsStarted == successSounds+1 && successOK;
  // A queued continuation is timed from the end of synchronous playback.
  _runner.defineValue(0,27,0); _runner.defineValue(1,4,1);
  Script afterSuccess = originalSuccess; Command continuation;
  continuation.opcode = 32; continuation.delay = 1000;
  continuation.args.push_back(1); continuation.args.push_back(4); continuation.args.push_back(99); afterSuccess.push_back(continuation);
  successOK = _runner.start(afterSuccess,400,true) && successOK;
  runScriptsAt(_lastSuccessEnd+999);
  successOK = _runner.getValue(1,4,completionFlag) && completionFlag == 1 && successOK;
  runScriptsAt(_lastSuccessEnd+1000);
  successOK = _runner.getValue(1,4,completionFlag) && completionFlag == 99 && _puzzlesCompleted == initialCompleted+2 && successOK;
  successOK = loadPlace(103) && _runner.getValue(0,27,completionFlag) && completionFlag == 1 &&
   !_runner.canRun(originalSuccess,true) && successOK;
  successOK = loadPlace(1) && _runner.getValue(0,27,completionFlag) && completionFlag == 0 && successOK;
  ConfMan.setBool("astronomica_audio", false);
  successOK = loadPlace(511) && !_runner.canRun(originalSuccess,true) && successOK;
  debug("Astronomica success verification: %s (original P511 custom 25, global 27, synchronous S12, duplicate suppression, continuation timing, scene persistence, P1 reset)", successOK ? "PASS" : "FAIL");
  scriptsOK = successOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_animation", true);
  bool endingOK = loadPlace(511);
  // Set the solved input state, then run the ENTIRE original ending script.
  // This exercises the ending sequence, not the player solving the puzzle.
  _runner.defineValue(1,5,7); _runner.defineValue(0,27,0);
  const uint32 completedBeforeEnding = _puzzlesCompleted;
  Script fullEnding = _scene.scripts[0];
  endingOK = _runner.canRun(fullEnding,true) && _runner.enqueue(fullEnding,0,true) && endingOK;
  for (uint i = 0; i < 6; ++i) runScriptsAt(0);
  endingOK = _place == 511 && _scene.sprites[19].x == 190 && _scene.sprites[19].y == 220 && _runner.clicksBlocked() && endingOK;
  const int routeX[] = {220,250,280,310,340,370,400};
  const int routeY[] = {215,210,205,205,210,210,215};
  for (uint i = 0; i < 7; ++i) {
   runScriptsAt((i+1)*300-1);
   endingOK = _scene.sprites[19].x == (i ? routeX[i-1] : 190) && endingOK;
   runScriptsAt((i+1)*300);
   endingOK = _place == 511 && _scene.sprites[19].x == routeX[i] && _scene.sprites[19].y == routeY[i] && endingOK;
  }
  runScriptsAt(7099);
  endingOK = _puzzlesCompleted == completedBeforeEnding && _place == 511 && endingOK;
  runScriptsAt(7100);
  endingOK = _puzzlesCompleted == completedBeforeEnding+1 && _runner.getValue(0,27,completionFlag) && completionFlag == 1 && endingOK;
  runScriptsAt(_lastSuccessEnd+999);
  endingOK = _place == 511 && endingOK;
  runScriptsAt(_lastSuccessEnd+1000);
  endingOK = _place == 388 && !_runner.pendingCount() && !_runner.clicksBlocked() &&
   _runner.getValue(0,27,completionFlag) && completionFlag == 1 && endingOK;
  // The same full program takes the other branch when not solved.
  endingOK = loadPlace(511) && endingOK;
  _runner.defineValue(1,5,0);
  Script lockInput; Command lock; lock.opcode = 28; lock.args.push_back(-1); lockInput.push_back(lock);
  endingOK = _runner.start(lockInput,0) && _runner.enqueue(_scene.scripts[0],0,true) && endingOK;
  runScriptsAt(0); runScriptsAt(0); runScriptsAt(74);
  endingOK = _runner.clicksBlocked() && _place == 511 && endingOK;
  runScriptsAt(75);
  endingOK = !_runner.clicksBlocked() && _place == 511 && _puzzlesCompleted == completedBeforeEnding+1 && endingOK;
  // Keep an immediate scene effect unsupported even after a control command.
  Script unsafeEnding = fullEnding;
  for (uint i = 0; i < unsafeEnding.size(); ++i) if (unsafeEnding[i].opcode == 45) {
   Command effect; effect.opcode = 17; effect.delay = -1; effect.args.push_back(5);
   unsafeEnding.insert_at(i+1,effect); break;
  }
  endingOK = !_runner.canRun(unsafeEnding,true) && endingOK;
  debug("Astronomica ending verification: %s (complete original P511 script 0, eight positions, success sound, P388 transition, unsolved branch, unsafe tail rejection)", endingOK ? "PASS" : "FAIL");
  scriptsOK = endingOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_audio", true);
  bool multiSuccessOK = true;
  const int successPlaces[] = {501,504,505,506,508,509,510,511,512,513,514,516,517,518,519,520,521,522,523,524,525,526,527,528,531,532,533,534,535,536};
  const int successGlobals[] = {20,21,22,23,24,25,26,27,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43,44,23,23,23,23,23,31};
  for (uint i = 0; i < ARRAYSIZE(successPlaces); ++i) {
   multiSuccessOK = loadPlace(successPlaces[i]) && multiSuccessOK;
   for (int g = 0; g < 100; ++g) _runner.defineValue(0,g,-2);
   const uint countBefore = _puzzlesCompleted, soundsBefore = _soundsStarted;
   // Nonzero flags normalize to 1 without replaying or incrementing.
   multiSuccessOK = _runner.start(originalSuccess,0,true) && multiSuccessOK;
   for (int g = 0; g < 100; ++g) {
    int32 actual = 0;
    multiSuccessOK = _runner.getValue(0,g,actual) && actual == (g == successGlobals[i] ? 1 : -2) && multiSuccessOK;
   }
   multiSuccessOK = _puzzlesCompleted == countBefore && _soundsStarted == soundsBefore && multiSuccessOK;
  }
  // A different puzzle executes its own original success command with sound.
  multiSuccessOK = loadPlace(517) && multiSuccessOK;
  Script success517;
  for (uint c = 0; c < _scene.sprites[5].click.size(); ++c)
   if (_scene.sprites[5].click[c].opcode == 23 && _scene.sprites[5].click[c].args[0] == 25) success517.push_back(_scene.sprites[5].click[c]);
  _runner.defineValue(0,33,0);
  const uint count517 = _puzzlesCompleted;
  multiSuccessOK = success517.size() == 1 && _runner.start(success517,0,true) &&
   _runner.getValue(0,33,completionFlag) && completionFlag == 1 && _puzzlesCompleted == count517+1 && _lastSound == 912 && multiSuccessOK;
  // P506 and variants P531..535 share global 23; changing scene must preserve it.
  multiSuccessOK = loadPlace(506) && multiSuccessOK; _runner.defineValue(0,23,1);
  multiSuccessOK = loadPlace(533) && _runner.start(originalSuccess,0,true) && _puzzlesCompleted == count517+1 && multiSuccessOK;
  debug("Astronomica multi-puzzle success verification: %s (30 scene mappings, 100 globals checked each, original P517 sound/count, shared P506/P533 state, silent P513 mapping)", multiSuccessOK ? "PASS" : "FAIL");
  scriptsOK = multiSuccessOK && scriptsOK;
  _runner.resetGlobals();
  for (int place = 500; place <= 537; ++place) {
   if (!loadPlace(place)) continue;
   uint admitted = 0;
   for (uint i = 0; i < _scene.scripts.size(); ++i)
    if (_runner.canRun(_scene.scripts[i],true)) ++admitted;
   debug("Astronomica puzzle coverage: P%d entry=%u/%u", place, admitted, _scene.scripts.size());
  }
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_animation", false);
  bool imageOK = true;
  const int imagePlaces[] = {505,511,509};
  const uint32 imageRGB[] = {0xc151b7ceU,0x20d2fafaU,0x5f179308U,0x345d92f2U,0xe05d7dc8U,0x22addbf3U};
  const uint32 image565[] = {0xad8d5612U,0xb18d8507U,0xc02158e3U,0x0b7246c5U,0xec80bd54U,0xa263c6caU};
  for (uint sceneIndex = 0; sceneIndex < 3; ++sceneIndex) {
   imageOK = loadPlace(imagePlaces[sceneIndex]) && imageOK;
   const uint32 beforeImage = screenRGBHash(_screen);
   Common::Array<Script> pairs;
   for (uint p = 0; p < _scene.scripts.size(); ++p) for (uint c = 0; c+1 < _scene.scripts[p].size(); ++c)
    if (_scene.scripts[p][c].opcode == 20 && _scene.scripts[p][c+1].opcode == 49) {
     Script pair; pair.push_back(_scene.scripts[p][c]); pair.push_back(_scene.scripts[p][c+1]); pairs.push_back(pair);
    }
   imageOK = pairs.size() >= 2 && imageOK;
   for (uint pairIndex = 0; pairIndex < 2 && pairIndex < pairs.size(); ++pairIndex) {
    imageOK = loadPlace(imagePlaces[sceneIndex]) && _runner.start(pairs[pairIndex],0,true) && imageOK;
    applyScriptActions(0);
    const uint32 expected = rgb565 ? image565[sceneIndex*2+pairIndex] : imageRGB[sceneIndex*2+pairIndex];
    imageOK = screenRGBHash(_screen) == expected && imageOK;
    redrawSprites(); imageOK = screenRGBHash(_screen) == expected && imageOK;
    Script missingImage = pairs[pairIndex]; missingImage[0].text = "MISSING_IMAGE";
    imageOK = !_runner.start(missingImage,0,true) && screenRGBHash(_screen) == expected && imageOK;
    missingImage[0].text = "../CLOUD3";
    imageOK = !_runner.start(missingImage,0,true) && imageOK;
    Script delayedDisplay = pairs[pairIndex]; delayedDisplay[1].delay = 1;
    imageOK = _runner.start(delayedDisplay,0,true) && imageOK; applyScriptActions(0);
    runScriptsAt(0); imageOK = _pendingImage.w > 0 && imageOK;
    runScriptsAt(1); imageOK = _pendingImage.w == 0 && screenRGBHash(_screen) == expected && imageOK;
    Script unknownImage = pairs[pairIndex]; Command unknown; unknown.opcode = 999; unknownImage.push_back(unknown);
    imageOK = !_runner.start(unknownImage,0,true) && screenRGBHash(_screen) == expected && imageOK;
   }
   imageOK = loadPlace(imagePlaces[sceneIndex]) && screenRGBHash(_screen) == beforeImage && imageOK;
  }
  // P508 stages its bitmap across branch control; this form is now admitted.
  imageOK = loadPlace(508) && _runner.canRun(_scene.scripts[1],true) && imageOK;
  debug("Astronomica background image verification: %s (six original pairs across P505/P511/P509, independent RGB hashes, redraw persistence, reload, deferred display, missing/unsafe rejection)", imageOK ? "PASS" : "FAIL");
  scriptsOK = imageOK && scriptsOK;
  bool stagedOK = loadPlace(508);
  const uint32 stagedRGB[] = {0x8030c548U,0x5f4137a0U,0x101541c3U,0x2cef2d6aU,0xc45e2cedU,0xa5dd2ad2U,0x241a9e5cU,0x75b89e6dU,0xc45e2cedU,0x2ed2ffb9U,0xa414a06eU,0x99bf6f36U,0xb08c43bcU,0xb4db34a1U,0x80b9192fU,0xa5645205U,0x60aafb01U,0x213a7946U};
  const uint32 staged565[] = {0x4068a930U,0x82a0a01eU,0xc24d9922U,0x8bff6df6U,0x72a16b4dU,0x4a6ee57bU,0xdeeef231U,0xb67036ddU,0x72a16b4dU,0xad5747f5U,0xdcbe0e03U,0x86069c4bU,0x9d56fb30U,0xc5a99ac2U,0x132050dbU,0xf3ac5cf9U,0x0d965bdcU,0x736c40b7U};
  _runner.seedRandom(1); uint32 seenChoices = 0;
  const Script stagedProgram = _scene.scripts[1];
  for (uint trial = 0; trial < 18; ++trial) {
   const uint32 before = screenRGBHash(_screen);
   stagedOK = _runner.enqueue(stagedProgram,0,true) && stagedOK;
   bool observedStaging = false;
   for (uint pass = 0; pass < 128 && _runner.pendingCount(); ++pass) {
    runScriptsAt(0);
    if (_pendingImage.w) { observedStaging = true; stagedOK = screenRGBHash(_screen) == before && stagedOK; }
   }
   int32 choice = 0; stagedOK = _runner.getValue(1,0,choice) && choice >= 1 && choice <= 18 && stagedOK;
   if (choice >= 1 && choice <= 18) {
    stagedOK = !(seenChoices & (1U << (choice-1))) &&
     screenRGBHash(_screen) == (rgb565 ? staged565[choice-1] : stagedRGB[choice-1]) && stagedOK;
    seenChoices |= 1U << (choice-1);
   }
   stagedOK = observedStaging && !_pendingImage.w && !_runner.pendingCount() && _place == 508 && stagedOK;
  }
  stagedOK = seenChoices == 0x3ffffU && stagedOK;
  // One staged image slot: a second load replaces the first without drawing.
  Script firstLoad, secondLoad, displayOnly;
  for (uint i = 0; i < stagedProgram.size(); ++i) {
   if (stagedProgram[i].opcode == 20) {
    if (firstLoad.empty()) firstLoad.push_back(stagedProgram[i]);
    else if (secondLoad.empty()) secondLoad.push_back(stagedProgram[i]);
   }
   if (stagedProgram[i].opcode == 49) displayOnly.push_back(stagedProgram[i]);
  }
  stagedOK = loadPlace(508) && stagedOK;
  const uint32 pristineImage = screenRGBHash(_screen);
  stagedOK = _runner.start(firstLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = _pendingImage.w && screenRGBHash(_screen) == pristineImage && stagedOK;
  stagedOK = _runner.start(secondLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == pristineImage && _runner.start(displayOnly,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == (rgb565 ? staged565[1] : stagedRGB[1]) && !_pendingImage.w && stagedOK;
  stagedOK = _runner.start(firstLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = loadPlace(508) && !_pendingImage.w && _runner.start(displayOnly,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == pristineImage && stagedOK;
  debug("Astronomica staged image verification: %s (full original P508 script 1, all 18 variants, deferred display, slot replacement, reload cleanup)", stagedOK ? "PASS" : "FAIL");
  scriptsOK = stagedOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  ConfMan.setBool("astronomica_animation", true);
  // Exercise the actual scene-entry path, including complete intro playback.
  ConfMan.setBool("astronomica_entry_scripts", true);
  const uint beforeIntro = _soundsStarted;
  bool entryAudioOK = loadPlace(508) && _scene.introSound && _scene.introSoundId == 302 &&
   _lastSound == 302 && _soundsStarted == beforeIntro+1 && !_mixer->isSoundHandleActive(_soundHandle) &&
   _loopSound == 0 && _runner.pendingCount() == 3;
  resumeLoopAt(5000);
  entryAudioOK = _soundsStarted == beforeIntro+1 && entryAudioOK;
  resumeLoopAt(5001);
  entryAudioOK = _lastSound == 0 && _soundsStarted == beforeIntro+2 && _mixer->isSoundHandleActive(_soundHandle) && entryAudioOK;
  playSound(8,6000);
  resumeLoopAt(12000);
  entryAudioOK = _lastSound == 8 && entryAudioOK;
  _mixer->stopHandle(_soundHandle); resumeLoopAt(12000);
  entryAudioOK = _lastSound == 0 && entryAudioOK;
  ConfMan.setBool("astronomica_entry_scripts", false);
  entryAudioOK = loadPlace(103) && _loopSound == -1 && !_mixer->isSoundHandleActive(_soundHandle) && entryAudioOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_entry_scripts", true);
  const uint beforeSilentEntry = _soundsStarted;
  entryAudioOK = loadPlace(508) && _soundsStarted == beforeSilentEntry && _loopSound == -1 && entryAudioOK;
  ConfMan.setBool("astronomica_entry_scripts", false);
  ConfMan.setBool("astronomica_audio", true);
  debug("Astronomica entry audio verification: %s (P508 S302 intro completes before scripts, default S0 loop, foreground priority, reload cleanup, audio disabled)", entryAudioOK ? "PASS" : "FAIL");
  scriptsOK = entryAudioOK && scriptsOK;
  bool answersOK = true;
  for (uint wrong = 0; wrong < 2; ++wrong) {
   _runner.resetGlobals(); _runner.seedRandom(1);
   answersOK = loadPlace(508) && answersOK;
   Script correctSound; Command correctSoundCommand; correctSoundCommand.opcode = 9; correctSoundCommand.args.push_back(9); correctSound.push_back(correctSoundCommand);
   const uint beforeCorrectSound = _soundsStarted;
   answersOK = _runner.start(correctSound,0,true) && answersOK; applyScriptActions(0);
   answersOK = _lastSound == 8 && _soundsStarted == beforeCorrectSound+1 && answersOK;
   _mixer->stopHandle(_soundHandle);
   const uint32 completedBefore = _puzzlesCompleted;
   answersOK = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && answersOK;
   uint32 answerTime = 0;
   for (uint pass = 0; pass < 128 && _runner.pendingCount(); ++pass) { runScriptsAt(answerTime); answerTime += 50; }
   answersOK = !_runner.pendingCount() && !_runner.clicksBlocked() && answersOK;
   const uint count = wrong ? 3 : 8;
   for (uint answer = 0; answer < count && _place == 508; ++answer) {
    int32 choice = 0; answersOK = _runner.getValue(1,0,choice) && choice >= 1 && choice <= 18 && answersOK;
    const bool upper = (choice > 12) != bool(wrong);
    const int x = upper ? 223 : 222, y = upper ? 188 : 253;
    answersOK = spriteAt(x,y) == (upper ? 4 : 6) && answersOK;
    clickAtTime(x,y,answerTime);
    answersOK = _runner.pendingCount() > 0 && answersOK;
    // Drive the same input/scheduler paths as the interactive loop.
    for (uint pass = 0; pass < 1200 && _place == 508 && _runner.pendingCount(); ++pass) {
     runScriptsAt(answerTime); animateSpritesAt(answerTime); answerTime += 50;
    }
    if (answer+1 < count) {
     int32 score = 0;
     answersOK = _place == 508 && !_runner.clicksBlocked() && !_runner.pendingCount() &&
      _runner.getValue(1,wrong ? 3 : 4,score) && score == int32(answer+1) && answersOK;
    }
   }
   int32 solved = 0;
   answersOK = _place == 388 && !_runner.pendingCount() && _runner.getValue(0,24,solved) &&
    solved == (wrong ? 0 : 1) && _puzzlesCompleted == completedBefore+(wrong ? 0 : 1) && answersOK;
   debug("Astronomica P508 %s route: %s (destination P%d, success=%d)",wrong ? "three-error" : "eight-answer",answersOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P508 interaction verification: %s (original startup and click programs, eight correct answers and three-error exit)",answersOK ? "PASS" : "FAIL");
  scriptsOK = answersOK && scriptsOK;
  // Original P509 delayed entry: first command becomes eligible after 3500 ms.
  bool delayedEntryOK = loadPlace(509) && _scene.scripts.size() == 6 && _scene.scripts[0][0].delay == 3500;
  Common::Array<Script> delayedEntry; delayedEntry.push_back(_scene.scripts[0]);
  delayedEntryOK = _runner.enqueueStartup(delayedEntry,0,true) == 1 && delayedEntryOK;
  int32 enabled = -1;
  runScriptsAt(3499);
  delayedEntryOK = _runner.getValue(1,15,enabled) && enabled == 0 && _runner.pendingCount() == 1 && delayedEntryOK;
  runScriptsAt(3500);
  delayedEntryOK = _runner.getValue(1,15,enabled) && enabled == 1 && !_runner.pendingCount() && delayedEntryOK;
  debug("Astronomica delayed entry verification: %s (original P509 script 0, 3499/3500 ms)",delayedEntryOK ? "PASS" : "FAIL");
  scriptsOK = delayedEntryOK && scriptsOK;
  scriptsOK = verifyAuroraPuzzle() && scriptsOK;
  scriptsOK = verifySpectrumPuzzle() && scriptsOK;
  scriptsOK = verifyMoveFrameCommand() && scriptsOK;
  scriptsOK = verifySolarPuzzle() && scriptsOK;
  scriptsOK = verifyUniversePuzzle() && scriptsOK;
  scriptsOK = verifyP530Puzzle() && scriptsOK;
  scriptsOK = verifyEclipsePuzzle() && scriptsOK;
  scriptsOK = verifyP521Puzzle() && scriptsOK;
  scriptsOK = verifyP518Puzzle() && scriptsOK;
  scriptsOK = verifyP526Puzzle() && scriptsOK;
  scriptsOK = verifyP512Puzzle() && scriptsOK;
  scriptsOK = verifyBuilderPuzzle() && scriptsOK;
  scriptsOK = verifyP514Puzzle() && scriptsOK;
  scriptsOK = verifyP513Puzzle() && scriptsOK;
  scriptsOK = verifyP507Wheel() && scriptsOK;
  scriptsOK = verifyCometPuzzles() && scriptsOK;
  scriptsOK = verifyP516Puzzle() && scriptsOK;
  scriptsOK = verifyP510Puzzle() && scriptsOK;
  scriptsOK = verifyLegacySaves() && scriptsOK;
  scriptsOK = verifyHelp() && scriptsOK;
  scriptsOK = verifyHover() && scriptsOK;
  scriptsOK = verifyWorldMovie29() && verifyWorldMovies(false) && scriptsOK;
  scriptsOK = verifyIntro() && scriptsOK;
  scriptsOK = verifyLogo(false) && scriptsOK;
  scriptsOK = verifyPostCredits() && scriptsOK;
  scriptsOK = verifyEndings() && scriptsOK;
  scriptsOK = verifyAdvice() && scriptsOK;
  scriptsOK = verifyGameState() && scriptsOK;
  scriptsOK = verifyTransitions() && scriptsOK;
  scriptsOK = verifyP523Puzzle() && scriptsOK;
  scriptsOK = verifyMentors() && scriptsOK;
  scriptsOK = verifySaves() && scriptsOK;
  scriptsOK = verifyP501Puzzle() && scriptsOK;
  scriptsOK = verifyP522Puzzle() && scriptsOK;
  scriptsOK = verifyP524Puzzle() && scriptsOK;
  scriptsOK = verifyVariantPuzzles() && scriptsOK;
  // P537 selector: exercise original clicks, including both clamped limits.
  bool selectorOK = loadPlace(537) && _scene.sprites.size() == 48;
  for (uint i = 9; i <= 28 && i < _scene.sprites.size(); ++i)
   selectorOK = _scene.sprites[i].selectedFrame == 0 && staticSpriteFrame(_scene,i) && selectorOK;
  int32 selection = -1;
  uint32 selectorTime = 0;
  auto selectStep = [&](int sprite, int expected) {
   const Sprite &button = _scene.sprites[sprite];
   selectorOK = spriteAt(button.x+1,button.y+1) == sprite && selectorOK;
   clickAtTime(button.x+1,button.y+1,selectorTime);
   for (uint tick = 0; tick <= 600; tick += 20) runScriptsAt(selectorTime+tick);
   selectorOK = _runner.getValue(1,0,selection) && selection == expected && !_runner.clicksBlocked() && selectorOK;
   if (expected > 0) {
    const uint indicator = expected == 1 ? 6 : 32+expected;
    selectorOK = _scene.sprites[indicator].visible && staticSpriteFrame(_scene,indicator) && selectorOK;
   }
   selectorTime += 1000;
  };
  selectStep(4,0);
  for (int value = 1; value <= 15; ++value) selectStep(5,value);
  selectStep(5,15);
  for (int value = 14; value >= 0; --value) selectStep(4,value);
  selectorOK = _runner.canRun(_scene.sprites[32].click,true) && selectorOK;
  debug("Astronomica P537 selector verification: %s (original clicks, 0..15, both bounds, inherited clone frames)",selectorOK ? "PASS" : "FAIL");
  scriptsOK = selectorOK && scriptsOK;
  {
   bool stopSpriteOK = loadPlace(517);
   Command stopCommand;
   for (uint i = 0; i < _scene.scripts.size(); ++i)
    for (uint j = 0; j < _scene.scripts[i].size(); ++j)
     if (_scene.scripts[i][j].opcode == 30) stopCommand = _scene.scripts[i][j];
   stopSpriteOK = stopCommand.opcode == 30 && stopCommand.args.size() == 1 && stopSpriteOK;
   if (stopSpriteOK) {
    Sprite &target = _scene.sprites[stopCommand.args[0]-1];
    const int32 x = target.x, y = target.y, frame = target.selectedFrame;
    target.autoMove = target.autoFrame = true; target.visible = 1; target.frameSince = 123;
    stopCommand.delay = 0; Script halt; halt.push_back(stopCommand);
    stopSpriteOK = _runner.start(halt,0,true) && stopSpriteOK; applyScriptActions(0);
    stopSpriteOK = !target.autoMove && !target.autoFrame && !target.visible &&
     target.frameData[0] == -1 && target.moveData[0] == -1 && target.x == x && target.y == y &&
     target.selectedFrame == frame && target.frameSince == 123 && stopSpriteOK;
    halt[0].args[0] = 999;
    stopSpriteOK = !_runner.canRun(halt,true) && stopSpriteOK;
   }
   debug("Astronomica stop/hide verification: %s (original P517 command 30, both timers, preserved position/frame)",stopSpriteOK ? "PASS" : "FAIL");
   scriptsOK = stopSpriteOK && scriptsOK;
   loadPlace(537);
  }
  uint32 originalRocketHash = 0;
  bool rocketOK = verifyRocketOriginalCallbacks(originalRocketHash);
  debug("Astronomica P537 original callback comparison: %s (96 fixtures, 14592 steps, %08x)",rocketOK ? "PASS" : "FAIL",originalRocketHash);
  // Independent endpoint/readout checks for every selectable nonzero setting.
  for (int setting = 1; setting <= 15; ++setting) {
   Scene flight = _scene; RocketMotion motion;
   rocketOK = startRocket(flight,motion,setting) && advanceRocket(flight,motion,setting,9) == 0 && rocketOK;
   int result = 0; uint steps = 0;
   while (motion.kind != RocketMotion::kStopped && steps < 300) {
    ++steps; result = advanceRocket(flight,motion,setting,steps*10);
   }
   const bool orbit = setting == 11 || setting == 12;
   const Sprite &r = flight.sprites[33];
   rocketOK = steps == (setting <= 10 ? 250U : orbit ? 150U : 56U) &&
    result == (orbit ? 3 : 2) && r.renderX == (setting <= 10 ? 500 : orbit ? 450 : 632) &&
    r.renderY == (setting <= 10 ? 200 : orbit ? 2 : -89) &&
    r.selectedFrame == (setting <= 10 ? 9 : orbit ? 4 : 8) && bool(r.visible) == orbit && rocketOK;
   rocketOK = flight.sprites[8].selectedFrame == 9 && flight.sprites[24].selectedFrame == 2 &&
    flight.sprites[25].selectedFrame == 5 && rocketOK;
   for (uint i = 8; i <= 28; ++i) rocketOK = !flight.sprites[i].autoFrame && rocketOK;
  }
  {
   Scene flight = _scene; RocketMotion motion; motion.since = 0xfffffffbU;
   rocketOK = startRocket(flight,motion,1) && advanceRocket(flight,motion,1,4) == 0 &&
    advanceRocket(flight,motion,1,5) == 1 && flight.sprites[33].renderX == 2 &&
    advanceRocket(flight,motion,1,10005) == 1 && flight.sprites[33].renderX == 4 && rocketOK;
  }
  const int settings[] = {0,1,10,11,12,13,15};
  for (uint route = 0; route < ARRAYSIZE(settings); ++route) {
   const int setting = settings[route];
   const bool success = setting == 11 || setting == 12;
   _runner.resetGlobals();
   rocketOK = loadPlace(537) && rocketOK;
   const uint beforeCompleted = _puzzlesCompleted;
   uint32 now = 0;
   auto settleRocket = [&](uint32 duration) {
    const uint32 end = now+duration;
    while (now < end && _place == 537) {
     runScriptsAt(now); animateSpritesAt(now); now += 10;
    }
   };
   for (int value = 1; value <= setting; ++value) {
    clickAtTime(154,421,now); settleRocket(600);
    int32 actual = -1;
    rocketOK = _runner.getValue(1,0,actual) && actual == value && rocketOK;
   }
   rocketOK = spriteAt(188,412) == 32 && rocketOK;
   clickAtTime(188,412,now); settleRocket(30000);
   int32 solved = -1;
   rocketOK = _runner.getValue(0,36,solved) && solved == int(success) &&
    _puzzlesCompleted == beforeCompleted+uint(success) && _rocket.kind == RocketMotion::kStopped && rocketOK;
   if (success) {
    rocketOK = _place == 321 && rocketOK;
    if (setting == 12) {
     rocketOK = loadPlace(537) && rocketOK;
     for (int value = 1; value <= 11; ++value) { clickAtTime(154,421,now); settleRocket(600); }
     clickAtTime(188,412,now); settleRocket(30000);
     rocketOK = _place == 321 && _puzzlesCompleted == beforeCompleted+1 && rocketOK;
    }
   }
   else {
    rocketOK = _place == 537 && !_runner.clicksBlocked() && rocketOK;
    if (setting) {
     const Sprite &r = _scene.sprites[33];
     rocketOK = !r.visible && r.renderX == (setting <= 10 ? 500 : 632) &&
      r.renderY == (setting <= 10 ? 200 : -89) && rocketOK;
    }
    clickAtTime(24,417,now); settleRocket(2000);
    rocketOK = _place == 321 && rocketOK;
   }
   debug("Astronomica P537 launch %d: %s (P%d, global36=%d)",setting,rocketOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P537 rocket verification: %s (original controls, zero/slow/orbit/fast, both successful settings, exit)",rocketOK ? "PASS" : "FAIL");
  scriptsOK = rocketOK && scriptsOK;
  bool ringsOK = true;
  for (uint route = 0; route < 3; ++route) {
   _runner.resetGlobals(); ringsOK = loadPlace(527) && _movie && ringsOK;
   const uint beforeCompleted = _puzzlesCompleted;
   uint32 now = 0;
   const int choices[] = {1,3,4,2};
   uint32 seen = 0;
   const uint selections = route == 0 ? 4 : 1;
   for (uint choice = 0; choice < selections && _place == 527; ++choice) {
    const int selected = route == 0 ? choices[choice] : route == 1 ? 2 : 1;
    const Sprite &ringButton = _scene.sprites[selected-1];
    // Adjacent 29-pixel buttons overlap at their edges; use their centers.
    ringsOK = spriteAt(ringButton.x+14,ringButton.y+13) == selected-1 && ringsOK;
    clickAtTime(ringButton.x+14,ringButton.y+13,now);
    for (uint tick = 0; tick < 600; tick += 10) { runScriptsAt(now); now += 10; }
    clickAtTime(400,393,now);
    for (uint tick = 0; tick < 200 && !_moviePlaying; ++tick) { runScriptsAt(now); now += 10; }
    const uint32 starts[] = {1800,2568,900,0};
    const uint32 lengths[] = {599,959,899,899};
    ringsOK = _movie && _moviePlaying && _movieX == 10 && _movieY == 10 &&
     _movie->getEndTime() == Audio::Timestamp(0,starts[selected-1]+lengths[selected-1],30) && ringsOK;
    debug("Astronomica P527 selection %d: movie=%d end=%u expected=%u status=%d",selected,_moviePlaying,_movie ? _movie->getEndTime().msecs() : 0,Audio::Timestamp(0,starts[selected-1]+lengths[selected-1],30).msecs(),ringsOK);
    if (_movie) {
     const uint beforeFrames = _movieFramesDrawn;
     updateMovie();
     ringsOK = _movieFramesDrawn == beforeFrames+1 && _movieFrame.w > 0 && ringsOK;
     if (route == 0 && choice == 0) {
      const uint32 movieTime = _movie->getTime();
      Command movieSpeech; movieSpeech.opcode = 9; movieSpeech.args.push_back(8);
      Script speech; speech.push_back(movieSpeech);
      ringsOK = isBlockingSound(7) && _runner.start(speech,now,true) &&
       !_movie->isPaused() && _lastSound == 7 && _lastBlockingSoundEnd > now &&
       _movie->getTime()-movieTime < 100 && ringsOK;
      now = _lastBlockingSoundEnd;
      debug("Astronomica P527 movie/speech pause verification: %s",ringsOK ? "PASS" : "FAIL");
     }
     redrawSprites();
     for (int y = 0; y < _movieFrame.h; ++y) for (int x = 0; x < _movieFrame.w; ++x)
      ringsOK = _screen.getPixel(x+10,y+10) == _movieFrame.getPixel(x,y) && ringsOK;
     ringsOK = _movie->seek(_movie->getEndTime()) && ringsOK;
     updateMovie(); ringsOK = !_moviePlaying && ringsOK;
     debug("Astronomica P527 decoded/retained: frames=%u status=%d",_movieFramesDrawn-beforeFrames,ringsOK);
    }
    seen |= 1U << (selected-1);
    for (uint tick = 0; tick < 45000 && _place == 527 && _runner.pendingCount(); tick += 50) {
     runScriptsAt(now); now += 50;
    }
    if (_place == 527) {
     int32 flags = -1;
     ringsOK = _runner.getValue(1,5,flags) && flags == int32(seen) && !_runner.clicksBlocked() && ringsOK;
     debug("Astronomica P527 seen=%d expected=%u blocked=%d",flags,seen,_runner.clicksBlocked());
    }
   }
   if (_place == 527) {
    clickAtTime(24,417,now);
    for (uint tick = 0; tick < 5000 && _place == 527; tick += 50) { runScriptsAt(now); now += 50; }
   }
   int32 solved = -1;
   ringsOK = _place == 174 && !_movie && !_movieFrame.w && _runner.getValue(0,43,solved) &&
    solved == int(route != 2) && _puzzlesCompleted == beforeCompleted+uint(route != 2) && ringsOK;
   debug("Astronomica P527 route %u: %s (P%d, global43=%d)",route,ringsOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P527 interaction verification: %s (four selections, movie frames, redraw retention, early solved/unsolved exit)",ringsOK ? "PASS" : "FAIL");
  scriptsOK = ringsOK && scriptsOK;
  bool movieOK = loadPlace(520) && _movie && _movie->getTimeScale() == 30;
  if (_movie) {
   movieOK = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && movieOK;
   runScriptsAt(0); runScriptsAt(0);
   const uint beforeFrames = _movieFramesDrawn;
   updateMovie();
   movieOK = _moviePlaying && _movieX == 240 && _movieY == 130 && _movieFramesDrawn == beforeFrames+1 &&
    _movie->getEndTime() == Audio::Timestamp(0,56681,30) && movieOK;
   for (uint point = 0; point < 3; ++point) {
    const uint32 tick = 55407 + point*600;
    movieOK = _movie->seek(Audio::Timestamp(0,tick,30)) && movieOK;
    const Graphics::Surface *frame = _movie->decodeNextFrame();
    movieOK = frame && frame->w > 0 && frame->h > 0 && movieOK;
   }
   runScriptsAt(43999); movieOK = _place == 520 && movieOK;
   runScriptsAt(44000); movieOK = _place == 537 && !_movie && !_moviePlaying && movieOK;
   movieOK = loadPlace(520) && movieOK;
   movieOK = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && movieOK;
   runScriptsAt(0); runScriptsAt(0);
   clickAtTime(10,10,1); runScriptsAt(1);
   movieOK = _place == 537 && !_movie && !_runner.pendingCount() && movieOK;
  }
  debug("Astronomica P520 movie verification: %s (original segment, three decoded positions, timed P537 transition, click skip and decoder cleanup)",movieOK ? "PASS" : "FAIL");
  scriptsOK = movieOK && scriptsOK;
  // P505: all eight original prompts, using rectangle clicks only.
  bool historyOK = true;
  for (uint wrong = 0; wrong < 2; ++wrong) {
   _runner.resetGlobals(); _runner.seedRandom(1);
   historyOK = loadPlace(505) && historyOK;
   const uint completedBefore = _puzzlesCompleted;
   historyOK = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && historyOK;
   uint32 now = 0;
   auto settle = [&]() {
    uint pass = 0;
    while (_runner.pendingCount() && pass++ < 3000) {
     runScriptsAt(now); animateSpritesAt(now); now += 50;
    }
    return !_runner.pendingCount() && !_runner.clicksBlocked();
   };
   historyOK = settle() && historyOK;
   const int correctRects[] = {9,4,1,8,7,3,5,6};
   for (uint answer = 0; answer < (wrong ? 3U : 8U) && _place == 505; ++answer) {
    int32 prompt = 0;
    if (!_runner.getValue(1,0,prompt) || prompt < 1 || prompt > 8) { historyOK = false; break; }
    const MouseRect &r = _scene.mouseRects[wrong ? 2 : correctRects[prompt-1]];
    const int x = (r.rect[0]+r.rect[2])/2, y = (r.rect[1]+r.rect[3])/2;
    historyOK = spriteAt(x,y) == -1 && !_runner.clicksBlocked() && historyOK;
    clickAtTime(x,y,now);
    historyOK = _runner.pendingCount() > 0 && settle() && historyOK;
    if (_place == 505) {
     int32 errors = -1;
     historyOK = _runner.getValue(1,2,errors) && errors == (wrong ? int32(answer+1) : 0) && historyOK;
    }
   }
   int32 solved = -1;
   historyOK = _place == (wrong ? 321 : 520) && _runner.getValue(0,22,solved) && solved == (wrong ? 0 : 1) &&
    _puzzlesCompleted == completedBefore+(wrong ? 0 : 1) && historyOK;
   debug("Astronomica P505 route %u: %s (destination P%d, success=%d)",wrong,historyOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P505 interaction verification: %s (eight original prompts, blocking speech, image clicks, three-error exit; P520 continuation verified separately)",historyOK ? "PASS" : "FAIL");
  scriptsOK = historyOK && scriptsOK;
  bool skyOK = true;
  for (uint route = 0; route < 2; ++route) {
   _runner.resetGlobals();
   skyOK = loadPlace(509) && skyOK;
   const uint completedBefore = _puzzlesCompleted;
   const uint skyEntries = _runner.enqueueStartup(_scene.scripts,0,true);
   skyOK = skyEntries == 6 && skyOK;
   debug("Astronomica P509 test startup: %u/6",skyEntries);
   uint32 now = 0;
   auto advance = [&](uint32 duration) {
    const uint32 end = now + duration;
    while (now < end && _place == 509) { runScriptsAt(now); animateSpritesAt(now); now += 50; }
   };
   auto valueIs = [&](int id, int expected) { int32 v = -1; return _runner.getValue(1,id,v) && v == expected; };
   auto choose = [&](int option) {
    const int xs[] = {83,166,257,338,408,490};
    if (_place != 509 || _runner.clicksBlocked() || spriteAt(xs[option-1],365) != option+3) return false;
    clickAtTime(xs[option-1],365,now); advance(1000);
    return !_runner.clicksBlocked() && valueIs(7,option);
   };
   auto target = [&](int rect) {
    if (_place != 509 || _runner.clicksBlocked()) return false;
    const MouseRect &r = _scene.mouseRects[rect];
    const int x = (r.rect[0]+r.rect[2])/2, y = (r.rect[1]+r.rect[3])/2;
    if (spriteAt(x,y) != -1) return false;
    clickAtTime(x,y,now); advance(2000);
    return _place != 509 || !_runner.clicksBlocked();
   };
   advance(4000);
   skyOK = valueIs(15,1) && valueIs(16,2) && !_runner.clicksBlocked() && skyOK;
   if (route == 0) {
    // Remove all six sources, then the remaining sources in the second sky.
    const int order[] = {0,1,2,4,3,5}, options[] = {2,1,1,2,1,3};
    for (uint i = 0; i < 6; ++i) {
     const bool selected = choose(options[i]), clicked = target(order[i]);
     skyOK = selected && clicked && skyOK;
     debug("Astronomica P509 target %d: selected=%d clicked=%d",order[i],selected,clicked);
    }
    skyOK = valueIs(16,1) && skyOK;
    skyOK = choose(1) && target(3) && skyOK;
    skyOK = choose(3) && target(5) && skyOK;
    advance(30000);
   } else {
    // Three wrong classifications must take the original failure route.
    skyOK = choose(3) && skyOK;
    for (int i = 0; i < 3; ++i) skyOK = target(0) && skyOK;
    advance(20000);
   }
   int32 solved = -1;
   skyOK = _place == 304 && _runner.getValue(0,25,solved) && solved == (route ? 0 : 1) &&
    _puzzlesCompleted == completedBefore+(route ? 0 : 1) && skyOK;
   debug("Astronomica P509 route %u: %s (destination P%d, success=%d)",route,skyOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P509 interaction verification: %s (original startup, timed image hotspots, two skies, three-error route)",skyOK ? "PASS" : "FAIL");
  scriptsOK = skyOK && scriptsOK;
  // P511: solve from the original initial conditions using only hit-tested clicks.
  bool controlsOK = true;
  for (uint route = 0; route < 3; ++route) {
   _runner.resetGlobals();
   controlsOK = loadPlace(511) && controlsOK;
   const uint completedBefore = _puzzlesCompleted;
   controlsOK = _runner.enqueueStartup(_scene.scripts,0,true) == 5 && controlsOK;
   uint32 now = 0;
   auto settle = [&]() {
    uint pass = 0;
    while (_runner.pendingCount() && pass++ < 1200) {
     runScriptsAt(now); animateSpritesAt(now); now += 50;
    }
    return !_runner.pendingCount() && !_runner.clicksBlocked();
   };
   auto valueIs = [&](int id, int expected) {
    int32 v = 0; return _runner.getValue(1,id,v) && v == expected;
   };
   auto press = [&](int sprite, int x, int y) {
    if (_place != 511 || _runner.clicksBlocked() || spriteAt(x,y) != sprite) return false;
    clickAtTime(x,y,now);
    if (!_runner.pendingCount()) return false;
    return settle();
   };
   controlsOK = settle() && valueIs(0,52) && valueIs(2,0) && valueIs(3,4) && valueIs(5,0) && controlsOK;
   if (route == 2) {
    controlsOK = press(1,35,430) && _place == 388 && controlsOK;
    int32 solved = -1;
    controlsOK = _runner.getValue(0,27,solved) && solved == 0 && _puzzlesCompleted == completedBefore && controlsOK;
    continue;
   }
   // Lower/upper clamp and reversible controls, before any solution.
   controlsOK = press(9,300,430) && valueIs(2,0) && controlsOK;
   controlsOK = press(17,534,443) && valueIs(0,52) && controlsOK;
   controlsOK = press(13,151,380) && valueIs(3,2) && controlsOK;
   controlsOK = press(14,179,380) && valueIs(3,3) && controlsOK;
   controlsOK = press(15,204,400) && valueIs(3,4) && controlsOK;
   auto setFirst = [&]() { return press(12,125,400) && (_place == 388 || valueIs(3,1)); };
   auto setDial = [&]() {
    bool ok = true;
    for (int step = 1; step <= 15; ++step) ok = press(10,376,430) && valueIs(2,step) && ok;
    ok = press(10,376,430) && valueIs(2,15) && ok;
    ok = press(9,300,430) && valueIs(2,14) && ok;
    return press(10,376,430) && valueIs(2,15) && ok;
   };
   auto clearClouds = [&]() {
    bool ok = true;
    for (int step = 1; step <= 13; ++step) {
     ok = press(16,440,443) && ok;
     if (_place == 511) ok = valueIs(0,52-step*4) && ok;
    }
    return ok;
   };
   if (route == 0) {
    controlsOK = setFirst() && controlsOK;
    controlsOK = setDial() && controlsOK;
    controlsOK = clearClouds() && controlsOK;
   } else {
    controlsOK = clearClouds() && controlsOK;
    controlsOK = press(16,440,443) && valueIs(0,0) && controlsOK;
    controlsOK = press(17,534,443) && valueIs(0,4) && controlsOK;
    controlsOK = press(16,440,443) && valueIs(0,0) && controlsOK;
    controlsOK = setDial() && controlsOK;
    controlsOK = setFirst() && controlsOK;
   }
   int32 solved = 0;
   controlsOK = _place == 388 && _runner.getValue(0,27,solved) && solved == 1 &&
    _puzzlesCompleted == completedBefore+1 && controlsOK;
   debug("Astronomica P511 click route %u: %s (destination P%d, success=%d)",route,controlsOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P511 interaction verification: %s (original initial state, hit-tested controls, bounds, reversal, two solution orders, unsolved exit)",controlsOK ? "PASS" : "FAIL");
  scriptsOK = controlsOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  ConfMan.setBool("astronomica_animation", false);
  // Full, unmodified P29 entry program: repeated show/hide and self-call.
  bool timerOK = loadPlace(29) && _scene.scripts.size() == 1;
  timerOK = _runner.enqueueStartup(_scene.scripts, 0, true) == 1 && timerOK;
  runScriptsAt(0); runScriptsAt(0); runScriptsAt(0); runScriptsAt(0);
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && timerOK;
  const uint beforeTimer = _runner.executedCount();
  runScriptsAt(599);
  timerOK = _runner.executedCount() == beforeTimer && timerOK;
  runScriptsAt(600); // queues the entry; does not run it during this pass
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && timerOK;
  runScriptsAt(600); runScriptsAt(600); runScriptsAt(600);
  timerOK = !_scene.sprites[1].visible && screenRGBHash(_screen) == (rgb565 ? 0xf46c822eU : 0xa8aa76a9U) && timerOK;
  runScriptsAt(1199);
  timerOK = !_scene.sprites[1].visible && timerOK;
  runScriptsAt(1200); runScriptsAt(1200); runScriptsAt(1200); runScriptsAt(1200); runScriptsAt(1200);
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && screenRGBHash(_screen) == (rgb565 ? 0x97802e24U : 0xca004a3bU) && timerOK;
  debug("Astronomica timer verification: %s (P29 complete original script, 599/600/1199/1200 ms)", timerOK ? "PASS" : "FAIL");
  scriptsOK = timerOK && scriptsOK;
  // Global values survive ordinary scene loads and reset on entry to P1.
  _runner.defineValue(0, 99, 123);
  bool lifecycleOK = loadPlace(103) && _runner.getValue(0, 99, state) && state == 123;
  lifecycleOK = loadPlace(1) && lifecycleOK;
  for (int id = 0; id < 100; ++id)
   lifecycleOK = _runner.getValue(0, id, state) && state == 0 && lifecycleOK;
  debug("Astronomica lifecycle verification: %s (100 globals, P1 reset, P505 entry queue)", lifecycleOK && conditionsOK ? "PASS" : "FAIL");
  scriptsOK = scriptsOK && lifecycleOK;
  scriptsOK = scriptsOK && conditionsOK;
  // Exercise actual input dispatch, queueing and scene loading against the
  // independently readable P103 PLACEDEF and its compiled command stream.
  scriptsOK = scriptsOK && loadPlace(103);
  clickAt(310, 61); runScripts();
  scriptsOK = scriptsOK && _place == 103;
  clickAt(552, 61); runScripts();
  scriptsOK = scriptsOK && _place == 103;
  clickAt(311, 61);
  scriptsOK = scriptsOK && _place == 103 && _runner.pendingCount() == 1;
  runScripts();
  scriptsOK = scriptsOK && _place == 126 && _previousPlace == 103 && !_runner.pendingCount();
  debug("Astronomica script verification: %s (scheduler and P103 -> P126 click)", scriptsOK ? "PASS" : "FAIL");
  _background.free(); _screen.free();
  quitGame();
  return scriptsOK && loaded == 420 && bitmaps == 3625 && commands == 10316 && tails == 4 ? Common::kNoError : Common::Error(Common::kReadingFailed, "Resource or script verification failed");
 }
 while (!shouldQuit()) {
  Common::Event event;
  while (_eventMan->pollEvent(event)) {
   if (_worldMovieCursorBottom >= 0 && event.type == Common::EVENT_MOUSEMOVE && event.mouse.y < _worldMovieCursorBottom)
    _system->warpMouse(event.mouse.x,_worldMovieCursorBottom);
   if (event.type == Common::EVENT_LBUTTONDOWN) { clickAt(event.mouse.x, event.mouse.y); continue; }
   if (event.type != Common::EVENT_KEYDOWN) continue;
   switch (event.kbd.keycode) {
   case Common::KEYCODE_F5: openMainMenuDialog(); break;
   case Common::KEYCODE_ESCAPE: quitGame(); break;
   case Common::KEYCODE_v: if (_place == 29 && _scene.sprites.size() >= 2) demoVisibility(!_scene.sprites[1].visible); break;
   case Common::KEYCODE_m:
    if (_place == 517 && _scene.sprites.size() >= 7) demoMovement(_scene.sprites[6].x == 447 ? 477 : 447);
    else if (_place == 510) demoOffset();
    break;
   case Common::KEYCODE_r: if (_place == 510) changePlace(510); break;
   case Common::KEYCODE_c: if (_place == 510) demoOffset(9); break;
   case Common::KEYCODE_f: if (_place == 510 && _scene.sprites.size() >= 10) demoFrame(_scene.sprites[9].selectedFrame == 1 ? 0 : 1); break;
   case Common::KEYCODE_PAGEDOWN: stepPlace(1); break;
   case Common::KEYCODE_PAGEUP: stepPlace(-1); break;
   case Common::KEYCODE_LEFT: if (_nav[0] > 0) changePlace(_nav[0]); break;
   case Common::KEYCODE_UP: if (_nav[1] > 0) changePlace(_nav[1]); break;
   case Common::KEYCODE_RIGHT: if (_nav[2] > 0) changePlace(_nav[2]); break;
   default: break;
   }
  }
  runScripts();
  const Common::Point mouse = _eventMan->getMousePos();
  hoverAtTime(mouse.x,mouse.y,scriptClock());
  updateWorldAt(scriptClock());
  animateSpritesAt(scriptClock());
  resumeLoopAt(scriptClock());
  updateMovie();
  // Cursor movement must be presented even when no scene pixels changed.
  _system->updateScreen();
  _system->delayMillis(10);
 }
 _background.free(); _screen.free();
 return Common::kNoError;
}
}



