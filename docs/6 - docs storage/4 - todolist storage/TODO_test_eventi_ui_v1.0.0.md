---
type: todo
feature: test_eventi_ui
agent: Agent-Plan
status: COMPLETED
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_ui_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari di eventi_ui.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_ui
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_ui_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
per coprire il contratto delle due dataclass del Gruppo B in `eventi_ui.py`,
senza toccare altri file di test e senza modificare file in [bingo_game/](../../bingo_game/).

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Scadenza (opzionale)

Non definita

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md)
- Plan: [PLAN_test_eventi_ui_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_ui_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere eventi_ui.py

- [x] Leggere [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) e annotare i campi di `EventoFocusAutoImpostato`
- [x] Leggere [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) e annotare i campi di `EventoFocusCartellaImpostato`
- [x] Verificare in [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) il default `reset_riga_colonna=False`
- [x] Verificare in [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) l'uso di `frozen=True`

### Passo 2 - Creare tests/unit/test_eventi_ui.py

- [x] Creare [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
- [x] Usare esclusivamente `unittest` come libreria di test
- [x] Inserire `TestEventoFocusAutoImpostato` come prima classe del file
- [x] Inserire `TestEventoFocusCartellaImpostato` come seconda classe del file
- [x] Coprire gli scenari di costruzione, default e immutabilita' del Gruppo B

### Passo 3 - Verificare che tutti i test del file passino

- [x] Eseguire `python -m unittest tests.unit.test_eventi_ui -q`
- [x] Verificare che [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) venga raccolto dal runner
- [x] Verificare che tutti i test del Gruppo B passino

### Passo 4 - Verificare assenza di pytest

- [x] Verificare che il file non contenga import di pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file usi solo unittest come libreria di test

### Passo 5 - Confermare il rispetto del perimetro

- [x] Verificare che nessun file esistente fuori da [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) sia stato modificato
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che il file nuovo non includa scenari dei Gruppi A, C, D o E

## Note operative

- Nessun mock necessario.
- Nessuna fixture condivisa necessaria.
- Nessuna dipendenza da wx, filesystem o avvio partita.
- Il file deve usare `unittest.TestCase` e asserzioni della standard library.
- Il controllo di immutabilita' deve accettare `FrozenInstanceError` oppure `AttributeError` come esito corretto.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato