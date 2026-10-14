# Formato ricostruito — Astronomica PC

Le informazioni specifiche del gioco provengono soltanto dai file originali di `D:\astro`.
Riferimento eseguibile: SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`.

## Eseguibile e simboli

- MZ con header NE a offset file `0x250`.
- 20 segmenti NE; unità di allineamento 512 byte.
- Blocco NB02 a `0x24600`; firma Borland `FB 52`, versione `01 04`, a `0x24610`.
- Record simboli a `0x24690`, 3.686 record di 14 byte: indice nome u32, indice tipo u32, offset u16, segmento u16, flags u16.
- Pool nomi a `0x61ff5`, stringhe terminate da NUL, indici a partire da 1.
- Offset file di un simbolo di codice: base del segmento NE + offset del simbolo.

| Funzione originale | Segmento:offset | Offset file |
|---|---|---|
| `_load_place` | 9:1404 | 0x15a04 |
| `_read_command_mem` | 9:2ff2 | 0x175f2 |
| `_getsome` | 9:2fcd | 0x175cd |
| `_execute_command` | 15:0060 | 0x1bc60 |
| `_load_game` | 13:01bc | 0x1a7bc |

Il riferimento generale Borland consultato è [borland-debug-info.bt](https://gist.github.com/hezi/1360089cc31b6b30b5f63b93d9ec2d49). Descrive una variante diversa: larghezze e offset qui riportati sono verificati nell'eseguibile, non copiati dalla variante del riferimento.

## Primitive

- Interi di serializzazione: 32 bit little endian, non gli int nativi Win16.
- Nomi: campi fissi di 255 byte; la parte dopo il primo NUL può contenere residui.
- Bitmap incorporate: lunghezza u32 seguita da un file BMP completo, inclusi header e palette.
- Comandi: opcode i32, argomenti di lunghezza dipendente dall'opcode, tempo i32; opcode 0 termina la sequenza e non ha altri campi.
- Alcuni argomenti rappresentano indici: il lettore originale modifica determinati indici dopo la lettura. I nuovi lettori mantengono invece i valori sul disco; non vanno passati direttamente a una futura VM senza la conversione verificata.

## Ordine di una scena

1. Modo i32. Per modo 1 seguono tre i32 di navigazione: sinistra, avanti/su, destra. Modi 0 e 3 non contengono la terna.
2. Sfondo: presente i32; se presente, incorporato i32; se incorporato, blocco bitmap, altrimenti nome di 255 byte.
3. Pannello: stessa struttura dello sfondo.
4. Suono introduttivo presente i32, seguito dal suo identificatore se presente.
5. Conteggi i32: livelli, sprite, suoni, filmati, cursori; poi campo nome di 255 byte.
6. Sprite.
7. Suoni: due i32 per elemento.
8. Filmati: nome di 255 byte per elemento.
9. Numero delle sequenze di comandi i32, seguito dalle sequenze.
10. Numero delle aree mouse i32; per ogni area quattro i32, poi tre sequenze opzionali ciascuna preceduta da un flag i32.
11. Numero delle condizioni i32; ogni condizione ha sei i32.

Una sequenza opzionale è un flag i32: 0 non ha payload, 1 è seguito dalla sequenza terminata da opcode 0.

## Sprite

- Riferimento clone i32. Se vale -1: numero dei frame i32, quindi per ogni frame un blocco BMP colore e un blocco BMP maschera.
- Livello, visibilità, x, y: quattro i32.
- Flag click. Se 1: tipo click i32 e sequenza comandi.
- Flag per l'altro gestore associato al trascinamento. Se 1: sequenza comandi.
- Quattro i32 del rettangolo.
- Due gestori opzionali mouse in/out.
- Flag avanzamento frame; se 1, tre i32.
- Flag movimento; se 1, cinque i32.
- Flag cursore; se 1, identificatore i32.

L'ordine è confermato dal caricatore e dall'attraversamento del corpus. Le etichette di alcuni campi sono ancora provvisorie: il loro significato completo richiede la verifica delle routine che li usano.

## Opcode

La tabella degli opcode è a `9:3528`; la tabella dei relativi indirizzi di lettura è a `9:35ec`. `opcode-layout.json` contiene i 49 layout, con indirizzi di ingresso e dimensioni delle letture degli argomenti. Tutti hanno inoltre un i32 finale letto dal percorso comune a `9:33f4`.

Nomi già confrontati con P0/PLACEDEF: 3 play_quicktime, 5 new_place, 6 quit_game, 23 custom, 31 condition, 32 set_condition, 42 end_condition, 45 else. Il codice 20 contiene un nome e due interi prima del tempo, ed è associato al caricamento dello sfondo. Questi nomi non equivalgono a un'implementazione verificata degli effetti.

Esempio P0: il primo comando a offset file `0xa64` è opcode 23, con argomenti `[26,11,0,0,0,0]` e tempo 0. A `0xa84` segue opcode 3 con `[0,160,120,0]` e tempo 0. Il nome del filmato nella tabella è `HQLOGO.MOV`.

## Limiti della validazione

Il caricatore C++ conserva i conteggi dei byte finali non interpretati; non li scambia per script. Il lettore Python rigoroso li rifiuta. Entrambi identificano il file P406 incompleto. Non è stata ancora eseguita una partita nell'eseguibile originale per confrontare gli effetti o la tempistica dei comandi.
