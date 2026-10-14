from pathlib import Path
import subprocess,sys
subprocess.run([sys.executable,'work/fresh-20260913/save_development_evidence.py'],check=True)
root=Path('outputs/astronomica-cleanroom')
summary = """

## 25 settembre, sera: P518 e gruppo P506/P531-P535

P518 implementato: caricamento del movimento ordinario del lanciatore,
aggancio e rilascio dei nove pianeti, rimbalzo e arresto alle soglie originali.
Due soluzioni complete (entrambe le direzioni), errore e recupero, limiti del
selettore, zero e uscita non risolta verificati attraverso clic. Suoni diretti
S9/S10, global34 e contatore verificati. Il timer runtime resta separato dal
parametro riutilizzato dal gioco. Prove aggiuntive sui bordi delle soglie e
sul cambio di velocita del lanciatore.

Custom17 implementato per P506 e P531-P535. Dopo la scena iniziale seleziona
tre varianti senza ripetizioni fra sei. La scena iniziale puo ricomparire.
Contatore e maschera sono variabili persistenti fra scene, inizializzate a
zero e azzerate al termine della sequenza originale. Successo global23,
S12 solo al primo completamento, poi sempre S22 globale sincrono e passaggio
a P519 dopo 3000 ms. La voce introduttiva e soppressa quando il contatore
e maggiore di uno. Sette percorsi di quattro scene, sei partenze diverse,
successo ripetuto e uscita normale superati nella suite nativa.

Compilazione e suite integrale PASS. Venti scene hanno percorsi completi
verificati automaticamente, non venti puzzle distinti: sei sono varianti
dello stesso gruppo. Conferma manuale solo P508. Copertura statica 98/121
(81.0%), misurata con audio abilitato e animazione disabilitata. P518 valida
3/3 template nella prova interattiva con animazione. Nessuna percentuale
globale di completamento affidabile. Nessun nuovo pacchetto o prototipo.

P526 resta da implementare: probe_p526_answers.py interpreta direttamente
588 combinazioni della logica originale e salva la tabella di accettazione.
Il movimento orbitale resta necessario prima di poterla dichiarare giocabile.
"""
for name in ['README.md','INTERPRETER.md']:
 with (root/name).open('ab') as f:f.write(summary.encode('ascii'))
(root/'NEXT-STEPS.md').write_text("""# Punto di ripresa: 25 settembre 2026, sera

Compilazione e suite completa PASS. Hash, log e copertura aggiornati in
evidence/development-validation.json. Codice canonico engine/astronomica;
copia compilata work/fresh-20260913/scummvm/engines/astronomica.
Nessun pacchetto aggiornato: ZIP, launcher, bin e patch v34 restano invariati.
Venti scene con percorsi verificati, incluse sei varianti dello stesso gruppo.
Conferma manuale soltanto P508; gioco intero e salvataggi ancora incompleti.
98/121 template (81.0%) nella misura statica senza animazione.

## Ultime implementazioni
P518: custom12 e callback _fxm_set_idplanet/_fxm_move_idplanet. Nove pianeti,
errore recuperabile, due direzioni, limiti e uscita non risolta verificati.
P506/P531-P535: custom17, tre estrazioni senza ripetizione dopo la prima
scena. DS014b/014f persistono anche attraverso loadLocalConditions e
resetGlobals, come nell'originale; reset al completamento. S12, global23,
S22 sincrono, poi P519 dopo 3000 ms. Introduttiva saltata quando round>1.
Prove originali: probe_p518_planets.py e probe_variants.py.
Per verificare solo il gruppo: work/fresh-20260913/check_variants.py.
Suite completa: work/fresh-20260913/runtime_test.py (limite 360 secondi).
Helper prove: save_development_evidence.py, ora richiede anche i nuovi PASS.

## Prossimo lavoro: P526, raggiunto da P528
Sonda probe_p526_answers.py: 588 combinazioni eseguite direttamente sulla
catena CMP/Jcc originale 4:2851-2e1d. Tabella in evidence/p526-answers.json.
Input locale2 (scenario), sprite18.frame e locale3 (scelta), output locale4.
Scenari 1..4 condividono una tabella; 5..6 ne condividono una diversa.
Nessun codice P526 integrato nel motore.

Custom13/0 (4:26a4-284e) configura sprite20,22,23: centro 300+arg3,
120+arg4; raggi 200/100; timer10, delta2/0; callback _fxm_eclipse 3:1199.
GameSprite+b9 viene scritto due volte e termina a zero (4:2844).
_fxm_eclipse chiama _fxm_move_ellipse solo per sprite20, sposta sprite21/22/23,
cambia visibilita davanti/dietro e si ferma alle soglie dipendenti da locale2.
Quando arriva, ferma anche l'animazione sprite18 e normalizza frame6..8 a5,
frame9..10 a11. Disassemblati in work/fresh-20260913/interpreter.
_fxm_move_ellipse (3:2733-33e4) usa sqrt e conversione intera PRIMA della
moltiplicazione/divisione dei raggi, non sin/cos. Verificare l'arrotondamento
del convertitore 1:15c3. Gestisce quadranti in +bd/+c1 e altri casi specifici
per P514: distinguere le parti effettivamente percorse da P526.

Restano P512 (uscita di P517), altri puzzle, navigazione, aiuti e salvataggi.
""")
print('Evening documentation saved')
