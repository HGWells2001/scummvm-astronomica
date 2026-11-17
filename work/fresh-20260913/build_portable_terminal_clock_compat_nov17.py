"""Compile the accepted cleanroom engine against the user's all-engine framework in isolation."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;s=w/'portable-terminal-clock-compat-nov17-stage';s.mkdir(exist_ok=False)
b=Path('D:/00/_BUILD_SCUMMVM_ALL_VS');stock=Path('D:/00/SCUMMVM-ALL-SRC');portable=Path('D:/00/_SCUMMVM_PORTATILE')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=w/'portable-audio-restore-nov17-stage';parent_proof=read(parent/'proof.json')
src=s/'source/engines/astronomica';src.mkdir(parents=True);(s/'bin').mkdir()
for n,h in parent_proof['engine_sha256'].items():
 assert sha(parent/'source/engines/astronomica'/n)==h;shutil.copyfile(parent/'source/engines/astronomica'/n,src/n)
from p525_terminal_clock_compat_source_nov17 import production
p=src/'astronomica.cpp';h=src/'astronomica.h';cpp,header=production(p.read_text(),h.read_text());p.write_text(cpp);h.write_text(header)
pin=sha(portable/'scummvm.exe');assert pin=='e73a9ecdca25193c6b01804722c6e6623c9f7ccb1950fa2e68e3da963ae70d77'
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdkroot=Path('C:/Program Files (x86)/Windows Kits/10');sdk=sdkroot/'Include/10.0.26100.0'
env={k.upper():v for k,v in os.environ.items()}
env['INCLUDE']=';'.join(map(str,[msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt']))
env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64']))
env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
def replace(text,old,new):return re.sub(re.escape(str(old)),lambda m:str(new),text,flags=re.I)
def blocks(path):
 groups=[]
 for line in path.read_text(encoding='utf-16').splitlines():
  if line.startswith('^'):groups.append([])
  elif groups:groups[-1].append(line)
 return ['\n'.join(g)for g in groups]
def run(tool,command,label):
 rsp=s/(label+'.rsp');rsp.write_text(command)
 result=subprocess.run([str(msvc/'bin/Hostx64/x64'/(tool+'.exe')),'@'+str(rsp)],cwd=b,env=env,capture_output=True,text=True)
 (s/(label+'.log')).write_text(result.stdout+result.stderr);result.check_returncode()
commands=blocks(b/'Releasex64/astronomica/astronomica.tlog/CL.command.1.tlog');assert len(commands)==7
objects=[]
for name in ('astronomica','conditions_test','help','metaengine','resource','script','sprites'):
 c=next(c for c in commands if c.upper().rstrip().endswith('\\'+name.upper()+'.CPP'))
 c=replace(c,stock/'engines/astronomica'/(name+'.cpp'),src/(name+'.cpp'))
 c=re.sub(r'/Fo"[^"]+"',lambda m:'/Fo"'+str(s/(name+'.obj'))+'"',c,flags=re.I)
 c=re.sub(r'/Fd"[^"]+"',lambda m:'/Fd"'+str(s/(name+'.pdb'))+'"',c,flags=re.I)
 c='/I"'+str(s/'source/engines')+'" '+c
 run('cl',c,'cl-'+name);objects.append(s/(name+'.obj'))
run('lib','/NOLOGO /OUT:"'+str(s/'bin/astronomica.lib')+'" '+' '.join('"'+str(p)+'"'for p in objects),'lib')
print('PORTABLE_EFFECT_MIX_SEVEN_FRESH_UNITS_PASS; link separately')
