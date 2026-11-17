// SPDX-License-Identifier: GPL-3.0-or-later
// Original ASTRONOM.HLP research: probe_help_directory/compression/navigation.py.
#ifndef ASTRONOMICA_HELP_H
#define ASTRONOMICA_HELP_H
#include "common/array.h"
#include "common/str.h"
#include "common/stream.h"
#include "common/path.h"
namespace Astronomica {
struct HelpImageAnchor { uint offset, image; }; // Offset in the adapted Markdown, before the image.
struct HelpArticle { Common::String title, text, markdown; Common::Array<uint> images; Common::Array<HelpImageAnchor> imageAnchors; uint exponentRuns = 0; };
struct HelpImage {
 uint width = 0, height = 0, pitch = 0;
 Common::Array<byte> palette, pixels; // Original BGRA palette and bottom-up DIB.
};
class HelpBook {
public:
 Common::Array<HelpArticle> articles;
 Common::Array<HelpImage> images;
 uint32 recordHash = 0, formatHash = 2166136261U;
 uint formatCommands = 0, formatRecords = 0;
 uint recordCount = 0, keywordCount = 0, referenceCount = 0;
 bool load(Common::SeekableReadStream &stream);
 Common::Array<uint> search(const Common::String &query) const;
private:
 struct Keyword { Common::String name; Common::Array<uint> articles; };
 Common::Array<Keyword> _keywords;
 bool parse(Common::SeekableReadStream &stream);
};
bool verifyHelpImages(const HelpBook &book);
bool verifyLegacyHelpFocus(const HelpBook &book);
bool verifyHelpBookUI(const HelpBook &book, const Common::Path &directory);
void showHelpBook(const HelpBook &book);
}
#endif
