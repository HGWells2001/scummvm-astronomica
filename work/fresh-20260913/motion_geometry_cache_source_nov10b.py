"""Reuse the verified decoded dimensions in the actual animation update loop."""
def production(cpp):
 assert 'bool AstronomicaEngine::spriteImageDimensions('in cpp
 start=cpp.index('void AstronomicaEngine::animateSpritesAt(uint32 now) {');end=cpp.index('\nvoid AstronomicaEngine::stepPlace(',start);old=cpp[start:end]
 anchor='''   Graphics::Surface *bmp = motionFile.isOpen() && frame ? decodeSpriteBitmap(motionFile,frame->image,_screen.format) : nullptr;
   if (bmp) {''';assert old.count(anchor)==1
 new=old.replace(anchor,'''   int frameWidth, frameHeight;
   if (motionFile.isOpen() && frame && spriteImageDimensions(motionFile,frame->image,frameWidth,frameHeight)) {''')
 assert new.count('    bmp->free(); delete bmp;')==1;new=new.replace('    bmp->free(); delete bmp;\n','').replace('bmp->w','frameWidth').replace('bmp->h','frameHeight');assert 'bmp'not in new
 return (cpp[:start]+new+cpp[end:]).replace('auto uncached = [&](int x, int y) -> int { \n','auto uncached = [&](int x, int y) -> int {\n')

def trace(cpp):
 start=cpp.index('void AstronomicaEngine::animateSpritesAt(uint32 now) {');end=cpp.index('\nvoid AstronomicaEngine::stepPlace(',start);body=cpp[start:end]
 anchor='   const Frame *frame = staticSpriteFrame(_scene,i);';assert body.count(anchor)==1;body=body.replace(anchor,'   const uint32 traceDecodesBefore = _hitGeometryDecodes;\n'+anchor)
 width,height=('frameWidth','frameHeight')if 'spriteImageDimensions(motionFile' in body else('bmp->w','bmp->h')
 anchor='    if (_place == 516 && i == 12) {';assert body.count(anchor)==1
 line='    if(ConfMan.hasKey("astronomica_trace_motion_geometry")&&ConfMan.getBool("astronomica_trace_motion_geometry"))debug("Motion dimension trace: P%d id%u offset%u size%u width%d height%d time%u misses%u",_place,i+1,frame->image.offset,frame->image.size,'+width+','+height+',now,_hitGeometryDecodes-traceDecodesBefore);\n'
 body=body.replace(anchor,line+anchor);return cpp[:start]+body+cpp[end:]
