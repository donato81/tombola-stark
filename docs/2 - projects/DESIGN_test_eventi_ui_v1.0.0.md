---
type: design
feature: test_eventi_ui
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per le dataclass di eventi_ui.py
data_creazione: 2026-03-30
agente: Agent-Design
stato: bozza
feature: test_eventi_ui
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task introduce un solo file di test, [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py),
dedicato alle due dataclass frozen del modulo eventi_ui.py.
L'obiettivo e' congelare il contratto strutturale degli eventi di focus,
usando esclusivamente unittest e asserzioni della standard library.

### Obiettivo

Definire il design tecnico del file [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
limitando il perimetro al solo Gruppo B del report e alle due dataclass del modulo
[bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py):

- `EventoFocusAutoImpostato`
- `EventoFocusCartellaImpostato`

Il design deve fissare:

- la struttura interna del file di test
- le due classi di test, una per dataclass
- gli scenari esatti da coprire, con logica delle asserzioni in stile unittest
- le dipendenze di import necessarie
- il vincolo esplicito sull'uso di unittest
- i criteri di completamento verificabili

### Contesto

Il report di riferimento, [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md),
ha gia' stabilito che il Gruppo B copre il modulo eventi_ui.py e riguarda due dataclass
frozen a bassa complessita', senza dipendenze da wx, filesystem o avvio partita.

Queste due dataclass sono fondamentali per la logica di focus e per i test successivi del
Gruppo D, quindi il loro contratto deve essere verificato in isolamento prima di estendere
la copertura ad aree piu' ricche di logica.

Il task resta volutamente confinato al Gruppo B. Non include scenari relativi a:

- test di contratto dei moduli `codici_*.py`
- dataclass e factory di [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py)
- logica di [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py)
- classi di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)

### Attori e Concetti

#### Attori

- file di test [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
- dataclass `EventoFocusAutoImpostato`
- dataclass `EventoFocusCartellaImpostato`
- `unittest` come libreria obbligatoria per i test
- `FrozenInstanceError` come segnale primario di immutabilita'

#### Concetti

- Contratto di costruzione:
  i campi obbligatori devono essere memorizzati senza trasformazioni inattese.
- Immutabilita' della dataclass:
  essendo `frozen=True`, un tentativo di riassegnazione deve fallire.
- Valori ammessi di `tipo_focus`:
  il design verifica i valori dichiarati dal contratto documentale del report
  attraverso istanze costruite con `cartella`, `riga` e `colonna`.
- Default esplicito:
  `reset_riga_colonna` deve risultare `False` quando non viene passato.

### Componenti coinvolti

- File di produzione di riferimento: [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py)
- File da creare: [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

Nessun altro file di test e nessun altro modulo del package `events` rientrano
nel perimetro di modifica di questo design.

### Flussi Concettuali

#### Flusso 1 - Costruzione di EventoFocusAutoImpostato

1. Il test costruisce un'istanza con `tipo_focus="cartella"` e `indice=0`.
2. Verifica con `self.assertEqual` che i campi siano memorizzati correttamente.
3. Ripete la costruzione per i valori ammessi `riga` e `colonna`.

#### Flusso 2 - Verifica immutabilita' di EventoFocusAutoImpostato

1. Il test costruisce un'istanza valida.
2. Tenta di riassegnare uno dei campi.
3. Verifica con `self.assertRaises` che venga sollevato `FrozenInstanceError`
   oppure `AttributeError` come fallback accettabile del contratto.

#### Flusso 3 - Costruzione di EventoFocusCartellaImpostato

1. Il test costruisce un'istanza con i soli campi obbligatori.
2. Verifica con `self.assertEqual` e `self.assertFalse` il valore dei campi e del default.
3. Costruisce una seconda istanza con `reset_riga_colonna=True` e verifica con `self.assertTrue`.

#### Flusso 4 - Verifica immutabilita' di EventoFocusCartellaImpostato

1. Il test costruisce un'istanza valida.
2. Tenta di riassegnare un campo.
3. Verifica con `self.assertRaises` che venga sollevato `FrozenInstanceError`
   oppure `AttributeError`.

### Decisioni Architetturali

#### Decisione 1 - Un solo file di test, due classi ordinate per dataclass

Il file [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) conterra'
esattamente due classi di test, nell'ordine fissato dal task:

1. `TestEventoFocusAutoImpostato`
2. `TestEventoFocusCartellaImpostato`

Questa scelta mantiene il file piccolo, leggibile e strettamente aderente al perimetro.

#### Decisione 2 - unittest e' la sola libreria ammessa

Il file deve usare esclusivamente `unittest` della standard library.

Il design esclude esplicitamente:

- `import pytest`
- fixture pytest
- marker pytest come libreria di test

Le asserzioni previste devono essere espresse con primitive unittest, per esempio:

- `self.assertEqual`
- `self.assertFalse`
- `self.assertTrue`
- `self.assertRaises`
- `self.assertIsNone` se necessario

#### Decisione 3 - Gli scenari restano strutturali, non semantici

Le due dataclass non implementano logica di business; quindi il test deve fermarsi a:

- costruzione corretta dell'istanza
- preservazione dei campi
- verifica del default dichiarato
- immutabilita' garantita da `frozen=True`

Non sono previsti test di integrazione con `GiocatoreUmano` in questo gruppo.

#### Decisione 4 - Verifica dei valori ammessi di tipo_focus tramite costruzione esplicita

Per `EventoFocusAutoImpostato` la verifica dei tipi ammessi non deve usare typing runtime
avanzato, ma costruzioni esplicite con i tre valori dichiarati dal report:

- `cartella`
- `riga`
- `colonna`

Le asserzioni devono verificare che ogni valore venga conservato correttamente nel campo.

#### Decisione 5 - L'immutabilita' accetta FrozenInstanceError o AttributeError

Il contratto richiesto dal task ammette che il tentativo di riassegnazione su una dataclass
frozen sollevi `FrozenInstanceError` oppure `AttributeError`.

Le asserzioni di immutabilita' devono quindi essere progettate in modo da accettare entrambe
le eccezioni come esito corretto, pur privilegiando il caso standard `FrozenInstanceError`.

### Struttura interna attesa del file di test

Il file [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) dovra' essere organizzato in questo ordine:

1. import `unittest`
2. import `FrozenInstanceError` da `dataclasses`
3. import delle due dataclass dal modulo target
4. definizione di `TestEventoFocusAutoImpostato(unittest.TestCase)`
5. definizione di `TestEventoFocusCartellaImpostato(unittest.TestCase)`
6. eventuale entry point `unittest.main()` se coerente con lo stile adottato nel repository

Non sono previsti helper privati, fixture condivise o setup complessi.

### Scenari esatti da coprire per classe

#### TestEventoFocusAutoImpostato

- Costruzione con `tipo_focus="cartella"` e `indice=0`.
- Costruzione con `tipo_focus="riga"` e verifica del valore memorizzato.
- Costruzione con `tipo_focus="colonna"` e verifica del valore memorizzato.
- Immutabilita': tentativo di assegnazione a `tipo_focus` o `indice` con attesa di `FrozenInstanceError` oppure `AttributeError`.

Forma attesa delle asserzioni:

- `self.assertEqual` per i campi costruiti
- `self.assertRaises` per l'immutabilita'

#### TestEventoFocusCartellaImpostato

- Costruzione base con i campi obbligatori `id_giocatore`, `nome_giocatore`, `numero_cartella`, `indice_cartella`.
- Verifica che `reset_riga_colonna` abbia default `False` quando omesso.
- Costruzione con `reset_riga_colonna=True`.
- Immutabilita': tentativo di assegnazione a uno dei campi con attesa di `FrozenInstanceError` oppure `AttributeError`.

Forma attesa delle asserzioni:

- `self.assertEqual` per i campi obbligatori
- `self.assertFalse` per il default `False`
- `self.assertTrue` per il caso esplicito a `True`
- `self.assertRaises` per l'immutabilita'

### Dipendenze di import necessarie

Import di supporto previsti:

- `import unittest`
- `from dataclasses import FrozenInstanceError`

Import modulo target previsti:

- `from bingo_game.events.eventi_ui import EventoFocusAutoImpostato`
- `from bingo_game.events.eventi_ui import EventoFocusCartellaImpostato`

Non sono previste dipendenze da:

- pytest come libreria di test
- wxPython
- mock
- filesystem
- controller o avvio partita

### Vincolo esplicito su unittest

Il design richiede in modo vincolante che il file [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
sia implementato con `unittest` e non con `pytest`.

L'uso di pytest e' consentito solo come eventuale runner esterno del repository,
non come libreria di test nel contenuto del file.

### Rischi e Vincoli

- Vincolo di scope: nessuno scenario oltre `eventi_ui.py` puo' entrare in questo file.
- Vincolo di libreria: il file non deve contenere `import pytest`.
- Rischio di drift: introdurre test di integrazione o di comportamento di altri moduli violerebbe il Gruppo B.
- Rischio di incompiutezza: omettere il controllo del default `reset_riga_colonna=False` lascerebbe scoperto un elemento dichiarato dal report.
- Rischio di falsa sicurezza: verificare solo la costruzione senza testare l'immutabilita' non basterebbe a congelare il contratto delle dataclass frozen.

### Coding plans correlati

- [PLAN_test_eventi_ui_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_ui_v1.0.0.md)

### Criteri di completamento verificabili

Il design si considera soddisfatto quando il futuro file
[tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py):

- contiene esattamente due classi di test, una per ciascuna dataclass del Gruppo B
- usa `unittest.TestCase` in modo uniforme
- verifica la costruzione di `EventoFocusAutoImpostato` con `cartella`, `riga` e `colonna`
- verifica l'immutabilita' di entrambe le dataclass con `self.assertRaises`
- verifica il default `reset_riga_colonna=False`
- verifica il caso esplicito `reset_riga_colonna=True`
- non introduce pytest come libreria di test
- non introduce scenari dei Gruppi A, C, D o E

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato