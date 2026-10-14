from pathlib import Path
r=Path('outputs/astronomica-cleanroom')
p=r/'README.md';s=p.read_text().replace('revisione 14. Progresso complessivo stimato: circa 37%', 'revisione 15. Progresso complessivo stimato: circa 38%')
s=s.replace('- Lettore Python indipendente', '- Uscite originali di P510 verso P136 e P408, con suono, ritardo e pulizia delle continuazioni.\n- Lettore Python indipendente')
s=s.replace('Il prototipo parte da P1.', '''`bin/Prova-uscite.cmd` apre P510 con audio, animazioni e mouse.
Cliccare vicino a **(35,430)** per la sequenza originale che riproduce S4
e porta a P136 dopo 500 ms. Il pulsante vicino a **(600,430)** riproduce S5
e porta a P408 dopo 700 ms. Riavviare la prova per verificare l'altra uscita.
I ritardi decorrono dai rispettivi passaggi della coda. L'arrivo mostra
le risorse della destinazione; non significa che il suo comportamento
completo o l'enigma P510 siano implementati.

Il prototipo parte da P1.''');p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text().replace('le azioni che cambiano scena o escono devono essere l’ultimo comando.', 'le azioni che cambiano scena o escono avevano inizialmente il vincolo di essere l’ultimo comando; la revisione 15 estende il caso 5 come descritto sotto.')
s=s.replace("le azioni che cambiano scena o escono devono essere l'ultimo comando.", 'le azioni che cambiano scena o escono avevano inizialmente il vincolo di essere l’ultimo comando; la revisione 15 estende il caso 5 come descritto sotto.')
s+='''

## Uscite ritardate: revisione 15

L'opcode 5 (15:0363–038f) aggiorna DS:0c8c con la destinazione e imposta
DS:0c98, poi raggiunge la gestione comune della continuazione. Non carica
direttamente il file della nuova scena. Il ciclo `_do_place` controlla
il flag in 9:0258; prima del successivo caricamento chiama
`_free_pending_commands` in 9:01a7. Lo sblocco dei clic viene azzerato
esplicitamente in 9:01e0.

Viene rimosso il vincolo che imponeva a new_place di essere l'ultima
istruzione, limitatamente alle catene il cui successore passa dalla coda
(delay >= 0). La verifica preventiva continua a validare tutta la catena.
I successori immediati con delay=-1 restano esclusi: potrebbero ancora
produrre effetti nella vecchia scena prima del cambio, comportamento non
ancora interamente riprodotto. Restano inoltre incomplete le regole
specifiche di accesso e le combinazioni di più cambi scena nello stesso
passaggio. Non si rivendica equivalenza generale di tutte le transizioni.

P510 sprite 4, programma originale completo: blocco clic, S4,
new_place(136,500), sblocco dopo altri 150 ms. L'ultimo comando viene
accodato ma eliminato dal cambio scena. Il test verifica permanenza a
499 ms, arrivo a 500 ms, coda vuota, input sbloccato, conservazione del
globale 95 e assenza di altre istruzioni eseguite a 650 ms.
Controlla inoltre che l'immagine della destinazione non cambi a 650 ms.

La seconda prova usa P510 sprite 6: S5, new_place(408,700). Verifica
permanenza a 699 ms e arrivo a 700 ms. Entrambe passano dall'effettivo
gestore dei clic, comprendendo la pressione del pulsante tipo 2.
Le destinazioni vengono caricate e renderizzate dai MEGAFILE originali.
Audio, grafica, condizioni e prove precedenti continuano a passare.

Precisazione sull'audio della revisione 14: il riferimento 9:06a6 dimostra
lo stop all'uscita dal ciclo principale, non prova da solo lo stop a ogni
transizione. Fermare l'handle al caricamento rimane per ora una politica
conservativa del prototipo; la continuità sonora tra scene va ricostruita.
''';p.write_text(s)
base=Path('work/fresh-20260913');s=(base/'package_v14.py').read_text().replace('v14','v15')
anchor='# Verify the distributable probe independently against the same original.'
s=s.replace(anchor,'''(out/'bin/Prova-uscite.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-audio\\r\\n')
'''+anchor)
s=s.replace("assert 'audio verification: PASS'", "assert 'transition verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'audio verification: PASS'")
(base/'package_v15.py').write_text(s)
