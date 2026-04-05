---
type: todo
feature: test_eventi_output_tabellone
agent: Agent-Plan
status: DONE
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_output_tabellone_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari degli eventi output tabellone
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_output_tabellone
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_output_tabellone_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_output_tabellone.py per coprire il perimetro E3 di eventi_output_ui_umani.py senza modificare file in [bingo_game/](../../bingo_game/) e senza toccare altri file di test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_output_tabellone_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md)
- Plan: [PLAN_test_eventi_output_tabellone_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_output_tabellone_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere il perimetro E3

- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoVerificaNumeroEstratto
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoUltimoNumeroEstratto
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoUltimiNumeriEstratti
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoRiepilogoTabellone
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoListaNumeriEstratti

### Passo 2 - Creare tests/unit/test_eventi_output_tabellone.py

- [x] Creare tests/unit/test_eventi_output_tabellone.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Verificare in EventoVerificaNumeroEstratto i factory estratto_si e estratto_no
- [x] Verificare in EventoUltimoNumeroEstratto i factory numero_presente e nessuna_estrazione
- [x] Verificare in EventoUltimiNumeriEstratti il caso con numeri
- [x] Verificare in EventoUltimiNumeriEstratti il caso di overflow oltre richiesti
- [x] Verificare in EventoUltimiNumeriEstratti il caso nessuna_estrazione
- [x] Verificare in EventoRiepilogoTabellone la conversione in tuple e il calcolo di ultimi_visualizzati
- [x] Verificare in EventoRiepilogoTabellone il reset difensivo di ultimo_estratto a None quando non ci sono estrazioni
- [x] Verificare in EventoListaNumeriEstratti l'ordinamento crescente dei numeri
- [x] Verificare in EventoListaNumeriEstratti il calcolo di totale_estratti

### Passo 3 - Verifiche del file

- [x] Eseguire python -m unittest tests.unit.test_eventi_output_tabellone -q
- [x] Verificare che il file non contenga import pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file non usi MagicMock
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- I casi di test devono includere sia input popolati sia input vuoti.
- Non usare mock o fixture esterne in questo sottogruppo.
- Il file deve restare confinato al solo perimetro E3.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
