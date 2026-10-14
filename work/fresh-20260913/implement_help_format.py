from pathlib import Path
r=Path('outputs/astronomica-cleanroom/engine/astronomica');p=r/'help.h';s=p.read_text().replace('Common::String title, text;', 'Common::String title, text, markdown;').replace('uint32 recordHash = 0;', 'uint32 recordHash = 0, formatHash = 2166136261U;\n uint formatCommands = 0, formatRecords = 0;');p.write_text(s)
p=r/'help.cpp';s=p.read_text();mark='}\nbool HelpBook::load('
insert='''// Original formatting pairs every NUL in the expanded body with exactly one
// command. The same paragraph grammar is used inside table cells (kind 35).
struct HelpFont { uint flags, halfPoints; };
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
 const Common::String marker = (flags&3) == 3 ? "***" : (flags&1) ? "**" : (flags&2) ? "*" : "";
 return raw.substr(0,begin)+(begin == end ? "" : marker+escapeMarkdown(raw.substr(begin,end-begin))+marker)+raw.substr(end);
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
  out += styledText(text,fonts[state.font].flags);
  switch (opcode) {
  case 0x80: state.font = r.get(2); if (state.font >= fonts.size()) return false; formatWord(hash,state.font); break;
  case 0x81: out += cell ? " " : "  \\n"; break;
  case 0x82: out += cell ? " " : "\\n\\n"; break;
  case 0x83: out += "    "; break;
  case 0x86: {
   static const byte prefix[] = {0x22,0x08,0x80,2,0,0};
   for (byte b : prefix) if (r.get(1) != b) return false;
   const uint id = r.get(2); if (id >= 31) return false; formatWord(hash,id);
   // The matching original picture is available through the Images button.
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
  if (state.tableColumns) { article.markdown += "\\n"; state.tableColumns = 0; }
  Common::String paragraph;
  if (!formatParagraph(r,body,cursor,fonts,article,state,paragraph,false,hash,commands)) return false;
  article.markdown += paragraph+"\\n\\n";
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
   article.markdown += "\\n|";
   for (uint i = 0; i < columns; ++i) article.markdown += " |";
   article.markdown += "\\n|";
   for (uint i = 0; i < columns; ++i) article.markdown += " --- |";
   article.markdown += "\\n"; state.tableColumns = columns;
  }
  article.markdown += "|";
  for (const Common::String &cellText : cells) article.markdown += " "+cellText+" |";
  article.markdown += "\\n";
 }
 return r.ok && r.pos == bytes.size() && cursor == body.size();
}
'''
s=s.replace(mark,insert+mark,1)
s=s.replace(' if (!fetch("|Phrases",data)', ''' if (!fetch("|FONT",data) || data.size() < 8) return false;
 Reader fontReader(data); const uint names = fontReader.get(2), fontCount = fontReader.get(2);
 const uint nameOffset = fontReader.get(2), fontOffset = fontReader.get(2);
 if (names != 93 || fontCount != 16 || nameOffset != 8 || fontOffset != nameOffset+20*names || data.size() != fontOffset+11*fontCount) return false;
 Common::Array<HelpFont> fonts;
 for (uint i = 0; i < fontCount; ++i) {
  fontReader.seek(fontOffset+11*i); HelpFont font; font.flags = fontReader.get(1); font.halfPoints = fontReader.get(1);
  if (fontReader.get(1) != 3 || fontReader.get(2) >= names) return false;
  fonts.push_back(font);
 }
 if (!fetch("|Phrases",data)''')
s=s.replace(' uint titleIndex = 0;', ' FormatState formatState;\n uint titleIndex = 0;')
s=s.replace('HelpArticle article; article.title = body;', 'formatState = FormatState(); HelpArticle article; article.title = body;')
s=s.replace('   articles.back().text += readingText(body)+"\\n\\n";', '''   articles.back().text += readingText(body)+"\\n\\n";
   if (!formatBody(raw,textOffset,kind,body,fonts,articles.back(),formatState,formatHash,formatCommands)) return false;
   ++formatRecords;''')
s=s.replace('escapeMarkdown(article.text);','article.markdown;')
p.write_text(s)
for n in ('help.cpp','help.h'):
 Path('work/fresh-20260913/scummvm/engines/astronomica',n).write_bytes((r/n).read_bytes())
