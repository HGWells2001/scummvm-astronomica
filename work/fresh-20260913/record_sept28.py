"""Record verified September 28 additions without rewriting historic encodings."""
from pathlib import Path
import json,hashlib
root=Path('outputs/astronomica-cleanroom');m=json.loads((root/'evidence/development-validation.json').read_text())
assert m['date']=='2026-09-28' and m['runtime_exit']==0 and len(m['complete_route_scenes'])==26
note='''

## Sviluppo 28 settembre: fotoni e ruota zodiacale

Build locale e collaudo generale PASS. Nessun nuovo pacchetto/prototipo.
P513: custom10/0 e10/1 attivi. Confronto con126 risposte originali e
nove traiettorie; quattordici scenari, limiti1..9, sette risposte corrette,
maschera completa, dieci errori, uscita volontaria e successo ripetuto.
Custom25 incrementa solo al primo successo e non riproduce S12.
P507: custom11 usa l'ultimo clic accettato. Verificati68121 punti originali,
dodici immagini e settori, S6, annulus30..122 inclusivo, clic bloccati,
indicatore alternato e uscite P508/P388. E una scena interattiva separata.
26 scene di puzzle con percorsi automatici, oltre P507. Manuale solo P508.
Validazione statica106/121 (87.6%): non percentuale di gioco completabile.
P522: ricerca originale, non ancora abilitato. Calendario1991..2003,
un lancio fallito e cinque finestre favorevoli eseguiti dalle istruzioni
originali; prove in evidence/p522-motion.json. I tick della ricerca non
sono ancora una verifica del tempo reale o dei quattro controlli.
Verificati anche66 casi di collisione e108 di correzione della sonda.
'''
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Sviluppo 28 settembre: fotoni' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'NEXT-STEPS.md').write_text('''# Checkpoint verificato 28 settembre

Build e collaudo generale PASS. Manifest con hash in
[evidence/development-validation.json](evidence/development-validation.json).
26 scene di puzzle con percorsi automatici, piu P507 interattiva.
Manuale solo P508. Nessuna percentuale affidabile del gioco completo.
Nessun nuovo pacchetto/prototipo; eseguibile nella build locale.

## Ultime integrazioni
P513: quattordici domande, nove impostazioni e animazioni; risposte originali
[7,2,2,2,8,1,8,7,6,2,5,9,4,5]. Successo globale29 senza suono S12;
sette corrette O tutte le domande selezionate; dieci errori e uscita P197.
P507: ruota zodiacale, dodici settori, immagini e S6; selezione dipendente
dall'ultimo clic non bloccato. Centro444,165, raggi30..122 inclusivi.
Helper astrologyRegion condiviso con P514, entrambe le prove PASS.
Prove dedicate check_p513.py e check_p507.py. runtime_test.py completo PASS.

## Prossimo: P522, sonda verso Marte
probe_p522_motion.py esegue i callback x86 originali e custom15/1.
Calendario: primo cambio anno al tick388, poi ogni340, uscita2003 al4128.
Hash0xd9ecccf1 con pianeti15/16 e sonda17 che segue Terra quando local1=0.
Anno/mese favorevoli:1992/8,1994/10,1997/0,1999/3,2001/5 (indici originali).
Lanci testati:1991/8 fallisce; cinque favorevoli raggiungono local1=2.
File evidence/p522-motion.json, work/fresh-20260913/p522-original.json e
interpreter/_fxm_move_probe*.asm, interpreter/p522-custom15.asm.
La ricerca usa i callback in ordine15/16/17 a passi fissi: non prova ancora
la temporizzazione del gioco o l'effetto dei quattro controlli local0.
Custom15/0: centro300,140, raggi120/60 (Terra/sonda) o226/113 (Marte),
passo2/0, movimento30ms, frame80ms; inizializzazione sonda resetta anno1991,
flag cambio anno e flag hit; null callback fino al lancio.
Terra aggiorna mese=(8-region+12)%12, regione300/20; mese1 arma cambio,
mese0 incrementa anno. Sonda cresce a226/113, incrementi2/1 quando x%10==0
con moto orizzontale o y%5==0 verticale. Marte corregge posizione della
sonda di un pixel per asse se local1=1, hit speciale e raggio>173.
Alla fine, flag hit oppure una delle quattro punte di Marte dentro sonda
produce local1=2; altrimenti nasconde sonda, callback nullo, raggi120/60,
local1=0. Originale non ferma gli altri movimenti al successo.
Template0 ciclico ogni200ms osserva local1=2, attende3000 custom25,
poi3500 prima di P388. Verificati66 casi di collisione e108 di correzione,
con soglia raggio173/174, flag hit e stati0/1/2.
Restano integrazione, input, tempi e prove native.

## Limiti
Altri puzzle, navigazione, aiuti e salvataggi ancora incompleti.
P512 rewind a fine segmento presente; comportamento implicito del controller
originale ancora da verificare isolatamente. Copertura statica106/121 con
animazioni disattivate; non misura la giocabilita.
Salvare nuove prove con save_development_evidence.py solo dopo PASS;
non rieseguire vecchi record_sept27/26/evening che sovrascrivono lo stato.
''')
files=sorted(root.glob('probe_*.py'))+sorted((root/'evidence').glob('p5*.json'))+[root/'evidence/builder.json']
manifest={'date':'2026-09-28','scope':'Original-file research; P507/P513 enabled and separately validated; P522 research only','sha256':{str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
manifest['original_inputs_sha256']={name:hashlib.sha256((Path('D:/astro')/name).read_bytes()).hexdigest() for name in ('SETUP/ASTRO.EXE','PLACES/P507/MEGAFILE.HYP','PLACES/P513/MEGAFILE.HYP','PLACES/P522/MEGAFILE.HYP')}
(root/'evidence/research-sept28.json').write_text(json.dumps(manifest,indent=2))
print('September28 checkpoint recorded')
