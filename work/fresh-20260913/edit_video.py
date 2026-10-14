from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom');engine=out/'engine/astronomica'
p=engine/'script.h';s=p.read_text().replace(' void setImageTargets(', ' void setMovieTargets(const Common::Array<uint32> &durations) { _movieDurations = durations; }\n void setImageTargets(').replace(' Common::Array<bool> _soundTargets;', ' Common::Array<bool> _soundTargets;\n Common::Array<uint32> _movieDurations;');p.write_text(s)
p=engine/'script.cpp';s=p.read_text().replace('_soundTargets.clear(); _imageTargets.clear();','_soundTargets.clear(); _imageTargets.clear(); _movieDurations.clear();')
s=s.replace('  if (c.opcode == 20) {\n   Common::String', '''  if (c.opcode == 3 || c.opcode == 37) {
   if (uint(c.args[0]) >= _movieDurations.size() || !_movieDurations[c.args[0]]) return false;
   if (c.opcode == 37 && uint64(c.args[1])+uint64(c.args[2]) > _movieDurations[c.args[0]]) return false;
  }
  if (c.opcode == 20) {
   Common::String''')
s=s.replace('  case 20:\n', '''  case 3:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] >= 100 || c.args[1] < 0 || c.args[1] > 640 || c.args[2] < 0 || c.args[2] > 480 || c.args[3] != 0) return false;
   break;
  case 37:
   if (c.args.size() != 3 || c.args[0] < 0 || c.args[0] >= 100 || c.args[1] < 0 || c.args[2] <= 0) return false;
   break;
  case 20:
''')
s=s.replace('  if (c.opcode == 20) {\n   Action image', '''  if (c.opcode == 3 || c.opcode == 37) {
   Action movie = {c.opcode, c.args[0], c.args[1], c.args[2]}; _actions.push_back(movie);
  }
  if (c.opcode == 20) {
   Action image''');p.write_text(s)
p=engine/'astronomica.h';s=p.read_text().replace('namespace Audio {', 'namespace Video { class QuickTimeDecoder; }\nnamespace Audio {').replace(' ~AstronomicaEngine() override { _pendingImage.free(); _mixer->stopHandle(_soundHandle); }',' ~AstronomicaEngine() override;')
s=s.replace(' int _place;', ''' Video::QuickTimeDecoder *_movie = nullptr;
 bool _moviePlaying = false;
 int _movieX = 0, _movieY = 0;
 uint _movieFramesDrawn = 0;
 void closeMovie();
 void configureMovie();
 void updateMovie();
 int _place;''');p.write_text(s)
p=engine/'astronomica.cpp';s=p.read_text().replace('#include "image/bmp.h"','#include "image/bmp.h"\n#include "video/qt_decoder.h"')
s=s.replace('namespace Astronomica {','''namespace Astronomica {
AstronomicaEngine::~AstronomicaEngine() {
 closeMovie(); _pendingImage.free(); _mixer->stopHandle(_soundHandle);
}
void AstronomicaEngine::closeMovie() {
 delete _movie; _movie = nullptr; _moviePlaying = false;
}
void AstronomicaEngine::configureMovie() {
 Common::Array<uint32> durations;
 // _load_place 9:2651-266f redirects P520's shared movie to P408.
 // Other movie contexts remain unregistered until their rules are decoded.
 if (_place == 520 && _scene.movies.size() == 1 && _scene.movies[0].equalsIgnoreCase("mentors.mov")) {
  Common::File *file = new Common::File();
  const Common::Path path = ConfMan.getPath("path").join(Common::Path("PLACES/P408/MENTORS.MOV"));
  if (file->open(Common::FSNode(path))) {
   _movie = new Video::QuickTimeDecoder();
   if (_movie->loadStream(file) && _movie->isSeekable() && _movie->getWidth() <= 640 && _movie->getHeight() <= 480) {
    durations.push_back(_movie->getDuration().totalNumberOfFrames());
    debug("Astronomica P520 movie: %ux%u, scale %u, duration %u",_movie->getWidth(),_movie->getHeight(),_movie->getTimeScale(),durations[0]);
   } else closeMovie();
  } else delete file;
 }
 _runner.setMovieTargets(durations);
}
void AstronomicaEngine::updateMovie() {
 if (!_movie || !_moviePlaying) return;
 if (_movie->endOfVideo()) { _movie->stop(); _moviePlaying = false; return; }
 if (!_movie->needsUpdate()) return;
 const Graphics::Surface *frame = _movie->decodeNextFrame();
 if (!frame) return;
 Graphics::Surface *rgb = frame->convertTo(_screen.format, _movie->getPalette());
 if (!rgb) return;
 for (int y = 0; y < rgb->h && y+_movieY < _screen.h; ++y)
  for (int x = 0; x < rgb->w && x+_movieX < _screen.w; ++x)
   _screen.setPixel(x+_movieX,y+_movieY,rgb->getPixel(x,y));
 rgb->free(); delete rgb; ++_movieFramesDrawn; presentScene();
}
''',1)
s=s.replace(' _background.copyFrom(candidate);', ' closeMovie();\n _background.copyFrom(candidate);',1)
s=s.replace(' configureImages();',' configureImages();\n configureMovie();',1)
s=s.replace(' if (_loopSound < 0 || !_loopEnabled', ' if (_moviePlaying || _loopSound < 0 || !_loopEnabled')
s=s.replace(' while (_runner.popAction(action)) {', ''' while (_runner.popAction(action)) {
  if (action.opcode == 37 && _movie) {
   const uint32 scale = _movie->getTimeScale();
   _movie->setEndTime(Audio::Timestamp(0,uint32(action.x)+uint32(action.y),scale));
   if (!_movie->seek(Audio::Timestamp(0,action.x,scale))) warning("Astronomica: movie segment seek failed");
   continue;
  }
  if (action.opcode == 3 && _movie) {
   _mixer->stopHandle(_soundHandle);
   _movieX = action.x; _movieY = action.y; _movie->start(); _moviePlaying = true;
   debug("Astronomica P520 movie started at %d,%d",_movieX,_movieY);
   continue;
  }''',1)
s=s.replace('   resumeLoopAt(scriptClock());','   resumeLoopAt(scriptClock());') # insertion below uses actual indentation
s=s.replace('  resumeLoopAt(scriptClock());','  resumeLoopAt(scriptClock());\n  updateMovie();')
marker='  // P505: all eight original prompts, using rectangle clicks only.'
test='''  bool movieOK = loadPlace(520) && _movie && _movie->getTimeScale() == 30;
  if (_movie) {
   movieOK = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && movieOK;
   runScriptsAt(0); runScriptsAt(0);
   const uint beforeFrames = _movieFramesDrawn;
   updateMovie();
   movieOK = _moviePlaying && _movieX == 240 && _movieY == 130 && _movieFramesDrawn == beforeFrames+1 &&
    _movie->getEndTime() == Audio::Timestamp(0,56681,30) && movieOK;
   for (uint point = 0; point < 3; ++point) {
    const uint32 tick = 55407 + point*600;
    movieOK = _movie->seek(Audio::Timestamp(0,tick,30)) && movieOK;
    const Graphics::Surface *frame = _movie->decodeNextFrame();
    movieOK = frame && frame->w > 0 && frame->h > 0 && movieOK;
   }
   runScriptsAt(43999); movieOK = _place == 520 && movieOK;
   runScriptsAt(44000); movieOK = _place == 537 && !_movie && !_moviePlaying && movieOK;
   movieOK = loadPlace(520) && movieOK;
   movieOK = _runner.enqueueStartup(_scene.scripts,0,true) == 1 && movieOK;
   runScriptsAt(0); runScriptsAt(0);
   clickAtTime(10,10,1); runScriptsAt(1);
   movieOK = _place == 537 && !_movie && !_runner.pendingCount() && movieOK;
  }
  debug("Astronomica P520 movie verification: %s (original segment, three decoded positions, timed P537 transition, click skip and decoder cleanup)",movieOK ? "PASS" : "FAIL");
  scriptsOK = movieOK && scriptsOK;
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
for f in engine.iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
