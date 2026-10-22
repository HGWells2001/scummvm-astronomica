"""Build the real staged engine in isolation; run only the original P522 native observation audit."""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess

root = Path(__file__).resolve().parents[2]
work = Path(__file__).resolve().parent
stage = work/'p522-audit'
out = stage/'candidate-build'
out.mkdir(exist_ok=True)
canonical = root/'outputs/astronomica-cleanroom/engine/astronomica'
running = work/'build/Releasex64/scummvm.exe'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {p.name:digest(p) for p in canonical.iterdir() if p.is_file()}
assert len(before) == 23
running_hash = digest(running)
overrides = json.loads((stage/'BASE.json').read_text())
assert len(overrides) == 6 and all((stage/name).is_file() for name in overrides)
assert all(before[name] == expected for name,expected in overrides.items()), 'Stage BASE must match the canonical engine'
stage_hashes = {name:digest(stage/name) for name in overrides}
include = out/'include/astronomica'
include.mkdir(parents=True, exist_ok=True)
for p in canonical.glob('*.h'):
    shutil.copyfile(stage/p.name if p.name in overrides else p, include/p.name)
msvc = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231')
sdkroot = Path('C:/Program Files (x86)/Windows Kits/10')
sdk = sdkroot/'Include/10.0.26100.0'
env = {k.upper():v for k,v in os.environ.items()}
env['INCLUDE'] = ';'.join(str(p) for p in [msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt'])
env['LIB'] = ';'.join(str(p) for p in [msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64',work/'SDL2-2.32.6/lib/x64'])
env['PATH'] = str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')

def run(command, log, timeout):
    with (out/log).open('w') as stream:
        result = subprocess.run(command,cwd=work/'build',env=env,stdout=stream,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    assert result.returncode == 0, (log,result.returncode)
    print(log+' PASS',flush=True)

try:
    lines = (work/'build/Releasex64/astronomica/astronomica.tlog/CL.command.1.tlog').read_text(encoding='utf-16').splitlines()
    flags = next(line for line in lines if line.startswith('/c '))
    flags = flags[:flags.rfind('  C:')]
    flags = re.sub(r'/Fo"[^"]*"|/Fd"[^"]*"','',flags)
    objects = []
    for p in sorted(canonical.glob('*.cpp')):
        source = stage/p.name if p.name in overrides else p
        obj = out/(p.stem+'.obj')
        rsp = out/(p.stem+'.rsp')
        rsp.write_text('/I"'+str(include.parent)+'" '+flags+' /Fo"'+str(obj)+'" /Fd"'+str(out/'engine.pdb')+'" "'+str(source)+'"\n')
        run([str(msvc/'bin/Hostx64/x64/cl.exe'),'@'+str(rsp)],p.stem+'-compile.log',300)
        objects.append(obj)
    lib = out/'astronomica.lib'
    rsp = out/'archive.rsp'
    rsp.write_text('/NOLOGO /OUT:"'+str(lib)+'"\n'+'\n'.join('"'+str(p)+'"' for p in objects)+'\n')
    run([str(msvc/'bin/Hostx64/x64/lib.exe'),'@'+str(rsp)],'archive.log',180)
    lines = (work/'build/Releasex64/scummvm/scummvm.tlog/link.command.1.tlog').read_text(encoding='utf-16').splitlines()
    link = '\n'.join(line for line in lines if line and not line.startswith('^'))
    for flag,name in [('OUT','scummvm.exe'),('PDB','scummvm.pdb'),('LTCGOUT','scummvm.iobj'),('IMPLIB','scummvm.lib')]:
        pattern = r'/'+flag+r':(?:"[^"]*"|\S+)'
        assert len(re.findall(pattern,link,re.I)) == 1
        link = re.sub(pattern,lambda m:'/'+flag+':"'+str(out/name)+'"',link,flags=re.I)
    old = str(work/'build/Releasex64/astronomica.lib')
    assert link.upper().count(old.upper()) == 1
    link = re.sub(re.escape(old),lambda m:str(lib),link,flags=re.I)
    rsp = out/'link.rsp'; rsp.write_text(link+'\n')
    run([str(msvc/'bin/Hostx64/x64/link.exe'),'@'+str(rsp)],'link.log',1200)
    shutil.copyfile(work/'SDL2-2.32.6/lib/x64/SDL2.dll',out/'SDL2.dll')
    config = out/'probe.ini'
    config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_probe_boundaries=true\nsavepath='+out.as_posix()+'\n')
    env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='dummy'
    logfile=out/'probe-boundaries.log'
    run([str(out/'scummvm.exe'),'--config='+str(config),'--extrapath='+str(work/'fonts'),'--savepath='+str(out),'--logfile='+str(logfile),'--debuglevel=1','astro-verify'],'probe-console.log',300)
    text = logfile.read_text()
    assert 'FAIL' not in text and 'Astronomica probe boundary result: PASS' in text and 'PASS' in text and 'Log closed successfully' in text
    print('\n'.join(line for line in text.splitlines() if 'probe boundary' in line.lower() or 'P522 route' in line),flush=True)
    result = dict(status='PASS',canonical_files=len(before),canonical_sha256=before,regression_exe_sha256=running_hash,candidate_exe_sha256=digest(out/'scummvm.exe'),stage_sha256=stage_hashes,compiled_sources=len(objects),probe_log=str(logfile),diagnostic_only=True)
finally:
    assert before == {p.name:digest(p) for p in canonical.iterdir() if p.is_file()}, 'Canonical source changed'
    assert running_hash == digest(running), 'Regression executable changed'
    assert stage_hashes == {name:digest(stage/name) for name in overrides}, 'Staged source changed'
    print('Canonical 23 files, six staged sources and regression executable unchanged',flush=True)
if 'result' in globals():
    (out/'proof.json').write_text(json.dumps(result,indent=2))
    print('Isolated real-engine candidate and P522 observation audit PASS',flush=True)
