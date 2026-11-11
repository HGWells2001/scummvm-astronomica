
  if(navLoopProbe){
   struct Expected {int scene,cursor;};const Expected expected[]={{103,0},{103,2},{103,-1},{106,1},{108,1},{110,1},{44,3},{349,-1},{340,3},{201,-1},{341,3},{214,-1},{103,0},{103,0},{501,-1},{103,0},{navProbeOldScene,-1}};
   if(navProbePhase==0)navProbeOwner=_navigationCursors[0];
   bool ok=navProbeOwner&&_navigationCursors[0]==navProbeOwner&&navProbePhase<ARRAYSIZE(expected)&&_place==expected[navProbePhase].scene&&_navigationCursorIndex==expected[navProbePhase].cursor&&CursorMan.isVisible()&&!shouldQuit();
   const int waitingScene=navProbePhase==7?44:navProbePhase==9?340:navProbePhase==11?341:-1;
   const bool waiting=waitingScene>=0&&_place==waitingScene&&_runner.pendingCount()&&navProbeWaits<64;
   if(waiting){++navProbeWaits;debug("Contextual cursor deferred frame: WAIT (phase%u,P%d,pending%u,blocked%d)",navProbePhase,_place,_runner.pendingCount(),_runner.clicksBlocked());}
   else {
   debug("Navigation cursor player frame: %s (phase%u,P%d,cursor%d,visible%d)",ok?"PASS":"FAIL",navProbePhase,_place,_navigationCursorIndex,CursorMan.isVisible());
   auto click=[&](int x,int y){navProbeMouse(Common::EVENT_LBUTTONDOWN,x,y);navProbeMouse(Common::EVENT_LBUTTONUP,x,y);};
   if(!ok){debug("Navigation cursor player loop: FAIL");quitGame();}
   else switch(++navProbePhase){
    case 1:navProbeMouse(Common::EVENT_MOUSEMOVE,639,100);break;
    case 2:navProbeMouse(Common::EVENT_MOUSEMOVE,100,0);break;
    case 3:ok=loadPlace(106,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,100,0);break;
    case 4:click(100,0);break;
    case 5:navProbeKey(Common::KEYCODE_RIGHT);break;
    case 6:ok=loadPlace(44,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,300,300);break;
    case 7:click(300,300);break;
    case 8:ok=loadPlace(340,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,300,300);break;
    case 9:click(300,300);break;
    case 10:ok=loadPlace(341,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,300,300);break;
    case 11:click(300,300);break;
    case 12:ok=loadPlace(103,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,0,100);break;
    case 13:navProbeKey(Common::KEYCODE_F5);navProbeKey(Common::KEYCODE_ESCAPE);break;
    case 14:{navProbeSavedHash=navProbeGlobals();navProbeSavedCompleted=_puzzlesCompleted;ok=saveGameState(60,"Original contextual cursor real-loop round trip").getCode()==Common::kNoError;Common::InSaveFile*physical=_saveFileMan->openForLoading(getSaveStateName(60));ok=ok&&physical&&physical->readUint32BE()==MKTAG('A','S','V','M')&&physical->readUint32LE()==2;delete physical;if(ok)ok=loadPlace(501,false,true);navProbeMouse(Common::EVENT_MOUSEMOVE,0,100);break;}
    case 15:ok=loadGameState(60).getCode()==Common::kNoError&&_place==103&&navProbeGlobals()==navProbeSavedHash&&_puzzlesCompleted==navProbeSavedCompleted;navProbeMouse(Common::EVENT_MOUSEMOVE,0,100);break;
    case 16:if(navProbeOld){ok=loadGameState(navProbeOldSlot).getCode()==Common::kNoError&&_place==navProbeOldScene;navProbeMouse(Common::EVENT_MOUSEMOVE,0,100);break;}debug("Navigation cursor player loop: PASS (16 actual frames,three raw portal clicks,raw NAVmouse/key exits,F5menu,physical ASVM2roundtrip,original resources retained)");quitGame();break;
    default:debug("Navigation cursor player loop: PASS (17 actual frames,three raw portal clicks,raw NAVmouse/key exits,F5menu,physical ASVM2roundtrip,historical native file loadP%d,original resources retained)",navProbeOldScene);quitGame();break;
   }
   if(!ok&&!shouldQuit()){debug("Navigation cursor player loop: FAIL (setup transition)");quitGame();}
   }
  }
