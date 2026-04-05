---
type: report
feature: diagnosi_test_eventi_strutturati
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Diagnosi test_giocatore_umano.py — test che usano testo invece di eventi
---

## Metadati

tipo: report
titolo: Diagnosi test_giocatore_umano.py — test che usano testo invece di eventi
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: bozza
feature: diagnosi_test_eventi_strutturati

---

## Sommario esecutivo

Il file `tests/test_giocatore_umano.py` contiene **67 test** in totale.
Di questi, **40 test** verificano ancora il risultato di un'azione leggendo
il testo che ne viene stampato, invece di controllare i campi strutturati
della risposta (l'oggetto `EsitoAzione`).

I metodi testati hanno smesso di restituire testo pronto. Ora restituiscono
una **risposta strutturata** con tre campi: `ok`, `errore`, `evento`.
I 40 test non lo sanno ancora: confrontano testo su un oggetto, e
l'oggetto a volte contiene per caso le parole che il test cerca.
La suite risulta verde (384/384), ma quella percentuale di verde è falsa
per circa il 60% dei test di navigazione: i test passano per coincidenza,
non perché il contratto sia verificato.

---

## Come leggere questo report

Il sistema definisce tre livelli di gravità per i test affetti:

- **Rosso**: il test confronta testo su un oggetto strutturato. Passa per
  coincidenza, ma non verifica nulla di utile. Un cambiamento nei testi
  interni lo farebbe implodere senza alcuna colpa logica.

- **Arancione**: il metodo restituisce una stringa (ottenuta convertendo
  l'oggetto strutturato), quindi il confronto testuale tecnicamente funziona,
  ma testa solo la rappresentazione visiva, non il contratto dei dati.

- **Verde**: il test usa già i campi strutturati dell'evento. Corretto.

---

## Mappa dei metodi e del livello di rischio

### Metodi con risposta strutturata (EsitoAzione grezzo)

Questi metodi restituiscono direttamente l'oggetto risposta.
I test devono leggere `.ok`, `.errore`, `.evento`.

| Metodo | Descrizione operativa |
|--------|----------------------|
| `sposta_focus_riga_su_semplice` | Sposta il focus verso la riga precedente (modalita base) |
| `sposta_focus_riga_giu_semplice` | Sposta il focus verso la riga successiva (modalita base) |
| `sposta_focus_riga_su` | Alias del precedente (comportamento identico) |
| `sposta_focus_riga_giu` | Alias del precedente (comportamento identico) |
| `sposta_focus_riga_su_avanzata` | Come sopra, con dati aggiuntivi sull'evento |
| `sposta_focus_riga_giu_avanzata` | Come sopra, con dati aggiuntivi sull'evento |
| `sposta_focus_colonna_sinistra` | Sposta il focus verso la colonna precedente (modalita base) |
| `sposta_focus_colonna_destra` | Sposta il focus verso la colonna successiva (modalita base) |
| `sposta_focus_colonna_sinistra_avanzata` | Come sopra, con dati avanzati sull'evento |
| `sposta_focus_colonna_destra_avanzata` | Come sopra, con dati avanzati sull'evento |

### Metodi che convertono la risposta in stringa prima di restituirla

Questi metodi costruiscono internamente l'oggetto risposta ma lo trasformano
in testo prima di restituirlo. I test testuali tecnicamente funzionano,
ma non verificano i dati: verificano solo la stampa.

| Metodo | Nota |
|--------|------|
| `visualizza_cartella_corrente_avanzata` | Restituisce la rappresentazione testuale dell'oggetto risposta |
| `visualizza_tutte_cartelle_avanzata` | Idem |

### Metodi che restituiscono testo diretto (corretti per design)

| Metodo | Nota |
|--------|------|
| `imposta_focus_cartella` | Restituisce testo nativo, i test sono corretti |
| `visualizza_cartella_corrente_semplice` | Idem |
| `visualizza_tutte_cartelle_semplice` | Idem |

---

## Elenco dei test affetti (gravita Rosso)

I test qui sotto usano confronti testuali (`assertIn`, `assertEqual`) su un
oggetto risposta strutturato, non su una stringa. Passano perche la
conversione automatica dell'oggetto in testo include per coincidenza le parole
cercate, ma non c'e' alcuna garanzia che continuino a passare al prossimo
cambiamento.

### Gruppo riga: spostamento verso l'alto (modalita base)

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_riga_su_semplice_cartella_mancante` | 501 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_riga_su_semplice_prima_riga` | 530 | `assertEqual("Sei alla prima riga...")` |
| `test_sposta_focus_riga_su_semplice_movimento_normale` | 561 | `assertIn("Riga 0:", ...)`, `assertIn(str(num), ...)` |
| `test_sposta_focus_riga_su_semplice_auto_inizializzazione` | 593 | `assertIn("Riga 0:", risultato)` |
| `test_sposta_focus_riga_su_semplice_stato_interno` | 611 | `assertIn("Riga 1:", risultato)` |

### Gruppo riga: spostamento verso il basso (modalita base)

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_riga_giu_semplice_cartella_mancante` | 628 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_riga_giu_semplice_ultima_riga` | 640 | `assertEqual("Sei all'ultima riga...")` |
| `test_sposta_focus_riga_giu_semplice_movimento_normale` | 653 | `assertIn("Riga 1:", ...)`, `assertIn(str(num), ...)` |
| `test_sposta_focus_riga_giu_semplice_auto_inizializzazione` | 671 | `assertIn("Riga 1:", risultato)` |
| `test_sposta_focus_riga_giu_semplice_stato_interno` | 685 | `assertIn("Riga 1:", risultato)` |

### Gruppo riga: spostamento verso l'alto (modalita avanzata)

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_riga_su_avanzata_cartella_mancante` | 706 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_riga_su_avanzata_prima_riga` | 728 | `assertEqual("Sei alla prima riga...")` |
| `test_sposta_focus_riga_su_avanzata_movimento_normale` | 745 | `assertIn("Riga 0:", ...)`, `assertIn(str(num), ...)` |
| `test_sposta_focus_riga_su_avanzata_auto_inizializzazione` | 761 | `assertIn("Riga 0:", risultato)` |
| `test_sposta_focus_riga_su_avanzata_stato_cartella_con_segni` | 774 | `assertIn(f"*{num}", risultato)` |

### Gruppo riga: spostamento verso il basso (modalita avanzata)

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_riga_giu_avanzata_cartella_mancante` | 794 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_riga_giu_avanzata_ultima_riga` | 806 | `assertEqual("Sei all'ultima riga...")` |
| `test_sposta_focus_riga_giu_avanzata_movimento_normale` | 819 | `assertIn("Riga 1:", risultato)` |
| `test_sposta_focus_riga_giu_avanzata_auto_inizializzazione` | 835 | `assertIn("Riga 1:", risultato)` |
| `test_sposta_focus_riga_giu_avanzata_stato_cartella_con_segni` | 848 | `assertIn(f"*{num}", risultato)` |

### Gruppo colonna sinistra: spostamento base

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_colonna_sinistra_semplice_cartella_mancante` | 869 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_colonna_sinistra_semplice_prima_colonna` | 898 | `assertEqual("Sei alla prima colonna...")` |
| `test_sposta_focus_colonna_sinistra_semplice_movimento_normale` | 930 | `assertIn("Colonna 4:", ...)`, `assertIn("vuota", ...)` |
| `test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione` | 972 | `assertIn("Colonna 3:", risultato)` |
| `test_sposta_focus_colonna_sinistra_semplice_colonna_vuota` | 989 | `assertIn("Colonna 3:", risultato)` |

### Gruppo colonna destra: spostamento base

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_colonna_destra_semplice_cartella_mancante` | 1006 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_colonna_destra_semplice_ultima_colonna` | 1018 | `assertEqual("Sei all'ultima colonna...")` |
| `test_sposta_focus_colonna_destra_semplice_movimento_normale` | 1031 | `assertIn("Colonna 4:", risultato)` |
| `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione` | 1048 | `assertIn("Colonna 5:", risultato)` |
| `test_sposta_focus_colonna_destra_semplice_colonna_vuota` | 1062 | `assertIn("Colonna 5:", risultato)` |
| `test_sposta_focus_colonna_destra_semplice_stato_interno` | 1075 | `assertIn("Colonna 4:", risultato)` |

### Gruppo colonna sinistra: spostamento avanzato (parzialmente gia' corretto)

Il test `movimento_normale` e' stato gia' corretto nella sessione precedente.
I quattro rimanenti usano ancora confronti testuali.

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_colonna_sinistra_avanzata_cartella_mancante` | 1096 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_colonna_sinistra_avanzata_prima_colonna` | 1124 | `assertEqual("Sei alla prima colonna...")` |
| `test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione` | 1194 | `assertIn("Colonna 3:", risultato)` |
| `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` | 1210 | `assertIn(f"*{num}", ...)`, `assertIn("Segnati:", ...)`, `assertIn("vuota", ...)` |

### Gruppo colonna destra: spostamento avanzato

| Test | Riga | Tipo di confronto errato |
|------|------|--------------------------|
| `test_sposta_focus_colonna_destra_avanzata_cartella_mancante` | ~1254 | `assertEqual("Non hai selezionato...")` |
| `test_sposta_focus_colonna_destra_avanzata_ultima_colonna` | ~1270 | `assertEqual("Sei all'ultima colonna...")` |
| `test_sposta_focus_colonna_destra_avanzata_movimento_normale` | ~1290 | `assertIn("Colonna 4:", ...)`, `assertIn("vuota", ...)` |
| `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione` | ~1315 | `assertIn("Colonna 5:", risultato)` |
| `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni` | ~1335 | `assertIn(f"*{num}", ...)`, `assertIn("Segnati:", ...)` |

---

## Test che convertono in testo prima di restituire (gravita Arancione)

Questi test non sono formalmente sbagliati, perche il metodo stesso restituisce
gia' una stringa (costruita internamente dalla risposta strutturata).
Tuttavia non verificano i dati dell'evento: verificano solo la loro
rappresentazione visiva. Questo li rende fragili a qualunque modifica
estetica del renderer.

| Test | Metodo | Riga approssimativa |
|------|--------|---------------------|
| `test_visualizza_cartella_corrente_avanzata_con_focus` | `visualizza_cartella_corrente_avanzata` | ~250 |
| `test_visualizza_tutte_cartelle_avanzata_con_segni` | `visualizza_tutte_cartelle_avanzata` | ~500 |

---

## Test gia' corretti (gravita Verde)

| Gruppo | Numero test corretti | Metodo o area |
|--------|---------------------|---------------|
| imposta_focus_cartella | 4 | Restituisce testo nativo, test corretti per design |
| visualizza semplice | vari | Restituisce testo nativo, test corretti per design |
| colonna sinistra avanzata (movimento normale) | 1 | Gia' convertito nella sessione precedente |

---

## Conteggio finale

| Categoria | Conteggio |
|-----------|-----------|
| Test totali nel file | 67 |
| Test corretti (verde) | ~25 |
| Test a rischio alto — confronto testo su oggetto strutturato (rosso) | 40 |
| Test a rischio medio — confronto testo su stringa derivata da oggetto (arancione) | 2 |

---

## Perche' la suite appare verde (384/384)

L'oggetto risposta (EsitoAzione) ha una funzione di conversione automatica in
testo (`__str__`). Quando un test scrive `assertIn("Riga 0:", risultato)` e
`risultato` e' un oggetto strutturato, Python chiama in silenzio quella
funzione di conversione. Il testo risultante contiene per caso le parole
cercate, quindi il test passa.

Non c'e' nessun bug applicativo. Il sistema funziona. Il problema e' che i
test non verificano il contratto reale del metodo: verificano solo una
proiezione testuale casuale di quell'oggetto. Se il testo della proiezione
cambia (per modifica del renderer, della lingua o del formato), tutti i 40
test crollano insieme — anche se il metodo continua a funzionare
perfettamente.

---

## Rischio operativo

Il rischio attuale e' classificabile come **medio-alto per i 40 test rossi**.

- Qualunque rinomina di un campo testuale interno dell'evento fa fallire
  decine di test in un colpo solo, senza che ci sia alcun bug reale.
- I test che verificano i numeri (es. `assertIn("Riga 1:", risultato)`)
  dipendono da come l'oggetto scrive i propri campi, non da quanti li
  espone o come li chiama.
- Il pattern `assertIn(f"*{num}", risultato)` sui segni di marcatura e'
  quello piu' fragile: verifica che il numero segnato compaia nel testo,
  ma non verifica che sia nel campo corretto dell'evento.

---

## Raccomandazione

Aprire un nuovo ciclo di planning (PLAN + TODO) per modernizzare i 40 test
rossi in blocchi logici coerenti:

1. **Blocco riga** (20 test): riga su semplice, riga giu semplice, riga su
   avanzata, riga giu avanzata.
2. **Blocco colonna sinistra** (9 test): semplice (5) + avanzata incompleta (4).
3. **Blocco colonna destra** (11 test): semplice (6) + avanzata (5).

Ogni test modernizzato dovra' seguire il pattern gia' stabilito da
`test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`:
controllare `risultato.ok`, `risultato.errore`, e i campi specifici
di `risultato.evento`.

I 2 test arancioni (visualizza avanzata) possono essere trattati in un
quarto micro-blocco, decidendo prima se mantenere il contratto "restituisce
stringa" o passare anche quei metodi a EsitoAzione puro.

---

## File coinvolti

- `tests/test_giocatore_umano.py` — file diagnosticato
- `bingo_game/players/giocatore_umano.py` — file con i metodi testati
- `bingo_game/events/eventi.py` — definizione di EsitoAzione
- `bingo_game/events/eventi_output_ui_umani.py` — definizione degli eventi strutturati
