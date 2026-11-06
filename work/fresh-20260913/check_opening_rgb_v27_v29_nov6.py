"""Bounded genuine prior-save checks on the exact physical/fresh P525 candidate.

--inventory-only reads frozen manifests and authors a plan; never launches.
Ordinary mode requires both actual physical producer and fresh-process PASS.
It runs genuine v27 once, v28 four times, v29 six times. Other available
frozen versions are inventoried, never silently counted as tested.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,configparser,hashlib,json,os,re,struct,subprocess,sys,traceback

ap=argparse.ArgumentParser();ap.add_argument('--inventory-only',action='store_true');a=ap.parse_args()
w=Path(__file__).resolve().parent
s=w/'opening-rgb-nov6-stage';exe=s/'complete-build/bin/scummvm.exe'
out=w/'opening-rgb-genuine-v27-v29-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent_pins={
 'check_frozen_p510_v28.py':'e49b06b7399d9f3363794abc936e28742fa81eb6a86e65b92c4384f530828b2d',
 'check_frozen_p512_v29.py':'b9c2890c883e8d4bf3ff9499c7328fc2917c421101a3ec1b97732757a13ed64d'}
scene_for_version={14:'rocket',15:'universe',16:'probe',17:'rendezvous',18:'planet',
 19:'p521',20:'p509',21:'p511',22:'p516',23:'p527',24:'p502',25:'p503',26:'p504',27:'p501'}

def inventory():
 rows=[]
 for manifest in sorted((w/'verified-checkpoints').glob('*/frozen*slot*.json')):
  m=json.loads(manifest.read_text())
  if not m.get('status','').startswith('FROZEN_VERIFIED_V'):continue
  number=m.get('slot')
  if number is None:number=int(re.search(r'slot(\d+)$',manifest.stem).group(1))
  path=manifest.parent/manifest.stem/('astro-verify.%03d'%number)
  assert path.is_file(),str(path)
  raw=path.read_bytes();assert raw[:4]==b'ASVM' and len(raw)>=8
  version=struct.unpack_from('<I',raw,4)[0]
  assert d(path)==m['slot_sha256'] and m.get('origin_commit') and m.get('producing_exe_sha256')
  cfg=w/('verify-%s-saves.ini'%scene_for_version[version]) if version in scene_for_version else None
  rows.append(dict(version=version,slot=number,manifest=str(manifest),manifest_sha256=d(manifest),
   path=str(path),slot_sha256=d(path),status=m['status'],origin_commit=m['origin_commit'],
   producing_exe_sha256=m['producing_exe_sha256'],bytes=len(raw),
   existing_config=str(cfg)if cfg and cfg.exists()else None,
   existing_config_sha256=d(cfg)if cfg and cfg.exists()else None,
   planned_execution='v27_original_false_entry'if version==27 else'v28_v29_exact_muted_derivation'if version in(28,29)else'inventory_only_not_run'))
 present=sorted({row['version']for row in rows})
 return dict(search_boundary='work/fresh-20260913/verified-checkpoints/*/frozen*slot*.json only',
  artifacts=rows,available_versions=present,
  no_genuine_manifest_in_boundary=[v for v in range(1,30)if v not in present],
  planned_tested_versions=[27,28,29],available_but_not_in_this_runtime_matrix=[v for v in present if v<27],
  limitations=['A missing manifest in this bounded search does not prove no historical save exists elsewhere',
   'Manifest identity is checked against preserved raw file; current regenerated roundtrips are never labeled genuine prior inputs'])

inv=inventory()
for name,pin in parent_pins.items():assert d(w/name)==pin;ast.parse((w/name).read_text())
if a.inventory_only:
 receipt=dict(status='AUTHOR_INVENTORY_ONLY_NO_NATIVE',created_at=datetime.now(timezone.utc).isoformat(),
  driver_sha256=d(Path(__file__)),parent_checker_sha256=parent_pins,inventory=inv,processes_started=0,
  expected_future_gates=['OPENING_RGB_ONLY_DELTA_REVIEW_PASS','P523_ASVM31_COMPLETE_SIX_FRESH_PROCESSES_PASS'])
 (w/'p523-complete-prior-versions-nov5-inventory.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],inv['available_versions']);raise SystemExit(0)

review=s/'source-review-proof.json';fresh=w/'opening-rgb-fresh-nov6/proof.json'
r=json.loads(review.read_text());f=json.loads(fresh.read_text())
assert r['status']=='OPENING_RGB_ONLY_DELTA_REVIEW_PASS'
assert f['status']=='P523_ASVM31_COMPLETE_SIX_FRESH_PROCESSES_PASS'
assert r['candidate_exe_sha256']==f['candidate_exe_sha256']==d(exe)
assert f['stage_sha256']==f['stage_sha256']=={n:d(s/n)for n in f['stage_sha256']}
assert f['source_physical_proof_sha256']==d(s/'complete-build/native-proof.json')
expected=d(exe);own=d(Path(__file__))
review_pin=d(review);fresh_pin=d(fresh)
out.mkdir(exist_ok=False)

def state(value,**fields):
 (out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),
  updated_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=expected,main_modified=False,
  public_support=False,**fields),indent=2)+'\n')

def validate():
 assert d(exe)==expected and d(Path(__file__))==own
 assert f['stage_sha256']=={n:d(s/n)for n in f['stage_sha256']}
 assert parent_pins=={n:d(w/n)for n in parent_pins}
 assert f['source_physical_proof_sha256']==d(s/'complete-build/native-proof.json')
 assert d(review)==review_pin and d(fresh)==fresh_pin
 for row in inv['artifacts']:
  assert d(Path(row['path']))==row['slot_sha256'] and d(Path(row['manifest']))==row['manifest_sha256']

try:
 state('RUNNING_PRIOR_VERSIONS')
 derived={}
 for version,parent_name in [(28,'check_frozen_p510_v28.py'),(29,'check_frozen_p512_v29.py')]:
  validate()
  original=(w/parent_name).read_text()
  # Only insert mute=true into the literal generated [scummvm] config.
  # All source identity, native result and immutable-file assertions stay exact.
  old='[scummvm]'+chr(92)+'n';new=old+'mute=true'+chr(92)+'n'
  assert original.count(old)==1
  modified=original.replace(old,new,1)
  assert modified.count(new)==1 and modified.replace(new,old,1)==original
  ast.parse(modified)
  helper=w/('check_opening_rgb_prior_v%d_muted_nov5.py'%version);assert not helper.exists()
  helper.write_bytes(modified.encode('utf-8'))
  directory=out/('genuine-v%d'%version)
  subprocess.run([sys.executable,str(helper),'--exe',str(exe),'--out',str(directory)],cwd=w.parents[1],check=True,timeout=4000)
  proof=directory/('frozen-v%d-proof.json'%version);p=json.loads(proof.read_text())
  assert p['status']=='PASS' and p['exe_sha256']==expected and p['actual_audio_driver']=='wasapi'
  assert len(p['cases'])==(4 if version==28 else 6)
  assert d(helper)==hashlib.sha256(modified.encode()).hexdigest()
  derived[version]=dict(parent_checker=parent_name,parent_sha256=parent_pins[parent_name],
   helper=str(helper),helper_sha256=d(helper),only_delta='Generated global mute=true',
   proof_sha256=d(proof),fresh_processes=len(p['cases']))
  validate()
 # Use the exact original v27 fresh-startup case already used by P512 closure.
 row=next(row for row in inv['artifacts']if row['version']==27 and row['slot']==26)
 assert row['slot_sha256']=='adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
 cfg_source=w/'verify-p501-saves.ini';cfg_hash=d(cfg_source)
 cfg=configparser.ConfigParser(interpolation=None);cfg.read(cfg_source)
 assert cfg['astro-verify'].getboolean('astronomica_verify_p501_saves')
 assert not cfg['astro-verify'].getboolean('astronomica_entry_scripts')
 cfg['scummvm']['mute']='true';cfg['scummvm']['autosave_period']='0'
 cfg['astro-verify']['savepath']=Path(row['path']).parent.as_posix()
 config_path=out/'genuine-v27.ini'
 with config_path.open('w')as stream:cfg.write(stream)
 env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
 log=out/'genuine-v27.log'
 command=[str(exe),'--config='+str(config_path),'--extrapath='+str(w/'fonts'),
  '--savepath='+str(Path(row['path']).parent),'--logfile='+str(log),'--debuglevel=1','--save-slot=26','astro-verify']
 validate()
 with(out/'genuine-v27-console.log').open('w')as stream:
  result=subprocess.run(command,cwd=w,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=240)
 text=log.read_text()
 assert result.returncode==0 and 'P501 startup save: PASS'in text and 'FAIL'not in text
 assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
 assert text.rstrip().endswith('--- Log closed successfully.') and d(cfg_source)==cfg_hash
 validate()
 receipt=dict(status='P523_COMPLETE_BOUNDED_GENUINE_PRIOR_V27_V28_V29_PASS',completed_at=datetime.now(timezone.utc).isoformat(),
  driver_sha256=own,candidate_exe_sha256=expected,stage_sha256=f['stage_sha256'],
  physical_native_review_sha256=d(review),physical_fresh_proof_sha256=d(fresh),
  inventory=inv,derived_checkers=derived,v27_case=dict(slot=26,entry_scripts=False,
   frozen_manifest_sha256=row['manifest_sha256'],slot_sha256=row['slot_sha256'],
   source_config_sha256=cfg_hash,config_sha256=d(config_path),log_sha256=d(log)),
  tested_versions=[27,28,29],fresh_processes=11,audio_driver='wasapi',mute=True,
  all_inventory_artifacts_unchanged=True,main_modified=False,public_support=False,
  limitations=['Only genuinev27/v28/v29 executed, not all1..29',
   'Availablev14..26 are inventoried/planned only; versions1..13 have no genuine manifest in the bounded search',
   'Broader general native suite and canonical/public integration remain separate',
   'Silent real-device timing, no listening or sample-phase parity'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:
 state('FAILED',error=traceback.format_exc());raise
