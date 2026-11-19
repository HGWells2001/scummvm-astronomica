// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/help.h"
#include "common/endian.h"
#include "common/debug.h"
#include "common/hashmap.h"
#include "common/hash-str.h"
#include "common/str-enc.h"
#include "common/system.h"
#include "common/file.h"
#include "graphics/surface.h"
#include "graphics/managed_surface.h"
#include "graphics/macgui/mactext.h"
#include "gui/gui-manager.h"
#include "gui/ThemeEval.h"
#include "gui/animation/FluidScroll.h"
#include "image/bmp.h"
#include "gui/dialog.h"
#include "gui/widget.h"
#include "gui/widgets/list.h"
#include "gui/widgets/edittext.h"
#include "gui/widgets/richtext.h"
#include "gui/widgets/scrollbar.h"

namespace Astronomica {
namespace {
typedef Common::Array<byte> Bytes;
struct Reader {
 const Bytes &data; uint pos = 0; bool ok = true;
 explicit Reader(const Bytes &bytes) : data(bytes) {}
 bool seek(uint offset) { if (offset > data.size()) return ok = false; pos = offset; return ok; }
 uint32 get(uint n) {
  if (!ok || n > 4 || pos > data.size() || n > data.size()-pos) { ok = false; return 0; }
  uint32 result = 0; for (uint i = 0; i < n; ++i) result |= uint32(data[pos++])<<(8*i); return result;
 }
 Common::String string() {
  Common::String s; while (ok && pos < data.size()) { byte c = get(1); if (!c) return s; s += char(c); }
  ok = false; return s;
 }
};
bool portion(const Bytes &data, uint32 offset, uint32 size, Bytes &out) {
 if (offset > data.size() || size > data.size()-offset) return false;
 out.resize(size); if (size) memcpy(&out[0],&data[offset],size); return true;
}
bool internalStream(const Bytes &file, uint32 offset, Bytes &out) {
 if (offset > file.size() || file.size()-offset < 9) return false;
 Reader r(file); r.seek(offset); const uint32 allocated = r.get(4), used = r.get(4); r.get(1);
 if (allocated < 9 || used > allocated-9 || allocated > file.size()-offset) return false;
 return portion(file,offset+9,used,out);
}
bool decompress(const Bytes &input, Bytes &out) {
 out.clear(); Reader r(input);
 while (r.pos < input.size()) {
  const uint flags = r.get(1);
  for (uint bit = 0; bit < 8 && r.pos < input.size(); ++bit) {
   if (flags & (1U<<bit)) {
    const uint word = r.get(2), distance = (word&4095)+1, count = (word>>12)+3;
    if (!r.ok || distance > out.size() || out.size()+count > 65536) return false;
    for (uint i = 0; i < count; ++i) out.push_back(out[out.size()-distance]);
   } else { if (out.size() == 65536) return false; out.push_back(r.get(1)); }
  }
 }
 return r.ok;
}
// The original image groups each contain one type-6 DIB at offset 8.
// Packed fields use a low-bit width marker, not a continuation-byte encoding.
uint32 packed(Reader &r, bool small = false) {
 const uint start = r.pos, size = small ? 1 : 2;
 uint32 value = r.get(size);
 if (value & 1) { r.seek(start); value = r.get(size*2); }
 return value >> 1;
}
bool decodeImage(const Bytes &data, HelpImage &image) {
 Reader r(data);
 if (r.get(2) != 0x506c || r.get(2) != 1 || r.get(4) != 8 || r.get(1) != 6) return false;
 const uint compression = r.get(1);
 if (compression != 0 && compression != 2) return false;
 const uint dpiX = packed(r), dpiY = packed(r), planes = packed(r,true), bits = packed(r,true);
 const uint width = packed(r), height = packed(r), colors = packed(r), important = packed(r);
 const uint size = packed(r), hotspots = packed(r), offset = r.get(4), hotspotOffset = r.get(4);
 if (!r.ok || dpiX != 72 || dpiY != 72 || planes != 1 || bits != 8 ||
     !width || width > 640 || !height || height > 480 || colors != 256 || important != 256 ||
     hotspots || hotspotOffset || uint64(offset)+8 != uint64(r.pos)+1024 ||
     uint64(offset)+8+size != data.size()) return false;
 Bytes stored;
 if (!portion(data,r.pos,1024,image.palette) || !portion(data,offset+8,size,stored)) return false;
 if (compression == 2) { if (!decompress(stored,image.pixels)) return false; }
 else image.pixels = stored;
 image.width = width; image.height = height; image.pitch = (width+3)&~3U;
 return image.pixels.size() == image.pitch*height;
}
struct Entry { Common::String name; uint32 value = 0, count = 0; };
bool tree(const Bytes &data, const char *format, Common::Array<Entry> &entries) {
 if (data.size() < 38) return false;
 Reader r(data); if (r.get(2) != 0x293b) return false;
 r.get(2); const uint size = r.get(2); const Common::String actual = r.string();
 r.seek(26); const uint root = r.get(2); r.get(2); const uint pages = r.get(2); r.get(2); const uint total = r.get(4);
 if (!r.ok || actual != format || size < 8 || !pages || root >= pages || total > 10000 ||
     uint64(size)*pages+38 != data.size()) return false;
 uint page = 0, previous = 65535; Common::Array<bool> seen; seen.resize(pages);
 while (page != 65535) {
  if (page >= pages || seen[page]) return false; seen[page] = true;
  const uint start = 38+page*size, end = start+size;
  r.seek(start); const uint unused = r.get(2), count = r.get(2), prev = r.get(2), next = r.get(2);
  if (prev != previous || entries.size()+count > total) return false;
  for (uint i = 0; i < count; ++i) {
   Entry entry;
   if (actual == "Lz") entry.value = r.get(4);
   entry.name = r.string();
   if (actual == "i24") entry.count = r.get(2);
   if (actual != "Lz") entry.value = r.get(4);
   if (!r.ok || r.pos > end) return false; entries.push_back(entry);
  }
  if (r.pos+unused != end) return false; previous = page; page = next;
 }
 return entries.size() == total;
}
bool readTopic(const Common::Array<Bytes> &blocks, uint32 address, uint size, Bytes &out) {
 uint block = address>>14, offset = address&16383;
 if (offset < 12 || size > 65536) return false; offset -= 12; out.clear();
 while (size) {
  if (block >= blocks.size() || offset >= blocks[block].size()) return false;
  const uint count = MIN(size,blocks[block].size()-offset);
  for (uint i = 0; i < count; ++i) out.push_back(blocks[block][offset+i]);
  size -= count; ++block; offset = 0;
 }
 return true;
}
bool expand(const Bytes &raw, uint start, const Common::Array<Common::String> &phrases, uint expected, Common::String &out) {
 if (start > raw.size() || expected > 65536) return false;
 Bytes result;
 for (uint i = start; i < raw.size(); ++i) {
  const byte c = raw[i];
  if (c >= 1 && c <= 15) {
   if (++i == raw.size()) return false;
   const uint token = (c-1)*256+raw[i], index = token>>1;
   if (index >= phrases.size()) return false;
   for (uint p = 0; p < phrases[index].size(); ++p) result.push_back(byte(phrases[index][p]));
   if (token&1) result.push_back(32);
  } else result.push_back(c);
  if (result.size() > expected) return false;
 }
 if (result.size() != expected) return false;
 if (!result.empty()) out = Common::String((const char *)&result[0],result.size());
 return true;
}
// A reading view preserves text and separates paragraph runs. Rich font,
// inline-link and bitmap rendering are separate from the verified text decoder.
Common::String readingText(const Common::String &raw) {
 Common::String text;
 for (uint i = 0; i < raw.size();) {
  if (raw[i]) { text += raw[i++]; continue; }
  uint count = 0; while (i < raw.size() && !raw[i]) { ++i; ++count; }
  if (count > 1 && !text.empty()) text += "\n\n";
 }
 return text;
}
Common::String escapeMarkdown(const Common::String &text) {
 Common::String out;
 for (uint i = 0; i < text.size(); ++i) {
  if (strchr("\\`*_{}[]<>()#+-!|",text[i])) out += '\\'; out += text[i];
 }
 return out;
}
// Original formatting pairs every NUL in the expanded body with exactly one
// command. The same paragraph grammar is used inside table cells (kind 35).
struct HelpFont { uint flags, halfPoints; bool exponent = false; };
struct FormatState { uint font = 3, tableColumns = 0; bool titleSeen = false; };
uint32 signedPacked(Reader &r, bool small = false) {
 const uint start = r.pos, size = small ? 1 : 2;
 uint32 value = r.get(size); uint bytes = size;
 if (value & 1) { r.seek(start); bytes *= 2; value = r.get(bytes); }
 return (value>>1) - (1U<<(8*bytes-2));
}
void formatWord(uint32 &hash, uint32 word) {
 for (uint i = 0; i < 4; ++i) hash = (hash ^ ((word>>(8*i))&255))*16777619U;
}
Common::String styledText(const Common::String &raw, uint flags) {
 // Keep surrounding spaces outside emphasis delimiters so Markdown preserves
 // a style change in the middle of a sentence.
 uint begin = 0, end = raw.size();
 while (begin < end && raw[begin] == ' ') ++begin;
 while (end > begin && raw[end-1] == ' ') --end;
 const Common::String marker = (flags&3) == 3 ? "**_" : (flags&1) ? "**" : (flags&2) ? "*" : "";
 const Common::String closing = (flags&3) == 3 ? "_**" : marker;
 return raw.substr(0,begin)+(begin == end ? "" : marker+escapeMarkdown(raw.substr(begin,end-begin))+closing)+raw.substr(end);
}
bool formatParagraph(Reader &r, const Common::String &body, uint &cursor, const Common::Array<HelpFont> &fonts,
                     HelpArticle &article, FormatState &state, Common::String &out, bool cell, uint32 &hash, uint &commands) {
 const uint textOffset = signedPacked(r), style = r.get(2), flags = r.get(2);
 if (!r.ok || textOffset != cursor || style || (flags&~0xa04U)) return false;
 formatWord(hash,textOffset); formatWord(hash,flags);
 const int indent = (flags&4) ? int(signedPacked(r,true)) : 0; formatWord(hash,uint32(indent));
 const uint tabs = (flags&0x200) ? signedPacked(r,true) : 0;
 if (tabs > 32) return false; formatWord(hash,tabs);
 for (uint i = 0; i < tabs; ++i) {
  const uint position = packed(r,true), alignment = (position&0x4000) ? r.get(1) : 0;
  formatWord(hash,position&0x3fff); formatWord(hash,alignment);
 }
 while (r.ok && r.pos < r.data.size()) {
  uint end = cursor; while (end < body.size() && body[end]) ++end;
  if (end == body.size() || state.font >= fonts.size()) return false;
  Common::String text = body.substr(cursor,end-cursor);
  const uint opcode = r.get(1); formatWord(hash,opcode); formatWord(hash,cursor); formatWord(hash,end-cursor);
  for (uint i = cursor; i < end; ++i) hash = (hash ^ byte(body[i]))*16777619U;
  cursor = end+1; ++commands;
  if (!text.empty() && !state.titleSeen) {
   state.titleSeen = true;
   if (text == article.title || (article.title.empty() && text == "Introduction")) text.clear();
  }
  if (fonts[state.font].exponent && !text.empty()) {
   // Arial Super is used for original exponents. Explicit power notation
   // retains their meaning with bitmap GUI fonts lacking raised digits.
   out += "^("+escapeMarkdown(text)+")"; ++article.exponentRuns;
  } else out += styledText(text,fonts[state.font].flags);
  switch (opcode) {
  case 0x80: state.font = r.get(2); if (state.font >= fonts.size()) return false; formatWord(hash,state.font); break;
  case 0x81: out += cell ? " " : "  \n"; break;
  case 0x82: out += cell ? " " : "\n\n"; break;
  case 0x83: out += "    "; break;
  case 0x86: {
   static const byte prefix[] = {0x22,0x08,0x80,2,0,0};
   for (byte b : prefix) if (r.get(1) != b) return false;
   const uint id = r.get(2); if (id >= 31) return false; formatWord(hash,id);
   // All original bitmap commands occur in paragraph records, never cells.
   if (cell) return false;
   article.imageAnchors.push_back({article.markdown.size()+out.size(),id});
   break;
  }
  case 0xff: return r.ok;
  default: return false;
  }
 }
 return false;
}
bool formatBody(const Bytes &raw, uint textOffset, uint kind, const Common::String &body,
                const Common::Array<HelpFont> &fonts, HelpArticle &article, FormatState &state,
                uint32 &hash, uint &commands) {
 Bytes bytes; if (!portion(raw,21,textOffset-21,bytes)) return false;
 Reader r(bytes); const uint length = signedPacked(r), characters = packed(r,true);
 if (!r.ok || length != bytes.size()-r.pos) return false;
 formatWord(hash,kind);
 uint cursor = 0, imageCount = 0;
 // The already verified bitmap associations count one additional character
 // in the original character-address space; text NULs still drive commands.
 for (uint i = 0; i+9 <= bytes.size(); ++i) {
  static const byte prefix[] = {0x86,0x22,0x08,0x80,2,0,0};
  if (!memcmp(&bytes[i],prefix,7)) { ++imageCount; i += 8; }
 }
 if (characters != body.size()+imageCount) return false;
 if (kind == 32) {
  formatWord(hash,0);
  if (state.tableColumns) { article.markdown += "\n"; state.tableColumns = 0; }
  Common::String paragraph;
  if (!formatParagraph(r,body,cursor,fonts,article,state,paragraph,false,hash,commands)) return false;
  article.markdown += paragraph+"\n\n";
 } else {
  const uint columns = r.get(1), type = r.get(1);
  if (type != 1 || !columns || columns > 8) return false; formatWord(hash,columns);
  for (uint i = 0; i < columns; ++i) { const uint width = r.get(2), gap = r.get(2); formatWord(hash,width); formatWord(hash,gap); }
  Common::Array<Common::String> cells; cells.resize(columns);
  for (;;) {
   const uint column = r.get(2); if (!r.ok) return false;
   if (column == 65535) break;
   if (column >= columns || r.get(1) != 1) return false;
   const uint size = signedPacked(r);
   if (size > bytes.size()-r.pos) return false;
   const uint stop = r.pos+size; formatWord(hash,column);
   if (!formatParagraph(r,body,cursor,fonts,article,state,cells[column],true,hash,commands) || r.pos != stop) return false;
  }
  formatWord(hash,65535);
  if (state.tableColumns != columns) {
   // Blank Markdown header supplies structure without inventing source labels.
   article.markdown += "\n|";
   for (uint i = 0; i < columns; ++i) article.markdown += " \xA0 |";
   article.markdown += "\n|";
   for (uint i = 0; i < columns; ++i) article.markdown += " --- |";
   article.markdown += "\n"; state.tableColumns = columns;
  }
  article.markdown += "|";
  for (const Common::String &cellText : cells) {
   Common::String visible = cellText; visible.trim();
   article.markdown += " "+(visible.empty() ? Common::String("\xA0") : cellText)+" |";
  }
  article.markdown += "\n";
 }
 return r.ok && r.pos == bytes.size() && cursor == body.size();
}
}
bool HelpBook::load(Common::SeekableReadStream &stream) {
 HelpBook candidate;
 if (!candidate.parse(stream)) return false;
 *this = candidate; return true;
}
bool HelpBook::parse(Common::SeekableReadStream &stream) {
 if (stream.size() < 16 || stream.size() > 16*1024*1024) return false;
 Bytes file; file.resize(uint(stream.size())); stream.seek(0);
 if (stream.read(&file[0],file.size()) != file.size()) return false;
 Reader header(file); if (header.get(4) != 0x35f3f) return false;
 const uint directory = header.get(4); header.get(4); if (header.get(4) != file.size()) return false;
 Bytes data; Common::Array<Entry> entries;
 if (!internalStream(file,directory,data) || !tree(data,"z4",entries)) return false;
 Common::HashMap<Common::String,uint32> locations;
 for (const Entry &e : entries) { if (locations.contains(e.name)) return false; locations[e.name] = e.value; }
 auto fetch = [&](const char *name, Bytes &result) {
  return locations.contains(name) && internalStream(file,locations[name],result);
 };
 for (uint i = 0; i < 31; ++i) {
  HelpImage image;
  if (!fetch(Common::String::format("|bm%u",i).c_str(),data) || !decodeImage(data,image)) return false;
  images.push_back(image);
 }
 if (!fetch("|SYSTEM",data) || data.size() < 12 || READ_LE_UINT16(&data[0]) != 0x36c || READ_LE_UINT16(&data[10]) != 4) return false;
 if (!fetch("|FONT",data) || data.size() < 8) return false;
 Reader fontReader(data); const uint names = fontReader.get(2), fontCount = fontReader.get(2);
 const uint nameOffset = fontReader.get(2), fontOffset = fontReader.get(2);
 if (names != 93 || fontCount != 16 || nameOffset != 8 || fontOffset != nameOffset+20*names || data.size() != fontOffset+11*fontCount) return false;
 Common::Array<HelpFont> fonts;
 for (uint i = 0; i < fontCount; ++i) {
  fontReader.seek(fontOffset+11*i); HelpFont font; font.flags = fontReader.get(1); font.halfPoints = fontReader.get(1);
  if (fontReader.get(1) != 3) return false;
  const uint nameIndex = fontReader.get(2); if (nameIndex >= names) return false;
  const uint begin = nameOffset+20*nameIndex; uint end = begin;
  while (end < begin+20 && data[end]) ++end;
  if (end == begin+20) return false;
  font.exponent = Common::String((const char *)&data[begin],end-begin) == "Arial Super";
  fonts.push_back(font);
 }
 if (!fetch("|Phrases",data) || data.size() < 8) return false;
 Reader phrasesReader(data); const uint count = phrasesReader.get(2), tag = phrasesReader.get(2), expanded = phrasesReader.get(4);
 if (!count || count > 4096 || tag != 256 || 8+2*(count+1) > data.size()) return false;
 Common::Array<uint> offsets; for (uint i = 0; i <= count; ++i) offsets.push_back(phrasesReader.get(2));
 if (offsets[0] != 2*(count+1) || offsets[count] < offsets[0] || offsets[count]-offsets[0] != expanded) return false;
 Bytes compressed, phraseBytes;
 if (!portion(data,phrasesReader.pos,data.size()-phrasesReader.pos,compressed) || !decompress(compressed,phraseBytes) || phraseBytes.size() != expanded) return false;
 Common::Array<Common::String> phrases;
 for (uint i = 0; i < count; ++i) {
  if (offsets[i+1] <= offsets[i] || offsets[i+1]-offsets[0] > phraseBytes.size()) return false;
  phrases.push_back(Common::String((const char *)&phraseBytes[offsets[i]-offsets[0]],offsets[i+1]-offsets[i]));
 }
 if (!fetch("|TTLBTREE",data)) return false;
 Common::Array<Entry> titles; if (!tree(data,"Lz",titles)) return false;
 if (!fetch("|TOPIC",data)) return false;
 Common::Array<Bytes> blocks;
 for (uint offset = 0; offset < data.size(); offset += 4096) {
  const uint size = MIN(4096U,data.size()-offset); Bytes decoded;
  if (size < 12 || !portion(data,offset+12,size-12,compressed) || !decompress(compressed,decoded) || decoded.empty()) return false;
  blocks.push_back(decoded);
 }
 struct Span { uint32 start, end; uint article; }; Common::Array<Span> spans;
 uint32 address = 12, previous = 0xffffffff, chars = 0, block = 0;
 FormatState formatState;
 uint titleIndex = 0; Common::HashMap<uint32,bool> seen; recordHash = 2166136261U;
 while (address != 0xffffffff) {
  if (seen.contains(address) || ++recordCount > 10000) return false; seen[address] = true;
  Bytes raw; if (!readTopic(blocks,address,21,raw)) return false;
  Reader r(raw); const uint size = r.get(4), outputSize = r.get(4), prev = r.get(4), next = r.get(4), textOffset = r.get(4), kind = r.get(1);
  if (prev != previous || textOffset < 21 || textOffset > size || (kind != 2 && kind != 32 && kind != 35) || !readTopic(blocks,address,size,raw)) return false;
  Common::String body; if (!expand(raw,textOffset,phrases,outputSize,body)) return false;
  recordHash = (recordHash ^ kind)*16777619U;
  for (uint i = 0; i < 4; ++i) recordHash = (recordHash ^ ((address>>(8*i))&255))*16777619U;
  for (uint i = 0; i < body.size(); ++i) recordHash = (recordHash ^ byte(body[i]))*16777619U;
  if ((address>>14) != block) { block = address>>14; chars = 0; }
  if (kind == 2) {
   if (titleIndex >= titles.size() || titles[titleIndex].name != body || titles[titleIndex].value != (block<<15)+chars) return false;
   formatState = FormatState(); HelpArticle article; article.title = body; articles.push_back(article); ++titleIndex;
  } else {
   if (articles.empty()) return false;
   uint imageCount = 0; static const byte imagePrefix[] = {0x86,0x22,0x08,0x80,2,0,0};
   for (uint i = 21; i+9 <= textOffset; ++i)
    if (!memcmp(&raw[i],imagePrefix,7)) { const uint id = READ_LE_UINT16(&raw[i+7]); if (id >= this->images.size()) return false; articles.back().images.push_back(id); ++imageCount; i += 8; }
   const uint32 start = (block<<15)+chars;
   spans.push_back({start,start+outputSize+imageCount,articles.size()-1}); chars += outputSize+imageCount;
   articles.back().text += readingText(body)+"\n\n";
   if (!formatBody(raw,textOffset,kind,body,fonts,articles.back(),formatState,formatHash,formatCommands)) return false;
   ++formatRecords;
  }
  previous = address; address = next;
 }
 if (titleIndex != titles.size() || articles.empty()) return false;
 // The article title is already rendered as a heading. Keep the source title
 // once when the first body paragraph repeats it verbatim.
 for (HelpArticle &article : articles) {
  const Common::String prefix = article.title+"\n\n";
  if (!article.title.empty() && article.text.hasPrefix(prefix)) article.text.erase(0,prefix.size());
 }
 if (articles[0].title.empty()) articles[0].title = "Introduction";
 if (!fetch("|KWBTREE",data)) return false;
 Common::Array<Entry> keywords; if (!tree(data,"i24",keywords)) return false;
 if (!fetch("|KWDATA",data)) return false;
 for (const Entry &e : keywords) {
  if (e.value > data.size() || e.count > (data.size()-e.value)/4) return false;
  Keyword keyword; keyword.name = e.name; keyword.name.toLowercase();
  for (uint i = 0; i < e.count; ++i) {
   const uint32 reference = READ_LE_UINT32(&data[e.value+4*i]); int match = -1;
   for (const Span &span : spans) if (reference >= span.start && reference < span.end) { if (match >= 0) return false; match = span.article; }
   if (match < 0) return false; keyword.articles.push_back(uint(match)); ++referenceCount;
  }
  _keywords.push_back(keyword);
 }
 keywordCount = _keywords.size(); return true;
}
Common::Array<uint> HelpBook::search(const Common::String &input) const {
 Common::String query = input; query.toLowercase();
 Common::Array<bool> matches; matches.resize(articles.size());
 for (uint i = 0; i < articles.size(); ++i) {
  Common::String title = articles[i].title; title.toLowercase();
  matches[i] = !title.empty() && (query.empty() || title.contains(query));
 }
 if (!query.empty()) for (const Keyword &word : _keywords)
  if (word.name.contains(query)) for (uint article : word.articles) matches[article] = true;
 Common::Array<uint> result;
 for (uint i = 0; i < matches.size(); ++i) if (matches[i] && !articles[i].title.empty()) result.push_back(i);
 return result;
}

namespace {
// Verification captures the real GUI overlay after several rendered frames.
// Normal dialogs have no capture path and never close themselves.
class BookDialog : public GUI::Dialog {
 Common::Path _capture; uint _ticks = 0; bool _closeAfterFrames = false;
public:
 bool captured = false;
 BookDialog() : GUI::Dialog(8,8,g_system->getOverlayWidth()-16,g_system->getOverlayHeight()-16) { _backgroundType = GUI::ThemeEngine::kDialogBackgroundPlain; }
 void captureThenClose(const Common::Path &path) { _capture = path; }
 void closeAfterFramesForVerification() { _closeAfterFrames = true; }
 void handleTickle() override {
  GUI::Dialog::handleTickle();
  if (_capture.empty() && !_closeAfterFrames) return;
  if (++_ticks < (_capture.empty() ? 2U : 5U)) return;
  if (_capture.empty()) { close(); return; }
  Graphics::Surface surface; surface.create(g_system->getOverlayWidth(),g_system->getOverlayHeight(),g_system->getOverlayFormat());
  g_system->grabOverlay(surface); Common::DumpFile output;
  if (output.open(_capture)) captured = Image::writeBMP(output,surface);
  surface.free(); close();
 }
};
// The separate image view remains available in addition to inline pictures.
class HelpImageDialog : public BookDialog {
public:
 HelpImageDialog(const HelpBook &book, const HelpArticle &article, uint index) {
  const HelpImage &image = book.images[article.images[index]];
  const Common::String caption = Common::String::format("%s (%u/%u)",article.title.c_str(),index+1,article.images.size());
  new GUI::StaticTextWidget(this,10,8,_w-20,20,Common::U32String(caption,Common::kWindows1252),Graphics::kTextAlignCenter);
  Graphics::Surface surface; surface.create(image.width,image.height,g_system->getOverlayFormat());
  for (uint y = 0; y < image.height; ++y) for (uint x = 0; x < image.width; ++x) {
   const uint color = image.pixels[(image.height-1-y)*image.pitch+x];
   surface.setPixel(x,y,surface.format.RGBToColor(image.palette[4*color+2],image.palette[4*color+1],image.palette[4*color]));
  }
  // Preserve the aspect ratio and never enlarge the source. Small overlays
  // still display the whole picture above the navigation controls.
  const uint fitWidth = MIN<uint>(image.width,MAX(1,_w-20));
  const uint fitHeight = MIN<uint>(image.height,MAX(1,_h-76));
  uint width = fitWidth, height = MAX(1U,image.height*width/image.width);
  if (height > fitHeight) { height = fitHeight; width = MAX(1U,image.width*height/image.height); }
  Graphics::Surface *scaled = surface.scale(width,height,false);
  GUI::GraphicsWidget *picture = new GUI::GraphicsWidget(this,(_w-width)/2,32+(_h-76-height)/2,width,height);
  picture->setGfx(scaled); scaled->free(); delete scaled; surface.free();
  const int buttonWidth = (_w-40)/3;
  GUI::ButtonWidget *previous = new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);
  GUI::ButtonWidget *next = new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);
  new GUI::ButtonWidget(this,30+buttonWidth*2,_h-32,buttonWidth,22,Common::U32String("Back to article"),Common::U32String(),3);
  previous->setEnabled(index > 0); next->setEnabled(index+1 < article.images.size());
 }
 void handleCommand(GUI::CommandSender *sender, uint32 cmd, uint32 data) override {
  if (cmd >= 1 && cmd <= 3) { setResult(cmd); close(); }
  else GUI::Dialog::handleCommand(sender,cmd,data);
 }
};
class HelpTextWidget : public GUI::RichTextWidget {
 const HelpBook &_book;
 const HelpArticle &_article;
 bool _composed = false, _held = false;
 int _dragY = 0;
 Common::Array<Common::Rect> _imageRects;
 static Common::String firstText(const HelpArticle &article) {
  const uint end = article.imageAnchors.empty() ? article.markdown.size() : article.imageAnchors[0].offset;
  return "## "+escapeMarkdown(article.title)+"\n\n"+article.markdown.substr(0,end);
 }
 void updateBounds() {
  if (_article.imageAnchors.empty() || !_cachedTextSurface) return;
  const int height = _cachedTextSurface->h, maxScroll = MAX(0,height-int(_limitH));
  _scrolledY = CLIP<int>(_scrolledY,0,maxScroll);
  _verticalScroll->_numEntries = height;
  _verticalScroll->_currentPos = _scrolledY;
  _verticalScroll->_entriesPerPage = _limitH;
  _verticalScroll->_singleStep = MAX(1,int(_limitH)/4);
  _verticalScroll->setVisible(height > _limitH); _verticalScroll->recalc();
  _fluidScroller->setBounds(float(maxScroll),float(_limitH),float(_verticalScroll->_singleStep));
 }
 void prepare() {
  if (!_cachedTextSurface) _composed = false;
  ensureWidget();
  if (_composed || _article.imageAnchors.empty()) return;
  Graphics::MacWindowManager *wm = g_gui.getWM();
  uint8 red = 255, green = 255, blue = 255;
  g_gui.theme()->getDrawDataColor(GUI::kDDWidgetBackgroundDefault,red,green,blue);
  const uint32 background = wm->_pixelformat.ARGBToColor(255,red,green,blue);
  // Use the same English reading font as RichTextWidget. Its current run can
  // be a heading or emphasis and must not become the next block's default.
  Graphics::MacFont font(Graphics::kMacFontNewYork,g_gui.xmlEval()->getVar("Globals.Font.Height",25),Graphics::kMacFontRegular);
  Common::Array<Graphics::ManagedSurface *> parts;
  parts.push_back(_cachedTextSurface); _cachedTextSurface = nullptr;
  uint height = parts[0]->h; _imageRects.clear();
  for (uint n = 0; n < _article.imageAnchors.size(); ++n) {
   const HelpImageAnchor &anchor = _article.imageAnchors[n];
   const HelpImage &image = _book.images[anchor.image];
   const uint width = MIN<uint>(image.width,_textWidth);
   const uint imageHeight = MAX(1U,image.height*width/image.width);
   Graphics::ManagedSurface *picture = new Graphics::ManagedSurface(_textWidth,imageHeight+8,wm->_pixelformat);
   picture->clear(background);
   // Original pictures are separate paragraph elements. Preserve order and
   // aspect ratio; reduce only when the viewport is narrower than the source.
   for (uint y = 0; y < imageHeight; ++y) for (uint x = 0; x < width; ++x) {
    const uint index = image.pixels[(image.height-1-y*image.height/imageHeight)*image.pitch+x*image.width/width];
    picture->setPixel(x,y,wm->_pixelformat.RGBToColor(image.palette[index*4+2],image.palette[index*4+1],image.palette[index*4]));
   }
   _imageRects.push_back(Common::Rect(0,height,width,height+imageHeight));
   parts.push_back(picture); height += picture->h;
   const uint end = n+1 < _article.imageAnchors.size() ? _article.imageAnchors[n+1].offset : _article.markdown.size();
   Common::String text = _article.markdown.substr(anchor.offset,end-anchor.offset); text.trim();
   if (!text.empty()) {
    Graphics::MacText block(Common::U32String(),wm,&font,_txtWnd->getTextColor(),background,_textWidth,Graphics::kTextAlignLeft);
    block.setMarkdownText(Common::U32String(text,Common::kWindows1252));
    const int blockHeight = MAX(1,block.getTextHeight());
    Graphics::ManagedSurface *rendered = new Graphics::ManagedSurface(_textWidth,blockHeight,wm->_pixelformat);
    rendered->clear(background); block.draw(rendered,0,0,_textWidth,blockHeight,0,0);
    parts.push_back(rendered); height += blockHeight;
   }
  }
  _cachedTextSurface = new Graphics::ManagedSurface(_textWidth,height,wm->_pixelformat);
  uint y = 0;
  for (Graphics::ManagedSurface *part : parts) {
   _cachedTextSurface->simpleBlitFrom(*part,Common::Point(0,y)); y += part->h;
   part->free(); delete part;
  }
  _composed = true; updateBounds();
 }
 void scrollTo(int position) {
  prepare(); _verticalScroll->_currentPos = CLIP(position,0,MAX(0,_verticalScroll->_numEntries-int(_limitH)));
  handleCommand(nullptr,GUI::kSetPositionCmd,0);
 }
public:
 HelpTextWidget(GUI::GuiObject *boss, int x, int y, int w, int h, const HelpBook &book, const HelpArticle &article) :
  GUI::RichTextWidget(boss,x,y,w,h,Common::U32String(firstText(article),Common::kWindows1252)),_book(book),_article(article) {}
 void reflowLayout() override { GUI::RichTextWidget::reflowLayout(); prepare(); updateBounds(); }
 void drawWidget() override { prepare(); GUI::RichTextWidget::drawWidget(); }
 bool scrollKey(Common::KeyState state) {
  if (state.flags & (Common::KBD_CTRL | Common::KBD_ALT | Common::KBD_SHIFT | Common::KBD_META)) return false;
  prepare();
  // Keep one line of context between pages. Use the composed article bounds,
  // including pictures, rather than the height of its first text block.
  const int page = MAX(1,int(_limitH)-g_gui.xmlEval()->getVar("Globals.Font.Height",25));
  switch (state.keycode) {
  case Common::KEYCODE_PAGEUP: scrollTo(_scrolledY-page); return true;
  case Common::KEYCODE_PAGEDOWN: scrollTo(_scrolledY+page); return true;
  case Common::KEYCODE_HOME: scrollTo(0); return true;
  case Common::KEYCODE_END: scrollTo(_verticalScroll->_numEntries); return true;
  default: return false;
  }
 }
 int scrollPosition() const { return _scrolledY; }
 int scrollEnd() const { return MAX(0,_verticalScroll->_numEntries-int(_limitH)); }
 void handleMouseWheel(int x, int y, int direction) override {
  if (_article.imageAnchors.empty()) GUI::RichTextWidget::handleMouseWheel(x,y,direction);
  else scrollTo(_scrolledY+direction*MAX(1,int(_limitH)/4));
 }
 void handleMouseDown(int x, int y, int button, int count) override {
  if (_article.imageAnchors.empty()) GUI::RichTextWidget::handleMouseDown(x,y,button,count);
  else { _held = true; _dragY = y; }
 }
 void handleMouseMoved(int x, int y, int button) override {
  if (_article.imageAnchors.empty()) GUI::RichTextWidget::handleMouseMoved(x,y,button);
  else if (_held) { const int delta = _dragY-y; _dragY = y; scrollTo(_scrolledY+delta); }
 }
 void handleMouseUp(int x, int y, int button, int count) override {
  if (_article.imageAnchors.empty()) GUI::RichTextWidget::handleMouseUp(x,y,button,count);
  _held = false;
 }
 void cancelDrag() override { _held = false; GUI::RichTextWidget::cancelDrag(); }
 void scrollToImageForCapture(uint index) { prepare(); if (index < _imageRects.size()) scrollTo(_imageRects[index].top); }
 bool verifyInlineImages() {
  prepare();
  if (_imageRects.size() != _article.imageAnchors.size()) return false;
  for (uint n = 0; n < _imageRects.size(); ++n) {
   const HelpImage &image = _book.images[_article.imageAnchors[n].image];
   const Common::Rect &rect = _imageRects[n];
   for (int y = 0; y < rect.height(); ++y) for (int x = 0; x < rect.width(); ++x) {
    const uint index = image.pixels[(image.height-1-y*image.height/rect.height())*image.pitch+x*image.width/rect.width()];
    const uint32 expected = _cachedTextSurface->format.RGBToColor(image.palette[index*4+2],image.palette[index*4+1],image.palette[index*4]);
    if (_cachedTextSurface->getPixel(rect.left+x,rect.top+y) != expected) return false;
   }
  }
  scrollTo(0x7fff); const int bottom = MAX(0,_verticalScroll->_numEntries-int(_limitH));
  if (_scrolledY != bottom || _verticalScroll->_currentPos != bottom) return false;
  scrollTo(0);
  handleMouseWheel(0,0,1);
  if (_scrolledY != MIN(bottom,MAX(1,int(_limitH)/4))) return false;
  scrollTo(0); handleMouseDown(0,100,1,1); handleMouseMoved(0,73,1); handleMouseUp(0,73,1,1);
  if (_scrolledY != MIN(bottom,27)) return false;
  handleMouseMoved(0,50,0); if (_scrolledY != MIN(bottom,27)) return false;
  scrollTo(0); return _scrolledY == 0;
 }
 bool verifyImageReflow() {
  const int width = _w, height = _h;
  setSize(190,200); reflowLayout(); bool ok = verifyInlineImages();
  setSize(190,280); reflowLayout(); ok = verifyInlineImages() && ok;
  setSize(width,height); reflowLayout(); return verifyInlineImages() && ok;
 }
 void scrollToEndForCapture() {
  scrollTo(0x7fff);
 }
};
class ArticleDialog : public BookDialog {
 const HelpBook &_book; const HelpArticle &_article;
 HelpTextWidget *_reader; bool _captureEnd = false; int _captureImage = -1;
public:
 ArticleDialog(const HelpBook &book, const HelpArticle &article, bool hasPrevious = false, bool hasNext = false) : BookDialog(), _book(book), _article(article) {
  _reader = new HelpTextWidget(this,10,10,_w-20,_h-52,book,article);
  const int buttonWidth = (_w-50)/4;
  GUI::ButtonWidget *previous = new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);
  previous->setEnabled(hasPrevious);
  GUI::ButtonWidget *next = new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);
  next->setEnabled(hasNext);
  GUI::ButtonWidget *pictures = new GUI::ButtonWidget(this,30+buttonWidth*2,_h-32,buttonWidth,22,Common::U32String("Images"),Common::U32String(),4);
  pictures->setEnabled(!article.images.empty());
  new GUI::ButtonWidget(this,40+buttonWidth*3,_h-32,buttonWidth,22,Common::U32String("Back to index"),Common::U32String(),3);
 }
 void captureAtEnd() { _captureEnd = true; }
 void captureAtImage(uint index) { _captureImage = index; }
 bool verifyInlineImages() { return _reader->verifyInlineImages() && _reader->verifyImageReflow(); }
 void handleKeyDown(Common::KeyState state) override {
  if (!_reader->scrollKey(state)) GUI::Dialog::handleKeyDown(state);
 }
 bool verifyKeyboard() {
  handleKeyDown(Common::KeyState(Common::KEYCODE_HOME));
  if (_reader->scrollPosition() != 0) return false;
  handleKeyDown(Common::KeyState(Common::KEYCODE_PAGEUP));
  if (_reader->scrollPosition() != 0) return false;
  const int bottom = _reader->scrollEnd();
  handleKeyDown(Common::KeyState(Common::KEYCODE_PAGEDOWN));
  const int page = _reader->scrollPosition();
  if (page < 0 || page > bottom || (bottom && !page)) return false;
  handleKeyDown(Common::KeyState(Common::KEYCODE_PAGEUP));
  if (_reader->scrollPosition() != 0) return false;
  handleKeyDown(Common::KeyState(Common::KEYCODE_END));
  if (_reader->scrollPosition() != bottom) return false;
  handleKeyDown(Common::KeyState(Common::KEYCODE_PAGEDOWN));
  if (_reader->scrollPosition() != bottom) return false;
  for (const byte modifier : {Common::KBD_CTRL,Common::KBD_ALT,Common::KBD_SHIFT,Common::KBD_META})
   if (_reader->scrollKey(Common::KeyState(Common::KEYCODE_HOME,0,modifier)) || _reader->scrollPosition() != bottom) return false;
  if (_reader->scrollKey(Common::KeyState(Common::KEYCODE_ESCAPE)) || _reader->scrollKey(Common::KeyState(Common::KEYCODE_TAB))) return false;
  handleKeyDown(Common::KeyState(Common::KEYCODE_HOME));
  return _reader->scrollPosition() == 0;
 }
 void handleTickle() override {
  if (_captureEnd) { _reader->scrollToEndForCapture(); _captureEnd = false; }
  if (_captureImage >= 0) { _reader->scrollToImageForCapture(_captureImage); _captureImage = -1; }
  BookDialog::handleTickle();
 }
 void handleCommand(GUI::CommandSender *sender, uint32 cmd, uint32 data) override {
  if (cmd == 4) {
   uint index = 0;
   while (index < _article.images.size()) {
    HelpImageDialog image(_book,_article,index); const int result = image.runModal();
    if (result == 1 && index > 0) --index;
    else if (result == 2 && index+1 < _article.images.size()) ++index;
    else break;
   }
   return;
  }
  if (cmd >= 1 && cmd <= 3) { setResult(cmd); close(); }
  else GUI::Dialog::handleCommand(sender,cmd,data);
 }
};
class HelpIndexDialog : public BookDialog {
 const HelpBook &_book;
 GUI::EditTextWidget *_query;
 GUI::ListWidget *_list;
 Common::Array<uint> _visible;
 void filter() {
  _visible = _book.search(_query->getEditString().encode(Common::kWindows1252));
  Common::U32StringArray titles; for (uint i : _visible) titles.push_back(Common::U32String(_book.articles[i].title,Common::kWindows1252));
  _list->setList(titles); if (!_visible.empty()) _list->setSelected(0);
 }
public:
 void query(const Common::String &text) { _query->setEditString(Common::U32String(text)); filter(); }
 uint visibleCount() const { return _visible.size(); }
 explicit HelpIndexDialog(const HelpBook &book) : BookDialog(), _book(book) {
  new GUI::StaticTextWidget(this,10,8,_w-20,18,Common::U32String("Astronomica Reference"),Graphics::kTextAlignLeft);
  _query = new GUI::EditTextWidget(this,10,32,_w-20,22,Common::U32String(),Common::U32String("Search titles and keywords"),1);
  _list = new GUI::ListWidget(this,10,62,_w-20,_h-108); _list->setNumberingMode(GUI::kListNumberingOff); _list->setEditable(false);
  new GUI::ButtonWidget(this,10,_h-34,100,22,Common::U32String("Read article"),Common::U32String(),2);
  new GUI::ButtonWidget(this,_w-130,_h-34,120,22,Common::U32String("Return to game"),Common::U32String(),3);
  filter();
 }
 void handleCommand(GUI::CommandSender *sender, uint32 cmd, uint32 data) override {
  if (cmd == 1) { filter(); return; }
  if (cmd == 3) { close(); return; }
  if (cmd == 2 || cmd == GUI::kListItemDoubleClickedCmd || cmd == GUI::kListItemActivatedCmd) {
   int index = _list->getSelected(); if (index < 0 || uint(index) >= _visible.size()) return;
   for (;;) {
    ArticleDialog article(_book,_book.articles[_visible[index]],index > 0,uint(index+1) < _visible.size()); const int result = article.runModal();
    if (result == 1 && index > 0) --index;
    else if (result == 2 && uint(index+1) < _visible.size()) ++index;
    else break;
   }
   _list->setSelected(index); return;
  }
  GUI::Dialog::handleCommand(sender,cmd,data);
 }
};
}
bool verifyHelpImages(const HelpBook &book) {
 // Independent original Arial Super runs: help-inline-original.json.
 struct ExponentReference { uint article; const char *text; };
 const ExponentReference exponents[] = {
  {350,"^(\\-7)"},{366,"^(2)"},{366,"^(3)"},{451,"^(22)"},{528,"^(3)"},{571,"^(2)"},
  {671,"^(27)"},{671,"^(30)"},{671,"^(38)"},{671,"^(2)"},{748,"^(17)"},{779,"^(\\-2)"},{779,"^(12)"}
 };
 uint runs = 0; for (const HelpArticle &article : book.articles) runs += article.exponentRuns;
 if (runs != ARRAYSIZE(exponents)) return false;
 for (const ExponentReference &ref : exponents)
  if (ref.article >= book.articles.size() || !book.articles[ref.article].markdown.contains(ref.text)) return false;
 if (!book.articles[366].markdown.contains("p^(2)=a^(3)") || !book.articles[571].markdown.contains("E=mc^(2)")) return false;
 debug("Astronomica help original exponents: PASS (13 runs, Kepler and relativity formulas)");
 // Independent original-file references: help-image-articles.json.
 struct Reference { uint article, width, height; uint32 paletteHash, pixelHash; };
 const Reference references[] = {
  {23,180,132,0x8026e5c5U,0xfc3bb9dfU},
  {54,180,125,0x8026e5c5U,0x8182024cU},
  {67,180,212,0x8026e5c5U,0xd0d7c063U},
  {67,180,238,0x8026e5c5U,0xb7c37013U},
  {77,180,159,0x8026e5c5U,0x51dbb5a1U},
  {267,180,51,0x8026e5c5U,0x4c31d614U},
  {267,180,134,0x8026e5c5U,0x3468d00aU},
  {267,180,240,0x8026e5c5U,0x09fda004U},
  {267,180,85,0x8026e5c5U,0xe7af2421U},
  {267,180,101,0x8026e5c5U,0x855f0c98U},
  {267,180,192,0x8026e5c5U,0xf745d4ebU},
  {361,180,162,0x8026e5c5U,0x6623febfU},
  {361,180,169,0x8026e5c5U,0x299b6db9U},
  {433,180,147,0x8026e5c5U,0xee91c1beU},
  {441,180,115,0x8026e5c5U,0xe2d14455U},
  {441,180,85,0x8026e5c5U,0xc82ab51eU},
  {444,180,133,0x8026e5c5U,0xd07471aeU},
  {451,180,95,0x8026e5c5U,0x0b6063c5U},
  {451,180,97,0x8026e5c5U,0x5bc07471U},
  {451,180,110,0x8026e5c5U,0x4fedfa43U},
  {462,180,223,0x8026e5c5U,0x6dfb95b4U},
  {520,180,223,0x8026e5c5U,0xd17ca4aeU},
  {529,180,218,0x8026e5c5U,0x80638720U},
  {529,180,152,0x8026e5c5U,0x3a0f5880U},
  {598,180,99,0x8026e5c5U,0x0eaf9ad9U},
  {639,180,163,0x8026e5c5U,0xda7ddd76U},
  {667,180,190,0x8026e5c5U,0x1f4c11c1U},
  {679,180,134,0x8026e5c5U,0xf953e185U},
  {721,180,82,0x8026e5c5U,0x95b2bfd4U},
  {731,180,79,0x8026e5c5U,0x0a4337d7U},
  {763,180,288,0x8026e5c5U,0xcc4fc6dcU},
 };
 if (book.images.size() != ARRAYSIZE(references)) return false;
 auto hash = [](const Common::Array<byte> &bytes) {
  uint32 value = 2166136261U; for (byte b : bytes) value = (value ^ b)*16777619U; return value;
 };
 uint associations = 0;
 for (uint a = 0; a < book.articles.size(); ++a) for (uint id : book.articles[a].images) {
  if (id >= ARRAYSIZE(references) || references[id].article != a) return false; ++associations;
 }
 if (associations != ARRAYSIZE(references)) return false;
 for (const HelpArticle &article : book.articles) {
  if (article.imageAnchors.size() != article.images.size()) return false;
  uint previous = 0;
  for (uint n = 0; n < article.imageAnchors.size(); ++n) {
   const HelpImageAnchor &anchor = article.imageAnchors[n];
   if (anchor.image != article.images[n] || anchor.offset < previous || anchor.offset > article.markdown.size()) return false;
   previous = anchor.offset;
  }
 }
 for (uint i = 0; i < book.images.size(); ++i) {
  const HelpImage &image = book.images[i]; const Reference &ref = references[i];
  if (image.width != ref.width || image.height != ref.height || image.pitch != ((ref.width+3)&~3U) ||
      hash(image.palette) != ref.paletteHash || hash(image.pixels) != ref.pixelHash) return false;
  uint count = 0; for (uint id : book.articles[ref.article].images) if (id == i) ++count;
  if (count != 1) return false;
 }
 return true;
}
bool verifyHelpBookUI(const HelpBook &book, const Common::Path &directory) {
 HelpIndexDialog index(book); index.query("moon");
 index.captureThenClose(directory.join("help-index.bmp")); index.runModal();
 if (!index.captured || index.visibleCount() != 24) return false;
 ArticleDialog article(book,book.articles[58]);
 article.captureThenClose(directory.join("help-article.bmp")); article.runModal();
 if (!article.captured) return false;
 for (const uint id : {1U,38U,366U}) {
  ArticleDialog formatted(book,book.articles[id]);
  if (id == 38) formatted.captureAtEnd();
  formatted.captureThenClose(directory.join(Common::String::format("help-format%u.bmp",id))); formatted.runModal();
  if (!formatted.captured) return false;
 }
 for (const uint id : {0U,12U,19U}) {
  uint owner = 0, imageIndex = 0; bool found = false;
  for (uint a = 0; a < book.articles.size(); ++a) for (uint n = 0; n < book.articles[a].images.size(); ++n)
   if (book.articles[a].images[n] == id) { owner = a; imageIndex = n; found = true; }
  if (!found) return false;
  HelpImageDialog picture(book,book.articles[owner],imageIndex);
  picture.captureThenClose(directory.join(Common::String::format("help-image%u.bmp",id))); picture.runModal();
  if (!picture.captured) return false;
  ArticleDialog inlineArticle(book,book.articles[owner]); inlineArticle.captureAtImage(imageIndex);
  inlineArticle.captureThenClose(directory.join(Common::String::format("help-inline%u.bmp",id))); inlineArticle.runModal();
  if (!inlineArticle.captured || !inlineArticle.verifyInlineImages()) return false;
 }
 // Exercise the production renderer for every article, including all tables
 // and combined emphasis; this catches GUI faults that data hashes cannot.
 uint rendered = 0, inlineImages = 0;
 for (const HelpArticle &entry : book.articles) {
  if (entry.title.empty()) continue;
  ArticleDialog dialog(book,entry); dialog.closeAfterFramesForVerification(); dialog.runModal(); ++rendered;
  if (!dialog.verifyKeyboard()) return false;
  if (!entry.imageAnchors.empty()) {
   if (!dialog.verifyInlineImages()) return false;
   inlineImages += entry.imageAnchors.size();
  }
 }
 debug("Astronomica help article rendering: %s (%u articles)",rendered == 781 ? "PASS" : "FAIL",rendered);
 debug("Astronomica help keyboard navigation: PASS (%u articles, page/home/end bounds and modifiers)",rendered);
 debug("Astronomica help inline images: %s (%u original images, pixels and scroll bounds)",inlineImages == 31 ? "PASS" : "FAIL",inlineImages);
 return rendered == 781 && inlineImages == 31;
}
void showHelpBook(const HelpBook &book) { HelpIndexDialog dialog(book); dialog.runModal(); }
}
