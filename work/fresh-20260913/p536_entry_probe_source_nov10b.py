"""Instrument the actual engine to exercise original exposed controls during startup."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_p536_entry")&&ConfMan.getBool("astronomica_verify_p536_entry")) {
  uint cases=0;
  for(uint quantum:{1U,10U,50U})for(uint ticks=0;ticks<=30;++ticks){
   _runner.resetGlobals();_runner.seedRandom(1);ConfMan.setBool("astronomica_entry_scripts",true);
   if(!loadPlace(536))return false;uint32 now=scriptClock();
   debug("P536 ENTRY CASE BEGIN q%u ticks%u",quantum,ticks);
   for(uint i=0;i<ticks;++i){runScriptsAt(now);animateSpritesAt(now);now+=quantum;}
   const Sprite&s=_scene.sprites[7];int hx=-1,hy=-1;
   for(int y=MAX(0,int(s.renderY));y<480&&hx<0;y+=2)for(int x=MAX(0,int(s.renderX));x<640;x+=2)if(spriteAt(x,y)==7){hx=x;hy=y;break;}
   if(hx<0||_runner.clicksBlocked()){debug("P536 ENTRY CASE SKIP q%u ticks%u blocked%d exposed%d",quantum,ticks,int(_runner.clicksBlocked()),hx>=0);continue;}
   debug("P536 ENTRY CLICK q%u ticks%u pending%u xy%d,%d",quantum,ticks,_runner.pendingCount(),hx,hy);
   clickAtTime(hx,hy,now);
   for(uint i=0;i<10000&&_place==536&&_runner.pendingCount();++i){runScriptsAt(now);animateSpritesAt(now);now+=quantum;}
   if(_place!=536||_runner.pendingCount()||_runner.clicksBlocked())return false;
   int32 project,phase,height;if(!_runner.getValue(1,1,project)||!_runner.getValue(1,2,phase)||!_runner.getValue(1,4,height))return false;
   debug("P536 ENTRY CASE END q%u ticks%u project%d phase%d height%d",quantum,ticks,project,phase,height);++cases;
  }
  debug("P536 entry timing verification: PASS (%u exposed original clicks,no scalar state injection)",cases);return loadPlace(103);
 }
'''
def inject(cpp,script):
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+'\n'+PROBE)
 anchor='   _lastTrue = result;';assert script.count(anchor)==1;script=script.replace(anchor,anchor+'\n   if(c.offset)debug("Astronomica condition trace: offset=%u scope=%d id=%d value=%d low=%d high=%d cmp=%d result=%d pending=%u",c.offset,c.args[0],c.args[1],v,c.args[2],c.args[3],c.args[4],int(result),_pending.size());')
 return cpp,script
