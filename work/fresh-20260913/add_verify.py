from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp')
s=p.read_text();needle=' while (!shouldQuit()) {'
insert=''' if (ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) {
  int loaded = 0;
  for (int id = 0; id <= 536; ++id) if (loadPlace(id)) ++loaded;
  debug("Astronomica verification: %d scene prefixes rendered", loaded);
  _screen.free();
  return loaded == 420 ? Common::kNoError : Common::Error(Common::kReadingFailed, "Unexpected scene count");
 }
'''
s=s.replace(needle,insert+needle);p.write_text(s)
Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_text(s)
