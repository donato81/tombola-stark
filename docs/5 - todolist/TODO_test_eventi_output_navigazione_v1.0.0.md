---
type: todo
feature: test_eventi_output_navigazione
agent: Agent-Plan
status: DONE
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_output_navigazione_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari degli eventi output navigazione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_output_navigazione
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_output_navigazione_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_output_navigazione.py per coprire il perimetro E2 di eventi_output_ui_umani.py senza modificare file in [bingo_game/](../../bingo_game/) e senza toccare altri file di test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_output_navigazione_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md)
- Plan: [PLAN_test_eventi_output_navigazione_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_output_navigazione_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere il perimetro E2

- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoNavigazioneRiga
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoNavigazioneRigaAvanzata
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoNavigazioneColonna
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoNavigazioneColonnaAvanzata
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoVaiARigaAvanzata e EventoVaiAColonnaAvanzata

### Passo 2 - Creare tests/unit/test_eventi_output_navigazione.py

- [x] Creare tests/unit/test_eventi_output_navigazione.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Verificare in EventoNavigazioneRiga il ramo mostra
- [x] Verificare in EventoNavigazioneRiga il ramo limite_minimo
- [x] Verificare in EventoNavigazioneRiga il ramo limite_massimo
- [x] Verificare in EventoNavigazioneRigaAvanzata il ramo mostra con stato_riga
- [x] Verificare in EventoNavigazioneRigaAvanzata i rami limite
- [x] Verificare in EventoNavigazioneColonna il ramo mostra
- [x] Verificare in EventoNavigazioneColonna il ramo limite_minimo
- [x] Verificare in EventoNavigazioneColonna il ramo limite_massimo
- [x] Verificare in EventoNavigazioneColonnaAvanzata il ramo mostra con stato_colonna
- [x] Verificare in EventoNavigazioneColonnaAvanzata i rami limite
- [x] Verificare in EventoVaiARigaAvanzata la coercizione a tuple e i campi avanzati
- [x] Verificare in EventoVaiAColonnaAvanzata la coercizione a tuple e i campi avanzati

### Passo 3 - Verifiche del file

- [x] Eseguire python -m unittest tests.unit.test_eventi_output_navigazione -q
- [x] Verificare che il file non contenga import pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file non usi MagicMock
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- Tutti i pacchetti avanzati devono essere costruiti con dict e tuple reali.
- Non usare mock o fixture esterne in questo sottogruppo.
- Il file deve restare confinato al solo perimetro E2.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
