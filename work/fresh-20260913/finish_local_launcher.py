"""Record the tested local entry point and refresh the current README only."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
proof=json.loads((root/'evidence/local-launcher-validation.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==hashlib.sha256((work/'build/Releasex64/scummvm.exe').read_bytes()).hexdigest()
assert proof['template_sha256']==hashlib.sha256((root/'astronomica-play.ini').read_bytes()).hexdigest()
shutil.copyfile(work/'launcher startup check/startup.log',root/'evidence/local-launcher-startup.log')
coverage=json.loads((root/'evidence/native-save-coverage.json').read_text())
places=', '.join('P'+str(r['scene']) for r in sorted(coverage['puzzle_saves'],key=lambda r:r['scene']))
p=root/'README.md';old=p.read_text();history=old[old.index('## Registro storico delle funzionalita (settembre)'):]
head=('# Astronomica — ripartenza dai file originali\n\n'
 'Stato verificato: 21 ottobre 2026. Motore ScummVM nativo in sviluppo; build locale e suite completa WASAPI PASS.\n\n'
 'Avvio corrente: aprire **Avvia-Astronomica.cmd nella radice del workspace**. Usa la build reale attuale, parte dal menu P1 e attiva audio, animazioni e interazione. '
 'Preferenze e salvataggi personali sono in userdata/astronomica, separati dalle prove. Il vecchio collegamento bin/Avvia-Astronomica.cmd rimanda allo stesso avvio. Vedere LOCAL-PLAY.md.\n\n'
 'Sono verificati automaticamente percorsi in 35 scene di puzzle, oltre a navigazione, filmati, audio, aiuto e salvataggi di esplorazione. '
 'L\'aiuto legge 781 articoli e 31 immagini originali fra testo e didascalie. I 13 esponenti originali sono resi con notazione ^(valore).\n\n'
 f'Salvataggi nativi verificati in esplorazione e in {places}. Import GAMESTAT originale disponibile per esplorazione con countdown inattivo. '
 'Restano altri salvataggi, fedelta tipografica e verifica audiovisiva manuale integrale. Nessuna percentuale globale attendibile; 94.2% misura solo 114/121 template statici, non la giocabilita.\n\n'
 'Usare NEXT-STEPS.md per riprendere e verify_development_evidence.py per verificare il checkpoint. Eseguibile corrente: work/fresh-20260913/build/Releasex64/scummvm.exe. '
 'L\'avvio richiede la build locale e i file originali D:/astro; non e un nuovo pacchetto distribuibile.\n\n'
 'Questo lavoro e stato ricostruito da D:/astro, senza consultare codice, rapporti o conclusioni dei tentativi precedenti esclusi dall\'utente. '
 'Il nome della cartella indica questa ripartenza; non e una certificazione legale di processo clean room.\n\n')
if (root/'evidence/probe-saves-validation.json').exists():
 head=head.replace('21 ottobre 2026','22 ottobre 2026')
 head=head.replace('Import GAMESTAT originale', 'P522 conserva solo confini ordinari senza volo, con poll e orbite attive. Import GAMESTAT originale')
if (root/'evidence/rendezvous-saves-validation.json').exists():
 head=head.replace('Import GAMESTAT originale', 'P514 conserva orbite attive, carburante e storia degli attracchi falliti ai confini senza comandi in coda. Import GAMESTAT originale')
if (root/'evidence/p516-saves-validation.json').exists():
 head=head.replace('Import GAMESTAT originale', 'P516 salva gli stati verificati con orbite attive e missile fermo. Import GAMESTAT originale')
if (root/'evidence/p511-saves-validation.json').exists():
 head=head.replace('22 ottobre 2026','25 ottobre 2026').replace('21 ottobre 2026','25 ottobre 2026')
 head=head.replace('Import GAMESTAT originale', 'P511 conserva nuvole, fotogrammi e intervalli originali ai confini senza lavoro in coda. Import GAMESTAT originale')
elif (root/'evidence/p509-saves-validation.json').exists():
 head=head.replace('22 ottobre 2026','24 ottobre 2026').replace('21 ottobre 2026','24 ottobre 2026')
 head=head.replace('Import GAMESTAT originale', 'P509 conserva il narratore originale in attesa, i due cieli ordinari e le animazioni nascoste; altre code e voci attive restano escluse. Import GAMESTAT originale')
elif (root/'evidence/p521-saves-validation.json').exists():
 head=head.replace('22 ottobre 2026','23 ottobre 2026')
if (root/'evidence/p503-saves-validation.json').exists():
 head=head.replace('25 ottobre 2026','26 ottobre 2026')
 head=head.replace('Import GAMESTAT originale', 'P503 conserva scelte e orbite parziali con timer indipendenti dei partner; ascesa, rilanci falliti di bersagli gia risolti e transizioni restano esclusi. Import GAMESTAT originale')
elif (root/'evidence/p502-saves-validation.json').exists():
 head=head.replace('25 ottobre 2026','26 ottobre 2026')
p.write_text(head+history)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
print('Current local launcher and README checkpoint PASS')
