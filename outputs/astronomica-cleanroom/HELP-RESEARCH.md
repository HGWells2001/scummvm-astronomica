# Original help and resume, 11 October 2026

probe_menu_services.py resolves custom22 to _process_help, which constructs
%s/HELP/ASTRONOM.HLP, calls USER ordinal171 with command2 then command9,
and sets the help-requested flag. P408 additionally stops sound, blacks the
screen, invokes KludgePlayFrame1 and stops the mentor movie. Help remains an
external Windows service in the original; no native replacement is claimed.

Custom33 calls _read_globals at9:4275, the TEXT gamestat reader. It does NOT
call _read_globals_save at9:433e. Both use102 values, but one uses decimal
long values separated by whitespace and the other uses102 binary DWORDs.
The earlier binary-layout research remains valid for that separate routine.
The text writer/reader bodies pass15 roundtrips, modeling libc formatted I/O
and successful file opening. Startup's resume flag checks only the first
text value: scenes27..422 or >437 enable it.1088 branch cases pass. The
original reader does not validate the entire payload before changing state;
a native importer must do so. No original gamestat import is implemented.

probe_help_directory.py checks all41 internal streams and every allocation
boundary in the838253-byte original HLP. Its title B-tree has782 entries;
31 streams contain bitmaps. The directory and title leaf links, entry counts,
page sizes and free-byte counts are consistent. The system title is
Astronomica Reference, with BrowseButtons() stored as a macro; it is not run.

probe_help_compression.py infers bounded LZ decoding and the phrase token
layout from the original file.1701 phrases expand to11766 bytes, exactly the
stored size. All68 compressed topic blocks decode.2117 linked records pass
previous/next linkage and exact expanded-text-size checks;2115 contain text.
The782 topic-header titles exactly match the independent title index in order.
This is strong file consistency evidence, not a comparison with Windows
WinHelp execution. Formatting records, bitmap rendering, hyperlinks and a
native help interface remain to be implemented. Text includes NUL-separated
format runs; do not treat NUL as an end of the whole article.

Next: decode formatting/link records and connect a native help viewer to
custom22, preserving P408 movie/audio state. For resume, distinguish native
ScummVM slots from legacy text gamestat and resolve the original countdown
clock epoch before importing active countdowns. Keep original files read-only.

## Navigation consistency, same checkpoint

All782 title references also match their decoded character positions: each
16384-address topic block contributes a32768-unit reference base, body text
contributes its expanded length, and each embedded bitmap contributes one
extra unit. The fixed bitmap record pattern86220880020000 followed by a
16-bit ID occurs31 times, covering IDs0..30 in order. This identifies embedded
bitmap references, not their rendering or a general formatting-bytecode parser.

probe_help_navigation.py validates the context/keyword B-tree leaf links,
counts, unused bytes and all referenced character positions.781 unique context
hashes,812 keywords and2008 keyword references resolve into exactly one decoded
body span. References are interior character positions, not header addresses;
776 contexts happen to be title-reference+3, but five are different, so no
fixed-offset shortcut is used. Inline hyperlink commands remain undecoded.
WinUser.h in the installed Windows SDK confirms help command2=HELP_QUIT and
command9=HELP_FORCEFILE. No Windows help process was launched.

## Native reading view, 12 October 2026 (targeted and full suite PASS)

help.cpp now reads the original HLP directly. No converted article files are
needed at runtime. Bounded LZ and phrase decoding, directory/title validation,
linked records and keyword character spans reconstruct782 topic headers,
including an empty footer;781 articles are exposed in the index. Native
record FNV2cab83c0 agrees with the independent original-file research for all
2117 records. Search includes title substrings and original keyword references.
Five independent result sets verify781/1/24/9/0 matches and article-order hashes.
Eleven truncations and seven corruptions are rejected without replacing the
previously loaded book. Text NUL runs are preserved for comparison and then
adapted into paragraphs for a reading view; this is not the original layout.

Custom22 is accepted only in P1/P408 with a successfully loaded book and
original arguments[22,1,0,0,0,0]. Original hit-tested buttons open a ScummVM
modal index. It stops foreground sound, stops the mentor movie in P408 and
pauses the native script clock until the viewer closes. Scene/input return is
verified. Article views have scrolling and previous/next within search results.
All changes are in the real engine; no prototype viewer is used.

The scoped GUI test captures actual ScummVM overlays after rendered frames.
The build has no PNG writer, so captures use BMP and are converted losslessly
to PNG only for inspection. The initial capture failure propagated a test
failure into ScummVM's error dialog, whose font warning was secondary; it was
not the cause of the reading-view failure. The index and article captures are
readable at640x480. Builtin bitmap fonts are used by this local build.

Remaining:31 inline bitmap renderings, original styles/table formatting,
inline link commands, symbol-font mapping and manual audiovisual/full-game
verification. The reading view must not be described as complete WinHelp
emulation. The original text is retained, including historical scientific
statements; no editorial rewriting or external content is substituted.
Full regression and checkpoint status: see help-native-validation.json.

## Bitmap decoding research, 12 October 2026

probe_help_bitmaps.py decodes all31 original picture streams. Thirty use
compression2 (bounded LZ); bitmap12 uses compression0 and stores raw pixels.
All are180 pixels wide,8-bit indexed DIBs with256 BGRA palette entries; row
sizes and entire internal-stream extents match. Their heights vary. Packed
integer widths depend on the low bit (16/32 or8/16 bits), then shift right1.
Group headers contain one image at offset8; there are no hotspot payloads.
The first image was inspected as a bottom-up DIB and depicts Andromeda.

This prepares the next production step but does not add images to the native
reading view yet. Use evidence/help-bitmaps.json for exact dimensions and
palette/pixel hashes. Respect compression0 for bitmap12; applying LZ to every
stream was rejected during research. No game files were modified.


## Original formatting research, 12 October 2026

probe_help_format.py independently decodes all1335 body-format records:
1031 paragraphs and304 table rows. Every one of11455 NUL separators pairs
with a command, and table paragraph text offsets match exactly.16 font
descriptions use11-byte entries;93 names have20-byte storage slots. Only
font80, line81, paragraph82, tab83, bitmap86 and endFF occur. Consequently
there are no hyperlink commands to implement in this source HLP; previous
notes listing inline hyperlinks as pending were an unverified assumption.

The native semantic reference is FNVb5265663, over kind, columns, paragraph
flags/offsets/tabs, each command, its text and any font/image operand. The
original file hash is checked by the independent probe. This reference is
separate from the unchanged2117-record text FNV2cab83c0.

The production renderer exposed two existing Markdown limitations during
validation: empty table cell buffers can trigger a null-string assertion,
and triple emphasis is an unimplemented callback. The engine supplies a
nonbreaking blank for empty cells and uses nested bold/italic delimiters.
HTML numeric entities displayed literally in this reader, so the blank is
an actual CP1252 nonbreaking space. Final status and captures are recorded
only by finish_help_media.py after the matching tests complete.


## Native help images and basic formatting, 12 October 2026

All31 original bitmap palettes/pixels and their associations with20 articles are checked against independent file research. The native Images button opens article pictures with previous/next navigation.41 image corruption cases reject bad data while preserving the loaded book. All1335 body records and11455 formatting commands match semantic FNVb5265663;304 table rows are decoded. Basic bold/italic, paragraphs and table cells are rendered. All781 articles opened in the production renderer without failure; targeted GUI captures and full WASAPI regression PASS. Exact typography, symbol fonts, underline/strikeout, original measurements and inline image positions remain pending. All body commands were inspected: there are no inline hyperlink opcodes in this original file; See references are text. This corrects the earlier pending-hyperlink assumption. No manual complete game-playthrough claim. See help-native-validation.json.


## Inline help pictures, 13 October 2026

All 31 pictures now appear between the original text runs in 20 articles. Anchors come from decoded bitmap commands, not caption matching. All are in paragraph records, none in tables. Rendering combines the existing Markdown text with decoded original pixels in one scrolling article; pictures shrink only for narrow viewports and retain their aspect ratio. No generated image archive or filesystem cache is needed. The separate Images view is still available. Exact WinHelp spacing is not claimed.

The production GUI opened all 781 articles. Pixel checks cover all 31 inline pictures, scrolling to both ends, wheel and drag, narrow width, height-only resize and restored dimensions. Andromeda, Jupiter and Moon captures were visually inspected. Native save/import regressions and the full WASAPI suite passed on the matching executable.

probe_help_inline.py also inventories every nonempty font run. No Symbol font is used; descriptors with flags 4 and 33 have no nonempty text runs. Earlier generic pending Symbol/underline items were not demonstrated by the original contents. Arial Super occurs in 13 runs, 21 characters, including Kepler and relativity exponents. These now use explicit ^(exponent) notation instead of misleading baseline digits. All 13 original runs and both formulas are checked; no new scientific values or corrections are added. Kepler article rendering was visually inspected. Raised glyph typography remains an adaptation, not a pixel-identical font recreation. See help-inline-original.json.
