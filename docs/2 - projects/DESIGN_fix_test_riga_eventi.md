---
type: design
feature: fix_test_riga_eventi
agent: Agent-Design
status: REVIEWED
version: v1.0
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md
---

## Metadati

tipo: design
titolo: Design modernizzazione test riga su eventi strutturati
data_creazione: 2026-03-29
agente: Agent-Design
stato: bozza
feature: fix_test_riga_eventi
versione_progetto: v1.0
report: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md

## Contenuto

### Idea in 3 righe

I test della navigazione riga devono smettere di verificare frasi renderizzate
e devono iniziare a verificare il contratto strutturato di `EsitoAzione`.
Le versioni semplici e avanzate condividono la stessa logica di esito, ma
espongono eventi diversi e quindi richiedono assertion diverse.
La tranche 1 corregge solo i 20 test riga e lascia invariato il codice applicativo.

### Attori e Concetti

#### Attori

- `GiocatoreUmano`
- `EsitoAzione`
- `EventoNavigazioneRiga`
- `EventoNavigazioneRigaAvanzata`
- `Cartella`
- `tests/test_giocatore_umano.py`

#### Concetti

- Errore di prerequisito:
  - `ok=False`
  - `errore` valorizzato
  - `evento=None`

- Limite di navigazione:
  - `ok=True`
  - `errore=None`
  - `evento.esito == "limite"`
  - `evento.limite == "minimo"` oppure `"massimo"`

- Movimento riuscito semplice:
  - `ok=True`
  - `errore=None`
  - `evento` di tipo `EventoNavigazioneRiga`
  - `evento.esito == "mostra"`
  - `evento.riga_semplice` contiene la riga richiesta

- Movimento riuscito avanzato:
  - `ok=True`
  - `errore=None`
  - `evento` di tipo `EventoNavigazioneRigaAvanzata`
  - `evento.esito == "mostra"`
  - `evento.riga_semplice`, `evento.stato_riga` e `evento.numeri_segnati_riga_ordinati` descrivono la riga

- Numero riga utente:
  - `numero_riga_corrente` negli eventi e' 1-based
  - `_indice_riga_focus` interno resta 0-based

### Flussi Concettuali

#### Flusso 1 — errore

1. Il test prepara un giocatore senza cartelle oppure senza focus cartella.
2. Invoca il metodo di navigazione riga.
3. Verifica un `EsitoAzione` di fallimento.
4. Controlla il codice errore specifico.
5. Verifica l'assenza di evento.

#### Flusso 2 — limite

1. Il test porta il focus riga al bordo minimo o massimo.
2. Invoca il metodo coerente con la direzione.
3. Verifica `ok=True` e `errore=None`.
4. Controlla che l'evento sia di tipo corretto.
5. Controlla `esito="limite"` e `limite` coerente.
6. Verifica che lo stato interno non cambi.

#### Flusso 3 — movimento riuscito semplice

1. Il test prepara una riga raggiungibile.
2. Invoca il metodo semplice.
3. Verifica il tipo evento semplice.
4. Controlla `numero_riga_corrente` e `riga_semplice`.
5. Verifica l'aggiornamento del focus interno.

#### Flusso 4 — movimento riuscito avanzato

1. Il test prepara una riga raggiungibile.
2. Invoca il metodo avanzato.
3. Verifica il tipo evento avanzato.
4. Confronta i tre blocchi dati della riga.
5. Verifica l'aggiornamento del focus interno.

### Decisioni Architetturali

#### Decisione 1 — testare il contratto, non il renderer

Le stringhe come `Riga 0:` o `Sei alla prima riga` appartengono alla fase di
rendering. Il contratto stabile del metodo e' l'oggetto `EsitoAzione`.
Le nuove assertion devono quindi fermarsi su `ok`, `errore`, `evento` e sui
campi dell'evento.

#### Decisione 2 — differenziare semplice e avanzata in modo esplicito

La versione semplice usa `EventoNavigazioneRiga` e non espone stato o numeri
segnati. La versione avanzata usa `EventoNavigazioneRigaAvanzata` e deve essere
verificata anche sui campi aggiuntivi.

#### Decisione 3 — trattare i casi con segni come dati, non come simboli

Gli asterischi sono una rappresentazione visiva. Il test corretto deve
controllare `numeri_segnati_riga_ordinati` e `stato_riga`, non la presenza di
`*numero` dentro una stringa.

#### Decisione 4 — preservare l'asimmetria di auto-inizializzazione

`sposta_focus_riga_su_*` con focus `None` si ferma sulla riga `0`.
`sposta_focus_riga_giu_*` con focus `None` inizializza a `0` e poi sposta a `1`.
I test devono fotografare questa asimmetria, non normalizzarla artificialmente.

### Pattern di asserzione

#### Pattern per test di errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, codice_atteso)
self.assertIsNone(risultato.evento)
```

#### Pattern per test di limite

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, TipoEventoAtteso)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, limite_atteso)
```

#### Pattern per test di movimento riuscito semplice

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRiga)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_riga_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.riga_semplice, self.cartella1.get_riga_semplice(indice_atteso))
self.assertIsNone(risultato.evento.limite)
```

#### Pattern per test di movimento riuscito avanzato

```python
dati_attesi = self.cartella1.get_dati_visualizzazione_riga_avanzata(indice_atteso)

self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRigaAvanzata)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_riga_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.riga_semplice, dati_attesi[0])
self.assertEqual(risultato.evento.stato_riga, dati_attesi[1])
self.assertEqual(risultato.evento.numeri_segnati_riga_ordinati, dati_attesi[2])
self.assertIsNone(risultato.evento.limite)
```

#### Pattern per test con numeri segnati

```python
self.assertIn(numero_segnato, risultato.evento.numeri_segnati_riga_ordinati)
self.assertEqual(risultato.evento.stato_riga["numeri_segnati"], conteggio_atteso)
```

### Rischi e Vincoli

- Nessuna modifica al di fuori di `docs/` in questa fase.
- Nessuna implementazione dei test in questa sessione.
- Nessun intervento sui gruppi colonna o sui test gia' verdi.
- I riferimenti al numero riga devono sempre distinguere tra indice interno 0-based e numero utente 1-based.

### Criteri di accettazione

- Esiste un report che mappa tutti i 20 test del gruppo riga.
- Esiste un design che definisce il contratto atteso per i quattro metodi.
- Esiste un piano di implementazione con quattro micro-fasi committabili separatamente.
- Esiste un TODO operativo coerente col piano.
- L'implementazione successiva dovra' lasciare la suite verde.

### Coding plans correlati

- `docs/3 - coding plans/PLAN_fix_test_riga_eventi_v1.md`

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Approvato
- [ ] Archiviato
