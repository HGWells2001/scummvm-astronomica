from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
try:
 for name,marker in [('intro.log','intro verification: PASS'),('logo.log','logo verification: PASS'),('postcredits.log','post-credits verification: PASS'),('endings.log','ending continuous playback: PASS')]:
  log=(work/name).read_text();assert marker in log and 'FAIL' not in log,(name,marker)
 subprocess.run([sys.executable,str(work/'runtime_test.py')],check=True)
 log=(work/'runtime.log').read_text();assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
 for marker in ('intro verification: PASS','logo verification: PASS','post-credits verification: PASS','post-credits P432 continuous: PASS','post-credits P433 continuous: PASS','ending continuous playback: PASS'):assert marker in log,marker
 (root/'evidence/postcredits-validation.json').write_text(json.dumps(dict(status='PASS',scenes=[432,433,0],continuous_movies=[432,433],motion_and_stop=True,timed_transitions=True,logo_menu_and_exit=True,full_suite=True,manual_confirmation=False),indent=2))
 (root/'evidence/intro-validation.json').write_text(json.dumps(dict(status='PASS',scenes=[1,2,3,4],new_game_click=True,card_images=9,p4_redirect=True,palette_adaptation='RGB24 Cinepak needs no Win16 display-palette change; original palette BMP validated',timed_transitions=True,continuous_intro=False,full_suite=True,manual_confirmation=False),indent=2))
 for name in ('intro','logo','postcredits','endings'):shutil.copyfile(work/(name+'.log'),root/'evidence'/(name+'-runtime.log'))
 note="\n\n## Intro and logo checkpoint, 10 October 2026\n\nThe new-game click, P2/P4 movies and nine P3 cards now reach exploration27.\nP4 reads its movie fromP2 as the original loader specifies. Opcode50's\nWin16 display palette is adapted to native RGB rendering: both original\nCinepak video descriptions are24-bit. Its original OPEN2_B must decode,\nthe movie and screen must be RGB, and other contexts/names fail closed.\nLogo0 handles state61=0/2 returning to menu and1 quitting after20000ms.\nQuit accepts trailing condition closures only; following effects still fail.\nP432/P433 moving text, stops, movie frames and continuous playback pass.\nThe prior full-suite failure was P423 reaching19.475s of video at the26s\nwall deadline. The test now allows50s but still requires natural completion;\nnew diagnostics record wall/media/end times. Full regression PASS.\nIntro continuous playback and manual audiovisual review remain unverified.\nEvidence:probe_intro_logo.py, intro-logo-original.json and runtime logs.\n"
 for name in ('README.md','INTERPRETER.md','P409-RESEARCH.md'):
  p=root/name
  if b'## Intro and logo checkpoint, 10 October 2026' not in p.read_bytes():
   with p.open('ab') as f:f.write(note.encode('ascii'))
 p=root/'NEXT-STEPS.md';s=p.read_text().replace('# Ripresa: P409 e conto alla rovescia integrati, 5 ottobre 2026','# Ripresa: introduzione, post-crediti e logo integrati, 10 ottobre 2026')
 a=s.index('Prossimo:coda432/433/0');b=s.index('Restano filmati esplorazione',a)
 s=s[:a]+"P432/P433:movimento, stop e playback continuo PASS. P0:logo/menu/uscita PASS.\nP1->P2->P3->P4->P27:pulsante nuova partita, filmati e nove immagini PASS.\nPalette50:adattamento RGB documentato in P409-RESEARCH.md.\nProssimo:playback continuo introduzione e filmati mondo29/82/222/231.\nRicerca:probe_world_interactions.py e evidence/world-interactions.json.\nOpcode35 azzera DS:01d1; custom29 chiama UpdateGame/SWUpdateSpriteWorld.\nVerificare il vincolo del cursore e il blit finale prima di integrare i filmati mondo.\nTest:check_intro.py,check_logo.py,check_postcredits.py,check_endings.py.\n"+s[b:]
 s=s.replace('record_advice_checkpoint.py','finish_oct10.py');p.write_text(s,encoding='utf-8')
 for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
 (root/'RUN-IN-PROGRESS.md').write_text('Complete native suite and checkpoint integrity PASS: intro, post-credits and logo integrated. Resume from NEXT-STEPS.md.\n')
 print('October10 checkpoint PASS')
except Exception:
 (root/'RUN-IN-PROGRESS.md').write_text('October10 full suite or checkpoint failed; inspect runtime.log and finish_oct10.py before further development.\n');raise
