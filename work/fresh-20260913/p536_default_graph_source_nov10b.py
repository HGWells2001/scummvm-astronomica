"""Explore settled default-design controls by replaying only real original clicks."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_p536_graph")&&ConfMan.getBool("astronomica_verify_p536_graph")) {
  struct Node {Common::Array<uint> path;Common::Array<uint32> key;};Common::Array<Node>nodes;
  uint32 now=0;
  auto settle=[&](){for(uint n=0;n<20000&&_place==536&&_runner.pendingCount();++n){runScriptsAt(now);animateSpritesAt(now);now+=50;}return _place!=536||(!_runner.pendingCount()&&!_runner.clicksBlocked());};
  auto point=[&](uint id,int&hx,int&hy){
   hx=hy=-1;if(id<1||id>_scene.sprites.size())return false;const Sprite&s=_scene.sprites[id-1];
   Common::File f;if(!f.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P536/MEGAFILE.HYP"))))return false;
   const Frame*frame=staticSpriteFrame(_scene,id-1);Graphics::Surface*bmp=frame?decodeSpriteBitmap(f,frame->image,_screen.format):nullptr;if(!bmp)return false;const int right=int16(s.renderX+bmp->w),bottom=int16(s.renderY+bmp->h);bmp->free();delete bmp;
   for(int y=MAX(0,int(s.renderY));y<=MIN(479,bottom)&&hx<0;++y)for(int x=MAX(0,int(s.renderX));x<=MIN(639,right);++x)if(spriteAt(x,y)==int(id)-1){hx=x;hy=y;break;}return hx>=0;
  };
  auto press=[&](uint id){int x,y;if(!point(id,x,y)||_runner.clicksBlocked())return false;clickAtTime(x,y,now);return settle();};
  auto key=[&](Common::Array<uint32>&out){if(!_runner.exportPersistentState(out)||!_runner.scriptsIdle())return false;out[601]=0;for(const Sprite&s:_scene.sprites){if(s.autoFrame||s.autoMove||s.standardMotion||s.orbitMotion||s.planetMotion)return false;Common::Array<uint32>w;p526SpriteWords(s,w);w[8]=w[9]=0;for(uint32 v:w)out.push_back(v);}out.push_back(_puzzlesCompleted);for(char c:_displayedImageName)out.push_back(byte(c));return true;};
  auto replay=[&](const Common::Array<uint>&path){_runner.resetGlobals();_runner.seedRandom(1);ConfMan.setBool("astronomica_entry_scripts",true);if(!loadPlace(536))return false;now=scriptClock();if(!settle())return false;for(uint id:path)if(!press(id))return false;return true;};
  Node initial;if(!replay(initial.path)||!key(initial.key))return false;nodes.push_back(initial);uint edges=0,terminals=0;
  for(uint index=0;index<nodes.size();++index){if(nodes.size()>128)return false;const Node node=nodes[index];
   if(!replay(node.path))return false;Common::Array<uint32>again;if(!key(again)||again!=node.key)return false;
   Common::Array<uint>controls;for(uint id=1;id<=_scene.sprites.size();++id){int x,y;if(_scene.sprites[id-1].clickEnabled&&point(id,x,y))controls.push_back(id);}
   debug("P536 GRAPH NODE %u depth%u controls%u",index,node.path.size(),controls.size());
   for(uint id:controls){if(!replay(node.path)||!press(id))return false;++edges;if(_place!=536){debug("P536 GRAPH TERMINAL node%u control%u exitP%d",index,id,_place);++terminals;continue;}int32 project=-1,phase=-1,height=-1;if(!_runner.getValue(1,1,project)||!_runner.getValue(1,2,phase)||!_runner.getValue(1,4,height))return false;
    if(project!=2){debug("P536 GRAPH TERMINAL node%u control%u project%d phase%d height%d",index,id,project,phase,height);++terminals;continue;}
    Node next;next.path=node.path;next.path.push_back(id);if(!key(next.key))return false;uint target=0;while(target<nodes.size()&&nodes[target].key!=next.key)++target;
    if(target==nodes.size())nodes.push_back(next);debug("P536 GRAPH EDGE node%u control%u target%u project%d phase%d height%d",index,id,target,project,phase,height);
   }
  }
  debug("P536 default settled graph: PASS (%u nodes,%u original exposed-control edges,%u selected-project terminals;idle epochs normalized)",nodes.size(),edges,terminals);return loadPlace(103);
 }
'''
def inject(cpp,script):
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+'\n'+PROBE)
 anchor='   _lastTrue = result;';assert script.count(anchor)==1;script=script.replace(anchor,anchor+'\n   if(c.offset)debug("Astronomica condition trace: offset=%u scope=%d id=%d value=%d low=%d high=%d cmp=%d result=%d pending=%u",c.offset,c.args[0],c.args[1],v,c.args[2],c.args[3],c.args[4],int(result),_pending.size());')
 return cpp,script
