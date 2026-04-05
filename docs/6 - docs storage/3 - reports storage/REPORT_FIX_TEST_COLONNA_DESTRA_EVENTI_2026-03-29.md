---
type: report
feature: fix_test_colonna_destra_eventi
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Report analisi tranche 3 modernizzazione test colonna destra
---

## Metadati

tipo: report
titolo: Report analisi tranche 3 modernizzazione test colonna destra
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: bozza
feature: fix_test_colonna_destra_eventi
versione_target: v1.0

## Contenuto

### Trigger

Dopo la tranche riga e la tranche colonna sinistra restano in
[tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) i test legacy del
gruppo colonna destra, ancora basati su confronti con stringhe renderizzate
anziche' sul contratto strutturato dei metodi.

I due metodi target della tranche 3 sono:

- `sposta_focus_colonna_destra`
- `sposta_focus_colonna_destra_avanzata`

### Sommario esecutivo

Nel gruppo colonna destra risultano presenti 11 test target:

- 6 per la variante base
- 5 per la variante avanzata

Allo stato attuale del file, tutti gli 11 test sono ancora legacy. Nessuno dei
test del gruppo destra verifica direttamente `ok`, `errore`, `evento` o il
payload dell'evento corretto.

Il contratto reale osservato nel codice sorgente e' chiaro:

- `sposta_focus_colonna_destra` ritorna `EsitoAzione` con evento
  `EventoNavigazioneColonna`
- `sposta_focus_colonna_destra_avanzata` ritorna `EsitoAzione` con evento
  `EventoNavigazioneColonnaAvanzata`

Ne consegue che ogni `assertEqual(risultato, "...")`, `assertIn("Colonna X:", risultato)`
o ricerca di parole del renderer e' una verifica del layer di presentazione e
non del contratto del metodo.

### Componenti coinvolti

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [bingo_game/players/giocatore_umano.py](bingo_game/players/giocatore_umano.py)
- [bingo_game/events/eventi.py](bingo_game/events/eventi.py)
- [bingo_game/events/eventi_output_ui_umani.py](bingo_game/events/eventi_output_ui_umani.py)
- [docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md](docs/4%20-%20reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md)
- [docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md](docs/2%20-%20projects/DESIGN_fix_test_colonna_sinistra_eventi.md)
- [docs/3 - coding plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md](docs/3%20-%20coding%20plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md)

### Dipendenze

- I test dipendono dal contratto di `EsitoAzione` e dalle factory evento per la
  navigazione colonne.
- La variante avanzata dipende anche dal pacchetto restituito da
  `Cartella.get_dati_visualizzazione_colonna_avanzata(indice_colonna)`.
- La lezione operativa della tranche 2 impone di leggere il corpo di ciascun
  test prima di modificarlo, per evitare di toccare test gia' strutturati.

### Contratti osservabili

#### Versione base

Metodo: `sposta_focus_colonna_destra`

- ritorna `EsitoAzione`
- in errore: `ok=False`, `errore` valorizzato, `evento=None`
- in limite massimo: `ok=True`, `errore=None`, `evento` di tipo
  `EventoNavigazioneColonna`, `esito="limite"`, `limite="massimo"`
- in movimento riuscito: `ok=True`, `errore=None`, `evento` di tipo
  `EventoNavigazioneColonna`, `esito="mostra"`
- in auto-inizializzazione da focus colonna `None`: il focus viene inizializzato
  e il primo comando destra sposta alla colonna successiva; nello stato attuale
  del metodo la colonna utente risultante e' la 5
- campi specifici osservabili:
  - `direzione="successiva"`
  - `numero_colonna_corrente` 1-based
  - `colonna_semplice`
  - `limite`

#### Versione avanzata

Metodo: `sposta_focus_colonna_destra_avanzata`

- ritorna `EsitoAzione`
- in errore: `ok=False`, `errore` valorizzato, `evento=None`
- in limite massimo: `ok=True`, `errore=None`, `evento` di tipo
  `EventoNavigazioneColonnaAvanzata`, `esito="limite"`, `limite="massimo"`
- in movimento riuscito: `ok=True`, `errore=None`, `evento` di tipo
  `EventoNavigazioneColonnaAvanzata`, `esito="mostra"`
- in auto-inizializzazione da focus colonna `None`: il metodo inizializza il
  focus alla colonna centrale interna e poi avanza di una posizione; nello stato
  attuale la colonna utente risultante e' la 6
- campi specifici osservabili:
  - `direzione="destra"`
  - `numero_colonna_corrente` 1-based
  - `colonna_semplice`
  - `stato_colonna`
  - `numeri_segnati_colonna_ordinati`
  - `limite`

### Differenza base vs avanzata

- La base espone solo `colonna_semplice` e `limite`.
- L'avanzata espone anche `stato_colonna` e `numeri_segnati_colonna_ordinati`.
- Il caso colonna vuota non e' un errore: e' un normale `esito="mostra"`.
- La direzione serializzata nell'evento non e' identica tra i due metodi:
  base `successiva`, avanzata `destra`.

### Diagnosi puntuale degli 11 test

#### Gruppo semplice — sposta_focus_colonna_destra

1. `test_sposta_focus_colonna_destra_semplice_cartella_mancante`
   - confronto errato attuale: `assertEqual` contro stringa utente
   - scenario: errore
   - campi da verificare:
     - scenario senza cartelle: `ok=False`, `errore="CARTELLE_NESSUNA_ASSEGNATA"`, `evento=None`
     - scenario focus cartella `None`: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`, `evento=None`

2. `test_sposta_focus_colonna_destra_semplice_ultima_colonna`
   - confronto errato attuale: `assertEqual` contro stringa di limite
   - scenario: limite massimo
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="limite"`
     - `evento.limite="massimo"`
     - `evento.numero_colonna_corrente == 9`
     - `_indice_colonna_focus == 8`

3. `test_sposta_focus_colonna_destra_semplice_movimento_normale`
   - confronto errato attuale: ricerca di header colonna e numeri nel renderer
   - scenario: movimento riuscito
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 5`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(4)`
     - `evento.limite is None`
     - `_indice_colonna_focus == 4`

4. `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`
   - confronto errato attuale: `assertIn("Colonna 5:", risultato)`
   - scenario: movimento riuscito da focus colonna `None`
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 5`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(4)`
     - `_indice_colonna_focus == 4`

5. `test_sposta_focus_colonna_destra_semplice_colonna_vuota`
   - confronto errato attuale: `assertIn("Colonna 5:", risultato)`
   - scenario: colonna vuota trattata come movimento riuscito
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 6`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(5)`
     - `_indice_colonna_focus == 5`

6. `test_sposta_focus_colonna_destra_semplice_stato_interno`
   - confronto errato attuale: ricerca testo renderizzato e assenza di `*`
   - scenario: movimento semplice con cartella che contiene numeri segnati
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 5`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(4)`
     - `_indice_colonna_focus == 4`
   - nota: il controllo corretto non e' l'assenza di asterischi nel renderer ma
     il fatto che la versione semplice esponga solo `colonna_semplice`

#### Gruppo avanzato — sposta_focus_colonna_destra_avanzata

7. `test_sposta_focus_colonna_destra_avanzata_cartella_mancante`
   - confronto errato attuale: `assertEqual` contro stringa utente
   - scenario: errore
   - campi da verificare:
     - scenario senza cartelle: `ok=False`, `errore="CARTELLE_NESSUNA_ASSEGNATA"`, `evento=None`
     - scenario focus cartella `None`: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`, `evento=None`

8. `test_sposta_focus_colonna_destra_avanzata_ultima_colonna`
   - confronto errato attuale: `assertEqual` contro stringa di limite
   - scenario: limite massimo
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonnaAvanzata`
     - `evento.esito="limite"`
     - `evento.limite="massimo"`
     - `evento.numero_colonna_corrente == 9`
     - `evento.colonna_semplice is None`
     - `evento.stato_colonna is None`
     - `evento.numeri_segnati_colonna_ordinati is None`
     - `_indice_colonna_focus == 8`

9. `test_sposta_focus_colonna_destra_avanzata_movimento_normale`
   - confronto errato attuale: ricerca di stringhe `Colonna 4`, `Segnati:` o `vuota`
   - scenario: movimento riuscito
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonnaAvanzata`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 5`
     - confronto completo con `get_dati_visualizzazione_colonna_avanzata(4)`
     - `_indice_colonna_focus == 4`

10. `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione`
    - confronto errato attuale: `assertIn("Colonna 5:", risultato)`
    - scenario: movimento riuscito avanzato da focus colonna `None`
    - campi da verificare:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneColonnaAvanzata`
      - `evento.esito="mostra"`
      - `evento.numero_colonna_corrente == 6`
      - confronto completo con `get_dati_visualizzazione_colonna_avanzata(5)`
      - `_indice_colonna_focus == 5`

11. `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`
    - confronto errato attuale: ricerca nel renderer di `*numero` o di `Segnati: 0 su 0`
    - scenario: movimento riuscito avanzato su colonna con o senza numeri segnati
    - campi da verificare:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneColonnaAvanzata`
      - `evento.esito="mostra"`
      - confronto completo con `get_dati_visualizzazione_colonna_avanzata(4)`
      - se presente numero segnato, verificarne la presenza in
        `numeri_segnati_colonna_ordinati`
      - `_indice_colonna_focus == 4`

### Test gia' strutturati

Nel gruppo colonna destra non risultano test gia' strutturati nello stato
attuale del file. Questo elimina esclusioni preventive, ma non rimuove il
vincolo operativo: in fase implementativa l'agente dovra' leggere il corpo di
ogni test prima di modificarlo, per evitare regressioni simili a quelle emerse
nella tranche 2.

### Pattern di asserzione raccomandati

#### Errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, codice_atteso)
self.assertIsNone(risultato.evento)
```

#### Limite massimo base

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "massimo")
```

#### Limite massimo avanzato

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "massimo")
self.assertIsNone(risultato.evento.colonna_semplice)
self.assertIsNone(risultato.evento.stato_colonna)
self.assertIsNone(risultato.evento.numeri_segnati_colonna_ordinati)
```

#### Movimento riuscito base

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_colonna_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.colonna_semplice, self.cartella1.get_colonna_semplice(indice_atteso))
```

#### Movimento riuscito avanzato / colonna vuota / con segni

```python
dati_attesi = self.cartella1.get_dati_visualizzazione_colonna_avanzata(indice_atteso)

self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_colonna_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.colonna_semplice, dati_attesi[0])
self.assertEqual(risultato.evento.stato_colonna, dati_attesi[1])
self.assertEqual(risultato.evento.numeri_segnati_colonna_ordinati, dati_attesi[2])
```

### Rischi

- Confondere `numero_colonna_corrente` 1-based con `_indice_colonna_focus` 0-based.
- Applicare al metodo base asserzioni su campi disponibili solo nell'avanzata.
- Continuare a verificare stringhe del renderer invece del payload strutturato.
- Saltare la lettura del corpo del singolo test prima della modifica, ripetendo
  l'errore operativo emerso nella tranche 2.

### Vincoli accessibilità NVDA

- Nessun impatto UI diretto in questa fase: si documenta soltanto il contratto.
- Il modello dati conferma la scelta architetturale di feedback brevi sui limiti
  e payload leggibili dal renderer per screen reader.

### Raccomandazioni

- Procedere in due micro-fasi separate: base e avanzata.
- Prima di modificare un test, rileggere il suo corpo e confermare che sia ancora
  legacy nello stato reale del file.
- Usare `get_colonna_semplice()` e `get_dati_visualizzazione_colonna_avanzata()`
  come sorgenti di verita' per i payload attesi.

### File analizzati

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [bingo_game/players/giocatore_umano.py](bingo_game/players/giocatore_umano.py)
- [bingo_game/events/eventi_output_ui_umani.py](bingo_game/events/eventi_output_ui_umani.py)

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Condiviso