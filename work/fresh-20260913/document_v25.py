from pathlib import Path
out=Path('outputs/astronomica-cleanroom')
p=out/'README.md';s=p.read_text().replace('revisione 24.', 'revisione 25.',1).replace('sottoinsieme di 28 opcode','sottoinsieme di 30 opcode').replace('15, 16, 17, 23,','15, 16, 17, 20, 23,').replace('46, 47, 48 e 51','46, 47, 48, 49 e 51');s+='''
## Revisione 25: immagini aggiuntive

Implementata la coppia di comandi 20/49 quando il caricamento e seguito
immediatamente dalla visualizzazione. Il bitmap originale viene copiato
sullo sfondo, poi gli sprite vengono ridisegnati. Sono verificate sei
coppie originali di P505, P509 e P511 contro immagini indipendenti.

Il supporto richiede una scena a un livello e un bitmap decodificabile;
le immagini esterne monocromatiche e i comandi separati da attese o
dir am azioni restano esclusi. P508 usa proprio una di queste forme.
Nessun nuovo enigma viene dichiarato completabile: il rapporto degli
script viene aggiornato usando la nuova build.
'''.replace('dir am azioni','diramazioni');p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text();s+='''
## Bitmap esterni 20/49: revisione 25

Opcode 20 (15:05ba) costruisce il percorso PLACES/P<scena>/<nome>, porta
il nome a maiuscole, legge un bitmap e conserva le coordinate attraverso
registri a 16 bit con segno. Non visualizza ancora nulla. Opcode 49
(15:068a) usa SRCCOPY (0x00cc0020) sul buffer di sfondo del mondo (+0x0c),
rilascia il bitmap temporaneo e chiama _UpdateGame (13:0eba).
_SWUpdateSpriteWorld (6:069d) copia lo sfondo e ricompone gli sprite.
Le nuove disassemblature sono incluse in evidence/interpreter.

Il sottoinsieme ammesso richiede 20 seguito da 49 con delay=-1, senza
istruzioni intermedie. Ogni 49 deve avere quel predecessore. Il motore
puo quindi applicare la coppia in una singola azione, senza conservare
un bitmap in attesa. Il controllo preventivo verifica il file nella
scena corrente e rifiuta la catena intera se non supportata. Sono ammesse
scene a un livello, nomi locali semplici e immagini fino a 640x480;
la superficie viene convertita nel formato del backend e ritagliata
ai bordi. I BMP esterni a 1 bit restano esclusi. Le coordinate vengono
convertite a int16 come nell'handler originale.

Il disegno modifica _background: un ridisegno successivo degli sprite
conserva l'immagine. Il caricamento della scena ripristina lo sfondo
originale. Le forme con staging attraverso rami o attese restano escluse,
compreso lo script 1 di P508. Anche il supporto dei livelli multipli
resta incompleto.

verify_background_reference.py costruisce con Pillow sei composizioni
indipendenti dai file originali: APOLLO/CAVE in P505, SKY1/SKY2 in P509,
CLOUD3/CLOUD2 in P511. La suite nativa esegue le rispettive coppie
originali e confronta gli hash RGB888/RGB565, la persistenza al ridisegno
e il ripristino al caricamento. Verifica rifiuto di file assente, percorso
non locale, visualizzazione ritardata e comando sconosciuto successivo.
Sono prove di singole coppie, non di soluzione integrale degli enigmi.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v24.py');s=p.read_text().replace('v24','v25');s=s.replace("assert 'multi-puzzle success verification: PASS'", "assert 'background image verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'multi-puzzle success verification: PASS'");p.with_name('package_v25.py').write_text(s)
# Remove only the earlier exploratory P508 references, not validated by the native suite.
for name in ('P508-0-x23-y365.png','P508-1-x23-y365.png','P508-movement.json'):
 p=out/'evidence/background'/name
 if p.exists():p.unlink()
