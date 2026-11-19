// SPDX-License-Identifier: GPL-3.0-or-later
// Original text _read_globals 9:4275. See probe_menu_services.py.
#ifndef ASTRONOMICA_LEGACY_SAVE_H
#define ASTRONOMICA_LEGACY_SAVE_H
#include "common/stream.h"
#include "common/array.h"
#include "common/file.h"
#include "common/fs.h"
namespace Astronomica {
struct LegacySaveState {
 uint32 place = 0, completed = 0;
 int32 globals[100] = {};
 bool hasUnknownClock() const { return globals[8] != 0 && (globals[60] == 1 || globals[60] == 2); }
};
inline bool legacyWhitespace(byte c) { return c == ' ' || (c >= 9 && c <= 13); }
inline bool readLegacySave(Common::SeekableReadStream &stream, LegacySaveState &state) {
 const int64 remaining = stream.size()-stream.pos();
 if (remaining <= 0 || remaining > 8192) return false;
 Common::Array<byte> bytes; bytes.resize(uint(remaining));
 if (stream.read(&bytes[0],bytes.size()) != bytes.size() || stream.err()) return false;
 uint cursor = 0; uint32 words[102];
 for (uint32 &word : words) {
  while (cursor < bytes.size() && legacyWhitespace(bytes[cursor])) ++cursor;
  bool negative = false;
  if (cursor < bytes.size() && (bytes[cursor] == '-' || bytes[cursor] == '+')) negative = bytes[cursor++] == '-';
  const uint first = cursor; uint32 value = 0, limit = negative ? 2147483648U : 2147483647U;
  while (cursor < bytes.size() && bytes[cursor] >= '0' && bytes[cursor] <= '9') {
   const uint digit = bytes[cursor++]-'0';
   if (value > (limit-digit)/10) return false;
   value = value*10+digit;
  }
  if (cursor == first || (cursor < bytes.size() && !legacyWhitespace(bytes[cursor]))) return false;
  word = negative ? 0U-value : value;
 }
 while (cursor < bytes.size() && legacyWhitespace(bytes[cursor])) ++cursor;
 if (cursor != bytes.size()) return false;
 LegacySaveState candidate; candidate.place = words[0]; candidate.completed = words[1];
 for (uint i = 0; i < 100; ++i) candidate.globals[i] = int32(words[i+2]);
 state = candidate; return true;
}
enum LegacyFileResult { kLegacyMissing, kLegacyInvalid, kLegacyLoaded };
inline LegacyFileResult readLegacyDirectory(const Common::FSNode &directory, LegacySaveState &state) {
 for (const char *name : {"gamestat","GAMESTAT"}) {
  const Common::FSNode node = directory.getChild(name);
  if (!node.exists()) continue;
  Common::File file;
  return file.open(node) && readLegacySave(file,state) ? kLegacyLoaded : kLegacyInvalid;
 }
 return kLegacyMissing;
}
}
#endif
