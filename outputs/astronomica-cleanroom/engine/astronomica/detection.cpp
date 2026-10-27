// SPDX-License-Identifier: GPL-3.0-or-later
#include "base/plugins.h"
#include "engines/advancedDetector.h"
static const PlainGameDescriptor games[] = {
 {"astronomica", "Astronomica: The Quest for the Edge of the Universe"}, {nullptr, nullptr}
};
static const ADGameDescription descriptions[] = {
 {"astronomica", "Experimental", AD_ENTRY2s("GAMEDATA", "84099c2580e5c71beec97ca3e52a5967", 1604, "ASTRO.EXE", "14929fa8e52d7e3bc539244413703ecb", 418376), Common::EN_ANY, Common::kPlatformWindows, ADGF_UNSTABLE, GUIO0()},
 {"astronomica", "CD root resources (experimental)", AD_ENTRY1s("ASTRO.EXE", "14929fa8e52d7e3bc539244413703ecb", 418376), Common::EN_ANY, Common::kPlatformWindows, ADGF_UNSTABLE, GUIO0()},
 AD_TABLE_END_MARKER
};
static const char *const globs[] = {"PLACES", "SETUP", nullptr};
class AstronomicaMetaEngineDetection : public AdvancedMetaEngineDetection<ADGameDescription> {
public:
 AstronomicaMetaEngineDetection() : AdvancedMetaEngineDetection(descriptions, games) { _maxScanDepth = 2; _directoryGlobs = globs; }
 const char *getName() const override { return "astronomica"; }
 const char *getEngineName() const override { return "Astronomica / Hyper-Trieve"; }
 const char *getOriginalCopyright() const override { return "(C) 1994 Hyper-Quest / FX Media"; }
};
REGISTER_PLUGIN_STATIC(ASTRONOMICA_DETECTION, PLUGIN_TYPE_ENGINE_DETECTION, AstronomicaMetaEngineDetection);
