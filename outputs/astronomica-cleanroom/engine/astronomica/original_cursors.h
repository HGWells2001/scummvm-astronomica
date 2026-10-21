// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_ORIGINAL_CURSORS_H
#define ASTRONOMICA_ORIGINAL_CURSORS_H

#include "common/array.h"
#include "common/path.h"

namespace Graphics {
class Cursor;
struct WinCursorGroup;
}

namespace Astronomica {

// The bitmaps stay in the player's original Windows executable. No original
// cursor image is distributed or rebuilt into the ScummVM executable.
class OriginalCursors {
 struct Entry {
  uint32 id;
  const Graphics::Cursor *cursor;
  Entry(uint32 resourceID, const Graphics::Cursor *graphicsCursor) : id(resourceID), cursor(graphicsCursor) {}
 };
 Common::Array<Entry> _entries;
 Common::Array<Graphics::WinCursorGroup *> _groups;
 Common::Array<Graphics::Cursor *> _standalone;
 Graphics::Cursor *_windowsArrow = nullptr;
 int32 _currentID = -1;
 bool _loaded = false;
 bool add(uint32 id, const Graphics::Cursor *cursor);
public:
 ~OriginalCursors();
 uint load(const Common::Path &gameRoot);
 void clear();
 void reset() { _currentID = -1; }
 bool contains(uint32 id) const;
 void select(int32 id);
 uint count() const { return _entries.size(); }
 bool loaded() const { return _loaded; }
};

} // namespace Astronomica
#endif
