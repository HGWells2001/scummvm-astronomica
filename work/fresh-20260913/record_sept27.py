"""Record this checkpoint only after its complete native test passes."""
import json,subprocess,sys
from pathlib import Path
subprocess.run([sys.executable,'work/fresh-20260913/save_development_evidence.py'],check=True)
root=Path('outputs/astronomica-cleanroom')
m=json.loads((root/'evidence/development-validation.json').read_text())
assert len(m['complete_route_scenes'])==25
note='''

## Sviluppo 27 settembre: meteorologia, montaggio e aggancio orbitale

Build locale e collaudo generale PASS. Nessun nuovo pacchetto/prototipo.
P512: 24576 combinazioni originali, sei scenari, tre regolazioni,
errori/recupero, successo ripetuto, uscita non risolta; sei segmenti di
FLATPHEN.MOV verificati anche a velocita reale. Opcode36 e custom24 attivi.
Correzione della ricerca: ShowMovie AVVIA il filmato (MCActionPlay8).
P515/P536: cinque configurazioni del razzo, due fasi, misura errata e
recupero, lancio verso P510 e conteggio solo al primo successo.
I cambi scena rispettano opcode49 inline; un frame oltre la fine viene
ignorato come in SWSetCurrentFrameIndex, mantenendo immagine e stato.
P514: due traiettorie da1000 passi confrontate con x86, 17161 regioni,
224 collisioni originali, tre velocita, limiti dei controlli, aggancio,
carburante esaurito, uscita volontaria e successo senza doppio conteggio.
Custom16/3 muove sprite20 ma confronta sprite19; usa cinque punti del
rettangolo bersaglio e cancella gli altri comandi pendenti al successo.
25 scene con percorsi automatici, incluse sei varianti di uno stesso
gruppo e due scene dello stesso puzzle di montaggio. Manuale solo P508.
La copertura statica non e una percentuale di giocabilita complessiva.
P513: sole prove originali per168 confronti, nessun supporto ancora attivo.
'''
for filename in ('README.md','INTERPRETER.md'):
    with (root/filename).open('ab') as f:f.write(note.encode('ascii'))
(root/'NEXT-STEPS.md').write_text('''# Checkpoint verificato 27 settembre

Build e collaudo generale PASS; prove e hash in evidence/development-validation.json.
25 scene con percorsi automatici. Conferma manuale solo P508. Non una
percentuale del gioco completo. Nessun pacchetto o prototipo nuovo.
Ultime integrazioni: P512, P515/P536 e P514; dettagli in INTERPRETER.md.

## Prossimo: P513
probe_p513_answers.py esegue custom10/1 originale:168 casi,126 normali,
hash0xa8180d31. Tabella scenario1..14 -> impostazione:
[7,2,2,2,8,1,8,7,6,2,5,9,4,5]. Impostazione3/scenario11 non accetta:
il salto originale prosegue senza successo; la risposta corretta e5.
Errore sotto risposta -> S10; sopra -> S11 (ID diretti).
Custom10/0 attiva sprite32, timer10ms, deltaX=10-local0, callback
_fxm_move_photon 3:06ee. All'arrivo (proposedX>442 e visibile) ferma32,
mostra9/10/11 e aggiorna tre cifre e uno degli sprite12..17.
probe_p513_motion.py verifica nove traiettorie e36 casi al bordo.
Output cifre per impostazione1..9:005,011,004,030,002,100,004,050,015.
Sprite risultato:12,13,14,14,15,15,16,16,17. Prove in p513-motion.json.
Il callback nasconde32, disabilita i due timer e azzera le velocita;
SWProcess applica comunque il punto gia calcolato in questo passo.
Otto casi di successo originale verificano global29 iniziale -1,0,1,2
e contatori0,29: incremento solo quando global29==0, nessuna chiamata audio.
Custom25 P513 4:5808 incrementa il contatore senza suono comune e pone
global29. Non presente ancora nella mappa del motore; non usare handler
di successo con S12. Sette risposte corrette O maschera16383 vincono;
dieci errori escono verso P197. Quattro template e32sprites, un livello.
Materiale originale in evidence/p513-answers.json e
evidence/p513-scripts.json (pulsanti, tempi, template e fotogrammi),
work/fresh-20260913/interpreter/_fxm_move_photon.asm.

## Limiti e verifiche
Restano altri puzzle, navigazione, aiuti e salvataggi.
P512 custom24/2: rewind a fine segmento nel motore; comportamento implicito
del controller originale ancora da provare isolatamente.
P514 prova dedicata check_p514.py. Completa runtime_test.py timeout600sec.
save_development_evidence.py salva solo dopo PASS; record_sept27.py
aggiunge questo checkpoint. Non usare record_sept26.py o record_evening.py.
''')
print('Sept27 checkpoint saved',m['entry_template_validation'])
