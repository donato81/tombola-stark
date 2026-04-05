---
type: todo
feature: test_helper_focus
agent: Agent-Plan
status: COMPLETED
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_TEST_HELPER_FOCUS.md
design_ref: docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md
date: 2026-03-30
report_ref: docs/4 - reports/report_verifica_lavori_test_helper_focus.md
---

## Metadati

tipo: todo_task
titolo: TODO test diretti per GestioneFocusMixin
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_helper_focus
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_TEST_HELPER_FOCUS.md
design: docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md
report: docs/4 - reports/report_verifica_lavori_test_helper_focus.md

## Contenuto

### Descrizione task

Scrivere `tests/unit/test_helper_focus.py` con test diretti e isolati per
`GestioneFocusMixin`, usando `unittest` e lo stub minimale concordato.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_TEST_HELPER_FOCUS.md](../2%20-%20projects/DESIGN_TEST_HELPER_FOCUS.md)
- Plan: [PLAN_TEST_HELPER_FOCUS.md](../3%20-%20coding%20plans/PLAN_TEST_HELPER_FOCUS.md)
- Report: [report_verifica_lavori_test_helper_focus.md](../4%20-%20reports/report_verifica_lavori_test_helper_focus.md)

## Checklist operativa

- [x] Creare `StubFocus`
- [x] Creare `setUp`

### Gruppo 1 — Cartella

- [x] `test_esito_focus_cartella_impostato_rigoroso_senza_focus`
- [x] `test_esito_focus_cartella_in_range_fuori_range_superiore`
- [x] `test_esito_focus_cartella_in_range_indice_negativo`

### Gruppo 2 — Riga

- [x] `test_esito_focus_riga_impostata_cartella_assente`
- [x] `test_esito_focus_riga_impostata_riga_assente`
- [x] `test_esito_focus_riga_impostata_ok`
- [x] `test_esito_focus_riga_in_range_fuori_range_superiore`
- [x] `test_esito_focus_riga_in_range_indice_negativo`
- [x] `test_esito_focus_riga_in_range_ok`
- [x] `test_esito_focus_riga_valido_riga_fuori_range`

### Gruppo 3 — Colonna

- [x] `test_esito_focus_colonna_impostata_cartella_assente`
- [x] `test_esito_focus_colonna_impostata_colonna_assente`
- [x] `test_esito_focus_colonna_impostata_ok`
- [x] `test_esito_focus_colonna_in_range_fuori_range_superiore`
- [x] `test_esito_focus_colonna_in_range_indice_negativo`
- [x] `test_esito_focus_colonna_in_range_ok`
- [x] `test_esito_focus_colonna_valido_colonna_assente`
- [x] `test_esito_focus_colonna_valido_colonna_fuori_range`
- [x] `test_esito_focus_colonna_valido_ok`

### Gruppo 4 — Reset

- [x] `test_reset_focus_cartella_riga_e_colonna_azzera_tutto`
- [x] `test_reset_focus_cartella_riga_e_colonna_da_stato_impostato`

### Verifica finale

- [x] Eseguire `python -m unittest tests/unit/test_helper_focus.py`
- [x] Confermare che tutti i test sono verdi

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato