// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/original_cursors.h"

#include "common/config-manager.h"
#include "common/formats/winexe.h"
#include "common/ptr.h"
#include "common/stream.h"
#include "common/textconsole.h"
#include "common/util.h"
#include "graphics/cursorman.h"
#include "graphics/wincursor.h"

namespace Astronomica {

OriginalCursors::~OriginalCursors() { clear(); }

void OriginalCursors::clear() {
 for (uint i = 0; i < _groups.size(); ++i) delete _groups[i];
 for (uint i = 0; i < _standalone.size(); ++i) delete _standalone[i];
 delete _windowsArrow;
 _windowsArrow = nullptr;
 _groups.clear(); _standalone.clear(); _entries.clear();
 _currentID = -1; _loaded = false;
}

bool OriginalCursors::contains(uint32 id) const {
 for (uint i = 0; i < _entries.size(); ++i)
  if (_entries[i].id == id) return true;
 return false;
}

bool OriginalCursors::add(uint32 id, const Graphics::Cursor *cursor) {
 if (!cursor || id == 0 || id == 0xffffffffU || contains(id)) return false;
 if (!cursor->getSurface() || !cursor->getWidth() || !cursor->getHeight() ||
     cursor->getWidth() > 128 || cursor->getHeight() > 128 ||
     cursor->getHotspotX() >= cursor->getWidth() || cursor->getHotspotY() >= cursor->getHeight())
  return false;
 _entries.push_back(Entry(id,cursor));
 return true;
}

uint OriginalCursors::load(const Common::Path &gameRoot) {
 clear();
 // Both published English CD layouts are supported. No Windows platform
 // dependencies: ScummVM's NE/PE resource reader decodes the game's EXE.
 static const char *const candidates[] = {
  "SETUP/ASTRO.EXE", "ASTRO.EXE"
 };
 Common::WinResources *exe = nullptr;
 for (uint i = 0; i < ARRAYSIZE(candidates); ++i) {
  exe = Common::WinResources::createFromEXE(gameRoot.join(Common::Path(candidates[i])));
  if (exe) break;
 }
 if (!exe) {
  debug("Astronomica original cursor resources: no supported original EXE");
  return 0;
 }
 const Common::Array<Common::WinResourceID> groups = exe->getIDList(Common::kWinGroupCursor);
 for (uint i = 0; i < groups.size(); ++i) {
  Graphics::WinCursorGroup *group = Graphics::WinCursorGroup::createCursorGroup(exe,groups[i]);
  if (!group || group->cursors.empty()) { delete group; continue; }
  _groups.push_back(group);
  const uint32 groupID = groups[i].getID();
  if (groupID != 0xffffffffU) add(groupID,group->cursors[0].cursor);
  for (uint j = 0; j < group->cursors.size(); ++j) {
   const uint32 resourceID = group->cursors[j].id.getID();
   if (resourceID != 0xffffffffU) add(resourceID,group->cursors[j].cursor);
  }
 }
 // Some Win16 games use RT_CURSOR directly, without RT_GROUP_CURSOR.
 // Read only entries not already owned by a Windows cursor group.
 const Common::Array<Common::WinResourceID> singles = exe->getIDList(Common::kWinCursor);
 for (uint i = 0; i < singles.size(); ++i) {
  const uint32 id = singles[i].getID();
  if (id == 0xffffffffU || contains(id)) continue;
  Common::SeekableReadStream *stream = exe->getResource(Common::kWinCursor,singles[i]);
  if (!stream) continue;
  if (stream->size() > 4 && stream->size() <= 65536) {
   const uint16 hotspotX = stream->readUint16LE();
   const uint16 hotspotY = stream->readUint16LE();
   Graphics::Cursor *cursor = Graphics::loadWindowsCursorFromDIB(*stream,hotspotX,hotspotY);
   if (cursor) {
    if (add(id,cursor)) _standalone.push_back(cursor);
    else delete cursor;
   }
  }
  delete stream;
 }
 delete exe;
 _loaded = !_entries.empty();
 if (_loaded) _windowsArrow = Graphics::makeDefaultWinCursor();
 debug("Astronomica original cursor resources: %u images from original executable",uint(_entries.size()));
 return _entries.size();
}

void OriginalCursors::select(int32 id) {
 if (!_loaded || id == _currentID) return;
 const Graphics::Cursor *cursor = nullptr;
 if (id > 0) for (uint i = 0; i < _entries.size(); ++i) {
  if (_entries[i].id == uint32(id)) { cursor = _entries[i].cursor; break; }
 }
 // The old game uses Windows' standard arrow outside special hot spots.
 if (!cursor) cursor = _windowsArrow;
 if (cursor) CursorMan.replaceCursor(cursor);
 else CursorMan.setDefaultArrowCursor();
 _currentID = id;
}

} // namespace Astronomica
