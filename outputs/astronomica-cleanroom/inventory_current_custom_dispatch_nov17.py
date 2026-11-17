"""Catalogue current custom-dispatch source references without claiming execution coverage."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,re,struct,traceback
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=a.workspace.resolve();out=a.out.resolve();out.mkdir(exist_ok=False,parents=True)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 seal=read(w/'p513-control-music-seal-nov17.json');source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica/script.cpp';assert sha(source)==seal['engine_sha256']['script.cpp']
 inventory=w/'original-branches-nov6/inventory.json';inv=read(inventory);prior=read(w/'original-behavior-requirements-nov17/proof.json');assert prior['syntax_inventory_sha256']==sha(inventory)
 cpp=source.read_text();lex=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]')
 def block(text,signature):
  assert text.count(signature)==1;start=text.index(signature);depth=1
  for token in lex.finditer(text,start+len(signature)):
   if token[0]=='{':depth+=1
   elif token[0]=='}':
    depth-=1
    if not depth:return start,text[start:token.end()]
  raise AssertionError('Unterminated source block')
 execute_at,execute=block(cpp,'void ScriptRunner::execute(const Script &script, uint index, uint32 now) {')
 custom_at,custom=block(execute,'if (c.opcode == 23) {');at=execute_at+custom_at
 masked=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27',lambda m:''.join('\n'if c=='\n'else' 'for c in m[0]),custom)
 line=lambda offset:cpp[:at+offset].count('\n')+1
 mentions=collections.defaultdict(list)
 for m in re.finditer(r'c\.args\[0\]\s*==\s*(\d+)\b',masked):mentions[int(m[1])].append(line(m.start()))
 callbacks=collections.defaultdict(list)
 for m in re.finditer(r'(_\w+Handler)->(\w+)\s*\(',masked):callbacks[(m[1],m[2])].append(line(m.start()))
 commands=[c for c in inv['commands']if c['opcode']==23];counts=collections.Counter(c['args'][0]for c in commands);assert len(commands)==158 and len(counts)==27 and set(counts)-set(mentions)=={25}
 files={};rows=[]
 for c in commands:
  if c['scene']not in files:
   raw=(a.root/f"PLACES/P{c['scene']}/MEGAFILE.HYP").read_bytes();assert hashlib.sha256(raw).hexdigest()==next(s['sha256']for s in inv['scenes']if s['scene']==c['scene']);files[c['scene']]=raw
  assert struct.unpack_from('<7i',files[c['scene']],c['file_offset'])==(23,*c['args'])
  rows.append(dict(original_command_id=c['id'],scene=c['scene'],selector=c['args'][0],file_offset=c['file_offset'],explicit_equality_lines=mentions.get(c['args'][0],[]),admission_verified=False,runtime_effects_verified=False))
 local=out/'dispatch-source-map-local.json';local.write_text(json.dumps(dict(schema_version=1,rows=rows),indent=2)+'\n')
 receipt=dict(status='CURRENT_CUSTOM_DISPATCH_SOURCE_CATALOGUE_PASS',schema_version=1,at=datetime.now(timezone.utc).isoformat(),engine_release_commit=seal['published_commit'],script_source_sha256=sha(source),execute_normalized_text_sha256=hashlib.sha256(execute.encode()).hexdigest(),custom_dispatch_normalized_text_sha256=hashlib.sha256(custom.encode()).hexdigest(),custom_dispatch_start_line=line(0),custom_dispatch_end_line=line(len(custom)-1),syntax_inventory_sha256=sha(inventory),original_custom_commands=158,resource_selector_families=27,explicit_selector_equality_families=len(mentions),selectors_without_explicit_equality=[25],selector_rows=[dict(selector=n,original_commands=counts[n],scenes=sorted({c['scene']for c in commands if c['args'][0]==n}),explicit_equality_lines=mentions.get(n,[]),admission_verified=False,runtime_effects_verified=False)for n in sorted(counts)],handler_method_references=[dict(owner=owner,method=method,lines=lines)for(owner,method),lines in sorted(callbacks.items())],unique_handler_methods=len(callbacks),local_detail_sha256=sha(local),author_sha256=sha(Path(__file__)),engine_modified=False,framework_modified=False,native_rerun=False,acceptance_A03_complete=False,whole_game_completion_percent=None,limits=['Static source references in current ScriptRunner::execute custom-dispatch block only; not callback implementation or original native behavior proof','A selector mention does not establish scene admission,pointer readiness,reachable histories or completed runtime effects','Selector25 remains an implicit fallback in this source block; it is not marked as executed by this catalogue','Other native callbacks and callback-generated queues remain outside this bounded catalogue','Source lines refer to the pinned current script.cpp; per-command map remains local'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],'selectors',len(counts),'explicit',len(mentions),'handler methods',len(callbacks))
except Exception:
 (out/'failure.json').write_text(json.dumps(dict(status='FAILED',error=traceback.format_exc()),indent=2)+'\n');raise
