// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_ORIGINAL_CURSORS_H
#define ASTRONOMICA_ORIGINAL_CURSORS_H

#include "common/array.h"
#include "common/path.h"

namespace Graphics { class Cursor; }

namespace Astronomica {

// Cursors are decoded from the player's own PLACES/GAMEPLAC/*_S and *_M
// monochrome BMPs. The engine never distributes the copyrighted bitmaps.
class OriginalCursors {
 struct Entry {
  uint32 id;
  const Graphics::Cursor *cursor;
  Entry(uint32 resourceID, const Graphics::Cursor *graphicsCursor)
   : id(resourceID), cursor(graphicsCursor) {}
 };
 Common::Array<Entry> _entries;
 Common::Array<Graphics::Cursor *> _owned;
 const Graphics::Cursor *_defaultArrow = nullptr;
 int32 _currentID = -1;
 bool _loaded = false;
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
