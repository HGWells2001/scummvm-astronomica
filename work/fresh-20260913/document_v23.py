from pathlib import Path
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text().replace('revisione 22. Progresso complessivo stimato: circa 44%', 'revisione 23. Progresso complessivo stimato: circa 45%');s=s.replace('- Prima operazione personalizzata di completamento P511: suono sincrono, variabile globale 27 e conteggio senza duplicati.', '- Prima operazione personalizzata di completamento P511: suono sincrono, variabile globale 27 e conteggio senza duplicati.\n- Sequenza finale originale completa di P511 verificata: otto posizioni, attesa del suono e transizione a P388, partendo dallo stato risolto impostato dal test.');s+='''
## Revisione 23

Superata la verifica dell'intero script 0 originale di P511 (21 comandi),
con stato iniziale di enigma risolto impostato dal test. La sequenza esegue
le otto posizioni, attende il suono di successo e passa a P388. Verificato
anche il ramo non risolto, che sblocca i clic dopo 75 ms senza uscire.

Corretto inoltre un accesso oltre la fine dello script quando una
dir am azione salta direttamente al termine. Ora sono ammesse le
transizioni seguite soltanto da controllo immediato del flusso;
gli effetti immediati sulla vecchia scena restano esclusi.

Il progresso stimato e circa 45%, senza equivalenza con la parte di gioco
completabile. Non e ancora possibile risolvere tutto P511 giocando: restano
le immagini aggiuntive e altre interazioni. Non sono aggiunti avvii di
soluzione automatica; questa e una verifica di sviluppo.
'''.replace('dir am azione','diramazione');p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
## Transizioni con chiusura della diramazione: revisione 23

Opcode 5 (15:0363) scrive la destinazione in DS:0c8c e imposta DS:0c98;
_execute_command continua a elaborare i collegamenti immediati e
_do_command li percorre prima di restituire. _do_place verifica la
richiesta dopo _place_loop e ripulisce i comandi in attesa prima del
caricamento. La transizione puo quindi precedere un opcode 45 immediato.

La validazione ora permette nel suffisso della transizione soltanto
istruzioni immediate 1,2,31,42,45. Controlla tutto il suffisso, anche oltre
ritardi intermedi, perche i collegamenti condizionali possono saltarli.
Gli effetti immediati sulla vecchia scena restano rifiutati. Il caricamento
avviene dopo il controllo del flusso; le continuazioni accodate vengono
eliminate al cambio scena come prima. Il controllo dell'indice viene
ripetuto DOPO aver seguito il collegamento condizionale: un salto alla
fine dello script termina senza leggere oltre l'array.

La prova nativa usa tutto lo script 0 originale P511 senza modificarlo,
impostando local[5]=7 e global[27]=0 soltanto come condizione iniziale.
Verifica le otto posizioni dello sprite 20 ogni 300 ms, la mancata
esecuzione anticipata del successo, il suono sincrono e il cambio P388
a 1000 ms dalla fine del suono. Verifica la pulizia delle continuazioni,
lo sblocco input e la persistenza del successo. Nel ramo non risolto,
local[5]=0, verifica che i clic restino bloccati a 74 ms e si sblocchino
a 75 ms, senza successo o transizione. Una variante di test con un
nascondimento immediato dopo la diramazione resta rifiutata atomicamente.
verify_ending_reference.py conferma le 21 istruzioni dai file originali,
con risultato riproducibile in evidence/ending.json.

Questa revisione supera il limite dello script 0 citato nella revisione
22. Non dimostra che il giocatore possa risolvere l'intero P511: lo stato
risolto e preparato dal test, e immagini/interazioni restano incomplete.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v22.py');s=p.read_text().replace('v22','v23');s=s.replace("assert 'success verification: PASS'", "assert 'ending verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'success verification: PASS'");p.with_name('package_v23.py').write_text(s)
