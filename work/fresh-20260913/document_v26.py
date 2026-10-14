from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace('reload, missing/unsafe/delayed rejection)', 'reload, deferred display, missing/unsafe rejection)');p.write_text(s);shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
p=Path('outputs/astronomica-cleanroom/survey_puzzles.py');s=p.read_text().replace('Gli opcode 20/49 sono ammessi soltanto in coppia consecutiva, con visualizzazione immediata, file BMP decodificabile e scena a un livello. I casi separati da diramazioni, come P508, restano esclusi.', 'Gli opcode 20/49 supportano caricamento e visualizzazione separati, anche attraverso diramazioni e attese. Restano necessari file BMP decodificabili e scene a un livello. P508 script 1 e verificato sulle 18 varianti, non equivale alla soluzione completa del puzzle.');p.write_text(s)
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text().replace('revisione 25.', 'revisione 26.',1);s+='''
## Revisione 26: immagini attraverso diramazioni e attese

Il caricamento di un'immagine non la disegna piu immediatamente: il
bitmap rimane in attesa fino al comando 49. Questo supera la restrizione
delle coppie consecutive della revisione 25. Un secondo caricamento
sostituisce l'immagine in attesa; il cambio scena la elimina.

Verificato lo script 1 originale completo di P508 per tutte le 18
varianti, con confronto dei pixel e controllo che nessuna immagine
compaia anticipatamente. Non e ancora una prova di soluzione dell'enigma:
le altre sequenze e interazioni possono restare incomplete.
''';p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
## Caricamento separato dalla visualizzazione: revisione 26

Gli handler originali 15:05ba e 15:068a conservano un bitmap intermedio
con coordinate globali: il comando 20 non deve alterare lo sfondo. Il
motore ora mantiene una superficie temporanea separata e coordinate;
49 la copia nello sfondo, libera la superficie e ridisegna gli sprite.
La superficie sopravvive ai passaggi della coda, alle diramazioni e alle
attese. Caricamenti successivi sostituiscono la superficie senza disegno.
Il cambio scena la libera; una visualizzazione senza immagine in attesa
ridisegna soltanto la scena, senza usare puntatori gia liberati.

Il controllo preventivo continua a validare file e catene intere, ma
non impone piu l'adiacenza di 20/49. Rimangono le restrizioni sui bitmap
esterni monocromatici e sulle scene a piu livelli. Non si riproducono
perdite di risorse o eventuali riusi di handle GDI gia liberati presenti
nell'eseguibile originale.

La prova nativa esegue lo script 1 P508 senza modificarne le istruzioni,
18 volte con seme casuale fissato. Verifica 18 scelte distinte, tutti
gli hash dei riferimenti Pillow, l'assenza di disegno durante lo staging,
la completa consumazione della coda e l'assenza di transizioni inattese.
Ulteriori prove isolano due caricamenti prima di una visualizzazione,
la pulizia al reload e un display temporizzato a 0/1 ms. Il vecchio test
di rifiuto del display ritardato e sostituito dal controllo dell'attesa.
verify_staged_reference.py e evidence/staged/choices.json rendono
riproducibili i 18 riferimenti dalle risorse originali.

Questa verifica copre la selezione/visualizzazione delle varianti di
P508, non le risposte del giocatore o la risoluzione completa del puzzle.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v25.py');s=p.read_text().replace('v25','v26');s=s.replace("assert 'background image verification: PASS'", "assert 'staged image verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'background image verification: PASS'");p.with_name('package_v26.py').write_text(s)
