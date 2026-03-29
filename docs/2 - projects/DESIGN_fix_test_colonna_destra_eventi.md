---
type: design
feature: fix_test_colonna_destra_eventi
agent: Agent-Design
status: REVIEWED
version: v1.0
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: design
titolo: Design modernizzazione test colonna destra su eventi strutturati
data_creazione: 2026-03-29
agente: Agent-Design
stato: revisionato
feature: fix_test_colonna_destra_eventi
versione_progetto: v1.0
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md

## Contenuto

### Idea in 3 righe

I test della navigazione colonna destra devono smettere di verificare il testo
renderizzato e devono iniziare a verificare il contratto strutturato di
`EsitoAzione`.
La variante base e la variante avanzata condividono la stessa semantica di esito,
ma espongono payload diversi e richiedono assertion distinte.
La tranche 3 corregge solo i test colonna destra ancora legacy, senza toccare il
codice applicativo e imponendo la rilettura del corpo di ogni test prima della
modifica.

### Obiettivo

Definire il perimetro e i criteri di modernizzazione dei test del gruppo colonna
destra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
sostituendo le assertion sul renderer con assertion su `ok`, `errore`, `evento`
e sui campi dell'evento corretto per i due metodi target.

### Contesto

La tranche 1 ha corretto il gruppo riga. La tranche 2 ha corretto il gruppo
colonna sinistra e ha mostrato un rischio operativo concreto: un test che si
voleva preservare e' stato comunque ritoccato durante la fase implementativa.

Per chiudere il ciclo resta il gruppo colonna destra, che nello stato attuale del
file contiene ancora solo test legacy. Il design deve quindi fissare non solo il
contratto tecnico da verificare, ma anche il vincolo procedurale di leggere il
corpo di ogni test prima di modificarlo.

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

- Limite massimo:
  - `ok=True`
  - `errore=None`
  - `evento.esito == "limite"`
  - `evento.limite == "massimo"`

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
  - `evento.colonna_semplice`, `evento.stato_colonna` e
    `evento.numeri_segnati_colonna_ordinati` descrivono la colonna

- Colonna vuota:
  - non e' errore
  - non e' limite
  - e' un normale caso di `esito="mostra"`
  - va verificata come dato, non come parola del renderer

### Componenti coinvolti

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [bingo_game/players/giocatore_umano.py](bingo_game/players/giocatore_umano.py)
- [bingo_game/events/eventi.py](bingo_game/events/eventi.py)
- [bingo_game/events/eventi_output_ui_umani.py](bingo_game/events/eventi_output_ui_umani.py)

### Flussi Concettuali

#### Flusso 1 — errore di prerequisito

1. Il test prepara un giocatore senza cartelle oppure con focus cartella rimosso.
2. Invoca il metodo base o avanzato verso destra.
3. Verifica un `EsitoAzione` di fallimento.
4. Controlla il codice errore specifico.
5. Verifica che `evento` sia `None`.

#### Flusso 2 — limite massimo

1. Il test porta il focus sull'ultima colonna interna, indice `8`.
2. Invoca il metodo verso destra.
3. Verifica `ok=True` e `errore=None`.
4. Controlla il tipo evento corretto.
5. Verifica `esito="limite"` e `limite="massimo"`.
6. Conferma che `_indice_colonna_focus` non cambi.

#### Flusso 3 — movimento riuscito base

1. Il test prepara una colonna raggiungibile a destra.
2. Invoca `sposta_focus_colonna_destra`.
3. Verifica `EventoNavigazioneColonna` con `esito="mostra"`.
4. Confronta `numero_colonna_corrente` e `colonna_semplice` con i dati della cartella.
5. Verifica l'aggiornamento del focus interno.

#### Flusso 4 — movimento riuscito avanzato

1. Il test prepara una colonna raggiungibile a destra.
2. Invoca `sposta_focus_colonna_destra_avanzata`.
3. Verifica `EventoNavigazioneColonnaAvanzata` con `esito="mostra"`.
4. Confronta il triplo `colonna_semplice`, `stato_colonna`, `numeri_segnati_colonna_ordinati`.
5. Verifica l'aggiornamento del focus interno.

#### Flusso 5 — auto-inizializzazione

1. Il test imposta `_indice_colonna_focus = None`.
2. Invoca il metodo base o avanzato.
3. Verifica il risultato strutturato di movimento, non il testo prodotto dal renderer.
4. Controlla l'indice finale reale imposto dal metodo corrente.
5. Confronta il payload con la colonna effettivamente raggiunta.

### Decisioni Architetturali

#### Decisione 1 — testare il contratto stabile e non il renderer

La stringa prodotta dal renderer o da eventuali conversioni legacy non e' il
contratto del metodo. I test devono fermarsi a `EsitoAzione` e ai campi degli
eventi di navigazione colonna.

#### Decisione 2 — mantenere asserzioni distinte per base e avanzata

La versione base espone solo `colonna_semplice` e `limite`.
La versione avanzata espone anche `stato_colonna` e
`numeri_segnati_colonna_ordinati`.
Le asserzioni devono rispettare questa differenza invece di appiattirla.

#### Decisione 3 — trattare il caso colonna vuota come dato valido

Il renderer puo' usare parole come `vuota`, ma il contratto corretto e' un
evento `mostra` con payload coerente alla colonna selezionata.

#### Decisione 4 — fotografare il comportamento reale di auto-inizializzazione

La tranche non cambia la logica produttiva. I test devono quindi documentare la
colonna effettivamente raggiunta dai metodi nello stato attuale del codice:

- base: da focus `None` si arriva alla colonna utente 5
- avanzata: da focus `None` si arriva alla colonna utente 6

#### Decisione 5 — imporre una guardia procedurale esplicita

Prima di modificare un test della tranche 3, l'agente implementativo deve leggerne
il corpo e verificare che sia ancora legacy. Questo vincolo e' obbligatorio anche
se il report corrente segnala che tutti gli 11 test risultano legacy.

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

#### Pattern base — limite massimo

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonna)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "massimo")
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso_invariato)
```

#### Pattern avanzato — limite massimo

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "massimo")
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

#### Pattern avanzato — movimento riuscito e colonna con segni o vuota

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

### Vincoli

- Non uscire da `docs/` in questa sessione.
- Nessuna scrittura di codice test nella fase 1-3.
- L'implementazione successiva deve leggere il corpo di ogni test prima della modifica.
- Se durante l'implementazione uno o piu' test risultassero gia' strutturati,
  devono essere lasciati invariati e registrati nel TODO.
- La base non espone `stato_colonna` o `numeri_segnati_colonna_ordinati`.
- La differenza tra `direzione="successiva"` e `direzione="destra"` deve essere
  considerata parte del contratto osservabile, se si decide di verificarla.

### Rischi e Vincoli

- Confondere colonna utente 1-based e indice interno 0-based.
- Sbagliare la colonna attesa nei casi di auto-inizializzazione.
- Reintrodurre assertion su testo nei casi colonna vuota o con segni.
- Toccare test che nel frattempo fossero gia' stati strutturati da altri cambiamenti.

### Criteri di accettazione

- Esiste un report che mappa tutti gli 11 test del gruppo destra.
- Esiste un design che definisce il contratto atteso per base e avanzata.
- Esiste un piano con due micro-fasi committabili separate.
- Esiste un TODO operativo coerente col piano.
- Il piano contiene una nota esplicita che impone la lettura del corpo di ogni test
  prima di modificarlo nella fase implementativa.

### Coding plans correlati

- `docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md`

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Approvato
- [ ] Archiviato