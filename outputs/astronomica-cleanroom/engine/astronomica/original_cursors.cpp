// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/original_cursors.h"

#include "common/file.h"
#include "common/fs.h"
#include "common/str.h"
#include "common/textconsole.h"
#include "graphics/cursor.h"
#include "graphics/cursorman.h"

namespace Astronomica {

namespace {

enum { kCursorSize = 16, kCursorPixels = kCursorSize * kCursorSize };

// The original GAMEDEF declares five cursors in this exact order.
// Its fourth argument is the image count (1), followed by the hotspot.
struct CursorDefinition {
 const char *name;
 uint32 id;
 uint16 hotspotX, hotspotY;
};
static const CursorDefinition kDefinitions[] = {
 {"HAND",  1,  8,  2},
 {"LEFT",  2,  1,  8},
 {"UP",    3,  8,  2},
 {"RIGHT", 4, 15,  8},
 {"DOWN",  5,  8, 15},
 {"ARROW", 0,  0,  0}
};

// Image::BitmapDecoder deliberately does not support 1-bit BMPs.
// Decode only the small, uncompressed 16x16 Windows BMP format found in
// PLACES/GAMEPLAC. Reject malformed or truncated files.
bool readMonochromeBMP(const Common::Path &path, byte *pixels) {
 Common::File file;
 if (!file.open(Common::FSNode(path)) || file.size() < 126)
  return false;
 if (file.readByte() != 'B' || file.readByte() != 'M')
  return false;
 const uint32 fileSize = file.readUint32LE();
 file.readUint16LE(); file.readUint16LE(); // Reserved
 const uint32 pixelOffset = file.readUint32LE();
 const uint32 headerSize = file.readUint32LE();
 const int32 width = file.readSint32LE();
 const int32 height = file.readSint32LE();
 const uint16 planes = file.readUint16LE();
 const uint16 bits = file.readUint16LE();
 const uint32 compression = file.readUint32LE();
 if (file.err() || headerSize != 40 || width != kCursorSize ||
     height != kCursorSize || planes != 1 || bits != 1 ||
     compression != 0 || fileSize > uint32(file.size()) ||
     pixelOffset < 62 || uint64(pixelOffset) + 64 > uint64(file.size()))
  return false;
 if (!file.seek(pixelOffset))
  return false;
 // BMP rows are bottom-up, 16 pixels packed MSB-first and padded to 4 bytes.
 for (int bottomRow = 0; bottomRow < kCursorSize; ++bottomRow) {
  byte row[4];
  if (file.read(row, sizeof(row)) != sizeof(row))
   return false;
  const int y = kCursorSize - bottomRow - 1;
  for (int x = 0; x < kCursorSize; ++x)
   pixels[y * kCursorSize + x] = (row[x / 8] >> (7 - (x % 8))) & 1;
 }
 return true;
}

class MonochromeCursor : public Graphics::Cursor {
 byte _surface[kCursorPixels];
 byte _palette[6];
 uint16 _hotspotX, _hotspotY;
public:
 MonochromeCursor(const byte *shape, const byte *mask, uint16 x, uint16 y)
  : _hotspotX(x), _hotspotY(y) {
  // ScummVM CLUT8: index 0 is transparent, 1 black, 2 white.
  _palette[0] = _palette[1] = _palette[2] = 0;
  _palette[3] = _palette[4] = _palette[5] = 255;
  for (int i = 0; i < kCursorPixels; ++i)
   _surface[i] = mask[i] ? 0 : (shape[i] ? 2 : 1);
 }
 uint16 getWidth() const override { return kCursorSize; }
 uint16 getHeight() const override { return kCursorSize; }
 uint16 getHotspotX() const override { return _hotspotX; }
 uint16 getHotspotY() const override { return _hotspotY; }
 byte getKeyColor() const override { return 0; }
 const byte *getSurface() const override { return _surface; }
 const byte *getPalette() const override { return _palette; }
 byte getPaletteStartIndex() const override { return 1; }
 uint16 getPaletteCount() const override { return 2; }
};

Graphics::Cursor *loadPair(const Common::Path &gameRoot, const CursorDefinition &def) {
 byte shape[kCursorPixels], mask[kCursorPixels];
 const Common::Path shapePath = gameRoot.join(Common::Path(
  Common::String::format("PLACES/GAMEPLAC/%s_S", def.name)));
 const Common::Path maskPath = gameRoot.join(Common::Path(
  Common::String::format("PLACES/GAMEPLAC/%s_M", def.name)));
 if (!readMonochromeBMP(shapePath, shape) || !readMonochromeBMP(maskPath, mask))
  return nullptr;
 return new MonochromeCursor(shape, mask, def.hotspotX, def.hotspotY);
}

} // namespace

OriginalCursors::~OriginalCursors() { clear(); }

void OriginalCursors::clear() {
 for (uint i = 0; i < _owned.size(); ++i)
  delete _owned[i];
 _owned.clear();
 _entries.clear();
 _defaultArrow = nullptr;
 _currentID = -1;
 _loaded = false;
}

bool OriginalCursors::contains(uint32 id) const {
 for (uint i = 0; i < _entries.size(); ++i)
  if (_entries[i].id == id) return true;
 return false;
}

uint OriginalCursors::load(const Common::Path &gameRoot) {
 clear();
 for (uint i = 0; i < sizeof(kDefinitions) / sizeof(kDefinitions[0]); ++i) {
  const CursorDefinition &def = kDefinitions[i];
  Graphics::Cursor *cursor = loadPair(gameRoot, def);
  if (!cursor) {
   debug("Astronomica original cursor %s: missing or invalid GAMEPLAC bitmap pair", def.name);
   continue;
  }
  _owned.push_back(cursor);
  if (def.id == 0)
   _defaultArrow = cursor;
  else
   _entries.push_back(Entry(def.id, cursor));
 }
 _loaded = _defaultArrow || !_entries.empty();
 debug("Astronomica original GAMEPLAC cursors: %u of 5 interaction cursors%s",
       uint(_entries.size()), _defaultArrow ? ", original arrow" : ", ScummVM arrow fallback");
 return _entries.size();
}

void OriginalCursors::select(int32 id) {
 if (!_loaded || id == _currentID) return;
 const Graphics::Cursor *cursor = nullptr;
 if (id > 0) {
  for (uint i = 0; i < _entries.size(); ++i) {
   if (_entries[i].id == uint32(id)) {
    cursor = _entries[i].cursor;
    break;
   }
  }
 }
 if (!cursor) cursor = _defaultArrow;
 if (cursor) CursorMan.replaceCursor(cursor);
 else CursorMan.setDefaultArrowCursor();
 _currentID = id;
}

} // namespace Astronomica
