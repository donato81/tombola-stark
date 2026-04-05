---
type: todo
feature: test_eventi_output_cartella
agent: Agent-Plan
status: DONE
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_eventi_output_cartella_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_eventi_output_cartella_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari degli eventi output cartella
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_eventi_output_cartella
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_eventi_output_cartella_v1.0.0.md
design: docs/2 - projects/DESIGN_test_eventi_output_cartella_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_eventi_output_cartella.py per coprire il perimetro E1 di eventi_output_ui_umani.py senza modificare file in [bingo_game/](../../bingo_game/) e senza toccare altri file di test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_test_eventi_output_cartella_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_cartella_v1.0.0.md)
- Plan: [PLAN_test_eventi_output_cartella_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_eventi_output_cartella_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere il perimetro E1

- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i campi di EventoRiepilogoCartellaCorrente
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i factory di EventoLimiteNavigazioneCartelle
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare il factory di EventoVisualizzaCartellaSemplice
- [x] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare costruzione diretta e factory di EventoVisualizzaCartellaAvanzata

### Passo 2 - Creare tests/unit/test_eventi_output_cartella.py

- [x] Creare tests/unit/test_eventi_output_cartella.py
- [x] Usare esclusivamente unittest come libreria di test
- [x] Verificare in EventoRiepilogoCartellaCorrente la conversione indice_cartella -> numero_cartella
- [x] Verificare in EventoRiepilogoCartellaCorrente l'ordinamento di numeri_non_segnati
- [x] Verificare in EventoRiepilogoCartellaCorrente il calcolo di mancanti
- [x] Verificare in EventoLimiteNavigazioneCartelle il ramo limite_minimo
- [x] Verificare in EventoLimiteNavigazioneCartelle il ramo limite_massimo
- [x] Verificare in EventoVisualizzaCartellaSemplice la conversione indice_cartella -> numero_cartella
- [x] Verificare in EventoVisualizzaCartellaSemplice che la griglia resti immutabile
- [x] Verificare in EventoVisualizzaCartellaAvanzata la costruzione diretta dei campi
- [x] Verificare in EventoVisualizzaCartellaAvanzata la scomposizione di dati_avanzati nel factory crea_da_dati_avanzati

### Passo 3 - Verifiche del file

- [x] Eseguire python -m unittest tests.unit.test_eventi_output_cartella -q
- [x] Verificare che il file non contenga import pytest
- [x] Verificare che il file non contenga fixture pytest
- [x] Verificare che il file non usi MagicMock
- [x] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [x] Verificare che nessun altro file in tests/unit/ sia stato modificato

## Note operative

- Tutti i dati di test devono essere reali, a base di primitivi, tuple e dict.
- Non usare mock o fixture condivise esterne in questo sottogruppo.
- Il file deve restare confinato al solo perimetro E1.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
