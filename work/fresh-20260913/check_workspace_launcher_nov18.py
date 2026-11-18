"""Exercise visible launch failures and real native success from a path containing spaces."""
from pathlib import Path
from datetime import datetime,timezone
import configparser,hashlib,json,os,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];out=w/'launcher-check-nov18';out.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();launcher=r/'Avvia-Astronomica.cmd';pin=sha(launcher)
missing=out/'missing build';missing.mkdir();shutil.copyfile(launcher,missing/launcher.name)
bad=subprocess.run(['cmd.exe','/d','/c',str(missing/launcher.name)],cwd=out,input='\n',capture_output=True,text=True)
(out/'missing-console.log').write_text(bad.stdout+bad.stderr)
assert bad.returncode==1 and 'Eseguibile corrente non trovato:'in bad.stdout and 'Questa finestra resta aperta'in bad.stdout
good=out/'real native build';good.mkdir();shutil.copyfile(launcher,good/launcher.name);binary=good/'work/fresh-20260913/build/Releasex64';binary.mkdir(parents=True);(good/'work/fresh-20260913/fonts').mkdir()
for name in('scummvm.exe','SDL2.dll'):os.link(w/'build/Releasex64'/name,binary/name)
template=good/'outputs/astronomica-cleanroom/astronomica-play.ini';template.parent.mkdir(parents=True)
template.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astronomica]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=1\nastronomica_verify_startup_sequence=true\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
result=subprocess.run(['cmd.exe','/d','/c',str(good/launcher.name)],cwd=out,env=env,input='\n',capture_output=True,text=True)
(out/'success-console.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
native=good/'userdata/astronomica/astronomica.log';console=good/'userdata/astronomica/avvio-console.log';assert 'Startup sequence: PASS'in native.read_text(errors='replace') and 'Codice di uscita: 0'in console.read_text(errors='replace')
config=good/'userdata/astronomica/astronomica.ini';config.write_text(config.read_text()+'\n[launcher-sentinel]\nkeep=unchanged\n')
again=subprocess.run(['cmd.exe','/d','/c',str(good/launcher.name)],cwd=out,env=env,input='\n',capture_output=True,text=True);assert again.returncode==0
settings=configparser.ConfigParser();settings.read(config);assert settings['launcher-sentinel']['keep']=='unchanged'
assert sha(launcher)==pin and sha(binary/'scummvm.exe')==sha(w/'build/Releasex64/scummvm.exe') and not list((good/'userdata/astronomica/saves').iterdir())
receipt=dict(status='WORKSPACE_LAUNCHER_NATIVE_AND_FAILURE_PASS',at=datetime.now(timezone.utc).isoformat(),launcher_sha256=pin,exe_sha256=sha(binary/'scummvm.exe'),missing_executable_exit_code=bad.returncode,missing_executable_message_held=True,real_native_exit_code=result.returncode,path_with_spaces=True,existing_configuration_preserved=True,native_startup_log_sha256=sha(native),console_log_sha256=sha(console),source_engine_changed=False,limits=['Missing-build error and two real native controlled startup exits;normal interactive exploration is verified separately','Does not establish the original cause of the reported Explorer double-click failure'])
(out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
