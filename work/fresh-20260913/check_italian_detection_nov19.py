from pathlib import Path
import subprocess,json,hashlib,shutil,configparser
w=Path(__file__).resolve().parent;s=w/'italian-detection-nov19-stage';d=w/'italian-detection-tests-nov19';d.mkdir(exist_ok=False);exe=s/'bin/scummvm.exe';results=[]
def detect(root,lang,label):
 cfg=d/(label+'.ini');p=subprocess.run([str(exe),'--config='+str(cfg),'--path='+str(root),'--add','--game=astronomica'],capture_output=True,text=True);(d/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
 c=configparser.ConfigParser();c.read(cfg,encoding='utf-8');games=[c[x]for x in c.sections()if c[x].get('gameid')=='astronomica'];assert len(games)==1,(label,p.stdout,p.stderr);assert games[0].get('language')==lang,(label,dict(games[0]));results.append(dict(case=label,language=lang,gameid=games[0]['gameid']))
detect(Path('D:/astroita'),'it','original-italian');detect(Path('D:/astro'),'en','original-english')
for folder,root,lang in [('neutral-a','D:/astroita','it'),('neutral-b','D:/astro','en')]:
 dst=d/folder
 for n in ['PLACES/GAMEDATA','PLACES/P1/MEGAFILE.HYP']:
  q=dst/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path(root)/n,q)
 shutil.copyfile(Path(root)/'SETUP/ASTRO.EXE',dst/'ASTRO.EXE')
 detect(dst,lang,folder)
# Incomplete data must not silently claim English based on common files.
root=d/'incomplete';root.mkdir();shutil.copyfile(Path('D:/astroita/SETUP/ASTRO.EXE'),root/'ASTRO.EXE');shutil.copyfile(Path('D:/astroita/PLACES/GAMEDATA'),root/'GAMEDATA')
cfg=d/'incomplete.ini';p=subprocess.run([str(exe),'--config='+str(cfg),'--path='+str(root),'--add','--game=astronomica'],capture_output=True,text=True);c=configparser.ConfigParser();c.read(cfg,encoding='utf-8');assert not any(c[x].get('gameid')=='astronomica'for x in c.sections());results.append(dict(case='incomplete-common-files',game_added=False))
proof=dict(status='ITALIAN_ENGLISH_ACTUAL_DETECTOR_PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),cases=results,original_data_modified=False)
(d/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'])
