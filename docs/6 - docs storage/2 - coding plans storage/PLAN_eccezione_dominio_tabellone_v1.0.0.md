---
type: plan
feature: eccezione_dominio_tabellone
agent: Agent-Plan
status: COMPLETED
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_eccezione_dominio_tabellone_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per l'eccezione di dominio del tabellone
data_creazione: 2026-03-31
agente: Agent-Plan
stato: completed
feature: eccezione_dominio_tabellone
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_eccezione_dominio_tabellone_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Executive Summary

- Tipo intervento: introduzione eccezione di dominio + test unitario dedicato
- Priorita': P1
- Branch: main
- Versione task: v1.0.0
- Obiettivo: correggere esclusivamente la incoerenza I-06 del report
- Vincolo di chiusura: `python -m unittest discover tests/unit` verde con zero failure e zero error

### Problema e Obiettivo

`bingo_game/tabellone.py` usa ancora un `ValueError` generico nel metodo
`gestione_errore_numeri_terminati()`, in contrasto con il pattern di eccezioni
di dominio gia' adottato dal progetto. L'obiettivo del ciclo e' introdurre
`TabelloneNumeriEsauritiException`, usarla nel tabellone, mantenere invariato
il comportamento di `bingo_game/partita.py` e aggiungere un test unitario
diretto che verifichi tipo e messaggio dell'eccezione.

### File coinvolti

- MODIFY: `bingo_game/exceptions/tabellone_exceptions.py`
- MODIFY: `bingo_game/tabellone.py`
- MODIFY: `bingo_game/partita.py` solo se necessario per l'intercettazione
- CREATE: `tests/unit/test_tabellone_eccezioni.py`
- MODIFY: `docs/todo.md`
- CREATE: `docs/2 - projects/DESIGN_eccezione_dominio_tabellone_v1.0.0.md`
- CREATE: `docs/3 - coding plans/PLAN_eccezione_dominio_tabellone_v1.0.0.md`
- CREATE: `docs/5 - todolist/TODO_eccezione_dominio_tabellone_v1.0.0.md`

### Fasi sequenziali

#### Passo 1 - Definizione di `TabelloneNumeriEsauritiException`

Cosa si modifica:

- definire `TabelloneNumeriEsauritiException` in
  `bingo_game/exceptions/tabellone_exceptions.py`;
- farla ereditare da `Exception`;
- aggiungere una docstring descrittiva.

File coinvolto:

- `bingo_game/exceptions/tabellone_exceptions.py`

Risultato atteso:

- il tabellone dispone di una eccezione di dominio nominata e dedicata al caso
  di numeri esauriti.

#### Passo 2 - Aggiornamento del raise in `bingo_game/tabellone.py`

Cosa si modifica:

- importare `TabelloneNumeriEsauritiException`;
- sostituire `raise ValueError(...)` con
  `raise TabelloneNumeriEsauritiException(...)` nel metodo
  `gestione_errore_numeri_terminati()`;
- mantenere identico il messaggio testuale.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- il tabellone solleva l'eccezione di dominio corretta senza modificare la
  logica del metodo.

#### Passo 3 - Verifica e aggiornamento della clausola in `bingo_game/partita.py`

Cosa si modifica:

- verificare il blocco `try/except` che delega a `self.tabellone.estrai_numero()`;
- aggiornare la clausola da `except ValueError` a
  `except TabelloneNumeriEsauritiException` se necessario.

File coinvolto:

- `bingo_game/partita.py` solo se strettamente necessario

Risultato atteso:

- la partita continua a tradurre l'errore del tabellone in
  `PartitaNumeriEsauritiException`, mantenendo invariato il comportamento runtime.

#### Passo 4 - Creazione del test unitario dedicato

Cosa si modifica:

- creare `tests/unit/test_tabellone_eccezioni.py`;
- scrivere test `unittest` che verifichino:
  `gestione_errore_numeri_terminati()` solleva
  `TabelloneNumeriEsauritiException` e che il messaggio sia corretto;
- non usare mai `pytest`.

File coinvolto:

- `tests/unit/test_tabellone_eccezioni.py`

Risultato atteso:

- esiste copertura diretta dell'eccezione di dominio del tabellone.

#### Passo 5 - Esecuzione dell'intera suite per verifica invarianza

Cosa si modifica:

- nessun file sorgente;
- esecuzione della suite completa `tests/unit`.

File coinvolti:

- intera cartella `tests/unit`

Risultato atteso:

- comando `python -m unittest discover tests/unit` completato con zero failure e zero error;
- il ciclo si considera chiuso solo dopo questa verifica.

### Test Plan

- creare `tests/unit/test_tabellone_eccezioni.py`
- usare esclusivamente `unittest`
- verificare tipo di eccezione e messaggio testuale
- eseguire `python -m unittest discover tests/unit`

### Stato avanzamento

- [x] Piano redatto
- [x] Validazione umana
- [x] Approvato per implementazione
- [x] Implementazione avviata
- [x] Suite `tests/unit` verde (331 passed, 0 failed)
