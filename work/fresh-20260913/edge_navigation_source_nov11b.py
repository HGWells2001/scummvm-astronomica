"""Restore original mode1 mouse edge navigation after sprite/rectangle consumption."""
GEOMETRY=r'''
// Original _do_place9:013a-0171 SetRect constants; _do_mouse9:1328-13e3.
// Serialized NAV order is left,top,right (_load_place9:15e2-1622).
static int navigationDirectionAt(int x,int y) {
 if(x>=-20&&x<50&&y>=50&&y<270)return 0;
 if(x>=590&&x<660&&y>=50&&y<270)return 2;
 if(x>=50&&x<590&&y>=-20&&y<50)return 1;
 return -1;
}
'''
TEST=r'''
bool AstronomicaEngine::verifyEdgeNavigation() {
 auto quiet=[&](int place){ConfMan.setBool("astronomica_entry_scripts",false);return loadPlace(place,false,true);};
 uint32 hash=2166136261U,counts[4]={};
 for(int y=0;y<480;++y)for(int x=0;x<640;++x){const int direction=navigationDirectionAt(x,y);if(direction<-1||direction>2)return false;const uint value=direction+1;++counts[value];hash=(hash^value)*16777619U;}
 // Independent current-Windows PtInRect oracle on constants decoded from original SetRect calls.
 if(hash!=3123994245U||counts[0]!=258200||counts[1]!=11000||counts[2]!=27000||counts[3]!=11000)return false;
 debug("Edge navigation geometry: PASS (307200 OS-oracle points,hash%08x)",hash);
 struct Edge {int x,y,expected;};const Edge boundaries[]={{-20,50,0},{-21,50,-1},{49,269,0},{50,269,-1},{0,270,-1},{590,50,2},{659,269,2},{660,50,-1},{590,49,-1},{50,-20,1},{589,49,1},{50,-21,-1},{50,50,-1},{-20,49,-1}};
 for(const Edge&e:boundaries)if(navigationDirectionAt(e.x,e.y)!=e.expected)return false;
 struct Route {int scene,x,y,destination;};const Route routes[]={{103,0,100,101},{106,100,0,108},{103,639,100,98}};
 for(const Route&r:routes){if(!quiet(r.scene)||_runner.clicksBlocked()||spriteAt(r.x,r.y)!=-1)return false;clickAtTime(r.x,r.y,scriptClock());if(_place!=r.destination)return false;}
 debug("Edge navigation live routes: PASS (left P103to101,top P106to108,right P103to98)");
 if(!quiet(103))return false;
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();for(const Edge&e:boundaries)if(e.expected<0){clickAtTime(e.x,e.y,scriptClock());if(p510WholeLiveHash()!=before)return false;}clickAtTime(100,0,scriptClock());if(p510WholeLiveHash()!=before)return false;}
 // Actual original P27 button script establishes opcode28 input lock.
 if(!quiet(27)||_scene.sprites.empty())return false;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP"))))return false;
 const Frame*f=staticSpriteFrame(_scene,0);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return false;
 const int bx=_scene.sprites[0].renderX+bmp->w/2,by=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;
 if(spriteAt(bx,by)!=0)return false;clickAtTime(bx,by,scriptClock());runScriptsAt(scriptClock());if(!_runner.clicksBlocked()||!_runner.pendingCount())return false;
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();for(const Route&r:routes){clickAtTime(r.x,r.y,scriptClock());if(p510WholeLiveHash()!=before)return false;}}
 debug("Edge navigation input lock: PASS (actual P27 block/pending queue,all live state preserved)");
 // Controlled overlap moves the exact original P103 rectangle/script to an edge.
 if(!quiet(103)||_scene.mouseRects.size()!=1)return false;
 MouseRect&r=_scene.mouseRects[0];r.rect[0]=0;r.rect[1]=50;r.rect[2]=50;r.rect[3]=270;
 clickAtTime(10,100,scriptClock());if(_place!=103||!_runner.pendingCount())return false;runScriptsAt(scriptClock());if(_place!=126)return false;
 if(!quiet(103))return false;MouseRect&empty=_scene.mouseRects[0];empty.rect[0]=0;empty.rect[1]=50;empty.rect[2]=50;empty.rect[3]=270;empty.click.clear();
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();clickAtTime(10,100,scriptClock());if(p510WholeLiveHash()!=before)return false;}
 // An original bitmap provides real sprite geometry; diagnostic position/flags exercise precedence.
 if(!quiet(117)||_scene.sprites.size()!=1)return false;Sprite&s=_scene.sprites[0];s.renderX=0;s.renderY=50;s.clickEnabled=true;s.clickType=1;
 if(spriteAt(1,51)!=0)return false;
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();clickAtTime(1,51,scriptClock());if(p510WholeLiveHash()!=before)return false;}
 if(!quiet(117))return false;Sprite&disabled=_scene.sprites[0];disabled.renderX=0;disabled.renderY=50;disabled.clickEnabled=false;disabled.dragEnabled=false;clickAtTime(1,51,scriptClock());if(_place!=122)return false;
 debug("Edge navigation priority: PASS (original rectangle script,empty rectangle,unsupported sprite consume edge hits;fully disabled sprite permits navigation;controlled overlaps)");
 if(!quiet(103))return false;_scene.mode=0;
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();clickAtTime(0,100,scriptClock());if(p510WholeLiveHash()!=before)return false;}
 // Reuse the already reconstructed original transition gate rather than bypassing it.
 if(!quiet(101)||!_runner.defineValue(0,57,0))return false;clickAtTime(100,0,scriptClock());if(_place!=429)return false;
 if(!quiet(101)||!_runner.defineValue(0,57,1))return false;clickAtTime(100,0,scriptClock());if(_place!=110)return false;
 debug("Edge navigation transition gates: PASS (P101top denied429/permitted110)");
 debug("Edge navigation verification: PASS (original geometry,three live exits,lock,consumption,mode and transition gates)");return true;
}
'''
BASELINE=r'''
 if(ConfMan.hasKey("astronomica_verify_edge_navigation_baseline")&&ConfMan.getBool("astronomica_verify_edge_navigation_baseline")) {
  ConfMan.setBool("astronomica_entry_scripts",false);bool ok=loadPlace(103,false,true)&&!_runner.clicksBlocked()&&_nav[0]==101&&spriteAt(0,100)==-1;
  if(ok){clickAtTime(0,100,scriptClock());ok=_place==103;}
  debug("Edge navigation pre-fix counterexample: %s (P103 left-zone click staysP%d despite original destination101;previous native engine,not original Windows)",ok?"PASS":"FAIL",_place);
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def production(cpp,header,guard=True):
 anchor='void AstronomicaEngine::clickAt(int x, int y) {';assert cpp.count(anchor)==1
 if guard:
  cpp=cpp.replace(anchor,GEOMETRY+'\n'+anchor)
  anchor=' for (uint i = 0; i < _scene.mouseRects.size(); ++i) {\n  const MouseRect &r = _scene.mouseRects[i];\n  if (x >= r.rect[0] && y >= r.rect[1] && x < r.rect[2] && y < r.rect[3]) {'
  assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,' bool rectangleHit = false;\n'+anchor+'\n   rectangleHit = true;')
  anchor='\n }\n}\nuint32 AstronomicaEngine::scriptClock() const {';assert cpp.count(anchor)==1
  cpp=cpp.replace(anchor,'\n }\n // Original _in_mr consumes rectangle hits even when their command list is empty.\n if (!rectangleHit && _scene.mode == 1) {\n  const int direction = navigationDirectionAt(x,y);\n  if (direction >= 0 && _nav[direction] != 0) changePlace(_nav[direction]);\n }\n}\nuint32 AstronomicaEngine::scriptClock() const {')
  anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,TEST+'\n'+anchor)
  anchor=' void handleGameKey(const Common::KeyState &key);';assert header.count(anchor)==1;header=header.replace(anchor,' bool verifyEdgeNavigation();\n'+anchor)
 branch=''' if(ConfMan.hasKey("astronomica_verify_edge_navigation")&&ConfMan.getBool("astronomica_verify_edge_navigation")) {
  const bool ok=verifyEdgeNavigation();debug("Edge navigation native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''if guard else BASELINE
 anchor=' if(ConfMan.hasKey("astronomica_verify_keyboard")';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,branch+'\n'+anchor)
 return cpp,header
