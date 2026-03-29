---
type: todo
feature: fix_test_colonna_destra_eventi
agent: Agent-Plan
status: DRAFT
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md
design_ref: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: todo_task
titolo: TODO tranche 3 modernizzazione test colonna destra
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_test_colonna_destra_eventi
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md
design: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md

## Contenuto

### Descrizione task

Modernizzare i test legacy del gruppo colonna destra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
sostituendo assertion su testo renderizzato con assertion strutturate su
`EsitoAzione`, `EventoNavigazioneColonna` ed `EventoNavigazioneColonnaAvanzata`.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_fix_test_colonna_destra_eventi.md](../2%20-%20projects/DESIGN_fix_test_colonna_destra_eventi.md)
- Plan: [PLAN_fix_test_colonna_destra_eventi_v1.md](../3%20-%20coding%20plans/PLAN_fix_test_colonna_destra_eventi_v1.md)
- Report: [REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md](../4%20-%20reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md)

## Checklist operativa

### Micro-fase 1 — versione base

- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_cartella_mancante` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_cartella_mancante`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_ultima_colonna` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_ultima_colonna`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_movimento_normale` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_movimento_normale`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_colonna_vuota` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_colonna_vuota`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_stato_interno` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_semplice_stato_interno`
- [ ] Verificare il gruppo base

### Micro-fase 2 — versione avanzata

- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_cartella_mancante` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_avanzata_cartella_mancante`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_ultima_colonna` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_avanzata_ultima_colonna`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_movimento_normale` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_avanzata_movimento_normale`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione`
- [ ] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni` prima di modificarlo
- [ ] Aggiornare `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`
- [ ] Verificare il gruppo avanzata

### Chiusura tranche

- [ ] Eseguire verifica finale del file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [ ] Confermare che i test legacy del gruppo colonna destra sono allineati al contratto eventi
- [ ] Registrare eventuali test gia' strutturati trovati durante la rilettura preventiva
- [ ] Aggiornare questo TODO marcando le fasi completate

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato