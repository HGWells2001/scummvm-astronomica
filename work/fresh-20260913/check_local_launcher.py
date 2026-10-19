"""Check the real launcher configuration without touching personal saves."""
from pathlib import Path
import configparser,hashlib,json,os,subprocess
base=Path('work/fresh-20260913').resolve();root=Path('outputs/astronomica-cleanroom').resolve()
folder=base/'launcher startup check';folder.mkdir(exist_ok=True)
template=root/'astronomica-play.ini';cfg=folder/'astronomica.ini';cfg.write_bytes(template.read_bytes())
c=configparser.ConfigParser();c.read(cfg)
assert c['astronomica']['path']=='D:/astro' and c['astronomica']['engineid']==c['astronomica']['gameid']=='astronomica'
for key in ('audio','animation','sprite_input','entry_scripts'):assert c.getboolean('astronomica','astronomica_'+key)
assert not any(k.startswith('astronomica_verify') or k=='astronomica_start_place' for k in c['astronomica'])
assert not c.getboolean('astronomica','astronomica_debug_overlay')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
exe=base/'build/Releasex64/scummvm.exe'
p=subprocess.run([str(exe),'--config='+str(cfg),'--list-targets'],env=env,capture_output=True,text=True,timeout=30)
assert p.returncode==0 and 'astronomica          Astronomica: The Quest' in p.stdout
log=folder/'startup.log'
p=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(folder),'--extrapath='+str(base/'fonts'),'--debuglevel=1','astronomica'],env=env,cwd=base,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
try:
 out=p.communicate(timeout=6)[0];raise AssertionError('Normal startup exited early: '+out[-1500:])
except subprocess.TimeoutExpired:
 p.terminate();out=p.communicate(timeout=10)[0]
(folder/'console.log').write_text(out)
s=log.read_text()
assert 'resource explorer: P1;' in s and 'FAIL' not in s and 'ERROR:' not in out
assert not any(p.suffix[1:].isdigit() for p in folder.glob('astronomica.*'))
proof=dict(date='2026-10-19',status='PASS',template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),target_listed=True,normal_P1_startup=True,no_verification_mode=True,personal_saves_untouched=True,headless_seconds=6,terminated_own_child=True,limitations='Native startup uses the launcher template directly. Batch paths reviewed; interactive GUI and full audiovisual playthrough remain manual.')
(root/'evidence/local-launcher-validation.json').write_text(json.dumps(proof,indent=2))
print('Launcher template and normal P1 startup PASS; personal saves untouched')
