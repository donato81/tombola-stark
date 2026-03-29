---
type: todo
feature: fix_test_destra_avanzata_rifinitura
agent: Agent-Plan
status: COMPLETED
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md
design_ref: docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md
---

## Metadati

tipo: todo_task
titolo: TODO rifinitura test colonna destra avanzata
data_creazione: 2026-03-29
agente: Agent-Plan
stato: completato
feature: fix_test_destra_avanzata_rifinitura
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md
design: docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md
report: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md

## Contenuto

### Descrizione task

Rifinire tre test avanzati di navigazione colonna in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
completando il pattern di asserzione del caso di movimento riuscito e rendendo
deterministico il setup dei casi con numeri segnati.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_fix_test_destra_avanzata_rifinitura.md](../2%20-%20projects/DESIGN_fix_test_destra_avanzata_rifinitura.md)
- Plan: [PLAN_fix_test_destra_avanzata_rifinitura_v1.md](../3%20-%20coding%20plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md)
- Report: [REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md](../4%20-%20reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md)

## Checklist operativa

### Micro-fase 1 — fix movimento normale avanzato destra

- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_movimento_normale` prima di modificarlo
- [x] Aggiungere `self.assertIsNone(risultato.evento.limite)` nel punto corretto
- [x] Verificare il solo test di movimento normale avanzato destra

### Micro-fase 2 — rafforzamento setup con segni destra avanzata

- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni` prima di modificarlo
- [x] Rendere incondizionata la verifica del numero segnato con setup deterministico
- [x] Eliminare il ramo che puo' saltare l'asserzione principale
- [x] Verificare il solo test con segni destra avanzata

### Micro-fase 3 — rafforzamento simmetrico sinistra avanzata

- [x] Leggere il corpo di `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` prima di modificarlo
- [x] Applicare lo stesso rafforzamento del setup alla variante sinistra
- [x] Eliminare il ramo che puo' saltare l'asserzione principale
- [x] Verificare il solo test con segni sinistra avanzata

### Chiusura rifinitura

- [x] Eseguire verifica finale del file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [x] Confermare che nessun test non target e' stato alterato
- [x] Aggiornare questo TODO marcando le fasi completate

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato