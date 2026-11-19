"""Restore original _draw_score as a derived presentation layer, without serialized state."""
RENDER=r'''
// ASTRO.EXE _draw_score3:39ca-3adf. The final flag adds its own27th marker.
static void composePuzzleProgress(Graphics::Surface &band,const ScriptRunner &runner){
 int32 finalFlag=0;runner.getValue(0,46,finalFlag);const int count=finalFlag==1?27:26;
 const uint32 white=band.format.RGBToColor(255,255,255);
 for(int i=0;i<count;++i){
  int32 value=0;runner.getValue(0,20+i,value);const int x=6*i;
  band.fillRect(value==1?Common::Rect(x,0,x+4,4):Common::Rect(x+1,1,x+3,3),white);
 }
}
'''
OVERLAY=r'''
 // Derive the original marks at presentation time. Keep puzzle/background
 // pixel buffers unchanged: progress is already persisted in the100 globals.
 if(_scene.mode==1&&_screen.w>=176&&_screen.h>=331&&_screen.format.bytesPerPixel<=4){
  byte pixels[160*4*4];Graphics::Surface band;
  band.init(160,4,160*_screen.format.bytesPerPixel,pixels,_screen.format);
  band.copyRectToSurface(_screen,0,0,Common::Rect(16,327,176,331));
  composePuzzleProgress(band,_runner);
  _system->copyRectToScreen(band.getPixels(),band.pitch,16,327,160,4);
 }
'''
def production(cpp,header):
    anchor='void AstronomicaEngine::presentScene() {';assert cpp.count(anchor)==1
    cpp=cpp.replace(anchor,RENDER+'\n'+anchor)
    anchor=' _system->copyRectToScreen(_screen.getPixels(), _screen.pitch, 0, 0, 640, 480);\n _system->updateScreen();\n}\nvoid AstronomicaEngine::redrawSprites()'
    assert cpp.count(anchor)==1
    cpp=cpp.replace(anchor,' _system->copyRectToScreen(_screen.getPixels(), _screen.pitch, 0, 0, 640, 480);\n'+OVERLAY+'\n _system->updateScreen();\n}\nvoid AstronomicaEngine::redrawSprites()')
    return cpp,header
