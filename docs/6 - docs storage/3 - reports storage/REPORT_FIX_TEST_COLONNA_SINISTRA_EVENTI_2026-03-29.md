---
type: report
feature: fix_test_colonna_sinistra_eventi
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Report analisi tranche 2 modernizzazione test colonna sinistra
---

## Metadati

tipo: report
titolo: Report analisi tranche 2 modernizzazione test colonna sinistra
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: bozza
feature: fix_test_colonna_sinistra_eventi
versione_target: v1.0

## Contenuto

### Trigger

Dopo la chiusura della tranche riga restano 9 test del gruppo colonna sinistra
in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) ancora ancorati
al testo renderizzato invece che al contratto strutturato dei metodi.

Il test gia' corretto da usare come modello locale e':

- `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`

### Sommario esecutivo

I 9 test target sono tutti disallineati rispetto al contratto reale dei metodi.
Sia la versione base `sposta_focus_colonna_sinistra` sia la versione avanzata
`sposta_focus_colonna_sinistra_avanzata` restituiscono `EsitoAzione` grezzo.
Non restituiscono stringhe.

Questo significa che:

- `assertEqual(risultato, "testo")` e' concettualmente sbagliato
- `assertIn("Colonna X:", risultato)` e' un controllo sul renderer, non sul contratto
- il test corretto deve verificare `ok`, `errore`, `evento` e i campi dell'evento

La variante base usa `EventoNavigazioneColonna`.
La variante avanzata usa `EventoNavigazioneColonnaAvanzata`.

### Componenti coinvolti

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [bingo_game/players/giocatore_umano.py](bingo_game/players/giocatore_umano.py)
- [bingo_game/events/eventi.py](bingo_game/events/eventi.py)
- [bingo_game/events/eventi_output_ui_umani.py](bingo_game/events/eventi_output_ui_umani.py)
- [docs/2 - projects/DESIGN_fix_test_riga_eventi.md](docs/2%20-%20projects/DESIGN_fix_test_riga_eventi.md)
- [docs/3 - coding plans/PLAN_fix_test_riga_eventi_v1.md](docs/3%20-%20coding%20plans/PLAN_fix_test_riga_eventi_v1.md)

### Contratti osservabili

#### Versione base

Metodo: `sposta_focus_colonna_sinistra`

- ritorna `EsitoAzione`
- in errore: `ok=False`, `errore` valorizzato, `evento=None`
- in limite minimo: `ok=True`, `errore=None`, `evento` di tipo `EventoNavigazioneColonna`, `esito="limite"`, `limite="minimo"`
- in movimento riuscito: `ok=True`, `errore=None`, `evento` di tipo `EventoNavigazioneColonna`, `esito="mostra"`
- campi specifici osservabili:
  - `numero_colonna_corrente` 1-based
  - `colonna_semplice`
  - `limite`

#### Versione avanzata

Metodo: `sposta_focus_colonna_sinistra_avanzata`

- ritorna `EsitoAzione`
- in errore: `ok=False`, `errore` valorizzato, `evento=None`
- in limite minimo: `ok=True`, `errore=None`, `evento` di tipo `EventoNavigazioneColonnaAvanzata`, `esito="limite"`, `limite="minimo"`
- in movimento riuscito: `ok=True`, `errore=None`, `evento` di tipo `EventoNavigazioneColonnaAvanzata`, `esito="mostra"`
- campi specifici osservabili:
  - `numero_colonna_corrente` 1-based
  - `colonna_semplice`
  - `stato_colonna`
  - `numeri_segnati_colonna_ordinati`
  - `limite`

### Differenza base vs avanzata

- La base espone solo il contenuto semplice della colonna e il limite.
- L'avanzata espone anche lo stato aggregato della colonna e l'elenco ordinato dei numeri segnati.
- La colonna vuota non e' un errore in nessuna delle due varianti: e' un normale caso di `esito="mostra"`.

### Diagnosi puntuale dei 9 test

#### Gruppo semplice — sposta_focus_colonna_sinistra

1. `test_sposta_focus_colonna_sinistra_semplice_cartella_mancante`
   - confronto errato attuale: `assertEqual` contro stringa utente
   - scenario: errore
   - campi da verificare:
     - scenario senza cartelle: `ok=False`, `errore="CARTELLE_NESSUNA_ASSEGNATA"`, `evento=None`
     - scenario focus cartella `None`: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`, `evento=None`

2. `test_sposta_focus_colonna_sinistra_semplice_prima_colonna`
   - confronto errato attuale: `assertEqual` contro stringa di limite
   - scenario: limite minimo
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="limite"`
     - `evento.limite="minimo"`
     - `evento.numero_colonna_corrente == 1`
     - `_indice_colonna_focus == 0`

3. `test_sposta_focus_colonna_sinistra_semplice_movimento_normale`
   - confronto errato attuale: `assertIn("Colonna 4:", risultato)` e ricerca numeri/testi nel renderer
   - scenario: movimento riuscito
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 5`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(4)`
     - `_indice_colonna_focus == 4`

4. `test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione`
   - confronto errato attuale: `assertIn("Colonna 3:", risultato)`
   - scenario: movimento riuscito da focus colonna `None`
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 4`
     - `evento.colonna_semplice == self.cartella1.get_colonna_semplice(3)`
     - `_indice_colonna_focus == 3`

5. `test_sposta_focus_colonna_sinistra_semplice_colonna_vuota`
   - confronto errato attuale: `assertIn("Colonna 3:", risultato)`
   - scenario: colonna vuota trattata come movimento riuscito
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonna`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 4`
     - se vuota: `evento.colonna_semplice == ("-", "-", "-")`
     - `_indice_colonna_focus == 3`

#### Gruppo avanzato — sposta_focus_colonna_sinistra_avanzata

6. `test_sposta_focus_colonna_sinistra_avanzata_cartella_mancante`
   - confronto errato attuale: `assertEqual` contro stringa utente
   - scenario: errore
   - campi da verificare:
     - scenario senza cartelle: `ok=False`, `errore="CARTELLE_NESSUNA_ASSEGNATA"`, `evento=None`
     - scenario focus cartella `None`: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`, `evento=None`

7. `test_sposta_focus_colonna_sinistra_avanzata_prima_colonna`
   - confronto errato attuale: `assertEqual` contro stringa di limite
   - scenario: limite minimo
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonnaAvanzata`
     - `evento.esito="limite"`
     - `evento.limite="minimo"`
     - `evento.colonna_semplice is None`
     - `evento.stato_colonna is None`
     - `evento.numeri_segnati_colonna_ordinati is None`
     - `_indice_colonna_focus == 0`

8. `test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione`
   - confronto errato attuale: `assertIn("Colonna 3:", risultato)`
   - scenario: movimento riuscito avanzato da focus colonna `None`
   - campi da verificare:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneColonnaAvanzata`
     - `evento.esito="mostra"`
     - `evento.numero_colonna_corrente == 4`
     - confronto completo del triplo restituito da `get_dati_visualizzazione_colonna_avanzata(3)`
     - `_indice_colonna_focus == 3`

9. `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`
   - stato attuale: gia' convertito in strutturato durante la validazione della tranche precedente
   - conseguenza: il report lo registra come target richiesto dalla tranche ma segnala che, allo stato attuale del file, non richiede ulteriori modifiche
   - vincolo operativo: non ritoccarlo nella successiva implementazione se il contenuto rimane invariato

### Pattern di asserzione raccomandati

#### Errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, codice_atteso)
self.assertIsNone(risultato.evento)
```

#### Limite base

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo")
```

#### Limite avanzato

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo")
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

#### Movimento riuscito avanzato / colonna vuota / segni

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

### Rischi e vincoli

- Non toccare `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`, gia' verde.
- Non uscire da `docs/` in queste fasi.
- La versione base non espone `stato_colonna`: non bisogna inventare assertion su campi assenti.
- La colonna vuota va trattata come dato strutturato, non come parola nel renderer.

### Conclusione

La tranche 2 e' ben delimitata. Dei 9 test richiesti, 8 sono certamente ancora da
modernizzare. Il nono, `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`,
risulta gia' strutturato nello stato attuale del file e dovra' essere preservato.
