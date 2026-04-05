---
type: todo
feature: test_eventi_output_segnazione
agent: Agent-Plan
status: DONE
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_output_segnazione_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari degli eventi output segnazione e ricerca
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_output_segnazione
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_output_segnazione_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_output_segnazione.py per coprire il perimetro E4 di eventi_output_ui_umani.py senza modificare file in [bingo_game/](../../bingo_game/) e senza toccare altri file di test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_output_segnazione_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md)
- Plan: [PLAN_test_eventi_output_segnazione_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_output_segnazione_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere il perimetro E4

- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i quattro factory di EventoSegnazioneNumero
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di RisultatoRicercaNumeroInCartella
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i due factory di EventoRicercaNumeroInCartelle

### Passo 2 - Creare tests/unit/test_eventi_output_segnazione.py

- [x] Creare tests/unit/test_eventi_output_segnazione.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Verificare in EventoSegnazioneNumero il ramo segnato
- [x] Verificare in EventoSegnazioneNumero il ramo gia_segnato
- [x] Verificare in EventoSegnazioneNumero il ramo non_presente
- [x] Verificare in EventoSegnazioneNumero il ramo non_estratto
- [x] Verificare in RisultatoRicercaNumeroInCartella la conversione indice_cartella -> numero_cartella
- [x] Verificare in EventoRicercaNumeroInCartelle il caso non_trovato
- [x] Verificare in EventoRicercaNumeroInCartelle il caso trovato con ordinamento per indice_cartella

### Passo 3 - Verifiche del file

- [x] Eseguire python -m unittest tests.unit.test_eventi_output_segnazione -q
- [x] Verificare che il file non contenga import pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file non usi MagicMock
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- Tutti i dati di test devono essere reali e deterministici.
- Il caso trovato di EventoRicercaNumeroInCartelle deve partire da una lista deliberatamente non ordinata.
- Il file deve restare confinato al solo perimetro E4.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
