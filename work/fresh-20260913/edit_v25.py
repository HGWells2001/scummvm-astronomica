from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'script.h';s=f.read_text().replace('struct Action { int32 opcode, value, x, y; };','struct Action { int32 opcode, value, x, y; Common::String text; };');s=s.replace(' void setSoundTargets(', ' void setImageTargets(const Common::Array<Common::String> &targets) { _imageTargets = targets; }\n void setSoundTargets(');s=s.replace(' Common::Array<bool> _soundTargets;', ' Common::Array<bool> _soundTargets;\n Common::Array<Common::String> _imageTargets;');f.write_text(s)
f=p/'script.cpp';s=f.read_text().replace(' _soundTargets.clear();',' _soundTargets.clear(); _imageTargets.clear();');s=s.replace('  if (c.opcode == 23 &&', '''  if (c.opcode == 20) {
   Common::String name = c.text; name.toUppercase(); bool found = false;
   for (uint t = 0; t < _imageTargets.size(); ++t) if (_imageTargets[t] == name) found = true;
   if (!found) return false;
  }
  if (c.opcode == 23 &&''',1);s=s.replace('  case 23:\n', '''  case 20:
   // Only the adjacent immediate display form is verified. No staged image
   // can survive a branch, delay or scene change in this admitted subset.
   if (c.args.size() != 2 || c.text.empty() || i + 1 >= script.size() || script[i+1].opcode != 49 || script[i+1].delay != -1) return false;
   break;
  case 49:
   if (!c.args.empty() || !i || script[i-1].opcode != 20 || c.delay != -1) return false;
   break;
  case 23:
''');needle='  if (c.opcode == 25 ||';s=s.replace(needle,'''  if (c.opcode == 20) {
   Action image = {20, 0, int16(c.args[0]), int16(c.args[1]), c.text};
   _actions.push_back(image);
  }
'''+needle);f.write_text(s)
f=p/'astronomica.h';s=f.read_text().replace(' void configureSounds();',' void configureSounds();\n void configureImages();\n Graphics::Surface *openBackgroundImage(const Common::String &name);\n bool drawBackgroundImage(const Common::String &name, int x, int y);');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace(' configureSounds();',' configureSounds();\n configureImages();',1);anchor='void AstronomicaEngine::configureSounds() {'
s=s.replace(anchor,'''Graphics::Surface *AstronomicaEngine::openBackgroundImage(const Common::String &rawName) {
 Common::String name = rawName; name.toUppercase();
 if (name.empty() || name == "." || name == "..") return nullptr;
 for (uint i = 0; i < name.size(); ++i)
  if (!((name[i] >= 'A' && name[i] <= 'Z') || (name[i] >= '0' && name[i] <= '9') || name[i] == '_' || name[i] == '-' || name[i] == '.')) return nullptr;
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/",_place) + name));
 if (!file.open(Common::FSNode(path)) || file.size() < 54 || file.readUint16LE() != 0x4d42) return nullptr;
 file.seek(0); Image::BitmapDecoder decoder;
 if (!decoder.loadStream(file) || !decoder.getSurface()) return nullptr;
 const Graphics::Surface *src = decoder.getSurface();
 if (src->w <= 0 || src->h <= 0 || src->w > 640 || src->h > 480) return nullptr;
 return src->convertTo(_screen.format,decoder.getPalette().data(),decoder.getPalette().size());
}
void AstronomicaEngine::configureImages() {
 Common::Array<Common::String> targets;
 if (_scene.layers == 1) {
  Common::FSList files;
  const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d",_place)));
  Common::FSNode(path).getChildren(files,Common::FSNode::kListFilesOnly);
  for (uint i = 0; i < files.size(); ++i) {
   Common::String name = files[i].getName(); name.toUppercase();
   Graphics::Surface *surface = openBackgroundImage(name);
   if (surface) { targets.push_back(name); surface->free(); delete surface; }
  }
 }
 _runner.setImageTargets(targets);
}
bool AstronomicaEngine::drawBackgroundImage(const Common::String &name, int x, int y) {
 Graphics::Surface *src = openBackgroundImage(name);
 if (!src) return false;
 // Original SRCCOPY modifies the world background, then redraws sprites.
 for (int sy = 0; sy < src->h; ++sy) for (int sx = 0; sx < src->w; ++sx)
  if (x+sx >= 0 && x+sx < _background.w && y+sy >= 0 && y+sy < _background.h)
   _background.setPixel(x+sx,y+sy,src->getPixel(sx,sy));
 src->free(); delete src; return true;
}
'''+anchor);s=s.replace('  if (action.opcode == 25) {','''  if (action.opcode == 20) {
   if (drawBackgroundImage(action.text,action.x,action.y)) { redrawSprites(); dirty = false; }
   else warning("Astronomica: cannot draw image %s",action.text.c_str());
   continue;
  }
  if (action.opcode == 25) {''');f.write_text(s)
