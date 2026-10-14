// SPDX-License-Identifier: GPL-3.0-or-later
#include "base/plugins.h"
#include "engines/advancedDetector.h"
#include "astronomica/astronomica.h"
class AstronomicaMetaEngine : public AdvancedMetaEngine<ADGameDescription> {
public:
 const char *getName() const override { return "astronomica"; }
 Common::Error createInstance(OSystem *syst, Engine **engine, const ADGameDescription *) const override {
  *engine = new Astronomica::AstronomicaEngine(syst);
  return Common::kNoError;
 }
};
#if PLUGIN_ENABLED_DYNAMIC(ASTRONOMICA)
REGISTER_PLUGIN_DYNAMIC(ASTRONOMICA, PLUGIN_TYPE_ENGINE, AstronomicaMetaEngine);
#else
REGISTER_PLUGIN_STATIC(ASTRONOMICA, PLUGIN_TYPE_ENGINE, AstronomicaMetaEngine);
#endif
