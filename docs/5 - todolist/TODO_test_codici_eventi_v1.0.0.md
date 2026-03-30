---
type: todo
feature: test_codici_eventi
agent: Agent-Plan
status: DRAFT
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_codici_eventi_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per test di contratto sui moduli codici_*.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: test_codici_eventi
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_codici_eventi_v1.0.0.md
design: docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
per coprire il contratto dei sette moduli codici_*.py del Gruppo A, senza toccare
altri file di test e senza modificare file in [bingo_game/](../../bingo_game/).

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Scadenza (opzionale)

Non definita

### Riferimento project/plan padre

- Project: [DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md)
- Plan: [PLAN_test_codici_eventi_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_codici_eventi_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere i sette moduli codici_*.py

- [ ] Leggere [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py) e annotare tutte le costanti esportate
- [ ] Leggere [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py) e annotare tutte le costanti esportate
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare i tre gruppi Literal piu' il contratto aggregato
- [ ] Leggere [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py) e annotare costante Final e Literal associato
- [ ] Leggere [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py) e annotare tutte le costanti Final e il Literal associato
- [ ] Leggere [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py) e annotare tutte le costanti Final e il Literal associato
- [ ] Leggere [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) e annotare l'insieme completo delle chiavi del Literal

### Passo 2 - Creare tests/unit/test_codici_eventi.py

- [ ] Creare [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
- [ ] Aggiungere il marcatore unit coerente con gli standard del repository
- [ ] Inserire la classe test per `codici_configurazione` come prima classe del file
- [ ] Inserire la classe test per `codici_controller` come seconda classe del file
- [ ] Inserire la classe test per `codici_errori` come terza classe del file
- [ ] Inserire la classe test per `codici_eventi` come quarta classe del file
- [ ] Inserire la classe test per `codici_loop` come quinta classe del file
- [ ] Inserire la classe test per `codici_messaggi_sistema` come sesta classe del file
- [ ] Inserire la classe test per `codici_output_ui_umani` come settima classe del file

### Passo 3 - Verificare con pytest -m unit

- [ ] Eseguire `pytest -m unit`
- [ ] Verificare che [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) venga raccolto dal runner
- [ ] Verificare che tutti i test del Gruppo A passino

### Passo 4 - Confermare il rispetto del perimetro

- [ ] Verificare che nessun file esistente fuori da [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) sia stato modificato
- [ ] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [ ] Verificare che il file nuovo non includa scenari dei Gruppi B, C, D o E

## Note operative

- Nessun mock necessario.
- Nessuna fixture condivisa necessaria.
- Nessuna dipendenza da wx, filesystem o avvio partita.
- Per [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) usare verifiche di unione e intersezione tra insiemi, non confronti nominali costante per costante.
- Per [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) verificare contenuto e cardinalita' del Literal, dato che il modulo non esporta una costante Final per ogni chiave.

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato