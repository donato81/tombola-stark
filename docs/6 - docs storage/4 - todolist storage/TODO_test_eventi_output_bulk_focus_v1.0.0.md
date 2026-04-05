---
type: todo
feature: test_eventi_output_bulk_focus
agent: Agent-Plan
status: DONE
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_output_bulk_focus_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari degli eventi output bulk e focus
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_output_bulk_focus
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_output_bulk_focus_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_output_bulk_focus.py per coprire il perimetro E5 di eventi_output_ui_umani.py senza modificare file in [bingo_game/](../../bingo_game/) e senza toccare altri file di test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_output_bulk_focus_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md)
- Plan: [PLAN_test_eventi_output_bulk_focus_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_output_bulk_focus_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere il perimetro E5

- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoVisualizzaTutteCartelleSemplice
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoVisualizzaTutteCartelleAvanzata
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoStatoFocusCorrente

### Passo 2 - Creare tests/unit/test_eventi_output_bulk_focus.py

- [x] Creare tests/unit/test_eventi_output_bulk_focus.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Usare unittest.mock.MagicMock solo per EventoVisualizzaTutteCartelleSemplice
- [x] Usare unittest.mock.MagicMock solo per EventoVisualizzaTutteCartelleAvanzata
- [x] Verificare in EventoVisualizzaTutteCartelleSemplice totale_cartelle, numerazione 1-based e ordine naturale
- [x] Verificare in EventoVisualizzaTutteCartelleAvanzata totale_cartelle, numerazione 1-based e scomposizione dei pacchetti avanzati
- [x] Verificare in EventoStatoFocusCorrente il caso con tutti i focus assenti
- [x] Verificare in EventoStatoFocusCorrente il caso con solo focus cartella presente
- [x] Verificare in EventoStatoFocusCorrente il caso con cartella, riga e colonna presenti

### Passo 3 - Verifiche del file

- [x] Eseguire python -m unittest tests.unit.test_eventi_output_bulk_focus -q
- [x] Verificare che il file non contenga import pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che MagicMock compaia solo nei due factory bulk previsti
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- I mock devono esporre solo l'interfaccia minima richiesta dai factory.
- Non istanziare Cartella reale in questo sottogruppo.
- Il file deve restare confinato al solo perimetro E5.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
