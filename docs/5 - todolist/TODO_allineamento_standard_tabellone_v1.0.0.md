---
type: todo
feature: allineamento_standard_tabellone
agent: Agent-Plan
status: DRAFT
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_allineamento_standard_tabellone_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_allineamento_standard_tabellone_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: todo_task
titolo: TODO allineamento standard di bingo_game/tabellone.py
data_creazione: 2026-03-31
agente: Agent-Plan
stato: draft
feature: allineamento_standard_tabellone
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_allineamento_standard_tabellone_v1.0.0.md
design: docs/2 - projects/DESIGN_allineamento_standard_tabellone_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Descrizione task

Allineare `bingo_game/tabellone.py` agli standard formali del progetto, correggendo esclusivamente le incoerenze I-01, I-02, I-03, I-04 e I-05 del report di riferimento, senza modificare la logica di gioco.

### Priorita'

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: DESIGN_allineamento_standard_tabellone_v1.0.0.md
- Plan: PLAN_allineamento_standard_tabellone_v1.0.0.md
- Report: REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Checklist operativa

- [ ] Aggiungere `from __future__ import annotations` in testa a `bingo_game/tabellone.py`
- [ ] Aggiungere gli import di typing necessari in `bingo_game/tabellone.py`
- [ ] Annotare `self.numeri_disponibili` come `set[int]` in `_inizializza_tabellone()`
- [ ] Annotare `self.numeri_estratti` come `set[int]` in `_inizializza_tabellone()`
- [ ] Annotare `self.ultimo_numero_estratto` come `int | None` in `_inizializza_tabellone()`
- [ ] Annotare `self.storico_estrazioni` come `list[int]` in `_inizializza_tabellone()`
- [ ] Aggiungere l'annotazione di ritorno a `__init__`
- [ ] Aggiungere l'annotazione di ritorno a `_inizializza_tabellone`
- [ ] Aggiungere l'annotazione di ritorno a `estrai_numero`
- [ ] Aggiungere l'annotazione di ritorno a `reset_tabellone`
- [ ] Aggiungere l'annotazione di ritorno a `numeri_terminati`
- [ ] Aggiungere l'annotazione di ritorno a `gestione_errore_numeri_terminati`
- [ ] Aggiungere l'annotazione di ritorno a `get_conteggio_estratti`
- [ ] Aggiungere l'annotazione di ritorno a `get_conteggio_disponibili`
- [ ] Aggiungere l'annotazione di ritorno a `get_numeri_estratti`
- [ ] Aggiungere l'annotazione di ritorno a `get_numeri_disponibili`
- [ ] Aggiungere l'annotazione di ritorno a `get_percentuale_avanzamento`
- [ ] Aggiungere l'annotazione di ritorno a `get_ultimo_numero_estratto`
- [ ] Aggiungere l'annotazione di ritorno a `get_stato_tabellone`
- [ ] Aggiungere la module docstring in apertura di `bingo_game/tabellone.py`
- [ ] Aggiungere la class docstring a `Tabellone`
- [ ] Aggiungere una docstring a `_inizializza_tabellone`
- [ ] Aggiungere una docstring a `estrai_numero`
- [ ] Aggiungere una docstring a `reset_tabellone`
- [ ] Aggiungere una docstring a `numeri_terminati`
- [ ] Aggiungere una docstring a `gestione_errore_numeri_terminati`
- [ ] Aggiungere una docstring a `get_numeri_estratti`
- [ ] Aggiungere una docstring a `get_numeri_disponibili`
- [ ] Verificare che I-06 resti invariata e non venga toccata
- [ ] Verificare che I-07 resti invariata e non venga toccata
- [ ] Eseguire `python -m unittest discover tests/unit`
- [ ] Confermare zero failure e zero error sulla suite `tests/unit`

## Istruzioni operative

- Non modificare la logica di gioco.
- Non modificare altri file Python oltre a `bingo_game/tabellone.py`.
- Non creare nuovi test.
- Non modificare test esistenti.
- Non toccare `bingo_game/exceptions/tabellone_exceptions.py`.

## Stato avanzamento

- [x] TODO redatto
- [ ] Validazione umana
- [ ] Approvato per implementazione
- [ ] Implementazione avviata
- [ ] Suite `tests/unit` verde
