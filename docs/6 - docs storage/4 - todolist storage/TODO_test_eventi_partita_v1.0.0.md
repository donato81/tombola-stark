---
type: todo
feature: test_eventi_partita
agent: Agent-Plan
status: COMPLETED
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_partita_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari di eventi_partita.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_partita
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_partita_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_partita.py per coprire factory methods e invarianti
delle quattro dataclass del Gruppo C in eventi_partita.py, senza toccare altri file di test
e senza modificare file in [bingo_game/](../../bingo_game/).

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Scadenza (opzionale)

Non definita

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md)
- Plan: [PLAN_test_eventi_partita_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_partita_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere eventi_partita.py

- [x] Leggere [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) e annotare i campi di ReclamoVittoria
- [x] Leggere [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) e annotare i campi di EventoReclamoVittoria
- [x] Leggere [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) e annotare i campi di EventoEsitoReclamoVittoria
- [x] Leggere [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) e annotare i campi di EventoFineTurno
- [x] Verificare in [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) i factory methods disponibili e i valori default

### Passo 2 - Leggere codici_errori.py

- [x] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) per identificare i codici errore validi
- [x] Verificare che VERIFICA_FALLITA sia disponibile come valore utilizzabile nei test di fallimento
- [x] Annotare il codice errore effettivamente scelto prima della scrittura del test

### Passo 3 - Creare tests/unit/test_eventi_partita.py

- [x] Creare tests/unit/test_eventi_partita.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Inserire TestReclamoVittoria come prima classe del file
- [x] Inserire TestEventoReclamoVittoria come seconda classe del file
- [x] Inserire TestEventoEsitoReclamoVittoria come terza classe del file
- [x] Inserire TestEventoFineTurno come quarta classe del file
- [x] Applicare la strategia FrozenInstanceError oppure AttributeError per i controlli di immutabilita'
- [x] Coprire solo gli scenari del Gruppo C

### Passo 4 - Verificare che tutti i test del file passino

- [x] Eseguire python -m unittest tests.unit.test_eventi_partita -q
- [x] Verificare che tests/unit/test_eventi_partita.py venga raccolto dal runner
- [x] Verificare che tutti i test del Gruppo C passino

### Passo 5 - Verificare assenza di pytest

- [x] Verificare che il file non contenga import di pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file usi solo unittest come libreria di test

### Passo 6 - Confermare il rispetto del perimetro

- [x] Verificare che nessun file esistente fuori da tests/unit/test_eventi_partita.py sia stato modificato
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che il file nuovo non includa scenari dei Gruppi A, B, D o E

## Note operative

- Nessun mock necessario.
- Nessuna dipendenza da wx, filesystem o avvio partita.
- Il file deve usare unittest.TestCase e asserzioni della standard library.
- Il codice errore dei casi negativi deve essere ricavato da [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) prima della scrittura del test.
- Il controllo di immutabilita' deve accettare FrozenInstanceError oppure AttributeError come esito corretto.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato