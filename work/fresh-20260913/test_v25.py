from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text();anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
s=s.replace(anchor,'''  ConfMan.setBool("astronomica_animation", false);
  bool imageOK = true;
  const int imagePlaces[] = {505,511,509};
  const uint32 imageRGB[] = {0xc151b7ceU,0x20d2fafaU,0x5f179308U,0x345d92f2U,0xe05d7dc8U,0x22addbf3U};
  const uint32 image565[] = {0xad8d5612U,0xb18d8507U,0xc02158e3U,0x0b7246c5U,0xec80bd54U,0xa263c6caU};
  for (uint sceneIndex = 0; sceneIndex < 3; ++sceneIndex) {
   imageOK = loadPlace(imagePlaces[sceneIndex]) && imageOK;
   const uint32 beforeImage = screenRGBHash(_screen);
   Common::Array<Script> pairs;
   for (uint p = 0; p < _scene.scripts.size(); ++p) for (uint c = 0; c+1 < _scene.scripts[p].size(); ++c)
    if (_scene.scripts[p][c].opcode == 20 && _scene.scripts[p][c+1].opcode == 49) {
     Script pair; pair.push_back(_scene.scripts[p][c]); pair.push_back(_scene.scripts[p][c+1]); pairs.push_back(pair);
    }
   imageOK = pairs.size() >= 2 && imageOK;
   for (uint pairIndex = 0; pairIndex < 2 && pairIndex < pairs.size(); ++pairIndex) {
    imageOK = loadPlace(imagePlaces[sceneIndex]) && _runner.start(pairs[pairIndex],0,true) && imageOK;
    applyScriptActions(0);
    const uint32 expected = rgb565 ? image565[sceneIndex*2+pairIndex] : imageRGB[sceneIndex*2+pairIndex];
    imageOK = screenRGBHash(_screen) == expected && imageOK;
    redrawSprites(); imageOK = screenRGBHash(_screen) == expected && imageOK;
    Script missingImage = pairs[pairIndex]; missingImage[0].text = "MISSING_IMAGE";
    imageOK = !_runner.start(missingImage,0,true) && screenRGBHash(_screen) == expected && imageOK;
    missingImage[0].text = "../CLOUD3";
    imageOK = !_runner.start(missingImage,0,true) && imageOK;
    Script delayedDisplay = pairs[pairIndex]; delayedDisplay[1].delay = 1;
    imageOK = !_runner.start(delayedDisplay,0,true) && imageOK;
    Script unknownImage = pairs[pairIndex]; Command unknown; unknown.opcode = 999; unknownImage.push_back(unknown);
    imageOK = !_runner.start(unknownImage,0,true) && screenRGBHash(_screen) == expected && imageOK;
   }
   imageOK = loadPlace(imagePlaces[sceneIndex]) && screenRGBHash(_screen) == beforeImage && imageOK;
  }
  // P508 stages its bitmap across branch control; this form remains rejected.
  imageOK = loadPlace(508) && !_runner.canRun(_scene.scripts[1],true) && imageOK;
  debug("Astronomica background image verification: %s (six original pairs across P505/P511/P509, independent RGB hashes, redraw persistence, reload, missing/unsafe/delayed rejection)", imageOK ? "PASS" : "FAIL");
  scriptsOK = imageOK && scriptsOK;
'''+anchor);p.write_text(s)
import shutil
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
