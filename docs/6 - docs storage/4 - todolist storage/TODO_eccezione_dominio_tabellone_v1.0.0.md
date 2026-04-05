---
type: todo
feature: eccezione_dominio_tabellone
agent: Agent-Plan
status: COMPLETED
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_eccezione_dominio_tabellone_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_eccezione_dominio_tabellone_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: todo_task
titolo: TODO eccezione di dominio del tabellone
data_creazione: 2026-03-31
agente: Agent-Plan
stato: completed
feature: eccezione_dominio_tabellone
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_eccezione_dominio_tabellone_v1.0.0.md
design: docs/2 - projects/DESIGN_eccezione_dominio_tabellone_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Descrizione task

Sostituire il `ValueError` generico del tabellone con una eccezione di dominio
specifica, aggiornare il punto di intercettazione in `partita.py` se necessario
e aggiungere il test unitario dedicato, senza toccare altre incoerenze del report.

### Priorita'

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: DESIGN_eccezione_dominio_tabellone_v1.0.0.md
- Plan: PLAN_eccezione_dominio_tabellone_v1.0.0.md
- Report: REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Checklist operativa

- [x] Definire `TabelloneNumeriEsauritiException` in `bingo_game/exceptions/tabellone_exceptions.py`
- [x] Far ereditare `TabelloneNumeriEsauritiException` da `Exception`
- [x] Aggiungere una docstring descrittiva a `TabelloneNumeriEsauritiException`
- [x] Importare `TabelloneNumeriEsauritiException` in `bingo_game/tabellone.py`
- [x] Sostituire `raise ValueError(...)` con `raise TabelloneNumeriEsauritiException(...)`
- [x] Mantenere invariato il messaggio testuale in `gestione_errore_numeri_terminati()`
- [x] Verificare la clausola di intercettazione in `bingo_game/partita.py`
- [x] Aggiornare `bingo_game/partita.py` da `except ValueError` a `except TabelloneNumeriEsauritiException` se necessario
- [x] Creare `tests/unit/test_tabellone_eccezioni.py`
- [x] Scrivere test `unittest` per il sollevamento di `TabelloneNumeriEsauritiException`
- [x] Verificare il messaggio testuale dell'eccezione nel nuovo test
- [x] Verificare che nessun test usi `pytest`
- [x] Eseguire `python -m unittest discover tests/unit`
- [x] Confermare zero failure e zero error sulla suite `tests/unit`

## Istruzioni operative

- Non modificare la logica di gioco del tabellone oltre al tipo di eccezione sollevata.
- Non modificare i test esistenti.
- Non toccare le incoerenze I-01, I-02, I-03, I-04, I-05, I-07.
- Non introdurre nuove eccezioni oltre a `TabelloneNumeriEsauritiException`.
- Non modificare la gerarchia delle eccezioni esistenti del progetto.

## Stato avanzamento

- [x] TODO redatto
- [x] Validazione umana
- [x] Approvato per implementazione
- [x] Implementazione avviata
- [x] Suite `tests/unit` verde (331 passed, 0 failed)

## Note di chiusura

- Modifiche applicate solo al perimetro I-06: nuova eccezione di dominio, sostituzione del raise nel tabellone, aggiornamento dell'intercettazione in partita e nuovo test unitario dedicato.
- Impatto runtime invariato: `Partita` continua a convertire l'errore del tabellone in `PartitaNumeriEsauritiException`.
