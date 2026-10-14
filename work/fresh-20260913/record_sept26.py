"""Record the Sept 26 engine only after its complete native suite passes."""
from pathlib import Path
import subprocess
import sys

root = Path('outputs/astronomica-cleanroom')
subprocess.run([sys.executable,'work/fresh-20260913/save_development_evidence.py'],check=True)
note = '''

## 26 settembre 2026: P526 integrato nel motore

P526 supera le prove native del percorso completo: sei scenari senza
ripetizione, risposte corrette, successo ripetuto senza doppio conteggio,
uscita dopo quattro errori e uscita volontaria. Global42 e ritorno a P268.
Custom13 configura l'orbita e controlla la risposta sul fotogramma corrente
di sprite18, prima della condizione successiva nello stesso script.

Il movimento riproduce _fxm_eclipse e la parte di _fxm_move_ellipse usata
da P526. La conversione 1:15c3 tronca sqrt prima del rapporto dei raggi.
Sono conservati ordine dei callback, alternanza davanti/dietro, cambio
dei raggi nello scenario3 e normalizzazione del fotogramma all'arresto.
Il confronto nativo coincide con 24 traiettorie ottenute eseguendo oltre
4 milioni di istruzioni originali in probe_p526_motion.py. I timer e le
funzioni SpriteWorld esterne sono modellati nella sonda, non emulati.
probe_p526_answers.py verifica 588 combinazioni normali e 294 casi di
confine dello scenario; l'originale sceglie la tabella solo con scenario>4.
Verificati anche ordine sincrono della risposta e rifiuto fuori contesto.

Compilazione e suite completa PASS; prove e hash in
evidence/development-validation.json. Ventuno scene hanno percorsi completi
verificati automaticamente, comprese sei varianti dello stesso gruppo.
Conferma manuale ancora soltanto P508. Il dato statico resta 98/121 (81.0%)
con animazione disabilitata: non misura il completamento del gioco intero.
Nessun nuovo prototipo, launcher, ZIP o aggiornamento del pacchetto v34.

P512: nuova sonda probe_p512_weather.py esegue tutte le 24.576 combinazioni
delle tre regolazioni (0..15) per i sei scenari originali. Verifica anche
la priorita delle voci d'errore S12/S11/S10 e i sei segmenti FLATPHEN.MOV.
Custom24 e il percorso completo P512 restano da integrare; questa prova
di ricerca non incrementa il numero di scene completabili.
'''
for name in ('README.md','INTERPRETER.md'):
    p = root/name
    if b'## 26 settembre 2026: P526 integrato nel motore' not in p.read_bytes():
        with p.open('ab') as f: f.write(note.encode('ascii'))
with (root/'PUZZLE-SURVEY.md').open('a') as f: f.write(note)
(root/'NEXT-STEPS.md').write_text('''# Stato aggiornato al 26 settembre 2026

Compilazione e suite completa PASS. Manifest con hash e log aggiornato in
evidence/development-validation.json. Canonico engine/astronomica; mirror
work/fresh-20260913/scummvm/engines/astronomica. Eseguibile locale in
work/fresh-20260913/build/Releasex64/scummvm.exe. Nessun pacchetto aggiornato.

21 scene con percorsi automatici completi, incluse sei varianti dello
stesso gruppo; conferma manuale solo P508. Copertura statica 98/121=81.0%
senza animazione, non una percentuale di giocabilita complessiva.

## Ultima integrazione: P526
Custom13 e moto orbitale. Verifica nativa: 24 traiettorie originali,
588 risposte, ordine sincrono frame/risposta, due soluzioni complete,
quattro errori e uscita volontaria. Global42, destinazione P268.
Sonde probe_p526_answers.py e probe_p526_motion.py; prove in evidence/.
Il moto e limitato al caso P526: non dichiarare implementata tutta la
callback _fxm_move_ellipse, che contiene anche comportamenti P514.

## Prossimo lavoro: P512
probe_p512_weather.py interpreta 24.576 combinazioni di custom24/0.
Tabella e pulsanti originali: evidence/p512-weather.json.
Locale4 scenario, locali0/1/2 regolazioni, locale5 risultato.
Scenari: 1=[0..8,0..8,15]; 2/3/4=[15,0..8,0..8];
5=[0..8,15,0..8]; 6=[0..8,15,15]. Primo valore errato in ordine
locale0,1,2 riproduce direttamente S12,S11,S10. Voce S14 sincrona.
Custom24/1 -> ShowMovie a160,57 senza avviare; /2 -> StartMovie;
/3 -> fxm_UpdateMovie (disegno del frame corrente).
Opcode36 -> SetMovieTimeValue, da aggiungere separatamente dal playback.
Opcode37 gia implementato: segmento attivo e seek iniziale.
FLATPHEN.MOV: segmenti [0,150],[150,204],[1272,184],[1456,186],
[1642,189],[1834,85], in unita della scala temporale del filmato.
La selezione tramite maschera locale3 usa63 e poi127 come sentinella:
verificare il numero effettivo di conferme prima della vittoria, senza
assumere che bastino sei risposte. Uscita risolta verso P157, global28.
Disassemblati ShowMovie, StartMovie, SetMovieTimeValue e custom24 nel
direttorio work/fresh-20260913/interpreter. Non c'e codice P512 nuovo.

Restano altri puzzle, navigazione, aiuti e salvataggi.
Verifica completa: work/fresh-20260913/runtime_test.py (timeout360s).
Verifica P526: work/fresh-20260913/check_p526.py.
Non usare record_evening.py: scriverebbe lo stato precedente del25settembre.
''')
print('Sept 26 development state recorded; no package generated.')
