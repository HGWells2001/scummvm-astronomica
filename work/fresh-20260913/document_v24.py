from pathlib import Path
import json,re
out=Path('outputs/astronomica-cleanroom');log=Path('work/fresh-20260913/runtime.log').read_text();rows=[dict(scene=int(p),accepted=int(a),total=int(t)) for p,a,t in re.findall(r'Astronomica puzzle coverage: P(\d+) entry=(\d+)/(\d+)',log)]
assert len(rows)==37
accepted=sum(r['accepted'] for r in rows);total=sum(r['total'] for r in rows)
(out/'evidence/puzzle-coverage.json').write_text(json.dumps(dict(metric='Static canRun validation of entry templates with audio enabled; not execution or playability',accepted=accepted,total=total,scenes=rows),indent=2))
p=out/'PUZZLE-SURVEY.md';s=p.read_text();s+='\n## Controllo nativo degli script\n\n'+f'{accepted} di {total} script di ingresso superano canRun, con audio abilitato e globali inizializzate. E un controllo preventivo dei comandi e dei riferimenti, non una prova di esecuzione o completamento. I clic, i trascinamenti e tutte le condizioni di avvio non sono misurati da questo rapporto.\n\n| Scena | Script che superano il controllo |\n|---|---:|\n'+''.join(f"| P{r['scene']} | {r['accepted']}/{r['total']} |\n" for r in rows);p.write_text(s)
p=out/'README.md';s=p.read_text();s=re.sub(r'Stato: 16 settembre 2026, revisione 23\. Progresso complessivo stimato: circa 45%\.\nLa percentuale.*?\n','Stato: 16 settembre 2026, revisione 24.\nLa precedente stima del 45% non era una misura verificata: viene sostituita dal rapporto PUZZLE-SURVEY.md. Nessun enigma completo e ancora verificato giocabile.\n',s,count=1);s+='''
## Revisione 24: ricognizione degli altri enigmi

Il rapporto PUZZLE-SURVEY.md copre 37 scene P501-P537, comprese varianti.
Elenca comandi mancanti, operazioni personalizzate, livelli e gestori di
trascinamento. I comandi immagini 20/49 compaiono in 18 scene ciascuno:
sono una priorita condivisa per il prossimo sviluppo.

La registrazione del successo e stata estesa a 29 scene verificate
nell'eseguibile originale, inclusi P501, P505, P510, P517 e P525.
Sono 29 associazioni scena/variabile, non 29 enigmi resi giocabili.
P506 e P531-P535 condividono la variabile globale 23. P513, P529 e P530
sono esclusi perche hanno effetti diversi. Test e compilazione passano,
compresa una prova del comando originale di successo del pulsante P517.
''';p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text();s+='''
## Successo condiviso e ricognizione: revisione 24

La mappa delle scene e derivata dalla tabella originale a 4:6c94 nel
sottocomando 25 di _do_custom. probe_success_map.py controlla l'impronta
dell'eseguibile, legge le destinazioni e verifica nei blocchi disassemblati
lo stesso offset globale nel confronto e nell'assegnazione, oltre alla
chiamata _puzzle_successful. evidence/success-map.json contiene le 29
associazioni comuni. Il motore passa all'interprete la scena verificata;
la variabile del successo non e piu fissata a 27.

Eccezioni lasciate escluse: P513 incrementa DS:0153 senza suono; P529
scrive anche il DWORD +0xfa (globale 60); P530 suona ma non incrementa
il contatore. P352/P359 non fanno nulla in questo ramo. P506 e le cinque
varianti P531-P535 puntano allo stesso handler e quindi alla globale 23.
Le associazioni non vengono dedotte dal numero della scena.

La verifica nativa normalizza un valore nonzero per tutte le 29 scene,
controllando tutte le 100 globali dopo ogni operazione e l'assenza di suoni
o conteggi ripetuti. Esegue inoltre il comando originale del clic dello
sprite 6 di P517 partendo da globale 33 zero, con suono e conteggio reali
nel mixer dummy; verifica condivisione P506/P533 ed esclusione dei tre
casi speciali. Tutte le precedenti verifiche restano attive.

survey_puzzles.py legge nuovamente i file originali P500-P537. Per i file
con coda extra valida il prefisso e registra la coda. La ricognizione
nativa misura separatamente canRun sui template di ingresso: non esegue
le sequenze, non misura tutti gli input e non dimostra completabilita.
I risultati riproducibili sono in puzzle-survey.json e in
 evidence/puzzle-coverage.json. Non viene assegnata una nuova percentuale
globale di completamento: la precedente era orientativa.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v23.py');s=p.read_text().replace('v23','v24');s=s.replace("assert 'ending verification: PASS'", "assert 'multi-puzzle success verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'ending verification: PASS'");s=s.replace("archive=out.parent/", "assert (base/'success-map-check.json').read_bytes() == (out/'evidence/success-map.json').read_bytes()\narchive=out.parent/");p.with_name('package_v24.py').write_text(s)
print('Validated script templates',accepted,'/',total)
