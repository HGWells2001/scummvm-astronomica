from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text();needle=' _runner.setSoundTargets(targets);';s=s.replace(needle,''' // The supplied P508 scripts request S9, absent from the original files.
 // _playSound does not abort command execution when sndPlaySound fails.
 if (_place == 508 && ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
  const Common::Path missing = ConfMan.getPath("path").join(Common::Path("PLACES/P508/S9.WAV"));
  if (!Common::FSNode(missing).exists()) targets[9] = true;
 }
'''+needle);needle=' Audio::SeekableAudioStream *stream = openSound(id);\n if (!stream) return false;';repl=''' Audio::SeekableAudioStream *stream = openSound(id);
 if (!stream) {
  const Common::Path missing = ConfMan.getPath("path").join(Common::Path("PLACES/P508/S9.WAV"));
  if (_place == 508 && id == 9 && !looping && !Common::FSNode(missing).exists()) {
   _mixer->stopHandle(_soundHandle); _lastSoundAt = now;
   debug("Astronomica: original P508/S9.WAV absent; continuing after failed sound request");
   return true;
  }
  return false;
 }''';assert needle in s;s=s.replace(needle,repl,1);p.write_text(s);shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
