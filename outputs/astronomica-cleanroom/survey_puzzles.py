"""Survey original puzzle-area resources; opcode presence is not playability."""
import argparse,collections,json,re
from pathlib import Path
from astro_reader import parse,FormatError
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--runtime-log',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
known={1,2,3,4,5,6,7,9,10,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,33,35,36,37,39,40,41,42,45,46,47,48,49,51}
def walk(x):
 if isinstance(x,dict):
  if 'opcode' in x: yield x
  else:
   for v in x.values(): yield from walk(v)
 elif isinstance(x,list):
  for v in x: yield from walk(v)
rows=[];blockers=collections.defaultdict(list)
for place in range(500,538):
 p=args.root/f'PLACES/P{place}/MEGAFILE.HYP'
 if not p.exists(): continue
 b=p.read_bytes(); trailing=0
 try:
  try: scene=parse(b)
  except FormatError as e:
   match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e))
   if not match: raise
   trailing=int(match[1]);scene=parse(b[:int(match[2],16)])
 except Exception as e:
  rows.append(dict(scene=place,error=str(e)));continue
 commands=list(walk(scene));unsupported=sorted({c['opcode'] for c in commands}-known)
 for op in unsupported: blockers[op].append(place)
 custom=sorted({c['args'][0] for c in commands if c['opcode']==23})
 rows.append(dict(scene=place,commands=len(commands),entry_scripts=len(scene['scripts']),sprites=len(scene['sprites']),drag_handlers=sum(bool(s.get('drag')) for s in scene['sprites']),layers=scene['layers'],unsupported_opcode_ids=unsupported,custom_operations=custom,trailing_bytes=trailing,status='Completabile: non verificato'))
args.out.mkdir(parents=True,exist_ok=True)
(args.out/'puzzle-survey.json').write_text(json.dumps(dict(scope='Existing resources P500..P537, not one scene per distinct puzzle',rows=rows,opcode_scene_counts={str(k):len(v) for k,v in blockers.items()}),indent=2))
lines=['# Ricognizione delle scene degli enigmi','', 'Risorse originali P500-P537. P537 ha ora i lanci del razzo verificati tramite clic, comprese entrambe le impostazioni riuscite e i casi errati. P527 ha selezioni e uscite verificate con tempo accelerato e seek; ora anche i quattro segmenti continui sono verificati separatamente. Le scene includono varianti: non equivalgono al numero di enigmi distinti. P505 ha otto risposte e tre errori verificati tramite clic; il successivo filmato P520 ha ora supporto dedicato e transizione verificata verso P537. P509 ha soluzione delle due fasi e uscita dopo tre errori verificate tramite clic dalla revisione 33. P511 ha due ordini di soluzione e uscita senza successo verificati tramite clic originali. P508 Astronomy vs Astrology ha due percorsi completi verificati tramite input simulato nel motore: otto risposte corrette e uscita dopo tre errori. Non e una prova manuale nella finestra di gioco. La presenza di un opcode supportato non garantisce che i suoi argomenti, lo script o le interazioni siano supportati.','', '| Scena | Comandi | Livelli | Trascinamenti | Opcode mancanti | Operazioni personalizzate |','|---|---:|---:|---:|---|---|']
for r in rows:
 if 'error' in r: lines.append(f"| P{r['scene']} | errore lettura | | | | |");continue
 lines.append(f"| P{r['scene']} | {r['commands']} | {r['layers']} | {r['drag_handlers']} | {', '.join(map(str,r['unsupported_opcode_ids'])) or '-'} | {', '.join(map(str,r['custom_operations'])) or '-'} |")
lines += ['', 'Frequenza dei comandi mancanti (numero di scene): '+', '.join(f'{k}: {len(v)}' for k,v in sorted(blockers.items())), '', 'Stato delle prove: P29 ha una sequenza di lampeggio completa verificata; P510 ha prove parziali di pulsanti, audio e uscite; P511 ha anche due soluzioni complete e uscita senza successo verificate tramite clic dalla revisione 31; la vecchia prova della sola sequenza finale resta separata. Queste prove precedenti non sono soluzioni integrali; dalla revisione 27 P508 ha anche prove complete di risposte corrette e di tre errori.']
lines += ['', 'Aggiornamento 25 settembre: P517 ha quattordici impostazioni, animazioni e uscite risolta/non risolta verificate tramite clic. P519 ha cinque abbinamenti in due ordini, errore, lampo bianco e uscita non risolta verificati. Dopo P521, P528 e P530, tredici scene di puzzle hanno percorsi completi verificati automaticamente (P505, P508, P509, P511, P517, P519, P521, P525, P527, P528, P529, P530, P537). P521 verifica cinque scelte e dieci frammenti in movimento. P528 verifica le 48 posizioni della Luna e i due ordini di eclissi. P530 verifica tre turni senza ripetizioni e il successo senza incremento del contatore. Per P525/P527/P529 sono disponibili anche prove separate dei dodici segmenti video continui, senza seek accelerato. Non e una percentuale della giocabilita complessiva.']
lines += ['', 'Aggiornamento 25 settembre, sera: P518 ora verificato con nove pianeti, errore e recupero, due direzioni e uscita non risolta. P506/P531-P535 verificati in sette percorsi di quattro scene, tre varianti senza ripetizione, successo ripetuto senza doppio conteggio e voce globale S22. Sono venti scene con percorsi completi automatici: le sei varianti appartengono allo stesso gruppo, percio non sono venti puzzle distinti. La conferma manuale resta solo P508.']
lines += ['', 'Aggiornamento 27 settembre: P512 verificato nei sei scenari e nei sei filmati continui; P515/P536 verificati nelle due fasi di montaggio con cinque configurazioni, errore e recupero. P514 verificato con due traiettorie originali di 1000 passi, 17161 classificazioni angolari, 224 collisioni, tre velocita, aggancio, carburante esaurito e uscita non risolta. Totale: 25 scene con percorsi automatici, non 25 puzzle distinti. Conferma manuale solo P508. P513 resta ricerca, non supporto abilitato.']
lines += ['', 'Aggiornamento 28 settembre: P513 verificato nelle quattordici domande, nove animazioni, successo silenzioso, dieci errori e uscita. Totale: 26 scene di puzzle con percorsi automatici. P507 ha inoltre selezione zodiacale, dodici immagini, suono, toggle e due uscite verificati; e una scena interattiva, non un altro puzzle risolto. P522 resta ricerca originale, non attivo nel motore.']
lines += ['', 'Aggiornamento 30 settembre: P522 verificato con calendario1991..2003, sei traiettorie originali di lancio, quattro controlli, errore/recupero, successo ripetuto, scadenza e uscita. P524 verificato nelle nove immagini/risposte, aiuto con stato ripristinato, tre errori e uscita. Totale28 scene di puzzle con percorsi automatici, oltre P507 interattiva; non28 puzzle distinti. Conferma manuale solo P508.']
lines += ['', 'Aggiornamento 1 ottobre: P501 verificato con nove traiettorie originali e 3600 transizioni, undici percorsi tramite pulsanti: cinque ambienti, colpo/presa su Vesta, vittoria ripetuta, presa prematura, scadenze, tre errori e uscita. Totale29 scene di puzzle con percorsi automatici, oltre P507 interattiva; non29 puzzle distinti. Conferma manuale solo P508.']
lines += ['', 'Aggiornamento 2 ottobre: P516 e P510 integrati,34 scene con percorsi automatici. P510 verificato in432 casi originali e otto percorsi; anche un percorso vincente con filmato continuo. Conferma manuale solo P508. Non e una percentuale di completamento del gioco.']
lines += ['', 'Aggiornamento 4 ottobre: P523 integrato,35 scene con percorsi automatici. Aiuto/ritorno P523 e cinque mentori P408 verificati;170 selezioni video e ritorni da37 scene. Libro di aiuto Windows, salvataggi e percorso integrale restano da completare. Conferma manuale solo P508.']
(args.out/'PUZZLE-SURVEY.md').write_text('\n'.join(lines)+'\n')
print('Scenes:',len(rows),'blockers:',{k:len(v) for k,v in sorted(blockers.items())})

if args.runtime_log:
    coverage=[dict(scene=int(p),accepted=int(a),total=int(t)) for p,a,t in re.findall(r'Astronomica puzzle coverage: P(\d+) entry=(\d+)/(\d+)',args.runtime_log.read_text())]
    assert len(coverage)==len(rows)
    accepted=sum(r['accepted'] for r in coverage);total=sum(r['total'] for r in coverage)
    (args.out/'evidence/puzzle-coverage.json').write_text(json.dumps(dict(metric='Static canRun validation, audio enabled, animation disabled; not execution/playability',accepted=accepted,total=total,scenes=coverage),indent=2))
    with (args.out/'PUZZLE-SURVEY.md').open('a') as f:
        f.write('\n## Controllo nativo degli script\n\n'+f'{accepted}/{total} template superano canRun. Non e una percentuale di gioco completabile, ne una prova di esecuzione.\n\n| Scena | Template validati |\n|---|---:|\n')
        for r in coverage:f.write(f"| P{r['scene']} | {r['accepted']}/{r['total']} |\n")
        f.write('\nGli opcode 20/49 supportano caricamento e visualizzazione separati, anche attraverso diramazioni e attese. Restano necessari file BMP decodificabili e scene a un livello. P508 script 1 e verificato sulle 18 varianti, non equivale alla soluzione completa del puzzle.\n')
    print('Native validation:',accepted,'/',total)
