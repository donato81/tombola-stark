---
type: todo
feature: test_eventi_output_segnazione
agent: Agent-Plan
status: DRAFT
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
stato: bozza
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

- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i quattro factory di EventoSegnazioneNumero
- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di RisultatoRicercaNumeroInCartella
- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i due factory di EventoRicercaNumeroInCartelle

### Passo 2 - Creare tests/unit/test_eventi_output_segnazione.py

- [ ] Creare tests/unit/test_eventi_output_segnazione.py
- [ ] Usare esclusivamente unittest come libreria di test
- [ ] Verificare in EventoSegnazioneNumero il ramo segnato
- [ ] Verificare in EventoSegnazioneNumero il ramo gia_segnato
- [ ] Verificare in EventoSegnazioneNumero il ramo non_presente
- [ ] Verificare in EventoSegnazioneNumero il ramo non_estratto
- [ ] Verificare in RisultatoRicercaNumeroInCartella la conversione indice_cartella -> numero_cartella
- [ ] Verificare in EventoRicercaNumeroInCartelle il caso non_trovato
- [ ] Verificare in EventoRicercaNumeroInCartelle il caso trovato con ordinamento per indice_cartella

### Passo 3 - Verifiche del file

- [ ] Eseguire python -m unittest tests.unit.test_eventi_output_segnazione -q
- [ ] Verificare che il file non contenga import pytest
- [ ] Verificare che il file non contenga fixture pytest
- [ ] Verificare che il file non usi MagicMock
- [ ] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [ ] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- Tutti i dati di test devono essere reali e deterministici.
- Il caso trovato di EventoRicercaNumeroInCartelle deve partire da una lista deliberatamente non ordinata.
- Il file deve restare confinato al solo perimetro E4.

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato
