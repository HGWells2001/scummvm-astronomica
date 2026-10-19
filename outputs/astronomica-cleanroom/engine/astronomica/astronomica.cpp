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
 const bool enabled = canSaveQuestion() || canSaveP513() || canSaveP519() || canSaveP524() || canSaveP526() || canSaveP528() || canSaveP530() || canSaveVariant() || (_place > 1 && _scene.mode == 1 && !_runner.variantRound() && !_runner.clicksBlocked() && !_runner.pendingCount());
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
 _movieSegmentStart = 0; _plotEvent = 0; _plotTime = 0;
 _dangerEvent[0] = _dangerEvent[1] = 0; _dangerButtons = 0;
 _movieFrame.free();
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
 for (int y = 0; y < height; ++y) for (int x = 0; x < 640; ++x) {
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
 _loopSound = -1; _loopEnabled = true; _lastSoundAt = 0;
 _scene = parsed;
 _questionSaveBaseline.clear(); if (questionProfile(place) || variantProfile(place) || place == 513 || place == 519 || place == 524 || place == 526 || place == 528 || place == 530) _questionSaveBaseline = _scene.sprites;
 _rocket = RocketMotion();
 _probe = ProbeMotion();
 _ball = BallMotion();
 // The original orientation phase is process-global, unlike the sprite links.
 const int oldCometFrame = _comet.frame, oldCometPrevious = _comet.previousFrame;
 _comet = CometMotion(); _comet.frame = oldCometFrame; _comet.previousFrame = oldCometPrevious;
 _runner.loadLocalConditions(_scene.conditions);
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
 // P515 is absent from custom25's original dispatch table. Its shared
 // script contains an unreachable success branch before entering P536.
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
 _movieFrame.free();
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
   _movieFrame.free(); presentScene(); dirty = false; continue;
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
 if (_place == 522 && _probe.expired) { changePlace(388); return; }
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
  now = scriptClock(); if (!select(setting) || !roundTrip(4,false)) return false;
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

bool AstronomicaEngine::verifyP510Puzzle() {
 uint32 hash = 2166136261U;
 const int events[] = {20,21,22,23,24,25,26,27,28,29,30,31,32,40,41,42,43,44,46,47,48,49,50,51,52,53,54};
 for (int event : events) for (int choice = -1; choice <= 6; ++choice) for (int solved = 0; solved < 2; ++solved) {
  const PlotStep s = plotCallback(event,choice);
  const int fields[] = {s.x,s.y,s.start,s.duration,s.event,s.time,int(s.play),int(s.leave),int(s.success)};
  for (int field : fields) hash = (hash ^ uint32(field))*16777619U;
 }
 bool ok = hash == 0x33d6e7a1U;
 debug("Astronomica P510 original callback comparison: %s (432 cases, %08x)",ok ? "PASS" : "FAIL",hash);
 const bool continuous = ConfMan.hasKey("astronomica_p510_continuous") && ConfMan.getBool("astronomica_p510_continuous");
 for (int route = 0; route < (continuous ? 1 : 8); ++route) {
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
  good = queued == 4 && good; wait(500);
  int32 actualMode = 0; _runner.getValue(1,0,actualMode);
  debug("P510 startup: %u queued, mode %d, event %d, playing %d",queued,actualMode,_plotEvent,int(_moviePlaying));
  good = actualMode == mode && _plotEvent == 19+mode && _moviePlaying && _movieX == 261 && _movieY == 33 && good;
  good = _scene.sprites[1].renderX == plotStart(mode).x && _scene.sprites[1].renderY == plotStart(mode).y && good;
  uint transitions = 0, frames = 0;
  auto press = [&](int id) {
   const Sprite &button = _scene.sprites[id-1]; const int x = button.renderX+10, y = button.renderY+10;
   if (_runner.clicksBlocked() || spriteAt(x,y) != id-1 || !_runner.canRun(button.click,true)) return false;
   clickAtTime(x,y,now); wait(300); return true;
  };
  // Routes0..3 win (both branch directions and repeated victory),4..5
  // fail with the middle button,6 exits,7 expires the original countdown.
  const int choice = route == 4 || route == 5 ? 3 : route == 1 ? 1 : 5;
  good = press(9+choice) && good;
  if (route == 6) { good = press(4) && good; wait(1000); }
  if (route == 7) {
   for (int i = 0; i < 450 && _place == 510; ++i) { now += 3000; runScriptsAt(now); }
  }
  const uint32 started = _system->getMillis();
  while (route < 6 && _place == 510 && _plotEvent && transitions < 40 && _system->getMillis()-started < 180000) {
   const int event = _plotEvent;
   if (continuous) {
    const uint before = _movieFramesDrawn;
    updateMovie(); if (_movie && _movieFramesDrawn > before) frames += _movieFramesDrawn-before;
    now = scriptClock(); runScriptsAt(now); animateSpritesAt(now); _system->delayMillis(5);
   } else {
    // Accelerated route checks use the real decoder; continuous playback
    // is independently checked without seeks by the dedicated option.
    good = _movie->seek(Audio::Timestamp(0,_plotTime+1,30)) && good;
    updateMovie();
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
 debug("Astronomica P510 interaction verification: %s",ok ? "PASS" : "FAIL");
 return ok;
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
 const uint32 seeds[] = {1,32,64,1};
 const int parts[5][11] = {{48,54,58,60,59,52,0},{46,47,53,58,57,56,45,44,50,0},
  {48,54,58,60,49,52,0},{48,54,58,45,43,51,0},{46,47,53,58,57,56,55,45,43,51,0}};
 for (uint route = 0; route < ARRAYSIZE(seeds); ++route) {
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
  auto value = [&](int id, int expected) { int32 v = -1; return _runner.getValue(1,id,v) && v == expected; };
  auto press = [&](uint id) {
   if (!inGroup() || id < 1 || id > _scene.sprites.size()) return false;
   const Sprite &s = _scene.sprites[id-1]; int hitX = -1, hitY = -1;
   for (int y = MAX(0,int(s.renderY)); y < 480 && hitX < 0; y += 4)
    for (int x = MAX(0,int(s.renderX)); x < 640; x += 4)
     if (spriteAt(x,y) == int(id)-1) { hitX = x; hitY = y; break; }
   if (hitX < 0) { warning("Builder no exposed sprite %u",id); return false; }
   clickAtTime(hitX,hitY,now); return settle();
  };
  ok = _runner.enqueueStartup(_scene.scripts,now,true) == 7 && settle() && ok;
  for (int phase = 0; phase < 2 && inGroup(); ++phase) {
   if (phase) ok = _runner.enqueueStartup(_scene.scripts,now,true) == 7 && settle() && ok;
   ok = press(5) && press(6) && value(2,2) && ok;
   int32 scenario = 0, required = 0;
   if (!_runner.getValue(1,1,scenario) || scenario < 1 || scenario > 5 ||
       !_runner.getValue(1,3,required)) return false;
   seen |= 1U << scenario;
   ok = (phase ? scenario >= 4 : scenario <= 3) && press(9) && ok;
   // Try an undersized rocket, remove its cap, then complete the same build.
   ok = press(13) && value(2,2) && press(14) && value(5,0) && ok;
   for (int stage = 1; stage < required-1; ++stage) ok = press(11) && ok;
   ok = press(13) && value(2,3) && ok;
   for (uint part = 0; parts[scenario-1][part]; ++part) ok = press(parts[scenario-1][part]) && ok;
   for (int flag = 7; flag <= 12; ++flag) ok = value(flag,1) && ok;
   ok = press(7) && value(2,4) && press(8) && ok;
   ok = _place == (phase ? 510 : 536) && ok;
   debug("Astronomica builder route %u phase %d: %s (scenario %d, P%d)",route,phase,ok ? "PASS" : "FAIL",scenario,_place);
  }
  int32 solved = 0;
  ok = _place == 510 && _runner.getValue(0,31,solved) && solved == 1 &&
   _puzzlesCompleted == completed+uint(route != 3) && ok;
 }
 ok = seen == 0x3e && ok;
 debug("Astronomica P515/P536 interaction verification: %s (five designs, original clicks, wrong size/recovery, two phases, repeated success)",ok ? "PASS" : "FAIL");
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
  bool rocketOK = true;
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
   rocketOK = flight.sprites[9].selectedFrame == 9 && flight.sprites[25].selectedFrame == 2 &&
    flight.sprites[26].selectedFrame == 5 && rocketOK;
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



