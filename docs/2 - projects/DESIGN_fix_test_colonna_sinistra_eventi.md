---
type: design
feature: fix_test_colonna_sinistra_eventi
agent: Agent-Design
status: DRAFT
version: v1.0
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: design
titolo: Design modernizzazione test colonna sinistra su eventi strutturati
data_creazione: 2026-03-29
agente: Agent-Design
stato: bozza
feature: fix_test_colonna_sinistra_eventi
versione_progetto: v1.0
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md

## Contenuto

### Idea in 3 righe

I test della navigazione colonna sinistra devono smettere di verificare testo
renderizzato e devono iniziare a verificare il contratto strutturato di
`EsitoAzione`.
La variante base e la variante avanzata condividono la stessa semantica di esito,
ma espongono eventi diversi e quindi richiedono assertion diverse.
La tranche 2 corregge solo i test colonna sinistra ancora legacy, lasciando
invariato il codice applicativo e i test gia' verdi.

### Attori e Concetti

#### Attori

- `GiocatoreUmano`
- `EsitoAzione`
- `EventoNavigazioneColonna`
- `EventoNavigazioneColonnaAvanzata`
- `Cartella`
- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)

#### Concetti

- Errore di prerequisito:
  - `ok=False`
  - `errore` valorizzato
  - `evento=None`

- Limite minimo:
  - `ok=True`
  - `errore=None`
  - `evento.esito == "limite"`
  - `evento.limite == "minimo"`

- Movimento riuscito base:
  - `ok=True`
  - `errore=None`
  - `evento` di tipo `EventoNavigazioneColonna`
  - `evento.esito == "mostra"`
  - `evento.colonna_semplice` contiene la colonna richiesta

- Movimento riuscito avanzato:
  - `ok=True`
  - `errore=None`
  - `evento` di tipo `EventoNavigazioneColonnaAvanzata`
  - `evento.esito == "mostra"`
  - `evento.colonna_semplice`, `evento.stato_colonna` e `evento.numeri_segnati_colonna_ordinati` descrivono la colonna

- Colonna vuota:
  - non e' errore
  - non e' limite
  - e' un normale caso di `esito="mostra"`
  - va verificata come dato, non come parola `vuota` nel renderer

### Flussi Concettuali

#### Flusso 1 — errore di prerequisito

1. Il test prepara un giocatore senza cartelle oppure con focus cartella rimosso.
2. Invoca il metodo base o avanzato verso sinistra.
3. Verifica un `EsitoAzione` di fallimento.
4. Controlla il codice errore specifico.
5. Verifica che `evento` sia `None`.

#### Flusso 2 — limite minimo

1. Il test porta il focus sulla prima colonna interna, indice `0`.
2. Invoca il metodo verso sinistra.
3. Verifica `ok=True` e `errore=None`.
4. Controlla il tipo evento corretto.
5. Verifica `esito="limite"` e `limite="minimo"`.
6. Conferma che `_indice_colonna_focus` non cambi.

#### Flusso 3 — movimento riuscito base

1. Il test prepara una colonna raggiungibile a sinistra.
2. Invoca `sposta_focus_colonna_sinistra`.
3. Verifica `EventoNavigazioneColonna` con `esito="mostra"`.
4. Confronta `numero_colonna_corrente` e `colonna_semplice` con i dati della cartella.
5. Verifica l'aggiornamento del focus interno.

#### Flusso 4 — movimento riuscito avanzato

1. Il test prepara una colonna raggiungibile a sinistra.
2. Invoca `sposta_focus_colonna_sinistra_avanzata`.
3. Verifica `EventoNavigazioneColonnaAvanzata` con `esito="mostra"`.
4. Confronta il triplo `colonna_semplice`, `stato_colonna`, `numeri_segnati_colonna_ordinati`.
5. Verifica l'aggiornamento del focus interno.

#### Flusso 5 — colonna vuota

1. Il test seleziona una colonna che, dopo lo spostamento, risulta priva di numeri.
2. Invoca il metodo base o avanzato.
3. Verifica che il risultato sia comunque `esito="mostra"`.
4. Nella base confronta `colonna_semplice` con `("-", "-", "-")` o con il valore reale della cartella.
5. Nell'avanzata confronta anche `stato_colonna` e `numeri_segnati_colonna_ordinati`.

### Decisioni Architetturali

#### Decisione 1 — testare il contratto stabile e non il renderer

La stringa prodotta da `__str__` su `EsitoAzione` e' solo una proiezione
compatibile col renderer legacy. Il contratto stabile del metodo e' il payload
strutturato, quindi i test devono fermarsi su `ok`, `errore`, `evento` e sui
campi dell'evento.

#### Decisione 2 — mantenere asserzioni distinte per base e avanzata

La versione base espone solo `colonna_semplice` e `limite`.
La versione avanzata espone anche `stato_colonna` e
`numeri_segnati_colonna_ordinati`.
Le asserzioni devono riflettere questa differenza invece di appiattirla.

#### Decisione 3 — usare il test avanzato gia' corretto come baseline locale

`test_sposta_focus_colonna_sinistra_avanzata_movimento_normale` e' gia'
allineato al contratto reale. Gli altri test della tranche devono copiarne il
principio: prima `EsitoAzione`, poi tipo evento, poi campi evento, poi stato
interno.

#### Decisione 4 — trattare la colonna vuota come dato valido

La parola `vuota` appartiene al renderer. Nel contratto corretto una colonna
vuota e' un caso `mostra` con celle vuote e, nella versione avanzata, con stato
coerente a zero numeri utili.

#### Decisione 5 — preservare l'auto-inizializzazione esistente

Quando il focus colonna e' `None`, i metodi sinistra inizializzano il focus e
poi si spostano dalla posizione centrale attesa. I test non devono riscrivere
questa logica: devono fotografarla controllando nuovo indice e numero colonna
utente.

### Pattern di asserzione

#### Pattern base — errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, codice_atteso)
self.assertIsNone(risultato.evento)
```

#### Pattern avanzato — errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, codice_atteso)
self.assertIsNone(risultato.evento)
```

#### Pattern base — limite minimo

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo")
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso_invariato)
```

#### Pattern avanzato — limite minimo

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo")
self.assertIsNone(risultato.evento.colonna_semplice)
self.assertIsNone(risultato.evento.stato_colonna)
self.assertIsNone(risultato.evento.numeri_segnati_colonna_ordinati)
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso_invariato)
```

#### Pattern base — movimento riuscito

```python
colonna_attesa = self.cartella1.get_colonna_semplice(indice_atteso)

self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_colonna_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.colonna_semplice, colonna_attesa)
self.assertIsNone(risultato.evento.limite)
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso)
```

#### Pattern avanzato — movimento riuscito e colonna vuota

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
self.assertIsNone(risultato.evento.limite)
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso)
```

#### Pattern avanzato — colonna con numeri segnati

```python
self.assertIn(numero_segnato, risultato.evento.numeri_segnati_colonna_ordinati)
self.assertEqual(risultato.evento.stato_colonna["numeri_segnati"], conteggio_atteso)
```

### Rischi e Vincoli

- Non toccare `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`, gia' verde.
- Non uscire da `docs/` in queste fasi.
- La versione base non espone `stato_colonna`: non bisogna inventare assertion su campi assenti.
- La colonna vuota va trattata come dato, non come parola nel renderer.
- Se il file resta nello stato corrente, `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` e' gia' strutturato e dovra' essere lasciato invariato.

### Criteri di accettazione

- Esiste un report che mappa i 9 test richiesti dalla tranche.
- Esiste un design che definisce il contratto atteso per base e avanzata.
- Esiste un piano con due micro-fasi committabili separatamente.
- Esiste un TODO operativo coerente col piano.
- L'implementazione successiva deve lasciare la suite verde.

### Coding plans correlati

- `docs/3 - coding plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md`

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato
