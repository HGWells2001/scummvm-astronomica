from pathlib import Path
import json
r=Path('outputs/astronomica-cleanroom');j=json.loads((r/'evidence/help-format.json').read_text());h=2166136261

def raw(b):
 global h
 for c in b:h=((h^c)*16777619)&0xffffffff

def word(x):raw((x&0xffffffff).to_bytes(4,'little'))
for rec in j['records']:
 word(rec['kind']);word(len(rec.get('columns',[])))
 for col in rec.get('columns',[]):word(col['width']);word(col['gap'])
 for p in rec['paragraphs']:
  if rec['kind']==35:word(p['column'])
  word(p['text_offset']);word(p['flags']);word(p['indent']);word(len(p['tabs']))
  for t in p['tabs']:word(t['position']);word(t['alignment'])
  cursor=p['text_offset']
  for c in p['commands']:
   b=c['text'].encode('cp1252');word(c['opcode']);word(cursor);word(len(b));raw(b);cursor+=len(b)+1
   if c['opcode']==0x80:word(c['font'])
   if c['opcode']==0x86:word(c['image'])
 if rec['kind']==35:word(65535)
j['semantic_hash_fnv32']=f'{h:08x}';(r/'evidence/help-format.json').write_text(json.dumps(j,indent=2));print('Semantic hash',hex(h))
p=r/'engine/astronomica/astronomica.cpp';s=p.read_text();m=' struct SearchCase { const char *query; uint count; uint32 hash; };';s=s.replace(m,f''' debug("Astronomica help format: %u records, %u commands, %08x",_helpBook.formatRecords,_helpBook.formatCommands,_helpBook.formatHash);
 ok = _helpBook.formatRecords == 1335 && _helpBook.formatCommands == 11455 && _helpBook.formatHash == 0x{h:08x}U && ok;
'''+m);p.write_text(s);Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_bytes(p.read_bytes())
d=json.loads((r/'evidence/help-compression.json').read_text());a=-1
for x in d['records']:
 if x['kind']==2:a+=1;title=x['text']
 elif x['kind']==35:print('First table',a,title);break
