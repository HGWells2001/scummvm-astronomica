// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_RESOURCE_H
#define ASTRONOMICA_RESOURCE_H
#include "common/array.h"
#include "common/str.h"
#include "common/stream.h"
namespace Astronomica {
struct BitmapRef { uint32 offset = 0, size = 0; };
struct Command { uint32 offset = 0; int32 opcode = 0, delay = 0; Common::Array<int32> args; Common::String text; };
typedef Common::Array<Command> Script;
struct Frame { BitmapRef image, mask; };
struct Sprite {
 int32 clone = -1, layer = 0, visible = 0, x = 0, y = 0, clickType = 0, cursor = 0;
 bool clickEnabled = false, dragEnabled = false, autoFrame = false, autoMove = false;
 int16 renderX = 0, renderY = 0;
 uint32 frameSince = 0;
 uint32 moveSince = 0;
 bool standardMotion = false;
 int16 moveDX = 0, moveDY = 0;
 int planetMotion = 0; // 0 ordinary, 1 follow launcher, 2 released planet.
 int32 planetPeriod = -1;
 bool orbitMotion = false;
 int32 orbitSideX = 0, orbitSideY = 0; // Original GameSprite bd/c1 quadrant flags.
 int32 frameFirst = 0, frameLast = -1; // -1 upper bound uses all loaded frames.
 int32 selectedFrame = -1; // Multiframe preview waits for an explicit command.
 Common::Array<Frame> frames;
 Script click, drag, mouseIn, mouseOut;
 int32 rect[4] = {}, frameData[3] = {}, moveData[5] = {};
};
struct MouseRect { int32 rect[4] = {}; Script click, mouseIn, mouseOut; };
struct Condition { int32 raw[6] = {}; };
struct Scene {
 int32 mode = 0, nav[3] = {}, layers = 0;
 bool introSound = false;
 int32 introSoundId = -1;
 BitmapRef background, control;
 Common::Array<Sprite> sprites;
 Common::Array<Script> scripts;
 Common::Array<MouseRect> mouseRects;
 Common::Array<Condition> conditions;
 Common::Array<Common::String> movies;
 uint32 consumed = 0, trailing = 0, bitmapCount = 0, commandCount = 0;
};
// Parses serialization only. Numeric fields retain original on-disk values.
class ResourceReader {
 Common::SeekableReadStream &_s;
 bool _ok;
 uint32 _bitmaps, _commands;
 int32 number();
 uint32 count();
 bool flag();
 Common::String text();
 BitmapRef bitmap();
 BitmapRef image();
 Script script();
 Script optionalScript();
 Sprite sprite();
 void numbers(int32 *v, uint n);
public:
 explicit ResourceReader(Common::SeekableReadStream &s) : _s(s), _ok(true), _bitmaps(0), _commands(0) {}
 bool read(Scene &scene);
};
}
#endif
