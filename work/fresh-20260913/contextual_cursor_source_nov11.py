"""Add only original group4 contextual indicator in its exact three-scene _dnav zone."""
PORTAL_TEST=r'''
 const int portalScenes[]={44,340,341},portalTargets[]={349,201,214};
 for(uint scene=0;scene<3;++scene){
  if(!quiet(portalScenes[scene]))return false;uint32 hash=2166136261U,count=0;
  {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();for(int y=0;y<480;++y)for(int x=0;x<640;++x){updateNavigationCursor(x,y);const uint value=_navigationCursorIndex==3;count+=value;hash=(hash^value)*16777619U;}if(p510WholeLiveHash()!=before)return false;}
  if(hash!=706905629U||count!=15096)return false;
  updateNavigationCursor(300,300);if(_navigationCursorIndex!=3)return false;clickAtTime(300,300,scriptClock());runScriptsAt(scriptClock());if(_place!=portalTargets[scene])return false;updateNavigationCursor(300,300);if(_navigationCursorIndex==3)return false;
 }
 for(int other:{103,106,117}){if(!quiet(other))return false;updateNavigationCursor(300,300);if(_navigationCursorIndex==3)return false;}
 debug("Contextual down cursor verification: PASS (three original scenes,921600 OS-oracle points,exact _dnav zone,three original portal scripts,other-room fallback,no fourth NAVaxis)");
'''
def production(cpp,header):
 begin=cpp.index('void AstronomicaEngine::clearNavigationCursors()');end=cpp.index('void AstronomicaEngine::clickAt(int x, int y)',begin);methods=cpp[begin:end]
 methods=methods.replace('i<3','i<4').replace('_navigationCursors[0]&&_navigationCursors[1]&&_navigationCursors[2]','_navigationCursors[0]&&_navigationCursors[1]&&_navigationCursors[2]&&_navigationCursors[3]').replace('groupIds[]={2,1,3}','groupIds[]={2,1,3,4}').replace('groups[3]={}','groups[4]={}')
 anchor=' if(direction>=0&&!ensureNavigationCursors())direction=-1;';assert methods.count(anchor)==1
 methods=methods.replace(anchor,' // _place_loop9:0f50-0fc8: contextual down arrow follows ordinary NAVhover.\n if((_place==44||_place==340||_place==341)&&x>=192&&x<414&&y>=252&&y<320)direction=3;\n'+anchor)
 cpp=cpp[:begin]+methods+cpp[end:]
 begin=cpp.index('bool AstronomicaEngine::verifyNavigationCursors()');end=cpp.index('bool AstronomicaEngine::verifyBuilderPuzzle()',begin);test=cpp[begin:end]
 test=test.replace('expectedHotX[]={0,6,31}','expectedHotX[]={0,6,31,6}').replace('expectedHotY[]={6,0,6}','expectedHotY[]={6,0,6,31}').replace('0x11480b87U};','0x11480b87U,0x51cc9907U};').replace('i<3','i<4')
 anchor=' debug("Navigation cursor verification: PASS';assert test.count(anchor)==1;test=test.replace(anchor,PORTAL_TEST+'\n'+anchor).replace('three exact original resources','four exact original resources')
 cpp=cpp[:begin]+test+cpp[end:]
 assert header.count('Graphics::WinCursorGroup *_navigationCursors[3]')==1;header=header.replace('Graphics::WinCursorGroup *_navigationCursors[3]','Graphics::WinCursorGroup *_navigationCursors[4]')
 return cpp,header
